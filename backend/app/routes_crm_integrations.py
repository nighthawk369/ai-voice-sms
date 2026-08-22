"""CRM Integrations API Routes"""

import logging
import json
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Header, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Integration, Organization
from app.dependencies import get_current_user, verify_organization_access
from app.integrations import (
    ServiceTitanAdapter,
    JobberAdapter,
    HousecallProAdapter,
    HubSpotAdapter,
    SalesforceAdapter,
)
from app.integrations.base import SyncDirection, WebhookHandler, SyncEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/crm-integrations", tags=["CRM Integrations"])


# ============================================================================
# SCHEMA DEFINITIONS
# ============================================================================

from pydantic import BaseModel, Field
from typing import List, Dict, Any


class CRMIntegrationConfig(BaseModel):
    """CRM integration configuration"""
    tenant_id: Optional[str] = None
    instance_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    custom_fields: Optional[Dict[str, str]] = {}


class CRMIntegrationCreate(BaseModel):
    """Create CRM integration"""
    integration_type: str = Field(..., description="servicetitan, jobber, housecall_pro, hubspot, salesforce")
    name: str
    access_token: str
    refresh_token: Optional[str] = None
    config: CRMIntegrationConfig = Field(default_factory=CRMIntegrationConfig)


class CRMIntegrationUpdate(BaseModel):
    """Update CRM integration"""
    name: Optional[str] = None
    is_active: Optional[bool] = None
    config: Optional[CRMIntegrationConfig] = None


class CRMIntegrationResponse(BaseModel):
    """CRM integration response"""
    id: UUID
    organization_id: UUID
    integration_type: str
    name: str
    is_active: bool
    sync_status: str
    last_sync_at: Optional[str] = None
    last_sync_error: Optional[str] = None


class SyncRequest(BaseModel):
    """Sync request"""
    direction: str = Field("bidirectional", description="to_external, from_external, bidirectional")
    entity_types: List[str] = Field(default=["contacts", "companies", "deals"])
    skip: int = 0
    limit: int = 100


class SyncResponse(BaseModel):
    """Sync response"""
    status: str
    message: str
    synced_records: int = 0
    errors: List[str] = []


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_adapter(integration_type: str, integration: Integration, db: AsyncSession):
    """Get appropriate adapter for integration type"""
    adapters = {
        "servicetitan": ServiceTitanAdapter,
        "jobber": JobberAdapter,
        "housecall_pro": HousecallProAdapter,
        "hubspot": HubSpotAdapter,
        "salesforce": SalesforceAdapter,
    }

    adapter_class = adapters.get(integration_type.lower())
    if not adapter_class:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported integration type: {integration_type}"
        )

    return adapter_class(integration, db)


# ============================================================================
# CRUD ENDPOINTS
# ============================================================================

@router.post("", response_model=CRMIntegrationResponse)
async def create_crm_integration(
    data: CRMIntegrationCreate,
    org_id: UUID = Depends(verify_organization_access),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Create new CRM integration"""
    try:
        # Create integration record
        integration = Integration(
            organization_id=org_id,
            integration_type=data.integration_type.lower(),
            name=data.name,
            access_token=data.access_token,
            refresh_token=data.refresh_token,
            config=data.config.dict(exclude_none=True),
            is_active=True,
        )

        # Test connection before saving
        adapter = get_adapter(data.integration_type, integration, db)
        if not await adapter.test_connection():
            raise HTTPException(
                status_code=400,
                detail="Failed to connect to external CRM. Please check your credentials."
            )

        db.add(integration)
        await db.commit()
        await db.refresh(integration)

        logger.info(f"Created CRM integration: {integration.id} ({data.integration_type})")

        return CRMIntegrationResponse(
            id=integration.id,
            organization_id=integration.organization_id,
            integration_type=integration.integration_type,
            name=integration.name,
            is_active=integration.is_active,
            sync_status=integration.sync_status,
        )
    except Exception as e:
        logger.error(f"Failed to create integration: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[CRMIntegrationResponse])
async def list_crm_integrations(
    org_id: UUID = Depends(verify_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """List CRM integrations for organization"""
    from sqlalchemy import select
    result = await db.execute(
        select(Integration).where(Integration.organization_id == org_id)
    )
    integrations = result.scalars().all()

    return [
        CRMIntegrationResponse(
            id=i.id,
            organization_id=i.organization_id,
            integration_type=i.integration_type,
            name=i.name,
            is_active=i.is_active,
            sync_status=i.sync_status,
            last_sync_at=i.last_sync_at.isoformat() if i.last_sync_at else None,
            last_sync_error=i.last_sync_error,
        )
        for i in integrations
    ]


@router.get("/{integration_id}", response_model=CRMIntegrationResponse)
async def get_crm_integration(
    integration_id: UUID,
    org_id: UUID = Depends(verify_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """Get CRM integration details"""
    from sqlalchemy import select
    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id,
            Integration.organization_id == org_id
        )
    )
    integration = result.scalar_one_or_none()

    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    return CRMIntegrationResponse(
        id=integration.id,
        organization_id=integration.organization_id,
        integration_type=integration.integration_type,
        name=integration.name,
        is_active=integration.is_active,
        sync_status=integration.sync_status,
        last_sync_at=integration.last_sync_at.isoformat() if integration.last_sync_at else None,
        last_sync_error=integration.last_sync_error,
    )


@router.patch("/{integration_id}", response_model=CRMIntegrationResponse)
async def update_crm_integration(
    integration_id: UUID,
    data: CRMIntegrationUpdate,
    org_id: UUID = Depends(verify_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """Update CRM integration"""
    from sqlalchemy import select
    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id,
            Integration.organization_id == org_id
        )
    )
    integration = result.scalar_one_or_none()

    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    if data.name:
        integration.name = data.name
    if data.is_active is not None:
        integration.is_active = data.is_active
    if data.config:
        integration.config.update(data.config.dict(exclude_none=True))

    await db.commit()
    await db.refresh(integration)

    return CRMIntegrationResponse(
        id=integration.id,
        organization_id=integration.organization_id,
        integration_type=integration.integration_type,
        name=integration.name,
        is_active=integration.is_active,
        sync_status=integration.sync_status,
    )


@router.delete("/{integration_id}", status_code=204)
async def delete_crm_integration(
    integration_id: UUID,
    org_id: UUID = Depends(verify_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """Delete CRM integration"""
    from sqlalchemy import select
    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id,
            Integration.organization_id == org_id
        )
    )
    integration = result.scalar_one_or_none()

    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    await db.delete(integration)
    await db.commit()

    logger.info(f"Deleted CRM integration: {integration_id}")


# ============================================================================
# SYNC ENDPOINTS
# ============================================================================

@router.post("/{integration_id}/test-connection", response_model=Dict[str, Any])
async def test_connection(
    integration_id: UUID,
    org_id: UUID = Depends(verify_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """Test CRM connection"""
    from sqlalchemy import select
    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id,
            Integration.organization_id == org_id
        )
    )
    integration = result.scalar_one_or_none()

    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    try:
        adapter = get_adapter(integration.integration_type, integration, db)
        is_connected = await adapter.test_connection()

        return {
            "connected": is_connected,
            "message": "Connection successful" if is_connected else "Connection failed"
        }
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return {
            "connected": False,
            "message": f"Connection failed: {str(e)}"
        }


@router.post("/{integration_id}/sync", response_model=SyncResponse)
async def sync_crm_data(
    integration_id: UUID,
    sync_request: SyncRequest,
    org_id: UUID = Depends(verify_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """Sync data with external CRM"""
    from sqlalchemy import select, update
    from datetime import datetime

    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id,
            Integration.organization_id == org_id
        )
    )
    integration = result.scalar_one_or_none()

    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    if not integration.is_active:
        raise HTTPException(status_code=400, detail="Integration is not active")

    try:
        # Update sync status
        await db.execute(
            update(Integration).where(Integration.id == integration_id).values(
                sync_status="syncing"
            )
        )
        await db.commit()

        adapter = get_adapter(integration.integration_type, integration, db)
        sync_engine = SyncEngine(adapter, db)

        sync_direction = SyncDirection(sync_request.direction.lower())
        synced_count = 0
        errors = []

        # Sync contacts
        if "contacts" in sync_request.entity_types:
            try:
                result = await sync_engine.sync_contacts(
                    direction=sync_direction,
                    skip=sync_request.skip,
                    limit=sync_request.limit
                )
                if result["status"] == "success":
                    synced_count += 1
                else:
                    errors.append(f"Contact sync: {result.get('error')}")
            except Exception as e:
                errors.append(f"Contact sync failed: {str(e)}")

        # Sync companies
        if "companies" in sync_request.entity_types:
            try:
                result = await sync_engine.sync_companies(direction=sync_direction)
                if result["status"] == "success":
                    synced_count += 1
                else:
                    errors.append(f"Company sync: {result.get('error')}")
            except Exception as e:
                errors.append(f"Company sync failed: {str(e)}")

        # Sync deals
        if "deals" in sync_request.entity_types:
            try:
                result = await sync_engine.sync_deals(direction=sync_direction)
                if result["status"] == "success":
                    synced_count += 1
                else:
                    errors.append(f"Deal sync: {result.get('error')}")
            except Exception as e:
                errors.append(f"Deal sync failed: {str(e)}")

        # Update sync metadata
        await db.execute(
            update(Integration).where(Integration.id == integration_id).values(
                sync_status="success" if not errors else "error",
                last_sync_at=datetime.utcnow(),
                last_sync_error="; ".join(errors) if errors else None
            )
        )
        await db.commit()

        logger.info(f"Sync completed for integration {integration_id}: {synced_count} entity types")

        return SyncResponse(
            status="success" if not errors else "partial",
            message=f"Synced {synced_count} entity types",
            synced_records=synced_count,
            errors=errors
        )

    except Exception as e:
        logger.error(f"Sync failed: {str(e)}")
        # Update error status
        await db.execute(
            update(Integration).where(Integration.id == integration_id).values(
                sync_status="error",
                last_sync_error=str(e)
            )
        )
        await db.commit()

        raise HTTPException(status_code=400, detail=f"Sync failed: {str(e)}")


# ============================================================================
# WEBHOOK ENDPOINTS
# ============================================================================

@router.post("/{integration_id}/webhooks/incoming")
async def handle_webhook(
    integration_id: UUID,
    payload: Dict[str, Any] = Body(...),
    x_signature: Optional[str] = Header(None),
    org_id: UUID = Depends(verify_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """Handle incoming webhook from external CRM"""
    from sqlalchemy import select

    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id,
            Integration.organization_id == org_id
        )
    )
    integration = result.scalar_one_or_none()

    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    try:
        adapter = get_adapter(integration.integration_type, integration, db)
        sync_engine = SyncEngine(adapter, db)
        webhook_handler = WebhookHandler(adapter, sync_engine)

        # Register default handlers
        webhook_handler.register_handler(
            "contact.created",
            webhook_handler.default_contact_created_handler
        )
        webhook_handler.register_handler(
            "contact.updated",
            webhook_handler.default_contact_updated_handler
        )
        webhook_handler.register_handler(
            "deal.created",
            webhook_handler.default_deal_created_handler
        )

        # Handle webhook
        success = await webhook_handler.handle_webhook(
            payload,
            x_signature or ""
        )

        if not success:
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

        return {"status": "received"}

    except Exception as e:
        logger.error(f"Webhook handling error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{integration_id}/webhooks", response_model=List[Dict[str, Any]])
async def list_webhooks(
    integration_id: UUID,
    org_id: UUID = Depends(verify_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """List registered webhooks for integration"""
    from sqlalchemy import select

    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id,
            Integration.organization_id == org_id
        )
    )
    integration = result.scalar_one_or_none()

    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    try:
        adapter = get_adapter(integration.integration_type, integration, db)
        webhooks = await adapter.client.list_webhooks()
        return webhooks.get("data", [])
    except Exception as e:
        logger.error(f"Failed to list webhooks: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{integration_id}/webhooks", response_model=Dict[str, Any])
async def register_webhook(
    integration_id: UUID,
    url: str,
    events: List[str],
    org_id: UUID = Depends(verify_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """Register webhook for integration"""
    from sqlalchemy import select

    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id,
            Integration.organization_id == org_id
        )
    )
    integration = result.scalar_one_or_none()

    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    try:
        adapter = get_adapter(integration.integration_type, integration, db)
        webhook = await adapter.client.register_webhook(url, events)
        logger.info(f"Registered webhook for integration {integration_id}")
        return webhook
    except Exception as e:
        logger.error(f"Failed to register webhook: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

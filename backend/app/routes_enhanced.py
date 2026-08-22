"""Enhanced API routes with pagination, filtering, sorting, and bulk operations"""

from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from app.db import get_db
from app.models import (
    Organization, Contact, Company, Deal, Activity, Pipeline, User,
    CustomField, Task, KnowledgeBaseItem
)
from app.schemas import (
    ContactRead, CompanyRead, DealRead, ActivityRead, PaginatedResponse
)
from app.security import get_token_user_id, get_token_org_id
from app.dependencies import get_current_user, get_current_org_id, get_admin_user
from app.utils import (
    FilterBuilder, SortBuilder, PaginationHelper, ChangeTracker, AuditLog, AuditAction
)
from app.config import get_settings
import logging

settings = get_settings()
router_enhanced = APIRouter()
logger = logging.getLogger(__name__)


# ============================================================================
# ENHANCED CONTACTS ENDPOINTS WITH PAGINATION, FILTERING, SORTING
# ============================================================================

@router_enhanced.get(
    "/contacts/search",
    tags=["CRM - Contacts"],
    summary="Search contacts with filtering and sorting"
)
async def search_contacts(
    org_id: UUID = Depends(get_current_org_id),
    user: User = Depends(get_current_user),
    # Pagination
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of records to return"),
    # Search
    search: Optional[str] = Query(None, min_length=1, description="Search term for name, email, phone"),
    # Filtering
    contact_type: Optional[str] = Query(None, description="Filter by contact type (LEAD, PROSPECT, CUSTOMER)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    company_id: Optional[UUID] = Query(None, description="Filter by company"),
    # Sorting
    sort_by: Optional[str] = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Search and filter contacts with advanced options

    - **search**: Search in name, email, phone
    - **contact_type**: LEAD, PROSPECT, CUSTOMER
    - **sort_by**: created_at, first_name, email, updated_at
    - **sort_order**: asc or desc
    """

    # Build base query
    query = select(Contact).where(Contact.organization_id == org_id)

    # Apply search
    if search:
        search_filter = FilterBuilder.build_search(
            Contact,
            search,
            ["first_name", "last_name", "email", "phone"]
        )
        if search_filter:
            query = query.where(search_filter)

    # Apply filters
    if contact_type:
        query = query.where(Contact.contact_type == contact_type)
    if status:
        query = query.where(Contact.status == status)
    if company_id:
        query = query.where(Contact.company_id == company_id)

    # Get total count
    count_result = await db.execute(select(func.count()).select_from(Contact).where(query.whereclause))
    total = count_result.scalar() or 0

    # Apply sorting
    sort_expr = SortBuilder.build_sort(Contact, sort_by, sort_order, "created_at")
    if sort_expr is not None:
        query = query.order_by(sort_expr)

    # Apply pagination
    offset = PaginationHelper.calculate_offset(skip, limit)
    limit = PaginationHelper.get_limit(limit)
    query = query.offset(offset).limit(limit)

    # Execute query
    result = await db.execute(query)
    contacts = result.scalars().all()

    # Build response
    items = [ContactRead.model_validate(c) for c in contacts]
    pagination = PaginationHelper.build_pagination_response(items, total, skip, limit)

    logger.info(
        f"Retrieved {len(items)} contacts for org {org_id}",
        extra={"user_id": str(user.id), "total": total}
    )

    return pagination


# ============================================================================
# ENHANCED COMPANIES ENDPOINTS
# ============================================================================

@router_enhanced.get(
    "/companies/search",
    tags=["CRM - Companies"],
    summary="Search companies with filtering"
)
async def search_companies(
    org_id: UUID = Depends(get_current_org_id),
    user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    sort_order: str = Query("desc"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Search and filter companies"""

    query = select(Company).where(Company.organization_id == org_id)

    if search:
        search_filter = FilterBuilder.build_search(
            Company,
            search,
            ["name", "industry", "website", "email"]
        )
        if search_filter:
            query = query.where(search_filter)

    if industry:
        query = query.where(Company.industry == industry)
    if status:
        query = query.where(Company.company_status == status)

    total = (await db.execute(select(func.count()).select_from(Company).where(query.whereclause))).scalar() or 0

    sort_expr = SortBuilder.build_sort(Company, sort_by, sort_order, "created_at")
    if sort_expr:
        query = query.order_by(sort_expr)

    offset = PaginationHelper.calculate_offset(skip, limit)
    limit = PaginationHelper.get_limit(limit)
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    items = [CompanyRead.model_validate(c) for c in result.scalars().all()]

    return PaginationHelper.build_pagination_response(items, total, skip, limit)


# ============================================================================
# ENHANCED DEALS ENDPOINTS
# ============================================================================

@router_enhanced.get(
    "/deals/search",
    tags=["CRM - Deals"],
    summary="Search deals with filtering and pipeline view"
)
async def search_deals(
    org_id: UUID = Depends(get_current_org_id),
    user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    pipeline_id: Optional[UUID] = Query(None),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    sort_order: str = Query("desc"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Search and filter deals with amount filtering"""

    query = select(Deal).where(Deal.organization_id == org_id)

    if search:
        search_filter = FilterBuilder.build_search(Deal, search, ["name", "description"])
        if search_filter:
            query = query.where(search_filter)

    if stage:
        query = query.where(Deal.stage == stage)
    if pipeline_id:
        query = query.where(Deal.pipeline_id == pipeline_id)
    if min_amount is not None:
        query = query.where(Deal.amount >= min_amount)
    if max_amount is not None:
        query = query.where(Deal.amount <= max_amount)

    total = (await db.execute(select(func.count()).select_from(Deal).where(query.whereclause))).scalar() or 0

    sort_expr = SortBuilder.build_sort(Deal, sort_by, sort_order, "created_at")
    if sort_expr:
        query = query.order_by(sort_expr)

    offset = PaginationHelper.calculate_offset(skip, limit)
    limit = PaginationHelper.get_limit(limit)
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    items = [DealRead.model_validate(d) for d in result.scalars().all()]

    return PaginationHelper.build_pagination_response(items, total, skip, limit)


# ============================================================================
# PIPELINE MANAGEMENT ENDPOINTS
# ============================================================================

@router_enhanced.post("/pipelines", tags=["CRM - Pipelines"])
async def create_pipeline(
    pipeline_data: Dict[str, Any],
    org_id: UUID = Depends(get_current_org_id),
    user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new sales pipeline (admin only)"""
    required_fields = ["name", "stages"]
    if not all(f in pipeline_data for f in required_fields):
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(required_fields)}")

    pipeline = Pipeline(
        organization_id=org_id,
        name=pipeline_data["name"],
        stages=pipeline_data["stages"],
        description=pipeline_data.get("description"),
        is_active=pipeline_data.get("is_active", True)
    )
    db.add(pipeline)
    await db.commit()
    await db.refresh(pipeline)

    logger.info(f"Pipeline created: {pipeline.id} by user {user.id}")

    return {
        "id": str(pipeline.id),
        "name": pipeline.name,
        "stages": pipeline.stages,
        "created_at": pipeline.created_at
    }


@router_enhanced.get("/pipelines", tags=["CRM - Pipelines"])
async def list_pipelines(
    org_id: UUID = Depends(get_current_org_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """List all sales pipelines"""
    query = select(Pipeline).where(Pipeline.organization_id == org_id)

    total = (await db.execute(select(func.count()).select_from(Pipeline).where(Pipeline.organization_id == org_id))).scalar() or 0

    offset = PaginationHelper.calculate_offset(skip, limit)
    limit = PaginationHelper.get_limit(limit)

    query = query.offset(offset).limit(limit).order_by(Pipeline.created_at.desc())
    result = await db.execute(query)
    pipelines = result.scalars().all()

    items = [
        {
            "id": str(p.id),
            "name": p.name,
            "stages": p.stages,
            "is_active": p.is_active,
            "created_at": p.created_at
        }
        for p in pipelines
    ]

    return PaginationHelper.build_pagination_response(items, total, skip, limit)


# ============================================================================
# BULK OPERATIONS
# ============================================================================

@router_enhanced.post("/contacts/bulk", tags=["CRM - Contacts"])
async def bulk_create_contacts(
    bulk_data: Dict[str, Any],
    org_id: UUID = Depends(get_current_org_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create multiple contacts in bulk

    Request body:
    ```json
    {
      "contacts": [
        {
          "first_name": "John",
          "last_name": "Doe",
          "phone": "1234567890",
          "email": "john@example.com"
        }
      ]
    }
    ```
    """
    contacts_data = bulk_data.get("contacts", [])

    if not contacts_data:
        raise HTTPException(status_code=400, detail="No contacts provided")

    if len(contacts_data) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 contacts per request")

    created_contacts = []
    errors = []

    for idx, contact_data in enumerate(contacts_data):
        try:
            # Validate required fields
            required = ["first_name", "last_name", "phone"]
            if not all(f in contact_data for f in required):
                errors.append({
                    "index": idx,
                    "error": f"Missing required fields: {', '.join(required)}"
                })
                continue

            contact = Contact(
                organization_id=org_id,
                **contact_data
            )
            db.add(contact)
            created_contacts.append(contact)

        except Exception as e:
            errors.append({
                "index": idx,
                "error": str(e)
            })

    if created_contacts:
        await db.commit()
        for contact in created_contacts:
            await db.refresh(contact)

    logger.info(
        f"Bulk created {len(created_contacts)} contacts (org: {org_id}, user: {user.id})",
        extra={"error_count": len(errors)}
    )

    return {
        "created": len(created_contacts),
        "failed": len(errors),
        "contacts": [
            {"id": str(c.id), "name": f"{c.first_name} {c.last_name}"}
            for c in created_contacts
        ],
        "errors": errors
    }


# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================

@router_enhanced.get("/organizations/config", tags=["Configuration"])
async def get_org_config(
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """Get organization configuration"""
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    return {
        "id": str(org.id),
        "name": org.name,
        "timezone": org.timezone,
        "locale": org.locale,
        "created_at": org.created_at,
        "settings": {
            "features": {
                "crm": True,
                "voice": True,
                "sms": True,
                "ai": True
            }
        }
    }


@router_enhanced.put("/organizations/config", tags=["Configuration"])
async def update_org_config(
    config_data: Dict[str, Any],
    org_id: UUID = Depends(get_current_org_id),
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update organization configuration (admin only)"""
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Track changes
    old_data = {
        "timezone": org.timezone,
        "locale": org.locale
    }

    # Update allowed fields
    if "timezone" in config_data:
        org.timezone = config_data["timezone"]
    if "locale" in config_data:
        org.locale = config_data["locale"]

    await db.commit()

    logger.info(
        f"Organization config updated (org: {org_id})",
        extra={"updated_by": str(admin.id)}
    )

    return {
        "message": "Configuration updated",
        "organization_id": str(org.id)
    }


# ============================================================================
# ANALYTICS & REPORTING ENDPOINTS
# ============================================================================

@router_enhanced.get("/contacts/analytics", tags=["Analytics"])
async def get_contacts_analytics(
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """Get contact analytics and statistics"""
    total_contacts = (await db.execute(
        select(func.count(Contact.id)).where(Contact.organization_id == org_id)
    )).scalar() or 0

    by_type = {}
    type_result = await db.execute(
        select(Contact.contact_type, func.count(Contact.id))
        .where(Contact.organization_id == org_id)
        .group_by(Contact.contact_type)
    )
    for contact_type, count in type_result.all():
        by_type[contact_type] = count

    by_status = {}
    status_result = await db.execute(
        select(Contact.status, func.count(Contact.id))
        .where(Contact.organization_id == org_id)
        .group_by(Contact.status)
    )
    for status, count in status_result.all():
        by_status[status] = count

    return {
        "total_contacts": total_contacts,
        "by_type": by_type,
        "by_status": by_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router_enhanced.get("/deals/analytics", tags=["Analytics"])
async def get_deals_analytics(
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """Get deal analytics and statistics"""
    total_deals = (await db.execute(
        select(func.count(Deal.id)).where(Deal.organization_id == org_id)
    )).scalar() or 0

    total_pipeline_value = (await db.execute(
        select(func.sum(Deal.amount)).where(Deal.organization_id == org_id)
    )).scalar() or 0

    by_stage = {}
    stage_result = await db.execute(
        select(Deal.stage, func.count(Deal.id), func.sum(Deal.amount))
        .where(Deal.organization_id == org_id)
        .group_by(Deal.stage)
    )
    for stage, count, total in stage_result.all():
        by_stage[stage] = {
            "count": count,
            "total_value": float(total) if total else 0
        }

    return {
        "total_deals": total_deals,
        "total_pipeline_value": float(total_pipeline_value) if total_pipeline_value else 0,
        "by_stage": by_stage,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

"""Jobber CRM Adapter"""

import logging
import json
import hmac
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Integration
from app.integrations.base import (
    CRMAdapter,
    FieldMapper,
    FieldMapping,
    SyncDirection,
    WebhookPayload,
    WebhookEventType,
)
from .client import JobberClient

logger = logging.getLogger(__name__)


class JobberAdapter(CRMAdapter):
    """Jobber CRM adapter implementation"""

    def __init__(
        self,
        integration: Integration,
        db: Optional[AsyncSession] = None
    ):
        client = JobberClient(access_token=integration.access_token)
        mappings = self._get_field_mappings()
        mapper = FieldMapper(mappings)
        super().__init__(integration, client, mapper, db)

    def _get_field_mappings(self) -> List[FieldMapping]:
        """Get field mappings from Jobber to in-house CRM"""
        return [
            # Contact mappings (Jobber calls them clients)
            FieldMapping(
                external_field="id",
                internal_field="external_id",
                field_type="string",
                required=True,
                direction=SyncDirection.FROM_EXTERNAL,
            ),
            FieldMapping(
                external_field="firstName",
                internal_field="first_name",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
            FieldMapping(
                external_field="lastName",
                internal_field="last_name",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
            FieldMapping(
                external_field="email",
                internal_field="email",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
            FieldMapping(
                external_field="mobile",
                internal_field="phone",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
            FieldMapping(
                external_field="address",
                internal_field="address",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
            FieldMapping(
                external_field="city",
                internal_field="city",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
            FieldMapping(
                external_field="province",
                internal_field="state",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
            FieldMapping(
                external_field="postalCode",
                internal_field="zip_code",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
        ]

    # ========================================================================
    # AUTHENTICATION
    # ========================================================================

    async def test_connection(self) -> bool:
        """Test connection to Jobber"""
        return await self.client.test_connection()

    # ========================================================================
    # CONTACT OPERATIONS
    # ========================================================================

    async def list_contacts(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List contacts from Jobber"""
        try:
            response = await self.client.list_clients(skip=skip, limit=limit)
            edges = response.get("data", {}).get("clients", {}).get("edges", [])
            return [edge["node"] for edge in edges]
        except Exception as e:
            logger.error(f"Failed to list contacts from Jobber: {str(e)}")
            return []

    async def get_contact(self, external_contact_id: str) -> Optional[Dict[str, Any]]:
        """Get single contact from Jobber"""
        try:
            response = await self.client.get_client(external_contact_id)
            return response.get("data", {}).get("client")
        except Exception as e:
            logger.error(f"Failed to get contact from Jobber: {str(e)}")
            return None

    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact in Jobber"""
        try:
            jobber_data = self.mapper.internal_to_external(contact_data)
            result = await self.client.create_client(jobber_data)
            client_data = result.get("data", {}).get("clientCreate", {}).get("client", {})
            logger.info(f"Created contact in Jobber: {client_data.get('id')}")
            return client_data
        except Exception as e:
            logger.error(f"Failed to create contact in Jobber: {str(e)}")
            raise

    async def update_contact(
        self,
        external_contact_id: str,
        contact_data: Dict[str, Any]
    ) -> bool:
        """Update contact in Jobber"""
        try:
            jobber_data = self.mapper.internal_to_external(contact_data)
            await self.client.update_client(external_contact_id, jobber_data)
            logger.info(f"Updated contact in Jobber: {external_contact_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update contact in Jobber: {str(e)}")
            return False

    async def delete_contact(self, external_contact_id: str) -> bool:
        """Delete contact from Jobber"""
        try:
            result = await self.client.delete_client(external_contact_id)
            if result:
                logger.info(f"Deleted contact from Jobber: {external_contact_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to delete contact in Jobber: {str(e)}")
            return False

    # ========================================================================
    # COMPANY OPERATIONS
    # ========================================================================

    async def list_companies(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List companies from Jobber (business accounts)"""
        try:
            response = await self.client.list_clients(skip=skip, limit=limit)
            edges = response.get("data", {}).get("clients", {}).get("edges", [])
            return [edge["node"] for edge in edges]
        except Exception as e:
            logger.error(f"Failed to list companies from Jobber: {str(e)}")
            return []

    async def get_company(self, external_company_id: str) -> Optional[Dict[str, Any]]:
        """Get single company from Jobber"""
        try:
            response = await self.client.get_client(external_company_id)
            return response.get("data", {}).get("client")
        except Exception as e:
            logger.error(f"Failed to get company from Jobber: {str(e)}")
            return None

    async def create_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create company in Jobber"""
        try:
            jobber_data = self.mapper.internal_to_external(company_data)
            result = await self.client.create_client(jobber_data)
            client_data = result.get("data", {}).get("clientCreate", {}).get("client", {})
            logger.info(f"Created company in Jobber: {client_data.get('id')}")
            return client_data
        except Exception as e:
            logger.error(f"Failed to create company in Jobber: {str(e)}")
            raise

    async def update_company(
        self,
        external_company_id: str,
        company_data: Dict[str, Any]
    ) -> bool:
        """Update company in Jobber"""
        try:
            jobber_data = self.mapper.internal_to_external(company_data)
            await self.client.update_client(external_company_id, jobber_data)
            logger.info(f"Updated company in Jobber: {external_company_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update company in Jobber: {str(e)}")
            return False

    # ========================================================================
    # DEAL OPERATIONS
    # ========================================================================

    async def list_deals(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List deals from Jobber (jobs)"""
        try:
            response = await self.client.list_jobs(skip=skip, limit=limit)
            edges = response.get("data", {}).get("jobs", {}).get("edges", [])
            return [edge["node"] for edge in edges]
        except Exception as e:
            logger.error(f"Failed to list deals from Jobber: {str(e)}")
            return []

    async def get_deal(self, external_deal_id: str) -> Optional[Dict[str, Any]]:
        """Get single deal from Jobber"""
        try:
            response = await self.client.get_job(external_deal_id)
            return response.get("data", {}).get("job")
        except Exception as e:
            logger.error(f"Failed to get deal from Jobber: {str(e)}")
            return None

    async def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create deal in Jobber"""
        try:
            jobber_data = self.mapper.internal_to_external(deal_data)
            result = await self.client.create_job(jobber_data)
            job_data = result.get("data", {}).get("jobCreate", {}).get("job", {})
            logger.info(f"Created deal in Jobber: {job_data.get('id')}")
            return job_data
        except Exception as e:
            logger.error(f"Failed to create deal in Jobber: {str(e)}")
            raise

    async def update_deal(
        self,
        external_deal_id: str,
        deal_data: Dict[str, Any]
    ) -> bool:
        """Update deal in Jobber"""
        try:
            jobber_data = self.mapper.internal_to_external(deal_data)
            await self.client.update_job(external_deal_id, jobber_data)
            logger.info(f"Updated deal in Jobber: {external_deal_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update deal in Jobber: {str(e)}")
            return False

    # ========================================================================
    # WEBHOOK HANDLING
    # ========================================================================

    async def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature from Jobber"""
        try:
            webhook_secret = self.integration.config.get("webhook_secret", "")
            expected_signature = hmac.new(
                webhook_secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            return False

    def parse_webhook_payload(self, payload: Dict[str, Any]) -> Optional[WebhookPayload]:
        """Parse webhook payload from Jobber"""
        try:
            event_type_map = {
                "client.created": WebhookEventType.CONTACT_CREATED,
                "client.updated": WebhookEventType.CONTACT_UPDATED,
                "client.deleted": WebhookEventType.CONTACT_DELETED,
                "job.created": WebhookEventType.DEAL_CREATED,
                "job.updated": WebhookEventType.DEAL_UPDATED,
                "job.completed": WebhookEventType.DEAL_CLOSED,
            }

            event_type = payload.get("event")
            event_type_enum = event_type_map.get(event_type)

            if not event_type_enum:
                logger.warning(f"Unknown webhook event type: {event_type}")
                return None

            entity_data = payload.get("data", {})

            return WebhookPayload(
                event_type=event_type_enum,
                entity_type="contact" if "client" in event_type else "deal",
                entity_id=entity_data.get("id", ""),
                data=entity_data,
                timestamp=datetime.utcnow(),
                webhook_id=payload.get("webhookId", ""),
            )
        except Exception as e:
            logger.error(f"Failed to parse webhook payload: {str(e)}")
            return None

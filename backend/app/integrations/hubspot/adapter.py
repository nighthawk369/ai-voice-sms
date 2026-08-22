"""HubSpot CRM Adapter"""

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
from .client import HubSpotClient

logger = logging.getLogger(__name__)


class HubSpotAdapter(CRMAdapter):
    """HubSpot CRM adapter implementation"""

    def __init__(
        self,
        integration: Integration,
        db: Optional[AsyncSession] = None
    ):
        client = HubSpotClient(access_token=integration.access_token)
        mappings = self._get_field_mappings()
        mapper = FieldMapper(mappings)
        super().__init__(integration, client, mapper, db)

    def _get_field_mappings(self) -> List[FieldMapping]:
        """Get field mappings from HubSpot to in-house CRM"""
        return [
            # Contact mappings
            FieldMapping(
                external_field="hs_object_id",
                internal_field="external_id",
                field_type="string",
                required=True,
                direction=SyncDirection.FROM_EXTERNAL,
            ),
            FieldMapping(
                external_field="firstname",
                internal_field="first_name",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
            FieldMapping(
                external_field="lastname",
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
                external_field="phone",
                internal_field="phone",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
            FieldMapping(
                external_field="street",
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
                external_field="state",
                internal_field="state",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
            FieldMapping(
                external_field="zip",
                internal_field="zip_code",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
        ]

    # ========================================================================
    # AUTHENTICATION
    # ========================================================================

    async def test_connection(self) -> bool:
        """Test connection to HubSpot"""
        return await self.client.test_connection()

    # ========================================================================
    # CONTACT OPERATIONS
    # ========================================================================

    async def list_contacts(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List contacts from HubSpot"""
        try:
            response = await self.client.list_contacts(skip=skip, limit=limit)
            results = response.get("results", [])
            return [self._parse_hubspot_object(item) for item in results]
        except Exception as e:
            logger.error(f"Failed to list contacts from HubSpot: {str(e)}")
            return []

    async def get_contact(self, external_contact_id: str) -> Optional[Dict[str, Any]]:
        """Get single contact from HubSpot"""
        try:
            response = await self.client.get_contact(external_contact_id)
            return self._parse_hubspot_object(response)
        except Exception as e:
            logger.error(f"Failed to get contact from HubSpot: {str(e)}")
            return None

    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact in HubSpot"""
        try:
            hs_data = self.mapper.internal_to_external(contact_data)
            result = await self.client.create_contact(hs_data)
            logger.info(f"Created contact in HubSpot: {result.get('id')}")
            return self._parse_hubspot_object(result)
        except Exception as e:
            logger.error(f"Failed to create contact in HubSpot: {str(e)}")
            raise

    async def update_contact(
        self,
        external_contact_id: str,
        contact_data: Dict[str, Any]
    ) -> bool:
        """Update contact in HubSpot"""
        try:
            hs_data = self.mapper.internal_to_external(contact_data)
            await self.client.update_contact(external_contact_id, hs_data)
            logger.info(f"Updated contact in HubSpot: {external_contact_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update contact in HubSpot: {str(e)}")
            return False

    async def delete_contact(self, external_contact_id: str) -> bool:
        """Delete contact from HubSpot"""
        try:
            result = await self.client.delete_contact(external_contact_id)
            if result:
                logger.info(f"Deleted contact from HubSpot: {external_contact_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to delete contact in HubSpot: {str(e)}")
            return False

    # ========================================================================
    # COMPANY OPERATIONS
    # ========================================================================

    async def list_companies(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List companies from HubSpot"""
        try:
            response = await self.client.list_companies(skip=skip, limit=limit)
            results = response.get("results", [])
            return [self._parse_hubspot_object(item) for item in results]
        except Exception as e:
            logger.error(f"Failed to list companies from HubSpot: {str(e)}")
            return []

    async def get_company(self, external_company_id: str) -> Optional[Dict[str, Any]]:
        """Get single company from HubSpot"""
        try:
            response = await self.client.get_company(external_company_id)
            return self._parse_hubspot_object(response)
        except Exception as e:
            logger.error(f"Failed to get company from HubSpot: {str(e)}")
            return None

    async def create_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create company in HubSpot"""
        try:
            hs_data = self.mapper.internal_to_external(company_data)
            result = await self.client.create_company(hs_data)
            logger.info(f"Created company in HubSpot: {result.get('id')}")
            return self._parse_hubspot_object(result)
        except Exception as e:
            logger.error(f"Failed to create company in HubSpot: {str(e)}")
            raise

    async def update_company(
        self,
        external_company_id: str,
        company_data: Dict[str, Any]
    ) -> bool:
        """Update company in HubSpot"""
        try:
            hs_data = self.mapper.internal_to_external(company_data)
            await self.client.update_company(external_company_id, hs_data)
            logger.info(f"Updated company in HubSpot: {external_company_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update company in HubSpot: {str(e)}")
            return False

    # ========================================================================
    # DEAL OPERATIONS
    # ========================================================================

    async def list_deals(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List deals from HubSpot"""
        try:
            response = await self.client.list_deals(skip=skip, limit=limit)
            results = response.get("results", [])
            return [self._parse_hubspot_object(item) for item in results]
        except Exception as e:
            logger.error(f"Failed to list deals from HubSpot: {str(e)}")
            return []

    async def get_deal(self, external_deal_id: str) -> Optional[Dict[str, Any]]:
        """Get single deal from HubSpot"""
        try:
            response = await self.client.get_deal(external_deal_id)
            return self._parse_hubspot_object(response)
        except Exception as e:
            logger.error(f"Failed to get deal from HubSpot: {str(e)}")
            return None

    async def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create deal in HubSpot"""
        try:
            hs_data = self.mapper.internal_to_external(deal_data)
            result = await self.client.create_deal(hs_data)
            logger.info(f"Created deal in HubSpot: {result.get('id')}")
            return self._parse_hubspot_object(result)
        except Exception as e:
            logger.error(f"Failed to create deal in HubSpot: {str(e)}")
            raise

    async def update_deal(
        self,
        external_deal_id: str,
        deal_data: Dict[str, Any]
    ) -> bool:
        """Update deal in HubSpot"""
        try:
            hs_data = self.mapper.internal_to_external(deal_data)
            await self.client.update_deal(external_deal_id, hs_data)
            logger.info(f"Updated deal in HubSpot: {external_deal_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update deal in HubSpot: {str(e)}")
            return False

    # ========================================================================
    # WEBHOOK HANDLING
    # ========================================================================

    async def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature from HubSpot"""
        try:
            # HubSpot uses request body + webhook signing secret
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
        """Parse webhook payload from HubSpot"""
        try:
            event_type_map = {
                "contact.creation": WebhookEventType.CONTACT_CREATED,
                "contact.propertyChange": WebhookEventType.CONTACT_UPDATED,
                "contact.deletion": WebhookEventType.CONTACT_DELETED,
                "deal.creation": WebhookEventType.DEAL_CREATED,
                "deal.propertyChange": WebhookEventType.DEAL_UPDATED,
                "deal.deletion": WebhookEventType.DEAL_CLOSED,
            }

            event_type = payload.get("eventType")
            event_type_enum = event_type_map.get(event_type)

            if not event_type_enum:
                logger.warning(f"Unknown webhook event type: {event_type}")
                return None

            object_id = payload.get("objectId")

            return WebhookPayload(
                event_type=event_type_enum,
                entity_type="contact" if "contact" in event_type else "deal",
                entity_id=str(object_id),
                data=payload,
                timestamp=datetime.utcnow(),
                webhook_id=payload.get("webhookId", ""),
            )
        except Exception as e:
            logger.error(f"Failed to parse webhook payload: {str(e)}")
            return None

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _parse_hubspot_object(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Parse HubSpot API object format to flat dict"""
        result = {"id": obj.get("id")}
        properties = obj.get("properties", {})
        for key, value in properties.items():
            if isinstance(value, dict):
                result[key] = value.get("value")
            else:
                result[key] = value
        return result

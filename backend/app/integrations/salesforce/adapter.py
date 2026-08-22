"""Salesforce CRM Adapter"""

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
from .client import SalesforceClient

logger = logging.getLogger(__name__)


class SalesforceAdapter(CRMAdapter):
    """Salesforce CRM adapter implementation"""

    def __init__(
        self,
        integration: Integration,
        db: Optional[AsyncSession] = None
    ):
        client = SalesforceClient(
            access_token=integration.access_token,
            instance_url=integration.config.get("instance_url", "https://login.salesforce.com")
        )
        mappings = self._get_field_mappings()
        mapper = FieldMapper(mappings)
        super().__init__(integration, client, mapper, db)

    def _get_field_mappings(self) -> List[FieldMapping]:
        """Get field mappings from Salesforce to in-house CRM"""
        return [
            # Contact mappings
            FieldMapping(
                external_field="Id",
                internal_field="external_id",
                field_type="string",
                required=True,
                direction=SyncDirection.FROM_EXTERNAL,
            ),
            FieldMapping(
                external_field="FirstName",
                internal_field="first_name",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
            FieldMapping(
                external_field="LastName",
                internal_field="last_name",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
            FieldMapping(
                external_field="Email",
                internal_field="email",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
            FieldMapping(
                external_field="Phone",
                internal_field="phone",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
            FieldMapping(
                external_field="BillingStreet",
                internal_field="address",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
            FieldMapping(
                external_field="BillingCity",
                internal_field="city",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
            FieldMapping(
                external_field="BillingState",
                internal_field="state",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
            FieldMapping(
                external_field="BillingPostalCode",
                internal_field="zip_code",
                field_type="string",
                direction=SyncDirection.BIDIRECTIONAL,
            ),
        ]

    # ========================================================================
    # AUTHENTICATION
    # ========================================================================

    async def test_connection(self) -> bool:
        """Test connection to Salesforce"""
        return await self.client.test_connection()

    # ========================================================================
    # CONTACT OPERATIONS
    # ========================================================================

    async def list_contacts(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List contacts from Salesforce"""
        try:
            response = await self.client.list_contacts(skip=skip, limit=limit)
            return response.get("records", [])
        except Exception as e:
            logger.error(f"Failed to list contacts from Salesforce: {str(e)}")
            return []

    async def get_contact(self, external_contact_id: str) -> Optional[Dict[str, Any]]:
        """Get single contact from Salesforce"""
        try:
            return await self.client.get_contact(external_contact_id)
        except Exception as e:
            logger.error(f"Failed to get contact from Salesforce: {str(e)}")
            return None

    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact in Salesforce"""
        try:
            sf_data = self.mapper.internal_to_external(contact_data)
            result = await self.client.create_contact(sf_data)
            logger.info(f"Created contact in Salesforce: {result.get('id')}")
            return result
        except Exception as e:
            logger.error(f"Failed to create contact in Salesforce: {str(e)}")
            raise

    async def update_contact(
        self,
        external_contact_id: str,
        contact_data: Dict[str, Any]
    ) -> bool:
        """Update contact in Salesforce"""
        try:
            sf_data = self.mapper.internal_to_external(contact_data)
            await self.client.update_contact(external_contact_id, sf_data)
            logger.info(f"Updated contact in Salesforce: {external_contact_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update contact in Salesforce: {str(e)}")
            return False

    async def delete_contact(self, external_contact_id: str) -> bool:
        """Delete contact from Salesforce"""
        try:
            result = await self.client.delete_contact(external_contact_id)
            if result:
                logger.info(f"Deleted contact from Salesforce: {external_contact_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to delete contact in Salesforce: {str(e)}")
            return False

    # ========================================================================
    # COMPANY OPERATIONS
    # ========================================================================

    async def list_companies(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List companies from Salesforce (accounts)"""
        try:
            response = await self.client.list_accounts(skip=skip, limit=limit)
            return response.get("records", [])
        except Exception as e:
            logger.error(f"Failed to list companies from Salesforce: {str(e)}")
            return []

    async def get_company(self, external_company_id: str) -> Optional[Dict[str, Any]]:
        """Get single company from Salesforce"""
        try:
            return await self.client.get_account(external_company_id)
        except Exception as e:
            logger.error(f"Failed to get company from Salesforce: {str(e)}")
            return None

    async def create_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create company in Salesforce"""
        try:
            sf_data = self.mapper.internal_to_external(company_data)
            result = await self.client.create_account(sf_data)
            logger.info(f"Created company in Salesforce: {result.get('id')}")
            return result
        except Exception as e:
            logger.error(f"Failed to create company in Salesforce: {str(e)}")
            raise

    async def update_company(
        self,
        external_company_id: str,
        company_data: Dict[str, Any]
    ) -> bool:
        """Update company in Salesforce"""
        try:
            sf_data = self.mapper.internal_to_external(company_data)
            await self.client.update_account(external_company_id, sf_data)
            logger.info(f"Updated company in Salesforce: {external_company_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update company in Salesforce: {str(e)}")
            return False

    # ========================================================================
    # DEAL OPERATIONS
    # ========================================================================

    async def list_deals(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List deals from Salesforce (opportunities)"""
        try:
            response = await self.client.list_opportunities(skip=skip, limit=limit)
            return response.get("records", [])
        except Exception as e:
            logger.error(f"Failed to list deals from Salesforce: {str(e)}")
            return []

    async def get_deal(self, external_deal_id: str) -> Optional[Dict[str, Any]]:
        """Get single deal from Salesforce"""
        try:
            return await self.client.get_opportunity(external_deal_id)
        except Exception as e:
            logger.error(f"Failed to get deal from Salesforce: {str(e)}")
            return None

    async def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create deal in Salesforce"""
        try:
            sf_data = self.mapper.internal_to_external(deal_data)
            result = await self.client.create_opportunity(sf_data)
            logger.info(f"Created deal in Salesforce: {result.get('id')}")
            return result
        except Exception as e:
            logger.error(f"Failed to create deal in Salesforce: {str(e)}")
            raise

    async def update_deal(
        self,
        external_deal_id: str,
        deal_data: Dict[str, Any]
    ) -> bool:
        """Update deal in Salesforce"""
        try:
            sf_data = self.mapper.internal_to_external(deal_data)
            await self.client.update_opportunity(external_deal_id, sf_data)
            logger.info(f"Updated deal in Salesforce: {external_deal_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update deal in Salesforce: {str(e)}")
            return False

    # ========================================================================
    # WEBHOOK HANDLING
    # ========================================================================

    async def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature from Salesforce"""
        try:
            # Salesforce uses SHA256 signature verification
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
        """Parse webhook payload from Salesforce"""
        try:
            event_type_map = {
                "created": WebhookEventType.CONTACT_CREATED,
                "updated": WebhookEventType.CONTACT_UPDATED,
                "deleted": WebhookEventType.CONTACT_DELETED,
            }

            event_type = payload.get("event", {}).get("type")
            event_type_enum = event_type_map.get(event_type)

            if not event_type_enum:
                logger.warning(f"Unknown webhook event type: {event_type}")
                return None

            sobject_data = payload.get("sobject", {})

            return WebhookPayload(
                event_type=event_type_enum,
                entity_type="contact",
                entity_id=sobject_data.get("Id", ""),
                data=sobject_data,
                timestamp=datetime.utcnow(),
                webhook_id=payload.get("channel", ""),
            )
        except Exception as e:
            logger.error(f"Failed to parse webhook payload: {str(e)}")
            return None

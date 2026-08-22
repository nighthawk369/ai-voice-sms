"""Base classes for CRM integrations"""

import logging
import json
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Callable, Coroutine
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID
import hmac
import hashlib
from dataclasses import dataclass, asdict

import aiohttp
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models import Integration, Contact, Company, Deal, Activity, Organization

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class SyncDirection(str, Enum):
    """Sync direction"""
    TO_EXTERNAL = "to_external"
    FROM_EXTERNAL = "from_external"
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(str, Enum):
    """Sync status"""
    IDLE = "idle"
    SYNCING = "syncing"
    SUCCESS = "success"
    ERROR = "error"
    PAUSED = "paused"


class WebhookEventType(str, Enum):
    """Webhook event types"""
    CONTACT_CREATED = "contact.created"
    CONTACT_UPDATED = "contact.updated"
    CONTACT_DELETED = "contact.deleted"
    DEAL_CREATED = "deal.created"
    DEAL_UPDATED = "deal.updated"
    DEAL_CLOSED = "deal.closed"
    COMPANY_CREATED = "company.created"
    COMPANY_UPDATED = "company.updated"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class OAuthToken:
    """OAuth token data"""
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    token_type: str = "Bearer"
    scope: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict"""
        return asdict(self)

    @property
    def is_expired(self) -> bool:
        """Check if token is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() >= self.expires_at

    @property
    def is_expiring_soon(self) -> bool:
        """Check if token will expire in next 5 minutes"""
        if not self.expires_at:
            return False
        return datetime.utcnow() >= (self.expires_at - timedelta(minutes=5))


@dataclass
class FieldMapping:
    """Field mapping definition"""
    external_field: str
    internal_field: str
    field_type: str = "string"  # string, int, bool, datetime, json
    required: bool = False
    transform_fn: Optional[Callable[[Any], Any]] = None
    reverse_transform_fn: Optional[Callable[[Any], Any]] = None
    direction: SyncDirection = SyncDirection.BIDIRECTIONAL


@dataclass
class SyncRecord:
    """Single record sync metadata"""
    external_id: str
    internal_id: UUID
    entity_type: str  # contact, company, deal, etc.
    last_synced_at: datetime
    last_synced_direction: SyncDirection
    external_hash: str  # Hash of external data for change detection
    internal_hash: str  # Hash of internal data for change detection


@dataclass
class WebhookPayload:
    """Webhook payload"""
    event_type: WebhookEventType
    entity_type: str
    entity_id: str
    data: Dict[str, Any]
    timestamp: datetime
    webhook_id: str


# ============================================================================
# ABSTRACT BASE CLASSES
# ============================================================================

class OAuthProvider(ABC):
    """OAuth 2.0 provider interface"""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    @property
    @abstractmethod
    def authorization_url(self) -> str:
        """Get authorization URL"""
        pass

    @property
    @abstractmethod
    def token_url(self) -> str:
        """Get token URL"""
        pass

    @property
    @abstractmethod
    def api_base_url(self) -> str:
        """Get API base URL"""
        pass

    @abstractmethod
    async def get_authorization_url(self, state: str, scopes: List[str]) -> str:
        """Get authorization URL for user"""
        pass

    @abstractmethod
    async def exchange_code_for_token(self, code: str, state: str) -> OAuthToken:
        """Exchange authorization code for access token"""
        pass

    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> OAuthToken:
        """Refresh access token"""
        pass


class CRMClient(ABC):
    """Base HTTP client for CRM APIs"""

    def __init__(self, base_url: str, access_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.session: Optional[aiohttp.ClientSession] = None

    @abstractmethod
    async def get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        pass

    async def request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request to CRM API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = await self.get_headers()
        headers.update(kwargs.pop("headers", {}))

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, **kwargs) as resp:
                if resp.status >= 400:
                    error_text = await resp.text()
                    logger.error(
                        f"CRM API error: {resp.status} - {error_text}",
                        extra={"url": url, "method": method}
                    )
                    raise Exception(f"CRM API error: {resp.status}")
                return await resp.json()

    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """GET request"""
        return await self.request("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """POST request"""
        return await self.request("POST", endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """PUT request"""
        return await self.request("PUT", endpoint, **kwargs)

    async def patch(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """PATCH request"""
        return await self.request("PATCH", endpoint, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE request"""
        return await self.request("DELETE", endpoint, **kwargs)


class FieldMapper:
    """Maps fields between external CRM and in-house CRM"""

    def __init__(self, mappings: List[FieldMapping]):
        self.mappings = mappings
        self.mapping_dict = {m.external_field: m for m in mappings}

    def external_to_internal(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform external CRM data to internal format"""
        internal_data = {}

        for mapping in self.mappings:
            if mapping.direction in [SyncDirection.FROM_EXTERNAL, SyncDirection.BIDIRECTIONAL]:
                if mapping.external_field in external_data:
                    value = external_data[mapping.external_field]
                    if mapping.transform_fn:
                        value = mapping.transform_fn(value)
                    internal_data[mapping.internal_field] = value

        return internal_data

    def internal_to_external(self, internal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform internal CRM data to external format"""
        external_data = {}

        for mapping in self.mappings:
            if mapping.direction in [SyncDirection.TO_EXTERNAL, SyncDirection.BIDIRECTIONAL]:
                if mapping.internal_field in internal_data:
                    value = internal_data[mapping.internal_field]
                    if mapping.reverse_transform_fn:
                        value = mapping.reverse_transform_fn(value)
                    external_data[mapping.external_field] = value

        return external_data

    def get_mapping(self, external_field: str) -> Optional[FieldMapping]:
        """Get mapping for external field"""
        return self.mapping_dict.get(external_field)


class CRMAdapter(ABC):
    """Abstract base class for CRM adapters"""

    def __init__(
        self,
        integration: Integration,
        client: CRMClient,
        mapper: FieldMapper,
        db: Optional[AsyncSession] = None
    ):
        self.integration = integration
        self.client = client
        self.mapper = mapper
        self.db = db

    # ========================================================================
    # AUTHENTICATION
    # ========================================================================

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test connection to CRM"""
        pass

    # ========================================================================
    # CONTACT OPERATIONS
    # ========================================================================

    @abstractmethod
    async def list_contacts(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List contacts from external CRM"""
        pass

    @abstractmethod
    async def get_contact(self, external_contact_id: str) -> Optional[Dict[str, Any]]:
        """Get single contact from external CRM"""
        pass

    @abstractmethod
    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact in external CRM"""
        pass

    @abstractmethod
    async def update_contact(self, external_contact_id: str, contact_data: Dict[str, Any]) -> bool:
        """Update contact in external CRM"""
        pass

    @abstractmethod
    async def delete_contact(self, external_contact_id: str) -> bool:
        """Delete contact from external CRM"""
        pass

    # ========================================================================
    # COMPANY OPERATIONS
    # ========================================================================

    @abstractmethod
    async def list_companies(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List companies from external CRM"""
        pass

    @abstractmethod
    async def get_company(self, external_company_id: str) -> Optional[Dict[str, Any]]:
        """Get single company from external CRM"""
        pass

    @abstractmethod
    async def create_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create company in external CRM"""
        pass

    @abstractmethod
    async def update_company(self, external_company_id: str, company_data: Dict[str, Any]) -> bool:
        """Update company in external CRM"""
        pass

    # ========================================================================
    # DEAL OPERATIONS
    # ========================================================================

    @abstractmethod
    async def list_deals(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List deals from external CRM"""
        pass

    @abstractmethod
    async def get_deal(self, external_deal_id: str) -> Optional[Dict[str, Any]]:
        """Get single deal from external CRM"""
        pass

    @abstractmethod
    async def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create deal in external CRM"""
        pass

    @abstractmethod
    async def update_deal(self, external_deal_id: str, deal_data: Dict[str, Any]) -> bool:
        """Update deal in external CRM"""
        pass

    # ========================================================================
    # WEBHOOK HANDLING
    # ========================================================================

    @abstractmethod
    async def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature from external CRM"""
        pass

    @abstractmethod
    def parse_webhook_payload(self, payload: Dict[str, Any]) -> Optional[WebhookPayload]:
        """Parse webhook payload from external CRM"""
        pass


class SyncEngine:
    """Handles bidirectional synchronization between in-house CRM and external CRMs"""

    def __init__(self, adapter: CRMAdapter, db: AsyncSession):
        self.adapter = adapter
        self.db = db
        self.sync_records: Dict[str, SyncRecord] = {}

    async def sync_contacts(
        self,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Sync contacts"""
        try:
            if direction in [SyncDirection.FROM_EXTERNAL, SyncDirection.BIDIRECTIONAL]:
                await self._sync_contacts_from_external(skip, limit)

            if direction in [SyncDirection.TO_EXTERNAL, SyncDirection.BIDIRECTIONAL]:
                await self._sync_contacts_to_external()

            return {"status": "success", "direction": direction}
        except Exception as e:
            logger.error(f"Contact sync error: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def _sync_contacts_from_external(self, skip: int, limit: int):
        """Sync contacts from external CRM to in-house CRM"""
        external_contacts = await self.adapter.list_contacts(skip, limit)

        for external_contact in external_contacts:
            internal_contact_data = self.adapter.mapper.external_to_internal(external_contact)
            # TODO: Create or update contact in internal DB
            logger.info(f"Synced contact: {external_contact}")

    async def _sync_contacts_to_external(self):
        """Sync contacts from in-house CRM to external CRM"""
        # TODO: Query contacts that need syncing
        # TODO: Transform to external format
        # TODO: Create or update in external CRM
        pass

    async def sync_companies(
        self,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    ) -> Dict[str, Any]:
        """Sync companies"""
        try:
            if direction in [SyncDirection.FROM_EXTERNAL, SyncDirection.BIDIRECTIONAL]:
                await self._sync_companies_from_external()

            if direction in [SyncDirection.TO_EXTERNAL, SyncDirection.BIDIRECTIONAL]:
                await self._sync_companies_to_external()

            return {"status": "success"}
        except Exception as e:
            logger.error(f"Company sync error: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def _sync_companies_from_external(self):
        """Sync companies from external CRM"""
        pass

    async def _sync_companies_to_external(self):
        """Sync companies to external CRM"""
        pass

    async def sync_deals(
        self,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    ) -> Dict[str, Any]:
        """Sync deals"""
        try:
            if direction in [SyncDirection.FROM_EXTERNAL, SyncDirection.BIDIRECTIONAL]:
                await self._sync_deals_from_external()

            if direction in [SyncDirection.TO_EXTERNAL, SyncDirection.BIDIRECTIONAL]:
                await self._sync_deals_to_external()

            return {"status": "success"}
        except Exception as e:
            logger.error(f"Deal sync error: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def _sync_deals_from_external(self):
        """Sync deals from external CRM"""
        pass

    async def _sync_deals_to_external(self):
        """Sync deals to external CRM"""
        pass


class WebhookHandler:
    """Handles incoming webhooks from external CRMs"""

    def __init__(self, adapter: CRMAdapter, sync_engine: SyncEngine):
        self.adapter = adapter
        self.sync_engine = sync_engine
        self.handlers: Dict[WebhookEventType, Callable] = {}

    def register_handler(
        self,
        event_type: WebhookEventType,
        handler: Callable[[WebhookPayload], Coroutine]
    ):
        """Register webhook event handler"""
        self.handlers[event_type] = handler

    async def handle_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """Handle incoming webhook"""
        try:
            # Verify signature
            if not await self.adapter.verify_webhook_signature(
                json.dumps(payload).encode(),
                signature
            ):
                logger.warning("Invalid webhook signature")
                return False

            # Parse payload
            webhook_payload = self.adapter.parse_webhook_payload(payload)
            if not webhook_payload:
                logger.warning("Failed to parse webhook payload")
                return False

            # Route to handler
            handler = self.handlers.get(webhook_payload.event_type)
            if handler:
                await handler(webhook_payload)

            return True
        except Exception as e:
            logger.error(f"Webhook handling error: {str(e)}")
            return False

    async def default_contact_created_handler(self, payload: WebhookPayload):
        """Default handler for contact created events"""
        logger.info(f"Contact created in external CRM: {payload.entity_id}")
        # Sync from external
        external_contact = await self.adapter.get_contact(payload.entity_id)
        if external_contact:
            internal_data = self.adapter.mapper.external_to_internal(external_contact)
            # TODO: Create in internal DB
            logger.info(f"Created contact in internal CRM from webhook")

    async def default_contact_updated_handler(self, payload: WebhookPayload):
        """Default handler for contact updated events"""
        logger.info(f"Contact updated in external CRM: {payload.entity_id}")

    async def default_deal_created_handler(self, payload: WebhookPayload):
        """Default handler for deal created events"""
        logger.info(f"Deal created in external CRM: {payload.entity_id}")

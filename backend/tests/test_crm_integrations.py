"""Tests for CRM Integrations"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

from app.models import Integration, Organization
from app.integrations.base import (
    FieldMapper,
    FieldMapping,
    SyncDirection,
    OAuthToken,
    WebhookPayload,
    WebhookEventType,
)
from app.integrations import (
    ServiceTitanAdapter,
    JobberAdapter,
    HousecallProAdapter,
    HubSpotAdapter,
    SalesforceAdapter,
)


# ============================================================================
# FIELD MAPPING TESTS
# ============================================================================

def test_field_mapping_creation():
    """Test field mapping creation"""
    mapping = FieldMapping(
        external_field="firstName",
        internal_field="first_name",
        field_type="string",
        direction=SyncDirection.BIDIRECTIONAL
    )

    assert mapping.external_field == "firstName"
    assert mapping.internal_field == "first_name"
    assert mapping.field_type == "string"
    assert mapping.direction == SyncDirection.BIDIRECTIONAL


def test_field_mapper_external_to_internal():
    """Test field mapping from external to internal"""
    mappings = [
        FieldMapping(
            external_field="firstName",
            internal_field="first_name",
            direction=SyncDirection.FROM_EXTERNAL
        ),
        FieldMapping(
            external_field="lastName",
            internal_field="last_name",
            direction=SyncDirection.FROM_EXTERNAL
        ),
    ]

    mapper = FieldMapper(mappings)
    external_data = {
        "firstName": "John",
        "lastName": "Doe"
    }

    internal_data = mapper.external_to_internal(external_data)

    assert internal_data["first_name"] == "John"
    assert internal_data["last_name"] == "Doe"


def test_field_mapper_internal_to_external():
    """Test field mapping from internal to external"""
    mappings = [
        FieldMapping(
            external_field="firstName",
            internal_field="first_name",
            direction=SyncDirection.TO_EXTERNAL
        ),
        FieldMapping(
            external_field="lastName",
            internal_field="last_name",
            direction=SyncDirection.TO_EXTERNAL
        ),
    ]

    mapper = FieldMapper(mappings)
    internal_data = {
        "first_name": "John",
        "last_name": "Doe"
    }

    external_data = mapper.internal_to_external(internal_data)

    assert external_data["firstName"] == "John"
    assert external_data["lastName"] == "Doe"


def test_field_mapper_with_transform():
    """Test field mapping with transformation function"""
    def transform_phone(phone):
        # Remove dashes
        return phone.replace("-", "")

    def reverse_transform_phone(phone):
        # Add dashes back
        return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"

    mappings = [
        FieldMapping(
            external_field="phone",
            internal_field="phone",
            direction=SyncDirection.BIDIRECTIONAL,
            transform_fn=transform_phone,
            reverse_transform_fn=reverse_transform_phone
        ),
    ]

    mapper = FieldMapper(mappings)

    # External to internal (transform)
    external_data = {"phone": "555-123-4567"}
    internal_data = mapper.external_to_internal(external_data)
    assert internal_data["phone"] == "5551234567"

    # Internal to external (reverse transform)
    internal_data = {"phone": "5551234567"}
    external_data = mapper.internal_to_external(internal_data)
    assert external_data["phone"] == "555-123-4567"


# ============================================================================
# OAUTH TOKEN TESTS
# ============================================================================

def test_oauth_token_creation():
    """Test OAuth token creation"""
    token = OAuthToken(
        access_token="test_token",
        refresh_token="test_refresh",
        expires_at=datetime.utcnow()
    )

    assert token.access_token == "test_token"
    assert token.refresh_token == "test_refresh"
    assert token.token_type == "Bearer"


def test_oauth_token_is_expired():
    """Test token expiration check"""
    from datetime import timedelta

    # Expired token
    expired_token = OAuthToken(
        access_token="test",
        expires_at=datetime.utcnow() - timedelta(hours=1)
    )
    assert expired_token.is_expired is True

    # Valid token
    valid_token = OAuthToken(
        access_token="test",
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    assert valid_token.is_expired is False


def test_oauth_token_is_expiring_soon():
    """Test token expiration soon check"""
    from datetime import timedelta

    # Expiring soon (within 5 minutes)
    token = OAuthToken(
        access_token="test",
        expires_at=datetime.utcnow() + timedelta(minutes=3)
    )
    assert token.is_expiring_soon is True

    # Not expiring soon
    token = OAuthToken(
        access_token="test",
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    assert token.is_expiring_soon is False


def test_oauth_token_to_dict():
    """Test OAuth token serialization"""
    expires_at = datetime.utcnow()
    token = OAuthToken(
        access_token="test_token",
        refresh_token="test_refresh",
        expires_at=expires_at,
        token_type="Bearer"
    )

    token_dict = token.to_dict()
    assert token_dict["access_token"] == "test_token"
    assert token_dict["refresh_token"] == "test_refresh"
    assert token_dict["token_type"] == "Bearer"


# ============================================================================
# SERVICETITAN ADAPTER TESTS
# ============================================================================

@pytest.fixture
def servicetitan_integration():
    """Create a ServiceTitan integration for testing"""
    return Integration(
        id=uuid4(),
        organization_id=uuid4(),
        integration_type="servicetitan",
        name="Test ServiceTitan",
        access_token="test_token",
        config={"tenant_id": "test_tenant"}
    )


@pytest.mark.asyncio
async def test_servicetitan_field_mappings(servicetitan_integration):
    """Test ServiceTitan field mappings"""
    adapter = ServiceTitanAdapter(servicetitan_integration)

    # Get mappings
    mappings = adapter.mapper.mappings
    assert len(mappings) > 0

    # Test mapping
    external_data = {
        "id": "123",
        "firstName": "John",
        "lastName": "Doe",
        "email": "john@example.com",
        "phoneNumber": "555-123-4567"
    }

    internal_data = adapter.mapper.external_to_internal(external_data)
    assert internal_data["external_id"] == "123"
    assert internal_data["first_name"] == "John"
    assert internal_data["last_name"] == "Doe"


# ============================================================================
# JOBBER ADAPTER TESTS
# ============================================================================

@pytest.fixture
def jobber_integration():
    """Create a Jobber integration for testing"""
    return Integration(
        id=uuid4(),
        organization_id=uuid4(),
        integration_type="jobber",
        name="Test Jobber",
        access_token="test_token",
    )


@pytest.mark.asyncio
async def test_jobber_field_mappings(jobber_integration):
    """Test Jobber field mappings"""
    adapter = JobberAdapter(jobber_integration)

    mappings = adapter.mapper.mappings
    assert len(mappings) > 0

    external_data = {
        "id": "client_123",
        "firstName": "Jane",
        "lastName": "Smith",
        "email": "jane@example.com",
        "mobile": "555-987-6543"
    }

    internal_data = adapter.mapper.external_to_internal(external_data)
    assert internal_data["external_id"] == "client_123"
    assert internal_data["first_name"] == "Jane"


# ============================================================================
# HOUSECALL PRO ADAPTER TESTS
# ============================================================================

@pytest.fixture
def housecall_integration():
    """Create a Housecall Pro integration for testing"""
    return Integration(
        id=uuid4(),
        organization_id=uuid4(),
        integration_type="housecall_pro",
        name="Test Housecall Pro",
        access_token="test_token",
    )


@pytest.mark.asyncio
async def test_housecall_field_mappings(housecall_integration):
    """Test Housecall Pro field mappings"""
    adapter = HousecallProAdapter(housecall_integration)

    mappings = adapter.mapper.mappings
    assert len(mappings) > 0


# ============================================================================
# HUBSPOT ADAPTER TESTS
# ============================================================================

@pytest.fixture
def hubspot_integration():
    """Create a HubSpot integration for testing"""
    return Integration(
        id=uuid4(),
        organization_id=uuid4(),
        integration_type="hubspot",
        name="Test HubSpot",
        access_token="test_token",
    )


@pytest.mark.asyncio
async def test_hubspot_parse_object(hubspot_integration):
    """Test HubSpot object parsing"""
    adapter = HubSpotAdapter(hubspot_integration)

    hs_object = {
        "id": "contact_123",
        "properties": {
            "firstname": {"value": "Bob"},
            "lastname": {"value": "Jones"},
            "email": {"value": "bob@example.com"}
        }
    }

    parsed = adapter._parse_hubspot_object(hs_object)
    assert parsed["id"] == "contact_123"
    assert parsed["firstname"] == "Bob"
    assert parsed["lastname"] == "Jones"
    assert parsed["email"] == "bob@example.com"


# ============================================================================
# SALESFORCE ADAPTER TESTS
# ============================================================================

@pytest.fixture
def salesforce_integration():
    """Create a Salesforce integration for testing"""
    return Integration(
        id=uuid4(),
        organization_id=uuid4(),
        integration_type="salesforce",
        name="Test Salesforce",
        access_token="test_token",
        config={"instance_url": "https://test.salesforce.com"}
    )


@pytest.mark.asyncio
async def test_salesforce_field_mappings(salesforce_integration):
    """Test Salesforce field mappings"""
    adapter = SalesforceAdapter(salesforce_integration)

    mappings = adapter.mapper.mappings
    assert len(mappings) > 0

    external_data = {
        "Id": "001xx000003DHP",
        "FirstName": "Alice",
        "LastName": "Wonder"
    }

    internal_data = adapter.mapper.external_to_internal(external_data)
    assert internal_data["external_id"] == "001xx000003DHP"
    assert internal_data["first_name"] == "Alice"


# ============================================================================
# WEBHOOK TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_webhook_payload_parsing(hubspot_integration):
    """Test webhook payload parsing"""
    adapter = HubSpotAdapter(hubspot_integration)

    payload = {
        "eventType": "contact.creation",
        "objectId": 12345,
    }

    webhook_payload = adapter.parse_webhook_payload(payload)
    assert webhook_payload is not None
    assert webhook_payload.entity_type == "contact"
    assert webhook_payload.entity_id == "12345"


@pytest.mark.asyncio
async def test_webhook_signature_verification(servicetitan_integration):
    """Test webhook signature verification"""
    import hmac
    import hashlib

    servicetitan_integration.config["webhook_secret"] = "test_secret"
    adapter = ServiceTitanAdapter(servicetitan_integration)

    payload = b'{"test": "data"}'
    signature = hmac.new(b"test_secret", payload, hashlib.sha256).hexdigest()

    is_valid = await adapter.verify_webhook_signature(payload, signature)
    assert is_valid is True

    # Test with wrong signature
    wrong_signature = "invalid"
    is_valid = await adapter.verify_webhook_signature(payload, wrong_signature)
    assert is_valid is False


# ============================================================================
# SYNC TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_sync_direction_enum():
    """Test SyncDirection enum"""
    assert SyncDirection.TO_EXTERNAL == "to_external"
    assert SyncDirection.FROM_EXTERNAL == "from_external"
    assert SyncDirection.BIDIRECTIONAL == "bidirectional"


@pytest.mark.asyncio
async def test_webhook_event_type_enum():
    """Test WebhookEventType enum"""
    assert WebhookEventType.CONTACT_CREATED == "contact.created"
    assert WebhookEventType.CONTACT_UPDATED == "contact.updated"
    assert WebhookEventType.DEAL_CREATED == "deal.created"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

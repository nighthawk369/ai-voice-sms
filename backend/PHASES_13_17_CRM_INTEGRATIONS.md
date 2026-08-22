# PHASES 13-17: Third-Party CRM Integrations

Complete implementation guide for integrating external CRMs with the in-house CRM system.

## Overview

This implementation provides a modular, extensible framework for integrating with multiple third-party CRM systems while maintaining the in-house CRM as the source of truth.

**Key Principles:**
- In-house CRM is the primary data source
- External CRMs sync bidirectionally
- Flexible field mapping with transformation support
- Webhook-based real-time sync
- Comprehensive error handling and retry logic

## Architecture

### Directory Structure

```
backend/app/integrations/
├── __init__.py
├── base.py (abstract base classes)
├── servicetitan/
│   ├── __init__.py
│   ├── client.py (API client)
│   └── adapter.py (CRM adapter)
├── jobber/
│   ├── __init__.py
│   ├── client.py
│   └── adapter.py
├── housecall_pro/
│   ├── __init__.py
│   ├── client.py
│   └── adapter.py
├── hubspot/
│   ├── __init__.py
│   ├── client.py
│   └── adapter.py
└── salesforce/
    ├── __init__.py
    ├── client.py
    └── adapter.py

backend/app/
├── routes_crm_integrations.py (API endpoints)

backend/tests/
└── test_crm_integrations.py (comprehensive tests)
```

### Core Components

#### 1. Base Classes (base.py)

**OAuthProvider**: Abstract OAuth 2.0 implementation
- `authorization_url`: Authorization endpoint
- `token_url`: Token endpoint
- `exchange_code_for_token()`: OAuth flow
- `refresh_access_token()`: Token refresh

**CRMClient**: Base HTTP client for CRM APIs
- Handles authentication headers
- Request/response management
- Error handling

**FieldMapper**: Field transformation between systems
- Bidirectional mapping
- Transform functions
- Type conversion

**CRMAdapter**: Abstract adapter for each CRM
- Contact/company/deal operations
- Webhook handling
- Signature verification

**SyncEngine**: Manages bidirectional sync
- FROM_EXTERNAL: External → In-house
- TO_EXTERNAL: In-house → External
- BIDIRECTIONAL: Both directions

**WebhookHandler**: Processes incoming webhooks
- Event routing
- Signature verification
- Error handling

#### 2. Data Models

```python
@dataclass
class OAuthToken:
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_expired: bool  # property
    is_expiring_soon: bool  # property

@dataclass
class FieldMapping:
    external_field: str
    internal_field: str
    field_type: str  # string, int, bool, datetime, json
    required: bool = False
    transform_fn: Optional[Callable]
    reverse_transform_fn: Optional[Callable]
    direction: SyncDirection  # bidirectional, to_external, from_external

@dataclass
class WebhookPayload:
    event_type: WebhookEventType
    entity_type: str  # contact, company, deal
    entity_id: str
    data: Dict[str, Any]
    timestamp: datetime
    webhook_id: str
```

## Phase Details

### PHASE 13: ServiceTitan Integration

**Focus**: HVAC, Plumbing, Electrical service businesses

**Files Created:**
- `integrations/servicetitan/client.py` - ServiceTitan API client
- `integrations/servicetitan/adapter.py` - Adapter implementation

**Features:**
- Customer ↔ Contact sync
- Job ↔ Deal sync
- Technician team management
- Webhook support (customer.created, job.updated, etc.)

**API Endpoints:**
```
POST   /api/v1/crm-integrations
GET    /api/v1/crm-integrations
GET    /api/v1/crm-integrations/{id}
PATCH  /api/v1/crm-integrations/{id}
DELETE /api/v1/crm-integrations/{id}
POST   /api/v1/crm-integrations/{id}/sync
POST   /api/v1/crm-integrations/{id}/test-connection
```

**Field Mappings:**
```
ServiceTitan → In-house CRM
id → external_id
firstName → first_name
lastName → last_name
email → email
phoneNumber → phone
address → address
city → city
state → state
zipCode → zip_code
```

### PHASE 14: Jobber Integration

**Focus**: Multi-trade service businesses

**Key Differences:**
- Uses GraphQL API (not REST)
- Clients (contacts) vs. jobs (deals)
- Real-time mutations for updates

**Features:**
- GraphQL query/mutation support
- Client-to-contact mapping
- Job-to-deal mapping
- Webhook integration

### PHASE 15: Housecall Pro Integration

**Focus**: Field service businesses

**Features:**
- Customer management
- Job scheduling
- Appointment tracking
- Bidirectional sync

### PHASE 16: HubSpot Integration

**Focus**: SMB sales teams

**Features:**
- Contact/company/deal objects
- Custom field support
- Workflow automation triggers
- HubSpot properties API

**Field Parsing:**
```python
# HubSpot returns nested properties:
{
    "id": "contact_123",
    "properties": {
        "firstname": {"value": "John"},
        "email": {"value": "john@example.com"}
    }
}

# Adapter flattens to:
{
    "id": "contact_123",
    "firstname": "John",
    "email": "john@example.com"
}
```

### PHASE 17: Salesforce Integration

**Focus**: Enterprise customers

**Features:**
- Contact/Account/Opportunity objects
- SOQL query support
- Platform events for webhooks
- Instance URL configuration

**Object Mapping:**
- Contact (in-house) → Contact (SF) or Lead (SF)
- Company (in-house) → Account (SF)
- Deal (in-house) → Opportunity (SF)

## API Documentation

### Create Integration

```bash
POST /api/v1/crm-integrations

{
  "integration_type": "servicetitan",
  "name": "ServiceTitan Prod",
  "access_token": "st_token_...",
  "refresh_token": "st_refresh_...",
  "config": {
    "tenant_id": "12345",
    "webhook_secret": "webhook_secret_...",
    "custom_fields": {
      "custom_field_1": "internal_field_1"
    }
  }
}

Response:
{
  "id": "integration_id",
  "organization_id": "org_id",
  "integration_type": "servicetitan",
  "name": "ServiceTitan Prod",
  "is_active": true,
  "sync_status": "idle"
}
```

### Test Connection

```bash
POST /api/v1/crm-integrations/{id}/test-connection

Response:
{
  "connected": true,
  "message": "Connection successful"
}
```

### Sync Data

```bash
POST /api/v1/crm-integrations/{id}/sync

{
  "direction": "bidirectional",
  "entity_types": ["contacts", "companies", "deals"],
  "skip": 0,
  "limit": 100
}

Response:
{
  "status": "success",
  "message": "Synced 3 entity types",
  "synced_records": 3,
  "errors": []
}
```

### Handle Webhook

```bash
POST /api/v1/crm-integrations/{id}/webhooks/incoming
Headers: X-Signature: <webhook_signature>

{
  "type": "customer.created",
  "data": {
    "id": "123",
    "firstName": "John",
    "email": "john@example.com"
  }
}

Response:
{
  "status": "received"
}
```

## OAuth Flow

### Authorization Code Flow

```
1. Redirect user to external CRM authorization URL
   GET https://auth.crm.com/authorize?client_id=...&redirect_uri=...

2. User authenticates and grants permission
   Redirected to: https://app.local/callback?code=AUTH_CODE&state=STATE

3. Exchange code for token
   POST /oauth/token
   {
     "grant_type": "authorization_code",
     "code": "AUTH_CODE",
     "client_id": "CLIENT_ID",
     "client_secret": "CLIENT_SECRET",
     "redirect_uri": "https://app.local/callback"
   }

4. Store token and refresh_token in Integration record
```

### Token Refresh

```python
# Automatically refresh when token is expiring soon
if integration.token.is_expiring_soon:
    new_token = await oauth_provider.refresh_access_token(
        integration.refresh_token
    )
    integration.access_token = new_token.access_token
    integration.expires_at = new_token.expires_at
    db.commit()
```

## Field Mapping Examples

### Example 1: Simple Field Mapping

```python
FieldMapping(
    external_field="firstName",
    internal_field="first_name",
    field_type="string",
    direction=SyncDirection.BIDIRECTIONAL
)
```

### Example 2: Field Transformation

```python
def normalize_phone(phone):
    # Convert "555-123-4567" to "5551234567"
    return phone.replace("-", "").replace(" ", "")

def format_phone(phone):
    # Convert "5551234567" to "555-123-4567"
    return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"

FieldMapping(
    external_field="phone_number",
    internal_field="phone",
    field_type="string",
    direction=SyncDirection.BIDIRECTIONAL,
    transform_fn=normalize_phone,
    reverse_transform_fn=format_phone
)
```

### Example 3: One-Way Sync

```python
# Only sync from external CRM to internal
FieldMapping(
    external_field="hs_object_id",
    internal_field="external_id",
    field_type="string",
    required=True,
    direction=SyncDirection.FROM_EXTERNAL
)
```

## Webhook Handling

### Incoming Webhooks

```python
# Register webhook handler
webhook_handler = WebhookHandler(adapter, sync_engine)

webhook_handler.register_handler(
    WebhookEventType.CONTACT_CREATED,
    async def handle_contact_created(payload: WebhookPayload):
        # Fetch full contact from external CRM
        external_contact = await adapter.get_contact(payload.entity_id)
        # Transform to internal format
        internal_data = adapter.mapper.external_to_internal(external_contact)
        # Create/update in in-house CRM
        # ...
)

# Handle incoming webhook
success = await webhook_handler.handle_webhook(payload, signature)
```

### Webhook Signature Verification

Each CRM uses different signature schemes:

**ServiceTitan:**
```python
signature = hmac.sha256(webhook_secret, request_body).hexdigest()
```

**Jobber:**
```python
signature = hmac.sha256(webhook_secret, request_body).hexdigest()
```

**HubSpot:**
```python
signature = hmac.sha256(webhook_secret, request_body).hexdigest()
# Or: request_signature header in webhook
```

**Salesforce:**
```python
# Platform events use MessageId + MessageTimestamp
# Custom verification logic needed
```

## Sync Logic

### Bidirectional Sync Flow

```
1. Fetch external data (skip, limit)
2. For each external record:
   a. Check if exists in internal DB
   b. If not exists:
      - Transform to internal format
      - Create in internal DB
      - Store mapping (external_id → internal_id)
   c. If exists:
      - Compare hashes (changed detection)
      - If changed: update internal DB
      - Update mapping metadata

3. Sync from internal to external (if TO_EXTERNAL or BIDIRECTIONAL):
   a. Query internal records needing sync
   b. For each internal record:
      - Transform to external format
      - Create or update in external CRM
      - Store external_id mapping
```

### Conflict Resolution

```python
# Last-write-wins strategy
if external_updated_at > internal_updated_at:
    # External is newer
    sync_from_external()
else:
    # Internal is newer or same
    sync_to_external()
```

## Error Handling

### Retry Logic

```python
@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((aiohttp.ClientError, TimeoutError))
)
async def sync_contact(contact_id):
    # Try to sync, retry with exponential backoff
    pass
```

### Error States

```python
Integration.sync_status values:
- "idle": No sync in progress
- "syncing": Sync currently running
- "success": Last sync succeeded
- "error": Last sync had errors
- "paused": Sync temporarily paused

Integration.last_sync_error:
Stores error message from last failed sync
```

## Testing

### Unit Tests

```python
# Test field mapping
def test_field_mapper_external_to_internal():
    mapper = FieldMapper(mappings)
    external_data = {"firstName": "John"}
    internal_data = mapper.external_to_internal(external_data)
    assert internal_data["first_name"] == "John"

# Test webhook parsing
def test_webhook_payload_parsing():
    adapter = ServiceTitanAdapter(integration)
    payload = {"type": "customer.created", "data": {...}}
    webhook = adapter.parse_webhook_payload(payload)
    assert webhook.event_type == WebhookEventType.CONTACT_CREATED

# Test signature verification
async def test_webhook_signature_verification():
    adapter = ServiceTitanAdapter(integration)
    is_valid = await adapter.verify_webhook_signature(payload, signature)
    assert is_valid is True
```

### Integration Tests

```python
# Test full sync flow
async def test_full_sync_flow():
    adapter = ServiceTitanAdapter(integration)
    sync_engine = SyncEngine(adapter, db)
    
    result = await sync_engine.sync_contacts(
        direction=SyncDirection.BIDIRECTIONAL
    )
    assert result["status"] == "success"

# Test webhook handling
async def test_webhook_handling():
    webhook_handler = WebhookHandler(adapter, sync_engine)
    success = await webhook_handler.handle_webhook(payload, signature)
    assert success is True
```

## Configuration

### Environment Variables

```bash
# OAuth credentials for each CRM
SERVICETITAN_CLIENT_ID=...
SERVICETITAN_CLIENT_SECRET=...
SERVICETITAN_REDIRECT_URI=http://localhost:8000/callback/servicetitan

JOBBER_CLIENT_ID=...
JOBBER_CLIENT_SECRET=...

HOUSECALL_CLIENT_ID=...
HOUSECALL_CLIENT_SECRET=...

HUBSPOT_CLIENT_ID=...
HUBSPOT_CLIENT_SECRET=...

SALESFORCE_CLIENT_ID=...
SALESFORCE_CLIENT_SECRET=...
SALESFORCE_INSTANCE_URL=...

# Webhook verification
WEBHOOK_TIMEOUT=30
WEBHOOK_RETRY_ATTEMPTS=3
```

## Deployment Considerations

### Database Migrations

Create tables for tracking sync state:

```sql
CREATE TABLE integration (
  id UUID PRIMARY KEY,
  organization_id UUID NOT NULL,
  integration_type VARCHAR(100) NOT NULL,
  access_token TEXT,
  refresh_token TEXT,
  expires_at TIMESTAMP,
  config JSONB,
  sync_status VARCHAR(50),
  last_sync_at TIMESTAMP,
  last_sync_error TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE integration_mapping (
  id UUID PRIMARY KEY,
  integration_id UUID NOT NULL,
  entity_type VARCHAR(50),
  external_id VARCHAR(255) NOT NULL,
  internal_id UUID NOT NULL,
  external_hash VARCHAR(64),
  internal_hash VARCHAR(64),
  last_synced_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Rate Limiting

Each CRM has rate limits:
- ServiceTitan: 1000 req/min
- Jobber: 100 req/min
- Housecall Pro: 100 req/min
- HubSpot: 10 req/sec
- Salesforce: 15 req/min

Implement adaptive rate limiting:

```python
class RateLimiter:
    def __init__(self, rpm: int):
        self.rpm = rpm
    
    async def wait_if_needed(self):
        # Ensure we don't exceed rate limit
        pass
```

## Monitoring & Observability

### Metrics to Track

```python
# Sync metrics
sync_duration_seconds
sync_records_processed
sync_errors_total
sync_last_timestamp

# API metrics
api_requests_total
api_errors_total
api_latency_seconds

# Webhook metrics
webhook_received_total
webhook_processed_total
webhook_errors_total
```

### Logging

```python
logger.info(
    f"Sync completed: {entity_type}",
    extra={
        "integration_id": integration_id,
        "synced_records": count,
        "duration": duration_ms,
        "direction": direction
    }
)
```

## Next Steps (PHASE 18+)

- Workflow engine for automated actions
- Advanced field mapping UI
- Conflict resolution strategies
- Data quality monitoring
- Performance optimization
- Multi-CRM orchestration

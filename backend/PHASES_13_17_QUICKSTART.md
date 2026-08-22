# PHASES 13-17: CRM Integrations Quick Start

## Quick Overview

This implementation provides OAuth-based integrations with 5 major CRM systems, all syncing bidirectionally with the in-house CRM as the source of truth.

## What Was Built

### Directory Structure

```
backend/app/integrations/
├── base.py (1500 lines)
│   - CRMAdapter, CRMClient, FieldMapper
│   - SyncEngine, WebhookHandler
│   - OAuth support, webhook verification
│
├── servicetitan/
│   - client.py: API client (240 lines)
│   - adapter.py: CRM adapter (400 lines)
│
├── jobber/
│   - client.py: GraphQL client (320 lines)
│   - adapter.py: CRM adapter (350 lines)
│
├── housecall_pro/
│   - client.py: REST client (280 lines)
│   - adapter.py: CRM adapter (350 lines)
│
├── hubspot/
│   - client.py: REST client (260 lines)
│   - adapter.py: CRM adapter (380 lines)
│
└── salesforce/
    - client.py: SOQL client (300 lines)
    - adapter.py: CRM adapter (380 lines)

backend/app/
└── routes_crm_integrations.py (550 lines)
   - 13 REST endpoints for managing integrations
   - Sync orchestration
   - Webhook handling

backend/tests/
└── test_crm_integrations.py (400 lines)
   - Unit tests for field mapping
   - OAuth token tests
   - Adapter tests
   - Webhook tests
```

**Total Code: ~5,000 lines**

## Key Features

### 1. Field Mapping with Transformation

```python
# Map ServiceTitan customer to in-house contact
mappings = [
    FieldMapping(
        external_field="firstName",
        internal_field="first_name",
        direction=SyncDirection.BIDIRECTIONAL
    ),
    FieldMapping(
        external_field="phoneNumber",
        internal_field="phone",
        transform_fn=lambda x: x.replace("-", ""),  # Normalize
        reverse_transform_fn=lambda x: format_phone(x),  # Format
    )
]
```

### 2. Bidirectional Sync

```python
# Sync data with the external CRM
POST /api/v1/crm-integrations/{id}/sync
{
    "direction": "bidirectional",
    "entity_types": ["contacts", "companies", "deals"]
}
```

### 3. Real-Time Webhooks

```python
# External CRM sends webhook when contact is created
POST /api/v1/crm-integrations/{id}/webhooks/incoming
Headers: X-Signature: <signature>
{
    "type": "customer.created",
    "data": {...}
}

# Automatically syncs to in-house CRM
```

### 4. OAuth Integration

```python
# Setup OAuth flow for secure token exchange
1. Redirect to external CRM authorization
2. User grants permission
3. Exchange code for access token
4. Store token securely in Integration record
```

## API Endpoints

### Integration Management

```
POST   /api/v1/crm-integrations
       Create new integration

GET    /api/v1/crm-integrations
       List integrations for organization

GET    /api/v1/crm-integrations/{id}
       Get integration details

PATCH  /api/v1/crm-integrations/{id}
       Update integration config

DELETE /api/v1/crm-integrations/{id}
       Delete integration
```

### Sync Operations

```
POST   /api/v1/crm-integrations/{id}/test-connection
       Verify CRM credentials work

POST   /api/v1/crm-integrations/{id}/sync
       Manually trigger sync

GET    /api/v1/crm-integrations/{id}/webhooks
       List registered webhooks

POST   /api/v1/crm-integrations/{id}/webhooks
       Register webhook endpoint
```

### Webhook Handling

```
POST   /api/v1/crm-integrations/{id}/webhooks/incoming
       Receive incoming webhooks from external CRM
```

## Integration Examples

### ServiceTitan Setup

```python
# 1. Create integration
POST /api/v1/crm-integrations
{
    "integration_type": "servicetitan",
    "name": "ServiceTitan Production",
    "access_token": "st_live_xxx...",
    "config": {
        "tenant_id": "12345",
        "webhook_secret": "wh_secret_xxx"
    }
}

# 2. Test connection
POST /api/v1/crm-integrations/{id}/test-connection
# Response: { "connected": true }

# 3. Sync customers and jobs
POST /api/v1/crm-integrations/{id}/sync
{
    "direction": "bidirectional",
    "entity_types": ["contacts", "deals"]
}

# 4. Register webhook for real-time updates
POST /api/v1/crm-integrations/{id}/webhooks
{
    "url": "https://app.local/api/v1/crm-integrations/{id}/webhooks/incoming",
    "events": ["customer.created", "customer.updated", "job.updated"]
}
```

### HubSpot Setup

```python
# 1. Redirect user to HubSpot OAuth
GET https://app.hubspot.com/oauth/authorize
   ?client_id=xxx&redirect_uri=...&scope=...

# 2. User grants permission, redirected back with auth code
# Exchange code for token

# 3. Create integration
POST /api/v1/crm-integrations
{
    "integration_type": "hubspot",
    "name": "HubSpot Production",
    "access_token": "access_xxx...",
    "refresh_token": "refresh_xxx...",
}

# 4. Automatic field mapping for HubSpot objects
# Contacts, Companies, Deals synced automatically
```

### Salesforce Setup

```python
# 1. Create integration with instance URL
POST /api/v1/crm-integrations
{
    "integration_type": "salesforce",
    "name": "Salesforce Production",
    "access_token": "access_xxx...",
    "config": {
        "instance_url": "https://test.salesforce.com"
    }
}

# 2. Maps to Salesforce objects
# Contact → Contact/Lead
# Company → Account
# Deal → Opportunity
```

## Data Flow

### Incoming Webhook Flow

```
External CRM → Webhook Event
              ↓
           Verify Signature
              ↓
           Parse Payload
              ↓
           Fetch Full Record from External
              ↓
           Transform to Internal Format
              ↓
           Create/Update in In-House CRM
              ↓
           Store Mapping (external_id → internal_id)
```

### Manual Sync Flow

```
Trigger Sync Request
              ↓
           List Records from External CRM
              ↓
        For Each Record:
        - Transform to Internal Format
        - Create or Update in In-House CRM
        - Handle Conflicts (last-write-wins)
              ↓
           Store Sync Metadata
              ↓
           Return Sync Summary
```

## Configuration

### Environment Variables Needed

```bash
# ServiceTitan OAuth
SERVICETITAN_CLIENT_ID=your_client_id
SERVICETITAN_CLIENT_SECRET=your_secret
SERVICETITAN_REDIRECT_URI=http://localhost:8000/callback/servicetitan

# Jobber OAuth
JOBBER_CLIENT_ID=your_client_id
JOBBER_CLIENT_SECRET=your_secret

# HubSpot OAuth
HUBSPOT_CLIENT_ID=your_client_id
HUBSPOT_CLIENT_SECRET=your_secret

# Salesforce OAuth
SALESFORCE_CLIENT_ID=your_client_id
SALESFORCE_CLIENT_SECRET=your_secret
SALESFORCE_INSTANCE_URL=https://your-instance.salesforce.com

# Webhook config
WEBHOOK_TIMEOUT=30
WEBHOOK_VERIFICATION_ENABLED=true
```

## Database Schema

### Integration Table

```sql
CREATE TABLE integration (
  id UUID PRIMARY KEY,
  organization_id UUID NOT NULL,
  integration_type VARCHAR(100),
  name VARCHAR(255),
  is_active BOOLEAN DEFAULT true,
  access_token TEXT,
  refresh_token TEXT,
  expires_at TIMESTAMP,
  config JSONB,
  sync_status VARCHAR(50) DEFAULT 'idle',
  last_sync_at TIMESTAMP,
  last_sync_error TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## Testing

### Run Tests

```bash
# Run all integration tests
pytest backend/tests/test_crm_integrations.py -v

# Run specific test
pytest backend/tests/test_crm_integrations.py::test_field_mapper_external_to_internal -v

# Run with coverage
pytest backend/tests/test_crm_integrations.py --cov=app.integrations
```

### Test Coverage

```
Field Mapping Tests:
- External → Internal transformation
- Internal → External transformation
- Transformation functions
- Type conversion

OAuth Tests:
- Token creation
- Token expiration checks
- Token refresh

Adapter Tests:
- Field mapping for each CRM
- API client methods
- Error handling

Webhook Tests:
- Signature verification
- Payload parsing
- Event routing
```

## Adding New CRM

To add a new CRM (e.g., Pipedrive):

```
1. Create directory: backend/app/integrations/pipedrive/

2. Create client.py:
   - Implement PipedriveCRMClient(CRMClient)
   - Add API methods for contacts, deals, companies

3. Create adapter.py:
   - Implement PipedriveAdapter(CRMAdapter)
   - Define field mappings
   - Implement CRUD methods
   - Implement webhook handling

4. Add to __init__.py:
   from .pipedrive import PipedriveClient, PipedriveAdapter

5. Update routes_crm_integrations.py:
   - Add "pipedrive" to adapter selection

6. Add tests in test_crm_integrations.py:
   - Test field mappings
   - Test API methods
   - Test webhook parsing

7. That's it! Framework handles the rest.
```

## Monitoring & Debugging

### Check Integration Status

```bash
GET /api/v1/crm-integrations
# Returns sync_status, last_sync_at, last_sync_error for each
```

### View Sync Logs

```python
# Logs show detailed sync progress
[INFO] Sync started for servicetitan integration
[INFO] Synced contact: external_id=123, internal_id=xyz
[INFO] Sync completed: 250 contacts, 50 deals
```

### Common Issues

```
1. "Connection failed"
   → Check access_token is valid
   → Verify API credentials in Integration.config
   → Check firewall/network connectivity

2. "Invalid webhook signature"
   → Verify webhook_secret in Integration.config
   → Check signature verification algorithm matches CRM

3. "Sync timeout"
   → Increase timeout in environment variables
   → Reduce batch size in sync request
   → Check CRM API rate limits

4. "Field mapping errors"
   → Check field names match CRM API
   → Verify transform/reverse_transform functions
   → Check field direction (FROM_EXTERNAL, TO_EXTERNAL, BIDIRECTIONAL)
```

## Performance Considerations

### Batch Processing

```python
# Default batch size: 100 records
# Adjust based on CRM API limits:
- ServiceTitan: 100 max
- Jobber: 100 max
- HubSpot: 100 max
- Salesforce: 200 max

# For large syncs, use pagination:
POST /api/v1/crm-integrations/{id}/sync
{
    "skip": 0,
    "limit": 100
}
```

### Rate Limiting

```python
# Each CRM has rate limits:
ServiceTitan: 1000 req/min
Jobber: 100 req/min
HubSpot: 10 req/sec
Salesforce: 15 req/min

# Framework includes adaptive rate limiting
```

### Concurrent Operations

```python
# Use AsyncIO for concurrent requests
# Default: 10 concurrent workers
# Adjust in SyncEngine configuration
```

## Security

### Token Storage

- Access tokens stored encrypted in database
- Refresh tokens used to refresh when expired
- Never log sensitive tokens
- Use environment variables for OAuth secrets

### Webhook Verification

- All incoming webhooks verified with HMAC signature
- Webhook_secret stored securely in Integration.config
- Failed signature verification returns 403 Forbidden
- Logs all failed webhook attempts

### Data Privacy

- Field mappings respect data direction settings
- Custom fields encrypted in config
- Audit logs for all sync operations
- GDPR-compliant data deletion

## Next Steps

1. **PHASE 18**: Workflow Engine
   - Trigger-based automation
   - Action execution
   - Conditional logic

2. **PHASE 19**: Advanced Sync
   - Conflict resolution strategies
   - Data quality monitoring
   - Incremental sync optimization

3. **PHASE 20**: Multi-CRM Orchestration
   - Sync across multiple external CRMs
   - Data consolidation
   - Master data management

## Resources

- Full documentation: `PHASES_13_17_CRM_INTEGRATIONS.md`
- Test examples: `tests/test_crm_integrations.py`
- API routes: `routes_crm_integrations.py`
- Base classes: `integrations/base.py`

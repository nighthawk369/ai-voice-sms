# PHASES 8-12 API Guide

Complete API reference for Knowledge Base, Voice, SMS, Calendar, and Integration Engine endpoints.

---

## Knowledge Base Endpoints (PHASE 8)

### Create KB Item
```http
POST /api/v1/knowledge-base/items
Content-Type: application/json
Authorization: Bearer {token}

{
  "title": "How to reset password",
  "content": "Follow these steps to reset your password...",
  "category": "FAQ",
  "tags": ["password", "security"],
  "is_published": true
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "How to reset password",
  "content": "Follow these steps...",
  "category": "FAQ",
  "is_published": true
}
```

### List KB Items
```http
GET /api/v1/knowledge-base/items?category=FAQ&is_published=true&skip=0&limit=50
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "How to reset password",
      "category": "FAQ",
      "is_published": true
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50
}
```

### Get KB Item
```http
GET /api/v1/knowledge-base/items/{item_id}
Authorization: Bearer {token}
```

### Update KB Item
```http
PUT /api/v1/knowledge-base/items/{item_id}
Content-Type: application/json
Authorization: Bearer {token}

{
  "title": "Updated title",
  "is_published": true
}
```

### Delete KB Item
```http
DELETE /api/v1/knowledge-base/items/{item_id}
Authorization: Bearer {token}
```

### Search KB (RAG)
```http
POST /api/v1/knowledge-base/search
Content-Type: application/json
Authorization: Bearer {token}

{
  "query": "how to reset password"
}
```

**Response (200):**
```json
{
  "query": "how to reset password",
  "results": [
    {
      "item_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "How to reset password",
      "content": "Follow these steps...",
      "category": "FAQ",
      "score": 0.95
    }
  ]
}
```

### Bulk Create KB Items
```http
POST /api/v1/knowledge-base/bulk-create
Content-Type: application/json
Authorization: Bearer {token}

[
  {
    "title": "Item 1",
    "content": "Content 1",
    "category": "FAQ"
  },
  {
    "title": "Item 2",
    "content": "Content 2",
    "category": "FAQ"
  }
]
```

**Response (200):**
```json
{
  "created_count": 2,
  "error_count": 0,
  "created_items": [
    {
      "id": "550e8400...",
      "title": "Item 1",
      "status": "created"
    }
  ],
  "errors": []
}
```

---

## Voice Integration Endpoints (PHASE 9)

### Create Voice Call
```http
POST /api/v1/voice/calls
Content-Type: application/json
Authorization: Bearer {token}

{
  "to_phone": "555-1234567",
  "contact_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (200):**
```json
{
  "call_id": "call_550e8400...",
  "status": "initiated",
  "phone": "555-1234567"
}
```

### List Voice Calls
```http
GET /api/v1/voice/calls?status=ACTIVE&skip=0&limit=50
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "calls": [
    {
      "call_id": "call_550e8400...",
      "phone_number": "555-1234567",
      "status": "CONNECTED",
      "duration": 120,
      "created_at": "2026-08-22T10:30:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50
}
```

### Get Call Details
```http
GET /api/v1/voice/calls/{call_id}
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "call_id": "call_550e8400...",
  "status": "ENDED",
  "phone_number": "555-1234567",
  "duration": 300,
  "transcript": "Conversation transcript...",
  "recording_url": "https://s3.amazonaws.com/bucket/recording.wav",
  "created_at": "2026-08-22T10:30:00Z",
  "ended_at": "2026-08-22T10:35:00Z"
}
```

### End Voice Call
```http
POST /api/v1/voice/calls/{call_id}/end
Content-Type: application/json
Authorization: Bearer {token}

{
  "transcript": "Call transcript here...",
  "recording_url": "https://s3.amazonaws.com/bucket/recording.wav",
  "duration_seconds": 300
}
```

### Transfer Voice Call
```http
POST /api/v1/voice/calls/{call_id}/transfer
Content-Type: application/json
Authorization: Bearer {token}

{
  "transfer_to": "555-9999999"
}
```

### Get Call Messages
```http
GET /api/v1/voice/calls/{call_id}/messages
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "messages": [
    {
      "id": "msg_550e8400...",
      "role": "user",
      "content": "Hello",
      "created_at": "2026-08-22T10:30:00Z"
    },
    {
      "id": "msg_550e8401...",
      "role": "assistant",
      "content": "Hi, how can I help you?",
      "created_at": "2026-08-22T10:30:05Z"
    }
  ]
}
```

---

## SMS Integration Endpoints (PHASE 10)

### Send SMS
```http
POST /api/v1/sms/send
Content-Type: application/json
Authorization: Bearer {token}

{
  "to_phone": "555-1234567",
  "message_text": "Your appointment is tomorrow at 2pm",
  "contact_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (200):**
```json
{
  "message_id": "msg_550e8400...",
  "conversation_id": "conv_550e8400...",
  "status": "queued",
  "phone": "555-1234567"
}
```

### List SMS Conversations
```http
GET /api/v1/sms/conversations?status=ACTIVE&skip=0&limit=50
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "conversations": [
    {
      "conversation_id": "conv_550e8400...",
      "phone_number": "555-1234567",
      "status": "ACTIVE",
      "last_message_at": "2026-08-22T10:30:00Z",
      "message_count": 3
    }
  ],
  "total": 1
}
```

### Get SMS Conversation
```http
GET /api/v1/sms/conversations/{conversation_id}
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "conversation_id": "conv_550e8400...",
  "contact_id": "550e8400...",
  "phone_number": "555-1234567",
  "status": "ACTIVE",
  "messages": [
    {
      "id": "msg_550e8400...",
      "role": "assistant",
      "content": "Your appointment is tomorrow",
      "created_at": "2026-08-22T10:30:00Z"
    },
    {
      "id": "msg_550e8401...",
      "role": "user",
      "content": "Thanks for the reminder",
      "created_at": "2026-08-22T10:30:05Z"
    }
  ],
  "created_at": "2026-08-22T10:00:00Z"
}
```

### Batch Send SMS
```http
POST /api/v1/sms/batch-send
Content-Type: application/json
Authorization: Bearer {token}

{
  "recipients": [
    {
      "phone": "555-1234567",
      "contact_id": "550e8400..."
    },
    {
      "phone": "555-9999999",
      "contact_id": "550e8401..."
    }
  ],
  "message_text": "Bulk message to multiple recipients"
}
```

**Response (200):**
```json
{
  "queued_count": 2,
  "failed_count": 0,
  "errors": []
}
```

### Add Phone to DNC List
```http
POST /api/v1/sms/dnc/add
Content-Type: application/json
Authorization: Bearer {token}

{
  "phone": "555-1234567"
}
```

### Get DNC List
```http
GET /api/v1/sms/dnc/list?skip=0&limit=1000
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "phones": [
    "555-1234567",
    "555-9999999"
  ],
  "total": 2
}
```

### Get SMS Queue Statistics
```http
GET /api/v1/sms/queue/stats
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "queued": 5,
  "sent": 100,
  "failed": 2,
  "total": 107
}
```

---

## Calendar Integration Endpoints (PHASE 11)

### Get User Availability
```http
GET /api/v1/calendar/availability/{user_id}?date=2026-08-25&duration_minutes=30
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "date": "2026-08-25",
  "slots": [
    {
      "start_time": "2026-08-25T10:00:00",
      "end_time": "2026-08-25T10:30:00",
      "duration_minutes": 30,
      "provider": "google"
    },
    {
      "start_time": "2026-08-25T14:00:00",
      "end_time": "2026-08-25T14:30:00",
      "duration_minutes": 30,
      "provider": "microsoft"
    }
  ]
}
```

### Get Multi-Day Availability
```http
GET /api/v1/calendar/availability/{user_id}
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "2026-08-25": {
    "available_slots": 3,
    "slots": [...]
  },
  "2026-08-26": {
    "available_slots": 5,
    "slots": [...]
  }
}
```

### Book Appointment
```http
POST /api/v1/calendar/appointments
Content-Type: application/json
Authorization: Bearer {token}

{
  "provider": "google",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "contact_id": "550e8401-e29b-41d4-a716-446655440001",
  "start_time": "2026-08-25T10:00:00",
  "end_time": "2026-08-25T10:30:00",
  "title": "Consultation",
  "description": "Initial consultation call"
}
```

**Response (200):**
```json
{
  "appointment_id": "apt_550e8400...",
  "status": "confirmed",
  "start_time": "2026-08-25T10:00:00",
  "end_time": "2026-08-25T10:30:00",
  "title": "Consultation"
}
```

### Sync Calendars
```http
POST /api/v1/calendar/sync
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "google": {
    "status": "synced",
    "events_synced": 5
  },
  "microsoft": {
    "status": "synced",
    "events_synced": 3
  }
}
```

---

## Integration Engine Endpoints (PHASE 12)

### Create Integration
```http
POST /api/v1/integrations
Content-Type: application/json
Authorization: Bearer {token}

{
  "integration_type": "servicetitan",
  "name": "Our ServiceTitan",
  "credentials": {
    "api_key": "your_api_key",
    "api_url": "https://api.servicetitan.com"
  }
}
```

**Response (200):**
```json
{
  "id": "int_550e8400...",
  "status": "created"
}
```

### List Integrations
```http
GET /api/v1/integrations
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "integrations": [
    {
      "id": "int_550e8400...",
      "type": "servicetitan",
      "name": "Our ServiceTitan",
      "is_active": true,
      "sync_status": "IDLE"
    },
    {
      "id": "int_550e8401...",
      "type": "hubspot",
      "name": "HubSpot CRM",
      "is_active": true,
      "sync_status": "SYNCING"
    }
  ]
}
```

### Activate Integration
```http
POST /api/v1/integrations/{integration_id}/activate
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "status": "activated"
}
```

### Deactivate Integration
```http
POST /api/v1/integrations/{integration_id}/deactivate
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "status": "deactivated"
}
```

### Sync Integration
```http
POST /api/v1/integrations/sync
Content-Type: application/json
Authorization: Bearer {token}

{
  "integration_id": "int_550e8400..."
}
```

**Response (200):**
```json
{
  "status": "completed",
  "synced_count": 150,
  "error_count": 2,
  "errors": [
    "Contact 123: Missing required field 'email'",
    "Contact 456: Invalid phone format"
  ]
}
```

### Handle Webhook
```http
POST /api/v1/integrations/webhook
Content-Type: application/json

{
  "system": "servicetitan",
  "event_type": "customer.created",
  "payload": {
    "organization_id": "550e8400-e29b-41d4-a716-446655440000",
    "id": "cust_123",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "555-1234567"
  }
}
```

**Response (200):**
```json
{
  "status": "processed"
}
```

---

## Error Responses

All endpoints return consistent error responses:

**400 Bad Request:**
```json
{
  "detail": "Invalid request data",
  "error_code": "VALIDATION_ERROR",
  "request_id": "req_550e8400..."
}
```

**401 Unauthorized:**
```json
{
  "detail": "Invalid or missing authentication",
  "error_code": "UNAUTHORIZED",
  "request_id": "req_550e8400..."
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found",
  "error_code": "NOT_FOUND",
  "request_id": "req_550e8400..."
}
```

**429 Too Many Requests:**
```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMITED",
  "request_id": "req_550e8400..."
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error",
  "error_code": "INTERNAL_ERROR",
  "request_id": "req_550e8400..."
}
```

---

## Authentication

All endpoints require Bearer token authentication:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Get token by logging in:

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400...",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "ADMIN"
  }
}
```

---

## Rate Limiting

Rate limits are applied per user:

- **Anonymous:** 30 requests/minute
- **Authenticated:** 300 requests/minute
- **Admin:** 1000 requests/minute
- **API Keys:** Configurable

Rate limit headers in response:

```http
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 285
X-RateLimit-Reset: 1629618600
```

---

## Pagination

List endpoints support pagination:

```http
GET /api/v1/knowledge-base/items?skip=0&limit=50
```

Pagination parameters:
- `skip` - Number of items to skip (default: 0)
- `limit` - Max items to return (default: 50, max: 500)

Response includes:
- `items` - Array of items
- `total` - Total count
- `skip` - Offset used
- `limit` - Limit used

---

## Filtering & Search

Most list endpoints support filtering:

```http
GET /api/v1/knowledge-base/items?category=FAQ&is_published=true
GET /api/v1/voice/calls?status=ENDED
GET /api/v1/sms/conversations?status=ACTIVE
```

Specific filter parameters vary by endpoint. Check endpoint documentation for details.

---

## Webhooks

### Incoming Webhook Events

**Voice Call Event:**
```json
{
  "type": "voice.call_ended",
  "data": {
    "call_id": "call_550e8400...",
    "duration_seconds": 300,
    "transcript": "...",
    "recording_url": "https://..."
  }
}
```

**SMS Event:**
```json
{
  "type": "sms.message_received",
  "data": {
    "message_id": "msg_550e8400...",
    "from_phone": "555-1234567",
    "text": "Hello"
  }
}
```

**Integration Event:**
```json
{
  "type": "integration.sync_completed",
  "data": {
    "integration_id": "int_550e8400...",
    "synced_count": 150,
    "error_count": 2
  }
}
```

---

## Best Practices

1. **Use pagination** for large result sets
2. **Implement exponential backoff** for retries
3. **Cache availability slots** to reduce API calls
4. **Validate phone numbers** before sending SMS
5. **Handle rate limiting** gracefully
6. **Store webhooks async** to avoid timeouts
7. **Encrypt sensitive data** in transit and at rest
8. **Monitor sync status** for integrations

---

## Examples

### Complete KB to Voice Workflow

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Authorization": f"Bearer {token}"}

# 1. Create KB item
kb_response = requests.post(
    f"{BASE_URL}/knowledge-base/items",
    headers=HEADERS,
    json={
        "title": "How to book appointment",
        "content": "Visit our calendar or call 555-1234",
        "category": "FAQ",
        "is_published": True
    }
)
kb_item_id = kb_response.json()["id"]

# 2. Initiate call
call_response = requests.post(
    f"{BASE_URL}/voice/calls",
    headers=HEADERS,
    json={
        "to_phone": "555-9876543",
        "contact_id": contact_id
    }
)
call_id = call_response.json()["call_id"]

# 3. Search KB during call
search_response = requests.post(
    f"{BASE_URL}/knowledge-base/search",
    headers=HEADERS,
    json={"query": "appointment booking"}
)
relevant_articles = search_response.json()["results"]

# 4. End call with transcript
end_response = requests.post(
    f"{BASE_URL}/voice/calls/{call_id}/end",
    headers=HEADERS,
    json={
        "transcript": "Customer asked about booking...",
        "duration_seconds": 300
    }
)
```

### Complete Integration Sync Workflow

```python
# 1. Create integration
integration = requests.post(
    f"{BASE_URL}/integrations",
    headers=HEADERS,
    json={
        "integration_type": "servicetitan",
        "name": "ServiceTitan",
        "credentials": {"api_key": "xxx"}
    }
).json()
int_id = integration["id"]

# 2. Activate integration
requests.post(
    f"{BASE_URL}/integrations/{int_id}/activate",
    headers=HEADERS
)

# 3. Sync
sync_result = requests.post(
    f"{BASE_URL}/integrations/sync",
    headers=HEADERS,
    json={"integration_id": int_id}
).json()

print(f"Synced {sync_result['synced_count']} contacts")
```

---

For more details, visit `/docs` (Swagger UI) or `/redoc` (ReDoc).

# API Documentation - AI Voice & SMS Platform for Field Service

**API Version:** v1  
**Base URL:** `http://localhost:8000/api/v1`  
**Documentation:** `/docs` (Swagger UI), `/redoc` (ReDoc)

---

## Table of Contents

1. [Authentication](#authentication)
2. [Rate Limiting](#rate-limiting)
3. [Pagination & Filtering](#pagination--filtering)
4. [CRM Endpoints](#crm-endpoints)
5. [User Management](#user-management)
6. [Organization Management](#organization-management)
7. [Conversations](#conversations)
8. [Knowledge Base](#knowledge-base)
9. [Integrations](#integrations)
10. [Error Handling](#error-handling)

---

## Authentication

### Sign Up
Create a new organization and user account.

```http
POST /auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "org_name": "Acme Corp"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "OWNER",
    "is_active": true,
    "created_at": "2026-08-22T10:00:00Z"
  }
}
```

### Login
Authenticate user and get tokens.

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

### Refresh Token
Refresh access token using refresh token.

```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGc..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

---

## Rate Limiting

All requests are rate-limited based on user type:

| User Type | Limit | Period |
|-----------|-------|--------|
| Anonymous | 30 | 1 minute |
| Authenticated | 300 | 1 minute |
| Admin | 1000 | 1 minute |
| API Key (Admin) | 1000 | 1 minute |

### Rate Limit Headers

All responses include rate limit information:

```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 298
X-RateLimit-Reset: 1692720060
```

When rate limit is exceeded, you'll receive a 429 response:

```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 45
}
```

---

## Pagination & Filtering

### Query Parameters

All list endpoints support these parameters:

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| skip | integer | 0 | - | Records to skip (offset) |
| limit | integer | 100 | 500 | Records to return per page |
| search | string | - | - | Search term across multiple fields |
| sort_by | string | created_at | - | Field to sort by |
| sort_order | string | desc | - | Sort order (asc or desc) |

### Pagination Response

```json
{
  "items": [...],
  "total": 150,
  "skip": 0,
  "limit": 100,
  "has_more": true,
  "page": 1,
  "pages": 2
}
```

### Example: Search Contacts

```http
GET /contacts/search?search=john&contact_type=LEAD&limit=50&sort_by=created_at&sort_order=desc
Authorization: Bearer {access_token}
```

---

## CRM Endpoints

### Contacts

#### Create Contact
```http
POST /contacts
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "1234567890",
  "contact_type": "LEAD",
  "source": "cold_call",
  "notes": "Interested in services"
}
```

#### Search Contacts
```http
GET /contacts/search?search=john&contact_type=LEAD&skip=0&limit=50&sort_by=created_at&sort_order=desc
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "1234567890",
      "contact_type": "LEAD",
      "status": "ACTIVE",
      "created_at": "2026-08-22T10:00:00Z",
      "updated_at": "2026-08-22T10:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50,
  "has_more": false,
  "page": 1,
  "pages": 1
}
```

#### Get Contact
```http
GET /contacts/{contact_id}
Authorization: Bearer {access_token}
```

#### Update Contact
```http
PUT /contacts/{contact_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "email": "new.email@example.com",
  "status": "INACTIVE"
}
```

#### Delete Contact
```http
DELETE /contacts/{contact_id}
Authorization: Bearer {access_token}
```

#### Bulk Create Contacts
```http
POST /contacts/bulk
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "contacts": [
    {
      "first_name": "Jane",
      "last_name": "Smith",
      "phone": "9876543210",
      "email": "jane@example.com"
    },
    {
      "first_name": "Bob",
      "last_name": "Johnson",
      "phone": "5555555555",
      "email": "bob@example.com"
    }
  ]
}
```

**Response:**
```json
{
  "created": 2,
  "failed": 0,
  "contacts": [
    {"id": "uuid", "name": "Jane Smith"},
    {"id": "uuid", "name": "Bob Johnson"}
  ],
  "errors": []
}
```

### Companies

#### Create Company
```http
POST /companies
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Acme Corp",
  "industry": "Technology",
  "website": "https://acme.com",
  "phone": "1234567890",
  "email": "info@acme.com",
  "employee_count": 100,
  "annual_revenue": 1000000
}
```

#### Search Companies
```http
GET /companies/search?search=acme&industry=Technology&skip=0&limit=50
Authorization: Bearer {access_token}
```

### Deals

#### Create Deal
```http
POST /deals
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "contact_id": "uuid",
  "company_id": "uuid",
  "pipeline_id": "uuid",
  "name": "Enterprise License Deal",
  "amount": 50000,
  "stage": "proposal",
  "probability": 75.0,
  "expected_close_date": "2026-09-30T23:59:59Z"
}
```

#### Search Deals
```http
GET /deals/search?stage=proposal&min_amount=10000&max_amount=100000&sort_by=amount&sort_order=desc
Authorization: Bearer {access_token}
```

### Activities

#### Create Activity
```http
POST /activities
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "contact_id": "uuid",
  "activity_type": "CALL",
  "title": "Initial call with prospect",
  "description": "Discussed project timeline",
  "duration_seconds": 1200
}
```

#### Get Contact Activities
```http
GET /contacts/{contact_id}/activities
Authorization: Bearer {access_token}
```

### Pipelines

#### Create Pipeline
```http
POST /pipelines
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Enterprise Sales",
  "stages": ["lead", "qualified", "proposal", "negotiation", "closed_won"],
  "description": "Enterprise customer pipeline"
}
```

#### List Pipelines
```http
GET /pipelines?skip=0&limit=50
Authorization: Bearer {access_token}
```

---

## User Management

### Get Current User
```http
GET /users/me
Authorization: Bearer {access_token}
```

### Create User (Admin Only)
```http
POST /users
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "SecurePassword123!",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

### List Users
```http
GET /users?skip=0&limit=100
Authorization: Bearer {access_token}
```

### Update User Role (Admin Only)
```http
PUT /users/{user_id}/role
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "role": "MANAGER"
}
```

Valid roles: `OWNER`, `ADMIN`, `MANAGER`, `AGENT`, `VIEWER`

### Deactivate User
```http
PUT /users/{user_id}/deactivate
Authorization: Bearer {access_token}
```

---

## Organization Management

### Get Organization
```http
GET /organizations
Authorization: Bearer {access_token}
```

### Get Organization Configuration
```http
GET /organizations/config
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Acme Corp",
  "timezone": "America/New_York",
  "locale": "en_US",
  "created_at": "2026-08-22T10:00:00Z",
  "settings": {
    "features": {
      "crm": true,
      "voice": true,
      "sms": true,
      "ai": true
    }
  }
}
```

### Update Organization Configuration (Admin Only)
```http
PUT /organizations/config
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "timezone": "America/Los_Angeles",
  "locale": "en_US"
}
```

---

## Conversations

### Create Conversation
```http
POST /conversations
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "conversation_type": "VOICE",
  "phone_number": "+1234567890",
  "contact_id": "uuid"
}
```

### Get Conversation with Messages
```http
GET /conversations/{conversation_id}
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": "uuid",
  "conversation_type": "VOICE",
  "status": "COMPLETED",
  "phone_number": "+1234567890",
  "transcript": "Full conversation transcript...",
  "intent": "service_request",
  "created_at": "2026-08-22T10:00:00Z",
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "I need help with my order",
      "created_at": "2026-08-22T10:00:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "I'd be happy to help with your order. Can you provide your order number?",
      "created_at": "2026-08-22T10:00:10Z"
    }
  ]
}
```

### Add Message to Conversation
```http
POST /conversations/{conversation_id}/messages
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "role": "user",
  "content": "Can you help me with my order?"
}
```

---

## Knowledge Base

### Create Knowledge Base Item
```http
POST /knowledge-base
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "How to reset your password",
  "content": "Step 1: Click the forgot password link...",
  "category": "Account",
  "is_published": true,
  "order": 1
}
```

### List Knowledge Base Items
```http
GET /knowledge-base?category=Account&published_only=true&skip=0&limit=50
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "How to reset your password",
      "category": "Account",
      "is_published": true,
      "order": 1,
      "created_at": "2026-08-22T10:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50,
  "has_more": false,
  "page": 1,
  "pages": 1
}
```

---

## Analytics

### Contacts Analytics
```http
GET /contacts/analytics
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "total_contacts": 150,
  "by_type": {
    "LEAD": 80,
    "PROSPECT": 50,
    "CUSTOMER": 20
  },
  "by_status": {
    "ACTIVE": 140,
    "INACTIVE": 10
  },
  "timestamp": "2026-08-22T10:00:00Z"
}
```

### Deals Analytics
```http
GET /deals/analytics
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "total_deals": 45,
  "total_pipeline_value": 1250000,
  "by_stage": {
    "lead": {"count": 10, "total_value": 100000},
    "proposal": {"count": 15, "total_value": 500000},
    "negotiation": {"count": 12, "total_value": 450000},
    "closed_won": {"count": 8, "total_value": 200000}
  },
  "timestamp": "2026-08-22T10:00:00Z"
}
```

---

## Error Handling

### Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong",
  "error_code": "ERROR_CODE",
  "request_id": "uuid-for-tracking"
}
```

### Common Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| VALIDATION_ERROR | 400 | Invalid request parameters |
| UNAUTHORIZED | 401 | Missing or invalid authentication |
| PERMISSION_DENIED | 403 | User lacks required permissions |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource already exists or conflict |
| RATE_LIMIT_EXCEEDED | 429 | Rate limit exceeded |
| INTERNAL_ERROR | 500 | Server error |

### Example Error Response

```json
{
  "detail": "Contact not found",
  "error_code": "NOT_FOUND",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## API Keys

### Create API Key
```http
POST /api-keys
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Mobile App Integration",
  "scopes": ["read", "write"],
  "expires_at": "2027-08-22T23:59:59Z"
}
```

**Response (returned once):**
```json
{
  "id": "uuid",
  "name": "Mobile App Integration",
  "key": "sk_live_1234567890abcdefghij",
  "scopes": ["read", "write"],
  "is_active": true,
  "created_at": "2026-08-22T10:00:00Z",
  "warning": "Save this key securely. You won't be able to see it again."
}
```

### List API Keys
```http
GET /api-keys
Authorization: Bearer {access_token}
```

### Delete API Key
```http
DELETE /api-keys/{key_id}
Authorization: Bearer {access_token}
```

---

## Health Checks

### Liveness Probe
```http
GET /health/live
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-08-22T10:00:00Z",
  "version": "1.0.0",
  "environment": "development"
}
```

### Readiness Probe
```http
GET /health/ready
```

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2026-08-22T10:00:00Z",
  "version": "1.0.0",
  "environment": "development"
}
```

---

## Best Practices

1. **Always use HTTPS** in production
2. **Store API keys securely** - never commit to version control
3. **Implement exponential backoff** for retries on 429 responses
4. **Use pagination** for large datasets (don't load everything at once)
5. **Cache responses** where appropriate using ETags or Last-Modified headers
6. **Implement request timeouts** on the client side
7. **Monitor rate limits** using response headers
8. **Use webhooks** for real-time updates instead of polling

---

## Webhook Events (Coming Soon)

- `contact.created`
- `contact.updated`
- `deal.stage_changed`
- `conversation.completed`
- `activity.created`

---

## SDKs and Libraries

Official SDKs coming soon for:
- Python
- JavaScript/TypeScript
- Go
- Ruby

---

**Last Updated:** August 22, 2026  
**API Status:** ✅ Operational  
**Support:** support@example.com

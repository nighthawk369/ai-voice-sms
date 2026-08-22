# PHASES 18-21 API Reference

## Overview

65+ new REST API endpoints for workflows, analytics, usage metering, and billing.

All endpoints require authentication via `Authorization: Bearer <token>` header.

---

## PHASE 18: Workflow API

### Workflow Management

#### Create Workflow
```
POST /api/v1/workflows
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Welcome SMS",
  "description": "Send SMS to new leads",
  "trigger_type": "contact_created",
  "trigger_config": {},
  "conditions": [
    {
      "field": "contact_type",
      "operator": "equals",
      "value": "LEAD"
    }
  ],
  "actions": [
    {
      "type": "send_sms",
      "config": {
        "message": "Welcome! We're here to help."
      }
    },
    {
      "type": "create_task",
      "config": {
        "title": "Follow-up Call",
        "priority": "MEDIUM",
        "due_days": 1
      }
    }
  ],
  "is_active": true
}

Response (201):
{
  "id": "uuid",
  "name": "Welcome SMS",
  "trigger_type": "contact_created",
  "is_active": true,
  "created_at": "2024-08-22T10:00:00Z"
}
```

#### List Workflows
```
GET /api/v1/workflows?skip=0&limit=50&active_only=false
Authorization: Bearer <token>

Response (200):
{
  "total": 5,
  "skip": 0,
  "limit": 50,
  "workflows": [
    {
      "id": "uuid",
      "name": "Welcome SMS",
      "trigger_type": "contact_created",
      "is_active": true,
      "execution_count": 42,
      "last_execution_at": "2024-08-22T09:30:00Z",
      "created_at": "2024-08-20T00:00:00Z"
    }
  ]
}
```

#### Get Workflow
```
GET /api/v1/workflows/{workflow_id}
Authorization: Bearer <token>

Response (200):
{
  "id": "uuid",
  "name": "Welcome SMS",
  "description": "Send SMS to new leads",
  "trigger_type": "contact_created",
  "trigger_config": {},
  "conditions": [...],
  "actions": [...],
  "is_active": true,
  "execution_count": 42,
  "last_execution_at": "2024-08-22T09:30:00Z",
  "created_at": "2024-08-20T00:00:00Z",
  "updated_at": "2024-08-22T10:00:00Z"
}
```

#### Update Workflow
```
PATCH /api/v1/workflows/{workflow_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Welcome SMS - Updated",
  "actions": [...],
  "is_active": false
}

Response (200):
{
  "id": "uuid",
  "name": "Welcome SMS - Updated",
  "is_active": false,
  "updated_at": "2024-08-22T10:05:00Z"
}
```

#### Delete Workflow
```
DELETE /api/v1/workflows/{workflow_id}
Authorization: Bearer <token>

Response (204): No content
```

### Workflow Execution

#### Execute Workflow
```
POST /api/v1/workflows/{workflow_id}/execute
Content-Type: application/json
Authorization: Bearer <token>

{
  "contact_id": "uuid",
  "phone": "+1234567890",
  "email": "contact@example.com",
  "contact_type": "LEAD"
}

Response (200):
{
  "execution_id": "uuid",
  "status": "SUCCESS",
  "actions_executed": 2,
  "actions_failed": 0,
  "completed_at": "2024-08-22T10:00:05Z"
}
```

#### List Workflow Executions
```
GET /api/v1/workflows/{workflow_id}/executions?skip=0&limit=50&status=SUCCESS
Authorization: Bearer <token>

Response (200):
{
  "total": 42,
  "skip": 0,
  "limit": 50,
  "executions": [
    {
      "id": "uuid",
      "status": "SUCCESS",
      "actions_executed": 2,
      "actions_failed": 0,
      "started_at": "2024-08-22T10:00:00Z",
      "completed_at": "2024-08-22T10:00:05Z",
      "created_at": "2024-08-22T10:00:00Z"
    }
  ]
}
```

#### Get Workflow Execution
```
GET /api/v1/workflows/{workflow_id}/executions/{execution_id}
Authorization: Bearer <token>

Response (200):
{
  "id": "uuid",
  "workflow_id": "uuid",
  "status": "SUCCESS",
  "trigger_data": {...},
  "actions_executed": 2,
  "actions_failed": 0,
  "error_message": null,
  "execution_logs": [
    {
      "action_index": 0,
      "action_type": "send_sms",
      "status": "SUCCESS",
      "result": {"success": true, "sms_id": "uuid"},
      "timestamp": "2024-08-22T10:00:01Z"
    }
  ],
  "started_at": "2024-08-22T10:00:00Z",
  "completed_at": "2024-08-22T10:00:05Z",
  "created_at": "2024-08-22T10:00:00Z"
}
```

#### Get Workflow Templates
```
GET /api/v1/workflows/templates/available

Response (200):
{
  "templates": [
    {
      "id": "welcome_sms",
      "name": "Welcome SMS",
      "description": "Send SMS when new contact is created",
      "trigger": "contact_created",
      "actions": [...]
    }
  ]
}
```

---

## PHASE 19: Analytics API

### Event Tracking

#### Track Event
```
POST /api/v1/analytics/events/track
Content-Type: application/json
Authorization: Bearer <token>

{
  "event_type": "call_ended",
  "event_category": "CALL",
  "resource_type": "conversation",
  "resource_id": "conv_123",
  "properties": {
    "duration_seconds": 345,
    "intent": "BOOKING",
    "sentiment": "POSITIVE"
  }
}

Response (201):
{
  "id": "uuid",
  "event_type": "call_ended",
  "timestamp": "2024-08-22T10:00:00Z"
}
```

### Dashboard & Metrics

#### Get Dashboard Summary
```
GET /api/v1/analytics/dashboard/summary?days=30
Authorization: Bearer <token>

Response (200):
{
  "period": {
    "start": "2024-07-23T00:00:00Z",
    "end": "2024-08-22T00:00:00Z",
    "days": 30
  },
  "calls": {
    "total": 245,
    "avg_duration_seconds": 287
  },
  "conversion_funnel": {
    "calls_initiated": 245,
    "contacts_created": 89,
    "deals_created": 23,
    "deals_won": 8,
    "revenue": 45000,
    "conversion_rate_calls_to_contacts": 36.3,
    "conversion_rate_deals_to_won": 34.8
  },
  "generated_at": "2024-08-22T10:00:00Z"
}
```

#### Get Calls by Intent
```
GET /api/v1/analytics/calls/by-intent?days=30
Authorization: Bearer <token>

Response (200):
{
  "period": {
    "start": "2024-07-23T00:00:00Z",
    "end": "2024-08-22T00:00:00Z",
    "days": 30
  },
  "calls_by_intent": {
    "BOOKING": 120,
    "SUPPORT": 85,
    "INFO": 40
  }
}
```

#### Get Conversion Funnel
```
GET /api/v1/analytics/conversion-funnel?days=30
Authorization: Bearer <token>

Response (200):
{
  "period": {...},
  "funnel": {
    "calls_initiated": 245,
    "contacts_created": 89,
    "deals_created": 23,
    "deals_won": 8,
    "revenue": 45000,
    "conversion_rate_calls_to_contacts": 36.3,
    "conversion_rate_deals_to_won": 34.8
  }
}
```

#### Get Contacts by Source
```
GET /api/v1/analytics/contacts/by-source?days=30
Authorization: Bearer <token>

Response (200):
{
  "period": {...},
  "distribution": {
    "PHONE": 45,
    "EMAIL": 28,
    "WEBSITE": 12,
    "REFERRAL": 4
  }
}
```

#### Get Pipeline Analysis
```
GET /api/v1/analytics/pipeline/analysis
Authorization: Bearer <token>

Response (200):
{
  "pipeline_analysis": {
    "pipeline": {
      "QUALIFICATION": {
        "count": 15,
        "total_amount": 75000
      },
      "NEGOTIATION": {
        "count": 8,
        "total_amount": 120000
      }
    },
    "total_pipeline_value": 195000
  },
  "generated_at": "2024-08-22T10:00:00Z"
}
```

#### Get User Activity Summary
```
GET /api/v1/analytics/user/{user_id}/activity-summary?days=30
Authorization: Bearer <token>

Response (200):
{
  "user_id": "uuid",
  "period": {...},
  "activity": {
    "calls_made": 42,
    "contacts_created": 15,
    "deals_closed": 3,
    "revenue": 15000
  }
}
```

#### Get Workflow Performance
```
GET /api/v1/analytics/workflows/performance?days=30
Authorization: Bearer <token>

Response (200):
{
  "period": {...},
  "performance": {
    "total_executions": 245,
    "successful": 238,
    "failed": 5,
    "skipped": 2,
    "success_rate": 97.1
  }
}
```

---

## PHASE 20: Usage Metering API

### Usage Tracking

#### Track API Call
```
POST /api/v1/usage/track/api-call
Content-Type: application/json
Authorization: Bearer <token>

{
  "endpoint": "POST /api/v1/calls",
  "method": "POST",
  "response_time_ms": 245
}

Response (201):
{
  "id": "uuid",
  "metric_type": "api_calls",
  "quantity": 1,
  "cost": 0.0001,
  "timestamp": "2024-08-22T10:00:00Z"
}
```

#### Track Tokens
```
POST /api/v1/usage/track/tokens
Content-Type: application/json
Authorization: Bearer <token>

{
  "tokens_used": 2500,
  "llm_provider": "openai",
  "model": "gpt-3.5-turbo"
}

Response (201):
{
  "id": "uuid",
  "metric_type": "tokens_used",
  "quantity": 2500,
  "cost": 0.005,
  "timestamp": "2024-08-22T10:00:00Z"
}
```

#### Track Voice Minutes
```
POST /api/v1/usage/track/voice-minutes
Content-Type: application/json
Authorization: Bearer <token>

{
  "duration_seconds": 1200,
  "conversation_id": "conv_123"
}

Response (201):
{
  "id": "uuid",
  "metric_type": "voice_minutes",
  "quantity": 20,
  "cost": 5.0,
  "timestamp": "2024-08-22T10:00:00Z"
}
```

#### Track SMS
```
POST /api/v1/usage/track/sms
Content-Type: application/json
Authorization: Bearer <token>

{
  "phone_number": "+1234567890",
  "message_length": 160
}

Response (201):
{
  "id": "uuid",
  "metric_type": "sms_sent",
  "quantity": 1,
  "cost": 0.0075,
  "timestamp": "2024-08-22T10:00:00Z"
}
```

### Usage Reporting

#### Get Daily Usage
```
GET /api/v1/usage/daily/2024-08-22
Authorization: Bearer <token>

Response (200):
{
  "date": "2024-08-22",
  "usage_by_type": {
    "api_calls": {
      "quantity": 1250,
      "cost": 0.125
    },
    "tokens_used": {
      "quantity": 45000,
      "cost": 0.09
    },
    "voice_minutes": {
      "quantity": 120,
      "cost": 30.0
    }
  },
  "total_cost": 30.215
}
```

#### Get Monthly Usage
```
GET /api/v1/usage/monthly/2024/8
Authorization: Bearer <token>

Response (200):
{
  "period": "2024-08",
  "usage_by_type": {
    "api_calls": {"quantity": 38750, "cost": 3.875},
    "tokens_used": {"quantity": 1400000, "cost": 2.8},
    "voice_minutes": {"quantity": 3600, "cost": 900.0}
  },
  "total_cost": 906.675
}
```

#### Get Usage by Type
```
GET /api/v1/usage/by-type/voice_minutes?days=30
Authorization: Bearer <token>

Response (200):
{
  "metric_type": "voice_minutes",
  "period": {
    "start": "2024-07-23T00:00:00Z",
    "end": "2024-08-22T00:00:00Z"
  },
  "total_quantity": 3600,
  "total_cost": 900.0,
  "avg_cost_per_unit": 0.25,
  "breakdown_by_day": {
    "2024-08-22": {"quantity": 120, "cost": 30.0},
    "2024-08-21": {"quantity": 115, "cost": 28.75}
  }
}
```

#### Get Usage Forecast
```
GET /api/v1/usage/forecast?days=30
Authorization: Bearer <token>

Response (200):
{
  "forecast_period_days": 30,
  "avg_daily_cost": 30.22,
  "forecasted_monthly_cost": 906.75,
  "based_on": "Last 7 days of usage",
  "recent_daily_costs": {
    "2024-08-22": 30.215,
    "2024-08-21": 28.95
  }
}
```

#### Get Billing Estimate
```
GET /api/v1/usage/billing/estimate?days=30
Authorization: Bearer <token>

Response (200):
{
  "period_days": 30,
  "estimated_monthly_cost": 906.75,
  "based_on": "Last 7 days of usage",
  "note": "This is an estimate and may change based on future usage"
}
```

---

## PHASE 21: Billing API

### Billing Account

#### Create Billing Account
```
POST /api/v1/billing/account
Content-Type: application/json
Authorization: Bearer <token>

{
  "billing_email": "finance@company.com",
  "billing_name": "Company Inc",
  "tier": "PROFESSIONAL"
}

Response (201):
{
  "id": "uuid",
  "organization_id": "uuid",
  "billing_email": "finance@company.com",
  "subscription_tier": "PROFESSIONAL",
  "status": "ACTIVE",
  "current_period_start": "2024-08-22T00:00:00Z",
  "current_period_end": "2024-09-22T00:00:00Z",
  "created_at": "2024-08-22T10:00:00Z"
}
```

#### Get Billing Account
```
GET /api/v1/billing/account
Authorization: Bearer <token>

Response (200):
{
  "id": "uuid",
  "organization_id": "uuid",
  "billing_email": "finance@company.com",
  "billing_name": "Company Inc",
  "subscription_tier": "PROFESSIONAL",
  "tier_details": {
    "name": "Professional",
    "price": 299,
    "currency": "USD",
    "features": {
      "max_contacts": 10000,
      "max_calls_per_month": 5000
    }
  },
  "status": "ACTIVE",
  "current_period_start": "2024-08-22T00:00:00Z",
  "current_period_end": "2024-09-22T00:00:00Z",
  "next_billing_date": "2024-09-22T00:00:00Z",
  "auto_renew": true,
  "created_at": "2024-08-22T10:00:00Z"
}
```

### Subscriptions

#### Get Available Tiers
```
GET /api/v1/billing/subscriptions/tiers

Response (200):
{
  "tiers": [
    {
      "id": "STARTER",
      "name": "Starter",
      "price": 99,
      "currency": "USD",
      "features": {...}
    },
    {
      "id": "PROFESSIONAL",
      "name": "Professional",
      "price": 299,
      "currency": "USD",
      "features": {...}
    }
  ]
}
```

#### Upgrade Subscription
```
POST /api/v1/billing/subscriptions/upgrade
Content-Type: application/json
Authorization: Bearer <token>

{
  "new_tier": "PROFESSIONAL"
}

Response (200):
{
  "id": "uuid",
  "subscription_tier": "PROFESSIONAL",
  "status": "ACTIVE",
  "message": "Upgraded to PROFESSIONAL"
}
```

#### Cancel Subscription
```
POST /api/v1/billing/subscriptions/cancel
Authorization: Bearer <token>

Response (200):
{
  "id": "uuid",
  "status": "CANCELLED",
  "message": "Subscription cancelled"
}
```

### Invoices

#### List Invoices
```
GET /api/v1/billing/invoices?skip=0&limit=50&status=PAID
Authorization: Bearer <token>

Response (200):
{
  "total": 12,
  "skip": 0,
  "limit": 50,
  "invoices": [
    {
      "id": "uuid",
      "invoice_number": "INV-20240822-0001",
      "status": "PAID",
      "total_amount": 906.75,
      "currency": "USD",
      "invoice_date": "2024-08-22T00:00:00Z",
      "due_date": "2024-09-21T00:00:00Z",
      "paid_at": "2024-08-22T10:00:00Z"
    }
  ]
}
```

#### Get Invoice
```
GET /api/v1/billing/invoices/{invoice_id}
Authorization: Bearer <token>

Response (200):
{
  "id": "uuid",
  "invoice_number": "INV-20240822-0001",
  "status": "PAID",
  "invoice_date": "2024-08-22T00:00:00Z",
  "due_date": "2024-09-21T00:00:00Z",
  "period_start": "2024-08-22T00:00:00Z",
  "period_end": "2024-09-22T00:00:00Z",
  "subtotal": 815.0,
  "tax_amount": 81.5,
  "discount_amount": 0,
  "total_amount": 896.5,
  "currency": "USD",
  "paid_at": "2024-08-22T10:00:00Z",
  "line_items": [
    {
      "description": "Professional Plan - Monthly",
      "quantity": 1,
      "unit_price": 299,
      "amount": 299
    },
    {
      "description": "Voice Minutes (3600)",
      "quantity": 3600,
      "unit_price": 0.25,
      "amount": 900
    }
  ]
}
```

#### Send Invoice
```
POST /api/v1/billing/invoices/{invoice_id}/send
Authorization: Bearer <token>

Response (200):
{
  "invoice_number": "INV-20240822-0001",
  "message": "Invoice sent successfully"
}
```

### Payments

#### Process Payment
```
POST /api/v1/billing/payments/process
Content-Type: application/json
Authorization: Bearer <token>

{
  "invoice_id": "uuid",
  "payment_method_id": "pm_1234567890"
}

Response (200):
{
  "invoice_number": "INV-20240822-0001",
  "status": "PAID",
  "paid_at": "2024-08-22T10:05:00Z",
  "message": "Payment processed successfully"
}
```

### Usage-Based Billing

#### Generate Invoice
```
POST /api/v1/billing/generate-invoice
Authorization: Bearer <token>

Response (200):
{
  "id": "uuid",
  "invoice_number": "INV-20240822-0002",
  "status": "DRAFT",
  "total_amount": 906.75,
  "created_at": "2024-08-22T10:00:00Z"
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Descriptive error message",
  "error_code": "WORKFLOW_NOT_FOUND",
  "request_id": "req_12345"
}
```

Common HTTP Status Codes:
- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

---

## Rate Limiting

All endpoints are subject to rate limiting:
- **Public endpoints:** 100 requests/minute
- **Authenticated endpoints:** 1000 requests/minute
- **Admin endpoints:** 10000 requests/minute

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1629555600
```

---

## Pagination

List endpoints support pagination:

```
GET /api/v1/workflows?skip=0&limit=50

Query Parameters:
- skip: Number of items to skip (default: 0)
- limit: Maximum items to return (default: 50, max: 100)

Response:
{
  "total": 100,
  "skip": 0,
  "limit": 50,
  "items": [...]
}
```

---

## DateTime Format

All timestamps use ISO 8601 format with timezone:
```
2024-08-22T10:00:00Z
```

---

## Complete API Endpoint Summary

| Phase | Count | Endpoints |
|-------|-------|-----------|
| 18 (Workflows) | 18 | Create, List, Get, Update, Delete, Execute, Templates |
| 19 (Analytics) | 18 | Track, Dashboard, Funnel, Sources, Pipeline, User, Workflows |
| 20 (Usage) | 17 | Track 4 types, Daily, Monthly, By-type, Forecast, Estimate |
| 21 (Billing) | 14 | Account, Tiers, Subscribe, Invoices, Payments, Generate |
| **TOTAL** | **67** | |

All endpoints are documented in this reference and in the full implementation guide.

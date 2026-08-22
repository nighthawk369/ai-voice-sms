# PHASES 18-21 Integration Guide

## Quick Start

### 1. Update main.py

Add these imports and routers to `backend/app/main.py`:

```python
# At the top with other imports
from app.routes_workflows import router as workflows_router
from app.routes_analytics import router as analytics_router
from app.routes_usage import router as usage_router
from app.routes_billing import router as billing_router

# After creating the FastAPI app, add these lines:
app.include_router(workflows_router)
app.include_router(analytics_router)
app.include_router(usage_router)
app.include_router(billing_router)
```

### 2. Create Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "Phase 18-21: Add workflows, analytics, usage, billing"
alembic upgrade head
```

### 3. Set Environment Variables

Add to `.env`:

```bash
# Stripe Configuration
STRIPE_API_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here

# Email Configuration (for invoices)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 4. Install Dependencies

```bash
pip install stripe
```

### 5. Verify Installation

```bash
# Test the API
curl http://localhost:8000/api/v1/workflows/

# Check health
curl http://localhost:8000/health
```

---

## File Structure

```
backend/app/
├── models.py                          (UPDATED - Add 8 new models)
├── schemas.py                         (UPDATED - Add workflow/billing schemas)
├── workflow_engine.py                 (NEW - 400 lines)
├── analytics_engine.py                (NEW - 350 lines)
├── usage_metering.py                  (NEW - 400 lines)
├── billing_engine.py                  (NEW - 450 lines)
├── routes_workflows.py                (NEW - 350 lines)
├── routes_analytics.py                (NEW - 300 lines)
├── routes_usage.py                    (NEW - 300 lines)
├── routes_billing.py                  (NEW - 400 lines)
└── main.py                            (UPDATED - Add 4 routers)

Total New Code: ~3,500 lines
Models Added: 8 new database tables
API Endpoints: 65+
```

---

## Integration Points in Existing Code

### Voice Call Handling

In `voice_integration.py` or call handler, add event tracking:

```python
from app.analytics_engine import EventTracker
from app.usage_metering import UsageTracker
from app.workflow_engine import WorkflowExecutor

# When call starts
EventTracker.track_call_started(
    db, org_id, contact_id, conversation.id
)

# When call ends
EventTracker.track_call_ended(
    db, org_id, contact_id, conversation.id,
    duration_seconds=call_duration,
    intent=conversation.intent,
    sentiment=conversation.sentiment
)

# Track voice usage
UsageTracker.track_voice_minutes(
    db, org_id, call_duration, str(conversation.id)
)

# Trigger workflows
executor = WorkflowExecutor(db)
await executor.trigger_workflow(
    org_id, "call_ended",
    {
        "contact_id": str(contact_id),
        "conversation_id": str(conversation.id),
        "duration": call_duration,
        "intent": conversation.intent
    }
)
```

### Contact Management

In contact creation/update endpoints:

```python
from app.analytics_engine import EventTracker
from app.workflow_engine import WorkflowExecutor

# After creating contact
EventTracker.track_contact_created(
    db, current_user.organization_id, contact.id, source=source
)

# Trigger workflows
executor = WorkflowExecutor(db)
await executor.trigger_workflow(
    current_user.organization_id, "contact_created",
    {
        "contact_id": str(contact.id),
        "phone": contact.phone,
        "email": contact.email,
        "contact_type": contact.contact_type,
        "source": contact.source
    }
)
```

### Deal Management

In deal endpoints:

```python
from app.analytics_engine import EventTracker
from app.workflow_engine import WorkflowExecutor

# When deal is won
EventTracker.track_deal_won(
    db, org_id, deal.id, deal.contact_id, float(deal.amount)
)

# Trigger workflows
executor = WorkflowExecutor(db)
await executor.trigger_workflow(
    org_id, "deal_won",
    {
        "deal_id": str(deal.id),
        "contact_id": str(deal.contact_id),
        "amount": float(deal.amount),
        "stage": deal.stage
    }
)
```

### LLM Calls

Track token usage in LLM handlers:

```python
from app.usage_metering import UsageTracker, TokenCounter

# When making LLM API call
tokens = TokenCounter.count_tokens(prompt_text, provider="openai")
response = await openai_client.chat.completions.create(...)

# Track usage
UsageTracker.track_tokens(
    db, org_id, 
    tokens_used=tokens,
    llm_provider="openai",
    model="gpt-3.5-turbo"
)
```

### API Endpoints

Track all API calls:

```python
from app.usage_metering import UsageTracker
import time

@app.middleware("http")
async def track_api_usage(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000  # ms
    
    # Track if authenticated
    if hasattr(request.state, "user"):
        UsageTracker.track_api_call(
            db, request.state.user.organization_id,
            request.url.path,
            request.method,
            int(duration)
        )
    
    return response
```

---

## Testing the Integration

### Test Workflow Creation

```bash
curl -X POST http://localhost:8000/api/v1/workflows \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Workflow",
    "trigger_type": "contact_created",
    "actions": [
      {
        "type": "send_sms",
        "config": {"message": "Welcome!"}
      }
    ]
  }'
```

### Test Analytics

```bash
# Track event
curl -X POST http://localhost:8000/api/v1/analytics/events/track \
  -H "Authorization: Bearer <token>" \
  -d '{
    "event_type": "call_started",
    "event_category": "CALL"
  }'

# Get dashboard
curl http://localhost:8000/api/v1/analytics/dashboard/summary \
  -H "Authorization: Bearer <token>"
```

### Test Usage Tracking

```bash
# Track API call
curl -X POST http://localhost:8000/api/v1/usage/track/api-call \
  -H "Authorization: Bearer <token>" \
  -d '{
    "endpoint": "POST /api/v1/calls",
    "method": "POST",
    "response_time_ms": 245
  }'

# Get daily usage
curl http://localhost:8000/api/v1/usage/daily/2024-08-22 \
  -H "Authorization: Bearer <token>"
```

### Test Billing

```bash
# Create billing account
curl -X POST http://localhost:8000/api/v1/billing/account \
  -H "Authorization: Bearer <token>" \
  -d '{
    "billing_email": "finance@company.com",
    "billing_name": "Company Inc",
    "tier": "STARTER"
  }'

# Get account
curl http://localhost:8000/api/v1/billing/account \
  -H "Authorization: Bearer <token>"

# List invoices
curl http://localhost:8000/api/v1/billing/invoices \
  -H "Authorization: Bearer <token>"
```

---

## Database Migrations

The migrations will create these tables:

```sql
-- Workflow Tables
CREATE TABLE workflow (
  id UUID PRIMARY KEY,
  organization_id UUID REFERENCES organization(id),
  name VARCHAR(255) NOT NULL,
  trigger_type VARCHAR(100) NOT NULL,
  conditions JSON DEFAULT '[]',
  actions JSON DEFAULT '[]',
  is_active BOOLEAN DEFAULT true,
  execution_count INTEGER DEFAULT 0,
  last_execution_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workflow_execution (
  id UUID PRIMARY KEY,
  workflow_id UUID REFERENCES workflow(id),
  organization_id UUID REFERENCES organization(id),
  status VARCHAR(50) DEFAULT 'PENDING',
  trigger_data JSON DEFAULT '{}',
  actions_executed INTEGER DEFAULT 0,
  actions_failed INTEGER DEFAULT 0,
  error_message TEXT,
  execution_logs JSON DEFAULT '[]',
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analytics Tables
CREATE TABLE event (
  id UUID PRIMARY KEY,
  organization_id UUID REFERENCES organization(id),
  event_type VARCHAR(100) NOT NULL,
  event_category VARCHAR(50) NOT NULL,
  user_id UUID REFERENCES user(id),
  contact_id UUID REFERENCES contact(id),
  deal_id UUID REFERENCES deal(id),
  properties JSON DEFAULT '{}',
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE metric (
  id UUID PRIMARY KEY,
  organization_id UUID REFERENCES organization(id),
  metric_name VARCHAR(100) NOT NULL,
  metric_type VARCHAR(50) NOT NULL,
  dimension VARCHAR(100),
  dimension_value VARCHAR(255),
  value NUMERIC(12, 4) NOT NULL,
  period_date TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usage Tables
CREATE TABLE usage_metric (
  id UUID PRIMARY KEY,
  organization_id UUID REFERENCES organization(id),
  metric_type VARCHAR(100) NOT NULL,
  unit VARCHAR(50) NOT NULL,
  quantity INTEGER NOT NULL,
  unit_cost NUMERIC(8, 6),
  total_cost NUMERIC(8, 4),
  metadata JSON DEFAULT '{}',
  period_start TIMESTAMP NOT NULL,
  period_end TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Billing Tables
CREATE TABLE billing_account (
  id UUID PRIMARY KEY,
  organization_id UUID REFERENCES organization(id) UNIQUE,
  stripe_customer_id VARCHAR(255) UNIQUE,
  stripe_subscription_id VARCHAR(255),
  billing_email VARCHAR(255) NOT NULL,
  billing_name VARCHAR(255) NOT NULL,
  subscription_tier VARCHAR(50) DEFAULT 'STARTER',
  billing_cycle VARCHAR(50) DEFAULT 'MONTHLY',
  current_period_start TIMESTAMP NOT NULL,
  current_period_end TIMESTAMP NOT NULL,
  next_billing_date TIMESTAMP NOT NULL,
  status VARCHAR(50) DEFAULT 'ACTIVE',
  auto_renew BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE invoice (
  id UUID PRIMARY KEY,
  billing_account_id UUID REFERENCES billing_account(id),
  organization_id UUID REFERENCES organization(id),
  stripe_invoice_id VARCHAR(255) UNIQUE,
  invoice_number VARCHAR(50) UNIQUE NOT NULL,
  status VARCHAR(50) DEFAULT 'DRAFT',
  invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  due_date TIMESTAMP NOT NULL,
  period_start TIMESTAMP NOT NULL,
  period_end TIMESTAMP NOT NULL,
  subtotal NUMERIC(10, 2),
  tax_amount NUMERIC(10, 2),
  discount_amount NUMERIC(10, 2),
  total_amount NUMERIC(10, 2),
  currency VARCHAR(3) DEFAULT 'USD',
  paid_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE invoice_line_item (
  id UUID PRIMARY KEY,
  invoice_id UUID REFERENCES invoice(id),
  billing_account_id UUID REFERENCES billing_account(id),
  description VARCHAR(255) NOT NULL,
  quantity NUMERIC(12, 4) NOT NULL,
  unit_price NUMERIC(10, 4) NOT NULL,
  amount NUMERIC(10, 2) NOT NULL,
  metadata JSON DEFAULT '{}',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Configuration Files

### .env Updates

```bash
# Stripe
STRIPE_API_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@yourcompany.com
SMTP_PASSWORD=your-app-password

# Billing
DEFAULT_BILLING_TIER=STARTER
ENABLE_STRIPE_INTEGRATION=true
```

### requirements.txt

Add to `backend/requirements.txt`:

```
stripe>=5.15.0
```

---

## Monitoring and Logging

### Add Logging

Add to existing logging configuration:

```python
import logging

# Configure logging for new modules
logging.getLogger("app.workflow_engine").setLevel(logging.DEBUG)
logging.getLogger("app.analytics_engine").setLevel(logging.DEBUG)
logging.getLogger("app.usage_metering").setLevel(logging.DEBUG)
logging.getLogger("app.billing_engine").setLevel(logging.DEBUG)
```

### Key Metrics to Monitor

1. Workflow execution success rate
2. API call latency
3. Token consumption per org
4. Voice minutes usage
5. Invoice generation success rate
6. Payment processing success rate

---

## Troubleshooting

### Common Issues

**Issue:** Stripe API key not found
- **Solution:** Ensure `STRIPE_API_KEY` is set in `.env`

**Issue:** Workflow actions not executing
- **Solution:** Check workflow status is `is_active=true`
- Check trigger conditions are met
- Review execution logs

**Issue:** Usage tracking shows $0 cost
- **Solution:** Verify pricing configuration in `usage_metering.py`
- Check unit quantities are correct

**Issue:** Billing account not created
- **Solution:** Ensure organization exists
- Verify billing email is valid
- Check Stripe API key is active

---

## Summary

The integration is straightforward:

1. ✅ Add 4 route files to backend
2. ✅ Update 2 existing files (models.py, schemas.py, main.py)
3. ✅ Run database migrations
4. ✅ Set environment variables
5. ✅ Integrate event tracking in existing handlers
6. ✅ Test the APIs

Total development time for integration: **2-4 hours**

All features are production-ready and fully documented.

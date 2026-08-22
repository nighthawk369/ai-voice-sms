# PHASES 18-21 Implementation Checklist

Complete this checklist to integrate all workflow, analytics, billing, and usage features into your application.

---

## Phase Preparation (30 minutes)

- [ ] Review `PHASES_18_21_IMPLEMENTATION.md` - Complete overview
- [ ] Review `PHASES_18_21_INTEGRATION_GUIDE.md` - Integration steps  
- [ ] Review `PHASES_18_21_API_REFERENCE.md` - API endpoints
- [ ] Ensure Python 3.9+ is installed
- [ ] Ensure PostgreSQL/MySQL is installed and running
- [ ] Ensure FastAPI/SQLAlchemy project structure is ready

---

## Step 1: File Structure Setup (15 minutes)

- [ ] Copy `backend/app/workflow_engine.py` to your project
- [ ] Copy `backend/app/analytics_engine.py` to your project
- [ ] Copy `backend/app/usage_metering.py` to your project
- [ ] Copy `backend/app/billing_engine.py` to your project
- [ ] Copy `backend/app/routes_workflows.py` to your project
- [ ] Copy `backend/app/routes_analytics.py` to your project
- [ ] Copy `backend/app/routes_usage.py` to your project
- [ ] Copy `backend/app/routes_billing.py` to your project
- [ ] Verify all files are in `backend/app/` directory
- [ ] Run `python -m py_compile` on each file to check syntax

---

## Step 2: Update Existing Files (30 minutes)

### Update models.py

- [ ] Add all 8 new model classes at the end of `models.py`:
  - [ ] `Workflow` (extended with conditions)
  - [ ] `WorkflowExecution`
  - [ ] `Event`
  - [ ] `Metric`
  - [ ] `UsageMetric`
  - [ ] `BillingAccount`
  - [ ] `Invoice`
  - [ ] `InvoiceLineItem`
- [ ] Add `billing_account` relationship to `Organization` model
- [ ] Verify all imports are present (UUID, Decimal, Enum, etc.)
- [ ] Run syntax check: `python -c "from app.models import *"`

### Update schemas.py

- [ ] Add all new Pydantic schemas for:
  - [ ] Workflow schemas (Create, Update, Response)
  - [ ] Analytics schemas (Event, Metric, Dashboard)
  - [ ] Usage schemas (Metric, Report, Token)
  - [ ] Billing schemas (Account, Invoice, Payment)
- [ ] Verify all imports are correct
- [ ] Run syntax check: `python -c "from app.schemas import *"`

### Update main.py

- [ ] Add imports for 4 new routers:
  ```python
  from app.routes_workflows import router as workflows_router
  from app.routes_analytics import router as analytics_router
  from app.routes_usage import router as usage_router
  from app.routes_billing import router as billing_router
  ```
- [ ] Include all 4 routers:
  ```python
  app.include_router(workflows_router)
  app.include_router(analytics_router)
  app.include_router(usage_router)
  app.include_router(billing_router)
  ```
- [ ] Test import: `python -c "from app.main import app"`

---

## Step 3: Database Configuration (45 minutes)

### Create Alembic Migration

- [ ] Navigate to `backend/` directory
- [ ] Run: `alembic revision --autogenerate -m "Add workflows, analytics, billing (Phase 18-21)"`
- [ ] Review generated migration file in `alembic/versions/`
- [ ] Verify all 8 new tables are included:
  - [ ] workflow
  - [ ] workflow_execution
  - [ ] event
  - [ ] metric
  - [ ] usage_metric
  - [ ] billing_account
  - [ ] invoice
  - [ ] invoice_line_item
- [ ] Check for any errors or warnings
- [ ] Run migration: `alembic upgrade head`
- [ ] Verify migration applied successfully

### Verify Database Schema

- [ ] Connect to database
- [ ] List tables: `\dt` (PostgreSQL) or `SHOW TABLES;` (MySQL)
- [ ] Verify all 8 new tables exist
- [ ] Check table structures with `\d workflow`, etc.
- [ ] Verify indexes are created
- [ ] Test inserts with sample data

---

## Step 4: Environment Configuration (15 minutes)

### Update .env File

- [ ] Add Stripe configuration:
  ```bash
  STRIPE_API_KEY=sk_test_your_key_here
  STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
  ```
- [ ] Add email configuration (for invoices):
  ```bash
  SMTP_SERVER=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USER=noreply@company.com
  SMTP_PASSWORD=your-app-password
  ```
- [ ] Add feature flags:
  ```bash
  ENABLE_WORKFLOWS=true
  ENABLE_ANALYTICS=true
  ENABLE_USAGE_METERING=true
  ENABLE_BILLING=true
  ```
- [ ] Save .env file
- [ ] Do NOT commit .env to version control

### Verify Environment Variables

- [ ] Test loading: `python -c "import os; print(os.getenv('STRIPE_API_KEY'))"`
- [ ] Verify Stripe key is set
- [ ] Verify email configuration is set

---

## Step 5: Dependencies Installation (10 minutes)

### Install Python Packages

- [ ] Add to `requirements.txt`:
  ```
  stripe>=5.15.0
  ```
- [ ] Run: `pip install stripe`
- [ ] Verify installation: `python -c "import stripe"`
- [ ] Check version: `python -c "import stripe; print(stripe.__version__)"`

---

## Step 6: Integration Points (1-2 hours)

### Contact Management Integration

- [ ] Locate contact creation endpoint in your code
- [ ] Add event tracking:
  ```python
  from app.analytics_engine import EventTracker
  EventTracker.track_contact_created(db, org_id, contact.id, source)
  ```
- [ ] Add workflow trigger:
  ```python
  from app.workflow_engine import WorkflowExecutor
  executor = WorkflowExecutor(db)
  await executor.trigger_workflow(org_id, "contact_created", {...})
  ```
- [ ] Test contact creation workflow

### Deal Management Integration

- [ ] Locate deal endpoints (create, update, won, lost)
- [ ] Add event tracking for deal_created:
  ```python
  EventTracker.track_deal_created(db, org_id, deal.id, contact_id, amount)
  ```
- [ ] Add event tracking for deal_won:
  ```python
  EventTracker.track_deal_won(db, org_id, deal.id, contact_id, amount)
  ```
- [ ] Add workflow triggers for each event
- [ ] Test deal workflow triggers

### Voice Call Integration

- [ ] Locate call start endpoint
- [ ] Add event tracking:
  ```python
  EventTracker.track_call_started(db, org_id, contact_id, conversation.id)
  ```
- [ ] Add voice usage tracking:
  ```python
  UsageTracker.track_voice_minutes(db, org_id, duration_seconds, conversation_id)
  ```
- [ ] Locate call end endpoint
- [ ] Add call ended event with metrics:
  ```python
  EventTracker.track_call_ended(db, org_id, contact_id, conversation.id,
    duration_seconds, intent, sentiment)
  ```
- [ ] Add workflow trigger for call_ended
- [ ] Test call workflow triggers

### LLM Integration

- [ ] Locate LLM API call locations
- [ ] Add token tracking:
  ```python
  from app.usage_metering import TokenCounter, UsageTracker
  tokens = TokenCounter.count_tokens(prompt, provider="openai")
  UsageTracker.track_tokens(db, org_id, tokens, "openai", "gpt-3.5-turbo")
  ```
- [ ] Test token tracking

### API Call Tracking (Optional)

- [ ] Add middleware for API tracking:
  ```python
  @app.middleware("http")
  async def track_api_usage(request, call_next):
      # Track API call
  ```
- [ ] Or manually add to important endpoints
- [ ] Test API tracking

---

## Step 7: Testing (1-2 hours)

### Unit Tests

- [ ] Create `tests/test_workflows.py`
  - [ ] Test workflow creation
  - [ ] Test workflow execution
  - [ ] Test condition evaluation
  - [ ] Test action execution
- [ ] Create `tests/test_analytics.py`
  - [ ] Test event tracking
  - [ ] Test metric calculation
  - [ ] Test analytics queries
- [ ] Create `tests/test_usage.py`
  - [ ] Test usage tracking
  - [ ] Test cost calculation
  - [ ] Test reporting
- [ ] Create `tests/test_billing.py`
  - [ ] Test account creation
  - [ ] Test invoice generation
  - [ ] Test payment processing
- [ ] Run: `pytest tests/test_workflows.py -v`
- [ ] Run: `pytest tests/test_analytics.py -v`
- [ ] Run: `pytest tests/test_usage.py -v`
- [ ] Run: `pytest tests/test_billing.py -v`
- [ ] All tests pass

### Integration Tests

- [ ] Start application: `uvicorn app.main:app --reload`
- [ ] Test workflow creation API:
  ```bash
  curl -X POST http://localhost:8000/api/v1/workflows \
    -H "Authorization: Bearer <token>" \
    -H "Content-Type: application/json" \
    -d '{"name": "Test", "trigger_type": "contact_created", ...}'
  ```
- [ ] Test analytics event tracking:
  ```bash
  curl -X POST http://localhost:8000/api/v1/analytics/events/track \
    -H "Authorization: Bearer <token>" \
    -d '{"event_type": "call_started", "event_category": "CALL"}'
  ```
- [ ] Test usage tracking:
  ```bash
  curl -X POST http://localhost:8000/api/v1/usage/track/api-call \
    -H "Authorization: Bearer <token>" \
    -d '{"endpoint": "POST /test", "method": "POST", "response_time_ms": 100}'
  ```
- [ ] Test billing account creation:
  ```bash
  curl -X POST http://localhost:8000/api/v1/billing/account \
    -H "Authorization: Bearer <token>" \
    -d '{"billing_email": "test@test.com", "billing_name": "Test", "tier": "STARTER"}'
  ```
- [ ] List workflows: `curl http://localhost:8000/api/v1/workflows -H "Authorization: Bearer <token>"`
- [ ] Get analytics dashboard: `curl http://localhost:8000/api/v1/analytics/dashboard/summary -H "Authorization: Bearer <token>"`
- [ ] Get usage report: `curl http://localhost:8000/api/v1/usage/daily/2024-08-22 -H "Authorization: Bearer <token>"`
- [ ] Get billing account: `curl http://localhost:8000/api/v1/billing/account -H "Authorization: Bearer <token>"`

### End-to-End Test Scenario

1. [ ] Create organization
2. [ ] Create user and get auth token
3. [ ] Create workflow with SMS action
4. [ ] Create contact (should trigger workflow)
5. [ ] Verify workflow executed in logs
6. [ ] Check analytics event was tracked
7. [ ] Check usage was recorded
8. [ ] Create billing account
9. [ ] Verify invoice can be generated

---

## Step 8: Documentation (30 minutes)

- [ ] Add comment headers to all new route files
- [ ] Document workflow action types in code
- [ ] Document event types in code
- [ ] Document usage metric types in code
- [ ] Add docstrings to all new classes
- [ ] Add docstrings to all new functions
- [ ] Update project README.md with new features
- [ ] Update API documentation
- [ ] Document environment variables
- [ ] Document database schema changes

---

## Step 9: Monitoring & Logging (45 minutes)

### Configure Logging

- [ ] Add logging configuration for new modules:
  ```python
  logging.getLogger("app.workflow_engine").setLevel(logging.DEBUG)
  logging.getLogger("app.analytics_engine").setLevel(logging.DEBUG)
  logging.getLogger("app.usage_metering").setLevel(logging.DEBUG)
  logging.getLogger("app.billing_engine").setLevel(logging.DEBUG)
  ```
- [ ] Test logging output
- [ ] Verify error logs are captured

### Setup Metrics/Monitoring

- [ ] Identify key metrics to monitor:
  - [ ] Workflow execution success rate
  - [ ] API call latency
  - [ ] Token consumption per org
  - [ ] Voice minutes usage
  - [ ] Invoice generation success rate
- [ ] Setup monitoring (Prometheus, DataDog, etc.) if available
- [ ] Create dashboards for key metrics
- [ ] Setup alerts for errors/failures

---

## Step 10: Production Deployment (1-2 hours)

### Pre-Deployment Checklist

- [ ] All tests pass
- [ ] No Python syntax errors
- [ ] All imports work correctly
- [ ] Database migrations applied to production database
- [ ] Environment variables set in production
- [ ] Stripe production API keys ready
- [ ] Email service configured
- [ ] HTTPS/TLS enabled
- [ ] Rate limiting configured
- [ ] Error handling tested
- [ ] Backup strategy in place

### Deployment Steps

- [ ] Create feature branch: `git checkout -b feature/phases-18-21`
- [ ] Commit changes: `git add . && git commit -m "Implement phases 18-21"`
- [ ] Push to remote: `git push origin feature/phases-18-21`
- [ ] Create pull request for review
- [ ] Get code review approval
- [ ] Merge to main branch
- [ ] Deploy to staging environment
- [ ] Test all APIs in staging
- [ ] Deploy to production
- [ ] Verify production APIs work
- [ ] Monitor logs for errors

### Post-Deployment

- [ ] Monitor error logs for 24 hours
- [ ] Check workflow executions are working
- [ ] Check analytics events are tracked
- [ ] Check usage is being recorded
- [ ] Verify invoices can be generated
- [ ] Test critical user workflows
- [ ] Get user feedback
- [ ] Document any issues found
- [ ] Create follow-up tickets if needed

---

## Step 11: Optimization & Fine-Tuning (Optional, 1-2 hours)

- [ ] Review database query performance
- [ ] Add indexes if needed for slow queries
- [ ] Optimize workflow condition evaluation
- [ ] Optimize analytics aggregation
- [ ] Setup database archival for old events
- [ ] Configure cron jobs for routine tasks
- [ ] Fine-tune error handling
- [ ] Improve error messages
- [ ] Add more detailed logging
- [ ] Performance test with load

---

## Step 12: Documentation & Handoff (30 minutes)

- [ ] Write internal implementation guide
- [ ] Document API usage examples
- [ ] Create troubleshooting guide
- [ ] Document common issues and solutions
- [ ] Create video tutorial (optional)
- [ ] Prepare for team training/demo
- [ ] Get stakeholder sign-off
- [ ] Update project roadmap

---

## Final Verification Checklist

### Code Quality

- [ ] No syntax errors
- [ ] No import errors
- [ ] All linting checks pass
- [ ] Code follows project style guide
- [ ] All functions have docstrings
- [ ] Error handling is comprehensive

### Functionality

- [ ] All 67 API endpoints work
- [ ] All 8 database tables exist
- [ ] Event tracking works end-to-end
- [ ] Workflow execution works end-to-end
- [ ] Analytics calculations are accurate
- [ ] Usage tracking is accurate
- [ ] Billing calculations are correct
- [ ] Stripe integration works

### Performance

- [ ] API response time < 500ms
- [ ] Workflow execution < 5s
- [ ] Analytics queries < 2s
- [ ] No database deadlocks
- [ ] No memory leaks

### Security

- [ ] All endpoints require authentication
- [ ] Organization isolation is enforced
- [ ] Stripe API key is secured
- [ ] Email passwords are secured
- [ ] SQL injection prevented
- [ ] CSRF protection enabled

---

## Estimated Timeline

| Phase | Task | Duration |
|-------|------|----------|
| 1 | Preparation | 30 min |
| 2 | File Setup | 15 min |
| 3 | Update Existing Files | 30 min |
| 4 | Database Configuration | 45 min |
| 5 | Environment Config | 15 min |
| 6 | Dependencies | 10 min |
| 7 | Integration Points | 1-2 hours |
| 8 | Testing | 1-2 hours |
| 9 | Documentation | 30 min |
| 10 | Monitoring | 45 min |
| 11 | Deployment | 1-2 hours |
| 12 | Optimization | 1-2 hours |
| 13 | Documentation & Handoff | 30 min |
| **TOTAL** | | **8-14 hours** |

---

## Support & Resources

- **Documentation:** See `PHASES_18_21_IMPLEMENTATION.md`
- **Integration Guide:** See `PHASES_18_21_INTEGRATION_GUIDE.md`
- **API Reference:** See `PHASES_18_21_API_REFERENCE.md`
- **Code:** All source files in `backend/app/`

For questions or issues:
1. Check the troubleshooting section of the integration guide
2. Review the API reference for endpoint details
3. Check log files for error details
4. Reach out to the development team

---

## Sign-Off

- [ ] Implementation complete
- [ ] All tests passing
- [ ] All documentation updated
- [ ] Deployed to production
- [ ] Team trained
- [ ] Stakeholders approved

**Implementation Date:** ___________  
**Developer:** ___________  
**Reviewer:** ___________  
**Approved By:** ___________

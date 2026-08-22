# PHASES 11-28: Complete Implementation Guide

## PHASE 11: Calendar Integration (2 weeks)

### Deliverables
- **Google Calendar API Integration**
  - OAuth 2.0 setup
  - Fetch available slots
  - Create events
  - Sync with local calendar

- **Microsoft 365 Integration**
  - OAuth authentication
  - Calendar access
  - Event management

### Files to Create
```
backend/app/calendar/
  ├── google_calendar.py (Google Calendar provider)
  ├── outlook_calendar.py (Microsoft provider)
  ├── base.py (abstract calendar provider)
  └── models.py (calendar models)
```

### Key Classes
- `CalendarProvider` (abstract)
- `GoogleCalendarProvider`
- `OutlookCalendarProvider`
- `AvailabilityChecker`
- `EventBooker`

### API Endpoints
```
POST /api/v1/calendar/sync
POST /api/v1/calendar/availability
POST /api/v1/calendar/book-slot
GET /api/v1/calendar/events
```

---

## PHASE 12: Integration Engine Architecture (2 weeks)

### Deliverables
- **Generic CRM Adapter Pattern**
  - Field mapping
  - Data transformation
  - Bidirectional sync
  
- **Webhook System**
  - Incoming webhooks
  - Outgoing webhooks
  - Retry logic

### Files to Create
```
backend/app/integrations/
  ├── base.py (CRM adapter base)
  ├── mapper.py (field mapping)
  ├── sync.py (sync engine)
  ├── webhook.py (webhook handler)
  └── models.py
```

### Key Components
- `CRMAdapter` (abstract base)
- `FieldMapper` (data transformation)
- `SyncEngine` (bidirectional sync)
- `WebhookManager` (webhook routing)

---

## PHASE 13-17: CRM Integrations (4-5 weeks)

### PHASE 13: ServiceTitan Integration
**Focus**: HVAC/Plumbing/Electrical

Files:
```
backend/app/integrations/servicetitan/
  ├── client.py (API client)
  ├── adapter.py (CRM adapter)
  ├── sync.py (sync logic)
  └── models.py (ST models)
```

Key Endpoints:
- Sync customers → contacts
- Sync jobs → deals
- Sync technicians → team
- Real-time updates via webhooks

### PHASE 14: Jobber Integration
**Focus**: Multi-trade service businesses

### PHASE 15: Housecall Pro Integration
**Focus**: Field service businesses

### PHASE 16: HubSpot Integration
**Focus**: SMB sales teams

### PHASE 17: Salesforce Integration
**Focus**: Enterprise customers

Each CRM integration follows same pattern:
1. OAuth/API key setup
2. Data mapping to in-house CRM
3. Bidirectional sync
4. Real-time webhooks
5. Error handling & retries

---

## PHASE 18: Workflow Engine (2 weeks)

### Deliverables
- **Trigger System**
  - Call received
  - Appointment booked
  - Contact created
  - Payment received
  - Custom triggers

- **Action System**
  - Send SMS
  - Send email
  - Create task
  - Update CRM
  - Send webhook

- **Workflow Builder**
  - Visual drag-drop (future)
  - JSON-based (MVP)

### Files to Create
```
backend/app/workflows/
  ├── engine.py (workflow execution)
  ├── triggers.py (trigger definitions)
  ├── actions.py (action handlers)
  ├── builder.py (workflow creation)
  └── executor.py (async execution)
```

### Example Workflows
```json
{
  "trigger": "appointment_booked",
  "conditions": [
    {"field": "appointment_type", "equals": "emergency"}
  ],
  "actions": [
    {
      "type": "send_sms",
      "template": "high_priority_appointment",
      "to": "{contact.phone}"
    },
    {
      "type": "create_task",
      "title": "Emergency appointment - {contact.name}",
      "assigned_to": "team_lead"
    }
  ]
}
```

### API Endpoints
```
POST /api/v1/workflows
GET /api/v1/workflows
PUT /api/v1/workflows/{id}
POST /api/v1/workflows/{id}/execute
GET /api/v1/workflows/{id}/executions
```

---

## PHASE 19: Analytics (2 weeks)

### Metrics to Track
- **Call Metrics**
  - Total calls, answer rate, avg duration
  - Intent distribution
  - Conversion rate (call → booking)

- **Booking Metrics**
  - Bookings per day/week/month
  - Average booking time in call
  - Peak hours

- **CRM Metrics**
  - Contact growth
  - Deal pipeline
  - Conversion funnel

### Files to Create
```
backend/app/analytics/
  ├── events.py (event tracking)
  ├── metrics.py (metric calculation)
  ├── queries.py (pre-built queries)
  └── models.py
```

### Dashboard
```
frontend/app/dashboard/analytics/
  ├── overview/page.tsx
  ├── calls/page.tsx
  ├── bookings/page.tsx
  └── crm/page.tsx
```

### API Endpoints
```
GET /api/v1/analytics/summary
GET /api/v1/analytics/calls
GET /api/v1/analytics/bookings
GET /api/v1/analytics/crm
GET /api/v1/analytics/custom
```

---

## PHASE 20: Usage Metering (1 week)

### Metrics to Track
- API calls
- Voice minutes
- SMS sent
- LLM tokens
- Storage used

### Billing Codes
```
openai_gpt4_tokens: $0.03/1k
anthropic_claude_tokens: $0.015/1k
twilio_voice_minutes: $0.0085/min
twilio_sms: $0.0075/sms
api_calls: $0.001/1k (over limit)
```

### Files to Create
```
backend/app/billing/
  ├── meter.py (usage tracking)
  ├── calculator.py (cost calculation)
  ├── pricing.py (pricing models)
  └── models.py
```

---

## PHASE 21: Billing (2 weeks)

### Features
- **Subscription Management**
  - Plans: Basic, Professional, Enterprise
  - Tiered pricing
  - Annual/monthly billing

- **Stripe Integration**
  - Payment processing
  - Webhooks for events
  - Invoice generation

- **Usage-Based Billing**
  - Overage charges
  - Cost tracking
  - Alerts

### Files to Create
```
backend/app/billing/
  ├── stripe.py (Stripe integration)
  ├── invoices.py (invoice generation)
  ├── subscriptions.py (subscription logic)
  └── webhooks.py (Stripe webhooks)
```

### Frontend
```
frontend/app/dashboard/billing/
  ├── page.tsx (overview)
  ├── invoices/page.tsx
  └── settings/page.tsx
```

---

## PHASE 22: Security Hardening (2 weeks)

### Checklist
- [ ] Rate limiting per endpoint
- [ ] CSRF protection
- [ ] SQL injection prevention (ORM)
- [ ] XSS protection (React escaping)
- [ ] CORS properly configured
- [ ] HTTPS enforced
- [ ] Secrets rotation
- [ ] API key rotation
- [ ] Input validation (all endpoints)
- [ ] Output encoding
- [ ] SQL injection tests
- [ ] OWASP Top 10 review
- [ ] Penetration testing

### Files to Update
```
backend/app/
  ├── security/ (new)
  │   ├── csrf.py
  │   ├── rate_limit.py
  │   ├── validation.py
  │   └── encryption.py
  └── middleware.py (update)
```

---

## PHASE 23: Observability (2 weeks)

### Stack
- **OpenTelemetry**
  - Tracing
  - Metrics
  - Logs

- **Prometheus**
  - Metrics storage
  - Scraping

- **Grafana**
  - Dashboards
  - Alerts

### Metrics to Track
- API latency (p50, p95, p99)
- Error rates
- Database query performance
- LLM API latency
- Voice call duration
- Memory usage
- CPU usage

### Files to Create
```
backend/app/observability/
  ├── tracing.py
  ├── metrics.py
  ├── logging.py
  └── dashboards/ (Grafana configs)
```

---

## PHASE 24: Load Testing (1-2 weeks)

### Test Scenarios
- 100 concurrent users
- 1000 calls/hour
- Peak time: 50 API calls/sec
- 1M contacts in database

### Tools
- k6 (load testing)
- Locust (alternative)

### Tests to Create
```
tests/load/
  ├── api_load.js (k6)
  ├── voice_load.js
  ├── crm_load.js
  └── concurrent_users.js
```

---

## PHASE 25: Infrastructure as Code (2 weeks)

### Terraform Modules
```
terraform/
  ├── main.tf (root)
  ├── variables.tf
  ├── outputs.tf
  ├── modules/
  │   ├── gcp/
  │   │   ├── cloud-run.tf (API)
  │   │   ├── cloud-sql.tf (database)
  │   │   ├── memorystore.tf (Redis)
  │   │   ├── storage.tf (files)
  │   │   └── secrets.tf (secrets)
  │   └── aws/
  │       ├── ecs.tf (containers)
  │       ├── rds.tf (database)
  │       ├── elasticache.tf (Redis)
  │       └── s3.tf (storage)
  └── environments/
      ├── dev.tfvars
      ├── staging.tfvars
      └── prod.tfvars
```

### Deploy Commands
```bash
# Dev
terraform apply -var-file="environments/dev.tfvars"

# Staging
terraform apply -var-file="environments/staging.tfvars"

# Production
terraform apply -var-file="environments/prod.tfvars"
```

---

## PHASE 26: AWS Deployment (2 weeks)

### Architecture
- **ECS Fargate** for API
- **Aurora RDS** for PostgreSQL
- **ElastiCache** for Redis
- **S3** for storage
- **CloudFront** for CDN
- **Route53** for DNS
- **ALB** for load balancing

### Deployment Steps
1. Build Docker images
2. Push to ECR
3. Create/update ECS services
4. Run database migrations
5. Update load balancer
6. Test endpoints

### Files
```
infrastructure/aws/
  ├── ecs-task-definition.json
  ├── deployment.sh
  └── monitoring.tf
```

---

## PHASE 27: CI/CD Pipeline (2 weeks)

### GitHub Actions Workflows
```yaml
# .github/workflows/

test.yml:
  - Run pytest (backend)
  - Run vitest (frontend)
  - Run eslint
  - Run black
  - Generate coverage

build.yml:
  - Build Docker images
  - Push to registry
  - Tag releases

deploy.yml:
  - Deploy to staging (auto)
  - Deploy to production (manual)
  - Run smoke tests

security.yml:
  - Dependency scanning
  - SAST scanning
  - Secret scanning
```

### Coverage Targets
- Backend: 80%+
- Frontend: 70%+
- Critical paths: 95%+

---

## PHASE 28: Production Readiness (2 weeks)

### Checklist
- [ ] Staging environment fully functional
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Monitoring and alerts configured
- [ ] Disaster recovery tested
- [ ] Runbooks written
- [ ] On-call setup
- [ ] Customer support ready
- [ ] SLA defined
- [ ] Backup strategy tested

### Runbooks to Write
- Incident response
- Database failover
- API restart
- Cache flush
- Emergency scaling

---

## IMPLEMENTATION ORDER

**Critical Path (12-14 weeks to MVP):**
1. **Phase 11-12** (4 weeks): Calendar + Integration engine
2. **Phase 13-15** (3 weeks): ServiceTitan, Jobber, HCP
3. **Phase 18-19** (2 weeks): Workflows + Analytics
4. **Phase 25** (2 weeks): Terraform
5. **Phase 27** (1-2 weeks): CI/CD

**Then Sequential:**
- Phase 20-21: Usage metering + Billing
- Phase 22-24: Security + Observability + Load testing
- Phase 26: AWS Deployment
- Phase 28: Production readiness

---

## TEAM EFFORT ESTIMATES

| Phase | Solo Dev | 2 Devs | 3 Devs |
|-------|----------|--------|--------|
| 11-12 | 4 weeks | 2 weeks | 1.5 weeks |
| 13-15 | 3 weeks | 1.5 weeks | 1 week |
| 16-17 | 2 weeks | 1 week | 5 days |
| 18-21 | 4 weeks | 2 weeks | 1.5 weeks |
| 22-28 | 4 weeks | 2 weeks | 1.5 weeks |

---

## SUCCESS METRICS

✅ **Can book appointment via voice call**
✅ **Synced with 3+ CRM systems**
✅ **<100ms API response time (p95)**
✅ **99.9% uptime**
✅ **80%+ test coverage**
✅ **$0 infrastructure cost/month (free tier)**
✅ **<5% error rate on calls**
✅ **1000+ concurrent users supported**

---

## DEPLOYMENT CHECKLIST

**Before Launch:**
- [ ] All tests passing
- [ ] Security audit passed
- [ ] Load testing completed
- [ ] Monitoring configured
- [ ] Backups automated
- [ ] Disaster recovery tested
- [ ] Team trained
- [ ] Customer support ready

**Launch Day:**
- [ ] 1 week on staging
- [ ] Smoke tests passing
- [ ] Alert system validated
- [ ] On-call rotation active
- [ ] Rollback plan ready

**Post-Launch:**
- [ ] Monitor error rates
- [ ] Check performance
- [ ] Gather customer feedback
- [ ] Weekly retrospectives
- [ ] Plan Phase 2 features

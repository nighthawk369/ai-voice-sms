# Product Specification Review & Optimization

## Executive Summary
The MASTER CLAUDE CODE PROMPT is comprehensive and well-structured. Below are critical additions, optimizations, and clarifications needed before implementation.

---

## ✅ STRENGTHS
1. **Clear phase-based approach** - Prevents scope creep and uncontrolled development
2. **Security-first** - Multi-tenancy, tenant isolation, audit logging emphasized
3. **Integration-agnostic** - Adapter pattern prevents provider lock-in
4. **Infrastructure as Code** - Complete Terraform specification
5. **Hallucination controls** - Explicit rules about what AI cannot claim
6. **Testing strategy** - Unit, integration, E2E, load, security tests defined

---

## 🔴 CRITICAL ADDITIONS NEEDED

### 1. **CONVERSATION STATE PERSISTENCE & RECOVERY**
Currently missing detailed specification on:
- How conversation state persists across call interruptions
- Recovery mechanism if worker crashes mid-call
- State machine event sourcing vs snapshot storage
- Conversation timeout and cleanup strategy

**Recommendation:**
```
Implement event sourcing for conversations:
- Every state change = immutable event
- Snapshots every 100 events
- Replay protection: max 10 retries
- Conversation TTL: 24 hours (configurable)
- Dead letter: unrecoverable conversations → human escalation
```

### 2. **ERROR RECOVERY & GRACEFUL DEGRADATION**
Not adequately covered:
- What happens when AI tool fails
- Fallback strategies for each tool type
- Circuit breaker patterns
- Exponential backoff with jitter details
- Error translation and user-facing messaging

**Recommendation:**
Add section:
```
TOOL FAILURE MODES:
- Tool timeout (>30s): escalate, collect info, follow-up
- Authentication failure: escalate, notify admin
- Rate limit: retry with backoff (max 3×)
- Unavailable service: AI offers alternative, escalates if needed
- Validation error: re-prompt AI, max 2 attempts then escalate

Never tell customer "system error" without collecting context.
```

### 3. **CACHING STRATEGY**
Redis mentioned but no cache layer specification:
- What gets cached (availability, customer, knowledge, config)
- Cache TTL per entity
- Cache invalidation strategy
- Cache warming strategy
- Cache monitoring/metrics

**Recommendation:**
```
CACHE LAYERS:
- L1: Customer lookup cache (5 min TTL)
- L2: Availability cache (2 min TTL, invalidate on book)
- L3: Knowledge base (10 min TTL)
- L4: Agent config (30 min TTL)
- L5: Integration health (1 min TTL)

Cache invalidation triggers:
- Configuration change → full cache flush
- Appointment booked → availability cache invalidate
- CRM sync → customer cache invalidate
- Webhook event → selective invalidation

Monitor cache hit rates; escalate if <70%.
```

### 4. **CONVERSATION TIMEOUT & ABANDONMENT**
Not specified:
- Max conversation duration (prevent endless loops)
- Silence timeout (when to auto-escalate)
- Customer hang-up handling
- Repeat call detection

**Recommendation:**
```
CONVERSATION LIMITS:
- Max duration: 15 minutes (configurable per org)
- Silence timeout: 30 seconds
- Max tool calls per conversation: 20
- Max re-prompts to AI: 3 per tool
- If limits exceeded: graceful escalation

Track: repeat calls from same number within 1 hour
→ Context from previous call available
```

### 5. **KNOWLEDGE BASE QUALITY & FRESHNESS**
RAG system mentioned but missing:
- How to detect stale/incorrect knowledge
- Version control for documents
- Change tracking and audit
- Knowledge validation before serving
- Conflict resolution (contradictory documents)

**Recommendation:**
```
KNOWLEDGE MANAGEMENT:
- Document versions with change history
- Knowledge verification workflow (human review)
- Document effectiveness metrics
- Contradiction detection alerts
- Document deprecation workflow
- Knowledge expiry dates (configurable)
- A/B testing knowledge variants
```

### 6. **DUPLICATE BOOKING PREVENTION - DETAILED**
Section 55 mentions idempotency but needs expansion:
- Race conditions when multiple calls simultaneous
- Double-booking across calendars
- Concurrent appointment requests

**Recommendation:**
```
DUPLICATE PREVENTION:
- Idempotency key = hash(tenant_id, customer_id, service_type, 
                          start_time, location_id)
- Lock on idempotency key during booking (5 min TTL)
- Check calendar immediately before commit
- Return same result if duplicate within 10 seconds
- Log all duplicate attempts for fraud detection

Test: 100 concurrent requests for same slot → 1 booking
```

### 7. **CONVERSATION CONTEXT WINDOW MANAGEMENT**
AI orchestrator needs specification:
- How much context to send to LLM
- Context pruning strategy
- Message summarization for long conversations
- Token counting and budget enforcement

**Recommendation:**
```
CONTEXT MANAGEMENT:
- Keep last 10 messages + system context
- If tokens > 3000: summarize old messages
- Never send customer messages > 5000 chars
- Truncate knowledge results to top 3 chunks
- Track tokens per call, alert on overages

Per-call budget: 2000 tokens input, 500 tokens output (default)
Per-tenant daily: 100k input, 50k output
```

### 8. **MOBILE APP STRATEGY**
Completely missing:
- Native iOS/Android apps
- Mobile-specific UX
- Offline sync
- Push notifications
- Mobile-specific features

**Recommendation:**
```
MOBILE ROADMAP (POST-MVP):
- React Native shared codebase
- Push notifications for leads/calls
- Offline queue for critical actions
- Biometric auth
- Wearable integration (future)
- App-specific integrations (Slack, Teams)
```

### 9. **TESTING DATA STRATEGY**
Limited detail on test environments:
- How to generate realistic test data
- Compliance with data privacy in staging
- Sandbox data isolation
- Load test data generation

**Recommendation:**
```
TEST DATA:
Phase 0: Create Acme HVAC demo tenant
- 100 customers
- 500 leads
- 1000 conversations
- Realistic distribution (20% emergency, 30% follow-up, etc.)

Faker library for PII:
- Phone numbers: (555) 123-4567 format
- Emails: generated@example.com
- Names: realistic HVAC names
- Addresses: major metro areas

Compliance:
- All test data uses clearly-marked demo status
- Never use real customer data in non-prod
- PII redaction in logs/monitoring
```

### 10. **DEPLOYMENT ROLLBACK & CANARY STRATEGY**
Terraform mentioned but deployment strategy vague:
- Canary deployments
- Blue/green strategy
- Automatic rollback triggers
- Data migration rollback

**Recommendation:**
```
DEPLOYMENT STRATEGY:
- Canary: 10% of traffic for 15 min, monitor errors
- If error rate > 0.5%, auto-rollback
- Blue/green for database-changing deploys
- All migrations reversible (down migrations required)
- Rollback: terraform apply previous state
- Feature flags control risky features during rollout

Automatic rollback triggers:
- 5xx error rate > 1% for 5 min
- P99 latency > 5s for 5 min
- Database migration failure
- Health check failures > 50%
```

### 11. **MONITORING & ALERTING SPECIFICS**
Generic but needs thresholds:
- Specific metrics and thresholds
- Dashboard structure
- Alert routing (Slack, PagerDuty, etc.)
- On-call rotation

**Recommendation:**
```
ALERTS (PagerDuty routing):

CRITICAL (page immediately):
- API error rate > 1% for 2 min
- Database CPU > 90% for 5 min
- Redis memory > 90%
- LLM provider outage
- Voice provider outage
- CRM sync failure > 10 min

HIGH (alert but no page):
- Error rate 0.1-1%
- Database backup failure
- Certificate expiry < 7 days

MEDIUM (Slack notification):
- Tool failure rate > 5%
- Queue depth > 1000
- Webhook delivery delay > 1 min
```

---

## 🟡 OPTIMIZATIONS & CLARIFICATIONS

### 1. **API PAGINATION SPECIFICS**
Missing:
- Default page size
- Max page size
- Cursor vs offset
- Sorting strategy

```
Add to Section 44 (API):

PAGINATION STANDARD:
- Cursor-based (offset has security issues)
- Default: 50 items
- Max: 500 items
- Sort: -created_at (newest first) by default
- Expose: has_more, next_cursor fields
- Cursor opaque string (base64 encoded)
```

### 2. **RATE LIMITING SPECIFICS**
Section 46 mentions rate limiting but lacks specifics:

```
Add detailed limits:

RATE LIMITS:
Public API (per API key):
- 100 req/min (free tier)
- 1000 req/min (pro)
- 10000 req/min (enterprise)

Webhook:
- Delivery retry: 5 attempts over 24h
- Exponential backoff: 1m, 5m, 30m, 2h, 8h

Voice API:
- 100 concurrent calls per tenant
- 1000 calls/day (free)

SMS API:
- 1000 SMS/day (free)
- Rate: 100 SMS/min
```

### 3. **COMPLIANCE & LEGAL SPECIFICS**
Section 97 is vague. Add:
- GDPR requirements
- CCPA requirements
- HIPAA (medical/emergency context)
- TCPA (SMS compliance)
- State-specific privacy laws

```
Add:

COMPLIANCE MATRIX:
- GDPR: Data residency EU, right to erasure, consent flows
- CCPA: Right to know, right to delete, opt-out
- HIPAA: If healthcare context, full compliance
- TCPA: SMS consent tracking, opt-out honor
- State laws: AR, CA, NY specific rules

Config per tenant:
- Data residency region
- Retention policies
- Consent workflow
```

### 4. **CONVERSATION BRANCHING & CONFIRMATION**
AI state machine lacks:
- How to handle ambiguous customer inputs
- Confirmation before high-impact actions
- Undo/correction workflows

```
Add:

CONFIRMATION PROTOCOL:
Book appointment:
- Confirm: "I have you down for Tuesday 2-4pm for furnace repair. 
           Is this correct?"
- If "no": restart availability check
- If "yes": book and send SMS confirmation

High-risk operations (>$500 job):
- Always confirm with supervisor name/context
- If uncertain: escalate
```

### 5. **CONVERSATION EXPORT & TRANSCRIPT HANDLING**
Missing specification for:
- Transcript format
- Compliance with call recording laws
- Customer download rights
- Retention enforcement

```
Add:

TRANSCRIPT & RECORDINGS:
Storage format: .wav (audio), .json (transcript with timings)
Compliance:
- Two-party consent states: confirm consent before recording
- One-party consent: collect consent opt-out
- EU: GDPR retention max 3 years without renewal
- US: state-specific (vary 1-7 years)

Customer access:
- Download all transcripts/recordings
- Redact PII before sharing
- Export within 24 hours
```

### 6. **COST TRACKING & UNIT ECONOMICS**
Section 42 mentions unit economics but needs detail:

```
Add:

COST STRUCTURE (detailed):
Per call:
- AI: $0.01 (GPT-4) to $0.002 (Claude 3.5)
- Voice: $0.04 (Twilio)
- Storage: ~$0.0001 (recording)
- Database: $0.001 (amortized)
Total: ~$0.05-0.10 per call

Break-even calculation:
- Subscription: $99/month = ~3 hours of technician time
- If AI books 5 appointments/month: +$500 revenue → profitable
```

### 7. **COMPETITOR DIFFERENTIATION**
Not mentioned anywhere but critical:
- What makes this product better than alternatives
- Key differentiators
- Market positioning

```
Add strategic section:

DIFFERENTIATION:
vs. Existing solutions:
- Bring your own CRM (not locked in)
- Works with any calendar
- Privacy-first (private AI option)
- Transparent pricing
- No AI hallucinations on facts (strict guardrails)

Key moats:
- Integration depth & quality
- Conversation quality (hallucination controls)
- Multi-provider LLM support (not vendor locked)
```

### 8. **TEAM COORDINATION & DEVELOPMENT**
Missing parallel development specs:
- Branch strategy (trunk-based, feature branches, trunk with flags)
- Code review requirements
- Merge strategy
- Hotfix process

```
Add:

DEVELOPMENT WORKFLOW:
Branching: Trunk-based development
- Main branch = production
- Feature branches: feature/description
- All features behind feature flags initially
- CI blocks merge if tests/lint fail

Code review:
- All changes require 1 approval
- Security changes require 2 approvals
- Tests must pass before merge

Hotfix:
- Branch from main, tag release, cherry-pick to main
- Bypass code review only for P1 security issues
```

### 9. **PERFORMANCE BASELINES**
Section 58 mentions SLOs but needs performance targets:

```
Add:

PERFORMANCE TARGETS:
API response times (p95):
- GET customer: 50ms
- POST appointment: 200ms
- Webhook delivery: 500ms

Voice latency:
- First voice response: < 1s
- Barge-in detection: < 100ms
- Tool execution: < 2s

Frontend:
- Page load: < 2s
- Input response: < 100ms
```

### 10. **ANALYTICS EVENT TAXONOMY**
Section 39 lists events but needs structure:

```
Add:

ANALYTICS STANDARD:
Event schema:
{
  event_type: string (snake_case),
  timestamp: ISO8601,
  user_id: UUID,
  organization_id: UUID,
  properties: {...},
  context: {
    user_agent, ip, session_id
  }
}

Core events:
- user.signup, user.login, user.logout
- org.created, org.updated
- agent.created, agent.configured
- call.started, call.ended
- call.transferred, call.failed
- message.sent, message.failed
- appointment.booked, appointment.cancelled
```

### 11. **INTEGRATION PROVIDER API VERSIONING**
Critical for long-term maintenance:

```
Add section 124.5:

PROVIDER API VERSION MANAGEMENT:
Each integration adapter:
├── v1/
│   ├── client.py
│   ├── models.py
│   └── tests/
├── v2/
│   └── ...
└── latest -> v2/

Update strategy:
- New API version → new adapter folder
- Deprecation: 6 months warning
- Legacy support: N-1 version
- Migration path documented

Monitor: Log all version usage, alert on deprecated version usage
```

---

## 📋 MISSING SECTIONS TO ADD

### NEW SECTION 131: **TENANT COMMUNICATION & SUPPORT**
- Support ticket system integration
- In-app messaging
- Help documentation embedding
- Changelog & feature announcements

### NEW SECTION 132: **CUSTOMER SUCCESS METRICS**
- NPS tracking
- Usage depth metrics
- Time to first value
- Churn indicators
- Expansion signals

### NEW SECTION 133: **INTEGRATION TEST FIXTURES**
- Mock CRM responses
- Mock voice provider
- Mock calendar
- Fixture management

### NEW SECTION 134: **ARCHITECTURE DECISION LOG (ADL)**
- How to record architecture decisions
- Template for ADRs
- Location: `docs/adr/`

### NEW SECTION 135: **DEBUGGING & INCIDENT PLAYBOOK**
- Common issues & troubleshooting
- Log analysis techniques
- How to replay conversations
- How to analyze failed tool calls

### NEW SECTION 136: **PERFORMANCE OPTIMIZATION ROADMAP**
- Caching opportunities
- Database optimization
- Frontend optimization
- API optimization

### NEW SECTION 137: **CUSTOMER DATA PIPELINE**
- ETL for analytics
- Data warehouse schema
- Reporting infrastructure
- BI tool integration

### NEW SECTION 138: **PARTNER INTEGRATIONS**
- How partners integrate with platform
- Marketplace strategy
- Partner NDA/licensing

---

## 🎯 IMPLEMENTATION ROADMAP ADJUSTMENTS

Current phases 0-28 are solid, but recommend:

### Insert between phases:
- **PHASE 3.5: Comprehensive Logging & Observability**
  - Before implementing features, have logging infrastructure
  
- **PHASE 9.5: Voice Quality Testing**
  - Load test voice system before going to production
  
- **PHASE 12.5: Integration Testing Framework**
  - Shared contract tests for all integrations

- **PHASE 24.5: Security Hardening Pass**
  - Full security audit before infrastructure deployment

---

## ✨ QUALITY IMPROVEMENTS

### 1. **Add Decision Rationale**
Current spec states WHAT but sometimes not WHY.
Example: "Why PostgreSQL?" Add explanations.

### 2. **Add Diagrams**
- Database schema ERD
- Integration architecture diagram
- Conversation flow diagram
- Deployment pipeline diagram

### 3. **Add Example Configurations**
- Example .env file
- Example agent configuration JSON
- Example workflow YAML

### 4. **Add Success Criteria per Phase**
Each phase should have explicit "DONE" definition:
```
PHASE 0 COMPLETE when:
✓ Repo initialized
✓ Docker Compose runs locally
✓ Database migrations work
✓ All tests pass
✓ Lint/format clean
✓ README complete
```

---

## 🚀 IMPLEMENTATION SEQUENCING RECOMMENDATION

Before writing a single line:

1. **Create detailed ARCHITECTURE.md** (reference current spec)
2. **Create detailed PHASE 0 plan** with exact deliverables
3. **Lock down tech stack choices** with rationale
4. **Create database schema diagram** (ERD)
5. **Create integration architecture diagram**
6. **Document assumptions** (e.g., "Assume Twilio for voice")

---

## 📊 METRICS TO TRACK FROM DAY 1

Add instrumentation early:
- Request latency (p50, p95, p99)
- Error rates by endpoint
- Tool call success rate
- Conversation completion rate
- Time to first booking
- Cost per call

---

## 🔗 DEPENDENCIES & ASSUMPTIONS TO CLARIFY

1. **Which LLM to use for MVP?** (Currently says "support all")
2. **Which voice provider?** (Twilio assumed, specify)
3. **Which vector DB for embeddings?** (Not mentioned, recommend Pgvector in Postgres)
4. **Frontend framework?** (Not specified, recommend React/Next.js)
5. **Python version & package manager?** (Specify Python 3.11+, Poetry for deps)

---

## SUMMARY

**Current spec is ~95% complete for MVP.**

**Critical additions needed:**
1. ✅ Conversation state persistence & recovery
2. ✅ Error handling & graceful degradation  
3. ✅ Caching strategy
4. ✅ Duplicate booking race condition handling
5. ✅ Monitoring thresholds

**Nice-to-have optimizations:**
- Mobile app roadmap
- Detailed cost structure
- Performance baselines
- Compliance matrix per region
- Team workflow specifications

**Recommendation: Create detailed PHASE 0 plan from this spec, then begin implementation.**

---

## NEXT STEPS

I can now:
1. Create detailed ARCHITECTURE.md from the specification
2. Create detailed PHASE 0 implementation plan
3. Create database schema ERD
4. Create detailed tech stack decision document
5. Begin PHASE 0 implementation

**Which would you like to prioritize?**

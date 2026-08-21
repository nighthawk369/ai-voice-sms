# MASTER PRODUCT SPECIFICATION & IMPLEMENTATION GUIDE

**Product:** AI Voice & SMS Platform for Field Service Businesses (HVAC, Plumbing, Electrical)  
**Version:** 1.0  
**Last Updated:** 2026-08-22  
**Status:** Ready for Phase 0 Implementation

---

## TABLE OF CONTENTS

1. [Product Vision & Positioning](#1-product-vision--positioning)
2. [Architecture Overview](#2-architecture-overview)
3. [Technology Stack & Decisions](#3-technology-stack--decisions)
4. [Database Schema & ERD](#4-database-schema--erd)
5. [Multi-Tenancy & Security](#5-multi-tenancy--security)
6. [Core Features](#6-core-features)
7. [AI Orchestrator System](#7-ai-orchestrator-system)
8. [Integration Engine](#8-integration-engine)
9. [Voice & Communications](#9-voice--communications)
10. [Workflow & Automation](#10-workflow--automation)
11. [Analytics & Billing](#11-analytics--billing)
12. [Infrastructure & Deployment](#12-infrastructure--deployment)
13. [Testing Strategy](#13-testing-strategy)
14. [PHASE 0: Repository Bootstrap](#14-phase-0-repository-bootstrap)
15. [Development Phases 1-28](#15-development-phases-1-28)
16. [Acceptance Criteria](#16-acceptance-criteria)
17. [Operating Sequence](#17-operating-sequence)

---

# 1. PRODUCT VISION & POSITIONING

## Problem Statement
Field service businesses (HVAC, plumbing, electrical) receive 30-50 calls/day but miss many due to:
- Limited staff availability
- Manual scheduling
- Poor follow-up
- High customer churn

## Solution
An AI-powered voice and SMS platform that:
- Answers calls 24/7
- Understands customer needs
- Checks availability across calendars
- Books appointments directly into CRM
- Never forgets follow-ups
- Works with existing CRM systems (ServiceTitan, Jobber, HubSpot, Salesforce, etc.)

## Key Differentiators
1. **Bring Your Own CRM** - Not locked into a single provider
2. **Privacy-First** - Support for private/self-hosted LLMs
3. **No Hallucinations** - Strict guardrails on facts (prices, availability, policies)
4. **Multi-Provider LLM** - Use OpenAI, Claude, Gemini, or private models
5. **Transparent Pricing** - Usage-based, no surprises

## Target Market
- Small to mid-size field service businesses (10-100 technicians)
- Industries: HVAC, plumbing, electrical, painting, general contracting
- Geographic: US-based initially (compliance for SMS/voice laws)

## Success Metrics (Year 1)
- 500+ active tenants
- 50k calls/month → 5k appointments/month
- $10k MRR
- 40% gross margin
- NPS > 40

---

# 2. ARCHITECTURE OVERVIEW

## 2.1 High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CUSTOMER                              │
│                   Phone / SMS / Web                          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│            COMMUNICATION GATEWAY                             │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ Twilio Voice API │  │  Twilio SMS API  │                │
│  └──────────────────┘  └──────────────────┘                │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              AI ORCHESTRATOR (Core Engine)                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Conversation Manager | State Machine | Tool Router  │   │
│  └─────────────────────────────────────────────────────┘   │
└───────┬─────────────────────────┬──────────────────────────┘
        │                         │
┌───────▼────────────┐   ┌────────▼──────────────┐
│  LLM GATEWAY       │   │   TOOL GATEWAY       │
│ ┌──────────────┐   │   │ ┌────────────────┐   │
│ │ OpenAI       │   │   │ │ CRM Operations │   │
│ │ Anthropic    │   │   │ │ Calendar Ops   │   │
│ │ Google       │   │   │ │ SMS Send       │   │
│ │ Private LLM  │   │   │ │ Knowledge      │   │
│ └──────────────┘   │   │ │ Search         │   │
└───────────────────┘   │ └────────────────┘   │
                        └──────────┬───────────┘
                                   │
┌───────────────────────────────────▼───────────────────────────┐
│         INTEGRATION ENGINE                                     │
│  ┌──────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ ServiceTitan │  │   Jobber   │  │  HubSpot   │            │
│  └──────────────┘  └────────────┘  └────────────┘            │
│  ┌──────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Salesforce  │  │  HCP       │  │ Calendar   │            │
│  └──────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              DATA LAYER                                      │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ PostgreSQL     │  │ Redis        │  │ Vector DB      │  │
│  │ (Primary DB)   │  │ (Cache)      │  │ (Embeddings)   │  │
│  └────────────────┘  └──────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 2.2 Component Responsibilities

| Component | Responsibility |
|-----------|-----------------|
| **Communication Gateway** | Route inbound calls/SMS to AI, handle voice/SMS operations |
| **AI Orchestrator** | Conversation state, intent detection, tool coordination, escalation |
| **LLM Gateway** | Multi-provider abstraction, token tracking, fallback handling |
| **Tool Gateway** | Execute tools (CRM ops, calendar, SMS) with auth & isolation |
| **Integration Engine** | Adapters for CRMs, calendars, webhooks, field mapping |
| **PostgreSQL** | Primary data store (tenant data, conversations, audit logs) |
| **Redis** | Session cache, conversation state, rate limiting, queue |
| **Vector DB** | Embeddings for knowledge base search (Pgvector in Postgres) |

---

# 3. TECHNOLOGY STACK & DECISIONS

## 3.1 Backend Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Language** | Python 3.11+ | FastAPI ecosystem, excellent for async, ML/data science friendly |
| **Framework** | FastAPI | High performance, async-native, excellent documentation, auto OpenAPI |
| **ORM** | SQLAlchemy + Alembic | Flexible, multi-database support, battle-tested |
| **Database** | PostgreSQL 15+ | ACID compliance, JSON support, vector extensions, mature |
| **Cache** | Redis 7+ | Sub-millisecond latency, perfect for session/queue storage |
| **Vector DB** | Pgvector (Postgres extension) | Eliminate external service, simpler architecture |
| **Message Queue** | Celery + Redis | Async task execution, retries, scheduling |
| **API Documentation** | OpenAPI 3.1 | Auto-generated from FastAPI, client SDK generation |
| **Testing** | Pytest + Faker | Fixture management, parametrization, realistic data |
| **Linting** | Ruff | 10-100x faster than Flake8 + Black |
| **Type Checking** | Pyright | Strict mode, excellent LSP integration |
| **Code Formatting** | Black | No configuration debates |

## 3.2 Frontend Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Framework** | React 18 + Next.js 14 | SSR, API routes, excellent DX |
| **Language** | TypeScript | Type safety, excellent IDE support |
| **Styling** | Tailwind CSS | Utility-first, rapid prototyping |
| **State Management** | TanStack Query (React Query) | Server-state management, caching, sync |
| **UI Components** | Headless UI + Radix UI | Accessible, unstyled, composable |
| **Forms** | React Hook Form + Zod | Performant, type-safe validation |
| **Testing** | Vitest + Playwright | Fast unit tests, E2E browser automation |
| **Linting** | ESLint + Prettier | Standard JS ecosystem |

## 3.3 DevOps Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Containerization** | Docker + multi-stage builds | Reproducible environments, layer caching |
| **Orchestration** | AWS ECS Fargate | Serverless containers, no cluster management |
| **Infrastructure** | Terraform | IaC, reproducible deployments, version control |
| **CI/CD** | GitHub Actions | Native to GitHub, no vendor lock-in |
| **Cloud Provider** | AWS | Mature services, excellent support for startup |
| **Monitoring** | OpenTelemetry + Prometheus + Grafana | Standard observability stack |
| **Logging** | CloudWatch + structured JSON | AWS-native, easy compliance |
| **Secrets** | AWS Secrets Manager | Rotation, encryption, audit |
| **DNS** | Route53 | AWS-integrated, DNSSEC support |
| **CDN** | CloudFront | AWS-integrated, DDoS protection |

## 3.4 External Services

| Service | Purpose | Alternative |
|---------|---------|-------------|
| **Twilio** | Voice & SMS | Telnyx, Bandwidth |
| **OpenAI** | Primary LLM | Claude (Anthropic), Gemini (Google) |
| **Anthropic Claude** | Secondary LLM | GPT-4o (OpenAI) |
| **Stripe** | Billing/Payments | Paddle, Chargebee |
| **SendGrid** | Email | AWS SES, Mailgun |
| **Sentry** | Error tracking | Rollbar, Datadog |

## 3.5 Tech Stack Decisions Rationale

**Why FastAPI over Django?**
- Django is heavier, slower for real-time (voice latency is critical)
- FastAPI is purpose-built for APIs with async
- FastAPI is more modern, better for new projects

**Why PostgreSQL only, not MongoDB?**
- Strict data integrity required (financial, bookings)
- ACID transactions critical
- Complex relational data (tenant-user-org hierarchy)
- JSON support in Postgres is sufficient for flexible fields

**Why Vector DB in Postgres vs Pinecone/Weaviate?**
- Eliminates external service dependency
- Pgvector extension is production-ready (used by major companies)
- Reduces cost and complexity
- Simpler data consistency (single database)

**Why Celery vs AWS Lambda?**
- Long-running tasks (voice conversations can be 15+ minutes)
- Lambda has 15-minute timeout limit
- Celery is simpler for complex workflows
- ECS workers provide better control and debugging

**Why Terraform over CDK/CloudFormation?**
- Language-agnostic (vendor lock-in prevention)
- Better version control and code review
- Module ecosystem is mature
- Multi-cloud capable (future flexibility)

---

# 4. DATABASE SCHEMA & ERD

## 4.1 Core Data Model

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         MULTI-TENANCY CORE                               │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Organization (id, name, created_at, updated_at)                        │
│    ├─ User (id, org_id, email, role, created_at)                       │
│    ├─ Location (id, org_id, name, address, phone, tz)                 │
│    ├─ PhoneNumber (id, org_id, number, type, provider, status)        │
│    └─ APIKey (id, org_id, name, key_hash, scopes, expires_at)         │
│                                                                           │
│  AIAgent (id, org_id, name, status, created_at)                        │
│    └─ AIAgentVersion (id, agent_id, system_prompt, model, config)      │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                      CUSTOMER & BUSINESS DATA                            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Customer (id, org_id, phone, email, first_name, last_name)            │
│    ├─ CustomerAddress (id, customer_id, address, type, primary)       │
│    ├─ CustomerNote (id, customer_id, note, created_at)                │
│    └─ ExternalObjectMapping (id, org_id, customer_id, provider, ext_id)│
│                                                                           │
│  Lead (id, org_id, customer_id, source, status, score, value)         │
│    └─ LeadUpdate (id, lead_id, field, old_value, new_value, timestamp) │
│                                                                           │
│  Appointment (id, org_id, customer_id, location_id, start, end, status)│
│    ├─ AppointmentHistory (id, appt_id, field, old_val, new_val)       │
│    └─ ExternalObjectMapping (id, org_id, appt_id, provider, ext_id)   │
│                                                                           │
│  Job (id, org_id, customer_id, appointment_id, service_type, status)  │
│    └─ ExternalObjectMapping (id, org_id, job_id, provider, ext_id)    │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                    CONVERSATION & COMMUNICATIONS                         │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Conversation (id, org_id, customer_id, agent_version_id, status)     │
│    ├─ ConversationEvent (id, conv_id, type, state, data, timestamp)   │
│    │   (Events: GREETING, IDENTIFYING, UNDERSTANDING, QUALIFYING,      │
│    │    COLLECTING, CHECKING_AVAIL, CONFIRMING, BOOKING, etc)        │
│    │                                                                    │
│    └─ Message (id, conv_id, role, content, created_at)               │
│        (role: CUSTOMER, AI, HUMAN)                                    │
│                                                                           │
│  Call (id, org_id, customer_id, conversation_id, phone)              │
│    ├─ CallRecording (id, call_id, s3_path, duration, transcription)  │
│    └─ CallMetrics (id, call_id, duration, transfers, cost)           │
│                                                                           │
│  SMSMessage (id, org_id, customer_id, direction, status, content)    │
│    └─ SMSDeliveryStatus (id, sms_id, status, timestamp)              │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                    INTEGRATIONS & EXTERNAL DATA                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Integration (id, org_id, provider, status, last_sync)                │
│    ├─ IntegrationCredential (id, integration_id, encrypted_cred)      │
│    ├─ IntegrationMapping (id, integration_id, internal_field, ext_fld)│
│    ├─ IntegrationSync (id, integration_id, object_type, status, time) │
│    └─ IntegrationWebhook (id, integration_id, url, secret, events)    │
│                                                                           │
│  ExternalObjectMapping (id, org_id, provider, object_type,            │
│                         internal_id, external_id, version, sync_time) │
│                                                                           │
│  WebhookEvent (id, org_id, provider, event_type, payload, processed)  │
│    └─ DeadLetterEvent (id, event_id, error_reason, retry_count)       │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE BASE & AI TRAINING                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  KnowledgeBase (id, org_id, name, status, created_at)                 │
│    ├─ KnowledgeDocument (id, kb_id, title, source, version)           │
│    │   └─ KnowledgeChunk (id, doc_id, content, embedding, metadata)   │
│    │                                                                    │
│    └─ KnowledgeSearch (id, kb_id, query, results_count, quality)      │
│                                                                           │
│  Tool (id, org_id, name, description, enabled, provider)              │
│    └─ ToolCall (id, tool_id, conversation_id, input, output, status)  │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                      WORKFLOWS & AUTOMATION                              │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Workflow (id, org_id, name, trigger, condition, action, enabled)     │
│    └─ WorkflowRun (id, workflow_id, status, result, timestamp)        │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                     ANALYTICS & COMPLIANCE                               │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  UsageRecord (id, org_id, metric_type, amount, timestamp)             │
│    (metric_type: voice_minutes, sms_count, api_calls, tokens_in/out)  │
│                                                                           │
│  AuditLog (id, org_id, actor_id, action, resource, timestamp, ip)    │
│    (action: login, config_change, crm_write, deletion, etc)           │
│                                                                           │
│  BillingAccount (id, org_id, stripe_customer_id, status)             │
│    ├─ Subscription (id, billing_id, plan, status, expires_at)        │
│    ├─ Invoice (id, billing_id, amount, status, stripe_invoice_id)   │
│    └─ PaymentMethod (id, billing_id, stripe_payment_method_id)       │
│                                                                           │
│  Event (id, org_id, event_type, entity_type, entity_id, timestamp)   │
│    (Types: customer.created, appointment.booked, lead.updated, etc)   │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

## 4.2 Critical Indexes & Constraints

```sql
-- Tenant isolation (CRITICAL)
CREATE UNIQUE INDEX idx_org_user_email ON "user"(organization_id, email);
CREATE INDEX idx_org_customer_phone ON customer(organization_id, phone);
CREATE INDEX idx_org_conversation ON conversation(organization_id, created_at DESC);
CREATE INDEX idx_org_call ON call(organization_id, created_at DESC);

-- Data access patterns
CREATE INDEX idx_customer_by_phone_email ON customer(organization_id, phone, email);
CREATE INDEX idx_appointment_by_dates ON appointment(organization_id, start_time, end_time);
CREATE INDEX idx_lead_by_score ON lead(organization_id, lead_score DESC, created_at DESC);
CREATE INDEX idx_conversation_by_status ON conversation(organization_id, status, created_at DESC);

-- Integration patterns
CREATE UNIQUE INDEX idx_ext_mapping_unique ON external_object_mapping(
  organization_id, provider, object_type, internal_id
);
CREATE INDEX idx_ext_mapping_lookup ON external_object_mapping(
  organization_id, provider, external_id
);

-- Audit & compliance
CREATE INDEX idx_audit_log_by_org_date ON audit_log(organization_id, created_at DESC);
CREATE INDEX idx_usage_record_by_metric ON usage_record(organization_id, metric_type, timestamp DESC);

-- Vector search (for embeddings)
CREATE INDEX idx_knowledge_chunk_embedding ON knowledge_chunk USING ivfflat (embedding vector_cosine_ops);
```

## 4.3 Key Table Details

### Organization
```sql
CREATE TABLE organization (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  timezone VARCHAR(50) DEFAULT 'America/New_York',
  locale VARCHAR(10) DEFAULT 'en_US',
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);
```

### Customer (Tenant-Aware)
```sql
CREATE TABLE customer (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id),
  
  -- Core identification
  external_ids JSONB DEFAULT '{}',  -- {ServiceTitan: "ST-123", Jobber: "JB-456"}
  phone VARCHAR(20) NOT NULL,
  email VARCHAR(255),
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  
  -- Additional info
  tags JSONB DEFAULT '[]',  -- ["emergency", "repeat_customer", "vip"]
  metadata JSONB DEFAULT '{}',  -- Provider-specific fields
  
  -- Compliance
  do_not_call BOOLEAN DEFAULT FALSE,
  sms_opt_out BOOLEAN DEFAULT FALSE,
  
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  deleted_at TIMESTAMP NULL,  -- Soft deletion
  
  UNIQUE(organization_id, phone)
);
```

### Conversation (State Persistence)
```sql
CREATE TABLE conversation (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id),
  customer_id UUID REFERENCES customer(id),
  agent_version_id UUID NOT NULL REFERENCES ai_agent_version(id),
  
  -- State machine
  state VARCHAR(50) NOT NULL DEFAULT 'GREETING',
  -- GREETING → IDENTIFYING → UNDERSTANDING → QUALIFYING → 
  -- COLLECTING → CHECKING_AVAILABILITY → CONFIRMING → BOOKING → COMPLETED
  
  -- Context
  context JSONB DEFAULT '{}',  -- Persisted conversation context
  extracted_data JSONB DEFAULT '{}',  -- Extracted customer intent, dates, etc
  
  -- Metadata
  channel VARCHAR(20) NOT NULL,  -- 'voice', 'sms', 'web'
  phone_number VARCHAR(20),
  outcome VARCHAR(50) DEFAULT 'PENDING',  -- COMPLETED, ESCALATED, ABANDONED, FAILED
  
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  ended_at TIMESTAMP NULL,
  
  CONSTRAINT check_state_valid CHECK (state IN (
    'GREETING', 'IDENTIFYING', 'UNDERSTANDING', 'QUALIFYING',
    'COLLECTING', 'CHECKING_AVAILABILITY', 'CONFIRMING', 'BOOKING',
    'FOLLOW_UP', 'HUMAN_ESCALATION', 'COMPLETED'
  ))
);

CREATE TABLE conversation_event (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
  event_type VARCHAR(50) NOT NULL,  -- state_change, tool_call, error, etc
  state VARCHAR(50),
  data JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT now()
);
```

### ExternalObjectMapping (Integration Abstraction)
```sql
CREATE TABLE external_object_mapping (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id),
  
  -- What we're mapping
  provider VARCHAR(50) NOT NULL,  -- 'servicetitan', 'jobber', 'hubspot'
  object_type VARCHAR(50) NOT NULL,  -- 'customer', 'appointment', 'job', 'lead'
  
  -- IDs
  internal_id UUID NOT NULL,  -- Our customer_id, appointment_id, etc
  external_id VARCHAR(255) NOT NULL,  -- ST-123, JB-456
  external_version VARCHAR(50),  -- Provider version for conflict detection
  
  -- Metadata
  last_synced_at TIMESTAMP,
  metadata JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  
  UNIQUE(organization_id, provider, object_type, internal_id)
);
```

---

# 5. MULTI-TENANCY & SECURITY

## 5.1 Tenant Isolation Implementation

**Every table must have `organization_id` as first column (after ID).**

### Row-Level Security (RLS) Policy Template
```python
# In ORM queries, ALWAYS filter by organization_id
class TenantAware(Base):
    organization_id: UUID = Column(UUID, ForeignKey('organization.id'), nullable=False)

    @classmethod
    def for_org(cls, org_id: UUID):
        """Filter to only this organization's data."""
        return select(cls).where(cls.organization_id == org_id)

# Usage:
customers = await db.execute(Customer.for_org(current_user.organization_id))
```

### Fields to Test for Tenant Isolation (MUST FAIL if not isolated)
```
Test that users cannot access:
✓ Another org's customers
✓ Another org's calls/conversations
✓ Another org's messages/recordings
✓ Another org's integrations/credentials
✓ Another org's analytics/billing
✓ Another org's AI configuration
✓ Another org's documents/knowledge base
```

## 5.2 User Roles & Permissions

### Role Hierarchy
```
OWNER (full access, manage billing/users)
  ├─ ADMIN (manage team, config, integrations)
  │   ├─ MANAGER (manage agents, view analytics)
  │   │   └─ AGENT (use AI, view own calls)
  │   │
  │   └─ VIEWER (read-only access)
```

### Permission Matrix
```
                    OWNER  ADMIN  MANAGER  AGENT  VIEWER
Configuration         ✓      ✓       ✗       ✗      ✗
Integration Config    ✓      ✓       ✓       ✗      ✗
User Mgmt             ✓      ✓       ✗       ✗      ✗
Billing               ✓      ✗       ✗       ✗      ✗
View All Calls        ✓      ✓       ✓       ✗      ✓
Take Calls            ✓      ✓       ✓       ✓      ✗
View Analytics        ✓      ✓       ✓       ✓      ✓
View Audit            ✓      ✓       ✗       ✗      ✗
```

## 5.3 Security Controls

### Authentication
```
✓ Email + password (bcrypt SHA256)
✓ Session tokens (JWT, 24h expiry)
✓ Refresh tokens (30-day expiry)
✓ MFA (TOTP, optional but recommended for admins)
✓ OAuth2 (future: Google, GitHub)
✗ Never send passwords in emails
```

### API Keys
```
✓ SHA256 hash stored (show only once at creation)
✓ Scopes support (e.g., "read:calls", "write:bookings")
✓ Rotation support
✓ Expiration dates
✓ Rate limiting per key
```

### Credential Encryption
```
✓ All third-party credentials (CRM, Twilio, etc) encrypted at rest
✓ Use AWS Secrets Manager or KMS
✓ Rotate credentials every 90 days
✓ Never log credentials
✓ Never expose in error messages
```

### Audit Logging
```
Every action logged: action, actor, resource, timestamp, IP
Actions to log:
- Login/logout
- Config changes
- Integration connect/disconnect
- CRM writes (appointment, lead creation)
- User invitations
- API key creation/revocation
- Data exports
- Data deletions
```

---

# 6. CORE FEATURES

## 6.1 Voice Call Flow

```
Incoming Call
    ↓
[Identify Organization] ← Phone routing rule
    ↓
Load Agent Configuration
    ↓
Load Customer (if repeat)
    ↓
AI Greeting → "Hi! This is [Business]. How can I help?"
    ↓
Customer speaks
    ↓
[AI Processing]
    ├─ Intent Detection: What does customer need?
    ├─ Customer Identification: Existing or new?
    ├─ Availability Check: Can we schedule?
    ├─ Tool Execution: Book, create lead, etc
    └─ Response Generation: What to say?
    ↓
AI Speaks Response
    ↓
[Conversation State Update]
    ├─ Save conversation event
    ├─ Update CRM if needed
    ├─ Send SMS if booking confirmed
    └─ Log all metrics
    ↓
Customer Satisfaction Rating (optional)
    ↓
Call Ended
```

## 6.2 Customer Identification

### Strategy
```
1. Phone number lookup → existing customer?
   If YES → load customer, personalize conversation
   If NO → capture name, address, phone

2. Repeat calls from same number within 24h
   → reference previous conversation
   "You called yesterday about furnace repair. How can I help?"

3. Edge cases:
   - Multiple people from same number → "Can I get your name?"
   - Business vs personal number → "Who am I speaking with?"
```

## 6.3 Intent Classification

### Categories
```
EMERGENCY
  → High priority, immediate response
  → "Your AC is broken in 90° heat?"
  
SERVICE_INQUIRY
  → "Do you replace thermostats?"
  
PRICING_INQUIRY
  → "How much is an AC service call?"
  
SCHEDULING
  → "Can you send someone Thursday?"
  
FOLLOW_UP
  → "Just checking on your furnace..."
  
COMPLAINT
  → "Your technician was rude"
  
CANCELLATION
  → "Cancel my appointment"
```

## 6.4 Availability Checking

### Process
```
1. AI requests: get_available_slots(
   service: "furnace_repair",
   location: "123 Main St, Denver CO",
   duration: 60 minutes,
   date_range: [today, today+7]
)

2. Integration Engine checks:
   a) Calendar (Google Calendar / Microsoft 365)
   b) Existing appointments
   c) Technician schedules
   d) Service duration requirements
   e) Exclude weekends/holidays/after-hours
   f) Timezone-aware

3. Return available times:
   [
     "Tuesday 2-4pm",
     "Wednesday 10am-12pm",
     "Thursday 3-5pm"
   ]
```

## 6.5 Appointment Booking

### Safeguards
```
BEFORE booking:
✓ Confirm all details with customer
✓ Verify appointment doesn't exist
✓ Check calendar for double-booking
✓ Generate idempotency key (org + customer + service + time)
✓ Lock on idempotency key

DURING booking:
✓ Call integration adapter
✓ Wait for confirmation
✓ Don't declare success until CRM confirms

AFTER booking:
✓ Create appointment record
✓ Map external ID
✓ Send SMS confirmation
✓ Create follow-up reminder
✓ Save conversation state
```

### Idempotency Key
```
idempotency_key = SHA256(
  organization_id +
  customer_id +
  service_type +
  start_time +
  location_id
)

If same idempotency key received within 10 seconds:
→ Return same result (already booked)
→ No duplicate appointment
```

## 6.6 Lead Scoring

### Default Scoring
```
Base: 0

Factors:
+ Emergency = +30 (immediate action)
+ New customer = +10 (potential long-term value)
+ Service area = +10 (we can serve)
+ High-value service = +20 ($500+ job)
+ Ready to book = +30 (immediate revenue)
+ Follow-up (from call) = +15

Range: 0-100
Threshold for manager notification: 70+
```

### Customization
Allow each org to set:
- Factor weights
- Threshold for notification
- Actions on high-score leads (auto-escalate, notify manager)

---

# 7. AI ORCHESTRATOR SYSTEM

## 7.1 State Machine Definition

```
STATE TRANSITIONS:

GREETING (initial)
  → customer provides information
  → IDENTIFYING_CUSTOMER

IDENTIFYING_CUSTOMER
  → found existing customer? → UNDERSTANDING_REQUEST
  → new customer? → COLLECTING_INFORMATION → UNDERSTANDING_REQUEST

UNDERSTANDING_REQUEST
  → understand intent? → QUALIFYING_LEAD (if lead-like)
  → → CHECKING_AVAILABILITY (if booking request)
  → unclear? → COLLECTING_INFORMATION

QUALIFYING_LEAD
  → qualified? → COLLECTING_INFORMATION
  → not qualified? → FOLLOW_UP or HUMAN_ESCALATION

COLLECTING_INFORMATION
  → have all needed info? → CHECKING_AVAILABILITY (if booking)
  → → FOLLOW_UP (if lead only)

CHECKING_AVAILABILITY
  → slots available? → CONFIRMING_APPOINTMENT
  → no slots? → FOLLOW_UP (offer callback)

CONFIRMING_APPOINTMENT
  → customer confirmed? → BOOKING
  → customer declined? → FOLLOW_UP

BOOKING
  → CRM confirmed? → COMPLETED (appointment booked)
  → CRM failed? → HUMAN_ESCALATION (don't claim success)

FOLLOW_UP
  → COMPLETED

HUMAN_ESCALATION
  → COMPLETED (handed off)

COMPLETED
  → [end]
```

## 7.2 Context & State Persistence

### What Gets Persisted
```
ConversationContext = {
  customer_id: UUID,
  identified_customer: bool,
  customer_name: str,
  customer_phone: str,
  
  intent: "SCHEDULING" | "INQUIRY" | "COMPLAINT" | etc,
  intent_confidence: 0.0-1.0,
  
  extracted_data: {
    service_type: "furnace_repair" | "ac_service" | etc,
    address: "123 Main St, Denver CO",
    preferred_date: "Tuesday",
    preferred_time: "afternoon",
    emergency: bool,
    budget: "$500-1000" | null,
  },
  
  availability_slots: [...],
  selected_slot: {...},
  
  lead_score: 0-100,
  escalation_reason: null | str,
  
  created_at: timestamp,
  updated_at: timestamp,
}
```

### Recovery After Crash
```
If worker crashes mid-conversation:
1. Service finds last conversation_event
2. Load conversation context
3. Replay context to AI: "Here's what we've discussed so far..."
4. Resume conversation at last state
5. Max 3 retries, then escalate to human
```

## 7.3 AI Hallucination Controls

**The AI MUST NEVER invent:**
```
✗ Prices (customer asks "How much?")
  → AI: "Let me check our pricing"
  → Call get_pricing() tool
  → Return actual price from knowledge base
  
✗ Availability (customer asks "Can you come Tuesday?")
  → Call get_available_slots() tool
  → Return only actual available times
  
✗ Policies (customer asks "Can I reschedule?")
  → Call search_knowledge() tool
  → Return actual policy from KB
  
✗ Appointment confirmation (before CRM confirms)
  → AI: "I'm booking this now..."
  → Wait for CRM response
  → Only after confirmation: "Your appointment is booked"
  → If CRM fails: "I'm having trouble booking. Let me escalate to our team."
  
✗ Technician availability (customer asks "Will John be there?")
  → Can't assume anything
  → Call get_technicians() tool
  → Return actual assignment

RULE: If uncertain → ask the customer or escalate.
```

## 7.4 Tool System Architecture

### Tool Definition
```python
class Tool:
    name: str  # "book_appointment"
    description: str  # "Book an appointment for service"
    input_schema: JSONSchema  # Typed validation
    authorization: List[Role]  # Who can call
    timeout: int  # Seconds
    retry_policy: RetryPolicy
    
    async def execute(
        self,
        organization_id: UUID,
        user_id: UUID,
        input_data: dict
    ) -> ToolResult:
        # Validate tenant context
        # Execute tool
        # Audit log
        # Track metrics
        pass
```

### Core Tools (MVP)
```
find_customer(phone: str, email: str) → Customer
create_customer(name: str, phone: str, email: str) → Customer
update_customer(customer_id: UUID, fields: dict) → Customer
get_customer(customer_id: UUID) → Customer

create_lead(customer_id: UUID, service_type: str, description: str) → Lead
update_lead(lead_id: UUID, fields: dict) → Lead
get_lead(lead_id: UUID) → Lead

get_available_slots(
  service: str,
  location: str,
  date_range: [date, date]
) → [Slot]

book_appointment(
  customer_id: UUID,
  service: str,
  slot: Slot
) → Appointment

cancel_appointment(appointment_id: UUID, reason: str) → bool
reschedule_appointment(appointment_id: UUID, new_slot: Slot) → Appointment

create_note(customer_id: UUID, content: str) → Note
send_sms(customer_id: UUID, message: str) → bool

search_knowledge(query: str, top_k: int = 3) → [Document]
get_business_hours() → BusinessHours
get_job_status(job_id: UUID) → Job

transfer_to_human(reason: str, details: str) → bool
create_followup(customer_id: UUID, type: str, due_date: date) → Followup
```

## 7.5 Token Budget & Cost Control

### Per-Call Limits
```
Max input tokens: 2000 (default)
Max output tokens: 500 (default)
Max tool calls: 20
Max conversation duration: 15 minutes
Max cost per call: $0.50

If exceeded → escalate to human
```

### Per-Tenant Limits
```
Daily limit: 100k input tokens, 50k output tokens
Monthly limit: 3M input, 1.5M output

Overage strategy:
→ Alert customer at 80%
→ Suspend new calls at 100%
→ Allow escalations to human
```

---

# 8. INTEGRATION ENGINE

## 8.1 CRM Adapter Pattern

### Interface
```python
class CRMAdapter(ABC):
    """All CRMs must implement this interface."""
    
    async def authenticate(self) -> bool
    async def get_customer(self, external_id: str) -> Customer
    async def find_customer_by_phone(self, phone: str) -> Customer
    async def find_customer_by_email(self, email: str) -> Customer
    async def create_customer(self, data: CustomerCreate) -> Customer
    async def update_customer(self, id: str, data: dict) -> Customer
    
    async def get_lead(self, external_id: str) -> Lead
    async def create_lead(self, data: LeadCreate) -> Lead
    async def update_lead(self, id: str, data: dict) -> Lead
    
    async def get_appointment(self, external_id: str) -> Appointment
    async def create_appointment(self, data: AppointmentCreate) -> Appointment
    async def update_appointment(self, id: str, data: dict) -> Appointment
    async def cancel_appointment(self, id: str, reason: str) -> bool
    async def get_available_slots(self, filters: dict) -> List[Slot]
    
    async def get_jobs(self, customer_id: str) -> List[Job]
    async def get_technicians() -> List[Technician]
    async def get_locations() -> List[Location]
    
    async def health_check() -> HealthStatus
```

### Adapters to Build (MVP Priority)
```
Priority 1 (MVP):
1. ServiceTitan (largest market share, ~40%)
2. Jobber (growing, ~30%)
3. HubSpot (tech-forward, ~15%)

Priority 2 (v1.1):
4. Housecall Pro (niche, ~10%)
5. Salesforce (enterprise, ~5%)

Priority 3 (future):
- FieldEdge
- Workiz
- Pipedrive
- Zoho CRM
```

## 8.2 Field Mapping System

### Configuration UI
```
Internal Field        Provider Field      Transformation
─────────────────────────────────────────────────────
first_name      →    firstName          (passthrough)
phone           →    mobilePhone        (format: E.164)
address         →    streetAddress      (passthrough)
service_area    →    serviceTerritory   (enum map)
tags            →    customTags         (comma-separated)
lead_score      →    leadScore          (normalize: 0-100)
```

### Supported Field Types
```
✓ string
✓ number
✓ boolean
✓ date (ISO8601)
✓ enum (with mapping)
✓ array (comma-separated or JSON)
✓ JSON (complex objects)
```

## 8.3 Webhook Processing

### Architecture
```
Provider sends webhook
    ↓
Webhook Endpoint (signature verification)
    ↓
Deduplication (event_id check)
    ↓
Event Normalization (to internal schema)
    ↓
Queue (Redis/RabbitMQ)
    ↓
Worker Process
    ↓
Update Internal Models
    ↓
Trigger Workflows
    ↓
Idempotency Check (don't re-process)
```

### Guarantees
```
✓ At-least-once delivery (with deduplication)
✓ Replay protection (event_id hash)
✓ Exponential backoff (1m, 5m, 30m, 2h, 8h)
✓ Dead-letter queue for unprocessable events
✓ Event logging for audit
```

## 8.4 Rate Limiting & Retry Strategy

### Per-Integration Limits
```
ServiceTitan: 100 req/sec
Jobber: 50 req/sec
HubSpot: 10 req/sec (free tier)
Salesforce: 15 req/sec (per user)

Implementation:
- Token bucket algorithm
- Backoff: exponential + jitter
- Circuit breaker if error rate > 50%
```

### Retry Logic
```
Transient errors (5xx, timeout):
  → Retry with exponential backoff
  → Max 3 retries
  
Permanent errors (4xx except 429):
  → Fail immediately
  → Log error
  → Escalate

Rate limit (429):
  → Wait + retry
  → Max 5 retries (up to 8 hours)
```

---

# 9. VOICE & COMMUNICATIONS

## 9.1 Voice Provider

### Twilio Configuration
```
- Incoming phone number routing
- IVR/Studio workflow for call handling
- Transcription enabled
- Recording enabled
- Barge-in detection enabled
- Silence timeout: 30 seconds
- Max call duration: 15 minutes (soft), 20 minutes (hard)
```

### Voice Metrics to Track
```
Per call:
- call_id (unique)
- duration
- status (completed, failed, transferred, abandoned)
- start_time, end_time
- customer_id
- transfer_count
- voice_latency (first response < 1s)
- barge-in count
- transcription accuracy (confidence score)
- cost (Twilio pricing)
- LLM cost
- total call cost
```

## 9.2 Text-to-Speech & Speech-to-Text

### TTS Configuration
```
Provider: Twilio (default), with fallback options
Voice: Natural sounding, gender-neutral
Speed: Normal (1.0x)
Pause handling: Natural pauses in response
Emotion: Neutral, professional, friendly
Language support: English (US/UK), Spanish, etc
```

### STT Configuration
```
Provider: Twilio (bundled)
Language: Auto-detect or tenant-specified
Confidence scoring: Track accuracy
Custom vocabulary: CRM terms, service areas, etc
Profanity filter: Optional
```

## 9.3 Call Transfer to Human

### When to Escalate
```
Automatic triggers:
- Customer requests transfer
- AI uncertain (confidence < 0.7)
- Emergency detected
- Complaint/angry customer
- System/tool failures
- After 3 AI re-prompts on single issue

User-initiated:
- Manager takes over conversation
- Agent joins call
```

### Transfer Flow
```
AI: "I'm connecting you with our team..."
    ↓
[Call transferred to available human]
    ↓
Human: "Hi, [AI] told me about your [issue]..."
    ↓
[Conversation continues]
```

## 9.4 SMS Strategy

### Use Cases
```
1. Appointment Confirmation
   "Your HVAC service is confirmed for Tuesday 2-4pm 
    at 123 Main St. Reply CONFIRM or call 555-HVAC-1"

2. Appointment Reminder
   "Reminder: Your furnace service is tomorrow 10am-12pm.
    Reply CONFIRM or 555-HVAC-1 to reschedule."

3. Follow-up Request
   "How was your recent HVAC service? Reply with 5-star 
    rating or feedback."

4. Missed Call Recovery
   "Hi, someone called from 555-0123. Need HVAC service?
    Reply YES to schedule or 555-HVAC-1."

5. Lead Qualification
   "Is your AC still broken? We can send someone today.
    Reply YES or call 555-HVAC-1."
```

### Compliance
```
✓ Track opt-in/opt-out (TCPA)
✓ Support STOP/START/HELP commands
✓ Honor unsubscribe requests immediately
✓ Comply with state-specific laws (carrier requirements)
✓ Log all opt-out requests for audit
✓ Include company name & number in messages
```

## 9.5 Call Recording & Transcription

### Configuration
```
Recording enabled by default (configurable)
Automatic transcription: yes
Retention: 30 days (default, configurable)
Compliance:
  - Two-party consent states: require consent flow
  - One-party consent: collect opt-out
  - EU: GDPR retention (max 3 years)
```

### Storage
```
Format: .wav (audio), .json (transcript with timings)
Location: S3 (encrypted, private)
Access:
  - Customer: can download own recordings
  - Org admin: can listen to any recording
  - PII redaction: automatic masking of phone/SSN
```

---

# 10. WORKFLOW & AUTOMATION

## 10.1 Workflow Engine

### Trigger Types
```
Scheduling:
- appointment.created
- appointment.updated
- appointment.cancelled
- job.completed

Communication:
- call.started
- call.ended
- message.received
- conversation.escalated

System:
- integration.connected
- integration.failed
- lead_score > threshold
```

### Conditions
```
if lead.lead_score > 80 AND lead.source = "call"
  → notify_manager
  
if appointment.status = "completed" AND customer.is_repeat = true
  → send_review_request

if call.duration > 10 minutes
  → send_summary_email
```

### Actions
```
✓ send_sms
✓ send_email
✓ create_task
✓ create_note
✓ assign_to_user
✓ schedule_followup
✓ update_crm
✓ notify_slack (future)
✓ call_webhook (future)
```

## 10.2 Missed Call Recovery

### Flow
```
Missed Call Detected
    ↓
[5-minute delay] ← Don't spam immediately
    ↓
Send SMS: "We missed your call. Need HVAC help? Reply YES"
    ↓
[Wait 1 hour for response]
    ↓
If customer replies YES:
    → Trigger new AI conversation (SMS)
    → Qualification
    → Booking
    → Create lead/appointment
    ↓
If no reply:
    → Create task for team
    → Increase lead score for callbacks
```

### Metrics
```
Track:
- Missed calls by hour/day/location
- Recovery rate (% that respond to SMS)
- Booked from recovery
- Revenue from recovery
```

---

# 11. ANALYTICS & BILLING

## 11.1 Analytics Events

### Event Schema
```json
{
  "event_id": "uuid",
  "event_type": "call.completed",  // snake_case
  "timestamp": "2024-08-22T14:30:00Z",
  "organization_id": "uuid",
  "user_id": "uuid (if applicable)",
  "entity_type": "call",
  "entity_id": "uuid",
  "properties": {
    "duration_seconds": 180,
    "customer_id": "uuid",
    "service_type": "furnace_repair",
    "outcome": "appointment_booked",
    "ai_model": "gpt-4o",
    "cost": 0.05
  },
  "context": {
    "user_agent": "...",
    "ip_address": "...",
    "session_id": "..."
  }
}
```

### Core Events
```
user.signup
user.login
user.logout

organization.created
organization.updated

agent.created
agent.updated
agent.tested
agent.deployed

call.started
call.ended
call.transferred
call.failed

conversation.started
conversation.completed
conversation.escalated

message.sent
message.delivered
message.failed

appointment.booked
appointment.confirmed
appointment.cancelled
appointment.rescheduled
appointment.completed

lead.created
lead.updated
lead.qualified
lead.disqualified

integration.connected
integration.disconnected
integration.synced
integration.failed

billing.subscription_started
billing.subscription_upgraded
billing.subscription_cancelled
billing.invoice_created
billing.payment_succeeded
billing.payment_failed
```

## 11.2 Dashboard Metrics

### Call Analytics
```
Active Calls: real-time count
Calls Today: 0-24h
Calls This Week: graph
Call Completion Rate: % that end in booking
Avg Call Duration: minutes
Missed Calls: count + recovery rate
Answer Rate: % of incoming calls answered by AI
```

### Appointments
```
Appointments Booked: today, this week, this month
Appointments Kept: %
Cancellation Rate: %
Rescheduled: count
No-Show Rate: %
Revenue Impact: estimated from appointment values
```

### Leads
```
Leads Created: today, week, month
Lead Score Distribution: histogram
Qualified Rate: % that convert to appointment
Avg Time to Qualification: hours
Top Sources: which channel (voice, SMS, web)
```

### AI Performance
```
Model Used: GPT-4o, Claude, etc
Avg First Response: milliseconds
Tool Call Success Rate: %
Hallucination Rate: manually tracked
Cost per Call: $ average
Cost per Appointment: $
Cost per Lead: $
```

### Usage & Costs
```
Voice Minutes: used, remaining
SMS Sent: count
API Calls: count
LLM Tokens In: count
LLM Tokens Out: count
Storage: GB used

Cost Breakdown:
- Voice: $ (Twilio)
- SMS: $ (Twilio)
- LLM: $ (OpenAI/Anthropic)
- Compute: $ (AWS)
- Storage: $ (S3)
- Other: $ (third-party)
Total: $
```

## 11.3 Billing System

### Plans
```
Starter: $99/month
- 100 voice minutes
- 500 SMS
- 1 agent
- 1 integration
- Community support

Growth: $299/month
- 1000 voice minutes
- 5000 SMS
- 5 agents
- 5 integrations
- Email support
- Advanced analytics

Pro: $999/month
- 10000 voice minutes
- 50000 SMS
- Unlimited agents
- Unlimited integrations
- Priority support
- Custom AI configuration

Enterprise: Custom
- Unlimited everything
- Dedicated account manager
- SLA guarantee
- Custom integrations
- Private AI option
```

### Overage Pricing
```
Voice: $0.05 per minute
SMS: $0.01 per message
API calls: $0.0001 per call
LLM tokens: varies by model
```

### Stripe Integration
```
✓ Subscription management
✓ Usage-based billing
✓ Invoices generated automatically
✓ Webhook notifications
✓ Failed payment recovery (3 retries over 7 days)
✓ Dunning management (pause service after 14 days)
```

---

# 12. INFRASTRUCTURE & DEPLOYMENT

## 12.1 AWS Architecture

```
┌─────────────────────────────────────────────────────────┐
│                       ROUTE53 (DNS)                      │
│         app.example.com  →  ALB IP                      │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│          ALB (Application Load Balancer)                 │
│  - HTTPS termination (ACM certificate)                  │
│  - Route /api → api-service                            │
│  - Route /websocket → ws-service                       │
│  - Health check: /health/live                          │
└────┬──────────────────────────────────────┬────────────┘
     │                                      │
┌────▼─────────────────┐    ┌──────────────▼──────┐
│  ECS Service: API    │    │ ECS Service: Web    │
│  - 2-4 tasks        │    │ - 1-2 tasks        │
│  - 512MB RAM        │    │ - 256MB RAM        │
│  - Port 8000        │    │ - Port 3000        │
└────┬─────────────────┘    └──────────────┬──────┘
     │                                      │
     └──────────────┬───────────────────────┘
                    │
     ┌──────────────┼──────────────┐
     │              │              │
┌────▼──────┐ ┌────▼──────┐ ┌────▼──────┐
│ RDS       │ │ Redis     │ │ S3        │
│ PostgreSQL│ │ Cache     │ │ (docs,   │
│ Multi-AZ  │ │ Sessions  │ │  recordings)
│           │ │ Queues    │ │           │
└───────────┘ └───────────┘ └───────────┘

Background:
┌────────────────────────────────────┐
│ ECS Service: Worker               │
│ - Process Celery tasks           │
│ - 2-4 tasks (scale by queue depth)│
│ - Handles integrations, webhooks │
└────────────────────────────────────┘
```

## 12.2 Terraform Structure

```
infrastructure/terraform/
├── modules/
│   ├── networking/
│   │   ├── vpc.tf
│   │   ├── subnets.tf
│   │   ├── nat.tf
│   │   └── security_groups.tf
│   ├── database/
│   │   ├── rds.tf
│   │   ├── parameter_groups.tf
│   │   └── backups.tf
│   ├── cache/
│   │   └── elasticache.tf
│   ├── storage/
│   │   ├── s3.tf
│   │   └── kms.tf
│   ├── compute/
│   │   ├── ecs_cluster.tf
│   │   ├── ecs_services.tf
│   │   ├── iam_roles.tf
│   │   └── autoscaling.tf
│   ├── monitoring/
│   │   ├── cloudwatch.tf
│   │   ├── alarms.tf
│   │   └── dashboards.tf
│   └── security/
│       ├── waf.tf
│       ├── secrets_manager.tf
│       └── kms.tf
├── environments/
│   ├── dev/
│   │   └── terraform.tfvars
│   ├── staging/
│   │   └── terraform.tfvars
│   └── production/
│       └── terraform.tfvars
└── global/
    ├── main.tf
    ├── provider.tf
    ├── backend.tf
    └── variables.tf
```

## 12.3 Deployment Pipeline

```
Git Push to main
    ↓
GitHub Actions Triggers
    ├─ Lint (Ruff, Black)
    ├─ Type Check (Pyright)
    ├─ Unit Tests (Pytest)
    ├─ Integration Tests
    ├─ Security Scan (Bandit, safety)
    └─ Container Scan (Trivy)
    ↓
Build Docker Images
    ├─ api:sha
    ├─ worker:sha
    ├─ web:sha
    └─ webhook-worker:sha
    ↓
Push to ECR
    ↓
[MANUAL APPROVAL for staging]
    ↓
Terraform Plan (staging)
    ↓
Deploy to Staging
    ├─ Update ECS services
    ├─ Run migrations
    ├─ Health checks
    └─ E2E tests
    ↓
[MANUAL APPROVAL for production]
    ↓
Terraform Plan (production)
    ↓
Deploy to Production
    ├─ Canary: 10% of traffic for 15 min
    ├─ Monitor error rate & latency
    ├─ Auto-rollback if metrics exceed thresholds
    └─ Full deployment if canary succeeds
```

---

# 13. TESTING STRATEGY

## 13.1 Test Types & Coverage

| Test Type | Tool | Scope | Frequency |
|-----------|------|-------|-----------|
| **Unit** | Pytest | Individual functions | On commit |
| **Integration** | Pytest | Multiple components | On commit |
| **Contract** | Pytest | Integration adapters | On commit |
| **API** | Pytest + Requests | REST endpoints | On commit |
| **E2E** | Playwright | Complete user flows | Before deploy |
| **Load** | k6 | Performance under load | Weekly |
| **Security** | OWASP, BANDIT | Vulnerability scan | On commit |
| **AI Evals** | Custom | AI response quality | On model changes |

## 13.2 Critical E2E Test Flows

```
✓ Signup → Organization creation → CRM connection → Test call
✓ Incoming call → Customer identification → Availability check → Booking
✓ SMS missed call recovery
✓ Human escalation & transfer
✓ CRM outage handling (don't falsely confirm)
✓ Calendar outage handling
✓ Webhook delivery & retry
✓ Tenant isolation (can't access another org's data)
✓ Duplicate booking prevention
✓ Integration reconnect after failure
```

## 13.3 AI Evaluation

### Test Dataset
Create 50+ realistic HVAC conversations:

```
Normal booking (10 scenarios):
- "I need AC service Monday"
- "Furnace isn't working"
- "Do you do maintenance plans?"

Emergency (5 scenarios):
- "My AC broke, it's 95 degrees"
- "No heat in winter"

Edge cases (10 scenarios):
- "Can I move my appointment?"
- "How much does this cost?"
- "What time works for you?"
- Ambiguous dates ("sometime next week")
- Ambiguous addresses ("Main Street, Denver" — multiple matches)

Failure scenarios (10 scenarios):
- CRM outage (should NOT confirm booking)
- Calendar outage (should NOT confirm booking)
- LLM timeout (fallback to human)
- Network latency (handle gracefully)

Adversarial (15 scenarios):
- Angry customer (escalate)
- Prompt injection attempt (ignore)
- Customer manipulation ("Your competitor charged $50")
- Out of service area (decline)
- Unsupported service (decline gracefully)
```

### Metrics
```
✓ Task completion rate (% that reach intended state)
✓ Tool correctness (% of tool calls with right parameters)
✓ Factual accuracy (prices, policies, availability correct)
✓ Booking correctness (appointments booked correctly)
✓ State transitions (correct state machine flow)
✓ Escalation appropriateness (escalated when needed)
✓ Hallucination rate (% of false claims)
✓ Latency (p50, p95, p99)
✓ Cost per call
```

---

# 14. PHASE 0: REPOSITORY BOOTSTRAP

## 14.1 Phase 0 Deliverables

```
✓ Git repository initialized
✓ Project structure created
✓ Docker Compose for local development
✓ Database schema and migrations
✓ Authentication system (JWT)
✓ Multi-tenancy middleware
✓ API base structure
✓ Frontend shell
✓ CI/CD pipeline
✓ Documentation
✓ All tests passing
```

## 14.2 Exact Deliverables

### Git Repository
```
repository-root/
├── .github/
│   ├── workflows/
│   │   ├── test.yml (lint, type-check, test)
│   │   ├── security.yml (bandit, safety)
│   │   └── deploy.yml (build, push, deploy)
│   └── pull_request_template.md
├── .env.example
├── .gitignore
├── README.md
├── ARCHITECTURE.md (from this spec)
├── SECURITY.md
├── DEVELOPMENT.md
├── ROADMAP.md
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py (FastAPI app)
│   │   ├── config.py (settings validation)
│   │   ├── dependencies.py (shared dependencies)
│   │   ├── auth/
│   │   │   ├── routes.py (login, signup, refresh)
│   │   │   ├── models.py (JWT schemas)
│   │   │   └── service.py (JWT/password handling)
│   │   ├── db/
│   │   │   ├── base.py (declarative base)
│   │   │   ├── models.py (all SQLAlchemy models)
│   │   │   └── connection.py (SessionLocal)
│   │   ├── middleware/
│   │   │   ├── tenant.py (extract org_id from token)
│   │   │   ├── error_handler.py (exception -> JSON)
│   │   │   └── logging.py (request logging)
│   │   ├── routes/
│   │   │   ├── api/
│   │   │   │   ├── v1/
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── organizations.py
│   │   │   │   │   ├── users.py
│   │   │   │   │   └── health.py
│   │   │   │   └── router.py (combine routes)
│   │   │   └── router.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── organization.py
│   │   │   └── errors.py
│   │   ├── utils/
│   │   │   ├── security.py (bcrypt, JWT)
│   │   │   └── validation.py
│   │   └── services/
│   │       └── user_service.py
│   ├── migrations/ (Alembic)
│   │   ├── alembic.ini
│   │   ├── env.py
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   ├── tests/
│   │   ├── conftest.py (pytest fixtures)
│   │   ├── test_auth.py
│   │   ├── test_organization.py
│   │   └── test_database.py
│   ├── Dockerfile
│   ├── requirements.txt (or pyproject.toml)
│   └── Makefile
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx (root layout)
│   │   ├── page.tsx (home/login)
│   │   ├── api/
│   │   │   └── route.ts (API client setup)
│   │   ├── auth/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   ├── signup/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx
│   │   ├── dashboard/
│   │   │   ├── layout.tsx (authenticated layout)
│   │   │   ├── page.tsx (home)
│   │   │   └── settings/
│   │   │       └── page.tsx
│   │   └── components/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Loading.tsx
│   ├── lib/
│   │   ├── api.ts (API client)
│   │   ├── auth.ts (JWT handling)
│   │   └── hooks.ts (custom React hooks)
│   ├── styles/
│   │   └── globals.css (Tailwind)
│   ├── tests/
│   │   └── example.test.tsx
│   ├── Dockerfile
│   ├── next.config.js
│   ├── tsconfig.json
│   ├── package.json
│   └── Makefile
│
├── infrastructure/
│   ├── terraform/
│   │   ├── modules/ (empty, ready for PHASE 25)
│   │   ├── environments/
│   │   │   ├── dev/
│   │   │   │   └── terraform.tfvars
│   │   │   ├── staging/
│   │   │   │   └── terraform.tfvars
│   │   │   └── production/
│   │   │       └── terraform.tfvars
│   │   ├── global/
│   │   │   ├── main.tf
│   │   │   ├── provider.tf (AWS)
│   │   │   ├── backend.tf (S3 remote state)
│   │   │   └── variables.tf
│   │   └── README.md
│   └── docker/
│       ├── api.dockerfile
│       ├── worker.dockerfile
│       ├── web.dockerfile
│       └── webhook-worker.dockerfile
│
├── docker-compose.yml (local dev: postgres, redis, api, web)
├── docker-compose.prod.yml (future)
├── Makefile (top-level)
├── .pre-commit-config.yaml
└── docs/
    ├── api.md (OpenAPI reference)
    ├── architecture.md (detailed architecture)
    ├── database.md (schema reference)
    └── getting-started.md
```

### Docker Compose (Local Development)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ai_platform
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  minio:  # S3 compatible storage
    image: minio/minio:latest
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    command: server /data

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://dev:dev_password@postgres:5432/ai_platform
      REDIS_URL: redis://redis:6379
      ENVIRONMENT: development
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --reload

  web:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    volumes:
      - ./frontend:/app
    command: npm run dev

volumes:
  postgres_data:
```

### Makefile

```makefile
.PHONY: setup dev test lint format migrate seed reset help

help:
	@echo "Available commands:"
	@echo "  make setup      - Initial setup (install deps, create .env)"
	@echo "  make dev        - Start local dev environment"
	@echo "  make test       - Run all tests"
	@echo "  make lint       - Lint code"
	@echo "  make format     - Format code"
	@echo "  make migrate    - Run database migrations"
	@echo "  make seed       - Seed demo data"
	@echo "  make reset      - Reset database and restart"

setup:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	cp .env.example .env
	docker-compose up -d postgres redis minio
	cd backend && alembic upgrade head

dev:
	docker-compose up

test:
	cd backend && pytest
	cd frontend && npm test

lint:
	cd backend && ruff check app tests
	cd frontend && eslint app lib

format:
	cd backend && black app tests && ruff check --fix app tests
	cd frontend && prettier --write "app/**/*.{ts,tsx}"

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python -m app.cli.seed

reset:
	docker-compose down -v
	docker-compose up -d
	cd backend && alembic upgrade head
```

## 14.3 Phase 0 Acceptance Criteria

```
✓ Repository initialized with correct structure
✓ Docker Compose brings up all services
✓ Database migrations run successfully
✓ POST /api/v1/auth/signup creates organization & user
✓ POST /api/v1/auth/login returns JWT token
✓ GET /api/v1/organizations returns current org (tenant-isolated)
✓ GET /api/v1/health returns 200 OK
✓ Frontend loads at http://localhost:3000
✓ Frontend can login and see dashboard shell
✓ All unit tests pass (>80% coverage)
✓ Linting passes (ruff, black)
✓ Type checking passes (pyright)
✓ README.md has setup instructions
✓ ARCHITECTURE.md documents design
✓ GitHub Actions CI runs (fails if tests fail)
```

---

# 15. DEVELOPMENT PHASES 1-28

## Phase Breakdown

```
PHASE 0:  ✅ Repository bootstrap
PHASE 1:  Database + domain models
PHASE 2:  Authentication + multi-tenancy
PHASE 3:  Backend API (CRUD endpoints)
PHASE 4:  Frontend shell (navigation, layout)
PHASE 5:  LLM provider abstraction (OpenAI, Claude, Gemini)
PHASE 6:  AI orchestrator (state machine, conversation management)
PHASE 7:  Tool system (tool definitions, execution, audit)
PHASE 8:  Knowledge base / RAG (upload, embed, retrieve)
PHASE 9:  Voice integration (Twilio API setup)
PHASE 10: SMS integration (Twilio SMS, opt-out, TCPA)
PHASE 11: Calendar integration (Google Calendar, Microsoft 365)
PHASE 12: Integration engine architecture (adapters, webhooks)
PHASE 13: ServiceTitan integration
PHASE 14: Jobber integration
PHASE 15: Housecall Pro integration
PHASE 16: HubSpot integration
PHASE 17: Salesforce integration
PHASE 18: Workflow engine (triggers, conditions, actions)
PHASE 19: Analytics (event tracking, dashboards)
PHASE 20: Usage metering (token counting, cost tracking)
PHASE 21: Billing (Stripe, subscriptions, invoices)
PHASE 22: Security hardening (penetration testing, audit)
PHASE 23: Observability (OpenTelemetry, Prometheus, Grafana)
PHASE 24: Load testing (k6, performance optimization)
PHASE 25: Terraform (AWS infrastructure)
PHASE 26: AWS deployment (dev environment)
PHASE 27: CI/CD pipeline (GitHub Actions)
PHASE 28: Production readiness (staging, canary deployment)
```

## Phase Execution Rule

**DO NOT generate the entire product in one operation.**

**Work phase by phase.**

Before each phase:
```
1. Inspect repository state
2. Review existing architecture
3. Identify dependencies
4. Create implementation plan for THIS PHASE ONLY
5. Implement features
6. Test thoroughly
7. Fix all failures
8. Document changes
9. Review security
10. Commit to main
11. Report completion
12. Move to next phase
```

---

# 16. ACCEPTANCE CRITERIA

## Phase Acceptance Template

```
PHASE: [number]
STATUS: COMPLETE / IN_PROGRESS / BLOCKED

IMPLEMENTED:
- [ ] Feature 1
- [ ] Feature 2

FILES CREATED:
- app/feature.py
- tests/test_feature.py

FILES CHANGED:
- app/main.py (register routes)
- tests/conftest.py (add fixtures)

TESTS:
- Unit tests: 5 added, all passing
- Integration tests: 3 added, all passing
- E2E tests: 2 added, all passing
- Coverage: 85% (target: 80%+)

SECURITY:
- ✓ No new vulnerabilities
- ✓ Input validation applied
- ✓ Tenant isolation tested
- ✓ Rate limiting tested

PERFORMANCE:
- API response: <100ms (p95)
- Database queries: no N+1 problems
- Memory usage: <100MB

FAILURES:
None

KNOWN LIMITATIONS:
- Feature X not implemented (deferred to PHASE Y)

NEXT PHASE:
PHASE [next number]
```

---

# 17. OPERATING SEQUENCE

## For Each Phase Implementation

```
1. READ THIS SPECIFICATION
2. Inspect current repository state
3. Identify what needs to be done THIS PHASE
4. Create detailed implementation plan
5. Implement the phase
6. Run tests:
   - pytest (all tests pass)
   - ruff check (lint passes)
   - mypy (type check passes)
7. Commit to git
8. Report completion with acceptance criteria template
9. Move to next phase
```

## Critical Rules

```
NEVER skip phases silently
DO NOT assume features are production-ready without testing
DO NOT move forward with critical failures
DO NOT claim completion without passing all tests
DO NOT implement features beyond scope of current phase
DO NOT change architecture without documenting decisions
```

---

# 18. SUMMARY & NEXT STEPS

## What We Have
- **Complete product specification** (this document)
- **Architecture design** (sections 2-12)
- **Technology stack decisions** (section 3 with rationales)
- **Database schema** (section 4, ready for migration)
- **Phase breakdown** (sections 14-15)
- **Acceptance criteria** (section 16)

## What's Missing (Will Create)
- Detailed PHASE 0 implementation plan
- Database schema diagrams (ERD visuals)
- Architecture diagrams (system, deployment, data flow)
- Tech stack decision document
- Integration provider documentation references

## Ready for PHASE 0?

**Checklist before starting:**
```
✓ Repository created (git init)
✓ Project structure created
✓ .env.example created
✓ Docker Compose created
✓ Makefile created
✓ GitHub Actions workflows created
✓ Database migrations prepared
✓ Authentication scaffold ready
✓ API routes scaffold ready
✓ Frontend structure ready
```

---

**This is your master specification. Print it, reference it, and follow it precisely. Success depends on disciplined phase-by-phase execution, not on ambitious big-bang implementation.**

**Ready to begin PHASE 0?**

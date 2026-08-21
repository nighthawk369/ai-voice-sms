# ARCHITECTURE DIAGRAMS & VISUAL SPECIFICATIONS

Complete visual architecture for the AI Voice & SMS platform for field service businesses.

---

## 1. SYSTEM ARCHITECTURE OVERVIEW

### Complete System Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                         CUSTOMER INTERFACES                           │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   ┌─────────────┐      ┌──────────────┐      ┌──────────────┐       │
│   │  Phone Call │      │  SMS/Text    │      │  Web Browser │       │
│   │  (Twilio)   │      │  (Twilio)    │      │   (Web App)  │       │
│   └──────┬──────┘      └──────┬───────┘      └──────┬───────┘       │
│          │                    │                     │                │
│          └────────────────────┼─────────────────────┘                │
│                               │                                       │
└───────────────────────────────┼───────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    COMMUNICATION GATEWAY                              │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ Incoming Call/SMS Handler                                      │  │
│  │ - Phone routing rule                                           │  │
│  │ - Tenant identification (phone number → org_id)                │  │
│  │ - Load agent configuration                                     │  │
│  │ - Load customer (if repeat)                                    │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    AI ORCHESTRATOR (Core Engine)                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ Conversation Manager                                           │  │
│  │ ├── State: GREETING → IDENTIFYING → QUALIFYING →              │  │
│  │ │        COLLECTING → CHECKING_AVAIL → CONFIRMING →           │  │
│  │ │        BOOKING → COMPLETED                                   │  │
│  │ ├── Context Persistence (state saved to database)             │  │
│  │ ├── Token Budget Enforcement (per-call & per-tenant)          │  │
│  │ ├── Hallucination Controls (prices, policies, availability)   │  │
│  │ └── Audit Logging (every action logged)                       │  │
│  │                                                                 │  │
│  │ Intent & Understanding                                         │  │
│  │ ├── Classify customer intent                                   │  │
│  │ ├── Extract required information                               │  │
│  │ └── Determine next state                                       │  │
│  │                                                                 │  │
│  │ Tool Orchestration                                             │  │
│  │ ├── Determine which tools to call                              │  │
│  │ ├── Call tools in correct order                                │  │
│  │ ├── Handle tool failures gracefully                            │  │
│  │ └── Generate response from tool results                        │  │
│  │                                                                 │  │
│  │ Escalation & Fallback                                          │  │
│  │ ├── Detect when to escalate to human                           │  │
│  │ ├── Handle tool timeouts                                       │  │
│  │ └── Fallback to safer options                                  │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────┬──────────────────────────────┬─────────────────────────────┘
           │                              │
    ┌──────▼──────────┐         ┌────────▼────────┐
    │  LLM GATEWAY    │         │  TOOL GATEWAY   │
    │                │         │                 │
    │ ┌────────────┐ │         │ ┌─────────────┐ │
    │ │ OpenAI    │ │         │ │ CRM Ops     │ │
    │ │ (GPT-4o)  │ │         │ │ Calendar    │ │
    │ │           │ │         │ │ SMS Send    │ │
    │ │ ┌────────┐│ │         │ │ Knowledge   │ │
    │ │ │Primary ││ │         │ │ Search      │ │
    │ │ └────────┘│ │         │ │             │ │
    │ └────────────┘ │         │ │ ┌─────────┐ │ │
    │                │         │ │ │Fallback │ │ │
    │ ┌────────────┐ │         │ │ │Escalate │ │ │
    │ │ Claude    │ │         │ │ │if tool  │ │ │
    │ │ (Sonnet)  │ │         │ │ │fails    │ │ │
    │ │           │ │         │ │ └─────────┘ │ │
    │ │ ┌────────┐│ │         │ └─────────────┘ │
    │ │ │Fallback││ │         │                 │
    │ │ └────────┘│ │         └────────┬────────┘
    │ └────────────┘ │                  │
    │                │         ┌────────▼────────┐
    │ ┌────────────┐ │         │ Token Counting  │
    │ │ Gemini    │ │         │ & Budget Mgmt   │
    │ │           │ │         └─────────────────┘
    │ │ ┌────────┐│ │
    │ │ │Option3 ││ │
    │ │ └────────┘│ │
    │ └────────────┘ │
    │                │
    │ ┌────────────┐ │
    │ │ vLLM /     │ │
    │ │ Ollama     │ │
    │ │(Private)   │ │
    │ │            │ │
    │ │ ┌────────┐ │ │
    │ │ │Private │ │ │
    │ │ │GPU     │ │ │
    │ │ └────────┘ │ │
    │ └────────────┘ │
    │                │
    │ Provider       │
    │ Router:        │
    │ Switch based   │
    │ on config      │
    └────────────────┘

           │
           ▼
┌──────────────────────────────────────────────────────────────────────┐
│             INTEGRATION ENGINE & DATA ACCESS LAYER                    │
│                                                                        │
│ CRM Adapters:                                                         │
│ ├── ServiceTitanAdapter (mock for MVP)                                │
│ ├── JobberAdapter (mock for MVP)                                      │
│ ├── HubSpotAdapter (mock for MVP)                                     │
│ ├── HousecallProAdapter (Phase 15)                                    │
│ └── SalesforceAdapter (Phase 17)                                      │
│                                                                        │
│ Other Integrations:                                                   │
│ ├── Google Calendar / Microsoft 365                                   │
│ ├── Webhook Processing (inbound events)                               │
│ ├── Field Mapping (CRM ↔ Internal)                                    │
│ └── Rate Limiting & Retry Logic                                       │
└──────────┬────────────────────────────┬────────────────────────────────┘
           │                            │
    ┌──────▼───────┐            ┌──────▼────────┐
    │ PRIMARY      │            │ CRM/Calendar  │
    │ DATABASE     │            │ EXTERNAL APIs │
    │              │            │               │
    │ PostgreSQL   │            │ ServiceTitan  │
    │ Multi-AZ     │            │ Jobber        │
    │ Encrypted    │            │ HubSpot       │
    │              │            │ Salesforce    │
    │ Tables:      │            │ Google Cal    │
    │ ├── Org      │            │ MS 365        │
    │ ├── User     │            │ Twilio        │
    │ ├── Customer │            │ OpenAI API    │
    │ ├── Lead     │            │ Anthropic API │
    │ ├── Apt      │            │ Google API    │
    │ ├── Call     │            │               │
    │ ├── Message  │            │ (Via adapters │
    │ ├── Integ    │            │  with auth &  │
    │ ├── Webhook  │            │  rate limits) │
    │ ├── Event    │            └───────────────┘
    │ └── Audit    │
    │              │
    └──────┬───────┘
           │
    ┌──────▼───────────┐
    │ CACHE & QUEUE    │
    │                  │
    │ Redis:           │
    │ ├── Sessions     │
    │ ├── JWT cache    │
    │ ├── Rate limits  │
    │ ├── Queues       │
    │ └── Hot data     │
    │ (customers,      │
    │  availability)   │
    └──────────────────┘

        VECTOR DB (for RAG):
        └── Pgvector (in Postgres)
            ├── Knowledge embeddings
            ├── Fast similarity search
            └── < 100ms retrieval
```

---

## 2. REQUEST FLOW DIAGRAM

### Example: Incoming Voice Call → Booking Appointment

```
┌─────────────────┐
│  Customer Call  │
│   (Twilio)      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ Communication Gateway                        │
│ - Receive call event                         │
│ - Extract phone number                       │
│ - Route to correct tenant (org lookup)       │
│ - Load AIAgent configuration                 │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ AI Orchestrator - Initialize Conversation   │
│ - Create Conversation record                │
│ - Set state: GREETING                       │
│ - Load customer (if exists)                 │
│ - Load context (if repeat call)             │
│ - Start conversation event log              │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ LLM Gateway                                  │
│ - Load system prompt                        │
│ - Include tenant configuration              │
│ - Set temperature, token limits             │
│ - Generate greeting: "Hi! This is..."       │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ Response Generation                         │
│ - Convert text to speech (TTS)              │
│ - Stream audio to Twilio                    │
│ - Play: "Hi! This is Acme HVAC..."          │
│ - Log TTS cost                              │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ Customer speaks: "My AC is broken"           │
│ Twilio sends audio to AI transcription      │
│ STT: "My AC is broken" (confidence: 0.95)   │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ Intent Detection (in LLM)                    │
│ - Analyze: "My AC is broken"                │
│ - Intent: SERVICE_REQUEST, EMERGENCY=true  │
│ - Extract: service_type = "AC_REPAIR"       │
│ - Confidence: 0.98                          │
│ - Next state: IDENTIFYING_CUSTOMER          │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ Tool Call: find_customer (by phone)         │
│ - Input: phone = "+1-303-555-0123"          │
│ - Query database                            │
│ - Result: Found customer "John Smith"       │
│ - Save to context                           │
│ - Next state: UNDERSTANDING_REQUEST         │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ LLM: Understanding (with context)           │
│ - Include customer name: "Hi John..."       │
│ - Confirm understanding                     │
│ - Ask clarifying questions if needed        │
│ - Generate response                         │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ Repeat: TTS → Audio → Twilio → Customer     │
│ "Hi John! I'm sorry to hear your AC is      │
│  broken. Let me check our availability      │
│  for AC repair. One moment..."              │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ Tool Call: get_available_slots              │
│ - Input: service="AC_REPAIR"                │
│          location="John's address"          │
│          date_range=[today, today+7]        │
│ - Query integration: Google Calendar        │
│ - Query technician schedules                │
│ - Check service duration (1 hour)           │
│ - Apply business hours                      │
│ - Result: [Tu 2-4pm, We 10-12pm, Th 3-5pm] │
│ - State: CHECKING_AVAILABILITY ✓            │
│ - Next state: CONFIRMING_APPOINTMENT        │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ LLM: Generate confirmation & options       │
│ - Include available times                   │
│ - Ask for preference: "Which works best?"   │
│ - DO NOT confirm yet (waiting for choice)   │
│ - Next state: CONFIRMING_APPOINTMENT        │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ Customer speaks: "Tuesday at 2 PM"          │
│ STT: "Tuesday at 2 PM"                      │
│ Extracted: date=Tuesday, time=2pm           │
│ Confirmation: "You want Tuesday 2-4pm? ✓"   │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ Customer: "Yes"                             │
│ State transition: CONFIRMING → BOOKING      │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ Tool Call: book_appointment                 │
│ - Input: customer_id, service, slot         │
│ - Create idempotency key (prevent dupes)    │
│ - Lock on idempotency key (concurrency)     │
│ - Call CRM adapter: ServiceTitan.create     │
│ - Wait for CRM response (success/failure)   │
│ - Result: appointment_id = "APT-12345"      │
│ - Map external ID                           │
│ - Send SMS confirmation                     │
│ - State: COMPLETED                          │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ LLM: Generate completion message            │
│ "Perfect! I've booked your AC repair for    │
│  Tuesday 2-4 PM. You'll receive a text      │
│  confirmation shortly with the address...   │
│  Thank you for choosing Acme HVAC!"         │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ TTS → Audio → Twilio → Customer             │
│ Play confirmation message                   │
│ End call (customer or AI)                   │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ Finalize Conversation                       │
│ - Save all events to database               │
│ - Save transcript                           │
│ - Record call if enabled                    │
│ - Calculate metrics:                        │
│   * Duration: 4 min 23 sec                 │
│   * Cost: voice $0.22, LLM $0.12, total $0.34
│   * Booking: SUCCESS                        │
│ - Create lead/log activity in CRM           │
│ - Trigger workflows (e.g., send SMS)        │
│ - Send SMS confirmation if not sent         │
│ - Save audit log                            │
│ - Fire event: appointment.booked            │
└────────────────────────────────────────────┘
```

---

## 3. DATA FLOW DIAGRAM

### Multi-Tenancy Data Isolation

```
┌─────────────────────────────────────────────────────────────┐
│                    INCOMING REQUEST                         │
│  POST /api/v1/appointments                                  │
│  Authorization: Bearer <JWT>                                │
│  Body: { ... appointment data ... }                         │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│  MIDDLEWARE: Extract Tenant                                 │
│                                                              │
│  1. Decode JWT (verify signature)                           │
│  2. Extract: user_id = "uuid-123"                          │
│  3. Query: SELECT org_id FROM user WHERE id = user_id      │
│  4. Result: organization_id = "org-456"                     │
│  5. Attach to request context:                              │
│     request.organization_id = "org-456"                     │
│     request.user_id = "uuid-123"                            │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│  ROUTE HANDLER                                              │
│                                                              │
│  @app.post("/appointments")                                 │
│  async def create_appointment(                              │
│      data: AppointmentCreate,                               │
│      org_id: UUID = Depends(get_org_id)  # From context     │
│  ):                                                          │
│      # org_id is automatically "org-456"                    │
│                                                              │
│      appointment = Appointment(                             │
│          organization_id=org_id,  # FORCED                  │
│          customer_id=data.customer_id,                      │
│          ...                                                │
│      )                                                       │
│      session.add(appointment)                               │
│      session.commit()                                       │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│  DATABASE WRITE                                             │
│                                                              │
│  INSERT INTO appointment (                                  │
│      id, organization_id, customer_id, ...                  │
│  ) VALUES (                                                 │
│      'apt-789', 'org-456', 'cust-101', ...                 │
│  )                                                          │
│                                                              │
│  KEY: organization_id = 'org-456' ← IMMUTABLE              │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│  TENANT ISOLATION VERIFICATION                              │
│                                                              │
│  If User B tries to access this appointment:               │
│  1. User B's org_id = 'org-789' (extracted from their JWT)  │
│  2. Query: SELECT * FROM appointment                        │
│            WHERE id = 'apt-789'                             │
│            AND organization_id = 'org-789'                  │
│  3. Result: 0 rows (not found)                              │
│  4. Return: 404 Not Found (or 403 Forbidden)                │
│                                                              │
│  If they try direct SQL:                                    │
│  SELECT * FROM appointment WHERE id = 'apt-789'             │
│  (no org filter) → Code review catches it                   │
└────────────────────────────────────────────────────────────┘
```

---

## 4. LLM PROVIDER ABSTRACTION

### Multi-Provider Architecture

```
┌─────────────────────────────────────────────────┐
│  AI ORCHESTRATOR                                 │
│  (wants to generate text)                        │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  Config: LLM_PROVIDER = "openai"                │
│  (from environment variable)                     │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  LLM ROUTER                                      │
│                                                  │
│  class LLMRouter:                               │
│      async def get_provider(provider_name):     │
│          if provider_name == "openai":          │
│              return OpenAIProvider()            │
│          elif provider_name == "anthropic":     │
│              return AnthropicProvider()         │
│          elif provider_name == "google":        │
│              return GoogleProvider()            │
│          elif provider_name == "local":         │
│              return LocalOpenAIProvider()       │
│                                                  │
│  provider = await router.get_provider("openai")│
└────────────┬────────────────────────────────────┘
             │
             ▼
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌────────────────┐ ┌─────────────────────────────┐
│ OpenAI Config  │ │  OpenAI Provider Class      │
│                │ │                             │
│ API Key: env   │ │  async def generate(       │
│ Model: gpt-4o  │ │      prompt: str            │
│ Base URL:      │ │  ):                         │
│ https://api... │ │                             │
│                │ │  1. Call OpenAI API        │
│                │ │  2. Count tokens           │
│                │ │  3. Track cost             │
│                │ │  4. Log request_id         │
│                │ │  5. Return response        │
│                │ │                             │
└────────────────┘ │  Supports:                  │
                   │  - Text generation          │
                   │  - Tool calling             │
                   │  - Streaming                │
                   │  - Vision (future)          │
                   └─────────────────────────────┘

    ┌─────────────────────────────────┐
    │  Anthropic Provider Class       │
    │                                 │
    │  async def generate(            │
    │      prompt: str                │
    │  ):                             │
    │                                 │
    │  1. Call Anthropic API          │
    │  2. Count tokens (tokens+cache) │
    │  3. Track cost                  │
    │  4. Log request_id              │
    │  5. Return response             │
    │                                 │
    │  Supports:                      │
    │  - Text generation              │
    │  - Tool calling                 │
    │  - Streaming                    │
    │  - Longer context (200k)        │
    └─────────────────────────────────┘

    ┌─────────────────────────────────┐
    │  Google Provider Class          │
    │                                 │
    │  async def generate(            │
    │      prompt: str                │
    │  ):                             │
    │  1. Call Google API             │
    │  2. Count tokens                │
    │  3. Track cost                  │
    │  4. Log request_id              │
    │  5. Return response             │
    │                                 │
    │  Supports:                      │
    │  - Text generation              │
    │  - Tool calling                 │
    │  - Streaming                    │
    │  - Multi-modal (future)         │
    └─────────────────────────────────┘

    ┌─────────────────────────────────────────┐
    │  Local OpenAI-Compatible Provider       │
    │                                         │
    │  Configuration:                         │
    │  Base URL: http://localhost:8000/v1     │
    │  (vLLM endpoint)                        │
    │                                         │
    │  async def generate(                    │
    │      prompt: str                        │
    │  ):                                     │
    │  1. Call local endpoint (vLLM/Ollama)  │
    │  2. Count tokens locally                │
    │  3. No cost (self-hosted)               │
    │  4. Fast inference on local GPU         │
    │  5. Return response                     │
    │                                         │
    │  Supports:                              │
    │  - Text generation                      │
    │  - Fast inference (proprietary model)   │
    │  - GPU-accelerated (Llama, Mistral)     │
    │  - Zero network latency                 │
    └─────────────────────────────────────────┘
```

### Provider Switching at Runtime

```
SCENARIO 1: Primary provider fails
─────────────────────────────────
AI Orchestrator calls OpenAI
  ↓
OpenAI API returns 500 (outage)
  ↓
Circuit breaker opens
  ↓
Fallback to Anthropic
  ↓
Anthropic returns response
  ↓
Continue conversation
  ↓
Log incident: OpenAI outage, fell back to Claude


SCENARIO 2: Customer requires private LLM
──────────────────────────────────────────
Organization.llm_provider = "local"
  ↓
AI Orchestrator calls LLM Router
  ↓
Router returns LocalOpenAIProvider
  ↓
Calls http://localhost:8000/v1/chat/completions
  ↓
vLLM (running on org's GPU) processes request
  ↓
Returns response from proprietary model
  ↓
No data leaves customer's infrastructure
  ↓
Organization satisfied with privacy requirements


SCENARIO 3: Cost optimization
─────────────────────────────
Simple FAQ query:
  → Gemini (cheapest, fast)
  
Normal conversation:
  → OpenAI (good balance)
  
Complex reasoning:
  → Claude (best reasoning)
  
Emergency escalation:
  → Try all providers in parallel
  → Use fastest response
```

---

## 5. DATABASE SCHEMA RELATIONSHIPS

### Simplified ER Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     ORGANIZATION (Tenant)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ id (UUID)          [PK]                                 │   │
│  │ name               [name of business]                    │   │
│  │ timezone           [America/New_York]                    │   │
│  │ created_at         [timestamp]                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                    │
│                              │ (1:N)                              │
│                              │                                    │
│  ┌───────────────────────────┴──────────────────────────────┐   │
│  ├──────────────────┐  ├──────────────────┐                 │   │
│  │ USER             │  │ LOCATION         │                 │   │
│  ├──────────────────┤  ├──────────────────┤                 │   │
│  │ id (UUID)        │  │ id (UUID)        │                 │   │
│  │ org_id (FK)      │  │ org_id (FK)      │                 │   │
│  │ email            │  │ name             │                 │   │
│  │ password_hash    │  │ address          │                 │   │
│  │ role             │  │ phone            │                 │   │
│  └──────────────────┘  └──────────────────┘                 │   │
│                                                               │   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ AI_AGENT                                                │   │
│  │ org_id (FK) | name | status | created_at              │   │
│  │    ├─ AI_AGENT_VERSION (1:N)                           │   │
│  │       ├─ system_prompt, model, config, temperature     │   │
│  │       └─ published/draft/archived status               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    CUSTOMER & BUSINESS DATA                      │
│                                                                   │
│  CUSTOMER (1:N conversations, calls, leads)                      │
│  ├─ org_id (FK to Organization)                                 │
│  ├─ phone, email, name                                          │
│  ├─ tags, metadata                                              │
│  └─ do_not_call, sms_opt_out                                    │
│                                                                   │
│  LEAD (parent: customer)                                         │
│  ├─ org_id (FK)                                                 │
│  ├─ customer_id (FK)                                            │
│  ├─ source, status, score                                       │
│  └─ value, metadata                                             │
│                                                                   │
│  APPOINTMENT (parent: customer)                                  │
│  ├─ org_id (FK)                                                 │
│  ├─ customer_id (FK)                                            │
│  ├─ location_id (FK)                                            │
│  ├─ start_time, end_time, status                                │
│  └─ external_ids (ServiceTitan, Jobber, etc)                    │
│                                                                   │
│  JOB (parent: appointment, customer)                             │
│  ├─ org_id (FK)                                                 │
│  ├─ appointment_id (FK)                                         │
│  ├─ customer_id (FK)                                            │
│  ├─ service_type, status                                        │
│  └─ external_ids (provider-specific)                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                 CONVERSATION & COMMUNICATIONS                    │
│                                                                   │
│  CONVERSATION (parent: customer, agent_version)                  │
│  ├─ org_id (FK)                                                 │
│  ├─ customer_id (FK)                                            │
│  ├─ agent_version_id (FK)                                       │
│  ├─ state (GREETING, IDENTIFYING, etc)                          │
│  ├─ context (JSON: extracted data, conversation state)          │
│  ├─ outcome (COMPLETED, ESCALATED, ABANDONED)                   │
│  └─ created_at, ended_at                                        │
│      │                                                            │
│      ├─ CONVERSATION_EVENT (1:N)                                │
│      │  ├─ event_type (state_change, tool_call, error)          │
│      │  ├─ data (JSON: what happened)                           │
│      │  └─ created_at (timestamp)                               │
│      │                                                            │
│      └─ MESSAGE (1:N)                                           │
│         ├─ role (CUSTOMER, AI, HUMAN)                           │
│         ├─ content                                              │
│         └─ created_at                                           │
│                                                                   │
│  CALL (parent: conversation, customer)                           │
│  ├─ org_id (FK)                                                 │
│  ├─ conversation_id (FK)                                        │
│  ├─ customer_id (FK)                                            │
│  ├─ phone_number                                                │
│  ├─ duration_seconds                                            │
│  ├─ status (completed, failed, transferred)                     │
│  │   ├─ CALL_RECORDING (1:1)                                   │
│  │   │  ├─ s3_path, duration, transcription                     │
│  │   │  └─ retention_expires_at                                 │
│  │   │                                                           │
│  │   └─ CALL_METRICS (1:1)                                      │
│  │      ├─ latency, cost, tool_calls                            │
│  │      └─ ai_model, provider                                   │
│  │                                                               │
│  └─ created_at, ended_at                                        │
│                                                                   │
│  SMS_MESSAGE (1:N)                                              │
│  ├─ org_id (FK)                                                 │
│  ├─ customer_id (FK)                                            │
│  ├─ direction (inbound, outbound)                               │
│  ├─ content, status                                             │
│  └─ delivery_status (pending, delivered, failed)                │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  INTEGRATIONS & EXTERNAL DATA                    │
│                                                                   │
│  INTEGRATION (org has many)                                      │
│  ├─ org_id (FK)                                                 │
│  ├─ provider (ServiceTitan, Jobber, HubSpot)                    │
│  ├─ status (connected, error, disconnected)                     │
│  ├─ last_sync_at                                                │
│  │   ├─ INTEGRATION_CREDENTIAL (1:1 encrypted)                  │
│  │   │  ├─ oauth_token, api_key (encrypted at rest)             │
│  │   │  ├─ scopes, expires_at                                   │
│  │   │  └─ last_refreshed_at                                    │
│  │   │                                                            │
│  │   ├─ INTEGRATION_MAPPING (1:N)                               │
│  │   │  ├─ internal_field ↔ provider_field                      │
│  │   │  ├─ transformation rules                                 │
│  │   │  └─ type (string, enum, number, date)                    │
│  │   │                                                            │
│  │   └─ INTEGRATION_WEBHOOK (1:N)                               │
│  │      ├─ url (webhook endpoint)                               │
│  │      ├─ events (customer.updated, appointment.created)       │
│  │      ├─ secret (for signature verification)                  │
│  │      └─ enabled, last_fired_at                               │
│  │                                                                │
│  └─ created_at, updated_at                                      │
│                                                                   │
│  EXTERNAL_OBJECT_MAPPING (bridge between systems)                │
│  ├─ org_id (FK)                                                 │
│  ├─ provider (ServiceTitan, Jobber)                             │
│  ├─ object_type (customer, appointment, lead, job)              │
│  ├─ internal_id (our UUID)                                      │
│  ├─ external_id (provider's ID)                                 │
│  ├─ external_version (for conflict detection)                   │
│  └─ last_synced_at                                              │
│                                                                   │
│  WEBHOOK_EVENT (inbound webhooks)                                │
│  ├─ org_id (FK)                                                 │
│  ├─ provider (ServiceTitan sent this)                           │
│  ├─ event_type (customer.updated, appointment.created)          │
│  ├─ payload (JSON: full webhook data)                           │
│  ├─ processed (bool: did we handle it?)                         │
│  └─ created_at                                                  │
│      └─ DEAD_LETTER_EVENT (if processing failed)                │
│         ├─ error_reason                                         │
│         ├─ retry_count                                          │
│         └─ last_retry_at                                        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. DEPLOYMENT ARCHITECTURE

### AWS Infrastructure (dev/staging/production)

```
┌──────────────────────────────────────────────────────────────────┐
│                         INTERNET                                  │
└────────────────┬─────────────────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────────────────┐
│              ROUTE53 (DNS)                                        │
│                                                                   │
│  app.example.com     → ALB IP (HTTPS)                            │
│  api.example.com     → ALB IP (HTTPS)                            │
└────────────────┬─────────────────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────────────────┐
│           APPLICATION LOAD BALANCER (ALB)                         │
│                                                                   │
│  - HTTPS termination (ACM certificate)                           │
│  - Health check: /health/live                                    │
│  - Target groups:                                                │
│    ├── API service (port 8000)                                   │
│    ├── Web service (port 3000)                                   │
│    └── WebSocket service (port 8001)                             │
│                                                                   │
│  - Security Group: Allow 443/80 from anywhere                    │
│    Allow 8000, 3000 from ALB only                                │
└────┬──────────────────────────────────────────────┬──────────────┘
     │                                              │
     ▼                                              ▼
┌─────────────────────────────────────┐    ┌──────────────────────┐
│    ECS SERVICE: API                 │    │  ECS SERVICE: Web    │
│                                     │    │                      │
│ Cluster: ai-platform               │    │ Cluster: ai-platform │
│ Task Definition: api:sha            │    │ Task: web:sha        │
│                                     │    │                      │
│ Tasks (replicas): 2-4               │    │ Tasks: 1-2           │
│ CPU: 512                            │    │ CPU: 256             │
│ Memory: 1024 MB                     │    │ Memory: 512 MB       │
│                                     │    │                      │
│ Environment:                        │    │ Environment:         │
│ - DATABASE_URL (Secrets Manager)    │    │ - NEXT_PUBLIC_API_URL│
│ - REDIS_URL                         │    │ - NODE_ENV=prod      │
│ - LLM_API_KEY (Secrets)             │    │                      │
│ - AWS_REGION                        │    │ Image: web:sha       │
│                                     │    │ Port: 3000           │
│ Image: api:sha                      │    │                      │
│ Port: 8000                          │    │ Logging:             │
│                                     │    │ - CloudWatch         │
│ Logging:                            │    │ - /ecs/web           │
│ - CloudWatch                        │    │                      │
│ - /ecs/api                          │    └──────────────────────┘
│                                     │
│ Health Check:                       │
│ - /health/live                      │
│ - Interval: 30s                     │
│ - Timeout: 5s                       │
│ - Healthy threshold: 2              │
│ - Unhealthy threshold: 2            │
│                                     │
│ Autoscaling:                        │
│ - Min: 2 tasks                      │
│ - Max: 4 tasks                      │
│ - Scale on CPU > 70% for 5 min      │
│ - Scale on memory > 75% for 5 min   │
│                                     │
│ Security Group:                     │
│ - Ingress: 8000 from ALB            │
│ - Egress: All to RDS, Redis, etc    │
└─────────────────────────────────────┘

Background Tasks:
┌──────────────────────────────────┐
│  ECS SERVICE: Worker             │
│                                  │
│  Cluster: ai-platform            │
│  Task Definition: worker:sha      │
│                                  │
│  Tasks (replicas): 1-4            │
│  Scale on queue depth             │
│  CPU: 512                         │
│  Memory: 1024 MB                  │
│                                  │
│  Processes:                      │
│  - Celery worker                 │
│  - Integration syncs             │
│  - Webhook processing            │
│  - Scheduled tasks               │
│  - Email delivery                │
│                                  │
│  Queue: Redis Celery queue       │
│  Max retries: 3                  │
│                                  │
│  Logging: CloudWatch /ecs/worker │
└──────────────────────────────────┘

Data Layer:
    │
    ├─ RDS PostgreSQL
    │  ├─ Multi-AZ (production)
    │  ├─ Instance class: db.t3.small (dev) → db.r6i.large (prod)
    │  ├─ Encryption at rest (KMS)
    │  ├─ Automated backups (7 days retention)
    │  ├─ Read replicas (optional, prod only)
    │  └─ Private subnet (no public access)
    │
    ├─ ElastiCache (Redis)
    │  ├─ Node type: cache.t3.micro (dev) → cache.r6g.xlarge (prod)
    │  ├─ Encryption at rest & in transit
    │  ├─ Automatic failover (production)
    │  ├─ Backup enabled
    │  └─ Private subnet
    │
    └─ S3
       ├─ Bucket: recordings-<env>
       ├─ Bucket: documents-<env>
       ├─ Bucket: exports-<env>
       ├─ Encryption: KMS
       ├─ Versioning enabled
       ├─ Lifecycle rules (delete old)
       ├─ Block public access
       └─ CloudFront distribution (optional, CDN)

Monitoring & Logging:
┌─────────────────────────┐
│  CloudWatch             │
│  ├─ Metrics             │
│  │  ├─ API latency      │
│  │  ├─ Error rate       │
│  │  ├─ RDS CPU/memory   │
│  │  ├─ ECS task count   │
│  │  └─ Custom metrics   │
│  │                      │
│  ├─ Logs                │
│  │  ├─ /ecs/api         │
│  │  ├─ /ecs/web         │
│  │  ├─ /ecs/worker      │
│  │  ├─ /rds/postgresql  │
│  │  └─ /lambda/...      │
│  │                      │
│  └─ Dashboards          │
│     ├─ System health    │
│     ├─ API performance  │
│     ├─ Error tracking   │
│     └─ Cost analysis    │
│                         │
└─────────────────────────┘

Alerting:
┌─────────────────────────┐
│  SNS → PagerDuty        │
│  Alerts:                │
│  ├─ 5xx error > 1%      │
│  ├─ Latency p99 > 5s    │
│  ├─ RDS CPU > 90%       │
│  ├─ No successful calls │
│  └─ Deployment failure  │
└─────────────────────────┘
```

---

## 7. STATE MACHINE DIAGRAM

### Conversation State Transitions

```
                      ┌─────────────────┐
                      │    GREETING     │
                      │  "Hi, this is.."│
                      └────────┬────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ IDENTIFYING_CUSTOMER │
                    │ Find or create user  │
                    └─────────┬────────────┘
                              │
                              ▼
                 ┌────────────────────────────┐
                 │  UNDERSTANDING_REQUEST     │
                 │  What does customer need?  │
                 └────────┬───────────────────┘
                          │
                 ┌────────┴────────────────┐
                 │                         │
                 ▼                         ▼
        ┌──────────────────┐     ┌──────────────────┐
        │ QUALIFYING_LEAD  │     │ COLLECTING_INFO  │
        │ Get details      │     │ Get all needed   │
        └────┬─────────────┘     │ information      │
             │                   └────┬─────────────┘
        ┌────▼────┐                  │
        │          │                  │
    YES │      NO  │                  │
        │    DISQ  │                  │
        │          │                  ▼
        │    ┌─────▼──────┐   ┌─────────────────────┐
        │    │  FOLLOW_UP │   │ CHECKING_AVAILABILITY│
        │    │  Schedule  │   │ Check calendar      │
        │    │  callback  │   └────┬────────────────┘
        │    └────────────┘         │
        │                 ┌─────────┴──────────┐
        └─────────────────┤                    │
                          │          ┌─────────▼─────────┐
                  Slots   │          │ NO SLOTS AVAILABLE│
                available │          │ FOLLOW_UP         │
                          │          │ (offer callback)  │
                          │          └───────────────────┘
                          │
                          ▼
                ┌──────────────────────┐
                │ CONFIRMING_APPOINTMENT│
                │ "Tuesday 2-4pm OK?"  │
                └──┬──────────────┬───┘
                   │              │
               YES │          NO  │
              ┌────▼────┐    ┌────▼──────┐
              │  BOOKING │    │ FOLLOW_UP │
              │Call CRM  │    │ Reschedule│
              └─┬────┬───┘    └───────────┘
         ┌──────┘    │
         │      ┌────▼──────────┐
     SUCCESS    │ CRM FAILED    │
         │      │ DON'T claim   │
         │      │ success       │
         │      │ ESCALATE      │
         │      └───────────────┘
         │
         ▼
    ┌────────────┐
    │ COMPLETED  │
    │ Appointment│
    │ Booked ✓   │
    └────────────┘


ESCALATION PATHS:

At any point, AI can escalate to HUMAN_ESCALATION:

    [Any State] 
         │
         ▼
    Customer requests transfer?
    AI uncertain (confidence < 0.7)?
    Tool failure?
    Emergency?
    Complaint?
         │
         ▼
    ┌──────────────────────┐
    │ HUMAN_ESCALATION     │
    │ Transfer to human    │
    │ Pass context         │
    │ Log reason           │
    └────┬─────────────────┘
         │
         ▼
    ┌──────────────────────┐
    │ COMPLETED            │
    │ (handed off)         │
    └──────────────────────┘


ABANDONMENT:

    [Any State]
         │
         ▼
    Customer hangs up?
    30s+ silence?
    Max duration (15m)?
    Max retries exceeded?
         │
         ▼
    ┌──────────────────────┐
    │ COMPLETED            │
    │ outcome=ABANDONED    │
    │ missed_call recovery │
    │ triggered            │
    └──────────────────────┘
```

---

This document provides complete visual representations of:
1. Overall system architecture
2. Request flow for a real booking scenario
3. Data flow and tenant isolation
4. LLM provider abstraction
5. Database relationships
6. AWS deployment infrastructure
7. State machine for conversations

Each diagram is ready to reference during implementation and can be shared with stakeholders.


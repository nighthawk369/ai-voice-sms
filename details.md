MASTER CLAUDE CODE PROMPT
# ============================================================


│   ├── docker/
│   └── scripts/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   ├── e2e/
│   ├── load/
│   ├── security/
│   └── ai-evals/
│
├── docs/
├── scripts/
├── .github/
│   └── workflows/
│
├── docker-compose.yml
├── Makefile
├── README.md
├── CLAUDE.md
├── ARCHITECTURE.md
├── ROADMAP.md
├── SECURITY.md
└── DEVELOPMENT.md


Maintain clean separation between:


- domain
- AI
- API
- integrations
- infrastructure
- frontend
- workers


============================================================
6. HIGH-LEVEL ARCHITECTURE
============================================================


                         CUSTOMER
                            |
                    Phone / SMS / Web
                            |
                            v
                 COMMUNICATION GATEWAY
                            |
                            v
                     AI ORCHESTRATOR
                            |
              +-------------+-------------+
              |                           |
              v                           v
        MODEL GATEWAY                TOOL GATEWAY
              |                           |
              v                           |
        MODEL ROUTER                      |
              |                           |
      +-------+-------+            +------+------+
      |       |       |            |             |
    OpenAI Claude Gemini          CRM         Calendar
                                  |
                                  +---- SMS
                                  |
                                  +---- Customer DB
                                  |
                                  +---- Scheduling
                                  |
                                  +---- Human escalation
                                  |
                                  +---- Workflows
                                  |
                                  v
                         INTEGRATION ENGINE
                                  |
          +-----------------------+-----------------------+
          |          |             |          |           |
     ServiceTitan  Jobber   Housecall Pro  HubSpot   Salesforce
          |
          +---- future providers


============================================================
7. MULTI-TENANCY

Everything must be tenant-aware.

Core entities:

Organization
User
OrganizationUser
Role
Permission
Location
PhoneNumber
AIAgent
AIAgentVersion
Customer
CustomerAddress
Lead
Appointment
Job
Conversation
Message
Call
CallRecording
Integration
IntegrationCredential
IntegrationScope
IntegrationMapping
IntegrationSync
IntegrationWebhook
KnowledgeBase
KnowledgeDocument
KnowledgeChunk
Tool
Workflow
WorkflowRun
AuditLog
UsageRecord
BillingAccount
Subscription
Notification
APIKey
WebhookEndpoint
Event
DeadLetterEvent

Every tenant-owned table must have:

organization_id.

Implement strict tenant isolation.

Test attempts to access:

another organization's customers
calls
messages
documents
recordings
integrations
credentials
analytics
billing
AI configuration

All must fail.

============================================================
8. USER ROLES

Roles:

OWNER
ADMIN
MANAGER
AGENT
VIEWER

Implement granular permissions.

============================================================
9. DATABASE

Use PostgreSQL.

Use UUIDs.

Use:

created_at
updated_at

where appropriate.

Use foreign keys.

Use unique constraints.

Use indexes based on real access patterns.

Use soft deletion where appropriate.

Implement migration system using Alembic.

No manual production schema changes.

============================================================
10. CORE CUSTOMER MODEL

Customer:

id
organization_id
external_ids
first_name
last_name
phone
email
addresses
tags
metadata
created_at
updated_at

Lead:

id
organization_id
customer_id
source
status
service_type
description
urgency
estimated_value
lead_score
metadata

Appointment:

id
organization_id
customer_id
technician_id
location_id
start_time
end_time
status
external_ids

Job:

id
organization_id
customer_id
appointment_id
status
service_type
description
technician_id
external_ids

============================================================
11. EXTERNAL ID MAPPING

Create:

external_object_mappings

Fields:

organization_id
provider
object_type
internal_id
external_id
external_version
last_synced_at

Example:

internal customer:
customer_123

ServiceTitan:
ST-98765

Jobber:
JB-123

HubSpot:
HS-456

Never contaminate core domain models with provider-specific structures.

============================================================
12. CRM ABSTRACTION

Create:

CRMAdapter

Required operations:

create_customer()
get_customer()
find_customer_by_phone()
find_customer_by_email()
update_customer()
create_lead()
get_lead()
update_lead()
create_note()
create_appointment()
get_appointment()
update_appointment()
cancel_appointment()
get_available_slots()
get_jobs()
get_technicians()
get_locations()

Provider-specific adapters:

ServiceTitanAdapter
JobberAdapter
HousecallProAdapter
HubSpotAdapter
SalesforceAdapter
GenericRESTAdapter

Never expose provider-specific models to core business logic.

============================================================
13. INTEGRATIONS

Initial priority:

ServiceTitan
Jobber
Housecall Pro
HubSpot
Salesforce

Later:

FieldEdge
Workiz
Service Fusion
Zoho
Microsoft Dynamics
Pipedrive
Freshsales

Also support:

Google Calendar
Microsoft 365
QuickBooks
Xero
Zapier
Make
generic REST
generic webhooks

Do not implement all integrations blindly.

Implement the architecture first.

Prioritize based on actual customer demand.

============================================================
14. OAUTH

Implement:

OAuth authorization
state validation
PKCE where supported
redirect validation
scopes
token refresh
token expiry
token revocation
reconnect
disconnect

Never expose tokens to frontend.

Never log tokens.

Encrypt credentials.

Use AWS Secrets Manager or equivalent secure secret storage.

============================================================
15. INTEGRATION ENGINE

Create:

IntegrationRegistry
IntegrationFactory
IntegrationManager
CredentialManager
OAuthManager
ExternalIDMapper
FieldMapper
WebhookProcessor
RetryPolicy
RateLimitHandler
IntegrationHealthMonitor

Every integration must implement:

auth
API client
models
mapping
retries
rate limits
pagination
error translation
health check
webhooks
tests
============================================================
16. FIELD MAPPING

UI:

Internal field
->
Provider field

Support:

string
number
boolean
date
enum
array
JSON

Allow:

custom fields
default values
transformations
enum mappings
============================================================
17. WEBHOOK ENGINE

Generic webhook architecture:

Provider
|
Webhook endpoint
|
signature verification
|
deduplication
|
event normalization
|
queue
|
worker
|
domain event
|
workflow

Support:

signatures
event IDs
replay protection
idempotency
retries
dead-letter queues
logs
metrics
============================================================
18. EVENT SYSTEM

Canonical events:

customer.created
customer.updated
lead.created
lead.updated
appointment.created
appointment.updated
appointment.cancelled
job.created
job.updated
job.completed
call.started
call.completed
message.received
message.sent
integration.connected
integration.disconnected
integration.error

Version events:

appointment.created.v1

============================================================
19. AI ORCHESTRATOR

Responsibilities:

conversation management
state
context
intent
tool selection
tool execution
retrieval
escalation
fallback
budget enforcement
audit logging

AI must not directly execute database queries.

AI must not directly execute shell commands.

AI must not directly execute arbitrary code.

============================================================
20. AI STATE MACHINE

States:

GREETING
IDENTIFYING_CUSTOMER
UNDERSTANDING_REQUEST
QUALIFYING_LEAD
COLLECTING_INFORMATION
CHECKING_AVAILABILITY
CONFIRMING_APPOINTMENT
BOOKING
FOLLOW_UP
HUMAN_ESCALATION
COMPLETED

Persist state.

Support recovery after worker/process restart.

============================================================
21. AI TOOLS

Implement:

find_customer
create_customer
update_customer
create_lead
update_lead
get_customer
get_available_slots
book_appointment
reschedule_appointment
cancel_appointment
create_note
send_sms
transfer_to_human
create_followup
get_business_hours
search_knowledge
get_job_status

Every tool:

typed schema
authorization
tenant context
timeout
retry policy
audit
metrics
============================================================
22. AI HALLUCINATION CONTROLS

The AI must never:

invent prices
invent policies
invent availability
invent technician schedules
claim appointment confirmation before CRM confirmation
claim payment success without payment confirmation
fabricate customer records
fabricate service availability

If uncertain:

ask
or
escalate.

Business facts should come from:

CRM
calendar
tools
knowledge base

not model memory.

============================================================
23. PROMPT ARCHITECTURE

Prompt layers:

SYSTEM
DEVELOPER
TENANT_CONFIGURATION
RETRIEVED_KNOWLEDGE
CUSTOMER_INPUT

Retrieved documents and customer messages are untrusted content.

They cannot override system/developer instructions.

Implement prompt injection defense.

============================================================
24. AI AGENT CONFIGURATION

Dashboard configuration:

business name
business description
services
service areas
business hours
holidays
emergency services
pricing policy
booking rules
appointment duration
transfer number
after-hours behavior
FAQ
CRM
calendar
knowledge base
allowed tools
voice
language
SMS
recording settings

============================================================
25. AI VERSIONING

Agents support:

draft
testing
published
archived

Version:

system prompt
model
provider
configuration
tools
knowledge base
temperature
token configuration

Rollback must be possible.

============================================================
26. LLM PROVIDER ABSTRACTION

Create:

LLMProvider

Methods:

generate()
stream()
generate_structured()
embed()
count_tokens()

Track:

provider
model
tokens_in
tokens_out
latency
cost
request_id

Providers:

OpenAI
Anthropic
Google
LocalOpenAICompatible

============================================================
27. MODEL ROUTER

Create:

ModelRouter

Allow different models for:

simple FAQ
normal conversation
complex reasoning
structured extraction
embeddings
private deployments

Support fallback:

Provider A
|
failure
|
Provider B

Provider failure must not automatically result in false customer-facing success.

============================================================
28. PRIVATE AI

Architecture must support:

Cloud LLM
Private LLM
Self-hosted LLM

Architecture:

AI Gateway
|
Model Router
|
+-------------+
| |
Cloud Private
LLM endpoint
|
vLLM
|
GPU

Support:

OpenAI-compatible endpoints.

Future:

vLLM
Ollama
dedicated GPU cluster
customer-owned inference
VPC/private deployment

Private AI must be configurable per organization.

============================================================
29. MODEL EVALUATION

Create benchmarks for:

accuracy
latency
cost
tool calling
structured output
hallucination
booking correctness
escalation correctness

Store results.

Model choice must be data-driven.

============================================================
30. RAG / KNOWLEDGE BASE

Support:

PDF
DOCX
TXT
HTML
URLs

Pipeline:

upload
|
parse
|
clean
|
chunk
|
embed
|
vector store
|
retrieve
|
rerank
|
LLM

Metadata:

organization_id
location_id
document_id
category
service_type

Strict tenant isolation.

============================================================
31. VOICE

Create VoiceProvider.

Architecture:

incoming call
|
identify tenant
|
load agent
|
load configuration
|
load customer
|
conversation
|
LLM
|
tool
|
response
|
voice

Track:

call_id
tenant_id
customer_id
start
end
duration
status
recording
transcript
model
provider
latency
cost
tool_calls

Support:

barge-in
interruption
silence
timeout
transfer
hangup
failure recovery

============================================================
32. CALL RECORDING

Support configurable:

recording enabled
recording disabled

Store recordings privately.

Support configurable retention.

Support consent/notification workflows.

Do not hard-code legal assumptions.

============================================================
33. SMS

Support:

inbound SMS
outbound SMS
templates
AI responses
delivery status
retries
opt-out

Support:

STOP
START
HELP

Maintain communication compliance controls.

============================================================
34. MISSED CALL RECOVERY

Flow:

missed call
|
delay
|
SMS
|
customer reply
|
AI
|
qualification
|
booking

Track:

missed calls
recovered calls
recovered leads
appointments
estimated revenue

============================================================
35. CALENDAR

CalendarProvider:

get_availability()
create_event()
update_event()
cancel_event()

Initial:

Google Calendar
Microsoft 365

Scheduling considers:

business hours
holidays
technician availability
service duration
buffers
locations
timezone
existing appointments

Prevent double booking.

============================================================
36. HUMAN ESCALATION

Support:

phone transfer
SMS handoff
email
internal notification
CRM note

Reasons:

customer_request
AI_uncertain
emergency
complaint
high_value_lead
billing_issue
technical_issue

============================================================
37. WORKFLOW ENGINE

Implement generic:

WHEN
IF
THEN

Examples:

missed_call
->
send_sms

lead.created
+
lead_score > 80
->
notify_manager

appointment.completed
->
send_review_request

Architecture must support future workflow types.

============================================================
38. DASHBOARD

Pages:

/dashboard
/calls
/conversations
/customers
/leads
/appointments
/jobs
/ai-agent
/knowledge
/integrations
/workflows
/analytics
/billing
/settings
/team
/audit-log

Operational SaaS UI.

Responsive.

Accessible.

Fast.

============================================================
39. ANALYTICS

Track:

calls
answered calls
missed calls
recovered calls
leads
appointments
conversion rate
estimated revenue
AI cost
average call duration
tool failures
integration failures
customer satisfaction
escalation rate
booking rate

============================================================
40. AI ANALYTICS

Track:

time to first response
time to first token
LLM latency
voice latency
tool latency
tool success rate
escalation rate
booking rate
call completion
cost per call
cost per appointment
hallucination rate

============================================================
41. USAGE METERING

Create usage ledger.

Track:

voice_minutes
sms_messages
llm_input_tokens
llm_output_tokens
embedding_tokens
storage
API_requests
workflow_runs

Calculate:

cost per call
cost per minute
cost per lead
cost per appointment
cost per tenant

Never calculate billing from frontend data.

============================================================
42. UNIT ECONOMICS

Dashboard for internal/admin use:

revenue
AI cost
voice cost
SMS cost
compute cost
storage cost
database cost
gross margin
cost/customer
cost/call
cost/appointment

Support tenant profitability analysis.

============================================================
43. BILLING

Stripe.

Plans:

Starter
Growth
Pro
Enterprise

Support:

subscription
usage
trial
upgrade
downgrade
cancel
invoice
payment failure
webhooks

Stripe webhooks must be idempotent.

============================================================
44. API

REST API:

/api/v1/

Endpoints:

/auth
/organizations
/users
/agents
/customers
/leads
/appointments
/jobs
/calls
/conversations
/messages
/integrations
/knowledge
/workflows
/analytics
/billing
/audit-logs

Generate OpenAPI.

Maintain API versioning.

============================================================
45. API KEYS

Tenant API keys:

create
list
revoke
rotate
expiration
scopes

Never return full key after creation.

============================================================
46. RATE LIMITING

Rate-limit by:

tenant
user
API key
IP
endpoint

Different limits for:

authentication
webhooks
AI
public APIs
internal APIs

============================================================
47. SECURITY

Implement:

authentication
authorization
RBAC
tenant isolation
input validation
rate limiting
secure headers
CORS
CSRF where applicable
encryption
secret management
audit logging
webhook signatures
request IDs
PII controls

Test:

SQL injection
XSS
CSRF
SSRF
broken access control
tenant breakout
secret leakage
JWT manipulation
API key abuse
webhook spoofing
prompt injection

============================================================
48. PII / DATA CLASSIFICATION

Classify:

public
internal
confidential
sensitive

Identify PII fields.

Never log sensitive PII unnecessarily.

Mask:

phone numbers
emails
addresses
tokens
payment data

where appropriate.

Create configurable retention policies.

============================================================
49. DATA EXPORT / DELETION

Support:

customer data export
organization data export
customer deletion
conversation deletion
recording deletion
document deletion
organization deletion

Deletion must propagate to relevant systems where contractually and
technically appropriate.

============================================================
50. AUDIT LOG

Track:

login
integration connection
integration disconnect
CRM write
appointment creation
appointment cancellation
AI configuration change
billing changes
user invitation
permission changes
API key creation
API key revocation
data export
data deletion

Record:

actor
tenant
action
resource
resource_id
timestamp
IP
metadata

============================================================
51. ADMIN PLATFORM

Internal admin dashboard:

organizations
usage
billing
health
integrations
errors
incidents
AI performance
cost
feature flags
support tools

Admin functions must be isolated from tenant functions.

============================================================
52. FEATURE FLAGS

Support:

voice_ai
sms_ai
servicetitan
jobber
housecallpro
hubspot
salesforce
private_ai
custom_integrations
workflows
advanced_analytics

Tenant-level feature flags.

============================================================
53. ONBOARDING

Wizard:

organization
business details
locations
hours
services
phone
CRM
calendar
knowledge
AI
test call
production

Target:

signup -> first test call < 15 minutes.

============================================================
54. TEST CALL / SANDBOX

Create sandbox mode.

Sandbox:

CRM writes simulated
calendar simulated
SMS simulated
test calls

Production:

real systems.

Never allow accidental production writes during tests.

============================================================
55. DUPLICATE PREVENTION

Appointment creation must be idempotent.

Example:

tenant
customer
service
time
location

must produce an idempotency key.

If API times out after creating appointment,
retry must not create duplicate appointment.

============================================================
56. RETRY ARCHITECTURE

External API failures:

request
|
failure
|
retry
|
exponential backoff
|
jitter
|
retry
|
dead letter

Use:

timeouts
retry limits
circuit breakers
bulkheads

============================================================
57. OBSERVABILITY

Use:

OpenTelemetry
Prometheus
Grafana
structured JSON logs
Sentry or equivalent

Trace:

request
conversation
call
tool
CRM request
LLM request
workflow

Every operation should have request/trace IDs.

============================================================
58. SLO

Initial targets:

API:
99.9%

Webhook processing:
99.9%

AI tool execution:
99.9%

CRM synchronization:
99.5%

Track:

p50
p95
p99

============================================================
59. ALERTING

Alert on:

API 5xx
high latency
ECS failures
RDS CPU
RDS storage
Redis memory
queue depth
webhook failures
LLM provider failures
CRM failures
voice provider failures
SMS failures
billing failures
certificate expiry

============================================================
60. AI EVALUATION

Create at least 50 realistic HVAC conversations.

Test:

normal booking
emergency
pricing
after-hours
angry customer
existing customer
new customer
ambiguous date
ambiguous address
CRM outage
calendar outage
LLM outage
human transfer
cancellation
rescheduling
duplicate booking
unsupported service
outside service area
knowledge question
prompt injection
customer manipulation

Measure:

task completion
tool correctness
factual accuracy
booking correctness
state transitions
escalation
hallucination
latency
cost

Run regression suite on prompt/model changes.

============================================================
61. TESTING

Every feature requires:

unit tests
integration tests
API tests
E2E tests where applicable

Critical E2E flows:

signup
login
organization
user invitation
CRM connection
customer creation
incoming call
customer identification
lead creation
availability
booking
SMS
missed call
human transfer
CRM failure
calendar failure
billing
webhook
tenant isolation

============================================================
62. LOAD TESTING

Use k6 or equivalent.

Test:

100 concurrent calls
500 concurrent API requests
1000 concurrent API requests
webhook bursts
CRM sync bursts

Measure:

latency
throughput
error rate
CPU
memory
queue depth

============================================================
63. CI/CD

GitHub Actions.

Pipeline:

commit
|
lint
|
type check
|
unit tests
|
integration tests
|
security scan
|
build
|
container scan
|
deploy staging
|
E2E
|
approval
|
production

============================================================
64. DOCKER

Separate images:

api
worker
web
webhook-worker

Use:

multi-stage builds
non-root
health checks
small images

Never deploy latest to production.

Use immutable Git SHA tags.

============================================================
65. TERRAFORM

ALL AWS infrastructure must be Terraform-managed.

Never manually create production infrastructure.

Create:

infrastructure/terraform/

modules:

networking
security-groups
iam
kms
ecr
rds
redis
s3
ecs
alb
route53
acm
secrets
cloudwatch
waf
autoscaling
backup

Environments:

dev
staging
production

============================================================
66. AWS

Use:

VPC
public/private subnets
ALB
ECS Fargate
RDS PostgreSQL
ElastiCache Redis
S3
ECR
Secrets Manager
KMS
CloudWatch
Route53
ACM
WAF
IAM
SNS/SQS/EventBridge where appropriate

============================================================
67. NETWORKING

Architecture:

Internet
|
ALB
|
ECS
|
+--- RDS
+--- Redis
+--- S3
+--- external APIs

RDS and Redis must be private.

No database public access.

============================================================
68. SECURITY GROUPS

Separate:

alb_sg
api_sg
worker_sg
rds_sg
redis_sg

Only required communication allowed.

============================================================
69. RDS

Production:

Multi-AZ
encryption
backup
deletion protection
private subnet
monitoring
performance monitoring

Development can be smaller.

============================================================
70. REDIS

Use ElastiCache.

Support:

encryption
authentication
private networking
high availability where appropriate

============================================================
71. S3

Buckets:

documents
recordings
exports

Enable:

encryption
private access
versioning where appropriate
lifecycle rules
public access block

============================================================
72. KMS

Use KMS for encryption.

Least privilege.

============================================================
73. SECRETS

Use AWS Secrets Manager.

Store:

LLM credentials
voice credentials
SMS credentials
CRM credentials
Stripe credentials
database credentials

Terraform creates secret resources,
but production secret values must not be stored in Terraform source.

============================================================
74. IAM

Separate roles:

ECS API
worker
webhook worker
web
Terraform
GitHub Actions

Least privilege.

No AdministratorAccess for workloads.

============================================================
75. GITHUB OIDC

Do not use permanent AWS credentials in GitHub.

Use:

GitHub OIDC
AWS STS
IAM role

Restrict by:

repository
branch
environment

============================================================
76. TERRAFORM STATE

Terraform state:

S3

Use locking supported by the chosen Terraform version.

Enable:

encryption
versioning
restricted access

Never commit state.

============================================================
77. TERRAFORM STRUCTURE

infrastructure/
└── terraform/
├── modules/
├── environments/
│ ├── dev/
│ ├── staging/
│ └── production/
└── global/

Use reusable modules.

Do not duplicate infrastructure logic.

============================================================
78. TERRAFORM VALIDATION

CI must run:

terraform fmt -check
terraform init
terraform validate
terraform plan
tflint
tfsec or equivalent
checkov or equivalent

============================================================
79. TERRAFORM DEPLOYMENT

Development:

Terraform
|
ECR
|
Docker
|
ECS
|
Migration
|
Smoke test

Staging:

Terraform
|
ECS
|
E2E
|
approval

Production:

Terraform plan
|
manual approval
|
apply
|
migration
|
deployment
|
health
|
smoke
|
production

============================================================
80. ECS

Services:

ai-api
ai-worker
ai-webhook-worker
ai-web

Configure:

CPU
memory
environment
secrets
health checks
logging
IAM
autoscaling

============================================================
81. DATABASE MIGRATIONS

Deployment:

new image
|
migration task
|
Alembic
|
success
|
ECS deployment

Migrations must be backward-compatible where practical.

Never perform destructive migrations without a documented strategy.

============================================================
82. HEALTH CHECKS

API:

/health/live
/health/ready

Readiness should not fail merely because an optional third-party provider
is temporarily unavailable.

============================================================
83. AUTOSCALING

Scale API based on:

CPU
memory
request load
latency where appropriate

Workers based on:

queue depth
processing latency

============================================================
84. DOMAIN / TLS

Support:

app.example.com
api.example.com

Use:

Route53
ACM
ALB

HTTPS only.

Automatic certificate renewal.

============================================================
85. WAF

Protect public endpoints.

Configure:

common attack protection
rate limiting
bad request protection

Do not blindly block legitimate AI/API traffic.

============================================================
86. BACKUPS

Configure:

RDS backups
S3 versioning
retention
restore procedures

Regularly test restoration.

A backup that has never been restored is not considered verified.

============================================================
87. DISASTER RECOVERY

Initial:

RPO <= 1 hour
RTO <= 4 hours

Document and test.

============================================================
88. ENVIRONMENT ISOLATION

Dev:

cheap
small

Staging:

production-like

Production:

high availability
protected
manual deployment approval

Never allow dev/staging access to production databases or secrets.

============================================================
89. COST MANAGEMENT

Tag AWS resources:

Project
Environment
Owner
ManagedBy
CostCenter
Service

Track:

ECS
RDS
Redis
NAT
S3
CloudWatch
data transfer

Create AWS budget alerts.

============================================================
90. COST OPTIMIZATION

Development:

small infrastructure
low log retention
scheduled shutdown where appropriate

Production:

optimize after measuring actual workload.

============================================================
91. PRODUCT ANALYTICS

Track product events:

signup
onboarding_started
onboarding_completed
integration_connected
agent_created
test_call
production_call
lead_created
appointment_booked
appointment_cancelled
workflow_created
subscription_started
subscription_upgraded
subscription_cancelled

Do not collect unnecessary personal information.

============================================================
92. SUPPORT / ADMIN TOOLS

Admin must be able to:

inspect tenant
inspect integration health
inspect usage
inspect errors
inspect calls
disable tenant
reconnect integration
view audit trail
manage feature flags

Actions must be audited.

============================================================
93. INTEGRATION HEALTH

Dashboard:

ServiceTitan
Connected
Last sync
Latency
Error rate
API status

Support:

Reconnect
Disconnect
Test connection
View errors

============================================================
94. INTEGRATION CERTIFICATION

Every provider adapter must pass a common contract:

authentication
customer lookup
customer creation
customer update
lead
appointment
job
webhook
pagination
retry
rate limits
idempotency
errors

No adapter is production-certified until all required tests pass.

============================================================
95. CUSTOM INTEGRATION BUILDER

Future feature.

Allow:

REST API
API key
Bearer
OAuth2
Basic Auth
webhooks

Mapping:

request
response
fields
transformation
events

Build architecture now so this can be added without rewriting core.

============================================================
96. WHITE LABEL / ENTERPRISE READINESS

Architecture should eventually support:

custom branding
custom domains
enterprise SSO
SAML
OIDC
advanced roles
private AI
dedicated deployment
custom retention
custom integrations

Do not implement all enterprise features immediately.

============================================================
97. LEGAL / COMPLIANCE ARCHITECTURE

Do not make legal claims.

Build configurable controls for:

call recording
consent
SMS opt-out
data retention
data deletion
privacy
data export
regional restrictions

The product must be designed so legal/compliance requirements can evolve.

============================================================
98. DEPENDENCY SECURITY

CI must check:

dependency vulnerabilities
container vulnerabilities
Terraform security
secret leakage
license issues

Use dependency pinning.

Generate SBOM where practical.

============================================================
99. SUPPLY CHAIN SECURITY

Use:

locked dependencies
immutable container tags
dependency scanning
container scanning
GitHub OIDC
least-privilege CI
protected branches

Do not execute untrusted CI artifacts with production permissions.

============================================================
100. INCIDENT RESPONSE

Create runbooks:

API outage
database outage
Redis outage
ECS outage
LLM outage
voice outage
SMS outage
CRM outage
ServiceTitan outage
webhook failure
bad deployment
migration failure
Terraform failure
credential compromise
security incident

============================================================
101. MODEL OUTAGE

If primary LLM fails:

Primary
|
failure
|
fallback model
|
failure
|
human escalation / safe response

Never fabricate a successful operation.

============================================================
102. CRM OUTAGE

If CRM is unavailable:

AI must not claim:

"Your appointment is booked."

Instead:

"I’m unable to access the scheduling system right now."

Collect information.

Create follow-up.

Escalate when appropriate.

============================================================
103. CALENDAR OUTAGE

Same principle.

No confirmed booking without successful confirmation.

============================================================
104. AI COST CONTROL

Per-call limits:

max tokens
max tool calls
max duration
max cost

Per-tenant:

daily limit
monthly limit
alert threshold

============================================================
105. LEAD SCORING

Configurable scoring.

Example:

emergency +30
new customer +10
service area +10
high-value service +20
ready to book +30

Range:

0–100

Allow tenant customization.

============================================================
106. NOTIFICATIONS

Channels:

SMS
email
in-app
webhook

Future:

Slack

Templates support variables.

============================================================
107. DATA RETENTION

Configurable:

call recordings
transcripts
messages
documents
audit logs

Respect configured retention.

============================================================
108. DISASTER TESTING

Regularly test:

database restore
application redeployment
provider outage
queue failure
Redis failure
bad deployment
credential rotation

============================================================
109. DEVELOPMENT EXPERIENCE

Provide:

make setup
make dev
make test
make lint
make format
make migrate
make seed
make reset
make infra-plan
make infra-apply

Local Docker Compose:

PostgreSQL
Redis
MinIO
API
worker
webhook-worker
web

Optional:

Ollama

============================================================
110. DEMO DATA

Create:

Acme HVAC

Demo users:

owner
manager
agent

Demo:

customers
leads
appointments
calls
knowledge
sandbox integrations

============================================================
111. COMPLETE DEMO

Demo flow:

customer calls
|
AI greets
|
understands issue
|
identifies customer
|
checks availability
|
books
|
creates CRM record
|
sends SMS
|
dashboard updates

============================================================
112. FAILURE DEMO

Simulate CRM failure.

Expected:

AI does not falsely confirm booking.

AI collects details.

AI creates follow-up.

AI escalates.

============================================================
113. TERRAFORM ACCEPTANCE

A clean environment must be deployable from Terraform.

After deployment:

DNS works
HTTPS works
frontend works
API works
database works
Redis works
workers work
logs appear
metrics appear
alerts exist
migrations work
sandbox test works

============================================================
114. PRODUCTION ACCEPTANCE

Before production:

unit tests pass
integration tests pass
contract tests pass
E2E tests pass
security tests pass
load tests pass
backup restore tested
tenant isolation tested
duplicate booking tested
provider outage tested
LLM outage tested
SMS outage tested
calendar outage tested
webhook replay tested

============================================================
115. DOCUMENTATION

Create:

README.md
ARCHITECTURE.md
ROADMAP.md
SECURITY.md
DEVELOPMENT.md

Also:

docs/
├── architecture.md
├── database.md
├── api.md
├── integrations.md
├── ai.md
├── rag.md
├── voice.md
├── security.md
├── deployment.md
├── terraform.md
├── infrastructure.md
├── monitoring.md
├── billing.md
├── testing.md
├── ai-evaluation.md
├── disaster-recovery.md
├── incident-response.md
└── runbooks/

============================================================
116. DEVELOPMENT PHASES

PHASE 0
Repository bootstrap

PHASE 1
Database + domain

PHASE 2
Authentication + multi-tenancy

PHASE 3
Backend API

PHASE 4
Frontend shell

PHASE 5
AI provider abstraction

PHASE 6
AI orchestrator

PHASE 7
Tool system

PHASE 8
Knowledge/RAG

PHASE 9
Voice

PHASE 10
SMS

PHASE 11
Calendar

PHASE 12
Integration engine

PHASE 13
ServiceTitan

PHASE 14
Jobber

PHASE 15
Housecall Pro

PHASE 16
HubSpot

PHASE 17
Salesforce

PHASE 18
Workflow engine

PHASE 19
Analytics

PHASE 20
Usage metering

PHASE 21
Billing

PHASE 22
Security hardening

PHASE 23
Observability

PHASE 24
Load testing

PHASE 25
Terraform

PHASE 26
AWS deployment

PHASE 27
CI/CD

PHASE 28
Production readiness

============================================================
117. PHASE EXECUTION RULE

DO NOT attempt to generate the entire product in one uncontrolled operation.

Work phase by phase.

Before each phase:

inspect repository
inspect architecture
inspect dependencies
create implementation plan
implement
test
fix
document
review security
continue

Do not move forward with unresolved critical failures.

============================================================
118. REPORTING

At the end of every phase report:

PHASE
STATUS

Implemented:
Files created:
Files changed:
Tests:
Security:
Performance:
Failures:
Known limitations:
Next phase:
============================================================
119. CODE QUALITY

Python:

ruff
black
pytest
mypy/pyright

TypeScript:

eslint
prettier
tsc
vitest
playwright

Avoid:

massive files
circular dependencies
duplicate logic
global mutable state
provider-specific leakage
untyped data
silent exceptions

Prefer:

dependency injection
interfaces
protocols
typed schemas
small modules
clear boundaries

============================================================
120. ENVIRONMENT CONFIGURATION

Create .env.example.

Group:

DATABASE
REDIS
AWS
AUTH
LLM
VOICE
SMS
CRM
CALENDAR
STRIPE
OBSERVABILITY

Validate configuration on startup.

Fail fast on required missing configuration.

============================================================
121. AI CODING RULE

AI-generated code must be treated as untrusted until verified.

For every implementation:

inspect
type-check
lint
test
security-review

Do not blindly accept generated code.

============================================================
122. THIRD-PARTY API RULE

When implementing integrations:

Find official documentation.
Determine actual authentication mechanism.
Determine supported endpoints.
Determine scopes.
Determine rate limits.
Determine pagination.
Determine webhooks.
Determine API version.
Implement adapter.
Add tests.

Never invent endpoints.

If credentials are unavailable:

implement mocked architecture
and explicitly state that live integration testing is pending.

============================================================
123. API VERSION ISOLATION

External API versions must be isolated inside adapters.

Example:

integrations/
servicetitan/
v2/

A provider API version change must not require changes to core AI/business logic.

============================================================
124. FEATURE FLAG SAFETY

New integrations and dangerous operations should initially be behind
feature flags.

Production activation requires explicit configuration.

============================================================
125. BUSINESS OPERATION SAFETY

High-impact operations:

book appointment
cancel appointment
reschedule
send message
create payment
modify customer
delete data

must have:

typed input
authorization
audit
idempotency where appropriate
confirmation where appropriate

============================================================
126. HUMAN OVERRIDE

Humans must always be able to:

take over conversation
cancel AI action
correct customer record
correct appointment
disable AI
disable integration
review transcript

============================================================
127. CUSTOMER TRUST

Dashboard must clearly show:

what AI did
what CRM changed
what appointment was booked
what message was sent
what model was used
what integrations were used

No hidden business actions.

============================================================
128. FINAL PRODUCT POSITIONING

The system should ultimately allow the customer to say:

"We already use ServiceTitan/Jobber/Housecall Pro/etc."

and your answer should be:

"Keep it. Connect it."

The AI becomes the interface between:

customer
phone
AI
CRM
calendar
technicians
workflow
business owner

============================================================
129. FINAL ARCHITECTURE
                     CUSTOMER
                        |
                PHONE / SMS / WEB
                        |
                        v
             COMMUNICATION LAYER
                        |
                        v
                  AI GATEWAY
                        |
                MODEL ROUTER
                        |
         +--------------+--------------+
         |              |              |
       OpenAI        Anthropic      Gemini
         |
         |
    FUTURE PRIVATE AI
         |
        vLLM
         |
        GPU
                        |
                        v
                AI ORCHESTRATOR
                        |
                     TOOLS
                        |
              INTEGRATION ENGINE
                        |
   +----------+---------+---------+---------+
   |          |         |         |         |

ServiceTitan Jobber HCP HubSpot Salesforce
|
+------ Calendar
|
+------ SMS
|
+------ Accounting
|
+------ Workflows

Underlying platform:

         AWS
          |
   +------+------+
   |             |
  ECS           RDS
   |             |
  Redis          |
   |             |
   +------+------+
          |
         S3

Infrastructure:

Terraform
|
AWS

Deployment:

GitHub
|
GitHub Actions
|
Tests
|
Security
|
Docker
|
ECR
|
Terraform
|
ECS
|
Production

============================================================
130. START NOW

First inspect the repository.

Do not assume files exist.

Do not start by writing application code blindly.

First:

Inspect repository.
Create ARCHITECTURE.md.
Create ROADMAP.md.
Create SECURITY.md.
Create DEVELOPMENT.md.
Create infrastructure documentation.
Create PHASE 0 implementation plan.
Implement PHASE 0.
Run tests.
Run lint.
Run type checking.
Run security checks.
Review generated code.
Report status.

Then proceed sequentially.

Never skip a phase silently.

Never claim a feature is production-ready without passing its acceptance criteria.

============================================================
END MASTER SPECIFICATION


## The Claude Code operating sequence


After putting that into `CLAUDE.md`, I would **not** simply tell Claude:


> "Build the product."


Use this sequence.


### 1. Initial architecture


```text
Read CLAUDE.md.


Inspect the entire repository.


Do not implement the product yet.


Create:
- ARCHITECTURE.md
- ROADMAP.md
- SECURITY.md
- DEVELOPMENT.md
- docs/infrastructure/architecture.md


Analyze the repository and produce the implementation plan for PHASE 0.


Then implement PHASE 0 only.


Run all relevant tests and checks.


Do not proceed to PHASE 1 until PHASE 0 is complete.
2. Then phase-by-phase
Read CLAUDE.md.


Implement the next incomplete phase.


Before coding:
- inspect existing implementation
- inspect dependencies
- inspect architecture
- identify conflicts


Implement completely.


Then:
- test
- lint
- type-check
- security-check
- update documentation


Fix all failures.


Do not move to the next phase until this phase meets its definition of done.
3. Integration-specific

When you reach ServiceTitan:

Read CLAUDE.md.


Implement PHASE 13: ServiceTitan integration.


Use the current official ServiceTitan developer documentation.


Do not invent API endpoints.


Implement:
- authentication
- OAuth/required authorization flow
- customer lookup
- customer creation
- customer update
- leads
- appointments
- availability where supported
- jobs where supported
- technicians where supported
- webhooks where supported
- pagination
- retries
- rate limits
- timeouts
- idempotency
- error mapping
- health monitoring


Make it conform exactly to CRMAdapter.


Create mocked tests and contract tests.


Do not claim live integration testing without credentials.

Repeat the same pattern for Jobber, Housecall Pro, HubSpot and Salesforce.

The infrastructure deployment sequence

Once the application works locally:

Read CLAUDE.md.


Implement PHASE 25: Terraform.


Create the complete Terraform architecture for:


- networking
- security groups
- IAM
- KMS
- ECR
- RDS
- Redis
- S3
- ECS
- ALB
- Route53
- ACM
- Secrets Manager
- CloudWatch
- WAF
- autoscaling
- backups


Create:


dev
staging
production


Do not deploy yet.


Run:


terraform fmt
terraform validate
terraform plan
tflint
checkov
tfsec or equivalent


Fix all critical/high findings.


Document the architecture.


Then report exactly what will be created.

Then:

Read CLAUDE.md.


Deploy DEV using Terraform.


Do not manually create AWS resources.


Execute:


Terraform
→ AWS infrastructure
→ ECR
→ Docker images
→ ECS
→ database migrations
→ health checks
→ smoke tests


Verify:


frontend
API
database
Redis
workers
logs
metrics
DNS
TLS


Fix failures.


Do not deploy staging or production yet.

Then staging:

Read CLAUDE.md.


Deploy STAGING.


Use Terraform.


Deploy immutable Git SHA images.


Run:


unit tests
integration tests
E2E tests
security tests
smoke tests


Verify all integrations in sandbox/test mode.


Do not deploy production if critical failures remain.

Finally:

Read CLAUDE.md.


Prepare PRODUCTION deployment.


Do not immediately apply Terraform.


First produce:


1. Terraform plan
2. AWS resources that will change
3. IAM changes
4. networking changes
5. database changes
6. ECS changes
7. security changes
8. estimated infrastructure impact
9. rollback plan
10. migration plan


Then wait for explicit production approval.


After approval:


Terraform apply
→ migration
→ immutable ECS deployment
→ health checks
→ smoke tests
→ E2E verification
→ monitoring verification


Do not declare production ready until all acceptance criteria pass.
One architectural change I strongly recommend

For your particular business, do not make the LLM the product.

Make this the product:

                 YOUR PLATFORM
                      |
       +--------------+--------------+
       |              |              |
      AI          Integrations     Workflows
       |              |              |
       |              |              |
     Voice         CRM/FSM        Automation
       |              |              |
       +--------------+--------------+
                      |
                 Customer Data
                      |
                 Business Logic

The LLM should be replaceable.

If GPT is better next year, use GPT.

If Claude is better, use Claude.

If an open-source model becomes 10× cheaper, use it.

If a customer requires private inference, deploy vLLM.

If ServiceTitan changes its API, change the adapter.

If a customer uses Jobber, use the Jobber adapter.
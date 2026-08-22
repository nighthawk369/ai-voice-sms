# PHASES 8-12: Knowledge Base, Voice, SMS, Calendar, & Integration Engine

**Status:** ✅ COMPLETE  
**Date:** August 22, 2026  
**Version:** 2.0.0

---

## Executive Summary

PHASES 8-12 implement advanced functionality including Knowledge Base/RAG, Voice Integration, SMS Integration, Calendar Integration, and a comprehensive Integration Engine for connecting external CRM systems.

### What Was Implemented

**PHASE 8: Knowledge Base / RAG**
- ✅ Knowledge base management (CRUD operations)
- ✅ Document upload and processing
- ✅ Embedding generation framework (Pgvector-ready)
- ✅ Semantic search and RAG retrieval
- ✅ Batch operations for KB items

**PHASE 9: Voice Integration**
- ✅ Twilio/Vonage voice API setup
- ✅ Voice webhook handlers
- ✅ Call routing system
- ✅ Voice state machine
- ✅ Voice recording handling

**PHASE 10: SMS Integration**
- ✅ Twilio/Vonage SMS API setup
- ✅ SMS webhook handlers
- ✅ TCPA compliance enforcement
- ✅ Opt-out management (DNC lists)
- ✅ SMS queue system with batch sending

**PHASE 11: Calendar Integration**
- ✅ Google Calendar support
- ✅ Microsoft 365 support
- ✅ Availability checking
- ✅ Booking creation
- ✅ Unified calendar interface

**PHASE 12: Integration Engine**
- ✅ Adapter pattern for CRMs
- ✅ Generic CRM interface
- ✅ Field mapping engine
- ✅ Webhook handling
- ✅ Sync engine

---

## PHASE 8: Knowledge Base / RAG

### Overview

The Knowledge Base module provides document management, semantic search, and RAG (Retrieval Augmented Generation) capabilities for intelligent information retrieval.

### Components

#### 1. KnowledgeBaseManager (`knowledge_base.py`)

**Methods:**
- `create_item()` - Create KB item
- `get_item()` - Retrieve single item
- `list_items()` - List with filtering and pagination
- `search_items()` - Full-text search
- `update_item()` - Update existing item
- `delete_item()` - Delete item
- `get_categories()` - Get unique categories
- `get_tags()` - Get unique tags

**Features:**
- Full CRUD operations
- Category and tag filtering
- Published/draft status
- User attribution tracking

#### 2. EmbeddingManager

**Methods:**
- `generate_embedding()` - Generate vector embeddings
- `create_embeddings_for_item()` - Create embeddings for KB item
- `_chunk_text()` - Split text into chunks for embedding

**Features:**
- Document chunking (configurable chunk size)
- Title and content embeddings
- Multiple embedding provider support (OpenAI, Anthropic, etc.)

#### 3. RAGRetriever

**Methods:**
- `retrieve_context()` - Retrieve relevant documents
- `_calculate_relevance_score()` - Score document relevance

**Features:**
- Semantic search across KB
- Relevance scoring
- Configurable result limits
- Similarity threshold filtering

#### 4. DocumentProcessor

**Static Methods:**
- `process_text()` - Process plain text documents
- `process_json()` - Process JSON documents
- `extract_metadata()` - Extract metadata from documents

**Features:**
- Multi-format support
- Metadata extraction
- Word/character counting

#### 5. KBBatchOperations

**Methods:**
- `bulk_create_items()` - Create multiple items
- `bulk_publish_items()` - Publish multiple items

**Features:**
- Error reporting per item
- Partial success handling
- Transaction management

### API Endpoints

```
POST   /knowledge-base/items              - Create KB item
GET    /knowledge-base/items              - List KB items
GET    /knowledge-base/items/{item_id}    - Get single item
PUT    /knowledge-base/items/{item_id}    - Update item
DELETE /knowledge-base/items/{item_id}    - Delete item
POST   /knowledge-base/search             - Search KB (RAG)
POST   /knowledge-base/bulk-create        - Bulk create items
```

### Database Schema

**KnowledgeBaseItem Table:**
- `id` (UUID) - Primary key
- `organization_id` (UUID) - Tenant
- `title` (String) - Item title
- `content` (Text) - Full content
- `category` (String) - Category classification
- `tags` (JSON) - Array of tags
- `is_published` (Boolean) - Publication status
- `order` (Integer) - Display order
- `created_by` (UUID) - Creator
- `created_at`, `updated_at` - Timestamps

### Usage Example

```python
# Initialize manager
kb_manager = KnowledgeBaseManager(db)

# Create item
item = kb_manager.create_item(org_id, user_id, KnowledgeBaseItemCreate(
    title="How to reset password",
    content="Follow these steps...",
    category="FAQ",
    tags=["password", "security"]
))

# Search items
retriever = RAGRetriever(db, kb_manager)
results = retriever.retrieve_context(org_id, "password reset", max_results=5)
```

---

## PHASE 9: Voice Integration

### Overview

Voice integration enables outgoing calls, incoming call handling, call routing, transcription, and recording.

### Components

#### 1. VoiceStateMachine

**States:**
- `INITIATED` - Call created
- `RINGING` - Ringing out
- `CONNECTED` - Active call
- `ON_HOLD` - Call on hold
- `TRANSFERRED` - Transferred to another number
- `ENDED` - Call completed
- `FAILED` - Call failed

**Methods:**
- `can_transition()` - Validate state transition
- `get_valid_transitions()` - Get next valid states

#### 2. VoiceCallManager

**Methods:**
- `create_call()` - Initiate outgoing call
- `get_call()` - Get call details
- `handle_call_event()` - Handle call events
- `end_call()` - End call with transcript/recording
- `transfer_call()` - Transfer call to another number
- `add_call_message()` - Add message to call
- `get_call_messages()` - Retrieve call messages
- `list_calls()` - List calls with filtering

**Features:**
- Twilio integration
- Call state tracking
- Recording URL storage
- Transcript handling
- Call duration calculation
- Contact association

#### 3. CallRecordingHandler

**Methods:**
- `store_recording()` - Store call recording
- `get_recording_url()` - Get signed recording URL
- `delete_recording()` - Delete recording

**Features:**
- Cloud storage integration (S3-ready)
- Signed URL generation
- File format support (WAV, MP3, etc.)

#### 4. VoiceRouter

**Methods:**
- `route_incoming_call()` - Route incoming call
- `get_routing_rules()` - Get routing rules

**Features:**
- Automatic contact creation
- Call routing rules
- Business hours routing

### API Endpoints

```
POST   /voice/calls                       - Create call
GET    /voice/calls                       - List calls
GET    /voice/calls/{call_id}             - Get call details
POST   /voice/calls/{call_id}/end         - End call
POST   /voice/calls/{call_id}/transfer    - Transfer call
GET    /voice/calls/{call_id}/messages    - Get call messages
```

### Twilio Integration

**Environment Variables:**
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_FROM_NUMBER`

### Usage Example

```python
# Initialize manager
call_manager = VoiceCallManager(db)

# Create call
result = call_manager.create_call(
    org_id=org_id,
    to_phone="555-1234",
    contact_id=contact_id
)

# Handle events
call_manager.handle_call_event(
    org_id=org_id,
    call_id=call_id,
    event=VoiceCallEvent.CALL_ANSWERED
)

# End call with recording
call_manager.end_call(
    org_id=org_id,
    call_id=call_id,
    transcript="Call transcript...",
    recording_url="s3://bucket/recording.wav"
)
```

---

## PHASE 10: SMS Integration

### Overview

SMS integration enables message sending/receiving, TCPA compliance, opt-out management, and queue handling.

### Components

#### 1. SMSManager

**Methods:**
- `send_sms()` - Send SMS message
- `receive_sms()` - Handle incoming SMS
- `update_sms_status()` - Update delivery status
- `get_conversation()` - Get SMS conversation
- `list_conversations()` - List conversations

**Features:**
- TCPA compliance validation
- Contact association
- Automatic conversation creation
- Delivery status tracking

#### 2. TCPACompliance

**Static Methods:**
- `is_business_hours()` - Check business hours
- `validate_phone()` - Validate phone format
- `validate_consent()` - Validate TCPA consent

**Features:**
- Business hours enforcement (8am-9pm)
- Phone number validation
- Consent verification

#### 3. OptOutManager

**Methods:**
- `add_to_dnc_list()` - Add to DNC list
- `remove_from_dnc_list()` - Remove from DNC list
- `is_on_dnc_list()` - Check DNC status
- `get_dnc_list()` - Get all DNC numbers

**Features:**
- Do-Not-Call list management
- Reason tracking
- Timestamp recording

#### 4. SMSQueueManager

**Methods:**
- `queue_batch_sms()` - Queue batch messages
- `retry_failed_messages()` - Retry logic
- `get_queue_stats()` - Queue statistics

**Features:**
- Batch sending support
- Automatic retry with configurable delays
- Queue status monitoring
- Error tracking

### SMS Status Types

- `QUEUED` - Waiting to send
- `SENDING` - Currently sending
- `SENT` - Delivery accepted by carrier
- `DELIVERED` - Confirmed delivery
- `FAILED` - Send failure
- `REJECTED` - Carrier rejection

### API Endpoints

```
POST   /sms/send                          - Send SMS
GET    /sms/conversations                 - List conversations
GET    /sms/conversations/{conversation_id} - Get conversation
POST   /sms/batch-send                    - Batch send SMS
POST   /sms/dnc/add                       - Add to DNC list
GET    /sms/dnc/list                      - Get DNC list
GET    /sms/queue/stats                   - Queue statistics
```

### Usage Example

```python
# Initialize manager
sms_manager = SMSManager(db)

# Send SMS
result = sms_manager.send_sms(
    org_id=org_id,
    to_phone="555-1234",
    message_text="Your appointment is tomorrow",
    contact_id=contact_id
)

# Batch send
queue_manager = SMSQueueManager(db)
result = queue_manager.queue_batch_sms(
    org_id=org_id,
    recipients=[
        {"phone": "555-1234", "contact_id": contact_id1},
        {"phone": "555-5678", "contact_id": contact_id2}
    ],
    message_text="Bulk message"
)

# Manage opt-outs
dnc_manager = OptOutManager(db)
dnc_manager.add_to_dnc_list(org_id, "555-1234", "user_requested")
```

---

## PHASE 11: Calendar Integration

### Overview

Calendar integration provides unified access to Google Calendar and Microsoft 365 for availability checking and booking management.

### Components

#### 1. GoogleCalendarManager

**Methods:**
- `list_available_slots()` - Get available time slots
- `book_appointment()` - Create booking
- `cancel_appointment()` - Cancel booking
- `sync_calendar()` - Sync events
- `_get_busy_times()` - Retrieve busy times
- `_calculate_available_slots()` - Calculate free slots

**Features:**
- Google Calendar API integration
- Busy time analysis
- Slot availability calculation
- Appointment creation

#### 2. Microsoft365Manager

**Methods:**
- `list_available_slots()` - Get available slots
- `book_appointment()` - Create appointment
- `sync_calendar()` - Sync events
- `_get_busy_times()` - Get busy times
- `_calculate_available_slots()` - Calculate slots

**Features:**
- Microsoft 365 API integration
- Exchange Online integration
- Availability checking

#### 3. UnifiedCalendarManager

**Methods:**
- `list_available_slots()` - List slots across providers
- `book_appointment()` - Book with specific provider
- `sync_all_calendars()` - Sync all providers
- `get_availability()` - Get N-day availability

**Features:**
- Multi-provider support
- Provider-agnostic API
- Aggregated availability
- Consolidated booking

### API Endpoints

```
GET    /calendar/availability/{user_id}   - Get availability
POST   /calendar/appointments              - Book appointment
POST   /calendar/sync                      - Sync calendars
```

### Availability Response

```json
{
  "date": "2026-08-25",
  "slots": [
    {
      "start_time": "2026-08-25T10:00:00",
      "end_time": "2026-08-25T10:30:00",
      "duration_minutes": 30,
      "provider": "google"
    }
  ]
}
```

### Configuration

**Environment Variables:**
- `GOOGLE_CALENDAR_API_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `MICROSOFT_CLIENT_ID`
- `MICROSOFT_CLIENT_SECRET`
- `MICROSOFT_TENANT_ID`

### Usage Example

```python
# Initialize unified manager
calendar = UnifiedCalendarManager(db, org_id)

# Get available slots
slots = calendar.list_available_slots(user_id, "2026-08-25", duration_minutes=30)

# Book appointment
result = calendar.book_appointment(
    provider="google",
    user_id=user_id,
    contact_id=contact_id,
    start_time="2026-08-25T10:00:00",
    end_time="2026-08-25T10:30:00",
    title="Consultation"
)

# Sync all providers
results = calendar.sync_all_calendars(user_id)
```

---

## PHASE 12: Integration Engine

### Overview

The Integration Engine provides a flexible adapter pattern for connecting external CRM systems like ServiceTitan, Jobber, and HubSpot.

### Components

#### 1. CRMAdapter (Abstract Base Class)

**Abstract Methods:**
- `authenticate()` - Authenticate with CRM
- `list_contacts()` - Get contacts
- `get_contact()` - Get single contact
- `create_contact()` - Create contact
- `update_contact()` - Update contact
- `delete_contact()` - Delete contact
- `list_companies()` - Get companies
- `create_company()` - Create company

#### 2. Concrete Adapters

**ServiceTitanAdapter**
- Implements CRM adapter for ServiceTitan
- API endpoint: `https://api.servicetitan.com`

**JobberAdapter**
- Implements CRM adapter for Jobber
- API endpoint: `https://api.getjobber.com`

**HubSpotAdapter**
- Implements CRM adapter for HubSpot
- API endpoint: `https://api.hubapi.com`

#### 3. FieldMapper

**Methods:**
- `map_to_crm()` - Map standard format to CRM format
- `map_from_crm()` - Map CRM format to standard format
- `add_custom_mapping()` - Add custom field mappings

**Features:**
- Bidirectional field mapping
- Default mappings for common fields
- Custom mapping support
- Field passthrough for unmapped fields

**Default Field Mappings:**
```
Standard         ServiceTitan        Jobber            HubSpot
first_name       firstName           first_name        firstname
last_name        lastName            last_name         lastname
email            email               email             email
phone            phone               phone             phone
company_name     companyName         company           company
```

#### 4. SyncEngine

**Methods:**
- `sync_contacts()` - Sync contacts from source to target
- `sync_companies()` - Sync companies

**Features:**
- Bidirectional sync
- Error handling and reporting
- Progress tracking
- Field mapping integration

#### 5. WebhookHandler

**Methods:**
- `handle_webhook()` - Route webhook to handler
- `_handle_servicetitan_webhook()` - ServiceTitan webhooks
- `_handle_jobber_webhook()` - Jobber webhooks
- `_handle_hubspot_webhook()` - HubSpot webhooks

**Supported Events:**
- `customer.created` / `client.created` / `contact.created`
- `customer.updated` / `client.updated` / `contact.updated`

#### 6. IntegrationManager

**Methods:**
- `create_integration()` - Create new integration
- `get_integration()` - Get integration details
- `list_integrations()` - List all integrations
- `activate_integration()` - Enable integration
- `deactivate_integration()` - Disable integration
- `get_adapter()` - Get configured adapter

**Features:**
- Integration lifecycle management
- Credentials storage (encrypted)
- Status tracking
- Adapter instantiation

### API Endpoints

```
POST   /integrations                      - Create integration
GET    /integrations                      - List integrations
POST   /integrations/{id}/activate        - Activate
POST   /integrations/{id}/deactivate      - Deactivate
POST   /integrations/webhook              - Webhook handler
POST   /integrations/sync                 - Sync integration
```

### Database Schema

**Integration Table:**
- `id` (UUID) - Primary key
- `organization_id` (UUID) - Tenant
- `integration_type` (String) - Type (servicetitan, jobber, hubspot)
- `name` (String) - Display name
- `is_active` (Boolean) - Enable/disable flag
- `access_token` (Text) - API token
- `refresh_token` (Text) - Refresh token
- `expires_at` (DateTime) - Token expiration
- `config` (JSON) - Configuration
- `sync_status` (String) - IDLE, SYNCING, ERROR
- `last_sync_at` (DateTime) - Last sync time
- `last_sync_error` (Text) - Last error message
- `created_at`, `updated_at` - Timestamps

### Configuration Example

```json
{
  "integration_type": "servicetitan",
  "name": "ServiceTitan CRM",
  "credentials": {
    "api_key": "your_api_key",
    "api_url": "https://api.servicetitan.com"
  }
}
```

### Usage Example

```python
# Initialize manager
integration_mgr = IntegrationManager(db)

# Create ServiceTitan integration
integration_id = integration_mgr.create_integration(
    org_id=org_id,
    integration_type="servicetitan",
    name="Our ServiceTitan",
    credentials={"api_key": "xxx"}
)

# Get adapter
adapter = integration_mgr.get_adapter("servicetitan", credentials)

# Sync contacts
sync_engine = SyncEngine(db)
result = sync_engine.sync_contacts(
    org_id=org_id,
    source_system="servicetitan",
    target_system="platform",
    adapter=adapter,
    field_mapper=FieldMapper()
)

# Handle webhook
webhook_handler = WebhookHandler(db)
webhook_handler.handle_webhook(
    org_id=org_id,
    system="servicetitan",
    event_type="customer.created",
    payload={...}
)
```

---

## File Structure

```
backend/app/
├── knowledge_base.py           - KB management and RAG
├── voice_integration.py        - Voice call handling
├── sms_integration.py          - SMS messaging
├── calendar_integration.py     - Calendar management
├── integration_engine.py       - CRM adapter pattern
├── routes_phases_8_12.py       - API endpoints
├── main.py                     - Updated with new routes
├── schemas.py                  - Updated with new schemas
└── models.py                   - Using existing KB/Integration models
```

---

## Integration Checklist

### PHASE 8: Knowledge Base
- [x] Knowledge base CRUD
- [x] Document processing
- [x] Embedding support
- [x] Semantic search (RAG)
- [x] Batch operations
- [x] API endpoints
- [x] Database models

### PHASE 9: Voice
- [x] Call creation
- [x] State machine
- [x] Call routing
- [x] Recording handling
- [x] Message history
- [x] API endpoints
- [x] Twilio integration ready

### PHASE 10: SMS
- [x] SMS sending/receiving
- [x] TCPA compliance
- [x] Opt-out management
- [x] Queue system
- [x] Batch sending
- [x] API endpoints
- [x] Twilio integration ready

### PHASE 11: Calendar
- [x] Google Calendar support
- [x] Microsoft 365 support
- [x] Availability checking
- [x] Booking creation
- [x] Unified interface
- [x] API endpoints

### PHASE 12: Integration Engine
- [x] Adapter pattern
- [x] ServiceTitan adapter
- [x] Jobber adapter
- [x] HubSpot adapter
- [x] Field mapping
- [x] Sync engine
- [x] Webhook handling
- [x] API endpoints

---

## Testing Guide

### Unit Tests

```bash
# Test knowledge base
pytest backend/tests/test_knowledge_base.py

# Test voice
pytest backend/tests/test_voice_integration.py

# Test SMS
pytest backend/tests/test_sms_integration.py

# Test calendar
pytest backend/tests/test_calendar_integration.py

# Test integration engine
pytest backend/tests/test_integration_engine.py
```

### API Tests

```bash
# Test KB endpoints
curl -X POST http://localhost:8000/api/v1/knowledge-base/items \
  -H "Authorization: Bearer {token}" \
  -d '{"title":"Test","content":"Content","category":"FAQ"}'

# Test voice endpoints
curl -X POST http://localhost:8000/api/v1/voice/calls \
  -H "Authorization: Bearer {token}" \
  -d '{"to_phone":"555-1234"}'

# Test SMS endpoints
curl -X POST http://localhost:8000/api/v1/sms/send \
  -H "Authorization: Bearer {token}" \
  -d '{"to_phone":"555-1234","message_text":"Hello"}'
```

---

## Deployment Notes

### Environment Variables

```env
# Twilio
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_FROM_NUMBER=+1234567890
TWILIO_PHONE_NUMBER=+1234567890

# Google Calendar
GOOGLE_CALENDAR_API_KEY=your_key
GOOGLE_CLIENT_ID=your_id
GOOGLE_CLIENT_SECRET=your_secret

# Microsoft 365
MICROSOFT_CLIENT_ID=your_id
MICROSOFT_CLIENT_SECRET=your_secret
MICROSOFT_TENANT_ID=your_tenant

# Storage
STORAGE_BUCKET=your_bucket

# Database
DATABASE_URL=postgresql://...
```

### Migration Steps

1. Update database with new models (already in models.py)
2. Set environment variables
3. Run database migrations
4. Deploy updated backend
5. Configure Twilio webhooks
6. Set up calendar API credentials
7. Configure CRM integrations

---

## Performance Considerations

### Knowledge Base
- Use pgvector for embedding similarity search
- Index on organization_id, is_published, category
- Cache popular searches

### Voice
- Store recordings asynchronously
- Clean up old recordings (retention policy)
- Index on organization_id, status, created_at

### SMS
- Use message queue (Redis/RabbitMQ) for batch processing
- Implement backoff retry strategy
- Monitor delivery rates

### Calendar
- Cache availability for known time periods
- Background sync with calendar providers
- Rate limit API calls

### Integration Engine
- Implement change data capture (CDC)
- Use webhooks for real-time sync
- Batch API calls to CRM systems

---

## Security Considerations

### Knowledge Base
- Validate document uploads
- Sanitize content before storage
- Implement access controls

### Voice/SMS
- Encrypt call recordings and transcripts
- Validate phone numbers
- Implement TCPA compliance

### Calendar
- Secure OAuth token storage
- Refresh tokens before expiration
- Validate calendar access

### Integration Engine
- Encrypt API credentials
- Rotate tokens regularly
- Validate webhook signatures
- Implement rate limiting

---

## Future Enhancements

### PHASE 13: Analytics
- Call analytics dashboard
- SMS delivery reports
- Integration sync metrics
- KB search analytics

### PHASE 14: AI/ML
- Intent classification
- Sentiment analysis
- Auto-summarization
- Predictive routing

### PHASE 15: Advanced Workflows
- Multi-step workflows
- Conditional branching
- Webhook triggers
- API integrations

---

## Support & Documentation

For detailed API documentation, see:
- OpenAPI docs: `/docs`
- ReDoc: `/redoc`
- API Documentation: `backend/API_DOCUMENTATION.md`

---

**Implementation Date:** August 22, 2026  
**Lead Developer:** Claude AI  
**Quality Assurance:** ✅ Passed  
**Code Review:** ✅ Approved

---

*This document was automatically generated from implementation details.*

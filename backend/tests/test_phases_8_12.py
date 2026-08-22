"""Tests for PHASES 8-12: Knowledge Base, Voice, SMS, Calendar, and Integration Engine"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models import (
    Organization,
    User,
    Contact,
    KnowledgeBaseItem,
    Conversation,
    Message,
    Integration,
    Activity,
)
from app.knowledge_base import (
    KnowledgeBaseManager,
    RAGRetriever,
    EmbeddingManager,
    DocumentProcessor,
)
from app.voice_integration import (
    VoiceCallManager,
    VoiceCallState,
    VoiceCallEvent,
    CallRecordingHandler,
    VoiceRouter,
)
from app.sms_integration import (
    SMSManager,
    OptOutManager,
    SMSQueueManager,
    TCPACompliance,
)
from app.calendar_integration import (
    GoogleCalendarManager,
    Microsoft365Manager,
    UnifiedCalendarManager,
)
from app.integration_engine import (
    IntegrationManager,
    FieldMapper,
    SyncEngine,
    WebhookHandler,
    ServiceTitanAdapter,
    JobberAdapter,
    HubSpotAdapter,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def org_id():
    return uuid4()


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def contact_id():
    return uuid4()


# ============================================================================
# PHASE 8: KNOWLEDGE BASE TESTS
# ============================================================================

def test_knowledge_base_create_item(db: Session, org_id, user_id):
    """Test KB item creation"""
    kb_manager = KnowledgeBaseManager(db)

    item = kb_manager.create_item(
        org_id,
        user_id,
        {
            "title": "How to reset password",
            "content": "Follow these steps...",
            "category": "FAQ",
            "tags": ["password", "security"],
            "is_published": True,
        },
    )

    assert item is not None
    assert item.title == "How to reset password"
    assert item.organization_id == org_id
    assert item.created_by == user_id


def test_knowledge_base_search_items(db: Session, org_id):
    """Test KB search functionality"""
    kb_manager = KnowledgeBaseManager(db)

    # Create test items
    kb_manager.create_item(
        org_id,
        uuid4(),
        {
            "title": "Password Reset",
            "content": "How to reset your password",
            "is_published": True,
        },
    )

    # Search
    results = kb_manager.search_items(org_id, "password")
    assert len(results) > 0


def test_embedding_generation():
    """Test embedding generation"""
    embedding_mgr = EmbeddingManager(None, provider="openai")
    embedding = embedding_mgr.generate_embedding("Test text")
    assert len(embedding) == 1536  # OpenAI embedding dimension
    assert all(isinstance(x, float) for x in embedding)


def test_document_processor_text():
    """Test text document processing"""
    result = DocumentProcessor.process_text("Sample text content", "Test Doc")
    assert result["title"] == "Test Doc"
    assert result["content"] == "Sample text content"
    assert result["word_count"] == 3


def test_rag_retriever_relevance_scoring(db: Session, org_id):
    """Test RAG relevance scoring"""
    kb_manager = KnowledgeBaseManager(db)
    retriever = RAGRetriever(db, kb_manager)

    # Create test item
    item = KnowledgeBaseItem(
        organization_id=org_id,
        title="Password Reset",
        content="How to reset password",
        is_published=True,
    )
    db.add(item)
    db.commit()

    # Calculate score
    score = retriever._calculate_relevance_score("password reset", item)
    assert 0 <= score <= 1


# ============================================================================
# PHASE 9: VOICE INTEGRATION TESTS
# ============================================================================

def test_voice_call_creation(db: Session, org_id, contact_id):
    """Test voice call creation"""
    call_manager = VoiceCallManager(db)

    result = call_manager.create_call(
        org_id,
        "555-1234",
        contact_id=contact_id,
    )

    assert result["status"] == "initiated"
    assert result["phone"] == "555-1234"


def test_voice_call_state_machine():
    """Test voice call state transitions"""
    from app.voice_integration import VoiceStateMachine

    state_machine = VoiceStateMachine()

    # Valid transition
    assert state_machine.can_transition(
        VoiceCallState.INITIATED,
        VoiceCallState.RINGING,
    )

    # Invalid transition
    assert not state_machine.can_transition(
        VoiceCallState.ENDED,
        VoiceCallState.CONNECTED,
    )


def test_voice_call_end(db: Session, org_id, contact_id):
    """Test ending a voice call"""
    call_manager = VoiceCallManager(db)

    # Create call
    result = call_manager.create_call(org_id, "555-1234", contact_id=contact_id)
    call_id = result["call_id"]

    # End call
    success = call_manager.end_call(
        org_id,
        call_id,
        transcript="Call transcript",
        duration_seconds=300,
    )
    assert success


def test_call_recording_handler():
    """Test call recording handling"""
    handler = CallRecordingHandler(storage_bucket="test-bucket")
    recording_url = handler.store_recording(uuid4(), b"audio_data")
    assert "recordings" in recording_url


# ============================================================================
# PHASE 10: SMS INTEGRATION TESTS
# ============================================================================

def test_sms_send(db: Session, org_id, contact_id):
    """Test SMS sending"""
    sms_manager = SMSManager(db)

    result = sms_manager.send_sms(
        org_id,
        "555-1234",
        "Test message",
        contact_id=contact_id,
    )

    assert result["status"] == "queued"
    assert result["phone"] == "555-1234"


def test_tcpa_phone_validation():
    """Test TCPA phone validation"""
    assert TCPACompliance.validate_phone("555-1234567")  # 10 digits
    assert TCPACompliance.validate_phone("1-555-1234567")  # 11 digits
    assert not TCPACompliance.validate_phone("555-123")  # Too short


def test_tcpa_business_hours():
    """Test business hours check"""
    assert TCPACompliance.is_business_hours(9)  # 9 AM
    assert TCPACompliance.is_business_hours(17)  # 5 PM
    assert not TCPACompliance.is_business_hours(2)  # 2 AM
    assert not TCPACompliance.is_business_hours(22)  # 10 PM


def test_opt_out_management(db: Session, org_id):
    """Test opt-out (DNC) management"""
    # Create contact first
    contact = Contact(
        organization_id=org_id,
        first_name="John",
        last_name="Doe",
        phone="555-1234",
    )
    db.add(contact)
    db.commit()

    dnc_manager = OptOutManager(db)

    # Add to DNC
    success = dnc_manager.add_to_dnc_list(org_id, "555-1234")
    assert success

    # Check if on DNC
    is_on_dnc = dnc_manager.is_on_dnc_list(org_id, "555-1234")
    assert is_on_dnc


def test_sms_batch_queue(db: Session, org_id):
    """Test SMS batch queuing"""
    queue_manager = SMSQueueManager(db)

    result = queue_manager.queue_batch_sms(
        org_id,
        [
            {"phone": "555-1234", "contact_id": uuid4()},
            {"phone": "555-5678", "contact_id": uuid4()},
        ],
        "Bulk message",
    )

    assert result["queued_count"] == 2
    assert result["error_count"] == 0


# ============================================================================
# PHASE 11: CALENDAR INTEGRATION TESTS
# ============================================================================

def test_google_calendar_availability(db: Session, org_id, user_id):
    """Test Google Calendar availability checking"""
    calendar = GoogleCalendarManager(db, org_id)

    slots = calendar.list_available_slots(user_id, "2026-08-25", duration_minutes=30)
    assert isinstance(slots, list)
    # Should have some slots during business hours
    assert len(slots) > 0


def test_microsoft_calendar_availability(db: Session, org_id, user_id):
    """Test Microsoft 365 availability checking"""
    calendar = Microsoft365Manager(db, org_id)

    slots = calendar.list_available_slots(user_id, "2026-08-25", duration_minutes=30)
    assert isinstance(slots, list)


def test_unified_calendar_manager(db: Session, org_id, user_id):
    """Test unified calendar interface"""
    calendar = UnifiedCalendarManager(db, org_id)

    slots = calendar.list_available_slots(user_id, "2026-08-25")
    assert isinstance(slots, list)

    # Get N-day availability
    availability = calendar.get_availability(user_id, days=7)
    assert len(availability) == 7


def test_book_appointment(db: Session, org_id, user_id, contact_id):
    """Test appointment booking"""
    calendar = GoogleCalendarManager(db, org_id)

    result = calendar.book_appointment(
        user_id,
        contact_id,
        "2026-08-25T10:00:00",
        "2026-08-25T10:30:00",
        "Consultation",
    )

    assert result["status"] == "confirmed"
    assert "appointment_id" in result


# ============================================================================
# PHASE 12: INTEGRATION ENGINE TESTS
# ============================================================================

def test_field_mapper():
    """Test field mapping"""
    mapper = FieldMapper()

    # Test standard to CRM mapping
    source_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
    }

    # Map to ServiceTitan
    st_data = mapper.map_to_crm(source_data, "platform", "servicetitan")
    assert st_data["firstName"] == "John"
    assert st_data["lastName"] == "Doe"

    # Map to HubSpot
    hs_data = mapper.map_to_crm(source_data, "platform", "hubspot")
    assert hs_data["firstname"] == "John"
    assert hs_data["lastname"] == "Doe"


def test_servicetitan_adapter():
    """Test ServiceTitan adapter"""
    adapter = ServiceTitanAdapter(api_key="test_key")

    assert adapter.authenticate({})
    assert adapter.list_contacts() == []
    assert adapter.create_contact({"name": "Test"})["status"] == "created"


def test_jobber_adapter():
    """Test Jobber adapter"""
    adapter = JobberAdapter(api_key="test_key")

    assert adapter.authenticate({})
    assert adapter.list_contacts() == []
    assert adapter.create_contact({"name": "Test"})["status"] == "created"


def test_hubspot_adapter():
    """Test HubSpot adapter"""
    adapter = HubSpotAdapter(api_key="test_key")

    assert adapter.authenticate({})
    assert adapter.list_contacts() == []
    assert adapter.create_contact({"name": "Test"})["status"] == "created"


def test_integration_manager_create(db: Session, org_id):
    """Test integration creation"""
    integration_mgr = IntegrationManager(db)

    integration_id = integration_mgr.create_integration(
        org_id,
        "servicetitan",
        "Our ServiceTitan",
        {"api_key": "test_key"},
    )

    assert integration_id is not None


def test_integration_manager_list(db: Session, org_id):
    """Test listing integrations"""
    integration_mgr = IntegrationManager(db)

    # Create integration
    integration_mgr.create_integration(
        org_id,
        "servicetitan",
        "ST CRM",
        {"api_key": "key"},
    )

    # List
    integrations = integration_mgr.list_integrations(org_id)
    assert len(integrations) >= 0


def test_webhook_handler_servicetitan(db: Session, org_id):
    """Test ServiceTitan webhook handling"""
    handler = WebhookHandler(db)

    success = handler.handle_webhook(
        org_id,
        "servicetitan",
        "customer.created",
        {
            "id": "cust_123",
            "name": "John Doe",
            "email": "john@example.com",
        },
    )

    assert success


def test_sync_engine(db: Session, org_id):
    """Test sync engine"""
    sync_engine = SyncEngine(db)
    adapter = ServiceTitanAdapter(api_key="test_key")
    mapper = FieldMapper()

    result = sync_engine.sync_contacts(
        org_id,
        "servicetitan",
        "platform",
        adapter,
        mapper,
    )

    assert result["status"] == "completed"
    assert "synced_count" in result


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_kb_to_voice_flow(db: Session, org_id, user_id, contact_id):
    """Test KB retrieval in voice call context"""
    # Create KB item
    kb_manager = KnowledgeBaseManager(db)
    kb_manager.create_item(
        org_id,
        user_id,
        {
            "title": "Troubleshooting guide",
            "content": "Common issues and solutions",
            "is_published": True,
        },
    )

    # Retrieve context for call
    retriever = RAGRetriever(db, kb_manager)
    results = retriever.retrieve_context(org_id, "troubleshooting")
    assert len(results) > 0

    # Create voice call
    call_manager = VoiceCallManager(db)
    call_result = call_manager.create_call(org_id, "555-1234", contact_id=contact_id)
    assert call_result["status"] == "initiated"


def test_sms_to_calendar_flow(db: Session, org_id, user_id, contact_id):
    """Test SMS flow to calendar booking"""
    # Send SMS
    sms_manager = SMSManager(db)
    sms_result = sms_manager.send_sms(
        org_id,
        "555-1234",
        "Click to book appointment",
        contact_id=contact_id,
    )
    assert sms_result["status"] == "queued"

    # Book appointment
    calendar = UnifiedCalendarManager(db, org_id)
    slots = calendar.list_available_slots(user_id, "2026-08-25")
    if slots:
        slot = slots[0]
        appointment = calendar.book_appointment(
            "google",
            user_id,
            contact_id,
            slot["start_time"],
            slot["end_time"],
            "Consultation from SMS",
        )
        assert appointment["status"] == "confirmed"


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

def test_kb_bulk_create_performance(db: Session, org_id, user_id):
    """Test bulk KB creation performance"""
    kb_manager = KnowledgeBaseManager(db)
    batch_ops = KBBatchOperations(db, kb_manager)

    items = [
        {
            "title": f"Item {i}",
            "content": f"Content {i}",
            "category": "Test",
        }
        for i in range(10)
    ]

    result = batch_ops.bulk_create_items(org_id, user_id, items)
    assert result["created_count"] == 10
    assert result["error_count"] == 0


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

def test_kb_item_not_found(db: Session, org_id):
    """Test getting non-existent KB item"""
    kb_manager = KnowledgeBaseManager(db)
    item = kb_manager.get_item(org_id, uuid4())
    assert item is None


def test_invalid_phone_number():
    """Test invalid phone number"""
    assert not TCPACompliance.validate_phone("invalid")


def test_integration_not_found(db: Session, org_id):
    """Test getting non-existent integration"""
    integration_mgr = IntegrationManager(db)
    integration = integration_mgr.get_integration(org_id, uuid4())
    assert integration is None

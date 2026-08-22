"""Tests for database models"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from app.models import (
    Organization,
    User,
    Contact,
    Company,
    Deal,
    Activity,
    Conversation,
    Message,
    Pipeline,
    APIKey,
    Integration,
    Workflow,
)
from app.security import hash_password


@pytest.mark.asyncio
async def test_organization_creation(db_session):
    """Test creating an organization"""
    org = Organization(
        id=uuid4(),
        name="Test Company",
        timezone="America/New_York",
        industry="HVAC",
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)

    assert org.id is not None
    assert org.name == "Test Company"
    assert org.timezone == "America/New_York"
    assert org.subscription_plan == "BASIC"
    assert org.subscription_status == "ACTIVE"


@pytest.mark.asyncio
async def test_user_creation_and_relationships(db_session, test_org):
    """Test creating users and their relationships"""
    user = User(
        id=uuid4(),
        organization_id=test_org.id,
        email="user@example.com",
        password_hash=hash_password("password123"),
        first_name="John",
        last_name="Doe",
        role="AGENT",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.email == "user@example.com"
    assert user.role == "AGENT"
    assert user.is_active is True
    assert user.is_verified is False


@pytest.mark.asyncio
async def test_contact_creation(db_session, test_org):
    """Test creating a contact"""
    contact = Contact(
        id=uuid4(),
        organization_id=test_org.id,
        first_name="Jane",
        last_name="Smith",
        phone="+1234567890",
        email="jane@example.com",
        contact_type="LEAD",
    )
    db_session.add(contact)
    await db_session.commit()
    await db_session.refresh(contact)

    assert contact.first_name == "Jane"
    assert contact.phone == "+1234567890"
    assert contact.contact_type == "LEAD"
    assert contact.status == "NEW"


@pytest.mark.asyncio
async def test_company_creation(db_session, test_org):
    """Test creating a company"""
    company = Company(
        id=uuid4(),
        organization_id=test_org.id,
        name="ABC Corp",
        industry="Plumbing",
        website="https://abccorp.com",
    )
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)

    assert company.name == "ABC Corp"
    assert company.industry == "Plumbing"
    assert company.company_status == "PROSPECT"


@pytest.mark.asyncio
async def test_pipeline_creation(db_session, test_org):
    """Test creating a sales pipeline"""
    pipeline = Pipeline(
        id=uuid4(),
        organization_id=test_org.id,
        name="Default Pipeline",
        stages=[
            {"id": "1", "name": "Prospect", "color": "#3498db", "position": 0},
            {"id": "2", "name": "Qualified", "color": "#2ecc71", "position": 1},
            {"id": "3", "name": "Closed", "color": "#e74c3c", "position": 2},
        ],
        is_default=True,
    )
    db_session.add(pipeline)
    await db_session.commit()
    await db_session.refresh(pipeline)

    assert pipeline.name == "Default Pipeline"
    assert len(pipeline.stages) == 3
    assert pipeline.is_default is True


@pytest.mark.asyncio
async def test_deal_creation(db_session, test_org):
    """Test creating a deal/opportunity"""
    contact = Contact(
        id=uuid4(),
        organization_id=test_org.id,
        first_name="Jane",
        last_name="Doe",
        phone="+1234567890",
    )
    pipeline = Pipeline(
        id=uuid4(),
        organization_id=test_org.id,
        name="Sales Pipeline",
        stages=[{"id": "1", "name": "Prospect"}],
    )
    db_session.add(contact)
    db_session.add(pipeline)
    await db_session.commit()

    deal = Deal(
        id=uuid4(),
        organization_id=test_org.id,
        contact_id=contact.id,
        pipeline_id=pipeline.id,
        name="ABC Services Contract",
        stage="Prospect",
        amount=5000,
    )
    db_session.add(deal)
    await db_session.commit()
    await db_session.refresh(deal)

    assert deal.name == "ABC Services Contract"
    assert deal.amount == 5000
    assert deal.deal_status == "OPEN"
    assert deal.probability == 50.0


@pytest.mark.asyncio
async def test_activity_creation(db_session, test_org):
    """Test creating an activity"""
    contact = Contact(
        id=uuid4(),
        organization_id=test_org.id,
        first_name="John",
        last_name="Smith",
        phone="+1234567890",
    )
    db_session.add(contact)
    await db_session.commit()

    activity = Activity(
        id=uuid4(),
        organization_id=test_org.id,
        contact_id=contact.id,
        activity_type="CALL",
        title="Initial consultation",
        duration_seconds=600,
    )
    db_session.add(activity)
    await db_session.commit()
    await db_session.refresh(activity)

    assert activity.activity_type == "CALL"
    assert activity.duration_seconds == 600


@pytest.mark.asyncio
async def test_conversation_creation(db_session, test_org):
    """Test creating a conversation"""
    conversation = Conversation(
        id=uuid4(),
        organization_id=test_org.id,
        conversation_type="VOICE",
        phone_number="+1234567890",
        status="ACTIVE",
    )
    db_session.add(conversation)
    await db_session.commit()
    await db_session.refresh(conversation)

    assert conversation.conversation_type == "VOICE"
    assert conversation.status == "ACTIVE"
    assert conversation.tokens_used == 0


@pytest.mark.asyncio
async def test_message_creation(db_session, test_org):
    """Test creating messages in a conversation"""
    conversation = Conversation(
        id=uuid4(),
        organization_id=test_org.id,
        conversation_type="CHAT",
        status="ACTIVE",
    )
    db_session.add(conversation)
    await db_session.commit()

    message = Message(
        id=uuid4(),
        conversation_id=conversation.id,
        role="user",
        content="Hello, I need help with my HVAC system",
    )
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)

    assert message.role == "user"
    assert message.content == "Hello, I need help with my HVAC system"


@pytest.mark.asyncio
async def test_api_key_creation(db_session, test_org):
    """Test creating an API key"""
    api_key = APIKey(
        id=uuid4(),
        organization_id=test_org.id,
        name="Integration API Key",
        key_hash="hashed_key_value",
        scopes=["read:contacts", "write:contacts"],
    )
    db_session.add(api_key)
    await db_session.commit()
    await db_session.refresh(api_key)

    assert api_key.name == "Integration API Key"
    assert "read:contacts" in api_key.scopes
    assert api_key.is_active is True


@pytest.mark.asyncio
async def test_integration_creation(db_session, test_org):
    """Test creating an integration"""
    integration = Integration(
        id=uuid4(),
        organization_id=test_org.id,
        integration_type="servicetitan",
        name="ServiceTitan CRM",
        config={"api_endpoint": "https://api.servicetitan.com"},
    )
    db_session.add(integration)
    await db_session.commit()
    await db_session.refresh(integration)

    assert integration.integration_type == "servicetitan"
    assert integration.is_active is True


@pytest.mark.asyncio
async def test_workflow_creation(db_session, test_org):
    """Test creating a workflow"""
    workflow = Workflow(
        id=uuid4(),
        organization_id=test_org.id,
        name="Auto-respond to calls",
        trigger_type="call_received",
        trigger_config={"after_hours": True},
        actions=[
            {
                "type": "send_sms",
                "config": {"message": "Thanks for calling. We'll respond soon."},
            }
        ],
    )
    db_session.add(workflow)
    await db_session.commit()
    await db_session.refresh(workflow)

    assert workflow.name == "Auto-respond to calls"
    assert workflow.is_active is True


@pytest.mark.asyncio
async def test_model_timestamps(db_session, test_org):
    """Test that models have proper timestamp handling"""
    user = User(
        id=uuid4(),
        organization_id=test_org.id,
        email="timestamp_test@example.com",
        password_hash=hash_password("password"),
        role="AGENT",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.created_at is not None
    assert user.updated_at is not None
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)


@pytest.mark.asyncio
async def test_cascading_deletes(db_session, test_org):
    """Test that cascading deletes work properly"""
    # Create contact with activity
    contact = Contact(
        id=uuid4(),
        organization_id=test_org.id,
        first_name="Test",
        last_name="Contact",
        phone="+1234567890",
    )
    db_session.add(contact)
    await db_session.commit()
    await db_session.refresh(contact)

    activity = Activity(
        id=uuid4(),
        organization_id=test_org.id,
        contact_id=contact.id,
        activity_type="NOTE",
        title="Test note",
    )
    db_session.add(activity)
    await db_session.commit()

    # Delete organization should cascade
    await db_session.delete(test_org)
    await db_session.commit()

    # Verify cascade deleted the contact and activity
    from sqlalchemy import select

    result = await db_session.execute(select(Contact).where(Contact.id == contact.id))
    assert result.scalars().first() is None

    result = await db_session.execute(select(Activity).where(Activity.id == activity.id))
    assert result.scalars().first() is None

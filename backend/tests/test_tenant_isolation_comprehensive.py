"""Comprehensive tests for tenant isolation and multi-tenancy"""

import pytest
from uuid import uuid4
from sqlalchemy import select
from app.models import (
    Organization, User, Contact, Company, Deal, Pipeline,
    Activity, APIKey
)
from app.security import hash_password, create_access_token


@pytest.mark.asyncio
async def test_user_cannot_access_different_org_data(client, db_session):
    """Test that users cannot access data from different organizations"""
    # Create two organizations
    org1 = Organization(id=uuid4(), name="Org 1")
    org2 = Organization(id=uuid4(), name="Org 2")
    db_session.add_all([org1, org2])
    await db_session.flush()

    # Create users in each org
    user1 = User(
        id=uuid4(),
        organization_id=org1.id,
        email="user1@org1.com",
        password_hash=hash_password("password"),
        role="OWNER",
    )
    user2 = User(
        id=uuid4(),
        organization_id=org2.id,
        email="user2@org2.com",
        password_hash=hash_password("password"),
        role="OWNER",
    )
    db_session.add_all([user1, user2])
    await db_session.commit()

    # User1 tries to access User2's organization
    token1 = create_access_token(str(user1.id), str(org1.id))
    response = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert response.status_code == 200
    users_data = response.json()
    # Should only see users from org1
    emails = [u["email"] for u in users_data]
    assert "user1@org1.com" in emails
    assert "user2@org2.com" not in emails


@pytest.mark.asyncio
async def test_contact_isolation_between_orgs(client, db_session):
    """Test that contacts are isolated between organizations"""
    # Create two organizations
    org1 = Organization(id=uuid4(), name="Org 1")
    org2 = Organization(id=uuid4(), name="Org 2")
    db_session.add_all([org1, org2])
    await db_session.flush()

    # Create users
    user1 = User(
        id=uuid4(),
        organization_id=org1.id,
        email="user1@org1.com",
        password_hash=hash_password("password"),
    )
    user2 = User(
        id=uuid4(),
        organization_id=org2.id,
        email="user2@org2.com",
        password_hash=hash_password("password"),
    )
    db_session.add_all([user1, user2])
    await db_session.flush()

    # Create contacts in each org
    contact1 = Contact(
        id=uuid4(),
        organization_id=org1.id,
        first_name="John",
        last_name="Doe",
        phone="+1234567890",
    )
    contact2 = Contact(
        id=uuid4(),
        organization_id=org2.id,
        first_name="Jane",
        last_name="Smith",
        phone="+0987654321",
    )
    db_session.add_all([contact1, contact2])
    await db_session.commit()

    # User1 lists contacts - should only see their org's contacts
    token1 = create_access_token(str(user1.id), str(org1.id))
    response = await client.get(
        "/api/v1/contacts",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert response.status_code == 200
    contacts = response.json()
    assert len(contacts) == 1
    assert contacts[0]["first_name"] == "John"

    # User2 lists contacts - should only see their org's contacts
    token2 = create_access_token(str(user2.id), str(org2.id))
    response = await client.get(
        "/api/v1/contacts",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert response.status_code == 200
    contacts = response.json()
    assert len(contacts) == 1
    assert contacts[0]["first_name"] == "Jane"


@pytest.mark.asyncio
async def test_cross_org_contact_access_denied(client, test_user, test_org, db_session):
    """Test that accessing another org's contact is denied"""
    # Create another organization and contact
    org2 = Organization(id=uuid4(), name="Org 2")
    db_session.add(org2)
    await db_session.flush()

    other_contact = Contact(
        id=uuid4(),
        organization_id=org2.id,
        first_name="Other",
        last_name="User",
        phone="+1111111111",
    )
    db_session.add(other_contact)
    await db_session.commit()

    # Test user tries to access other contact
    token = create_access_token(str(test_user.id), str(test_org.id))
    response = await client.get(
        f"/api/v1/contacts/{other_contact.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404  # Should not find it


@pytest.mark.asyncio
async def test_api_keys_isolated_by_org(client, test_user, test_org, db_session):
    """Test that API keys are isolated by organization"""
    # Create another org and key
    org2 = Organization(id=uuid4(), name="Org 2")
    user2 = User(
        id=uuid4(),
        organization_id=org2.id,
        email="user2@example.com",
        password_hash=hash_password("password"),
        role="ADMIN",
    )
    db_session.add_all([org2, user2])
    await db_session.flush()

    key_org1 = APIKey(
        id=uuid4(),
        organization_id=test_org.id,
        name="Key Org 1",
        key_hash="hash1",
    )
    key_org2 = APIKey(
        id=uuid4(),
        organization_id=org2.id,
        name="Key Org 2",
        key_hash="hash2",
    )
    db_session.add_all([key_org1, key_org2])
    await db_session.commit()

    # User1 lists their API keys
    token1 = create_access_token(str(test_user.id), str(test_org.id))
    response = await client.get(
        "/api/v1/api-keys",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert response.status_code == 200
    keys = response.json()
    key_names = [k["name"] for k in keys]
    assert "Key Org 1" in key_names
    assert "Key Org 2" not in key_names


@pytest.mark.asyncio
async def test_company_isolation(client, test_user, test_org, db_session):
    """Test that companies are isolated between orgs"""
    org2 = Organization(id=uuid4(), name="Org 2")
    db_session.add(org2)
    await db_session.flush()

    company1 = Company(
        id=uuid4(),
        organization_id=test_org.id,
        name="Company Org 1",
    )
    company2 = Company(
        id=uuid4(),
        organization_id=org2.id,
        name="Company Org 2",
    )
    db_session.add_all([company1, company2])
    await db_session.commit()

    # Test user lists companies
    token = create_access_token(str(test_user.id), str(test_org.id))
    response = await client.get(
        "/api/v1/companies",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    companies = response.json()
    assert len(companies) == 1
    assert companies[0]["name"] == "Company Org 1"


@pytest.mark.asyncio
async def test_deal_isolation(client, test_user, test_org, db_session):
    """Test that deals are isolated between orgs"""
    org2 = Organization(id=uuid4(), name="Org 2")
    db_session.add(org2)
    await db_session.flush()

    # Create contacts and deals in both orgs
    contact1 = Contact(
        id=uuid4(),
        organization_id=test_org.id,
        first_name="John",
        last_name="Org1",
        phone="+1111111111",
    )
    contact2 = Contact(
        id=uuid4(),
        organization_id=org2.id,
        first_name="Jane",
        last_name="Org2",
        phone="+2222222222",
    )
    db_session.add_all([contact1, contact2])
    await db_session.flush()

    pipeline1 = Pipeline(
        id=uuid4(),
        organization_id=test_org.id,
        name="Pipeline 1",
        stages=[],
    )
    pipeline2 = Pipeline(
        id=uuid4(),
        organization_id=org2.id,
        name="Pipeline 2",
        stages=[],
    )
    db_session.add_all([pipeline1, pipeline2])
    await db_session.flush()

    deal1 = Deal(
        id=uuid4(),
        organization_id=test_org.id,
        contact_id=contact1.id,
        pipeline_id=pipeline1.id,
        name="Deal Org 1",
        stage="Negotiation",
    )
    deal2 = Deal(
        id=uuid4(),
        organization_id=org2.id,
        contact_id=contact2.id,
        pipeline_id=pipeline2.id,
        name="Deal Org 2",
        stage="Closed",
    )
    db_session.add_all([deal1, deal2])
    await db_session.commit()

    # Test user lists deals
    token = create_access_token(str(test_user.id), str(test_org.id))
    response = await client.get(
        "/api/v1/deals",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    deals = response.json()
    assert len(deals) == 1
    assert deals[0]["name"] == "Deal Org 1"


@pytest.mark.asyncio
async def test_activity_isolation(client, test_user, test_org, db_session):
    """Test that activities are isolated between orgs"""
    org2 = Organization(id=uuid4(), name="Org 2")
    db_session.add(org2)
    await db_session.flush()

    contact1 = Contact(
        id=uuid4(),
        organization_id=test_org.id,
        first_name="John",
        last_name="Org1",
        phone="+1111111111",
    )
    contact2 = Contact(
        id=uuid4(),
        organization_id=org2.id,
        first_name="Jane",
        last_name="Org2",
        phone="+2222222222",
    )
    db_session.add_all([contact1, contact2])
    await db_session.flush()

    activity1 = Activity(
        id=uuid4(),
        organization_id=test_org.id,
        contact_id=contact1.id,
        activity_type="CALL",
        title="Call Org 1",
        created_by=test_user.id,
    )
    activity2 = Activity(
        id=uuid4(),
        organization_id=org2.id,
        contact_id=contact2.id,
        activity_type="EMAIL",
        title="Email Org 2",
    )
    db_session.add_all([activity1, activity2])
    await db_session.commit()

    # Test that activities are isolated
    token = create_access_token(str(test_user.id), str(test_org.id))
    response = await client.get(
        f"/api/v1/contacts/{contact1.id}/activities",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    activities = response.json()
    assert len(activities) == 1
    assert activities[0]["title"] == "Call Org 1"


@pytest.mark.asyncio
async def test_conversation_isolation(client, test_user, test_org, db_session):
    """Test that conversations are isolated between orgs"""
    org2 = Organization(id=uuid4(), name="Org 2")
    db_session.add(org2)
    await db_session.flush()

    from app.models import Conversation

    conv1 = Conversation(
        id=uuid4(),
        organization_id=test_org.id,
        conversation_type="VOICE",
        status="ACTIVE",
    )
    conv2 = Conversation(
        id=uuid4(),
        organization_id=org2.id,
        conversation_type="SMS",
        status="ENDED",
    )
    db_session.add_all([conv1, conv2])
    await db_session.commit()

    # Test that conversations are isolated
    token = create_access_token(str(test_user.id), str(test_org.id))
    response = await client.get(
        f"/api/v1/conversations/{conv1.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["conversation_type"] == "VOICE"

    # Try to access other org's conversation
    response = await client.get(
        f"/api/v1/conversations/{conv2.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404

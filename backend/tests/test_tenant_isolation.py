"""Tenant isolation tests"""

import pytest
from uuid import uuid4
from sqlalchemy import select
from app.models import Organization, User
from app.security import hash_password


@pytest.mark.asyncio
async def test_user_belongs_to_organization(db_session, test_org, test_user):
    """Test that user belongs to correct organization"""
    assert test_user.organization_id == test_org.id


@pytest.mark.asyncio
async def test_organization_isolation(db_session):
    """Test that organizations don't see each other's data"""
    # Create two organizations
    org1 = Organization(id=uuid4(), name="Org 1")
    org2 = Organization(id=uuid4(), name="Org 2")
    db_session.add(org1)
    db_session.add(org2)
    await db_session.commit()

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
    db_session.add(user1)
    db_session.add(user2)
    await db_session.commit()

    # Query users for org1 only
    result = await db_session.execute(
        select(User).where(User.organization_id == org1.id)
    )
    org1_users = result.scalars().all()

    # Should only see user1
    assert len(org1_users) == 1
    assert org1_users[0].id == user1.id
    assert org1_users[0].email == "user1@org1.com"


@pytest.mark.asyncio
async def test_user_cant_query_other_org_users(db_session):
    """Test that user cannot access other org's users"""
    # Create two organizations
    org1 = Organization(id=uuid4(), name="Org 1")
    org2 = Organization(id=uuid4(), name="Org 2")
    db_session.add(org1)
    db_session.add(org2)
    await db_session.commit()

    # Create users
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
    db_session.add(user1)
    db_session.add(user2)
    await db_session.commit()

    # User1 tries to query user2 (should use org_id filter in real code)
    # This simulates what happens if org_id filter is applied correctly
    result = await db_session.execute(
        select(User).where(
            (User.organization_id == org1.id) & (User.id == user2.id)
        )
    )
    users = result.scalars().all()

    # Should not find user2 because they're in different org
    assert len(users) == 0

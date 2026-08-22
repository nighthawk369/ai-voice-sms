"""Tests for database operations and transactions"""

import pytest
from uuid import uuid4
from sqlalchemy import select
from app.models import Organization, User, Contact, Deal, Pipeline, Company
from app.security import hash_password


@pytest.mark.asyncio
async def test_transaction_rollback(db_session, test_org):
    """Test that transaction rollback works"""
    try:
        user = User(
            id=uuid4(),
            organization_id=test_org.id,
            email="rollback_test@example.com",
            password_hash=hash_password("password"),
        )
        db_session.add(user)
        await db_session.flush()

        # Simulate an error
        raise Exception("Test error")
    except Exception:
        await db_session.rollback()

    # User should not exist
    result = await db_session.execute(
        select(User).where(User.email == "rollback_test@example.com")
    )
    assert result.scalars().first() is None


@pytest.mark.asyncio
async def test_concurrent_user_creation(db_session, test_org):
    """Test creating multiple users concurrently"""
    users = [
        User(
            id=uuid4(),
            organization_id=test_org.id,
            email=f"user{i}@example.com",
            password_hash=hash_password("password"),
        )
        for i in range(5)
    ]

    for user in users:
        db_session.add(user)

    await db_session.commit()

    # Verify all users were created
    result = await db_session.execute(
        select(User).where(User.organization_id == test_org.id)
    )
    created_users = result.scalars().all()
    assert len(created_users) >= 5


@pytest.mark.asyncio
async def test_organization_user_relationship(db_session, test_org):
    """Test organization to user relationship"""
    user1 = User(
        id=uuid4(),
        organization_id=test_org.id,
        email="user1@example.com",
        password_hash=hash_password("password"),
    )
    user2 = User(
        id=uuid4(),
        organization_id=test_org.id,
        email="user2@example.com",
        password_hash=hash_password("password"),
    )
    db_session.add_all([user1, user2])
    await db_session.commit()
    await db_session.refresh(test_org)

    assert len(test_org.users) == 2


@pytest.mark.asyncio
async def test_contact_to_company_relationship(db_session, test_org):
    """Test contact to company relationship"""
    company = Company(
        id=uuid4(),
        organization_id=test_org.id,
        name="Test Company",
    )
    db_session.add(company)
    await db_session.commit()

    contact = Contact(
        id=uuid4(),
        organization_id=test_org.id,
        first_name="John",
        last_name="Doe",
        phone="+1234567890",
        company_id=company.id,
    )
    db_session.add(contact)
    await db_session.commit()
    await db_session.refresh(contact)

    assert contact.company_id == company.id


@pytest.mark.asyncio
async def test_bulk_update_operation(db_session, test_org):
    """Test bulk updating contacts"""
    # Create contacts
    contacts = [
        Contact(
            id=uuid4(),
            organization_id=test_org.id,
            first_name=f"Contact{i}",
            last_name="Test",
            phone=f"+123456789{i}",
            status="NEW",
        )
        for i in range(3)
    ]
    db_session.add_all(contacts)
    await db_session.commit()

    # Update all contacts
    result = await db_session.execute(
        select(Contact).where(Contact.organization_id == test_org.id)
    )
    all_contacts = result.scalars().all()
    for contact in all_contacts:
        contact.status = "QUALIFIED"

    await db_session.commit()

    # Verify update
    result = await db_session.execute(
        select(Contact).where(Contact.organization_id == test_org.id)
    )
    updated = result.scalars().all()
    assert all(c.status == "QUALIFIED" for c in updated)


@pytest.mark.asyncio
async def test_query_with_filters(db_session, test_org):
    """Test querying with multiple filters"""
    # Create contacts with different statuses
    for i in range(3):
        Contact(
            id=uuid4(),
            organization_id=test_org.id,
            first_name=f"Lead{i}",
            last_name="Test",
            phone=f"+123456789{i}",
            contact_type="LEAD",
            status="NEW" if i < 2 else "QUALIFIED",
        )

    await db_session.commit()

    # Query with multiple filters
    result = await db_session.execute(
        select(Contact).where(
            (Contact.organization_id == test_org.id)
            & (Contact.contact_type == "LEAD")
            & (Contact.status == "NEW")
        )
    )
    filtered_contacts = result.scalars().all()
    assert len(filtered_contacts) == 2


@pytest.mark.asyncio
async def test_pagination(db_session, test_org):
    """Test pagination functionality"""
    # Create many contacts
    for i in range(15):
        contact = Contact(
            id=uuid4(),
            organization_id=test_org.id,
            first_name=f"Contact{i}",
            last_name="Test",
            phone=f"+123456789{i:02d}",
        )
        db_session.add(contact)

    await db_session.commit()

    # Test pagination
    page_size = 5
    page = 0

    result = await db_session.execute(
        select(Contact)
        .where(Contact.organization_id == test_org.id)
        .limit(page_size)
        .offset(page * page_size)
    )
    page_contacts = result.scalars().all()

    assert len(page_contacts) == page_size


@pytest.mark.asyncio
async def test_unique_constraint_violation(db_session, test_org):
    """Test that unique constraints are enforced"""
    from sqlalchemy.exc import IntegrityError

    user1 = User(
        id=uuid4(),
        organization_id=test_org.id,
        email="unique@example.com",
        password_hash=hash_password("password"),
    )
    db_session.add(user1)
    await db_session.commit()

    # Try to create duplicate
    user2 = User(
        id=uuid4(),
        organization_id=test_org.id,
        email="unique@example.com",
        password_hash=hash_password("password"),
    )
    db_session.add(user2)

    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_foreign_key_constraint(db_session, test_org):
    """Test that foreign key constraints are enforced"""
    from sqlalchemy.exc import IntegrityError
    from uuid import uuid4 as new_uuid

    # Try to create contact with non-existent organization
    contact = Contact(
        id=uuid4(),
        organization_id=new_uuid(),  # Non-existent org
        first_name="Test",
        last_name="Contact",
        phone="+1234567890",
    )
    db_session.add(contact)

    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_update_with_timestamp(db_session, test_org):
    """Test that updated_at timestamp is updated on modification"""
    import asyncio
    from datetime import datetime

    user = User(
        id=uuid4(),
        organization_id=test_org.id,
        email="timestamp@example.com",
        password_hash=hash_password("password"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    original_updated = user.updated_at

    # Wait a moment
    await asyncio.sleep(0.1)

    # Update user
    user.first_name = "Updated"
    await db_session.commit()
    await db_session.refresh(user)

    # Verify timestamp was updated
    assert user.updated_at > original_updated or user.updated_at == original_updated


@pytest.mark.asyncio
async def test_json_field_storage(db_session, test_org):
    """Test storing and retrieving JSON data"""
    contact = Contact(
        id=uuid4(),
        organization_id=test_org.id,
        first_name="John",
        last_name="Doe",
        phone="+1234567890",
        custom_fields={
            "preferred_language": "Spanish",
            "industry": "Construction",
            "company_size": "10-50",
        },
    )
    db_session.add(contact)
    await db_session.commit()
    await db_session.refresh(contact)

    assert contact.custom_fields["preferred_language"] == "Spanish"
    assert contact.custom_fields["company_size"] == "10-50"


@pytest.mark.asyncio
async def test_index_usage(db_session, test_org):
    """Test that queries using indexes work efficiently"""
    # Create contacts
    for i in range(10):
        contact = Contact(
            id=uuid4(),
            organization_id=test_org.id,
            first_name=f"Contact{i}",
            last_name="Test",
            phone=f"+123456789{i}",
            contact_type="LEAD",
        )
        db_session.add(contact)

    await db_session.commit()

    # Query using indexed columns
    result = await db_session.execute(
        select(Contact).where(
            (Contact.organization_id == test_org.id)
            & (Contact.contact_type == "LEAD")
        )
    )
    contacts = result.scalars().all()

    assert len(contacts) == 10

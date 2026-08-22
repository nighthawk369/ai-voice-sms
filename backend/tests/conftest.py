"""Pytest configuration and fixtures"""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from uuid import uuid4

from app.main import app
from app.db import Base, get_db
from app.models import Organization, User, Contact, Company, Pipeline, Deal
from app.security import hash_password, create_access_token


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session():
    """Create a test database session"""
    # Use in-memory SQLite for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def client(db_session):
    """Create a test client with database override"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_org(db_session):
    """Create a test organization"""
    org = Organization(
        id=uuid4(),
        name="Test Org",
        timezone="America/New_York",
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return org


@pytest.fixture
async def test_user(db_session, test_org):
    """Create a test user"""
    user = User(
        id=uuid4(),
        organization_id=test_org.id,
        email="test@example.com",
        password_hash=hash_password("testpass123"),
        role="OWNER",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_company(db_session, test_org):
    """Create a test company"""
    company = Company(
        id=uuid4(),
        organization_id=test_org.id,
        name="Test Company",
        industry="Technology",
        website="https://testcompany.com",
        email="info@testcompany.com",
        phone="+1234567890",
    )
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)
    return company


@pytest.fixture
async def test_contact(db_session, test_org, test_company):
    """Create a test contact"""
    contact = Contact(
        id=uuid4(),
        organization_id=test_org.id,
        company_id=test_company.id,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+1234567890",
        contact_type="LEAD",
        status="NEW",
    )
    db_session.add(contact)
    await db_session.commit()
    await db_session.refresh(contact)
    return contact


@pytest.fixture
async def test_pipeline(db_session, test_org):
    """Create a test pipeline"""
    pipeline = Pipeline(
        id=uuid4(),
        organization_id=test_org.id,
        name="Test Pipeline",
        stages=[
            {"id": "new", "name": "New", "color": "#3498db", "position": 0},
            {"id": "qualified", "name": "Qualified", "color": "#2ecc71", "position": 1},
            {"id": "closed", "name": "Closed", "color": "#27ae60", "position": 2},
        ],
        is_default=True,
    )
    db_session.add(pipeline)
    await db_session.commit()
    await db_session.refresh(pipeline)
    return pipeline


@pytest.fixture
async def test_deal(db_session, test_org, test_contact, test_pipeline, test_company):
    """Create a test deal"""
    deal = Deal(
        id=uuid4(),
        organization_id=test_org.id,
        contact_id=test_contact.id,
        company_id=test_company.id,
        pipeline_id=test_pipeline.id,
        name="Test Deal",
        amount=10000.00,
        stage="new",
        deal_status="OPEN",
    )
    db_session.add(deal)
    await db_session.commit()
    await db_session.refresh(deal)
    return deal

"""Database seed script - populate initial data for testing and demo"""

import asyncio
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import get_settings
from app.models import (
    Organization, User, Pipeline, CustomField, KnowledgeBaseItem, Contact, Company
)
from app.security import hash_password
from app.db import Base

settings = get_settings()


async def seed_database():
    """Seed the database with initial data"""
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=True,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    AsyncSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionLocal() as session:
        # Check if seed data already exists
        from sqlalchemy import select

        existing_org = await session.execute(
            select(Organization).where(Organization.name == "Demo Organization")
        )
        if existing_org.scalar_one_or_none():
            print("Seed data already exists. Skipping.")
            await engine.dispose()
            return

        # Create demo organization
        org = Organization(
            id=uuid4(),
            name="Demo Organization",
            timezone="America/New_York",
            locale="en_US",
            website="https://example.com",
            industry="Professional Services",
            subscription_plan="PROFESSIONAL",
            subscription_status="ACTIVE",
        )
        session.add(org)
        await session.flush()

        # Create demo users
        owner = User(
            id=uuid4(),
            organization_id=org.id,
            email="owner@example.com",
            password_hash=hash_password("demo1234"),
            first_name="John",
            last_name="Owner",
            role="OWNER",
            is_active=True,
            is_verified=True,
        )

        admin = User(
            id=uuid4(),
            organization_id=org.id,
            email="admin@example.com",
            password_hash=hash_password("demo1234"),
            first_name="Jane",
            last_name="Admin",
            role="ADMIN",
            is_active=True,
            is_verified=True,
        )

        manager = User(
            id=uuid4(),
            organization_id=org.id,
            email="manager@example.com",
            password_hash=hash_password("demo1234"),
            first_name="Bob",
            last_name="Manager",
            role="MANAGER",
            is_active=True,
            is_verified=True,
        )

        agent = User(
            id=uuid4(),
            organization_id=org.id,
            email="agent@example.com",
            password_hash=hash_password("demo1234"),
            first_name="Alice",
            last_name="Agent",
            role="AGENT",
            is_active=True,
            is_verified=True,
        )

        session.add_all([owner, admin, manager, agent])
        await session.flush()

        # Create default pipelines
        sales_pipeline = Pipeline(
            id=uuid4(),
            organization_id=org.id,
            name="Sales Pipeline",
            description="Standard sales pipeline",
            stages=[
                {"id": "lead", "name": "Lead", "color": "#3498db", "position": 0},
                {"id": "qualified", "name": "Qualified", "color": "#2ecc71", "position": 1},
                {"id": "proposal", "name": "Proposal", "color": "#f39c12", "position": 2},
                {"id": "negotiation", "name": "Negotiation", "color": "#e74c3c", "position": 3},
                {"id": "closed", "name": "Closed Won", "color": "#27ae60", "position": 4},
            ],
            is_default=True,
            is_active=True,
        )

        support_pipeline = Pipeline(
            id=uuid4(),
            organization_id=org.id,
            name="Support Pipeline",
            description="Customer support ticket pipeline",
            stages=[
                {"id": "new", "name": "New", "color": "#e74c3c", "position": 0},
                {"id": "assigned", "name": "Assigned", "color": "#f39c12", "position": 1},
                {"id": "in_progress", "name": "In Progress", "color": "#3498db", "position": 2},
                {"id": "resolved", "name": "Resolved", "color": "#2ecc71", "position": 3},
                {"id": "closed", "name": "Closed", "color": "#95a5a6", "position": 4},
            ],
            is_default=False,
            is_active=True,
        )

        session.add_all([sales_pipeline, support_pipeline])
        await session.flush()

        # Create custom fields for contacts
        custom_fields = [
            CustomField(
                id=uuid4(),
                organization_id=org.id,
                object_type="CONTACT",
                field_name="linkedin_profile",
                field_label="LinkedIn Profile",
                field_type="TEXT",
                is_required=False,
                is_active=True,
            ),
            CustomField(
                id=uuid4(),
                organization_id=org.id,
                object_type="CONTACT",
                field_name="lead_source_detail",
                field_label="Lead Source Detail",
                field_type="DROPDOWN",
                field_options=["Referral", "Online Ad", "Content", "Event", "Cold Outreach", "Other"],
                is_required=False,
                is_active=True,
            ),
            CustomField(
                id=uuid4(),
                organization_id=org.id,
                object_type="COMPANY",
                field_name="annual_mrr",
                field_label="Annual MRR",
                field_type="NUMBER",
                is_required=False,
                is_active=True,
            ),
            CustomField(
                id=uuid4(),
                organization_id=org.id,
                object_type="COMPANY",
                field_name="technology_stack",
                field_label="Technology Stack",
                field_type="TEXT",
                is_required=False,
                is_active=True,
            ),
            CustomField(
                id=uuid4(),
                organization_id=org.id,
                object_type="DEAL",
                field_name="deal_type",
                field_label="Deal Type",
                field_type="DROPDOWN",
                field_options=["New Business", "Expansion", "Renewal", "Upsell"],
                is_required=True,
                is_active=True,
            ),
            CustomField(
                id=uuid4(),
                organization_id=org.id,
                object_type="DEAL",
                field_name="competitor",
                field_label="Competing Against",
                field_type="TEXT",
                is_required=False,
                is_active=True,
            ),
        ]
        session.add_all(custom_fields)
        await session.flush()

        # Create demo companies
        companies = [
            Company(
                id=uuid4(),
                organization_id=org.id,
                name="Acme Corp",
                industry="Technology",
                website="https://acme.example.com",
                phone="+1-555-0100",
                email="info@acme.example.com",
                address="123 Tech Street",
                city="San Francisco",
                state="CA",
                zip_code="94105",
                country="USA",
                employee_count=250,
                annual_revenue=25000000,
                company_status="CUSTOMER",
                assigned_to=manager.id,
            ),
            Company(
                id=uuid4(),
                organization_id=org.id,
                name="TechStart Inc",
                industry="SaaS",
                website="https://techstart.example.com",
                phone="+1-555-0101",
                email="sales@techstart.example.com",
                address="456 Innovation Way",
                city="Austin",
                state="TX",
                zip_code="78701",
                country="USA",
                employee_count=50,
                annual_revenue=5000000,
                company_status="PROSPECT",
                assigned_to=agent.id,
            ),
        ]
        session.add_all(companies)
        await session.flush()

        # Create demo contacts
        contacts = [
            Contact(
                id=uuid4(),
                organization_id=org.id,
                company_id=companies[0].id,
                first_name="Michael",
                last_name="Smith",
                email="michael@acme.example.com",
                phone="+1-555-0110",
                contact_type="CUSTOMER",
                status="CONVERTED",
                source="REFERRAL",
                assigned_to=manager.id,
            ),
            Contact(
                id=uuid4(),
                organization_id=org.id,
                company_id=companies[1].id,
                first_name="Sarah",
                last_name="Johnson",
                email="sarah@techstart.example.com",
                phone="+1-555-0111",
                contact_type="LEAD",
                status="QUALIFIED",
                source="WEBSITE",
                assigned_to=agent.id,
            ),
        ]
        session.add_all(contacts)
        await session.flush()

        # Create knowledge base items
        kb_items = [
            KnowledgeBaseItem(
                id=uuid4(),
                organization_id=org.id,
                title="Getting Started Guide",
                content="This guide will help you get started with the platform...",
                category="Getting Started",
                tags=["onboarding", "basics"],
                is_published=True,
                order=0,
                created_by=admin.id,
            ),
            KnowledgeBaseItem(
                id=uuid4(),
                organization_id=org.id,
                title="CRM Best Practices",
                content="Here are some best practices for using the CRM...",
                category="Best Practices",
                tags=["crm", "tips"],
                is_published=True,
                order=1,
                created_by=admin.id,
            ),
            KnowledgeBaseItem(
                id=uuid4(),
                organization_id=org.id,
                title="API Integration Guide",
                content="Learn how to integrate with our API...",
                category="Integration",
                tags=["api", "integration", "development"],
                is_published=True,
                order=2,
                created_by=admin.id,
            ),
        ]
        session.add_all(kb_items)

        # Commit all changes
        await session.commit()

        print("✓ Database seeded successfully!")
        print(f"✓ Created organization: {org.name}")
        print(f"✓ Created 4 users (owner, admin, manager, agent)")
        print(f"✓ Created 2 pipelines (Sales, Support)")
        print(f"✓ Created 6 custom field definitions")
        print(f"✓ Created 2 demo companies and 2 demo contacts")
        print(f"✓ Created 3 knowledge base items")
        print("\nDemo credentials:")
        print("  Email: owner@example.com | Password: demo1234 (Owner)")
        print("  Email: admin@example.com | Password: demo1234 (Admin)")
        print("  Email: manager@example.com | Password: demo1234 (Manager)")
        print("  Email: agent@example.com | Password: demo1234 (Agent)")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())

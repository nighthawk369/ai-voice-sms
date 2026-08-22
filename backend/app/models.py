"""SQLAlchemy ORM models for AI Voice & SMS Platform with In-House CRM"""

from datetime import datetime
from uuid import uuid4
from decimal import Decimal
from sqlalchemy import Column, String, UUID, DateTime, Boolean, ForeignKey, Index, Text, JSON, Integer, Numeric, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base
import enum


# ============================================================================
# CORE PLATFORM MODELS
# ============================================================================

class Organization(Base):
    """Tenant organization"""

    __tablename__ = "organization"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    timezone = Column(String(50), default="America/New_York")
    locale = Column(String(10), default="en_US")
    phone = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)  # HVAC, Plumbing, Electrical, etc.
    subscription_plan = Column(String(50), default="BASIC")  # BASIC, PROFESSIONAL, ENTERPRISE
    subscription_status = Column(String(50), default="ACTIVE")  # ACTIVE, TRIAL, SUSPENDED, CANCELLED
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    max_users = Column(Integer, default=10)
    max_contacts = Column(Integer, default=10000)
    max_calls_per_month = Column(Integer, default=1000)
    billing_email = Column(String(255), nullable=True)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="organization", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="organization", cascade="all, delete-orphan")
    companies = relationship("Company", back_populates="organization", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="organization", cascade="all, delete-orphan")
    pipelines = relationship("Pipeline", back_populates="organization", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="organization", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="organization", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="organization", cascade="all, delete-orphan")
    workflows = relationship("Workflow", back_populates="organization", cascade="all, delete-orphan")
    custom_fields = relationship("CustomField", back_populates="organization", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="organization", cascade="all, delete-orphan")
    knowledge_base_items = relationship("KnowledgeBaseItem", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization {self.name}>"


class User(Base):
    """Platform user (belongs to organization)"""

    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    role = Column(String(50), default="AGENT", nullable=False)  # OWNER, ADMIN, MANAGER, AGENT, VIEWER
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_org_user_email", "organization_id", "email", unique=True),
        Index("idx_user_is_active", "is_active"),
    )

    def __repr__(self):
        return f"<User {self.email}>"


class Session(Base):
    """User session tracking"""

    __tablename__ = "session"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="sessions")
    user = relationship("User", back_populates="sessions")

    __table_args__ = (
        Index("idx_org_session", "organization_id", "user_id"),
        Index("idx_session_expires", "expires_at"),
    )

    def __repr__(self):
        return f"<Session {self.user_id}>"


class APIKey(Base):
    """API key for external integrations"""

    __tablename__ = "api_key"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False, unique=True)
    scopes = Column(JSON, default=["read", "write"])
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="api_keys")

    # Indexes
    __table_args__ = (
        Index("idx_org_api_key", "organization_id", "is_active"),
    )

    def __repr__(self):
        return f"<APIKey {self.name}>"


# ============================================================================
# IN-HOUSE CRM MODELS
# ============================================================================

class Contact(Base):
    """Customer/Lead contact in CRM"""

    __tablename__ = "contact"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company.id"), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=False)
    secondary_phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    zip_code = Column(String(10), nullable=True)
    country = Column(String(100), nullable=True)
    contact_type = Column(String(50), default="LEAD")  # LEAD, PROSPECT, CUSTOMER, INACTIVE
    status = Column(String(50), default="NEW")  # NEW, QUALIFIED, UNQUALIFIED, CONVERTED
    source = Column(String(100), nullable=True)  # PHONE, EMAIL, WEBSITE, REFERRAL, etc.
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSON, default={})
    last_contact_date = Column(DateTime(timezone=True), nullable=True)
    next_follow_up = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="contacts")
    company = relationship("Company", back_populates="contacts")
    activities = relationship("Activity", back_populates="contact", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="contact")
    tasks = relationship("Task", back_populates="contact", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_org_contact_phone", "organization_id", "phone"),
        Index("idx_org_contact_type", "organization_id", "contact_type"),
        Index("idx_contact_status", "status"),
    )

    def __repr__(self):
        return f"<Contact {self.first_name} {self.last_name}>"


class Company(Base):
    """Company/Account in CRM"""

    __tablename__ = "company"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    name = Column(String(255), nullable=False)
    industry = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    zip_code = Column(String(10), nullable=True)
    country = Column(String(100), nullable=True)
    employee_count = Column(Integer, nullable=True)
    annual_revenue = Column(Numeric(12, 2), nullable=True)
    company_status = Column(String(50), default="PROSPECT")  # PROSPECT, CUSTOMER, INACTIVE
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="companies")
    contacts = relationship("Contact", back_populates="company")
    deals = relationship("Deal", back_populates="company")

    __table_args__ = (
        Index("idx_org_company_name", "organization_id", "name"),
        Index("idx_company_status", "company_status"),
    )

    def __repr__(self):
        return f"<Company {self.name}>"


class Pipeline(Base):
    """Sales pipeline/stage configuration"""

    __tablename__ = "pipeline"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    stages = Column(JSON, default=[])  # [{id, name, color, position}]
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="pipelines")
    deals = relationship("Deal", back_populates="pipeline")

    def __repr__(self):
        return f"<Pipeline {self.name}>"


class Deal(Base):
    """Sales deal/opportunity"""

    __tablename__ = "deal"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contact.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company.id"), nullable=True)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipeline.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Numeric(12, 2), nullable=True)
    stage = Column(String(100), nullable=False)  # Matches pipeline stage
    deal_status = Column(String(50), default="OPEN")  # OPEN, WON, LOST
    probability = Column(Float, default=50.0)  # 0-100
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    expected_close_date = Column(DateTime(timezone=True), nullable=True)
    closed_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="deals")
    contact = relationship("Contact", back_populates="deals")
    company = relationship("Company", back_populates="deals")
    pipeline = relationship("Pipeline", back_populates="deals")
    activities = relationship("Activity", back_populates="deal", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_org_deal_status", "organization_id", "deal_status"),
        Index("idx_deal_stage", "stage"),
    )

    def __repr__(self):
        return f"<Deal {self.name}>"


class Activity(Base):
    """Activity log (calls, emails, meetings, notes)"""

    __tablename__ = "activity"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contact.id"), nullable=False)
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deal.id"), nullable=True)
    activity_type = Column(String(50), nullable=False)  # CALL, EMAIL, MEETING, NOTE, TASK
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    metadata = Column(JSON, default={})  # Recording URL, transcript, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="activities")
    contact = relationship("Contact", back_populates="activities")
    deal = relationship("Deal", back_populates="activities")

    __table_args__ = (
        Index("idx_org_activity_type", "organization_id", "activity_type"),
        Index("idx_contact_activity", "contact_id", "activity_type"),
    )

    def __repr__(self):
        return f"<Activity {self.activity_type}>"


class Task(Base):
    """Task/To-do items"""

    __tablename__ = "task"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contact.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED, CANCELLED
    priority = Column(String(50), default="MEDIUM")  # LOW, MEDIUM, HIGH, URGENT
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    contact = relationship("Contact", back_populates="tasks")

    __table_args__ = (
        Index("idx_org_task_status", "organization_id", "status"),
        Index("idx_task_due_date", "due_date"),
    )

    def __repr__(self):
        return f"<Task {self.title}>"


class CustomField(Base):
    """Custom field definitions for contacts, companies, deals"""

    __tablename__ = "custom_field"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    object_type = Column(String(50), nullable=False)  # CONTACT, COMPANY, DEAL
    field_name = Column(String(255), nullable=False)
    field_label = Column(String(255), nullable=False)
    field_type = Column(String(50), nullable=False)  # TEXT, NUMBER, DROPDOWN, DATE, CHECKBOX, etc.
    field_options = Column(JSON, default=[])  # For dropdown fields
    is_required = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="custom_fields")

    __table_args__ = (
        Index("idx_org_custom_field", "organization_id", "object_type"),
    )

    def __repr__(self):
        return f"<CustomField {self.field_name}>"


# ============================================================================
# VOICE & CONVERSATION MODELS
# ============================================================================

class Conversation(Base):
    """Voice/chat conversation with AI"""

    __tablename__ = "conversation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contact.id"), nullable=True)
    conversation_type = Column(String(50), nullable=False)  # VOICE, SMS, CHAT
    status = Column(String(50), default="ACTIVE")  # ACTIVE, ENDED, ESCALATED
    phone_number = Column(String(20), nullable=True)
    twilio_call_sid = Column(String(255), nullable=True, unique=True)
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    intent = Column(String(100), nullable=True)  # BOOKING, SUPPORT, INFO, etc.
    sentiment = Column(String(50), nullable=True)  # POSITIVE, NEUTRAL, NEGATIVE
    llm_provider = Column(String(50), default="openai")  # openai, claude, gemini, ollama
    tokens_used = Column(Integer, default=0)
    cost = Column(Numeric(8, 4), default=0)
    transfer_to = Column(String(255), nullable=True)  # Phone number if escalated
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_org_conversation_status", "organization_id", "status"),
        Index("idx_twilio_call_sid", "twilio_call_sid"),
    )

    def __repr__(self):
        return f"<Conversation {self.id}>"


class Message(Base):
    """Individual message in conversation"""

    __tablename__ = "message"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversation.id"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message {self.role}>"


# ============================================================================
# KNOWLEDGE BASE MODELS
# ============================================================================

class KnowledgeBaseItem(Base):
    """Knowledge base articles and documents"""

    __tablename__ = "knowledge_base_item"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    tags = Column(JSON, default=[])
    is_published = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    created_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="knowledge_base_items")

    __table_args__ = (
        Index("idx_org_kb_published", "organization_id", "is_published"),
        Index("idx_kb_category", "category"),
    )

    def __repr__(self):
        return f"<KnowledgeBaseItem {self.title}>"


# ============================================================================
# INTEGRATION MODELS
# ============================================================================

class Integration(Base):
    """External service integration (CRM, Calendar, etc.)"""

    __tablename__ = "integration"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    integration_type = Column(String(100), nullable=False)  # servicetitan, jobber, hubspot, etc.
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    config = Column(JSON, default={})
    sync_status = Column(String(50), default="IDLE")  # IDLE, SYNCING, ERROR
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    last_sync_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="integrations")

    __table_args__ = (
        Index("idx_org_integration_type", "organization_id", "integration_type"),
    )

    def __repr__(self):
        return f"<Integration {self.integration_type}>"


# ============================================================================
# WORKFLOW & AUTOMATION MODELS
# ============================================================================

class Workflow(Base):
    """Workflow automation configuration"""

    __tablename__ = "workflow"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    trigger_type = Column(String(100), nullable=False)  # call_received, deal_created, etc.
    trigger_config = Column(JSON, default={})
    actions = Column(JSON, default=[])  # [{type, config}]
    is_active = Column(Boolean, default=True)
    execution_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="workflows")

    def __repr__(self):
        return f"<Workflow {self.name}>"

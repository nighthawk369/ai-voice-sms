"""SQLAlchemy ORM models"""

from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, UUID, DateTime, Boolean, ForeignKey, Index, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base


class Organization(Base):
    """Tenant organization"""

    __tablename__ = "organization"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    timezone = Column(String(50), default="America/New_York")
    locale = Column(String(10), default="en_US")
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="organization", cascade="all, delete-orphan")

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
    role = Column(String(50), default="AGENT", nullable=False)  # OWNER, ADMIN, MANAGER, AGENT, VIEWER
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="users")

    # Indexes for fast lookups
    __table_args__ = (
        Index("idx_org_user_email", "organization_id", "email", unique=True),
        Index("idx_user_is_active", "is_active"),
    )

    def __repr__(self):
        return f"<User {self.email}>"


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

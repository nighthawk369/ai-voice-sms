"""Pydantic schemas for API requests/responses"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


# Organization Schemas
class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    business_type: str = "general_contractor"
    timezone: str = "America/New_York"
    locale: str = "en_US"


class OrganizationRead(BaseModel):
    id: UUID
    name: str
    business_type: str
    industry_category: str
    timezone: str
    locale: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    org_name: Optional[str] = None  # For signup
    business_type: Optional[str] = "general_contractor"  # HVAC, Restaurant, Hotel, etc.


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Auth Schemas
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# API Key Schemas
class APIKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    scopes: List[str] = ["read", "write"]
    expires_at: Optional[datetime] = None


class APIKeyRead(BaseModel):
    id: UUID
    name: str
    scopes: List[str]
    is_active: bool
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Error Schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    request_id: Optional[str] = None


# Health Check
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    environment: str


class ReadinessResponse(BaseModel):
    database: bool
    redis: bool
    timestamp: datetime


# ============================================================================
# CRM SCHEMAS - CONTACT
# ============================================================================

class ContactCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = None
    phone: str = Field(..., min_length=10)
    secondary_phone: Optional[str] = None
    company_id: Optional[UUID] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    contact_type: str = "LEAD"
    source: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: dict = {}


class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    contact_type: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: Optional[dict] = None


class ContactRead(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: Optional[str]
    phone: str
    contact_type: str
    status: str
    source: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CRM SCHEMAS - COMPANY
# ============================================================================

class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    notes: Optional[str] = None


class CompanyRead(BaseModel):
    id: UUID
    name: str
    industry: Optional[str]
    website: Optional[str]
    phone: Optional[str]
    company_status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CRM SCHEMAS - DEAL
# ============================================================================

class DealCreate(BaseModel):
    contact_id: UUID
    company_id: Optional[UUID] = None
    pipeline_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    amount: Optional[float] = None
    stage: str
    probability: float = 50.0
    expected_close_date: Optional[datetime] = None


class DealRead(BaseModel):
    id: UUID
    name: str
    amount: Optional[float]
    stage: str
    deal_status: str
    probability: float
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CRM SCHEMAS - ACTIVITY
# ============================================================================

class ActivityCreate(BaseModel):
    contact_id: UUID
    deal_id: Optional[UUID] = None
    activity_type: str  # CALL, EMAIL, MEETING, NOTE, TASK
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    duration_seconds: Optional[int] = None
    scheduled_for: Optional[datetime] = None


class ActivityRead(BaseModel):
    id: UUID
    contact_id: UUID
    activity_type: str
    title: str
    description: Optional[str]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CONVERSATION SCHEMAS
# ============================================================================

class MessageCreate(BaseModel):
    role: str  # user, assistant, system
    content: str = Field(..., min_length=1)
    metadata: Optional[dict] = {}


class MessageRead(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    conversation_type: str  # VOICE, SMS, CHAT
    phone_number: Optional[str] = None
    contact_id: Optional[UUID] = None


class ConversationRead(BaseModel):
    id: UUID
    conversation_type: str
    status: str
    phone_number: Optional[str]
    transcript: Optional[str]
    intent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationDetail(ConversationRead):
    messages: List[MessageRead]


# ============================================================================
# INTEGRATION SCHEMAS
# ============================================================================

class IntegrationCreate(BaseModel):
    integration_type: str
    name: str
    config: dict = {}


class IntegrationRead(BaseModel):
    id: UUID
    integration_type: str
    name: str
    is_active: bool
    sync_status: str
    last_sync_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# WORKFLOW SCHEMAS
# ============================================================================

class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    trigger_type: str
    trigger_config: dict = {}
    actions: List[dict] = []


class WorkflowRead(BaseModel):
    id: UUID
    name: str
    trigger_type: str
    is_active: bool
    execution_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# PAGINATION SCHEMAS
# ============================================================================

class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 100
    sort_by: Optional[str] = None
    sort_order: str = "asc"


class PaginatedResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List
    has_more: bool


# ============================================================================
# KNOWLEDGE BASE SCHEMAS (PHASE 8)
# ============================================================================

class KnowledgeBaseItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    is_published: bool = False


class KnowledgeBaseItemUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None
    order: Optional[int] = None


class KnowledgeBaseItemRead(BaseModel):
    id: UUID
    title: str
    content: str
    category: Optional[str]
    tags: List[str]
    is_published: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# VOICE INTEGRATION SCHEMAS (PHASE 9)
# ============================================================================

class VoiceCallCreate(BaseModel):
    to_phone: str
    contact_id: Optional[UUID] = None


class VoiceCallRead(BaseModel):
    call_id: str
    status: str
    phone_number: str
    duration: int
    transcript: Optional[str]
    created_at: str


class CallMessageCreate(BaseModel):
    role: str
    content: str


class CallMessageRead(BaseModel):
    id: str
    role: str
    content: str
    created_at: str


# ============================================================================
# SMS INTEGRATION SCHEMAS (PHASE 10)
# ============================================================================

class SMSSendCreate(BaseModel):
    to_phone: str
    message_text: str
    contact_id: Optional[UUID] = None


class SMSConversationRead(BaseModel):
    conversation_id: str
    phone_number: str
    status: str
    last_message_at: str
    message_count: int


class SMSBatchCreate(BaseModel):
    recipients: List[dict]
    message_text: str


class OptOutCreate(BaseModel):
    phone: str
    reason: str = "user_requested"


# ============================================================================
# CALENDAR INTEGRATION SCHEMAS (PHASE 11)
# ============================================================================

class AvailabilitySlot(BaseModel):
    start_time: str
    end_time: str
    duration_minutes: int
    provider: Optional[str] = None


class AppointmentCreate(BaseModel):
    provider: str
    user_id: UUID
    contact_id: UUID
    start_time: str
    end_time: str
    title: str
    description: Optional[str] = None


class AppointmentRead(BaseModel):
    appointment_id: str
    status: str
    start_time: str
    end_time: str
    title: str


# ============================================================================
# INTEGRATION ENGINE SCHEMAS (PHASE 12)
# ============================================================================

class IntegrationCreateRequest(BaseModel):
    integration_type: str
    name: str
    credentials: dict = {}


class IntegrationReadResponse(BaseModel):
    id: str
    type: str
    name: str
    is_active: bool
    sync_status: str


class WebhookPayload(BaseModel):
    system: str
    event_type: str
    payload: dict


class SyncResult(BaseModel):
    status: str
    synced_count: int
    error_count: int


# ============================================================================
# WORKFLOW SCHEMAS (PHASE 18)
# ============================================================================

class WorkflowAction(BaseModel):
    type: str
    config: dict = {}


class WorkflowCondition(BaseModel):
    field: str
    operator: str
    value: str


class WorkflowCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    trigger_type: str
    trigger_config: Optional[dict] = None
    conditions: Optional[List[dict]] = None
    actions: Optional[List[dict]] = None
    is_active: Optional[bool] = True


class WorkflowUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[List[dict]] = None
    actions: Optional[List[dict]] = None
    is_active: Optional[bool] = None


class WorkflowResponseSchema(BaseModel):
    id: str
    name: str
    trigger_type: str
    is_active: bool
    execution_count: int
    created_at: datetime


# ============================================================================
# ANALYTICS SCHEMAS (PHASE 19)
# ============================================================================

class EventTrackingSchema(BaseModel):
    event_type: str
    event_category: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    properties: Optional[dict] = None


class AnalyticsMetricSchema(BaseModel):
    metric_name: str
    metric_type: str
    value: float
    dimension: Optional[str] = None
    dimension_value: Optional[str] = None


class DashboardSummarySchema(BaseModel):
    period: dict
    calls: dict
    conversion_funnel: dict


# ============================================================================
# USAGE METERING SCHEMAS (PHASE 20)
# ============================================================================

class UsageMetricSchema(BaseModel):
    metric_type: str
    quantity: int
    unit: str
    cost: float


class UsageReportSchema(BaseModel):
    period: dict
    usage_by_type: dict
    total_cost: float


class TokenCountSchema(BaseModel):
    text: str
    provider: Optional[str] = "openai"


# ============================================================================
# BILLING SCHEMAS (PHASE 21)
# ============================================================================

class BillingAccountCreateSchema(BaseModel):
    billing_email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    billing_name: str = Field(..., min_length=1, max_length=255)
    tier: Optional[str] = "STARTER"


class BillingAccountSchema(BaseModel):
    id: str
    organization_id: str
    billing_email: str
    subscription_tier: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    next_billing_date: datetime


class SubscriptionUpgradeSchema(BaseModel):
    new_tier: str


class InvoiceLineItemSchema(BaseModel):
    description: str
    quantity: float
    unit_price: float
    amount: float


class InvoiceSchema(BaseModel):
    id: str
    invoice_number: str
    status: str
    total_amount: float
    currency: str
    invoice_date: datetime
    due_date: datetime
    line_items: List[InvoiceLineItemSchema]


class PaymentProcessingSchema(BaseModel):
    invoice_id: str
    payment_method_id: Optional[str] = None
    errors: List[str] = []

"""Comprehensive API routes for AI Voice & SMS Platform with CRM"""

from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.db import get_db
from app.models import (
    User, Organization, Contact, Company, Deal, Activity, Conversation,
    Message, Integration, Workflow, Pipeline, APIKey
)
from app.schemas import (
    UserCreate, UserLogin, UserRead, TokenResponse, TokenRefresh, TokenRefreshResponse,
    OrganizationRead, HealthResponse,
    ContactCreate, ContactUpdate, ContactRead,
    CompanyCreate, CompanyRead,
    DealCreate, DealRead,
    ActivityCreate, ActivityRead,
    ConversationCreate, ConversationRead, ConversationDetail, MessageCreate, MessageRead,
    IntegrationCreate, IntegrationRead,
    WorkflowCreate, WorkflowRead,
    APIKeyCreate, APIKeyRead,
    PaginatedResponse, ErrorResponse
)
from app.security import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    get_token_user_id, get_token_org_id
)
from app.dependencies import get_current_user, get_current_org_id
from app.config import get_settings
import logging

settings = get_settings()
router = APIRouter()
logger = logging.getLogger(__name__)


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@router.get("/health/live", response_model=HealthResponse, tags=["Health"])
async def health_live():
    """Liveness probe - basic health check"""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc),
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )


@router.get("/health/ready", response_model=HealthResponse, tags=["Health"])
async def health_ready(db: AsyncSession = Depends(get_db)):
    """Readiness probe - check database connectivity"""
    try:
        await db.execute(select(1))
        return HealthResponse(
            status="ready",
            timestamp=datetime.now(timezone.utc),
            version=settings.APP_VERSION,
            environment=settings.ENVIRONMENT,
        )
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@router.post("/auth/signup", response_model=TokenResponse, tags=["Auth"])
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create new organization and user"""
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="User already exists")

    # Create organization
    org = Organization(
        name=user_data.org_name or user_data.email.split("@")[0],
        timezone="America/New_York"
    )
    db.add(org)
    await db.flush()

    # Create user
    user = User(
        organization_id=org.id,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role="OWNER"
    )
    db.add(user)
    await db.commit()

    access_token = create_access_token(str(user.id), str(org.id))
    refresh_token = create_refresh_token(str(user.id), str(org.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.model_validate(user)
    )


@router.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return tokens"""
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    access_token = create_access_token(str(user.id), str(user.organization_id))
    refresh_token = create_refresh_token(str(user.id), str(user.organization_id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.model_validate(user)
    )


@router.post("/auth/refresh", response_model=TokenRefreshResponse, tags=["Auth"])
async def refresh_token(token_data: TokenRefresh):
    """Refresh access token"""
    user_id = get_token_user_id(token_data.refresh_token)
    org_id = get_token_org_id(token_data.refresh_token)

    if not user_id or not org_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = create_access_token(user_id, org_id)
    return TokenRefreshResponse(access_token=access_token)


# ============================================================================
# ORGANIZATION ENDPOINTS
# ============================================================================

@router.get("/organizations", response_model=OrganizationRead, tags=["Organizations"])
async def get_organization(
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """Get current organization"""
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return OrganizationRead.model_validate(org)


# ============================================================================
# CRM - CONTACTS ENDPOINTS
# ============================================================================

@router.post("/contacts", response_model=ContactRead, tags=["CRM - Contacts"])
async def create_contact(
    contact_data: ContactCreate,
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new contact"""
    contact = Contact(
        organization_id=org_id,
        **contact_data.model_dump()
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return ContactRead.model_validate(contact)


@router.get("/contacts", response_model=List[ContactRead], tags=["CRM - Contacts"])
async def list_contacts(
    org_id: UUID = Depends(get_current_org_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """List all contacts for organization"""
    result = await db.execute(
        select(Contact)
        .where(Contact.organization_id == org_id)
        .offset(skip)
        .limit(limit)
    )
    contacts = result.scalars().all()
    return [ContactRead.model_validate(c) for c in contacts]


@router.get("/contacts/{contact_id}", response_model=ContactRead, tags=["CRM - Contacts"])
async def get_contact(
    contact_id: UUID,
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """Get contact by ID"""
    result = await db.execute(
        select(Contact).where(
            and_(Contact.id == contact_id, Contact.organization_id == org_id)
        )
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return ContactRead.model_validate(contact)


@router.put("/contacts/{contact_id}", response_model=ContactRead, tags=["CRM - Contacts"])
async def update_contact(
    contact_id: UUID,
    contact_data: ContactUpdate,
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """Update contact"""
    result = await db.execute(
        select(Contact).where(
            and_(Contact.id == contact_id, Contact.organization_id == org_id)
        )
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    for key, value in contact_data.model_dump(exclude_unset=True).items():
        setattr(contact, key, value)

    await db.commit()
    await db.refresh(contact)
    return ContactRead.model_validate(contact)


@router.delete("/contacts/{contact_id}", status_code=204, tags=["CRM - Contacts"])
async def delete_contact(
    contact_id: UUID,
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete contact"""
    result = await db.execute(
        select(Contact).where(
            and_(Contact.id == contact_id, Contact.organization_id == org_id)
        )
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    await db.delete(contact)
    await db.commit()


# ============================================================================
# CRM - COMPANIES ENDPOINTS
# ============================================================================

@router.post("/companies", response_model=CompanyRead, tags=["CRM - Companies"])
async def create_company(
    company_data: CompanyCreate,
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new company"""
    company = Company(organization_id=org_id, **company_data.model_dump())
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return CompanyRead.model_validate(company)


@router.get("/companies", response_model=List[CompanyRead], tags=["CRM - Companies"])
async def list_companies(
    org_id: UUID = Depends(get_current_org_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """List all companies"""
    result = await db.execute(
        select(Company)
        .where(Company.organization_id == org_id)
        .offset(skip)
        .limit(limit)
    )
    return [CompanyRead.model_validate(c) for c in result.scalars().all()]


@router.get("/companies/{company_id}", response_model=CompanyRead, tags=["CRM - Companies"])
async def get_company(
    company_id: UUID,
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """Get company by ID"""
    result = await db.execute(
        select(Company).where(
            and_(Company.id == company_id, Company.organization_id == org_id)
        )
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyRead.model_validate(company)


# ============================================================================
# CRM - DEALS ENDPOINTS
# ============================================================================

@router.post("/deals", response_model=DealRead, tags=["CRM - Deals"])
async def create_deal(
    deal_data: DealCreate,
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new deal"""
    deal = Deal(organization_id=org_id, **deal_data.model_dump())
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return DealRead.model_validate(deal)


@router.get("/deals", response_model=List[DealRead], tags=["CRM - Deals"])
async def list_deals(
    org_id: UUID = Depends(get_current_org_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """List all deals"""
    result = await db.execute(
        select(Deal)
        .where(Deal.organization_id == org_id)
        .offset(skip)
        .limit(limit)
    )
    return [DealRead.model_validate(d) for d in result.scalars().all()]


# ============================================================================
# CRM - ACTIVITIES ENDPOINTS
# ============================================================================

@router.post("/activities", response_model=ActivityRead, tags=["CRM - Activities"])
async def create_activity(
    activity_data: ActivityCreate,
    org_id: UUID = Depends(get_current_org_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new activity"""
    activity = Activity(
        organization_id=org_id,
        created_by=user.id,
        **activity_data.model_dump()
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return ActivityRead.model_validate(activity)


@router.get("/contacts/{contact_id}/activities", response_model=List[ActivityRead], tags=["CRM - Activities"])
async def list_contact_activities(
    contact_id: UUID,
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """List activities for a contact"""
    result = await db.execute(
        select(Activity).where(
            and_(
                Activity.contact_id == contact_id,
                Activity.organization_id == org_id
            )
        )
        .order_by(Activity.created_at.desc())
    )
    return [ActivityRead.model_validate(a) for a in result.scalars().all()]


# ============================================================================
# CONVERSATIONS ENDPOINTS
# ============================================================================

@router.post("/conversations", response_model=ConversationRead, tags=["Conversations"])
async def create_conversation(
    conv_data: ConversationCreate,
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation"""
    conversation = Conversation(organization_id=org_id, **conv_data.model_dump())
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return ConversationRead.model_validate(conversation)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail, tags=["Conversations"])
async def get_conversation(
    conversation_id: UUID,
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """Get conversation with messages"""
    result = await db.execute(
        select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.organization_id == org_id
            )
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_result = await db.execute(
        select(Message).where(Message.conversation_id == conversation_id)
    )
    messages = msg_result.scalars().all()

    conv_data = ConversationRead.model_validate(conversation)
    return ConversationDetail(
        **conv_data.model_dump(),
        messages=[MessageRead.model_validate(m) for m in messages]
    )


@router.post("/conversations/{conversation_id}/messages", response_model=MessageRead, tags=["Conversations"])
async def add_message(
    conversation_id: UUID,
    message_data: MessageCreate,
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """Add message to conversation"""
    # Verify conversation exists and belongs to org
    result = await db.execute(
        select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.organization_id == org_id
            )
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Conversation not found")

    message = Message(
        conversation_id=conversation_id,
        **message_data.model_dump()
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return MessageRead.model_validate(message)


# ============================================================================
# INTEGRATIONS ENDPOINTS
# ============================================================================

@router.post("/integrations", response_model=IntegrationRead, tags=["Integrations"])
async def create_integration(
    integration_data: IntegrationCreate,
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """Create integration configuration"""
    integration = Integration(organization_id=org_id, **integration_data.model_dump())
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    return IntegrationRead.model_validate(integration)


@router.get("/integrations", response_model=List[IntegrationRead], tags=["Integrations"])
async def list_integrations(
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """List all integrations"""
    result = await db.execute(select(Integration).where(Integration.organization_id == org_id))
    return [IntegrationRead.model_validate(i) for i in result.scalars().all()]


# ============================================================================
# WORKFLOWS ENDPOINTS
# ============================================================================

@router.post("/workflows", response_model=WorkflowRead, tags=["Workflows"])
async def create_workflow(
    workflow_data: WorkflowCreate,
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """Create workflow automation"""
    workflow = Workflow(organization_id=org_id, **workflow_data.model_dump())
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    return WorkflowRead.model_validate(workflow)


@router.get("/workflows", response_model=List[WorkflowRead], tags=["Workflows"])
async def list_workflows(
    org_id: UUID = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db)
):
    """List all workflows"""
    result = await db.execute(select(Workflow).where(Workflow.organization_id == org_id))
    return [WorkflowRead.model_validate(w) for w in result.scalars().all()]


# ============================================================================
# API KEYS ENDPOINTS
# ============================================================================

@router.post("/api-keys", response_model=APIKeyRead, tags=["API Keys"])
async def create_api_key(
    key_data: APIKeyCreate,
    org_id: UUID = Depends(get_current_org_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create API key"""
    if user.role not in ["OWNER", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    key_value = f"sk-{uuid4()}"
    key_hash = hash_password(key_value)

    api_key = APIKey(
        organization_id=org_id,
        key_hash=key_hash,
        **key_data.model_dump()
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return APIKeyRead.model_validate(api_key)


@router.get("/api-keys", response_model=List[APIKeyRead], tags=["API Keys"])
async def list_api_keys(
    org_id: UUID = Depends(get_current_org_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List API keys"""
    if user.role not in ["OWNER", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(
        select(APIKey).where(APIKey.organization_id == org_id)
    )
    return [APIKeyRead.model_validate(k) for k in result.scalars().all()]

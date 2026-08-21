"""API routes"""

from datetime import timedelta
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.models import User, Organization
from app.schemas import (
    UserCreate,
    UserLogin,
    TokenResponse,
    TokenRefresh,
    TokenRefreshResponse,
    UserRead,
    OrganizationRead,
    HealthResponse,
)
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_token_user_id,
    get_token_org_id,
)
from app.dependencies import get_current_user, get_current_org_id
from app.config import get_settings
from datetime import datetime, timezone

settings = get_settings()
router = APIRouter()


# ============================================================
# Health Check Endpoints
# ============================================================

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
        # Simple query to verify database is accessible
        await db.execute(select(1))
        return HealthResponse(
            status="ok",
            timestamp=datetime.now(timezone.utc),
            version=settings.APP_VERSION,
            environment=settings.ENVIRONMENT,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unavailable: {str(e)}",
        )


# ============================================================
# Authentication Endpoints
# ============================================================

@router.post("/auth/signup", response_model=TokenResponse, tags=["Auth"])
async def signup(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create new organization and user (signup)"""

    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_create.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create organization
    org = Organization(
        id=uuid4(),
        name=user_create.org_name or user_create.email.split("@")[0],
    )
    db.add(org)

    # Create user (OWNER role for first user)
    user = User(
        id=uuid4(),
        organization_id=org.id,
        email=user_create.email,
        password_hash=hash_password(user_create.password),
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        role="OWNER",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "org_id": str(org.id)}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "org_id": str(org.id)}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.model_validate(user),
    )


@router.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
async def login(user_login: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return tokens"""

    # Find user by email
    result = await db.execute(select(User).where(User.email == user_login.email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not verify_password(user_login.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "org_id": str(user.organization_id)}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "org_id": str(user.organization_id)}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.model_validate(user),
    )


@router.post("/auth/refresh", response_model=TokenRefreshResponse, tags=["Auth"])
async def refresh_token(request: TokenRefresh, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token"""

    user_id = get_token_user_id(request.refresh_token)
    org_id = get_token_org_id(request.refresh_token)

    if not user_id or not org_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Verify user still exists
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new access token
    access_token = create_access_token(
        data={"sub": str(user.id), "org_id": str(org_id)}
    )

    return TokenRefreshResponse(access_token=access_token)


# ============================================================
# Organization Endpoints
# ============================================================

@router.get("/organizations/me", response_model=OrganizationRead, tags=["Organizations"])
async def get_current_organization(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's organization"""
    result = await db.execute(
        select(Organization).where(Organization.id == user.organization_id)
    )
    org = result.scalars().first()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return OrganizationRead.model_validate(org)


# ============================================================
# User Endpoints
# ============================================================

@router.get("/users/me", response_model=UserRead, tags=["Users"])
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserRead.model_validate(user)

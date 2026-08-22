"""Comprehensive authentication and authorization tests"""

import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.models import User, Organization, Session as SessionModel
from app.security import hash_password, create_access_token, create_refresh_token


@pytest.mark.asyncio
async def test_signup_creates_organization_and_user(client: AsyncClient, db_session):
    """Test that signup creates both organization and user"""
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe",
            "org_name": "Test Organization",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["role"] == "OWNER"  # First user should be owner


@pytest.mark.asyncio
async def test_signup_duplicate_email_fails(client: AsyncClient):
    """Test that signup with duplicate email fails"""
    # First signup
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",
        },
    )

    # Second signup with same email
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "password": "DifferentPass123!",
        },
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_signup_weak_password_fails(client: AsyncClient):
    """Test that weak password is rejected"""
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "short",  # Too short
        },
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpass123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, test_user):
    """Test login with invalid credentials"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent user"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "anypassword",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient, test_user):
    """Test successful token refresh"""
    # First login to get refresh token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpass123",
        },
    )
    refresh_token = login_response.json()["refresh_token"]

    # Refresh the token
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_token_invalid(client: AsyncClient):
    """Test refresh with invalid token"""
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user):
    """Test getting current user info"""
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpass123",
        },
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "OWNER"


@pytest.mark.asyncio
async def test_unauthorized_request(client: AsyncClient):
    """Test request without auth token"""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token_format(client: AsyncClient):
    """Test request with malformed token"""
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "InvalidFormat"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_role_hierarchy(client: AsyncClient, test_org, db_session):
    """Test that user roles are respected"""
    # Create users with different roles
    owner = User(
        id=uuid4(),
        organization_id=test_org.id,
        email="owner@example.com",
        password_hash=hash_password("testpass123"),
        role="OWNER",
        is_active=True,
    )
    admin = User(
        id=uuid4(),
        organization_id=test_org.id,
        email="admin@example.com",
        password_hash=hash_password("testpass123"),
        role="ADMIN",
        is_active=True,
    )
    agent = User(
        id=uuid4(),
        organization_id=test_org.id,
        email="agent@example.com",
        password_hash=hash_password("testpass123"),
        role="AGENT",
        is_active=True,
    )
    db_session.add_all([owner, admin, agent])
    await db_session.commit()

    # Test that agent cannot create API keys
    agent_token = create_access_token(str(agent.id), str(test_org.id))
    response = await client.post(
        "/api/v1/api-keys",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={
            "name": "Test API Key",
            "scopes": ["read", "write"],
        },
    )
    assert response.status_code == 403

    # Test that admin can create API keys
    admin_token = create_access_token(str(admin.id), str(test_org.id))
    response = await client.post(
        "/api/v1/api-keys",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test API Key",
            "scopes": ["read", "write"],
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_inactive_user_cannot_login(client: AsyncClient, db_session, test_org):
    """Test that inactive users cannot use their tokens"""
    inactive_user = User(
        id=uuid4(),
        organization_id=test_org.id,
        email="inactive@example.com",
        password_hash=hash_password("testpass123"),
        is_active=False,
    )
    db_session.add(inactive_user)
    await db_session.commit()

    token = create_access_token(str(inactive_user.id), str(test_org.id))
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert "inactive" in response.json()["detail"]


@pytest.mark.asyncio
async def test_token_expiration(client: AsyncClient, test_user, test_org):
    """Test that expired tokens are rejected"""
    from datetime import datetime, timedelta, timezone
    from app.security import create_access_token as create_token
    from jose import jwt
    from app.config import get_settings

    settings = get_settings()

    # Create an expired token
    expired_payload = {
        "sub": str(test_user.id),
        "org_id": str(test_org.id),
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1)  # Expired
    }
    expired_token = jwt.encode(
        expired_payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )

    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_list_requires_auth(client: AsyncClient):
    """Test that user list endpoint requires authentication"""
    response = await client.get("/api/v1/users")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_user_requires_admin(client: AsyncClient, test_user, test_org, db_session):
    """Test that creating users requires admin role"""
    # Create a regular agent user
    agent = User(
        id=uuid4(),
        organization_id=test_org.id,
        email="agent@example.com",
        password_hash=hash_password("testpass123"),
        role="AGENT",
    )
    db_session.add(agent)
    await db_session.commit()

    agent_token = create_access_token(str(agent.id), str(test_org.id))
    response = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
        },
    )
    assert response.status_code == 403

"""API endpoint tests"""

import pytest


@pytest.mark.asyncio
async def test_api_root(client):
    """Test root API endpoint"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["name"] == "AI Platform"


@pytest.mark.asyncio
async def test_health_live(client):
    """Test liveness probe"""
    response = await client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_ready(client):
    """Test readiness probe"""
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_missing_auth_header(client):
    """Test request without auth header"""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_invalid_token(client):
    """Test request with invalid token"""
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_wrong_auth_scheme(client):
    """Test request with wrong auth scheme"""
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Basic dXNlcjpwYXNz"},
    )
    assert response.status_code == 401

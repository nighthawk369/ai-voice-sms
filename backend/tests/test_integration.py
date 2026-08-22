"""Integration tests for the API"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.db import get_db
from app.models import User, Organization
from app.schemas import UserCreate, OrganizationCreate


@pytest.mark.asyncio
async def test_complete_flow():
    """Test complete user flow: signup → login → create organization → create contact"""
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Signup
        signup_response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "testuser@example.com",
                "password": "TestPassword123!",
                "business_type": "hvac_contractor"
            }
        )
        assert signup_response.status_code == 201
        user_data = signup_response.json()
        assert user_data["email"] == "testuser@example.com"
        user_id = user_data["id"]

        # 2. Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "testuser@example.com",
                "password": "TestPassword123!"
            }
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data
        token = login_data["access_token"]

        # 3. Get current user
        me_response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["id"] == user_id
        assert me_data["email"] == "testuser@example.com"
        org_id = me_data["organization_id"]

        # 4. Get organization
        org_response = await client.get(
            f"/api/v1/organizations/{org_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert org_response.status_code == 200
        org_data = org_response.json()
        assert org_data["business_type"] == "hvac_contractor"

        # 5. Create contact
        contact_response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone": "+13125551234"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert contact_response.status_code == 201
        contact_data = contact_response.json()
        contact_id = contact_data["id"]

        # 6. List contacts
        contacts_response = await client.get(
            "/api/v1/contacts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert contacts_response.status_code == 200
        contacts = contacts_response.json()
        assert len(contacts) >= 1
        assert any(c["id"] == contact_id for c in contacts)

        # 7. Get specific contact
        get_contact_response = await client.get(
            f"/api/v1/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_contact_response.status_code == 200
        contact = get_contact_response.json()
        assert contact["first_name"] == "John"
        assert contact["last_name"] == "Doe"

        # 8. Update contact
        update_response = await client.put(
            f"/api/v1/contacts/{contact_id}",
            json={
                "first_name": "Jane",
                "email": "jane@example.com"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["first_name"] == "Jane"

        # 9. Start conversation
        conv_response = await client.post(
            "/api/v1/conversations",
            json={
                "contact_id": contact_id,
                "type": "inbound_call"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert conv_response.status_code == 201
        conv_data = conv_response.json()
        conversation_id = conv_data["id"]

        # 10. Send message
        msg_response = await client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            json={
                "content": "How can I help you?",
                "type": "assistant"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert msg_response.status_code == 201
        msg_data = msg_response.json()
        assert msg_data["content"] == "How can I help you?"

        # 11. Get conversation messages
        msgs_response = await client.get(
            f"/api/v1/conversations/{conversation_id}/messages",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert msgs_response.status_code == 200
        messages = msgs_response.json()
        assert len(messages) >= 1


@pytest.mark.asyncio
async def test_multi_tenancy_isolation():
    """Test that users can't access other organization's data"""
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create user 1
        user1_signup = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "user1@example.com",
                "password": "TestPassword123!",
                "business_type": "hvac_contractor"
            }
        )
        user1_token = (await client.post(
            "/api/v1/auth/login",
            json={"email": "user1@example.com", "password": "TestPassword123!"}
        )).json()["access_token"]

        # Create contact in org 1
        contact1 = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "Contact1",
                "email": "contact1@example.com",
                "phone": "+13125551111"
            },
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        contact1_id = contact1.json()["id"]

        # Create user 2
        user2_signup = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "user2@example.com",
                "password": "TestPassword123!",
                "business_type": "electrician"
            }
        )
        user2_token = (await client.post(
            "/api/v1/auth/login",
            json={"email": "user2@example.com", "password": "TestPassword123!"}
        )).json()["access_token"]

        # User 2 should NOT see user 1's contact
        contacts2 = await client.get(
            "/api/v1/contacts",
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        contacts2_data = contacts2.json()
        assert not any(c["id"] == contact1_id for c in contacts2_data)

        # User 2 should NOT be able to get user 1's contact by ID
        forbidden_response = await client.get(
            f"/api/v1/contacts/{contact1_id}",
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        assert forbidden_response.status_code == 404


@pytest.mark.asyncio
async def test_business_type_flow():
    """Test business type selection and configuration"""
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Get all business types
        bt_response = await client.get("/api/v1/business-types")
        assert bt_response.status_code == 200
        bt_data = bt_response.json()
        assert "business_types" in bt_data
        assert len(bt_data["business_types"]) > 0
        assert "categories" in bt_data

        # Get specific business type config
        hvac_response = await client.get("/api/v1/business-types/hvac_contractor")
        assert hvac_response.status_code == 200
        hvac_data = hvac_response.json()
        assert hvac_data["business_type"] == "hvac_contractor"
        assert "system_prompt" in hvac_data
        assert "features" in hvac_data
        assert "custom_fields" in hvac_data

        # Create user with that business type
        signup = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "hvac@example.com",
                "password": "TestPassword123!",
                "business_type": "hvac_contractor"
            }
        )
        assert signup.status_code == 201
        user_data = signup.json()
        assert user_data["business_type"] == "hvac_contractor"


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling and validation"""
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Invalid email
        invalid_email = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "not-an-email",
                "password": "TestPassword123!",
                "business_type": "hvac_contractor"
            }
        )
        assert invalid_email.status_code in [400, 422]

        # Weak password
        weak_password = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "weak",
                "business_type": "hvac_contractor"
            }
        )
        assert weak_password.status_code in [400, 422]

        # Missing required fields
        missing_fields = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com"
            }
        )
        assert missing_fields.status_code in [400, 422]

        # Login with wrong password
        await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "existing@example.com",
                "password": "CorrectPassword123!",
                "business_type": "hvac_contractor"
            }
        )
        
        wrong_password = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "existing@example.com",
                "password": "WrongPassword123!"
            }
        )
        assert wrong_password.status_code == 401

        # Access protected endpoint without token
        no_token = await client.get("/api/v1/users/me")
        assert no_token.status_code == 401

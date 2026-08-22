"""Housecall Pro API Client"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import aiohttp

from app.integrations.base import CRMClient, OAuthProvider, OAuthToken

logger = logging.getLogger(__name__)


class HousecallProOAuthProvider(OAuthProvider):
    """Housecall Pro OAuth 2.0 provider"""

    @property
    def authorization_url(self) -> str:
        return "https://api.housecallpro.com/oauth/authorize"

    @property
    def token_url(self) -> str:
        return "https://api.housecallpro.com/oauth/token"

    @property
    def api_base_url(self) -> str:
        return "https://api.housecallpro.com/v1"

    async def get_authorization_url(self, state: str, scopes: List[str]) -> str:
        """Get authorization URL for user"""
        scope_str = " ".join(scopes)
        return (
            f"{self.authorization_url}?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"response_type=code&"
            f"scope={scope_str}&"
            f"state={state}"
        )

    async def exchange_code_for_token(self, code: str, state: str) -> OAuthToken:
        """Exchange authorization code for access token"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                },
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"OAuth token exchange failed: {resp.status}")
                data = await resp.json()

                expires_at = None
                if "expires_in" in data:
                    expires_at = datetime.utcnow() + timedelta(seconds=data["expires_in"])

                return OAuthToken(
                    access_token=data["access_token"],
                    refresh_token=data.get("refresh_token"),
                    expires_at=expires_at,
                    token_type=data.get("token_type", "Bearer"),
                    scope=data.get("scope", ""),
                )

    async def refresh_access_token(self, refresh_token: str) -> OAuthToken:
        """Refresh access token"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.token_url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"Token refresh failed: {resp.status}")
                data = await resp.json()

                expires_at = None
                if "expires_in" in data:
                    expires_at = datetime.utcnow() + timedelta(seconds=data["expires_in"])

                return OAuthToken(
                    access_token=data["access_token"],
                    refresh_token=data.get("refresh_token", refresh_token),
                    expires_at=expires_at,
                    token_type=data.get("token_type", "Bearer"),
                    scope=data.get("scope", ""),
                )


class HousecallProClient(CRMClient):
    """Housecall Pro REST API client"""

    def __init__(self, access_token: str, base_url: str = "https://api.housecallpro.com/v1"):
        super().__init__(base_url, access_token)

    async def get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "CRM-Integration/1.0",
        }

    async def test_connection(self) -> bool:
        """Test connection to Housecall Pro API"""
        try:
            await self.get("/me")
            return True
        except Exception as e:
            logger.error(f"Housecall Pro connection test failed: {str(e)}")
            return False

    # ========================================================================
    # CUSTOMER ENDPOINTS
    # ========================================================================

    async def list_customers(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List customers"""
        params = {
            "offset": skip,
            "limit": min(limit, 100),
        }
        return await self.get("/customers", params=params)

    async def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Get single customer"""
        return await self.get(f"/customers/{customer_id}")

    async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create customer"""
        return await self.post("/customers", json=customer_data)

    async def update_customer(
        self,
        customer_id: str,
        customer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update customer"""
        return await self.put(f"/customers/{customer_id}", json=customer_data)

    async def delete_customer(self, customer_id: str) -> bool:
        """Delete customer"""
        try:
            await self.delete(f"/customers/{customer_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete customer: {str(e)}")
            return False

    # ========================================================================
    # JOB ENDPOINTS
    # ========================================================================

    async def list_jobs(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """List jobs"""
        params = {
            "offset": skip,
            "limit": min(limit, 100),
        }
        if status:
            params["status"] = status

        return await self.get("/jobs", params=params)

    async def get_job(self, job_id: str) -> Dict[str, Any]:
        """Get single job"""
        return await self.get(f"/jobs/{job_id}")

    async def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create job"""
        return await self.post("/jobs", json=job_data)

    async def update_job(self, job_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update job"""
        return await self.put(f"/jobs/{job_id}", json=job_data)

    async def close_job(self, job_id: str) -> bool:
        """Close job"""
        try:
            await self.post(f"/jobs/{job_id}/close")
            return True
        except Exception as e:
            logger.error(f"Failed to close job: {str(e)}")
            return False

    # ========================================================================
    # WEBHOOK ENDPOINTS
    # ========================================================================

    async def register_webhook(
        self,
        url: str,
        events: List[str]
    ) -> Dict[str, Any]:
        """Register webhook"""
        payload = {
            "url": url,
            "events": events,
        }
        return await self.post("/webhooks", json=payload)

    async def list_webhooks(self) -> Dict[str, Any]:
        """List registered webhooks"""
        return await self.get("/webhooks")

    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete webhook"""
        try:
            await self.delete(f"/webhooks/{webhook_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete webhook: {str(e)}")
            return False

    # ========================================================================
    # APPOINTMENT ENDPOINTS
    # ========================================================================

    async def list_appointments(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List appointments"""
        params = {
            "offset": skip,
            "limit": min(limit, 100),
        }
        return await self.get("/appointments", params=params)

    async def get_appointment(self, appointment_id: str) -> Dict[str, Any]:
        """Get single appointment"""
        return await self.get(f"/appointments/{appointment_id}")

    async def create_appointment(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create appointment"""
        return await self.post("/appointments", json=appointment_data)

    async def update_appointment(
        self,
        appointment_id: str,
        appointment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update appointment"""
        return await self.put(f"/appointments/{appointment_id}", json=appointment_data)

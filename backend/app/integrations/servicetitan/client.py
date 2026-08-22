"""ServiceTitan API Client"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import aiohttp

from app.integrations.base import CRMClient, OAuthProvider, OAuthToken

logger = logging.getLogger(__name__)


class ServiceTitanOAuthProvider(OAuthProvider):
    """ServiceTitan OAuth 2.0 provider"""

    @property
    def authorization_url(self) -> str:
        return "https://authorization.servicetitan.com/connect/authorize"

    @property
    def token_url(self) -> str:
        return "https://authorization.servicetitan.com/connect/token"

    @property
    def api_base_url(self) -> str:
        return "https://api.servicetitan.com/v2"

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


class ServiceTitanClient(CRMClient):
    """ServiceTitan API client"""

    def __init__(
        self,
        access_token: str,
        tenant_id: Optional[str] = None,
        base_url: str = "https://api.servicetitan.com/v2"
    ):
        super().__init__(base_url, access_token)
        self.tenant_id = tenant_id

    async def get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        if self.tenant_id:
            headers["X-Tenant-ID"] = self.tenant_id
        return headers

    async def test_connection(self) -> bool:
        """Test connection to ServiceTitan API"""
        try:
            await self.get("/crm/customers?limit=1")
            return True
        except Exception as e:
            logger.error(f"ServiceTitan connection test failed: {str(e)}")
            return False

    # ========================================================================
    # CUSTOMER ENDPOINTS
    # ========================================================================

    async def list_customers(
        self,
        skip: int = 0,
        limit: int = 100,
        modified_after: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """List customers"""
        params = {
            "offset": skip,
            "limit": min(limit, 100),  # ST has max 100
        }
        if modified_after:
            params["modifiedDateFrom"] = modified_after.isoformat()

        return await self.get("/crm/customers", params=params)

    async def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Get single customer"""
        return await self.get(f"/crm/customers/{customer_id}")

    async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create customer"""
        return await self.post("/crm/customers", json=customer_data)

    async def update_customer(
        self,
        customer_id: str,
        customer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update customer"""
        return await self.put(f"/crm/customers/{customer_id}", json=customer_data)

    async def delete_customer(self, customer_id: str) -> bool:
        """Delete customer"""
        try:
            await self.delete(f"/crm/customers/{customer_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete customer: {str(e)}")
            return False

    # ========================================================================
    # JOB ENDPOINTS (equivalent to deals)
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

        return await self.get("/crm/jobs", params=params)

    async def get_job(self, job_id: str) -> Dict[str, Any]:
        """Get single job"""
        return await self.get(f"/crm/jobs/{job_id}")

    async def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create job"""
        return await self.post("/crm/jobs", json=job_data)

    async def update_job(self, job_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update job"""
        return await self.put(f"/crm/jobs/{job_id}", json=job_data)

    # ========================================================================
    # TECHNICIAN ENDPOINTS
    # ========================================================================

    async def list_technicians(self) -> Dict[str, Any]:
        """List technicians"""
        return await self.get("/crm/technicians")

    async def get_technician(self, technician_id: str) -> Dict[str, Any]:
        """Get single technician"""
        return await self.get(f"/crm/technicians/{technician_id}")

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

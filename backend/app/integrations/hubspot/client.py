"""HubSpot API Client"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import aiohttp

from app.integrations.base import CRMClient, OAuthProvider, OAuthToken

logger = logging.getLogger(__name__)


class HubSpotOAuthProvider(OAuthProvider):
    """HubSpot OAuth 2.0 provider"""

    @property
    def authorization_url(self) -> str:
        return "https://app.hubspot.com/oauth/authorize"

    @property
    def token_url(self) -> str:
        return "https://api.hubapi.com/oauth/v1/token"

    @property
    def api_base_url(self) -> str:
        return "https://api.hubapi.com"

    async def get_authorization_url(self, state: str, scopes: List[str]) -> str:
        """Get authorization URL for user"""
        scope_str=" ".join(scopes)
        return (
            f"{self.authorization_url}?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
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


class HubSpotClient(CRMClient):
    """HubSpot REST API client"""

    def __init__(self, access_token: str, base_url: str = "https://api.hubapi.com"):
        super().__init__(base_url, access_token)

    async def get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "CRM-Integration/1.0",
        }

    async def test_connection(self) -> bool:
        """Test connection to HubSpot API"""
        try:
            await self.get("/crm/v3/objects/contacts?limit=1")
            return True
        except Exception as e:
            logger.error(f"HubSpot connection test failed: {str(e)}")
            return False

    # ========================================================================
    # CONTACT ENDPOINTS
    # ========================================================================

    async def list_contacts(
        self,
        skip: int = 0,
        limit: int = 100,
        properties: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List contacts"""
        params = {
            "limit": min(limit, 100),
            "after": skip,
        }
        if properties:
            params["properties"] = properties

        return await self.get("/crm/v3/objects/contacts", params=params)

    async def get_contact(self, contact_id: str, properties: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get single contact"""
        params = {}
        if properties:
            params["properties"] = properties
        return await self.get(f"/crm/v3/objects/contacts/{contact_id}", params=params)

    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact"""
        payload = {"properties": contact_data}
        return await self.post("/crm/v3/objects/contacts", json=payload)

    async def update_contact(
        self,
        contact_id: str,
        contact_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update contact"""
        payload = {"properties": contact_data}
        return await self.patch(f"/crm/v3/objects/contacts/{contact_id}", json=payload)

    async def delete_contact(self, contact_id: str) -> bool:
        """Delete contact"""
        try:
            await self.delete(f"/crm/v3/objects/contacts/{contact_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete contact: {str(e)}")
            return False

    # ========================================================================
    # COMPANY ENDPOINTS
    # ========================================================================

    async def list_companies(
        self,
        skip: int = 0,
        limit: int = 100,
        properties: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List companies"""
        params = {
            "limit": min(limit, 100),
            "after": skip,
        }
        if properties:
            params["properties"] = properties

        return await self.get("/crm/v3/objects/companies", params=params)

    async def get_company(self, company_id: str, properties: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get single company"""
        params = {}
        if properties:
            params["properties"] = properties
        return await self.get(f"/crm/v3/objects/companies/{company_id}", params=params)

    async def create_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create company"""
        payload = {"properties": company_data}
        return await self.post("/crm/v3/objects/companies", json=payload)

    async def update_company(
        self,
        company_id: str,
        company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update company"""
        payload = {"properties": company_data}
        return await self.patch(f"/crm/v3/objects/companies/{company_id}", json=payload)

    # ========================================================================
    # DEAL ENDPOINTS
    # ========================================================================

    async def list_deals(
        self,
        skip: int = 0,
        limit: int = 100,
        properties: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List deals"""
        params = {
            "limit": min(limit, 100),
            "after": skip,
        }
        if properties:
            params["properties"] = properties

        return await self.get("/crm/v3/objects/deals", params=params)

    async def get_deal(self, deal_id: str, properties: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get single deal"""
        params = {}
        if properties:
            params["properties"] = properties
        return await self.get(f"/crm/v3/objects/deals/{deal_id}", params=params)

    async def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create deal"""
        payload = {"properties": deal_data}
        return await self.post("/crm/v3/objects/deals", json=payload)

    async def update_deal(self, deal_id: str, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update deal"""
        payload = {"properties": deal_data}
        return await self.patch(f"/crm/v3/objects/deals/{deal_id}", json=payload)

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
            "targetUrl": url,
            "subscriptionDetails": {
                "subscriptionType": events,
            },
        }
        return await self.post("/crm/v3/webhooks", json=payload)

    async def list_webhooks(self) -> Dict[str, Any]:
        """List webhooks"""
        return await self.get("/crm/v3/webhooks")

    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete webhook"""
        try:
            await self.delete(f"/crm/v3/webhooks/{webhook_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete webhook: {str(e)}")
            return False

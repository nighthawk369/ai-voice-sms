"""Salesforce API Client"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import aiohttp

from app.integrations.base import CRMClient, OAuthProvider, OAuthToken

logger = logging.getLogger(__name__)


class SalesforceOAuthProvider(OAuthProvider):
    """Salesforce OAuth 2.0 provider"""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        instance_url: str = "https://login.salesforce.com"
    ):
        super().__init__(client_id, client_secret, redirect_uri)
        self.instance_url = instance_url

    @property
    def authorization_url(self) -> str:
        return f"{self.instance_url}/services/oauth2/authorize"

    @property
    def token_url(self) -> str:
        return f"{self.instance_url}/services/oauth2/token"

    @property
    def api_base_url(self) -> str:
        return f"{self.instance_url}/services/data/v60.0"

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


class SalesforceClient(CRMClient):
    """Salesforce REST API client"""

    def __init__(
        self,
        access_token: str,
        instance_url: str = "https://login.salesforce.com",
        base_url: str = "/services/data/v60.0"
    ):
        # Combine instance URL with API path
        full_url = f"{instance_url.rstrip('/')}{base_url}"
        super().__init__(full_url, access_token)
        self.instance_url = instance_url

    async def get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "CRM-Integration/1.0",
        }

    async def test_connection(self) -> bool:
        """Test connection to Salesforce API"""
        try:
            await self.get("/sobjects")
            return True
        except Exception as e:
            logger.error(f"Salesforce connection test failed: {str(e)}")
            return False

    # ========================================================================
    # CONTACT ENDPOINTS (Lead & Contact)
    # ========================================================================

    async def list_contacts(
        self,
        skip: int = 0,
        limit: int = 100,
        soql: Optional[str] = None
    ) -> Dict[str, Any]:
        """List contacts"""
        if soql:
            params = {"q": soql}
            return await self.get("/query", params=params)
        else:
            params = {
                "q": f"SELECT Id, FirstName, LastName, Email, Phone, BillingStreet, BillingCity, BillingState, BillingPostalCode FROM Contact LIMIT {limit} OFFSET {skip}"
            }
            return await self.get("/query", params=params)

    async def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """Get single contact"""
        return await self.get(f"/sobjects/Contact/{contact_id}")

    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact"""
        return await self.post("/sobjects/Contact", json=contact_data)

    async def update_contact(
        self,
        contact_id: str,
        contact_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update contact"""
        return await self.patch(f"/sobjects/Contact/{contact_id}", json=contact_data)

    async def delete_contact(self, contact_id: str) -> bool:
        """Delete contact"""
        try:
            await self.delete(f"/sobjects/Contact/{contact_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete contact: {str(e)}")
            return False

    # ========================================================================
    # ACCOUNT ENDPOINTS (Company)
    # ========================================================================

    async def list_accounts(
        self,
        skip: int = 0,
        limit: int = 100,
        soql: Optional[str] = None
    ) -> Dict[str, Any]:
        """List accounts (companies)"""
        if soql:
            params = {"q": soql}
            return await self.get("/query", params=params)
        else:
            params = {
                "q": f"SELECT Id, Name, BillingStreet, BillingCity, BillingState, BillingPostalCode, Phone, Website FROM Account LIMIT {limit} OFFSET {skip}"
            }
            return await self.get("/query", params=params)

    async def get_account(self, account_id: str) -> Dict[str, Any]:
        """Get single account"""
        return await self.get(f"/sobjects/Account/{account_id}")

    async def create_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create account"""
        return await self.post("/sobjects/Account", json=account_data)

    async def update_account(
        self,
        account_id: str,
        account_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update account"""
        return await self.patch(f"/sobjects/Account/{account_id}", json=account_data)

    # ========================================================================
    # OPPORTUNITY ENDPOINTS (Deal)
    # ========================================================================

    async def list_opportunities(
        self,
        skip: int = 0,
        limit: int = 100,
        soql: Optional[str] = None
    ) -> Dict[str, Any]:
        """List opportunities (deals)"""
        if soql:
            params = {"q": soql}
            return await self.get("/query", params=params)
        else:
            params = {
                "q": f"SELECT Id, Name, Amount, StageName, CloseDate, AccountId FROM Opportunity LIMIT {limit} OFFSET {skip}"
            }
            return await self.get("/query", params=params)

    async def get_opportunity(self, opportunity_id: str) -> Dict[str, Any]:
        """Get single opportunity"""
        return await self.get(f"/sobjects/Opportunity/{opportunity_id}")

    async def create_opportunity(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create opportunity"""
        return await self.post("/sobjects/Opportunity", json=opportunity_data)

    async def update_opportunity(
        self,
        opportunity_id: str,
        opportunity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update opportunity"""
        return await self.patch(f"/sobjects/Opportunity/{opportunity_id}", json=opportunity_data)

    # ========================================================================
    # WEBHOOK ENDPOINTS
    # ========================================================================

    async def register_webhook(
        self,
        name: str,
        url: str,
        events: List[str]
    ) -> Dict[str, Any]:
        """Register platform event subscription (webhook-like)"""
        payload = {
            "Name": name,
            "Url": url,
            "Events": events,
        }
        return await self.post("/sobjects/PushTopic", json=payload)

    async def list_webhooks(self) -> Dict[str, Any]:
        """List platform event subscriptions"""
        params = {"q": "SELECT Id, Name, Url, Events FROM PushTopic"}
        return await self.get("/query", params=params)

    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete platform event subscription"""
        try:
            await self.delete(f"/sobjects/PushTopic/{webhook_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete webhook: {str(e)}")
            return False

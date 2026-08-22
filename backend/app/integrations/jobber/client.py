"""Jobber API Client"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import aiohttp

from app.integrations.base import CRMClient, OAuthProvider, OAuthToken

logger = logging.getLogger(__name__)


class JobberOAuthProvider(OAuthProvider):
    """Jobber OAuth 2.0 provider"""

    @property
    def authorization_url(self) -> str:
        return "https://api.getjobber.com/oauth/authorize"

    @property
    def token_url(self) -> str:
        return "https://api.getjobber.com/oauth/token"

    @property
    def api_base_url(self) -> str:
        return "https://api.getjobber.com"

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


class JobberClient(CRMClient):
    """Jobber GraphQL API client"""

    def __init__(self, access_token: str, base_url: str = "https://api.getjobber.com"):
        super().__init__(base_url, access_token)

    async def get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "CRM-Integration/1.0",
        }

    async def graphql_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute GraphQL query"""
        payload = {
            "query": query,
            "variables": variables or {},
        }
        return await self.post("/graphql", json=payload)

    async def test_connection(self) -> bool:
        """Test connection to Jobber API"""
        try:
            query = """
            query {
              viewer {
                user {
                  id
                  email
                }
              }
            }
            """
            await self.graphql_query(query)
            return True
        except Exception as e:
            logger.error(f"Jobber connection test failed: {str(e)}")
            return False

    # ========================================================================
    # CLIENT ENDPOINTS
    # ========================================================================

    async def list_clients(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List clients"""
        query = """
        query ListClients($first: Int!, $after: String) {
          clients(first: $first, after: $after) {
            edges {
              node {
                id
                fullName
                firstName
                lastName
                email
                mobile
                address
                city
                province
                postalCode
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
        """
        variables = {"first": min(limit, 100)}
        return await self.graphql_query(query, variables)

    async def get_client(self, client_id: str) -> Dict[str, Any]:
        """Get single client"""
        query = """
        query GetClient($id: ID!) {
          client(id: $id) {
            id
            fullName
            firstName
            lastName
            email
            mobile
            address
            city
            province
            postalCode
          }
        }
        """
        return await self.graphql_query(query, {"id": client_id})

    async def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create client"""
        mutation = """
        mutation CreateClient($input: ClientInput!) {
          clientCreate(input: $input) {
            client {
              id
              fullName
              email
              mobile
            }
            errors {
              field
              message
            }
          }
        }
        """
        return await self.graphql_query(mutation, {"input": client_data})

    async def update_client(self, client_id: str, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update client"""
        mutation = """
        mutation UpdateClient($id: ID!, $input: ClientInput!) {
          clientUpdate(id: $id, input: $input) {
            client {
              id
              fullName
              email
            }
            errors {
              field
              message
            }
          }
        }
        """
        return await self.graphql_query(
            mutation,
            {"id": client_id, "input": client_data}
        )

    async def delete_client(self, client_id: str) -> bool:
        """Delete client"""
        try:
            mutation = """
            mutation DeleteClient($id: ID!) {
              clientDelete(id: $id) {
                success
              }
            }
            """
            await self.graphql_query(mutation, {"id": client_id})
            return True
        except Exception as e:
            logger.error(f"Failed to delete client: {str(e)}")
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
        query = """
        query ListJobs($first: Int!, $after: String, $filter: JobFilter) {
          jobs(first: $first, after: $after, filter: $filter) {
            edges {
              node {
                id
                jobNumber
                title
                client {
                  id
                  fullName
                }
                status
                totalPrice
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
        """
        variables = {"first": min(limit, 100)}
        if status:
            variables["filter"] = {"status": status}
        return await self.graphql_query(query, variables)

    async def get_job(self, job_id: str) -> Dict[str, Any]:
        """Get single job"""
        query = """
        query GetJob($id: ID!) {
          job(id: $id) {
            id
            jobNumber
            title
            status
            totalPrice
            client {
              id
              fullName
            }
          }
        }
        """
        return await self.graphql_query(query, {"id": job_id})

    async def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create job"""
        mutation = """
        mutation CreateJob($input: JobInput!) {
          jobCreate(input: $input) {
            job {
              id
              jobNumber
              title
              status
            }
            errors {
              field
              message
            }
          }
        }
        """
        return await self.graphql_query(mutation, {"input": job_data})

    async def update_job(self, job_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update job"""
        mutation = """
        mutation UpdateJob($id: ID!, $input: JobInput!) {
          jobUpdate(id: $id, input: $input) {
            job {
              id
              title
              status
            }
            errors {
              field
              message
            }
          }
        }
        """
        return await self.graphql_query(
            mutation,
            {"id": job_id, "input": job_data}
        )

    # ========================================================================
    # WEBHOOK ENDPOINTS
    # ========================================================================

    async def register_webhook(
        self,
        url: str,
        events: List[str]
    ) -> Dict[str, Any]:
        """Register webhook"""
        mutation = """
        mutation RegisterWebhook($input: WebhookInput!) {
          webhookCreate(input: $input) {
            webhook {
              id
              url
              events
            }
            errors {
              field
              message
            }
          }
        }
        """
        payload = {"url": url, "events": events}
        return await self.graphql_query(mutation, {"input": payload})

    async def list_webhooks(self) -> Dict[str, Any]:
        """List webhooks"""
        query = """
        query {
          webhooks {
            id
            url
            events
          }
        }
        """
        return await self.graphql_query(query)

    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete webhook"""
        try:
            mutation = """
            mutation DeleteWebhook($id: ID!) {
              webhookDelete(id: $id) {
                success
              }
            }
            """
            await self.graphql_query(mutation, {"id": webhook_id})
            return True
        except Exception as e:
            logger.error(f"Failed to delete webhook: {str(e)}")
            return False

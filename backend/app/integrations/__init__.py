"""CRM Integration Framework - Third-party CRM integrations with in-house CRM sync"""

from .base import (
    CRMAdapter,
    CRMClient,
    FieldMapper,
    SyncEngine,
    WebhookHandler,
    OAuthProvider,
)
from .servicetitan import ServiceTitanAdapter, ServiceTitanClient
from .jobber import JobberAdapter, JobberClient
from .housecall_pro import HousecallProAdapter, HousecallProClient
from .hubspot import HubSpotAdapter, HubSpotClient
from .salesforce import SalesforceAdapter, SalesforceClient

__all__ = [
    "CRMAdapter",
    "CRMClient",
    "FieldMapper",
    "SyncEngine",
    "WebhookHandler",
    "OAuthProvider",
    "ServiceTitanAdapter",
    "ServiceTitanClient",
    "JobberAdapter",
    "JobberClient",
    "HousecallProAdapter",
    "HousecallProClient",
    "HubSpotAdapter",
    "HubSpotClient",
    "SalesforceAdapter",
    "SalesforceClient",
]

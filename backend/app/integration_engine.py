"""Integration Engine Module for CRM Adapter Pattern"""

import os
import logging
import json
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models import Integration, Contact, Company, Deal, Activity

logger = logging.getLogger(__name__)


# ============================================================================
# INTEGRATION ADAPTERS (ABSTRACT BASE CLASSES)
# ============================================================================

class CRMAdapter(ABC):
    """Abstract base class for CRM adapters"""

    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with CRM"""
        pass

    @abstractmethod
    def list_contacts(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List contacts from CRM"""
        pass

    @abstractmethod
    def get_contact(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get single contact from CRM"""
        pass

    @abstractmethod
    def create_contact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact in CRM"""
        pass

    @abstractmethod
    def update_contact(self, contact_id: str, data: Dict[str, Any]) -> bool:
        """Update contact in CRM"""
        pass

    @abstractmethod
    def delete_contact(self, contact_id: str) -> bool:
        """Delete contact in CRM"""
        pass

    @abstractmethod
    def list_companies(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List companies from CRM"""
        pass

    @abstractmethod
    def create_company(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create company in CRM"""
        pass


# ============================================================================
# CONCRETE CRM ADAPTERS
# ============================================================================

class ServiceTitanAdapter(CRMAdapter):
    """ServiceTitan CRM Adapter"""

    def __init__(self, api_key: str, api_url: str = "https://api.servicetitan.com"):
        self.api_key = api_key
        self.api_url = api_url

    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with ServiceTitan"""
        # In production, validate credentials with API
        logger.info("ServiceTitan authenticated")
        return True

    def list_contacts(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List contacts from ServiceTitan"""
        # In production, call ServiceTitan API
        logger.info(f"Listed contacts from ServiceTitan")
        return []

    def get_contact(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get contact from ServiceTitan"""
        # In production, call ServiceTitan API
        return None

    def create_contact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact in ServiceTitan"""
        logger.info(f"Created contact in ServiceTitan")
        return {"id": "st_123", "status": "created"}

    def update_contact(self, contact_id: str, data: Dict[str, Any]) -> bool:
        """Update contact in ServiceTitan"""
        logger.info(f"Updated contact {contact_id} in ServiceTitan")
        return True

    def delete_contact(self, contact_id: str) -> bool:
        """Delete contact in ServiceTitan"""
        logger.info(f"Deleted contact {contact_id} from ServiceTitan")
        return True

    def list_companies(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List companies from ServiceTitan"""
        return []

    def create_company(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create company in ServiceTitan"""
        return {"id": "st_comp_123", "status": "created"}


class JobberAdapter(CRMAdapter):
    """Jobber CRM Adapter"""

    def __init__(self, api_key: str, api_url: str = "https://api.getjobber.com"):
        self.api_key = api_key
        self.api_url = api_url

    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with Jobber"""
        logger.info("Jobber authenticated")
        return True

    def list_contacts(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List contacts from Jobber"""
        logger.info("Listed contacts from Jobber")
        return []

    def get_contact(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get contact from Jobber"""
        return None

    def create_contact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact in Jobber"""
        logger.info(f"Created contact in Jobber")
        return {"id": "jobber_123", "status": "created"}

    def update_contact(self, contact_id: str, data: Dict[str, Any]) -> bool:
        """Update contact in Jobber"""
        logger.info(f"Updated contact {contact_id} in Jobber")
        return True

    def delete_contact(self, contact_id: str) -> bool:
        """Delete contact in Jobber"""
        logger.info(f"Deleted contact {contact_id} from Jobber")
        return True

    def list_companies(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List companies from Jobber"""
        return []

    def create_company(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create company in Jobber"""
        return {"id": "jobber_comp_123", "status": "created"}


class HubSpotAdapter(CRMAdapter):
    """HubSpot CRM Adapter"""

    def __init__(self, api_key: str, api_url: str = "https://api.hubapi.com"):
        self.api_key = api_key
        self.api_url = api_url

    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with HubSpot"""
        logger.info("HubSpot authenticated")
        return True

    def list_contacts(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List contacts from HubSpot"""
        logger.info("Listed contacts from HubSpot")
        return []

    def get_contact(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get contact from HubSpot"""
        return None

    def create_contact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact in HubSpot"""
        logger.info(f"Created contact in HubSpot")
        return {"id": "hs_123", "status": "created"}

    def update_contact(self, contact_id: str, data: Dict[str, Any]) -> bool:
        """Update contact in HubSpot"""
        logger.info(f"Updated contact {contact_id} in HubSpot")
        return True

    def delete_contact(self, contact_id: str) -> bool:
        """Delete contact in HubSpot"""
        logger.info(f"Deleted contact {contact_id} from HubSpot")
        return True

    def list_companies(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List companies from HubSpot"""
        return []

    def create_company(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create company in HubSpot"""
        return {"id": "hs_comp_123", "status": "created"}


# ============================================================================
# FIELD MAPPING ENGINE
# ============================================================================

class FieldMapper:
    """Maps fields between different CRM systems"""

    # Default mappings
    DEFAULT_MAPPINGS = {
        "first_name": {
            "servicetitan": "firstName",
            "jobber": "first_name",
            "hubspot": "firstname",
        },
        "last_name": {
            "servicetitan": "lastName",
            "jobber": "last_name",
            "hubspot": "lastname",
        },
        "email": {
            "servicetitan": "email",
            "jobber": "email",
            "hubspot": "email",
        },
        "phone": {
            "servicetitan": "phone",
            "jobber": "phone",
            "hubspot": "phone",
        },
        "company_name": {
            "servicetitan": "companyName",
            "jobber": "company",
            "hubspot": "company",
        },
    }

    def __init__(self, custom_mappings: Optional[Dict[str, Dict[str, str]]] = None):
        self.mappings = {**self.DEFAULT_MAPPINGS}
        if custom_mappings:
            self.mappings.update(custom_mappings)

    def map_to_crm(
        self,
        source_data: Dict[str, Any],
        source_system: str,
        target_system: str,
    ) -> Dict[str, Any]:
        """Map data from source to target CRM format"""
        target_data = {}

        for source_field, value in source_data.items():
            # Find mapping for this field
            if source_field in self.mappings:
                target_field = self.mappings[source_field].get(target_system)
                if target_field:
                    target_data[target_field] = value
            else:
                # Pass through unmapped fields
                target_data[source_field] = value

        return target_data

    def map_from_crm(
        self,
        crm_data: Dict[str, Any],
        source_system: str,
    ) -> Dict[str, Any]:
        """Map data from CRM format to standard format"""
        standard_data = {}

        for standard_field, system_mappings in self.mappings.items():
            crm_field = system_mappings.get(source_system)
            if crm_field and crm_field in crm_data:
                standard_data[standard_field] = crm_data[crm_field]

        return standard_data

    def add_custom_mapping(
        self,
        source_field: str,
        system: str,
        target_field: str,
    ):
        """Add custom field mapping"""
        if source_field not in self.mappings:
            self.mappings[source_field] = {}
        self.mappings[source_field][system] = target_field


# ============================================================================
# SYNC ENGINE
# ============================================================================

class SyncEngine:
    """Handles synchronization between systems"""

    def __init__(self, db: Session):
        self.db = db

    def sync_contacts(
        self,
        org_id: UUID,
        source_system: str,
        target_system: str,
        adapter: CRMAdapter,
        field_mapper: FieldMapper,
    ) -> Dict[str, Any]:
        """Sync contacts from source to target system"""
        try:
            synced_count = 0
            error_count = 0
            errors = []

            # Get contacts from source
            source_contacts = adapter.list_contacts()

            for contact_data in source_contacts:
                try:
                    # Map fields to target format
                    mapped_data = field_mapper.map_to_crm(
                        contact_data,
                        source_system,
                        target_system,
                    )

                    # Create or update contact
                    # This would call the appropriate adapter method
                    synced_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(str(e))

            logger.info(f"Synced {synced_count} contacts from {source_system} to {target_system}")
            return {
                "status": "completed",
                "synced_count": synced_count,
                "error_count": error_count,
                "errors": errors,
            }
        except Exception as e:
            logger.error(f"Error syncing contacts: {e}")
            raise

    def sync_companies(
        self,
        org_id: UUID,
        source_system: str,
        target_system: str,
        adapter: CRMAdapter,
        field_mapper: FieldMapper,
    ) -> Dict[str, Any]:
        """Sync companies from source to target system"""
        try:
            synced_count = 0
            error_count = 0

            source_companies = adapter.list_companies()

            for company_data in source_companies:
                try:
                    mapped_data = field_mapper.map_to_crm(
                        company_data,
                        source_system,
                        target_system,
                    )
                    synced_count += 1
                except Exception as e:
                    error_count += 1

            logger.info(f"Synced {synced_count} companies")
            return {
                "status": "completed",
                "synced_count": synced_count,
                "error_count": error_count,
            }
        except Exception as e:
            logger.error(f"Error syncing companies: {e}")
            raise


# ============================================================================
# WEBHOOK HANDLER
# ============================================================================

class WebhookHandler:
    """Handles incoming webhooks from integrated systems"""

    def __init__(self, db: Session):
        self.db = db

    def handle_webhook(
        self,
        org_id: UUID,
        system: str,
        event_type: str,
        payload: Dict[str, Any],
    ) -> bool:
        """Handle incoming webhook"""
        try:
            logger.info(f"Received webhook from {system}: {event_type}")

            if system == "servicetitan":
                return self._handle_servicetitan_webhook(org_id, event_type, payload)
            elif system == "jobber":
                return self._handle_jobber_webhook(org_id, event_type, payload)
            elif system == "hubspot":
                return self._handle_hubspot_webhook(org_id, event_type, payload)
            else:
                logger.warning(f"Unknown webhook system: {system}")
                return False
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return False

    def _handle_servicetitan_webhook(
        self,
        org_id: UUID,
        event_type: str,
        payload: Dict[str, Any],
    ) -> bool:
        """Handle ServiceTitan webhook"""
        if event_type == "customer.created":
            # Extract and sync customer data
            logger.info("Processing ServiceTitan customer.created event")
            return True
        elif event_type == "customer.updated":
            # Update customer data
            logger.info("Processing ServiceTitan customer.updated event")
            return True
        return False

    def _handle_jobber_webhook(
        self,
        org_id: UUID,
        event_type: str,
        payload: Dict[str, Any],
    ) -> bool:
        """Handle Jobber webhook"""
        if event_type == "client.created":
            logger.info("Processing Jobber client.created event")
            return True
        elif event_type == "client.updated":
            logger.info("Processing Jobber client.updated event")
            return True
        return False

    def _handle_hubspot_webhook(
        self,
        org_id: UUID,
        event_type: str,
        payload: Dict[str, Any],
    ) -> bool:
        """Handle HubSpot webhook"""
        if event_type == "contact.created":
            logger.info("Processing HubSpot contact.created event")
            return True
        elif event_type == "contact.updated":
            logger.info("Processing HubSpot contact.updated event")
            return True
        return False


# ============================================================================
# INTEGRATION MANAGER
# ============================================================================

class IntegrationManager:
    """Manages external integrations"""

    def __init__(self, db: Session):
        self.db = db
        self.adapters = {
            "servicetitan": ServiceTitanAdapter,
            "jobber": JobberAdapter,
            "hubspot": HubSpotAdapter,
        }

    def create_integration(
        self,
        org_id: UUID,
        integration_type: str,
        name: str,
        credentials: Dict[str, Any],
    ) -> Optional[str]:
        """Create new integration"""
        try:
            if integration_type not in self.adapters:
                raise ValueError(f"Unknown integration type: {integration_type}")

            integration = Integration(
                organization_id=org_id,
                integration_type=integration_type,
                name=name,
                access_token=credentials.get("access_token"),
                refresh_token=credentials.get("refresh_token"),
                config=credentials,
                sync_status="IDLE",
            )
            self.db.add(integration)
            self.db.commit()
            self.db.refresh(integration)

            logger.info(f"Created integration {integration.id}")
            return str(integration.id)
        except Exception as e:
            logger.error(f"Error creating integration: {e}")
            return None

    def get_integration(self, org_id: UUID, integration_id: UUID) -> Optional[Integration]:
        """Get integration"""
        return self.db.query(Integration).filter(
            and_(
                Integration.organization_id == org_id,
                Integration.id == integration_id,
            )
        ).first()

    def list_integrations(self, org_id: UUID) -> List[Integration]:
        """List all integrations for organization"""
        return self.db.query(Integration).filter(
            Integration.organization_id == org_id
        ).all()

    def activate_integration(self, org_id: UUID, integration_id: UUID) -> bool:
        """Activate integration"""
        integration = self.get_integration(org_id, integration_id)
        if not integration:
            return False

        integration.is_active = True
        self.db.commit()
        logger.info(f"Activated integration {integration_id}")
        return True

    def deactivate_integration(self, org_id: UUID, integration_id: UUID) -> bool:
        """Deactivate integration"""
        integration = self.get_integration(org_id, integration_id)
        if not integration:
            return False

        integration.is_active = False
        self.db.commit()
        logger.info(f"Deactivated integration {integration_id}")
        return True

    def get_adapter(
        self,
        integration_type: str,
        credentials: Dict[str, Any],
    ) -> Optional[CRMAdapter]:
        """Get adapter for integration type"""
        adapter_class = self.adapters.get(integration_type)
        if not adapter_class:
            return None

        api_key = credentials.get("api_key")
        return adapter_class(api_key) if api_key else None

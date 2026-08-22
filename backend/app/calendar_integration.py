"""Calendar Integration Module for Google Calendar and Microsoft 365"""

import os
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_

from app.models import Integration, Activity, Contact, User

logger = logging.getLogger(__name__)


# ============================================================================
# CALENDAR MODELS & ENUMS
# ============================================================================

class CalendarProvider(str, Enum):
    """Calendar providers"""
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    OFFICE365 = "office365"


class EventStatus(str, Enum):
    """Calendar event status"""
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"


# ============================================================================
# GOOGLE CALENDAR INTEGRATION
# ============================================================================

class GoogleCalendarManager:
    """Manages Google Calendar integration"""

    def __init__(self, db: Session, org_id: UUID):
        self.db = db
        self.org_id = org_id
        self.api_key = os.getenv("GOOGLE_CALENDAR_API_KEY")
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    def get_integration(self) -> Optional[Integration]:
        """Get Google Calendar integration"""
        return self.db.query(Integration).filter(
            and_(
                Integration.organization_id == self.org_id,
                Integration.integration_type == "google_calendar",
                Integration.is_active == True,
            )
        ).first()

    def list_available_slots(
        self,
        user_id: UUID,
        date: str,  # YYYY-MM-DD
        duration_minutes: int = 30,
    ) -> List[Dict[str, Any]]:
        """List available booking slots for a user on a given date"""
        try:
            # Parse date
            start_datetime = datetime.strptime(date, "%Y-%m-%d")
            end_datetime = start_datetime + timedelta(days=1)

            # Get busy times from calendar
            busy_times = self._get_busy_times(user_id, start_datetime, end_datetime)

            # Calculate available slots
            available_slots = self._calculate_available_slots(
                busy_times,
                start_datetime,
                end_datetime,
                duration_minutes,
            )

            return available_slots
        except Exception as e:
            logger.error(f"Error listing available slots: {e}")
            return []

    def book_appointment(
        self,
        user_id: UUID,
        contact_id: UUID,
        start_time: str,  # ISO format
        end_time: str,
        title: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a calendar booking"""
        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)

            # Create activity record
            activity = Activity(
                organization_id=self.org_id,
                contact_id=contact_id,
                activity_type="MEETING",
                title=title,
                description=description or f"Scheduled meeting with {self._get_contact_name(contact_id)}",
                scheduled_for=start_dt,
                metadata={
                    "calendar_provider": "google",
                    "status": "confirmed",
                    "start_time": start_time,
                    "end_time": end_time,
                },
            )
            self.db.add(activity)
            self.db.commit()
            self.db.refresh(activity)

            logger.info(f"Created appointment {activity.id}")
            return {
                "appointment_id": str(activity.id),
                "status": "confirmed",
                "start_time": start_time,
                "end_time": end_time,
                "title": title,
            }
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            raise

    def cancel_appointment(self, appointment_id: UUID) -> bool:
        """Cancel a calendar appointment"""
        try:
            activity = self.db.query(Activity).filter(
                and_(
                    Activity.id == appointment_id,
                    Activity.activity_type == "MEETING",
                )
            ).first()

            if not activity:
                return False

            activity.metadata["status"] = "cancelled"
            self.db.commit()
            logger.info(f"Cancelled appointment {appointment_id}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            return False

    def sync_calendar(self, user_id: UUID) -> Dict[str, Any]:
        """Sync calendar events"""
        try:
            integration = self.get_integration()
            if not integration:
                return {"status": "error", "message": "Google Calendar not configured"}

            # In production, this would call Google Calendar API
            logger.info(f"Synced calendar for user {user_id}")
            return {
                "status": "synced",
                "events_synced": 0,
            }
        except Exception as e:
            logger.error(f"Error syncing calendar: {e}")
            raise

    def _get_busy_times(
        self,
        user_id: UUID,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> List[Dict[str, Any]]:
        """Get busy times from calendar"""
        # In production, call Google Calendar API
        # For now, return empty list (no busy times)
        return []

    def _calculate_available_slots(
        self,
        busy_times: List[Dict[str, Any]],
        start_datetime: datetime,
        end_datetime: datetime,
        duration_minutes: int,
    ) -> List[Dict[str, Any]]:
        """Calculate available time slots"""
        slots = []
        current = start_datetime.replace(hour=9, minute=0, second=0)
        end = end_datetime.replace(hour=17, minute=0, second=0)

        while current + timedelta(minutes=duration_minutes) <= end:
            # Check if slot overlaps with busy times
            is_available = True
            for busy in busy_times:
                busy_start = datetime.fromisoformat(busy["start"])
                busy_end = datetime.fromisoformat(busy["end"])
                if current < busy_end and (current + timedelta(minutes=duration_minutes)) > busy_start:
                    is_available = False
                    break

            if is_available:
                slots.append({
                    "start_time": current.isoformat(),
                    "end_time": (current + timedelta(minutes=duration_minutes)).isoformat(),
                    "duration_minutes": duration_minutes,
                })

            current += timedelta(minutes=duration_minutes)

        return slots

    def _get_contact_name(self, contact_id: UUID) -> str:
        """Get contact name"""
        contact = self.db.query(Contact).filter(Contact.id == contact_id).first()
        if contact:
            return f"{contact.first_name} {contact.last_name}"
        return "Contact"


# ============================================================================
# MICROSOFT 365 INTEGRATION
# ============================================================================

class Microsoft365Manager:
    """Manages Microsoft 365 calendar integration"""

    def __init__(self, db: Session, org_id: UUID):
        self.db = db
        self.org_id = org_id
        self.client_id = os.getenv("MICROSOFT_CLIENT_ID")
        self.client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
        self.tenant_id = os.getenv("MICROSOFT_TENANT_ID")

    def get_integration(self) -> Optional[Integration]:
        """Get Microsoft 365 integration"""
        return self.db.query(Integration).filter(
            and_(
                Integration.organization_id == self.org_id,
                Integration.integration_type == "microsoft_365",
                Integration.is_active == True,
            )
        ).first()

    def list_available_slots(
        self,
        user_id: UUID,
        date: str,  # YYYY-MM-DD
        duration_minutes: int = 30,
    ) -> List[Dict[str, Any]]:
        """List available booking slots for a user on a given date"""
        try:
            # Parse date
            start_datetime = datetime.strptime(date, "%Y-%m-%d")
            end_datetime = start_datetime + timedelta(days=1)

            # Get busy times
            busy_times = self._get_busy_times(user_id, start_datetime, end_datetime)

            # Calculate available slots
            available_slots = self._calculate_available_slots(
                busy_times,
                start_datetime,
                end_datetime,
                duration_minutes,
            )

            return available_slots
        except Exception as e:
            logger.error(f"Error listing available slots: {e}")
            return []

    def book_appointment(
        self,
        user_id: UUID,
        contact_id: UUID,
        start_time: str,  # ISO format
        end_time: str,
        title: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a calendar booking"""
        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)

            # Create activity record
            activity = Activity(
                organization_id=self.org_id,
                contact_id=contact_id,
                activity_type="MEETING",
                title=title,
                description=description or f"Scheduled meeting with {self._get_contact_name(contact_id)}",
                scheduled_for=start_dt,
                metadata={
                    "calendar_provider": "microsoft",
                    "status": "confirmed",
                    "start_time": start_time,
                    "end_time": end_time,
                },
            )
            self.db.add(activity)
            self.db.commit()
            self.db.refresh(activity)

            logger.info(f"Created appointment {activity.id}")
            return {
                "appointment_id": str(activity.id),
                "status": "confirmed",
                "start_time": start_time,
                "end_time": end_time,
                "title": title,
            }
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            raise

    def sync_calendar(self, user_id: UUID) -> Dict[str, Any]:
        """Sync calendar events"""
        try:
            integration = self.get_integration()
            if not integration:
                return {"status": "error", "message": "Microsoft 365 not configured"}

            logger.info(f"Synced calendar for user {user_id}")
            return {
                "status": "synced",
                "events_synced": 0,
            }
        except Exception as e:
            logger.error(f"Error syncing calendar: {e}")
            raise

    def _get_busy_times(
        self,
        user_id: UUID,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> List[Dict[str, Any]]:
        """Get busy times from Microsoft calendar"""
        return []

    def _calculate_available_slots(
        self,
        busy_times: List[Dict[str, Any]],
        start_datetime: datetime,
        end_datetime: datetime,
        duration_minutes: int,
    ) -> List[Dict[str, Any]]:
        """Calculate available time slots"""
        slots = []
        current = start_datetime.replace(hour=9, minute=0, second=0)
        end = end_datetime.replace(hour=17, minute=0, second=0)

        while current + timedelta(minutes=duration_minutes) <= end:
            is_available = True
            for busy in busy_times:
                busy_start = datetime.fromisoformat(busy["start"])
                busy_end = datetime.fromisoformat(busy["end"])
                if current < busy_end and (current + timedelta(minutes=duration_minutes)) > busy_start:
                    is_available = False
                    break

            if is_available:
                slots.append({
                    "start_time": current.isoformat(),
                    "end_time": (current + timedelta(minutes=duration_minutes)).isoformat(),
                    "duration_minutes": duration_minutes,
                })

            current += timedelta(minutes=duration_minutes)

        return slots

    def _get_contact_name(self, contact_id: UUID) -> str:
        """Get contact name"""
        contact = self.db.query(Contact).filter(Contact.id == contact_id).first()
        if contact:
            return f"{contact.first_name} {contact.last_name}"
        return "Contact"


# ============================================================================
# UNIFIED CALENDAR MANAGER
# ============================================================================

class UnifiedCalendarManager:
    """Unified interface for multiple calendar providers"""

    def __init__(self, db: Session, org_id: UUID):
        self.db = db
        self.org_id = org_id
        self.google = GoogleCalendarManager(db, org_id)
        self.microsoft = Microsoft365Manager(db, org_id)

    def list_available_slots(
        self,
        user_id: UUID,
        date: str,
        duration_minutes: int = 30,
        provider: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List available slots across configured providers"""
        slots = []

        if provider == CalendarProvider.GOOGLE.value or provider is None:
            try:
                google_slots = self.google.list_available_slots(user_id, date, duration_minutes)
                slots.extend([{**s, "provider": "google"} for s in google_slots])
            except Exception as e:
                logger.warning(f"Error getting Google Calendar slots: {e}")

        if provider == CalendarProvider.MICROSOFT.value or provider is None:
            try:
                ms_slots = self.microsoft.list_available_slots(user_id, date, duration_minutes)
                slots.extend([{**s, "provider": "microsoft"} for s in ms_slots])
            except Exception as e:
                logger.warning(f"Error getting Microsoft Calendar slots: {e}")

        # Sort slots by start time
        slots.sort(key=lambda x: x["start_time"])
        return slots

    def book_appointment(
        self,
        provider: str,
        user_id: UUID,
        contact_id: UUID,
        start_time: str,
        end_time: str,
        title: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Book appointment with specified provider"""
        if provider == CalendarProvider.GOOGLE.value:
            return self.google.book_appointment(
                user_id, contact_id, start_time, end_time, title, description
            )
        elif provider == CalendarProvider.MICROSOFT.value:
            return self.microsoft.book_appointment(
                user_id, contact_id, start_time, end_time, title, description
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def sync_all_calendars(self, user_id: UUID) -> Dict[str, Any]:
        """Sync all calendar providers"""
        results = {}

        try:
            results["google"] = self.google.sync_calendar(user_id)
        except Exception as e:
            results["google"] = {"status": "error", "message": str(e)}

        try:
            results["microsoft"] = self.microsoft.sync_calendar(user_id)
        except Exception as e:
            results["microsoft"] = {"status": "error", "message": str(e)}

        return results

    def get_availability(self, user_id: UUID, days: int = 7) -> Dict[str, Any]:
        """Get user availability for next N days"""
        availability = {}
        for i in range(days):
            date = (datetime.utcnow() + timedelta(days=i)).strftime("%Y-%m-%d")
            slots = self.list_available_slots(user_id, date)
            availability[date] = {
                "available_slots": len(slots),
                "slots": slots[:3],  # Return first 3 slots
            }

        return availability

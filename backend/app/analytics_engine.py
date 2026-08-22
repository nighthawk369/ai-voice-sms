"""Analytics Engine - Event Tracking and Dashboard Metrics"""

import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional
from uuid import UUID, uuid4
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, distinct

from app.models import (
    Event, Metric, Conversation, Deal, Contact, Activity,
    WorkflowExecution, Organization
)

logger = logging.getLogger(__name__)


class EventTracker:
    """Tracks events for analytics"""

    @staticmethod
    def track_event(
        db: Session,
        organization_id: UUID,
        event_type: str,
        event_category: str,
        user_id: Optional[UUID] = None,
        contact_id: Optional[UUID] = None,
        deal_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> Event:
        """Track an event"""
        try:
            event = Event(
                id=uuid4(),
                organization_id=organization_id,
                event_type=event_type,
                event_category=event_category,
                user_id=user_id,
                contact_id=contact_id,
                deal_id=deal_id,
                resource_type=resource_type,
                resource_id=resource_id,
                properties=properties or {},
                timestamp=datetime.utcnow()
            )

            db.add(event)
            db.commit()

            logger.debug(f"Event tracked: {event_type} for org {organization_id}")
            return event

        except Exception as e:
            logger.error(f"Failed to track event: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def track_call_started(
        db: Session,
        organization_id: UUID,
        contact_id: Optional[UUID] = None,
        conversation_id: Optional[str] = None
    ) -> Event:
        """Track call started event"""
        return EventTracker.track_event(
            db,
            organization_id,
            "call_started",
            "CALL",
            contact_id=contact_id,
            resource_type="conversation",
            resource_id=conversation_id
        )

    @staticmethod
    def track_call_ended(
        db: Session,
        organization_id: UUID,
        contact_id: Optional[UUID] = None,
        conversation_id: Optional[str] = None,
        duration_seconds: int = 0,
        intent: Optional[str] = None,
        sentiment: Optional[str] = None
    ) -> Event:
        """Track call ended event"""
        return EventTracker.track_event(
            db,
            organization_id,
            "call_ended",
            "CALL",
            contact_id=contact_id,
            resource_type="conversation",
            resource_id=conversation_id,
            properties={
                "duration_seconds": duration_seconds,
                "intent": intent,
                "sentiment": sentiment
            }
        )

    @staticmethod
    def track_contact_created(
        db: Session,
        organization_id: UUID,
        contact_id: UUID,
        source: Optional[str] = None
    ) -> Event:
        """Track contact created event"""
        return EventTracker.track_event(
            db,
            organization_id,
            "contact_created",
            "CONTACT",
            contact_id=contact_id,
            properties={"source": source}
        )

    @staticmethod
    def track_deal_created(
        db: Session,
        organization_id: UUID,
        deal_id: UUID,
        contact_id: Optional[UUID] = None,
        amount: Optional[float] = None
    ) -> Event:
        """Track deal created event"""
        return EventTracker.track_event(
            db,
            organization_id,
            "deal_created",
            "DEAL",
            deal_id=deal_id,
            contact_id=contact_id,
            properties={"amount": amount}
        )

    @staticmethod
    def track_deal_won(
        db: Session,
        organization_id: UUID,
        deal_id: UUID,
        contact_id: Optional[UUID] = None,
        amount: Optional[float] = None
    ) -> Event:
        """Track deal won event"""
        return EventTracker.track_event(
            db,
            organization_id,
            "deal_won",
            "DEAL",
            deal_id=deal_id,
            contact_id=contact_id,
            properties={"amount": amount}
        )

    @staticmethod
    def track_deal_lost(
        db: Session,
        organization_id: UUID,
        deal_id: UUID,
        contact_id: Optional[UUID] = None,
        reason: Optional[str] = None
    ) -> Event:
        """Track deal lost event"""
        return EventTracker.track_event(
            db,
            organization_id,
            "deal_lost",
            "DEAL",
            deal_id=deal_id,
            contact_id=contact_id,
            properties={"reason": reason}
        )


class AnalyticsCalculator:
    """Calculates analytics metrics"""

    @staticmethod
    def get_calls_count(
        db: Session,
        organization_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """Get total calls count"""
        return db.query(func.count(Event.id)).filter(
            and_(
                Event.organization_id == organization_id,
                Event.event_type == "call_started",
                Event.timestamp.between(start_date, end_date)
            )
        ).scalar() or 0

    @staticmethod
    def get_average_call_duration(
        db: Session,
        organization_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Get average call duration in seconds"""
        events = db.query(Event).filter(
            and_(
                Event.organization_id == organization_id,
                Event.event_type == "call_ended",
                Event.timestamp.between(start_date, end_date)
            )
        ).all()

        if not events:
            return 0.0

        total_duration = 0
        for event in events:
            duration = event.properties.get("duration_seconds", 0)
            total_duration += duration

        return total_duration / len(events)

    @staticmethod
    def get_calls_by_intent(
        db: Session,
        organization_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        """Get calls grouped by intent"""
        events = db.query(Event).filter(
            and_(
                Event.organization_id == organization_id,
                Event.event_type == "call_ended",
                Event.timestamp.between(start_date, end_date)
            )
        ).all()

        intent_counts = {}
        for event in events:
            intent = event.properties.get("intent", "UNKNOWN")
            intent_counts[intent] = intent_counts.get(intent, 0) + 1

        return intent_counts

    @staticmethod
    def get_conversion_funnel(
        db: Session,
        organization_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get conversion funnel: calls -> contacts -> deals -> revenue"""
        calls = db.query(func.count(distinct(Event.resource_id))).filter(
            and_(
                Event.organization_id == organization_id,
                Event.event_type == "call_started",
                Event.timestamp.between(start_date, end_date)
            )
        ).scalar() or 0

        contacts = db.query(func.count(Contact.id)).filter(
            and_(
                Contact.organization_id == organization_id,
                Contact.created_at.between(start_date, end_date)
            )
        ).scalar() or 0

        deals = db.query(func.count(Deal.id)).filter(
            and_(
                Deal.organization_id == organization_id,
                Deal.created_at.between(start_date, end_date)
            )
        ).scalar() or 0

        deals_won = db.query(func.count(Deal.id)).filter(
            and_(
                Deal.organization_id == organization_id,
                Deal.deal_status == "WON",
                Deal.closed_date.between(start_date, end_date)
            )
        ).scalar() or 0

        revenue = db.query(func.sum(Deal.amount)).filter(
            and_(
                Deal.organization_id == organization_id,
                Deal.deal_status == "WON",
                Deal.closed_date.between(start_date, end_date)
            )
        ).scalar() or 0

        return {
            "calls_initiated": calls,
            "contacts_created": contacts,
            "deals_created": deals,
            "deals_won": deals_won,
            "revenue": float(revenue) if revenue else 0,
            "conversion_rate_calls_to_contacts": (contacts / calls * 100) if calls > 0 else 0,
            "conversion_rate_deals_to_won": (deals_won / deals * 100) if deals > 0 else 0,
        }

    @staticmethod
    def get_contact_source_distribution(
        db: Session,
        organization_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        """Get distribution of contacts by source"""
        contacts = db.query(Contact.source, func.count(Contact.id)).filter(
            and_(
                Contact.organization_id == organization_id,
                Contact.created_at.between(start_date, end_date)
            )
        ).group_by(Contact.source).all()

        return {source or "UNKNOWN": count for source, count in contacts}

    @staticmethod
    def get_deal_pipeline_analysis(
        db: Session,
        organization_id: UUID
    ) -> Dict[str, Any]:
        """Get deal pipeline analysis"""
        deals = db.query(Deal.stage, func.count(Deal.id), func.sum(Deal.amount)).filter(
            and_(
                Deal.organization_id == organization_id,
                Deal.deal_status == "OPEN"
            )
        ).group_by(Deal.stage).all()

        pipeline = {}
        total_pipeline_value = 0

        for stage, count, total_amount in deals:
            total_amount = float(total_amount) if total_amount else 0
            pipeline[stage or "UNKNOWN"] = {
                "count": count,
                "total_amount": total_amount
            }
            total_pipeline_value += total_amount

        return {
            "pipeline": pipeline,
            "total_pipeline_value": total_pipeline_value
        }

    @staticmethod
    def get_user_activity_summary(
        db: Session,
        organization_id: UUID,
        user_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get user activity summary"""
        calls_made = db.query(func.count(Event.id)).filter(
            and_(
                Event.organization_id == organization_id,
                Event.user_id == user_id,
                Event.event_type == "call_started",
                Event.timestamp.between(start_date, end_date)
            )
        ).scalar() or 0

        contacts_created = db.query(func.count(Contact.id)).filter(
            and_(
                Contact.organization_id == organization_id,
                Contact.assigned_to == user_id,
                Contact.created_at.between(start_date, end_date)
            )
        ).scalar() or 0

        deals_closed = db.query(func.count(Deal.id)).filter(
            and_(
                Deal.organization_id == organization_id,
                Deal.assigned_to == user_id,
                Deal.deal_status == "WON",
                Deal.closed_date.between(start_date, end_date)
            )
        ).scalar() or 0

        revenue = db.query(func.sum(Deal.amount)).filter(
            and_(
                Deal.organization_id == organization_id,
                Deal.assigned_to == user_id,
                Deal.deal_status == "WON",
                Deal.closed_date.between(start_date, end_date)
            )
        ).scalar() or 0

        return {
            "calls_made": calls_made,
            "contacts_created": contacts_created,
            "deals_closed": deals_closed,
            "revenue": float(revenue) if revenue else 0
        }

    @staticmethod
    def get_workflow_performance(
        db: Session,
        organization_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get workflow performance metrics"""
        executions = db.query(
            WorkflowExecution.status,
            func.count(WorkflowExecution.id)
        ).filter(
            and_(
                WorkflowExecution.organization_id == organization_id,
                WorkflowExecution.created_at.between(start_date, end_date)
            )
        ).group_by(WorkflowExecution.status).all()

        status_counts = {status: count for status, count in executions}

        total = sum(status_counts.values())
        success_rate = (status_counts.get("SUCCESS", 0) / total * 100) if total > 0 else 0

        return {
            "total_executions": total,
            "successful": status_counts.get("SUCCESS", 0),
            "failed": status_counts.get("FAILED", 0),
            "skipped": status_counts.get("SKIPPED", 0),
            "success_rate": success_rate
        }

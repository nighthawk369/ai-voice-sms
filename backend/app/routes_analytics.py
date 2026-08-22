"""Analytics API Routes - Event tracking and dashboard metrics"""

import logging
from datetime import datetime, timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.analytics_engine import EventTracker, AnalyticsCalculator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


# ============================================================================
# EVENT TRACKING ROUTES
# ============================================================================

@router.post("/events/track", response_model=dict, status_code=status.HTTP_201_CREATED)
async def track_event(
    event_type: str,
    event_category: str,
    resource_type: str = None,
    resource_id: str = None,
    properties: dict = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Track an event"""
    try:
        event = EventTracker.track_event(
            db,
            current_user.organization_id,
            event_type,
            event_category,
            user_id=current_user.id,
            resource_type=resource_type,
            resource_id=resource_id,
            properties=properties or {}
        )

        logger.info(f"Tracked event {event_type}")

        return {
            "id": str(event.id),
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to track event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DASHBOARD METRICS ROUTES
# ============================================================================

@router.get("/dashboard/summary", response_model=dict)
async def get_dashboard_summary(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard summary metrics"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        calls_count = AnalyticsCalculator.get_calls_count(
            db, current_user.organization_id, start_date, end_date
        )
        avg_call_duration = AnalyticsCalculator.get_average_call_duration(
            db, current_user.organization_id, start_date, end_date
        )
        conversion_funnel = AnalyticsCalculator.get_conversion_funnel(
            db, current_user.organization_id, start_date, end_date
        )

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "calls": {
                "total": calls_count,
                "avg_duration_seconds": avg_call_duration
            },
            "conversion_funnel": conversion_funnel,
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get dashboard summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calls/by-intent", response_model=dict)
async def get_calls_by_intent(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get call distribution by intent"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        calls_by_intent = AnalyticsCalculator.get_calls_by_intent(
            db, current_user.organization_id, start_date, end_date
        )

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "calls_by_intent": calls_by_intent
        }

    except Exception as e:
        logger.error(f"Failed to get calls by intent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversion-funnel", response_model=dict)
async def get_conversion_funnel(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conversion funnel analysis"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        funnel = AnalyticsCalculator.get_conversion_funnel(
            db, current_user.organization_id, start_date, end_date
        )

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "funnel": funnel
        }

    except Exception as e:
        logger.error(f"Failed to get conversion funnel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contacts/by-source", response_model=dict)
async def get_contacts_by_source(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get contact distribution by source"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        distribution = AnalyticsCalculator.get_contact_source_distribution(
            db, current_user.organization_id, start_date, end_date
        )

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "distribution": distribution
        }

    except Exception as e:
        logger.error(f"Failed to get contacts by source: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipeline/analysis", response_model=dict)
async def get_pipeline_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get deal pipeline analysis"""
    try:
        analysis = AnalyticsCalculator.get_deal_pipeline_analysis(
            db, current_user.organization_id
        )

        return {
            "pipeline_analysis": analysis,
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get pipeline analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/activity-summary", response_model=dict)
async def get_user_activity_summary(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user activity summary"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        summary = AnalyticsCalculator.get_user_activity_summary(
            db,
            current_user.organization_id,
            UUID(user_id),
            start_date,
            end_date
        )

        return {
            "user_id": user_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "activity": summary
        }

    except Exception as e:
        logger.error(f"Failed to get user activity summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/performance", response_model=dict)
async def get_workflow_performance(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get workflow performance metrics"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        performance = AnalyticsCalculator.get_workflow_performance(
            db, current_user.organization_id, start_date, end_date
        )

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "performance": performance
        }

    except Exception as e:
        logger.error(f"Failed to get workflow performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CUSTOM ANALYTICS ROUTES
# ============================================================================

@router.post("/custom-query", response_model=dict)
async def run_custom_query(
    metric_type: str,
    start_date: str,
    end_date: str,
    filters: dict = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run custom analytics query"""
    try:
        # TODO: Implement custom query engine with flexible filtering
        # This would allow customers to build custom reports

        return {
            "metric_type": metric_type,
            "period": {
                "start": start_date,
                "end": end_date
            },
            "filters": filters or {},
            "data": [],
            "note": "Custom queries coming soon"
        }

    except Exception as e:
        logger.error(f"Failed to run custom query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

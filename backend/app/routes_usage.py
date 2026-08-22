"""Usage Metering API Routes - Track and report API usage"""

import logging
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.usage_metering import UsageTracker, UsageReporter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/usage", tags=["usage"])


# ============================================================================
# USAGE TRACKING ROUTES
# ============================================================================

@router.post("/track/api-call", response_model=dict, status_code=status.HTTP_201_CREATED)
async def track_api_call(
    endpoint: str,
    method: str,
    response_time_ms: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Track API call"""
    try:
        metric = UsageTracker.track_api_call(
            db,
            current_user.organization_id,
            endpoint,
            method,
            response_time_ms
        )

        return {
            "id": str(metric.id),
            "metric_type": metric.metric_type,
            "quantity": metric.quantity,
            "cost": float(metric.total_cost),
            "timestamp": metric.created_at.isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to track API call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/track/tokens", response_model=dict, status_code=status.HTTP_201_CREATED)
async def track_tokens(
    tokens_used: int,
    llm_provider: str,
    model: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Track token usage"""
    try:
        metric = UsageTracker.track_tokens(
            db,
            current_user.organization_id,
            tokens_used,
            llm_provider,
            model
        )

        return {
            "id": str(metric.id),
            "metric_type": metric.metric_type,
            "quantity": metric.quantity,
            "cost": float(metric.total_cost),
            "timestamp": metric.created_at.isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to track tokens: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/track/voice-minutes", response_model=dict, status_code=status.HTTP_201_CREATED)
async def track_voice_minutes(
    duration_seconds: int,
    conversation_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Track voice minutes"""
    try:
        metric = UsageTracker.track_voice_minutes(
            db,
            current_user.organization_id,
            duration_seconds,
            conversation_id
        )

        return {
            "id": str(metric.id),
            "metric_type": metric.metric_type,
            "quantity": metric.quantity,
            "cost": float(metric.total_cost),
            "timestamp": metric.created_at.isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to track voice minutes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/track/sms", response_model=dict, status_code=status.HTTP_201_CREATED)
async def track_sms(
    phone_number: str,
    message_length: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Track SMS sent"""
    try:
        metric = UsageTracker.track_sms_sent(
            db,
            current_user.organization_id,
            phone_number,
            message_length
        )

        return {
            "id": str(metric.id),
            "metric_type": metric.metric_type,
            "quantity": metric.quantity,
            "cost": float(metric.total_cost),
            "timestamp": metric.created_at.isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to track SMS: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# USAGE REPORTING ROUTES
# ============================================================================

@router.get("/daily/{date_str}", response_model=dict)
async def get_daily_usage(
    date_str: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get daily usage breakdown"""
    try:
        date_obj = datetime.fromisoformat(date_str).date()
        report = UsageReporter.get_daily_usage(
            db,
            current_user.organization_id,
            date_obj
        )

        return report

    except Exception as e:
        logger.error(f"Failed to get daily usage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monthly/{year}/{month}", response_model=dict)
async def get_monthly_usage(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get monthly usage breakdown"""
    try:
        if month < 1 or month > 12 or year < 2020:
            raise HTTPException(status_code=400, detail="Invalid year or month")

        report = UsageReporter.get_monthly_usage(
            db,
            current_user.organization_id,
            year,
            month
        )

        return report

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get monthly usage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-type/{metric_type}", response_model=dict)
async def get_usage_by_type(
    metric_type: str,
    start_date: str = None,
    end_date: str = None,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get usage for specific metric type"""
    try:
        if end_date:
            end = datetime.fromisoformat(end_date)
        else:
            end = datetime.utcnow()

        if start_date:
            start = datetime.fromisoformat(start_date)
        else:
            start = end - timedelta(days=days)

        report = UsageReporter.get_usage_by_type(
            db,
            current_user.organization_id,
            start,
            end,
            metric_type
        )

        return report

    except Exception as e:
        logger.error(f"Failed to get usage by type: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast", response_model=dict)
async def get_usage_forecast(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get usage forecast based on trends"""
    try:
        forecast = UsageReporter.get_forecast(
            db,
            current_user.organization_id,
            days
        )

        return forecast

    except Exception as e:
        logger.error(f"Failed to get forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=dict)
async def get_usage_summary(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get usage summary"""
    try:
        from datetime import timedelta as td

        end_date = datetime.utcnow()
        start_date = end_date - td(days=days)

        daily_reports = []
        current_date = start_date.date()
        while current_date <= end_date.date():
            report = UsageReporter.get_daily_usage(
                db,
                current_user.organization_id,
                current_date
            )
            daily_reports.append(report)
            current_date += td(days=1).date() - current_date

        total_cost = sum(r.get("total_cost", 0) for r in daily_reports)

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "total_cost": total_cost,
            "avg_daily_cost": total_cost / days if days > 0 else 0,
            "daily_breakdown": daily_reports
        }

    except Exception as e:
        logger.error(f"Failed to get usage summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BILLING INTEGRATION ROUTES
# ============================================================================

@router.get("/billing/estimate", response_model=dict)
async def get_billing_estimate(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get billing estimate based on current usage"""
    try:
        forecast = UsageReporter.get_forecast(db, current_user.organization_id, days)

        return {
            "period_days": days,
            "estimated_monthly_cost": forecast.get("forecasted_monthly_cost", 0),
            "based_on": "Last 7 days of usage",
            "note": "This is an estimate and may change based on future usage"
        }

    except Exception as e:
        logger.error(f"Failed to get billing estimate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

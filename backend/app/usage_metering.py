"""Usage Metering - Token Counting and API Usage Tracking"""

import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional
from uuid import UUID, uuid4
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models import UsageMetric, Organization, Conversation

logger = logging.getLogger(__name__)


class TokenCounter:
    """Token counting utilities"""

    @staticmethod
    def count_tokens_openai(text: str) -> int:
        """Estimate tokens for OpenAI API (rough estimate: 1 token ≈ 4 chars)"""
        return max(1, len(text) // 4)

    @staticmethod
    def count_tokens_anthropic(text: str) -> int:
        """Estimate tokens for Anthropic API (rough estimate: 1 token ≈ 4 chars)"""
        return max(1, len(text) // 4)

    @staticmethod
    def count_tokens_gemini(text: str) -> int:
        """Estimate tokens for Google Gemini (rough estimate: 1 token ≈ 4 chars)"""
        return max(1, len(text) // 4)

    @staticmethod
    def count_tokens(text: str, provider: str = "openai") -> int:
        """Count tokens based on provider"""
        if provider == "anthropic":
            return TokenCounter.count_tokens_anthropic(text)
        elif provider == "gemini":
            return TokenCounter.count_tokens_gemini(text)
        else:
            return TokenCounter.count_tokens_openai(text)


class UsageTracker:
    """Tracks API usage and metering"""

    # Pricing configuration (in USD per unit)
    PRICING = {
        "api_calls": 0.0001,  # Per API call
        "tokens_used": 0.000002,  # Per token (OpenAI gpt-3.5)
        "voice_minutes": 0.25,  # Per minute
        "sms_sent": 0.0075,  # Per SMS
    }

    @staticmethod
    def track_usage(
        db: Session,
        organization_id: UUID,
        metric_type: str,
        quantity: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None
    ) -> UsageMetric:
        """Track usage metric"""
        try:
            if period_start is None:
                period_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            if period_end is None:
                period_end = period_start + timedelta(days=1)

            unit_cost = Decimal(str(UsageTracker.PRICING.get(metric_type, 0)))
            total_cost = unit_cost * Decimal(str(quantity))

            metric = UsageMetric(
                id=uuid4(),
                organization_id=organization_id,
                metric_type=metric_type,
                unit=UsageTracker._get_unit(metric_type),
                quantity=quantity,
                unit_cost=unit_cost,
                total_cost=total_cost,
                metadata=metadata or {},
                period_start=period_start,
                period_end=period_end
            )

            db.add(metric)
            db.commit()

            logger.debug(f"Usage tracked: {metric_type} x {quantity} for org {organization_id}")
            return metric

        except Exception as e:
            logger.error(f"Failed to track usage: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def _get_unit(metric_type: str) -> str:
        """Get unit for metric type"""
        if metric_type == "voice_minutes":
            return "minutes"
        elif metric_type == "tokens_used":
            return "tokens"
        elif metric_type == "sms_sent":
            return "count"
        else:
            return "count"

    @staticmethod
    def track_api_call(
        db: Session,
        organization_id: UUID,
        endpoint: str,
        method: str,
        response_time_ms: int
    ) -> UsageMetric:
        """Track API call"""
        return UsageTracker.track_usage(
            db,
            organization_id,
            "api_calls",
            quantity=1,
            metadata={
                "endpoint": endpoint,
                "method": method,
                "response_time_ms": response_time_ms
            }
        )

    @staticmethod
    def track_tokens(
        db: Session,
        organization_id: UUID,
        tokens_used: int,
        llm_provider: str,
        model: str
    ) -> UsageMetric:
        """Track token usage"""
        return UsageTracker.track_usage(
            db,
            organization_id,
            "tokens_used",
            quantity=tokens_used,
            metadata={
                "llm_provider": llm_provider,
                "model": model
            }
        )

    @staticmethod
    def track_voice_minutes(
        db: Session,
        organization_id: UUID,
        duration_seconds: int,
        conversation_id: Optional[str] = None
    ) -> UsageMetric:
        """Track voice minutes"""
        minutes = max(1, duration_seconds // 60)  # Round up to 1 minute minimum

        return UsageTracker.track_usage(
            db,
            organization_id,
            "voice_minutes",
            quantity=minutes,
            metadata={
                "duration_seconds": duration_seconds,
                "conversation_id": conversation_id
            }
        )

    @staticmethod
    def track_sms_sent(
        db: Session,
        organization_id: UUID,
        phone_number: str,
        message_length: int
    ) -> UsageMetric:
        """Track SMS sent"""
        # SMS charges are typically per message (but might be multiple for long messages)
        sms_count = max(1, (message_length + 159) // 160)  # 160 chars per SMS

        return UsageTracker.track_usage(
            db,
            organization_id,
            "sms_sent",
            quantity=sms_count,
            metadata={
                "phone_number": phone_number,
                "message_length": message_length
            }
        )


class UsageReporter:
    """Generates usage reports and analytics"""

    @staticmethod
    def get_daily_usage(
        db: Session,
        organization_id: UUID,
        date_obj: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get daily usage breakdown"""
        if date_obj is None:
            date_obj = date.today()

        start_date = datetime.combine(date_obj, datetime.min.time())
        end_date = start_date + timedelta(days=1)

        metrics = db.query(UsageMetric).filter(
            and_(
                UsageMetric.organization_id == organization_id,
                UsageMetric.created_at.between(start_date, end_date)
            )
        ).all()

        usage_by_type = {}
        total_cost = Decimal(0)

        for metric in metrics:
            if metric.metric_type not in usage_by_type:
                usage_by_type[metric.metric_type] = {
                    "quantity": 0,
                    "cost": Decimal(0)
                }

            usage_by_type[metric.metric_type]["quantity"] += metric.quantity
            usage_by_type[metric.metric_type]["cost"] += metric.total_cost
            total_cost += metric.total_cost

        return {
            "date": date_obj.isoformat(),
            "usage_by_type": {k: {
                "quantity": v["quantity"],
                "cost": float(v["cost"])
            } for k, v in usage_by_type.items()},
            "total_cost": float(total_cost)
        }

    @staticmethod
    def get_monthly_usage(
        db: Session,
        organization_id: UUID,
        year: int,
        month: int
    ) -> Dict[str, Any]:
        """Get monthly usage breakdown"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        metrics = db.query(UsageMetric).filter(
            and_(
                UsageMetric.organization_id == organization_id,
                UsageMetric.created_at.between(start_date, end_date)
            )
        ).all()

        usage_by_type = {}
        total_cost = Decimal(0)

        for metric in metrics:
            if metric.metric_type not in usage_by_type:
                usage_by_type[metric.metric_type] = {
                    "quantity": 0,
                    "cost": Decimal(0)
                }

            usage_by_type[metric.metric_type]["quantity"] += metric.quantity
            usage_by_type[metric.metric_type]["cost"] += metric.total_cost
            total_cost += metric.total_cost

        return {
            "period": f"{year}-{month:02d}",
            "usage_by_type": {k: {
                "quantity": v["quantity"],
                "cost": float(v["cost"])
            } for k, v in usage_by_type.items()},
            "total_cost": float(total_cost)
        }

    @staticmethod
    def get_usage_by_type(
        db: Session,
        organization_id: UUID,
        start_date: datetime,
        end_date: datetime,
        metric_type: str
    ) -> Dict[str, Any]:
        """Get usage for specific metric type"""
        metrics = db.query(UsageMetric).filter(
            and_(
                UsageMetric.organization_id == organization_id,
                UsageMetric.metric_type == metric_type,
                UsageMetric.created_at.between(start_date, end_date)
            )
        ).all()

        total_quantity = sum(m.quantity for m in metrics)
        total_cost = sum(m.total_cost for m in metrics)
        avg_cost_per_unit = (total_cost / total_quantity) if total_quantity > 0 else Decimal(0)

        return {
            "metric_type": metric_type,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_quantity": total_quantity,
            "total_cost": float(total_cost),
            "avg_cost_per_unit": float(avg_cost_per_unit),
            "breakdown_by_day": UsageReporter._breakdown_by_day(metrics)
        }

    @staticmethod
    def _breakdown_by_day(metrics: List[UsageMetric]) -> Dict[str, Dict[str, Any]]:
        """Break down metrics by day"""
        daily = {}

        for metric in metrics:
            day = metric.created_at.date().isoformat()

            if day not in daily:
                daily[day] = {
                    "quantity": 0,
                    "cost": Decimal(0)
                }

            daily[day]["quantity"] += metric.quantity
            daily[day]["cost"] += metric.total_cost

        return {k: {
            "quantity": v["quantity"],
            "cost": float(v["cost"])
        } for k, v in daily.items()}

    @staticmethod
    def get_forecast(
        db: Session,
        organization_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """Forecast usage based on recent trends"""
        # Get last 7 days of data
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()

        metrics = db.query(UsageMetric).filter(
            and_(
                UsageMetric.organization_id == organization_id,
                UsageMetric.created_at.between(start_date, end_date)
            )
        ).all()

        if not metrics:
            return {
                "forecast_period_days": days,
                "forecast": {},
                "note": "Insufficient data for forecast"
            }

        # Calculate average daily usage
        daily_totals = {}
        for metric in metrics:
            day = metric.created_at.date()
            if day not in daily_totals:
                daily_totals[day] = Decimal(0)
            daily_totals[day] += metric.total_cost

        avg_daily_cost = sum(daily_totals.values()) / len(daily_totals) if daily_totals else Decimal(0)
        forecasted_monthly_cost = avg_daily_cost * Decimal(30)

        return {
            "forecast_period_days": days,
            "avg_daily_cost": float(avg_daily_cost),
            "forecasted_monthly_cost": float(forecasted_monthly_cost),
            "recent_daily_costs": {k.isoformat(): float(v) for k, v in daily_totals.items()}
        }

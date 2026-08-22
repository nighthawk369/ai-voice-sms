"""LLM usage tracking and analytics"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from uuid import UUID
from decimal import Decimal

logger = logging.getLogger(__name__)

# Token pricing per 1M tokens (as of 2024)
PROVIDER_PRICING = {
    "openai": {
        "gpt-4o": {"input": Decimal("2.50"), "output": Decimal("10.00")},
        "gpt-4o-mini": {"input": Decimal("0.15"), "output": Decimal("0.60")},
        "gpt-4-turbo": {"input": Decimal("10.00"), "output": Decimal("30.00")},
    },
    "anthropic": {
        "claude-3-5-sonnet-20241022": {"input": Decimal("3.00"), "output": Decimal("15.00")},
        "claude-3-5-haiku-20241022": {"input": Decimal("0.80"), "output": Decimal("4.00")},
        "claude-3-opus-20250219": {"input": Decimal("15.00"), "output": Decimal("75.00")},
    },
    "google": {
        "gemini-2.0-flash-exp": {"input": Decimal("0.075"), "output": Decimal("0.30")},
        "gemini-1.5-pro": {"input": Decimal("1.25"), "output": Decimal("5.00")},
    },
    "local": {
        "mistral": {"input": Decimal("0"), "output": Decimal("0")},
        "llama": {"input": Decimal("0"), "output": Decimal("0")},
    },
}


@dataclass
class TokenUsage:
    """Token usage for a single request"""
    provider: str
    model: str
    tokens_in: int
    tokens_out: int
    total_tokens: int = field(init=False)
    cost: Decimal = field(init=False)

    def __post_init__(self):
        self.total_tokens = self.tokens_in + self.tokens_out
        self.cost = self._calculate_cost()

    def _calculate_cost(self) -> Decimal:
        """Calculate cost based on token usage"""
        provider_models = PROVIDER_PRICING.get(self.provider, {})
        model_pricing = provider_models.get(self.model)

        if not model_pricing:
            logger.warning(f"No pricing found for {self.provider}/{self.model}")
            return Decimal("0")

        input_cost = (Decimal(self.tokens_in) / Decimal("1000000")) * model_pricing.get("input", Decimal("0"))
        output_cost = (Decimal(self.tokens_out) / Decimal("1000000")) * model_pricing.get("output", Decimal("0"))

        return input_cost + output_cost


@dataclass
class UsageStats:
    """Aggregated usage statistics"""
    provider: str
    model: str
    total_requests: int = 0
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    total_cost: Decimal = field(default_factory=lambda: Decimal("0"))
    average_response_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return self.cache_hits / total

    @property
    def average_tokens_per_request(self) -> float:
        """Calculate average tokens per request"""
        if self.total_requests == 0:
            return 0.0
        return (self.total_tokens_in + self.total_tokens_out) / self.total_requests


class UsageTracker:
    """Track LLM API usage and costs"""

    def __init__(self):
        self.usage_by_provider: Dict[str, UsageStats] = {}
        self.usage_by_org: Dict[UUID, Dict[str, UsageStats]] = {}
        self.request_times: Dict[str, list] = {}

    def record_usage(
        self,
        provider: str,
        model: str,
        tokens_in: int,
        tokens_out: int,
        response_time: float,
        org_id: Optional[UUID] = None,
        is_cache_hit: bool = False,
    ) -> TokenUsage:
        """Record token usage"""
        usage = TokenUsage(provider=provider, model=model, tokens_in=tokens_in, tokens_out=tokens_out)

        # Update provider stats
        key = f"{provider}:{model}"
        if key not in self.usage_by_provider:
            self.usage_by_provider[key] = UsageStats(provider=provider, model=model)

        stats = self.usage_by_provider[key]
        stats.total_requests += 1
        stats.total_tokens_in += tokens_in
        stats.total_tokens_out += tokens_out
        stats.total_cost += usage.cost

        if is_cache_hit:
            stats.cache_hits += 1
        else:
            stats.cache_misses += 1

        # Update response time
        if key not in self.request_times:
            self.request_times[key] = []
        self.request_times[key].append(response_time)
        stats.average_response_time = sum(self.request_times[key]) / len(self.request_times[key])

        # Update org stats if provided
        if org_id:
            if org_id not in self.usage_by_org:
                self.usage_by_org[org_id] = {}
            if key not in self.usage_by_org[org_id]:
                self.usage_by_org[org_id][key] = UsageStats(provider=provider, model=model)

            org_stats = self.usage_by_org[org_id][key]
            org_stats.total_requests += 1
            org_stats.total_tokens_in += tokens_in
            org_stats.total_tokens_out += tokens_out
            org_stats.total_cost += usage.cost
            if is_cache_hit:
                org_stats.cache_hits += 1
            else:
                org_stats.cache_misses += 1

        logger.info(f"Recorded usage: {provider}/{model}, tokens: {usage.total_tokens}, cost: ${usage.cost}")
        return usage

    def get_provider_stats(self, provider: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Get usage stats for a provider"""
        if model:
            key = f"{provider}:{model}"
            stats = self.usage_by_provider.get(key)
            return stats.__dict__ if stats else {}

        # Aggregate all models for provider
        total_requests = 0
        total_tokens_in = 0
        total_tokens_out = 0
        total_cost = Decimal("0")

        for key, stats in self.usage_by_provider.items():
            if stats.provider == provider:
                total_requests += stats.total_requests
                total_tokens_in += stats.total_tokens_in
                total_tokens_out += stats.total_tokens_out
                total_cost += stats.total_cost

        return {
            "provider": provider,
            "total_requests": total_requests,
            "total_tokens": total_tokens_in + total_tokens_out,
            "total_cost": str(total_cost),
        }

    def get_org_stats(self, org_id: UUID) -> Dict[str, Any]:
        """Get usage stats for an organization"""
        if org_id not in self.usage_by_org:
            return {
                "org_id": str(org_id),
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": "0",
            }

        org_usage = self.usage_by_org[org_id]
        total_requests = sum(stats.total_requests for stats in org_usage.values())
        total_tokens = sum(stats.total_tokens_in + stats.total_tokens_out for stats in org_usage.values())
        total_cost = sum(stats.total_cost for stats in org_usage.values())

        return {
            "org_id": str(org_id),
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "total_cost": str(total_cost),
            "by_provider": {key: stats.__dict__ for key, stats in org_usage.items()},
        }

    def reset_stats(self) -> None:
        """Reset all statistics"""
        self.usage_by_provider.clear()
        self.usage_by_org.clear()
        self.request_times.clear()
        logger.info("Usage stats reset")


# Global usage tracker instance
_tracker = None


def get_usage_tracker() -> UsageTracker:
    """Get or create global usage tracker"""
    global _tracker
    if _tracker is None:
        _tracker = UsageTracker()
    return _tracker

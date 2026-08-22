"""LLM response caching"""

import hashlib
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CachedResponse:
    """Cached LLM response"""
    content: str
    tokens_in: int
    tokens_out: int
    model: str
    provider: str
    created_at: datetime
    expires_at: datetime
    hit_count: int = 0


class LLMCache:
    """Simple in-memory LLM response cache"""

    def __init__(self, ttl_hours: int = 24, max_size: int = 1000):
        self.cache: Dict[str, CachedResponse] = {}
        self.ttl = timedelta(hours=ttl_hours)
        self.max_size = max_size

    def _make_key(self, prompt: str, system_prompt: Optional[str], provider: str, model: str) -> str:
        """Generate cache key from prompt and context"""
        content = f"{system_prompt or ''}{prompt}{provider}{model}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, prompt: str, system_prompt: Optional[str], provider: str, model: str) -> Optional[CachedResponse]:
        """Get cached response"""
        key = self._make_key(prompt, system_prompt, provider, model)

        if key not in self.cache:
            return None

        cached = self.cache[key]

        # Check if expired
        if datetime.utcnow() > cached.expires_at:
            del self.cache[key]
            return None

        # Update hit count
        cached.hit_count += 1
        logger.info(f"Cache hit for {provider}/{model}, hit count: {cached.hit_count}")
        return cached

    def set(self, prompt: str, system_prompt: Optional[str], provider: str, model: str,
            content: str, tokens_in: int, tokens_out: int) -> None:
        """Cache response"""
        # Evict oldest entry if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].created_at)
            del self.cache[oldest_key]
            logger.info(f"Evicted oldest cache entry, cache size: {len(self.cache)}")

        key = self._make_key(prompt, system_prompt, provider, model)
        now = datetime.utcnow()

        self.cache[key] = CachedResponse(
            content=content,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            model=model,
            provider=provider,
            created_at=now,
            expires_at=now + self.ttl,
        )
        logger.info(f"Cached response for {provider}/{model}, cache size: {len(self.cache)}")

    def clear(self) -> None:
        """Clear entire cache"""
        self.cache.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_hits = sum(r.hit_count for r in self.cache.values())
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "total_hits": total_hits,
            "average_hits": total_hits / len(self.cache) if self.cache else 0,
        }


# Global cache instance
_cache = None


def get_llm_cache(ttl_hours: int = 24) -> LLMCache:
    """Get or create global LLM cache"""
    global _cache
    if _cache is None:
        _cache = LLMCache(ttl_hours=ttl_hours)
    return _cache

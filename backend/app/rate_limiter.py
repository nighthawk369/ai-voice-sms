"""Rate limiting implementation"""

import time
import logging
from typing import Dict, Optional
from functools import wraps
from datetime import datetime, timezone, timedelta
from uuid import UUID

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self, calls_per_minute: int = 60, cleanup_interval: int = 60):
        self.calls_per_minute = calls_per_minute
        self.cleanup_interval = cleanup_interval
        self.requests: Dict[str, list] = {}
        self.last_cleanup = time.time()

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed"""
        now = time.time()

        # Cleanup old entries every cleanup_interval seconds
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup()
            self.last_cleanup = now

        # Get current minute
        current_minute = int(now / 60)

        if key not in self.requests:
            self.requests[key] = []

        # Remove old entries
        cutoff = now - 60
        self.requests[key] = [ts for ts in self.requests[key] if ts > cutoff]

        # Check limit
        if len(self.requests[key]) >= self.calls_per_minute:
            return False

        # Add current request
        self.requests[key].append(now)
        return True

    def get_remaining(self, key: str) -> int:
        """Get remaining requests for key"""
        if key not in self.requests:
            return self.calls_per_minute

        now = time.time()
        cutoff = now - 60
        valid_requests = [ts for ts in self.requests[key] if ts > cutoff]

        return max(0, self.calls_per_minute - len(valid_requests))

    def get_reset_time(self, key: str) -> Optional[datetime]:
        """Get time when rate limit resets"""
        if key not in self.requests or not self.requests[key]:
            return None

        oldest = min(self.requests[key])
        reset_time = oldest + 60

        return datetime.fromtimestamp(reset_time, tz=timezone.utc)

    def _cleanup(self):
        """Remove keys with no recent requests"""
        now = time.time()
        cutoff = now - 60

        to_remove = []
        for key, timestamps in self.requests.items():
            valid = [ts for ts in timestamps if ts > cutoff]
            if not valid:
                to_remove.append(key)

        for key in to_remove:
            del self.requests[key]

        logger.debug(f"Rate limiter cleanup: removed {len(to_remove)} keys")


class RateLimitConfig:
    """Rate limit configuration"""

    def __init__(
        self,
        default_calls_per_minute: int = 60,
        authenticated_calls_per_minute: int = 300,
        admin_calls_per_minute: int = 1000,
        public_endpoints_calls_per_minute: int = 30
    ):
        self.default = default_calls_per_minute
        self.authenticated = authenticated_calls_per_minute
        self.admin = admin_calls_per_minute
        self.public = public_endpoints_calls_per_minute

    def get_limit(
        self,
        user_id: Optional[UUID] = None,
        user_role: Optional[str] = None,
        is_api_key: bool = False
    ) -> int:
        """Get rate limit based on user type"""
        if is_api_key:
            if user_role in ["OWNER", "ADMIN"]:
                return self.admin
            return self.authenticated

        if user_role in ["OWNER", "ADMIN"]:
            return self.admin
        elif user_id:
            return self.authenticated
        else:
            return self.public


# Global rate limiter instance
_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter"""
    return _rate_limiter


def reset_rate_limiter():
    """Reset rate limiter (for testing)"""
    global _rate_limiter
    _rate_limiter = RateLimiter()

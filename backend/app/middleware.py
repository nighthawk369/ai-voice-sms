"""Middleware for tenant isolation, error handling, request logging, and rate limiting"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from uuid import uuid4
import logging
import time
import json
from app.rate_limiter import get_rate_limiter, RateLimitConfig
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
rate_limit_config = RateLimitConfig()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add request ID for tracing"""
    async def dispatch(self, request: Request, call_next):
        request.state.request_id = str(uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response


class TenantIsolationMiddleware(BaseHTTPMiddleware):
    """Enforce tenant isolation - validate organization access"""

    # Paths that don't require tenant validation
    EXEMPT_PATHS = {
        "/docs", "/redoc", "/openapi.json",
        "/health/live", "/health/ready",
        "/api/v1/auth/signup", "/api/v1/auth/login",
        "/api/v1/auth/refresh"
    }

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip exempt paths
        if any(path.startswith(exempt) for exempt in self.EXEMPT_PATHS):
            return await call_next(request)

        # For authenticated endpoints, tenant validation happens in dependencies
        return await call_next(request)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses"""

    async def dispatch(self, request: Request, call_next):
        request.state.start_time = time.time()

        # Log request
        logger.info(
            f"[{request.state.request_id}] {request.method} {request.url.path}",
            extra={
                "request_id": request.state.request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
            }
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            process_time = time.time() - request.state.start_time
            logger.error(
                f"[{request.state.request_id}] Exception: {exc}",
                extra={
                    "request_id": request.state.request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "process_time": process_time,
                },
                exc_info=True
            )
            raise

        # Log response
        process_time = time.time() - request.state.start_time
        logger.info(
            f"[{request.state.request_id}] {response.status_code} ({process_time:.3f}s)",
            extra={
                "request_id": request.state.request_id,
                "status_code": response.status_code,
                "process_time": process_time,
            }
        )

        response.headers["X-Process-Time"] = str(process_time)
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Centralized error handling"""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "detail": str(e),
                    "error_code": "VALIDATION_ERROR",
                    "request_id": getattr(request.state, "request_id", None)
                }
            )
        except PermissionError as e:
            logger.warning(f"Permission error: {e}")
            return JSONResponse(
                status_code=403,
                content={
                    "detail": str(e),
                    "error_code": "PERMISSION_DENIED",
                    "request_id": getattr(request.state, "request_id", None)
                }
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "error_code": "INTERNAL_ERROR",
                    "request_id": getattr(request.state, "request_id", None)
                }
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""

    # Paths exempt from rate limiting
    EXEMPT_PATHS = {
        "/docs", "/redoc", "/openapi.json",
        "/health/live", "/health/ready",
    }

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for exempt paths
        if any(request.url.path.startswith(path) for path in self.EXEMPT_PATHS):
            return await call_next(request)

        # Get rate limit key
        # Try to use user_id from token, fall back to IP address
        user_id = getattr(request.state, "user_id", None)
        client_ip = request.client.host if request.client else "unknown"
        rate_limit_key = str(user_id) if user_id else f"ip:{client_ip}"

        # Check rate limit
        limiter = get_rate_limiter()
        user_role = getattr(request.state, "user_role", None)

        limit = rate_limit_config.get_limit(
            user_id=user_id,
            user_role=user_role,
            is_api_key=getattr(request.state, "is_api_key", False)
        )

        if not limiter.is_allowed(rate_limit_key):
            remaining = limiter.get_remaining(rate_limit_key)
            reset_time = limiter.get_reset_time(rate_limit_key)

            logger.warning(
                f"Rate limit exceeded for {rate_limit_key}",
                extra={"request_id": getattr(request.state, "request_id", None)}
            )

            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "request_id": getattr(request.state, "request_id", None),
                    "retry_after": int((reset_time.timestamp() - datetime.now(timezone.utc).timestamp())) if reset_time else 60
                },
                headers={
                    "Retry-After": str(int((reset_time.timestamp() - datetime.now(timezone.utc).timestamp())) if reset_time else 60)
                }
            )

        response = await call_next(request)

        # Add rate limit headers
        remaining = limiter.get_remaining(rate_limit_key)
        reset_time = limiter.get_reset_time(rate_limit_key)

        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        if reset_time:
            response.headers["X-RateLimit-Reset"] = str(int(reset_time.timestamp()))

        return response

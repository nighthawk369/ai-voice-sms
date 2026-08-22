"""Middleware for tenant isolation, error handling, and request logging"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from uuid import uuid4
import logging
import time
import json

logger = logging.getLogger(__name__)


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

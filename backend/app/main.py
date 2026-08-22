"""Main FastAPI application"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import logging

from app.config import get_settings
from app.routes import router
from app.routes_enhanced import router_enhanced
from app.routes_orchestrator import router as router_orchestrator
from app.routes_phases_8_12 import router as router_phases_8_12
from app.db import init_db

settings = get_settings()

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Configuration
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
REQUEST_TIMEOUT = 60  # seconds


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Enforce maximum request body size"""

    async def dispatch(self, request: Request, call_next):
        if "content-length" in request.headers:
            try:
                content_length = int(request.headers["content-length"])
                if content_length > MAX_REQUEST_SIZE:
                    return JSONResponse(
                        status_code=413,
                        content={"detail": f"Request body exceeds maximum size of {MAX_REQUEST_SIZE} bytes"},
                    )
            except ValueError:
                pass
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events with graceful shutdown"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    # Initialize database on startup
    await init_db()
    logger.info("Database initialized")

    yield  # App running

    # Graceful shutdown
    logger.info("Shutting down gracefully...")
    import asyncio

    # Close database connections
    try:
        await init_db(shutdown=True)
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")

    # Wait for any pending tasks (but don't wait forever)
    pending = asyncio.all_tasks()
    for task in pending:
        task.cancel()

    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Voice & SMS Platform for Field Service Businesses",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add middleware in reverse order (bottom to top execution)
from app.middleware import ErrorHandlingMiddleware, LoggingMiddleware, RequestIDMiddleware, TenantIsolationMiddleware, RateLimitMiddleware

app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(TenantIsolationMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)

# Add HTTPS redirect in production
if settings.ENVIRONMENT == "production":
    from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
    app.add_middleware(HTTPSRedirectMiddleware)
    logger.info("HTTPS redirect enabled for production")

# Add CORS middleware with environment-aware origins
cors_origins = settings.get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
    max_age=600,
)
logger.info(f"CORS configured for origins: {cors_origins}")


# Include routes
app.include_router(router, prefix="/api/v1")
app.include_router(router_enhanced, prefix="/api/v1")
app.include_router(router_orchestrator)
app.include_router(router_phases_8_12)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

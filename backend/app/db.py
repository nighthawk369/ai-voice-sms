"""Database connection and session management"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool, NullPool
from app.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

# Async engine for FastAPI with optimized connection pooling
db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

if settings.ENVIRONMENT == "production":
    # Production: use connection pooling
    engine = create_async_engine(
        db_url,
        echo=settings.DATABASE_ECHO,
        future=True,
        poolclass=QueuePool,
        pool_size=20,           # Keep 20 connections open
        max_overflow=10,        # Allow 10 additional connections
        pool_recycle=3600,      # Recycle every hour
        pool_pre_ping=True,     # Test connection before using
        echo_pool=False,
    )
    logger.info("Database: Production pooling configured (pool_size=20, max_overflow=10, recycle=3600s)")
else:
    # Development: simpler pooling
    engine = create_async_engine(
        db_url,
        echo=settings.DATABASE_ECHO,
        future=True,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=5,
        pool_pre_ping=True,
    )
    logger.info("Database: Development pooling configured (pool_size=5, max_overflow=5)")

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for ORM models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db(shutdown: bool = False):
    """Initialize database tables or shutdown connections"""
    if shutdown:
        await engine.dispose()
        logger.info("Database connections disposed")
    else:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized")

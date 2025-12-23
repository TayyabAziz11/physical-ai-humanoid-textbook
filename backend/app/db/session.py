"""
Database session management

Provides async SQLAlchemy session factory and dependency injection
for FastAPI routes.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)

from app.core.config import get_settings


# Get settings
settings = get_settings()

# Create async engine
# Note: asyncpg requires ssl to be True/False or ssl.SSLContext, not "require"
# Remove sslmode from URL and handle SSL via connect_args
import ssl as ssl_module
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Parse DATABASE_URL and remove sslmode/channel_binding parameters
parsed = urlparse(settings.DATABASE_URL)
query_params = parse_qs(parsed.query)

# Check if SSL is required
ssl_required = query_params.get("sslmode", [""])[0] == "require"

# Remove asyncpg-incompatible parameters
query_params.pop("sslmode", None)
query_params.pop("channel_binding", None)

# Rebuild URL without those parameters
new_query = urlencode(query_params, doseq=True)
clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

# Create SSL context if required
ssl_context = ssl_module.create_default_context() if ssl_required else None

engine = create_async_engine(
    clean_url,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    connect_args={"ssl": ssl_context} if ssl_context else {},
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session

    Yields:
        AsyncSession: Database session

    Usage in FastAPI:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            # Use db here
            pass
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

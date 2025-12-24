"""
Database session management (Railway + Neon SAFE)

Provides async SQLAlchemy session factory and dependency injection
for FastAPI routes.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from app.core.config import get_settings
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import ssl as ssl_module

# -------------------------
# Load settings
# -------------------------
settings = get_settings()

if not settings.DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

DATABASE_URL = settings.DATABASE_URL

# -------------------------
# FORCE asyncpg (CRITICAL)
# -------------------------
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )

# -------------------------
# Handle Neon SSL properly
# -------------------------
parsed = urlparse(DATABASE_URL)
query_params = parse_qs(parsed.query)

ssl_required = query_params.get("sslmode", [""])[0] == "require"

# Remove asyncpg-incompatible params
query_params.pop("sslmode", None)
query_params.pop("channel_binding", None)

clean_query = urlencode(query_params, doseq=True)
CLEAN_DATABASE_URL = urlunparse(
    (
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        clean_query,
        parsed.fragment,
    )
)

ssl_context = ssl_module.create_default_context() if ssl_required else None

# -------------------------
# Create async engine
# -------------------------
engine = create_async_engine(
    CLEAN_DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    connect_args={"ssl": ssl_context} if ssl_context else {},
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# -------------------------
# Dependency
# -------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

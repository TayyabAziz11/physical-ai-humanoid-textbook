"""
FastAPI dependency injection functions

Provides reusable dependencies for:
- Application settings
- Database sessions
- Qdrant client
- Logging
"""
from functools import lru_cache
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_client import QdrantClient

from app.core.config import Settings, get_settings as _get_settings
from app.core.logging import get_logger
from app.db.session import get_db as _get_db
from app.services.qdrant import get_qdrant_client


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings (singleton)

    This function is cached to ensure Settings is instantiated only once,
    which is important for performance and consistency.

    Returns:
        Settings: Application settings instance
    """
    return _get_settings()


# Type alias for dependency injection
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_app_logger():
    """
    Get application logger

    Returns:
        Logger instance
    """
    return get_logger()


# Database session dependency (Phase 3)
async def get_db():
    """
    Get async database session

    Yields:
        AsyncSession: Database session
    """
    async for session in _get_db():
        yield session


# Type alias for database dependency injection
DBDep = Annotated[AsyncSession, Depends(get_db)]


# Qdrant client dependency (Phase 4)
def get_qdrant() -> QdrantClient:
    """
    Get Qdrant vector database client

    Returns:
        QdrantClient: Qdrant client instance
    """
    return get_qdrant_client()


# Type alias for Qdrant dependency injection
QdrantDep = Annotated[QdrantClient, Depends(get_qdrant)]

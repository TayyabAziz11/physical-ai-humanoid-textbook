"""
Dependency injection helpers for FastAPI and other modules.
"""

from typing import AsyncGenerator

from app.core.config import get_settings
from app.core.config import Settings


# FastAPI-style dependency
def get_settings_dep() -> Settings:
    """
    Dependency wrapper for settings.
    Returns the cached Settings instance.
    """
    return get_settings()


# Placeholder async DB session dependency
async def get_db() -> AsyncGenerator[None, None]:
    """
    Database session dependency.

    NOTE:
    This is intentionally a placeholder because DB integration
    is tested separately in phase 4 of the backend setup.
    """
    try:
        # In the real system, you would yield your asyncpg session or SQLAlchemy session
        yield None
    finally:
        # Close DB session if needed
        pass

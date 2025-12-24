"""
Database initialization script

Creates all database tables defined in the ORM models.
Run this script to initialize the database schema.

Usage:
    uv run python backend/scripts/init_db.py
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from app.db.base import Base
from app.models.database import ChatSession, ChatMessage  # noqa: F401 - Import to register models
from app.core.logging import setup_logging, get_logger


async def init_db():
    """Initialize database by creating all tables"""
    settings = get_settings()
    logger = setup_logging(settings.LOG_LEVEL)

    logger.info("Initializing database...")
    logger.info(f"Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'N/A'}")

    try:
        # Create async engine
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG
        )

        # Create all tables
        async with engine.begin() as conn:
            logger.info("Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)

        logger.info("✅ Database initialized successfully!")
        logger.info("Tables created: chat_sessions, chat_messages")

        await engine.dispose()

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(init_db())

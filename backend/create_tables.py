#!/usr/bin/env python3
"""
Create database tables for RAG Study Assistant

This script creates all tables defined in the database models.
Run this once to initialize the database schema.

Usage:
    python create_tables.py
"""
import asyncio
from app.db.base import Base
from app.db.session import engine
from app.models.database import ChatSession, ChatMessage


async def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    async with engine.begin() as conn:
        # Drop all tables (use with caution!)
        # await conn.run_sync(Base.metadata.drop_all)

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    print("✓ Database tables created successfully!")
    print("  - chat_sessions")
    print("  - chat_messages")


async def main():
    """Main entry point"""
    try:
        await create_tables()
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

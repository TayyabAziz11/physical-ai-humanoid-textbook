"""
Application Configuration using Pydantic Settings

Railway-compatible configuration with proper environment variable handling.
"""

import json
import os
from functools import lru_cache
from typing import Any

from pydantic import field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Railway automatically provides:
    - PORT (exposed port)
    - RAILWAY_ENVIRONMENT (production/staging/development)
    - RAILWAY_PROJECT_NAME
    - RAILWAY_SERVICE_NAME

    You must set manually in Railway:
    - OPENAI_API_KEY
    - QDRANT_URL
    - QDRANT_API_KEY
    - DATABASE_URL (Neon Postgres connection string)
    """

    # ============================================
    # Application Configuration
    # ============================================
    APP_NAME: str = "RAG Study Assistant"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode (set to False in production)"
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )

    # Railway-specific (optional, auto-provided)
    RAILWAY_ENVIRONMENT: str | None = Field(
        default=None,
        description="Railway environment name"
    )
    PORT: int = Field(
        default=8000,
        description="Port to run the server (Railway sets this automatically)"
    )

    # ============================================
    # OpenAI Configuration
    # ============================================
    OPENAI_API_KEY: str = Field(
        ...,
        description="OpenAI API key (required)"
    )
    OPENAI_CHAT_MODEL: str = Field(
        default="gpt-4-turbo-preview",
        description="OpenAI chat completion model"
    )
    OPENAI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model (1536 dimensions)"
    )

    # ============================================
    # Qdrant Vector Database
    # ============================================
    QDRANT_URL: str = Field(
        ...,
        description="Qdrant server URL (e.g., https://your-cluster.qdrant.io)"
    )
    QDRANT_API_KEY: str = Field(
        ...,
        description="Qdrant API key"
    )
    QDRANT_COLLECTION: str = Field(
        default="textbook_chunks",
        description="Qdrant collection name for textbook chunks"
    )

    # ============================================
    # Neon Postgres Database
    # ============================================
    DATABASE_URL: str = Field(
        ...,
        description="Neon Postgres connection string (e.g., postgresql://user:pass@host/db)"
    )

    # ============================================
    # CORS Configuration
    # ============================================
    CORS_ORIGINS: list[str] = Field(
        default_factory=list,
        description="Allowed CORS origins (JSON array or comma-separated string)"
    )

    # ============================================
    # RAG Configuration
    # ============================================
    RAG_TOP_K_CHUNKS: int = Field(
        default=7,
        description="Number of top chunks to retrieve for RAG"
    )
    RAG_CHUNK_MAX_TOKENS: int = Field(
        default=500,
        description="Maximum tokens per chunk"
    )
    MAX_QUESTION_TOKENS: int = Field(
        default=2000,
        description="Maximum tokens for user questions"
    )
    MAX_SELECTION_TOKENS: int = Field(
        default=5000,
        description="Maximum tokens for selected text"
    )
    CHUNK_RETRIEVAL_LIMIT: int = Field(
        default=10,
        description="Maximum chunks to retrieve from Qdrant"
    )

    # ============================================
    # Pydantic Settings Configuration
    # ============================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra env vars (Railway adds many)
    )

    # ============================================
    # Validators
    # ============================================

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """
        Parse CORS_ORIGINS from JSON string or comma-separated string.

        Examples:
            CORS_ORIGINS='["http://localhost:3000", "https://example.com"]'
            CORS_ORIGINS='http://localhost:3000,https://example.com'
        """
        if isinstance(v, str):
            # Try JSON first
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass

            # Fall back to comma-separated
            return [origin.strip() for origin in v.split(",") if origin.strip()]

        return v if isinstance(v, list) else []

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v: Any) -> bool:
        """
        Parse DEBUG from various string formats.

        Examples:
            DEBUG='true' → True
            DEBUG='1' → True
            DEBUG='false' → False
        """
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)

    # ============================================
    # Helper Properties
    # ============================================

    @property
    def is_production(self) -> bool:
        """Check if running in Railway production environment."""
        return self.RAILWAY_ENVIRONMENT == "production"

    @property
    def is_railway(self) -> bool:
        """Check if running on Railway platform."""
        return self.RAILWAY_ENVIRONMENT is not None


@lru_cache
def get_settings() -> Settings:
    """
    Return cached application settings (singleton).

    Uses LRU cache to ensure Settings is instantiated only once,
    which is important for performance and consistency.

    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Export settings singleton for direct imports
# Usage: from app.core.config import settings
settings = get_settings()


# ============================================
# Railway Deployment Notes
# ============================================
"""
Railway Environment Variables Setup:

1. Required Variables (set in Railway dashboard):
   ✓ OPENAI_API_KEY=sk-...
   ✓ QDRANT_URL=https://your-cluster.qdrant.io
   ✓ QDRANT_API_KEY=...
   ✓ DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

2. Optional Variables:
   - DEBUG=false (recommended for production)
   - LOG_LEVEL=INFO
   - CORS_ORIGINS=["https://your-frontend.com"]
   - APP_NAME="Custom Name"

3. Auto-Provided by Railway:
   - PORT (Railway sets this automatically)
   - RAILWAY_ENVIRONMENT
   - RAILWAY_PROJECT_NAME
   - RAILWAY_SERVICE_NAME

4. Uvicorn Start Command:
   uvicorn main:app --host 0.0.0.0 --port $PORT

   Railway will automatically inject $PORT
"""

<<<<<<< HEAD
"""Application Configuration using Pydantic Settings."""

import json
from typing import Any
from pydantic import field_validator
=======
"""
Configuration management using Pydantic Settings.

All configuration is loaded from environment variables or a .env file.
"""

from typing import List
from functools import lru_cache
from pydantic import Field
>>>>>>> 002-rag-backend-study-assistant
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

<<<<<<< HEAD
    # Application Configuration
    APP_NAME: str = "RAG Study Assistant"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_CHAT_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Qdrant Vector Database
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str = "textbook_chunks"

    # Neon Postgres Database (optional)
    DATABASE_URL: str | None = None

    # CORS Configuration
    CORS_ORIGINS: list[str] = []

    # RAG Configuration
    RAG_TOP_K_CHUNKS: int = 7
    RAG_CHUNK_MAX_TOKENS: int = 500
    MAX_QUESTION_TOKENS: int = 2000
    MAX_SELECTION_TOKENS: int = 5000
    CHUNK_RETRIEVAL_LIMIT: int = 10

=======
    # Application metadata
    APP_NAME: str = "RAG Study Assistant"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Logging configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR)")

    # OpenAI configuration
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    OPENAI_CHAT_MODEL: str = Field(
        default="gpt-4-turbo-preview",
        description="OpenAI chat model for answer generation"
    )
    OPENAI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model for vector generation"
    )

    # Qdrant configuration
    QDRANT_URL: str = Field(..., description="Qdrant Cloud cluster URL")
    QDRANT_API_KEY: str = Field(..., description="Qdrant API key")
    QDRANT_COLLECTION: str = Field(
        default="textbook_chunks",
        description="Qdrant collection name for textbook chunks"
    )

    # Neon/Postgres configuration
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string (asyncpg)")

    # CORS configuration
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )

    # RAG configuration
    RAG_TOP_K_CHUNKS: int = Field(
        default=7,
        description="Number of chunks to retrieve for RAG context"
    )
    RAG_CHUNK_MAX_TOKENS: int = Field(
        default=500,
        description="Maximum token count per chunk during indexing"
    )
    MAX_QUESTION_TOKENS: int = Field(
        default=2000,
        description="Maximum tokens allowed in user question"
    )
    MAX_SELECTION_TOKENS: int = Field(
        default=5000,
        description="Maximum tokens allowed in selected text"
    )

    # Pydantic Settings config
>>>>>>> 002-rag-backend-study-assistant
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

<<<<<<< HEAD
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS_ORIGINS from JSON string or list."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If not valid JSON, split by comma
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


# Singleton instance
settings = Settings()
=======

@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()


# Pre-instantiated settings for direct imports
settings = get_settings()
>>>>>>> 002-rag-backend-study-assistant

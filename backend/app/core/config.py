"""Application Configuration using Pydantic Settings."""

import json
from typing import Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

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

"""
Configuration management using Pydantic Settings

All configuration is loaded from environment variables or .env file.
"""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application metadata
    APP_NAME: str = "RAG Study Assistant"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR)")

    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    OPENAI_CHAT_MODEL: str = Field(
        default="gpt-4-turbo-preview",
        description="OpenAI chat model for answer generation"
    )
    OPENAI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model for vector generation"
    )

    # Qdrant Vector Database
    QDRANT_URL: str = Field(..., description="Qdrant Cloud cluster URL")
    QDRANT_API_KEY: str = Field(..., description="Qdrant API key")
    QDRANT_COLLECTION: str = Field(
        default="textbook_chunks",
        description="Qdrant collection name for textbook chunks"
    )

    # Neon Postgres Database
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string (asyncpg)")

    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )

    # RAG Configuration
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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


def get_settings() -> Settings:
    """
    Get application settings (cached singleton)

    Returns:
        Settings: Application settings instance
    """
    return Settings()

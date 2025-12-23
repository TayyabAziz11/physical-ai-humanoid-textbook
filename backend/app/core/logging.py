<<<<<<< HEAD
"""Logging configuration for the application."""

import logging
import sys
from app.core.config import settings


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if handlers haven't been added yet
    if not logger.handlers:
        # Set log level from settings
        log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(log_level)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        # Create formatter
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(console_handler)

        # Prevent propagation to root logger
        logger.propagate = False

    return logger
=======
"""
Structured logging configuration.

Configures Python's logging module with consistent formatting and
log levels based on application settings.
"""

import logging
import sys
from typing import Optional

from app.core.config import settings


def setup_logging(log_level: str = None) -> logging.Logger:
    """
    Configure application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Logger instance for the application.
    """
    log_level = log_level or settings.LOG_LEVEL
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger("rag_backend")
    logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates when reloading
    logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    # Structured formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Prevent double logging
    logger.propagate = False

    logger.info(f"Logging initialized with level: {log_level}")

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (defaults to 'rag_backend')

    Returns:
        Logger instance.
    """
    return logging.getLogger(name or "rag_backend")


def log_config_on_startup():
    """
    Log a summary of key application settings.
    Required by verify_config.py.
    """
    logger = get_logger("config")

    logger.info("=== Application Configuration Summary ===")
    logger.info(f"APP_NAME: {settings.APP_NAME}")
    logger.info(f"APP_VERSION: {settings.APP_VERSION}")
    logger.info(f"LOG_LEVEL: {settings.LOG_LEVEL}")
    logger.info(f"DEBUG: {settings.DEBUG}")

    logger.info("--- OpenAI ---")
    logger.info(f"OPENAI_CHAT_MODEL: {settings.OPENAI_CHAT_MODEL}")
    logger.info(f"OPENAI_EMBEDDING_MODEL: {settings.OPENAI_EMBEDDING_MODEL}")

    logger.info("--- Qdrant ---")
    logger.info(f"QDRANT_URL: {settings.QDRANT_URL}")
    logger.info(f"QDRANT_COLLECTION: {settings.QDRANT_COLLECTION}")

    logger.info("--- Postgres ---")
    logger.info(f"DATABASE_URL: {settings.DATABASE_URL}")

    logger.info("--- RAG ---")
    logger.info(f"RAG_TOP_K_CHUNKS: {settings.RAG_TOP_K_CHUNKS}")
    logger.info(f"RAG_CHUNK_MAX_TOKENS: {settings.RAG_CHUNK_MAX_TOKENS}")
    logger.info(f"MAX_QUESTION_TOKENS: {settings.MAX_QUESTION_TOKENS}")
    logger.info(f"MAX_SELECTION_TOKENS: {settings.MAX_SELECTION_TOKENS}")

    logger.info("--- CORS ---")
    logger.info(f"CORS_ORIGINS: {settings.CORS_ORIGINS}")

    logger.info("==========================================")
>>>>>>> 002-rag-backend-study-assistant

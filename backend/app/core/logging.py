"""Logging configuration for the application."""

import logging
import sys
from app.core.config import get_settings


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
        settings = get_settings()  # ✅ CALL the function

        # Set log level from settings (fallback to INFO)
        log_level = getattr(
            logging,
            settings.LOG_LEVEL.upper(),
            logging.INFO
        )

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

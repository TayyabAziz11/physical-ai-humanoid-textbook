"""
Security utilities for input sanitization and CORS configuration
"""
import re
from typing import Optional


def sanitize_user_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize user input to prevent injection attacks and prompt manipulation

    Args:
        text: User-provided text (question, selected text, etc.)
        max_length: Optional maximum length to truncate to

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove null bytes
    sanitized = text.replace("\x00", "")

    # Remove excessive whitespace while preserving newlines
    sanitized = re.sub(r"[ \t]+", " ", sanitized)
    sanitized = re.sub(r"\n{3,}", "\n\n", sanitized)

    # Strip leading/trailing whitespace
    sanitized = sanitized.strip()

    # Truncate if max_length specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def validate_question(question: str, max_tokens: int = 2000) -> tuple[bool, Optional[str]]:
    """
    Validate user question

    Args:
        question: User's question text
        max_tokens: Maximum token count (approximate by character count)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not question or not question.strip():
        return False, "Please enter a question."

    # Approximate token count (rough estimate: 4 chars = 1 token)
    approx_tokens = len(question) // 4

    if approx_tokens > max_tokens:
        return False, f"Question is too long. Please keep it under {max_tokens} tokens (~{max_tokens * 4} characters)."

    return True, None


def validate_selected_text(selected_text: str, max_tokens: int = 5000) -> tuple[bool, Optional[str]]:
    """
    Validate selected text

    Args:
        selected_text: User's selected text
        max_tokens: Maximum token count (approximate by character count)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not selected_text or not selected_text.strip():
        return True, None  # Selected text is optional

    # Approximate token count (rough estimate: 4 chars = 1 token)
    approx_tokens = len(selected_text) // 4

    if approx_tokens > max_tokens:
        return False, f"Selected text is too long. Please select a smaller passage (under {max_tokens} tokens)."

    return True, None


def get_cors_config(allowed_origins: list[str]) -> dict:
    """
    Get CORS middleware configuration

    Args:
        allowed_origins: List of allowed origin URLs

    Returns:
        Dictionary of CORS configuration parameters
    """
    return {
        "allow_origins": allowed_origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"],
    }

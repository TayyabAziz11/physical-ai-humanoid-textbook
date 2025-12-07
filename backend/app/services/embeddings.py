"""
Embeddings service

Provides text embedding generation using OpenAI API.
"""
from typing import List
from openai import OpenAI, OpenAIError

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Lazy-initialized OpenAI client
_openai_client = None


def get_openai_client() -> OpenAI:
    """
    Get or create OpenAI client (lazy initialization)

    Returns:
        OpenAI: OpenAI client instance

    Raises:
        ValueError: If OPENAI_API_KEY is not configured
    """
    global _openai_client

    if _openai_client is not None:
        return _openai_client

    settings = get_settings()

    if not settings.OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is not configured. "
            "Please set it in your .env file or environment variables."
        )

    logger.info("Initializing OpenAI client for embeddings")
    _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    return _openai_client


async def embed_text(text: str) -> List[float]:
    """
    Generate embedding vector for text using OpenAI API

    Args:
        text: Text to embed (will be truncated if too long)

    Returns:
        List[float]: Embedding vector (typically 1536 dimensions for text-embedding-3-small)

    Raises:
        ValueError: If text is empty or API key not configured
        OpenAIError: If OpenAI API call fails

    Example:
        >>> embedding = await embed_text("What is ROS 2?")
        >>> len(embedding)
        1536
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    settings = get_settings()
    client = get_openai_client()

    try:
        logger.debug(f"Generating embedding for text (length: {len(text)} chars)")

        # Generate embedding
        response = client.embeddings.create(
            input=text.strip(),
            model=settings.OPENAI_EMBEDDING_MODEL
        )

        embedding = response.data[0].embedding

        logger.debug(f"Generated embedding with {len(embedding)} dimensions")

        return embedding

    except OpenAIError as e:
        logger.error(f"OpenAI API error while generating embedding: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error while generating embedding: {e}")
        raise


async def embed_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in a single API call (more efficient)

    Args:
        texts: List of texts to embed

    Returns:
        List[List[float]]: List of embedding vectors

    Raises:
        ValueError: If texts is empty or contains empty strings
        OpenAIError: If OpenAI API call fails

    Example:
        >>> embeddings = await embed_batch(["Question 1", "Question 2"])
        >>> len(embeddings)
        2
    """
    if not texts:
        raise ValueError("Texts list cannot be empty")

    # Filter out empty strings
    valid_texts = [t.strip() for t in texts if t and t.strip()]

    if not valid_texts:
        raise ValueError("All texts are empty after stripping whitespace")

    settings = get_settings()
    client = get_openai_client()

    try:
        logger.debug(f"Generating embeddings for {len(valid_texts)} texts")

        # Generate embeddings in batch
        response = client.embeddings.create(
            input=valid_texts,
            model=settings.OPENAI_EMBEDDING_MODEL
        )

        # Extract embeddings in order
        embeddings = [item.embedding for item in response.data]

        logger.debug(f"Generated {len(embeddings)} embeddings")

        return embeddings

    except OpenAIError as e:
        logger.error(f"OpenAI API error while generating batch embeddings: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error while generating batch embeddings: {e}")
        raise

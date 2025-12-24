"""
Qdrant vector database client

Provides client initialization and collection schema for the textbook RAG system.
"""
from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, CollectionInfo
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Collection schema constants
VECTOR_SIZE = 1536  # OpenAI text-embedding-3-small dimension
DISTANCE_METRIC = Distance.COSINE

# Singleton instance
_qdrant_client: Optional[QdrantClient] = None


def get_qdrant_client() -> QdrantClient:
    """
    Get or create Qdrant client instance (singleton pattern)

    Returns:
        QdrantClient: Initialized Qdrant client

    Raises:
        Exception: If client initialization fails
    """
    global _qdrant_client

    if _qdrant_client is not None:
        return _qdrant_client

    settings = get_settings()

    try:
        logger.info(f"Initializing Qdrant client: {settings.QDRANT_URL}")

        _qdrant_client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=30.0,
        )

        logger.info("✅ Qdrant client initialized successfully")
        return _qdrant_client

    except Exception as e:
        logger.error(f"❌ Failed to initialize Qdrant client: {e}")
        raise


def ensure_collection_exists() -> bool:
    """
    Ensure the Qdrant collection exists with proper schema

    Creates the collection if it doesn't exist.
    If it exists, validates the vector configuration.

    Returns:
        bool: True if collection exists or was created successfully

    Raises:
        Exception: If collection creation or validation fails
    """
    settings = get_settings()
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION

    try:
        # Check if collection exists
        collections = client.get_collections().collections
        collection_exists = any(c.name == collection_name for c in collections)

        if collection_exists:
            logger.info(f"Collection '{collection_name}' already exists")

            # Validate vector configuration
            collection_info: CollectionInfo = client.get_collection(collection_name)
            vector_size = collection_info.config.params.vectors.size
            distance = collection_info.config.params.vectors.distance

            if vector_size != VECTOR_SIZE:
                logger.warning(
                    f"Collection vector size mismatch: expected {VECTOR_SIZE}, got {vector_size}"
                )

            if distance != DISTANCE_METRIC:
                logger.warning(
                    f"Collection distance metric mismatch: expected {DISTANCE_METRIC}, got {distance}"
                )

            return True

        # Create collection
        logger.info(f"Creating collection '{collection_name}' with vector_size={VECTOR_SIZE}")

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=DISTANCE_METRIC
            )
        )

        logger.info(f"✅ Collection '{collection_name}' created successfully")
        return True

    except UnexpectedResponse as e:
        logger.error(f"❌ Qdrant API error: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to ensure collection exists: {e}")
        raise


def test_qdrant_connection() -> tuple[bool, str]:
    """
    Test Qdrant connection and collection availability

    Returns:
        tuple[bool, str]: (success, status_message)
    """
    try:
        client = get_qdrant_client()
        settings = get_settings()

        # Test basic connectivity
        collections = client.get_collections()

        # Check if our collection exists
        collection_exists = any(
            c.name == settings.QDRANT_COLLECTION
            for c in collections.collections
        )

        if collection_exists:
            # Get collection stats
            collection_info = client.get_collection(settings.QDRANT_COLLECTION)
            point_count = collection_info.points_count
            return True, f"connected (collection: {settings.QDRANT_COLLECTION}, points: {point_count})"
        else:
            return True, f"connected (collection '{settings.QDRANT_COLLECTION}' not found)"

    except Exception as e:
        return False, f"error: {str(e)[:50]}"


def close_qdrant_client():
    """
    Close the Qdrant client connection

    Call this during application shutdown.
    """
    global _qdrant_client

    if _qdrant_client is not None:
        try:
            _qdrant_client.close()
            logger.info("Qdrant client closed")
        except Exception as e:
            logger.warning(f"Error closing Qdrant client: {e}")
        finally:
            _qdrant_client = None

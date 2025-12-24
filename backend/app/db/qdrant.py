"""Qdrant vector database client initialization and management."""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Singleton Qdrant client instance
_qdrant_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    """
    Get or create Qdrant client instance (singleton pattern).

    Returns:
        QdrantClient instance connected to configured Qdrant server
    """
    global _qdrant_client

    if _qdrant_client is None:
        settings = get_settings()

        logger.info(f"Initializing Qdrant client: {settings.QDRANT_URL}")

        _qdrant_client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=30,
        )

        logger.info("Qdrant client initialized successfully")

    return _qdrant_client


async def init_collection() -> None:
    """
    Initialize Qdrant collection if it doesn't exist.

    Creates collection with:
    - Vector size: 1536 (text-embedding-3-small dimension)
    - Distance metric: Cosine similarity
    """
    settings = get_settings()
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION

    try:
        collections = client.get_collections()
        collection_names = [col.name for col in collections.collections]

        if collection_name in collection_names:
            logger.info(f"Collection '{collection_name}' already exists")
            return

        logger.info(f"Creating collection '{collection_name}'")

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1536,
                distance=Distance.COSINE,
            ),
        )

        logger.info(f"Collection '{collection_name}' created successfully")

    except Exception as exc:
        logger.exception("Error initializing Qdrant collection")
        raise exc

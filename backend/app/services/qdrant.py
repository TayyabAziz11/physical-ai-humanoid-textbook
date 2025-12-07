"""
Qdrant vector database service

Provides collection management and vector search functionality.
"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    ScoredPoint
)
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Collection schema constants
VECTOR_SIZE = 1536  # OpenAI text-embedding-3-small dimension
DISTANCE_METRIC = Distance.COSINE

# Lazy-initialized Qdrant client
_qdrant_client: Optional[QdrantClient] = None


@dataclass
class EmbeddingChunk:
    """
    Data model for embedding chunks with metadata

    Represents a chunk of text with its embedding and associated metadata
    for storage in Qdrant vector database.
    """
    id: str  # Unique identifier (UUID)
    vector: List[float]  # Embedding vector
    doc_path: str  # Document path (e.g., "docs/module-1-ros2/chapter-1-basics.mdx")
    module_id: Optional[str]  # Module identifier (e.g., "module-1-ros2")
    heading: str  # Section heading
    chunk_text: str  # Actual text content
    chunk_index: int  # Index within the section
    total_chunks: int  # Total chunks in the section

    def to_point_struct(self) -> PointStruct:
        """
        Convert to Qdrant PointStruct for upsert

        Returns:
            PointStruct: Qdrant point with vector and payload
        """
        return PointStruct(
            id=self.id,
            vector=self.vector,
            payload={
                "doc_path": self.doc_path,
                "module_id": self.module_id,
                "heading": self.heading,
                "chunk_text": self.chunk_text,
                "chunk_index": self.chunk_index,
                "total_chunks": self.total_chunks
            }
        )


def get_qdrant_client() -> QdrantClient:
    """
    Get or create Qdrant client (lazy initialization)

    Returns:
        QdrantClient: Qdrant client instance

    Raises:
        ValueError: If QDRANT_URL or QDRANT_API_KEY not configured
        Exception: If client initialization fails
    """
    global _qdrant_client

    if _qdrant_client is not None:
        return _qdrant_client

    settings = get_settings()

    if not settings.QDRANT_URL:
        raise ValueError(
            "QDRANT_URL is not configured. "
            "Please set it in your .env file or environment variables."
        )

    if not settings.QDRANT_API_KEY:
        raise ValueError(
            "QDRANT_API_KEY is not configured. "
            "Please set it in your .env file or environment variables."
        )

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
    Ensure the Qdrant collection exists with proper vector configuration

    Creates the collection if it doesn't exist. If it exists, validates
    the vector size and distance metric match expected values.

    Returns:
        bool: True if collection exists or was created successfully

    Raises:
        ValueError: If collection exists with incompatible configuration
        Exception: If collection creation fails

    Example:
        >>> ensure_collection_exists()
        True
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
            collection_info = client.get_collection(collection_name)
            vector_size = collection_info.config.params.vectors.size
            distance = collection_info.config.params.vectors.distance

            if vector_size != VECTOR_SIZE:
                raise ValueError(
                    f"Collection has incompatible vector size: "
                    f"expected {VECTOR_SIZE}, got {vector_size}"
                )

            if distance != DISTANCE_METRIC:
                logger.warning(
                    f"Collection distance metric differs: "
                    f"expected {DISTANCE_METRIC}, got {distance}"
                )

            return True

        # Create collection
        logger.info(
            f"Creating collection '{collection_name}' "
            f"(vector_size={VECTOR_SIZE}, distance={DISTANCE_METRIC})"
        )

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=DISTANCE_METRIC
            )
        )

        logger.info(f"✅ Collection '{collection_name}' created successfully")
        return True

    except ValueError:
        raise
    except UnexpectedResponse as e:
        logger.error(f"❌ Qdrant API error: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to ensure collection exists: {e}")
        raise


def upsert_embeddings(chunks: List[EmbeddingChunk]) -> int:
    """
    Upsert (insert or update) embedding chunks into Qdrant

    Args:
        chunks: List of EmbeddingChunk objects to upsert

    Returns:
        int: Number of chunks successfully upserted

    Raises:
        ValueError: If chunks list is empty
        Exception: If upsert operation fails

    Example:
        >>> chunk = EmbeddingChunk(
        ...     id="uuid-here",
        ...     vector=[0.1, 0.2, ...],
        ...     doc_path="docs/intro.md",
        ...     module_id="intro",
        ...     heading="Introduction",
        ...     chunk_text="This is the intro...",
        ...     chunk_index=0,
        ...     total_chunks=1
        ... )
        >>> upsert_embeddings([chunk])
        1
    """
    if not chunks:
        raise ValueError("Chunks list cannot be empty")

    settings = get_settings()
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION

    try:
        logger.info(f"Upserting {len(chunks)} chunks to '{collection_name}'")

        # Convert chunks to PointStruct
        points = [chunk.to_point_struct() for chunk in chunks]

        # Upsert to Qdrant
        client.upsert(
            collection_name=collection_name,
            points=points
        )

        logger.info(f"✅ Successfully upserted {len(chunks)} chunks")
        return len(chunks)

    except Exception as e:
        logger.error(f"❌ Failed to upsert embeddings: {e}")
        raise


def search_similar(
    query_vector: List[float],
    limit: int = 7,
    doc_path_filter: Optional[str] = None,
    module_id_filter: Optional[str] = None
) -> List[ScoredPoint]:
    """
    Search for similar vectors in Qdrant

    Args:
        query_vector: Query embedding vector
        limit: Maximum number of results to return (default: 7)
        doc_path_filter: Optional filter by exact doc_path
        module_id_filter: Optional filter by module_id

    Returns:
        List[ScoredPoint]: Scored search results with metadata

    Raises:
        ValueError: If query_vector is empty or has wrong dimensions
        Exception: If search operation fails

    Example:
        >>> results = search_similar(
        ...     query_vector=[0.1, 0.2, ...],
        ...     limit=5,
        ...     module_id_filter="module-1-ros2"
        ... )
        >>> for result in results:
        ...     print(result.payload["heading"], result.score)
    """
    if not query_vector:
        raise ValueError("Query vector cannot be empty")

    if len(query_vector) != VECTOR_SIZE:
        raise ValueError(
            f"Query vector has wrong dimensions: "
            f"expected {VECTOR_SIZE}, got {len(query_vector)}"
        )

    settings = get_settings()
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION

    try:
        # Build filter conditions
        filter_conditions = []

        if doc_path_filter:
            filter_conditions.append(
                FieldCondition(
                    key="doc_path",
                    match=MatchValue(value=doc_path_filter)
                )
            )

        if module_id_filter:
            filter_conditions.append(
                FieldCondition(
                    key="module_id",
                    match=MatchValue(value=module_id_filter)
                )
            )

        # Create filter if conditions exist
        search_filter = None
        if filter_conditions:
            search_filter = Filter(must=filter_conditions)

        logger.info(
            f"Searching '{collection_name}' (limit={limit}, "
            f"filters={len(filter_conditions)})"
        )

        # Execute search
        results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=search_filter,
            with_payload=True
        )

        logger.info(f"Found {len(results)} results")
        return results

    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        raise


def close_qdrant_client():
    """
    Close the Qdrant client connection

    Should be called during application shutdown to clean up resources.
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

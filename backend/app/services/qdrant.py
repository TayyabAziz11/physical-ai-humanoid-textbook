"""
Qdrant async client wrapper for Study Assistant.

Features:
- Collection management (create, ensure exists)
- Embedding storage (upsert)
- Similarity search (async)
- Deletion by document path
- Proper async client cleanup
"""

from typing import Any, List, Optional, Sequence
from dataclasses import dataclass
from uuid import uuid4
import asyncio

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
)

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# -------------------
# Data models
# -------------------
@dataclass
class EmbeddingChunk:
    id: str
    vector: list[float]
    doc_path: str
    module_id: str
    heading: str
    chunk_index: int
    text: str


@dataclass
class SearchResult:
    id: str
    score: float
    doc_path: str
    module_id: str
    heading: str
    chunk_index: int
    text: str


# -------------------
# Async client management
# -------------------
_client: Optional[AsyncQdrantClient] = None


def get_qdrant_client() -> AsyncQdrantClient:
    """Get or create async Qdrant client."""
    global _client
    if _client is None:
        if not settings.QDRANT_URL or not settings.QDRANT_API_KEY:
            raise ValueError("QDRANT_URL or QDRANT_API_KEY not configured")
        _client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
    return _client


async def close_qdrant_client() -> None:
    """Close async Qdrant client if open."""
    global _client
    if _client:
        await _client.close()
        _client = None


# -------------------
# Collection management
# -------------------
async def ensure_collection_exists(
    collection_name: Optional[str] = None,
    vector_size: int = 1536,
    distance: Distance = Distance.COSINE,
) -> bool:
    """Ensure collection exists, create if missing."""
    client = get_qdrant_client()
    collection_name = collection_name or settings.QDRANT_COLLECTION

    collections = await client.get_collections()
    existing_names = [col.name for col in collections.collections]

    if collection_name in existing_names:
        return False

    await client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=distance),
    )

    await create_payload_indexes(collection_name)
    logger.info(f"Created Qdrant collection: {collection_name}")
    return True


async def create_payload_indexes(collection_name: str) -> None:
    """Create indexes for filtering."""
    client = get_qdrant_client()
    for field_name, schema in [
        ("doc_path", PayloadSchemaType.KEYWORD),
        ("chunk_index", PayloadSchemaType.INTEGER),
        ("module_id", PayloadSchemaType.KEYWORD),
    ]:
        await client.create_payload_index(
            collection_name=collection_name,
            field_name=field_name,
            field_schema=schema,
        )


# -------------------
# Embedding operations
# -------------------
async def upsert_embeddings(
    chunks: Sequence[EmbeddingChunk], collection_name: Optional[str] = None
) -> None:
    if not chunks:
        raise ValueError("Chunks list cannot be empty")

    client = get_qdrant_client()
    collection_name = collection_name or settings.QDRANT_COLLECTION

    points = [
        PointStruct(
            id=uuid4(),
            vector=chunk.vector,
            payload={
                "chunk_id": chunk.id,
                "doc_path": chunk.doc_path,
                "module_id": chunk.module_id,
                "heading": chunk.heading,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
            },
        )
        for chunk in chunks
    ]

    await client.upsert(collection_name=collection_name, points=points)
    logger.info(f"Upserted {len(points)} embeddings into {collection_name}")


async def search_similar(
    query_vector: list[float],
    limit: int = 10,
    collection_name: Optional[str] = None,
    doc_path: Optional[str] = None,
    module_id: Optional[str] = None,
    score_threshold: Optional[float] = None,
) -> List[SearchResult]:
    """Search for similar embeddings with optional filters."""
    client = get_qdrant_client()
    collection_name = collection_name or settings.QDRANT_COLLECTION

    must_conditions = []
    if doc_path:
        must_conditions.append(FieldCondition(key="doc_path", match=MatchValue(value=doc_path)))
    if module_id:
        must_conditions.append(FieldCondition(key="module_id", match=MatchValue(value=module_id)))

    query_filter = Filter(must=must_conditions) if must_conditions else None

    # AsyncQdrantClient uses .search() method
    response = await client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=limit,
        query_filter=query_filter,
        score_threshold=score_threshold,
        with_payload=True,
    )

    results = [
        SearchResult(
            id=str(point.id),
            score=point.score,
            doc_path=point.payload.get("doc_path", ""),
            module_id=point.payload.get("module_id", ""),
            heading=point.payload.get("heading", ""),
            chunk_index=point.payload.get("chunk_index", 0),
            text=point.payload.get("text", ""),
        )
        for point in response
    ]
    logger.info(f"Found {len(results)} similar chunks in {collection_name}")
    return results


# -------------------
# Deletion operations
# -------------------
async def delete_by_doc_path(doc_path: str, collection_name: Optional[str] = None) -> None:
    client = get_qdrant_client()
    collection_name = collection_name or settings.QDRANT_COLLECTION

    await client.delete(
        collection_name=collection_name,
        points_selector=Filter(
            must=[FieldCondition(key="doc_path", match=MatchValue(value=doc_path))]
        ),
    )
    logger.info(f"Deleted points with doc_path={doc_path} from {collection_name}")


# -------------------
# Utility
# -------------------
async def get_collection_info(collection_name: Optional[str] = None) -> dict[str, Any]:
    client = get_qdrant_client()
    collection_name = collection_name or settings.QDRANT_COLLECTION
    col = await client.get_collection(collection_name=collection_name)
    return {
        "name": collection_name,
        "points_count": col.points_count,
        "vectors_count": col.vectors_count,
        "status": col.status,
    }

"""Retrieval service for vector similarity search using Qdrant."""

from typing import List

from qdrant_client.models import FieldCondition, Filter, MatchValue, ScoredPoint

from app.core.config import settings
from app.core.logging import get_logger
from app.db.qdrant import get_qdrant_client
from app.models.chunk import ContentChunk
from app.services.embedder import EmbeddingService

logger = get_logger(__name__)


class RetrievalService:
    """Service for retrieving relevant chunks from Qdrant vector database."""

    def __init__(self, top_k: int | None = None):
        """
        Initialize the retrieval service.

        Args:
            top_k: Number of top results to retrieve (defaults to settings.RAG_TOP_K_CHUNKS)
        """
        self.client = get_qdrant_client()
        self.collection_name = settings.QDRANT_COLLECTION
        self.top_k = top_k or settings.RAG_TOP_K_CHUNKS
        self.embedder = EmbeddingService()
        self.logger = get_logger(__name__)

    async def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int | None = None,
        filters: dict[str, str] | None = None,
    ) -> list[ContentChunk]:
        """
        Retrieve relevant chunks for a query using vector similarity search.

        Args:
            query: User's question or query text
            top_k: Number of top results to retrieve (overrides instance default)
            filters: Optional metadata filters (e.g., {"source_file": "intro.md"})

        Returns:
            List of ContentChunk objects ordered by relevance (highest score first)
        """
        k = top_k or self.top_k

        self.logger.info(f"Retrieving top {k} chunks for query: '{query[:100]}...'")

        # Generate embedding for the query
        query_embedding = await self.embedder.embed_text(query)

        # Build Qdrant filter if provided
        qdrant_filter = self._build_filter(filters) if filters else None

        # Perform vector search
        search_results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=k,
            query_filter=qdrant_filter,
        ).points

        # Convert ScoredPoint results to ContentChunk objects
        chunks = [ContentChunk.from_qdrant_point(point) for point in search_results]

        self.logger.info(
            f"Retrieved {len(chunks)} chunks with scores: "
            f"{[f'{point.score:.3f}' for point in search_results[:3]]}"
        )

        return chunks

    async def retrieve_with_score_threshold(
        self,
        query: str,
        score_threshold: float = 0.7,
        top_k: int | None = None,
    ) -> list[tuple[ContentChunk, float]]:
        """
        Retrieve chunks that exceed a minimum similarity score threshold.

        Args:
            query: User's question or query text
            score_threshold: Minimum cosine similarity score (0.0 to 1.0)
            top_k: Maximum number of results to consider

        Returns:
            List of (ContentChunk, score) tuples for chunks above threshold
        """
        k = top_k or self.top_k

        self.logger.info(
            f"Retrieving chunks with score >= {score_threshold} for query: '{query[:100]}...'"
        )

        # Generate embedding for the query
        query_embedding = await self.embedder.embed_text(query)

        # Perform vector search
        search_results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=k,
            score_threshold=score_threshold,
        ).points

        # Convert results to (ContentChunk, score) tuples
        results = [
            (ContentChunk.from_qdrant_point(point), point.score) for point in search_results
        ]

        self.logger.info(
            f"Retrieved {len(results)} chunks above threshold {score_threshold}"
        )

        return results

    async def retrieve_by_file(
        self,
        query: str,
        source_file: str,
        top_k: int | None = None,
    ) -> list[ContentChunk]:
        """
        Retrieve relevant chunks from a specific source file.

        Args:
            query: User's question or query text
            source_file: Source file to filter by (e.g., "docs/intro.md")
            top_k: Number of top results to retrieve

        Returns:
            List of ContentChunk objects from the specified file
        """
        return await self.retrieve_relevant_chunks(
            query=query,
            top_k=top_k,
            filters={"source_file": source_file},
        )

    async def retrieve_selection(self, selected_text: str) -> list[ContentChunk]:
        """
        Create a ContentChunk from selected text without performing retrieval.

        This method bypasses Qdrant entirely and wraps the selected text in a ContentChunk
        for consistent handling in the response pipeline.

        Args:
            selected_text: Text selected by the user

        Returns:
            List containing a single ContentChunk with chunk_type="selection"
        """
        self.logger.info(
            f"Creating selection chunk (no retrieval) for {len(selected_text)} chars"
        )

        # Wrap selected text in ContentChunk with special metadata
        chunk = ContentChunk(
            text=selected_text,
            metadata={"source": "user_selection"},
            chunk_type="selection",
            embedding=None,  # No embedding needed for selection mode
        )

        return [chunk]

    def _build_filter(self, filters: dict[str, str]) -> Filter:
        """
        Build Qdrant Filter object from metadata filters.

        Args:
            filters: Dictionary of field name to value mappings

        Returns:
            Qdrant Filter object
        """
        # Build field conditions for each filter
        conditions = [
            FieldCondition(
                key=f"metadata.{field}",
                match=MatchValue(value=value),
            )
            for field, value in filters.items()
        ]

        return Filter(must=conditions)

    async def check_collection_exists(self) -> bool:
        """
        Check if the collection exists in Qdrant.

        Returns:
            True if collection exists, False otherwise
        """
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            exists = self.collection_name in collection_names

            if exists:
                self.logger.info(f"Collection '{self.collection_name}' exists")
            else:
                self.logger.warning(f"Collection '{self.collection_name}' does not exist")

            return exists
        except Exception as e:
            self.logger.error(f"Error checking collection existence: {e}")
            return False

    async def get_collection_stats(self) -> dict[str, int]:
        """
        Get statistics about the collection.

        Returns:
            Dictionary with collection stats (points_count, vectors_count, etc.)
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)

            stats = {
                "points_count": collection_info.points_count,
                "vectors_count": collection_info.vectors_count or 0,
                "indexed_vectors_count": collection_info.indexed_vectors_count or 0,
            }

            self.logger.info(
                f"Collection stats: {stats['points_count']} points, "
                f"{stats['indexed_vectors_count']} indexed vectors"
            )

            return stats
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {e}")
            return {"points_count": 0, "vectors_count": 0, "indexed_vectors_count": 0}

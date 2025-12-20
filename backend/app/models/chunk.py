"""ContentChunk model for representing searchable book passages."""

from typing import Any, Literal
from pydantic import BaseModel, Field
from qdrant_client.models import PointStruct, ScoredPoint


class ContentChunk(BaseModel):
    """
    Represents a searchable chunk of book content.

    Attributes:
        text: The actual text content of the chunk
        metadata: Metadata about the chunk (source_file, section_title, heading_hierarchy, chunk_index)
        chunk_type: Type of chunk (text_with_code, code_only, or selection)
        embedding: Vector embedding of the text (None if not yet embedded)
    """

    text: str = Field(..., description="The text content of this chunk")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Metadata about the chunk"
    )
    chunk_type: Literal["text_with_code", "code_only", "selection"] = Field(
        ..., description="Type of content chunk"
    )
    embedding: list[float] | None = Field(
        None, description="Vector embedding (1536 dimensions for text-embedding-3-small)"
    )

    @classmethod
    def from_qdrant_point(cls, point: ScoredPoint) -> "ContentChunk":
        """
        Convert a Qdrant ScoredPoint to a ContentChunk.

        Args:
            point: Qdrant search result point

        Returns:
            ContentChunk instance
        """
        payload = point.payload or {}
        return cls(
            text=payload.get("text", ""),
            metadata=payload.get("metadata", {}),
            chunk_type=payload.get("chunk_type", "text_with_code"),
            embedding=point.vector if isinstance(point.vector, list) else None,
        )

    def to_qdrant_point(self, chunk_id: str) -> PointStruct:
        """
        Convert ContentChunk to a Qdrant PointStruct for upserting.

        Args:
            chunk_id: Unique identifier for this chunk

        Returns:
            PointStruct ready for Qdrant upsert
        """
        if self.embedding is None:
            raise ValueError("Cannot create PointStruct without embedding")

        return PointStruct(
            id=chunk_id,
            vector=self.embedding,
            payload={
                "text": self.text,
                "metadata": self.metadata,
                "chunk_type": self.chunk_type,
            },
        )

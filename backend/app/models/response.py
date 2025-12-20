"""Response models for API endpoints."""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Citation referencing a book section."""

    section_title: str = Field(..., description="Title of the book section")
    source_file: str = Field(..., description="Source file path")
    link_url: str = Field(..., description="URL to navigate to this section")


class QueryResponse(BaseModel):
    """Response model for query endpoints (global and selection)."""

    answer: str = Field(..., description="Generated answer to the user's question")
    citations: list[Citation] = Field(
        default_factory=list, description="Source citations for the answer"
    )
    retrieved_chunks: int = Field(..., description="Number of chunks retrieved")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class ReindexResponse(BaseModel):
    """Response model for reindexing operations."""

    status: str = Field(..., description="Status: started, completed, or failed")
    total_files: int = Field(default=0, description="Total files processed")
    total_chunks: int = Field(default=0, description="Total chunks created")
    duration_seconds: float = Field(default=0.0, description="Duration of the operation")

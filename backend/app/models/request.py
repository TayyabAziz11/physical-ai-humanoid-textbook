"""Request models for API endpoints."""

from typing import Any
from pydantic import BaseModel, Field, field_validator
import tiktoken

from app.core.config import settings


# Initialize tiktoken encoder for token counting
try:
    encoding = tiktoken.encoding_for_model("gpt-4")
except KeyError:
    encoding = tiktoken.get_encoding("cl100k_base")


class GlobalQueryRequest(BaseModel):
    """Request model for global book queries."""

    question: str = Field(..., min_length=1, description="User's question about the book")
    conversation_history: list[dict[str, Any]] | None = Field(
        None, description="Optional conversation history for follow-up questions"
    )

    @field_validator("question")
    @classmethod
    def validate_question_length(cls, v: str) -> str:
        """Validate question doesn't exceed maximum token limit."""
        token_count = len(encoding.encode(v))
        if token_count > settings.MAX_QUESTION_TOKENS:
            raise ValueError(
                f"Question exceeds maximum length of {settings.MAX_QUESTION_TOKENS} tokens "
                f"(got {token_count} tokens)"
            )
        return v


class SelectionQueryRequest(BaseModel):
    """Request model for selection-based queries (constrained to selected text)."""

    question: str = Field(..., min_length=1, description="User's question about selected text")
    selected_text: str = Field(..., min_length=1, description="Text selected by the user")

    @field_validator("question")
    @classmethod
    def validate_question_length(cls, v: str) -> str:
        """Validate question doesn't exceed maximum token limit."""
        token_count = len(encoding.encode(v))
        if token_count > settings.MAX_QUESTION_TOKENS:
            raise ValueError(
                f"Question exceeds maximum length of {settings.MAX_QUESTION_TOKENS} tokens "
                f"(got {token_count} tokens)"
            )
        return v

    @field_validator("selected_text")
    @classmethod
    def validate_selected_text_length(cls, v: str) -> str:
        """Validate selected text doesn't exceed maximum token limit."""
        token_count = len(encoding.encode(v))
        if token_count > settings.MAX_SELECTION_TOKENS:
            raise ValueError(
                f"Selected text exceeds maximum length of {settings.MAX_SELECTION_TOKENS} tokens "
                f"(got {token_count} tokens)"
            )
        return v


class ReindexRequest(BaseModel):
    """Request model for triggering content re-indexing."""

    docs_directory: str = Field(
        default="./docs", description="Path to documentation directory to index"
    )

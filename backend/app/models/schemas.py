"""
Pydantic models for API request/response validation

Defines the schema for API endpoints (not database models).
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class ChatRequest(BaseModel):
    """Request schema for POST /api/v1/chat"""

    mode: Literal["whole-book", "selection"] = Field(
        ...,
        description="Chat mode: whole-book searches entire textbook, selection searches selected passage"
    )
    question: str = Field(
        ...,
        min_length=1,
        max_length=8000,
        description="User's question"
    )
    selected_text: Optional[str] = Field(
        default=None,
        max_length=20000,
        description="Selected text from textbook (for selection mode)"
    )
    doc_path: Optional[str] = Field(
        default=None,
        description="Document path for selection mode (e.g., 'docs/module-1-ros2/chapter-1-basics.mdx')"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="User ID (nullable for anonymous users)"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID for continuing conversation"
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Validate question is not empty after stripping whitespace"""
        if not v.strip():
            raise ValueError("Question cannot be empty")
        return v.strip()

    @field_validator("selected_text")
    @classmethod
    def validate_selected_text(cls, v: Optional[str]) -> Optional[str]:
        """Strip whitespace from selected text"""
        if v:
            return v.strip()
        return v


class Citation(BaseModel):
    """Citation schema for referencing textbook sources"""

    doc_path: str = Field(
        ...,
        description="Path to source document"
    )
    heading: str = Field(
        ...,
        description="Section heading in document"
    )
    snippet: str = Field(
        ...,
        max_length=200,
        description="Short snippet from source (50-150 chars)"
    )


class ChatResponse(BaseModel):
    """Response schema for POST /api/v1/chat"""

    answer: str = Field(
        ...,
        description="AI-generated answer to user's question"
    )
    citations: list[Citation] = Field(
        default_factory=list,
        description="List of source citations used in answer"
    )
    mode: Literal["whole-book", "selection"] = Field(
        ...,
        description="Echo of request mode"
    )
    session_id: str = Field(
        ...,
        description="Session ID (for continuing conversation)"
    )


class ErrorResponse(BaseModel):
    """Error response schema"""

    detail: str = Field(
        ...,
        description="User-friendly error message"
    )
    code: Optional[str] = Field(
        default=None,
        description="Machine-readable error code"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="ISO 8601 timestamp of error"
    )


class SessionListItem(BaseModel):
    """Session list item for GET /api/v1/sessions"""

    session_id: str
    mode: Literal["whole-book", "selection"]
    started_at: datetime
    last_message_at: datetime
    first_question_preview: Optional[str] = None


class MessageItem(BaseModel):
    """Message item for GET /api/v1/sessions/{id}/messages"""

    role: Literal["user", "assistant"]
    content: str
    created_at: datetime
    selected_text: Optional[str] = None
    doc_path: Optional[str] = None

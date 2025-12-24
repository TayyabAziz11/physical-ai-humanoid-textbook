"""
SQLAlchemy ORM models for database tables

Defines the database schema for chat sessions and messages.
"""
import uuid
from datetime import datetime, timezone
from typing import List
from sqlalchemy import String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


class ChatMode(str, enum.Enum):
    """Chat mode enum"""
    WHOLE_BOOK = "whole-book"
    SELECTION = "selection"


class MessageRole(str, enum.Enum):
    """Message role enum"""
    USER = "user"
    ASSISTANT = "assistant"


class ChatSession(Base):
    """
    Chat session model

    Represents a conversation between a user and the Study Assistant.
    Groups related messages together.
    """
    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        index=True,
        comment="User ID (nullable for anonymous users)"
    )
    mode: Mapped[ChatMode] = mapped_column(
        SQLEnum(ChatMode, name="chat_mode", create_constraint=True),
        nullable=False,
        comment="Chat mode: whole-book or selection"
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_message_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )

    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, user_id={self.user_id}, mode={self.mode})>"


class ChatMessage(Base):
    """
    Chat message model

    Represents a single message in a conversation (user question or assistant response).
    """
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role: Mapped[MessageRole] = mapped_column(
        SQLEnum(MessageRole, name="message_role", create_constraint=True),
        nullable=False,
        comment="Role: user or assistant"
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Message content (question or answer)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    selected_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Selected text for selection mode (user messages only)"
    )
    doc_path: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        comment="Document path for selection mode (user messages only)"
    )

    # Relationships
    session: Mapped["ChatSession"] = relationship(
        "ChatSession",
        back_populates="messages"
    )

    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, role={self.role}, session_id={self.session_id})>"

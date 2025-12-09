"""
Chat storage service

Handles persistence of chat sessions and messages to database.
Only persists when user_id is provided (non-null, non-empty).
"""
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import ChatSession, ChatMessage, ChatMode, MessageRole
from app.models.schemas import ChatRequest, ChatResponse
from app.core.logging import get_logger

logger = get_logger(__name__)


async def create_session_if_needed(
    user_id: Optional[str],
    mode: str,
    db: AsyncSession
) -> Optional[ChatSession]:
    """
    Create a new chat session if user_id is provided

    Per spec: Anonymous users (null/empty user_id) are NOT stored.

    Args:
        user_id: User ID (nullable)
        mode: Chat mode ("whole-book" or "selection")
        db: Database session

    Returns:
        ChatSession instance if created, None if anonymous user
    """
    # Anonymous users are not stored
    if not user_id or not user_id.strip():
        logger.debug("Anonymous user - session will not be persisted")
        return None

    # Map mode string to enum
    chat_mode = ChatMode.WHOLE_BOOK if mode == "whole-book" else ChatMode.SELECTION

    # Create new session
    session = ChatSession(
        user_id=user_id.strip(),
        mode=chat_mode,
        started_at=datetime.now(timezone.utc),
        last_message_at=datetime.now(timezone.utc)
    )

    db.add(session)
    await db.flush()  # Get ID without committing

    logger.info(f"Created session {session.id} for user {user_id}")
    return session


async def get_or_create_session(
    session_id: Optional[str],
    user_id: Optional[str],
    mode: str,
    db: AsyncSession
) -> Optional[ChatSession]:
    """
    Get existing session or create new one if user_id is provided

    Args:
        session_id: Existing session ID (optional)
        user_id: User ID (nullable)
        mode: Chat mode
        db: Database session

    Returns:
        ChatSession instance or None for anonymous users
    """
    # If no user_id, don't persist
    if not user_id or not user_id.strip():
        return None

    # Try to find existing session
    if session_id:
        try:
            from uuid import UUID
            session_uuid = UUID(session_id)

            result = await db.execute(
                select(ChatSession).where(ChatSession.id == session_uuid)
            )
            session = result.scalar_one_or_none()

            if session:
                # Update last_message_at
                session.last_message_at = datetime.now(timezone.utc)
                logger.info(f"Continuing session {session_id}")
                return session

        except (ValueError, Exception) as e:
            logger.warning(f"Invalid session_id: {session_id} - {e}")

    # Create new session
    return await create_session_if_needed(user_id, mode, db)


async def add_user_message(
    session: Optional[ChatSession],
    request: ChatRequest,
    db: AsyncSession
) -> Optional[ChatMessage]:
    """
    Add user message to session

    Only persists if session exists (i.e., user is not anonymous).

    Args:
        session: Chat session (None for anonymous users)
        request: Chat request with question and optional selected_text/doc_path
        db: Database session

    Returns:
        ChatMessage instance if created, None if anonymous
    """
    if not session:
        logger.debug("No session - user message will not be persisted")
        return None

    message = ChatMessage(
        session_id=session.id,
        role=MessageRole.USER,
        content=request.question,
        selected_text=request.selected_text,
        doc_path=request.doc_path,
        created_at=datetime.now(timezone.utc)
    )

    db.add(message)
    logger.debug(f"Added user message to session {session.id}")
    return message


async def add_assistant_message(
    session: Optional[ChatSession],
    response: ChatResponse,
    db: AsyncSession
) -> Optional[ChatMessage]:
    """
    Add assistant response to session

    Only persists if session exists (i.e., user is not anonymous).

    Args:
        session: Chat session (None for anonymous users)
        response: Chat response with answer
        db: Database session

    Returns:
        ChatMessage instance if created, None if anonymous
    """
    if not session:
        logger.debug("No session - assistant message will not be persisted")
        return None

    message = ChatMessage(
        session_id=session.id,
        role=MessageRole.ASSISTANT,
        content=response.answer,
        created_at=datetime.now(timezone.utc)
    )

    db.add(message)
    logger.debug(f"Added assistant message to session {session.id}")
    return message


async def get_conversation_history(
    session: Optional[ChatSession],
    db: AsyncSession,
    limit: int = 10
) -> list[dict]:
    """
    Get recent conversation history for context

    Args:
        session: Chat session (None for anonymous users)
        db: Database session
        limit: Maximum number of previous messages

    Returns:
        List of message dicts in OpenAI format or empty list for anonymous users
    """
    if not session:
        return []

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()

    # Reverse to chronological order and convert to OpenAI format
    conversation_history = []
    for msg in reversed(messages):
        conversation_history.append({
            "role": msg.role.value,
            "content": msg.content
        })

    logger.info(f"Retrieved {len(conversation_history)} previous messages")
    return conversation_history

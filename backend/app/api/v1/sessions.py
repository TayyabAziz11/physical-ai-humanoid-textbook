"""
Session history endpoints

Provides endpoints to list sessions, retrieve session messages, and delete sessions.
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.api.deps import DBDep
from app.models.schemas import SessionListItem, MessageItem
from app.models.database import ChatSession, ChatMessage
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/sessions", response_model=List[SessionListItem])
async def list_sessions(
    db: DBDep,
    user_id: Optional[str] = Query(None, description="Filter by user_id (optional for anonymous users)")
):
    """
    List all chat sessions

    Optionally filter by user_id. Returns sessions ordered by most recent activity.

    Args:
        db: Database session (injected)
        user_id: Optional user_id to filter sessions

    Returns:
        List of SessionListItem with session metadata

    Example:
        GET /api/v1/sessions
        GET /api/v1/sessions?user_id=user123
    """
    try:
        logger.info(f"Listing sessions (user_id={user_id or 'all'})")

        # Build query
        query = select(ChatSession).options(
            selectinload(ChatSession.messages)
        ).order_by(ChatSession.last_message_at.desc())

        # Apply user_id filter if provided
        if user_id:
            query = query.where(ChatSession.user_id == user_id)

        # Execute query
        result = await db.execute(query)
        sessions = result.scalars().all()

        logger.info(f"Found {len(sessions)} sessions")

        # Convert to response model
        session_list = []
        for session in sessions:
            # Get first user message for preview
            first_question_preview = None
            if session.messages:
                for msg in session.messages:
                    if msg.role.value == "user":
                        # Take first 100 chars of first question
                        first_question_preview = msg.content[:100]
                        if len(msg.content) > 100:
                            first_question_preview += "..."
                        break

            session_item = SessionListItem(
                session_id=str(session.id),
                mode=session.mode.value,
                started_at=session.started_at,
                last_message_at=session.last_message_at,
                first_question_preview=first_question_preview
            )
            session_list.append(session_item)

        return session_list

    except Exception as e:
        logger.error(f"Error listing sessions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve sessions: {str(e)}"
        )


@router.get("/sessions/{session_id}/messages", response_model=List[MessageItem])
async def get_session_messages(
    session_id: str,
    db: DBDep
):
    """
    Retrieve all messages for a specific session

    Returns messages in chronological order.

    Args:
        session_id: UUID of the session
        db: Database session (injected)

    Returns:
        List of MessageItem with message content and metadata

    Raises:
        HTTPException: If session not found

    Example:
        GET /api/v1/sessions/550e8400-e29b-41d4-a716-446655440000/messages
    """
    try:
        # Parse session_id
        try:
            session_uuid = uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session_id format")

        logger.info(f"Retrieving messages for session {session_id}")

        # Get session with messages
        result = await db.execute(
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(ChatSession.id == session_uuid)
        )
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Sort messages by created_at (chronological order)
        sorted_messages = sorted(session.messages, key=lambda m: m.created_at)

        logger.info(f"Found {len(sorted_messages)} messages")

        # Convert to response model
        message_list = []
        for msg in sorted_messages:
            message_item = MessageItem(
                role=msg.role.value,
                content=msg.content,
                created_at=msg.created_at,
                selected_text=msg.selected_text,
                doc_path=msg.doc_path
            )
            message_list.append(message_item)

        return message_list

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session messages: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve messages: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: DBDep
):
    """
    Delete a chat session and all its messages

    Due to CASCADE delete, all associated messages will also be deleted.

    Args:
        session_id: UUID of the session to delete
        db: Database session (injected)

    Returns:
        Success message with deleted session_id

    Raises:
        HTTPException: If session not found

    Example:
        DELETE /api/v1/sessions/550e8400-e29b-41d4-a716-446655440000
    """
    try:
        # Parse session_id
        try:
            session_uuid = uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session_id format")

        logger.info(f"Deleting session {session_id}")

        # Check if session exists
        result = await db.execute(
            select(ChatSession).where(ChatSession.id == session_uuid)
        )
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Delete session (CASCADE will delete messages)
        await db.execute(
            delete(ChatSession).where(ChatSession.id == session_uuid)
        )
        await db.commit()

        logger.info(f"Successfully deleted session {session_id}")

        return {
            "message": "Session deleted successfully",
            "session_id": session_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session: {str(e)}"
        )

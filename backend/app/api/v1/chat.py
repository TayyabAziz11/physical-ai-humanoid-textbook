"""
Chat endpoint for Study Assistant

Handles POST /api/v1/chat for whole-book and selection mode Q&A.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import SettingsDep, DBDep
from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse
from app.models.database import ChatSession, ChatMessage, ChatMode, MessageRole
from app.services.rag import rag_query
from app.core.logging import get_logger
from app.core.security import sanitize_user_input, validate_question

logger = get_logger(__name__)
router = APIRouter()


async def get_or_create_session(
    db: DBDep,
    session_id: Optional[str],
    user_id: Optional[str],
    mode: str
) -> ChatSession:
    """
    Get existing session or create new one

    Args:
        db: Database session
        session_id: Existing session ID (optional)
        user_id: User ID (optional, nullable for anonymous)
        mode: Chat mode (whole-book or selection)

    Returns:
        ChatSession instance
    """
    if session_id:
        # Try to find existing session
        try:
            session_uuid = uuid.UUID(session_id)
            result = await db.execute(
                select(ChatSession).where(ChatSession.id == session_uuid)
            )
            session = result.scalar_one_or_none()

            if session:
                logger.info(f"Continuing existing session: {session_id}")
                # Update last_message_at
                session.last_message_at = datetime.now(timezone.utc)
                return session
            else:
                logger.warning(f"Session {session_id} not found, creating new session")

        except ValueError:
            logger.warning(f"Invalid session_id format: {session_id}")

    # Create new session
    chat_mode = ChatMode.WHOLE_BOOK if mode == "whole-book" else ChatMode.SELECTION
    new_session = ChatSession(
        user_id=user_id,
        mode=chat_mode,
        started_at=datetime.now(timezone.utc),
        last_message_at=datetime.now(timezone.utc)
    )
    db.add(new_session)
    await db.flush()  # Get the ID without committing

    logger.info(f"Created new session: {new_session.id}")
    return new_session


async def get_conversation_history(
    db: DBDep,
    session: ChatSession,
    limit: int = 10
) -> List[dict]:
    """
    Get recent conversation history for context

    Args:
        db: Database session
        session: Chat session
        limit: Maximum number of previous messages to retrieve

    Returns:
        List of message dicts in OpenAI format [{"role": "user", "content": "..."}]
    """
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


async def save_messages(
    db: DBDep,
    session: ChatSession,
    question: str,
    answer: str,
    selected_text: Optional[str] = None,
    doc_path: Optional[str] = None
):
    """
    Save user question and assistant answer to database

    Args:
        db: Database session
        session: Chat session
        question: User's question
        answer: Assistant's answer
        selected_text: Selected text (for selection mode)
        doc_path: Document path (for selection mode)
    """
    # Save user message
    user_message = ChatMessage(
        session_id=session.id,
        role=MessageRole.USER,
        content=question,
        selected_text=selected_text,
        doc_path=doc_path,
        created_at=datetime.now(timezone.utc)
    )
    db.add(user_message)

    # Save assistant message
    assistant_message = ChatMessage(
        session_id=session.id,
        role=MessageRole.ASSISTANT,
        content=answer,
        created_at=datetime.now(timezone.utc)
    )
    db.add(assistant_message)

    logger.info(f"Saved 2 messages to session {session.id}")


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    settings: SettingsDep,
    db: DBDep
):
    """
    Chat with Study Assistant

    Supports two modes:
    - **whole-book**: Semantic search across entire textbook
    - **selection**: Answer based on user-selected text passage

    Args:
        request: Chat request with question, mode, and optional context
        settings: Application settings (injected)
        db: Database session (injected)

    Returns:
        ChatResponse with answer, citations, and session_id

    Raises:
        HTTPException: If validation fails or processing errors occur
    """
    try:
        logger.info(f"Received chat request: mode={request.mode}, question_len={len(request.question)}")

        # Validate question
        is_valid, error_msg = validate_question(request.question, settings.MAX_QUESTION_TOKENS)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Sanitize inputs
        question = sanitize_user_input(request.question, max_length=settings.MAX_QUESTION_TOKENS * 4)

        selected_text = None
        doc_path = None

        if request.mode == "selection":
            # Validate selection mode requirements
            if not request.selected_text:
                raise HTTPException(
                    status_code=400,
                    detail="selected_text is required for selection mode"
                )

            selected_text = sanitize_user_input(
                request.selected_text,
                max_length=settings.MAX_SELECTION_TOKENS * 4
            )
            doc_path = request.doc_path

        # Get or create session
        session = await get_or_create_session(
            db=db,
            session_id=request.session_id,
            user_id=request.user_id,
            mode=request.mode
        )

        # Get conversation history (last 10 messages)
        conversation_history = await get_conversation_history(db, session, limit=10)

        # Execute RAG query
        logger.info("Executing RAG query...")
        answer, citations = rag_query(
            question=question,
            mode=request.mode,
            selected_text=selected_text,
            doc_path=doc_path,
            conversation_history=conversation_history if conversation_history else None
        )

        # Save messages to database
        await save_messages(
            db=db,
            session=session,
            question=question,
            answer=answer,
            selected_text=selected_text,
            doc_path=doc_path
        )

        # Commit all changes
        await db.commit()

        logger.info(f"Chat request completed successfully: session={session.id}")

        # Return response
        return ChatResponse(
            answer=answer,
            citations=citations,
            mode=request.mode,
            session_id=str(session.id)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat request failed: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

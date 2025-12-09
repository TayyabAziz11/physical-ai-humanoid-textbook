"""
Chat API router

Implements POST /api/chat endpoint for RAG-based question answering.
"""
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import SettingsDep, DBDep
from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag import answer_chat_request
from app.services.chat_storage import (
    get_or_create_session,
    add_user_message,
    add_assistant_message
)
from app.core.security import sanitize_user_input, validate_question
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    settings: SettingsDep,
    db: DBDep
):
    """
    Chat with Study Assistant using RAG

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
        HTTPException: 400 for validation errors, 500 for internal errors

    Example (whole-book):
        POST /api/chat
        {
            "mode": "whole-book",
            "question": "What is ROS 2?",
            "user_id": "user123"
        }

    Example (selection):
        POST /api/chat
        {
            "mode": "selection",
            "question": "Explain this concept",
            "selected_text": "ROS 2 is a robot operating system...",
            "doc_path": "docs/module-1-ros2/chapter-1.mdx",
            "user_id": "user123"
        }
    """
    try:
        logger.info(f"Received chat request: mode={request.mode}, user_id={request.user_id or 'anonymous'}")

        # === VALIDATION ===

        # Validate question
        is_valid, error_msg = validate_question(request.question, settings.MAX_QUESTION_TOKENS)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

        # Sanitize question
        question = sanitize_user_input(request.question, max_length=settings.MAX_QUESTION_TOKENS * 4)
        request.question = question

        # Validate mode-specific requirements
        if request.mode == "selection":
            if not request.selected_text:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="selected_text is required for selection mode"
                )

            # Sanitize selected text
            selected_text = sanitize_user_input(
                request.selected_text,
                max_length=settings.MAX_SELECTION_TOKENS * 4
            )
            request.selected_text = selected_text

        elif request.mode not in ["whole-book", "selection"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid mode: {request.mode}. Must be 'whole-book' or 'selection'"
            )

        # === SESSION MANAGEMENT ===

        # Get or create session (None for anonymous users)
        session = await get_or_create_session(
            session_id=request.session_id,
            user_id=request.user_id,
            mode=request.mode,
            db=db
        )

        # Add user message (only if session exists)
        await add_user_message(session, request, db)

        # === RAG PIPELINE ===

        logger.info("Executing RAG pipeline...")
        response = await answer_chat_request(
            request=request,
            db=db,
            settings=settings
        )

        # === SAVE RESPONSE ===

        # Add assistant message (only if session exists)
        await add_assistant_message(session, response, db)

        # Commit all changes
        await db.commit()

        logger.info(f"Chat request completed successfully")

        return response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise

    except ValueError as e:
        # Validation errors from services
        logger.warning(f"Validation error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        # Internal errors
        logger.error(f"Chat request failed: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request. Please try again."
        )

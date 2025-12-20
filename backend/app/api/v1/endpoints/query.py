"""Query endpoints for RAG chatbot (global and selection modes)."""

import time

from fastapi import APIRouter, HTTPException, status

from app.core.logging import get_logger
from app.models.request import GlobalQueryRequest, SelectionQueryRequest
from app.models.response import QueryResponse
from app.services.retriever import RetrievalService
from app.services.responder import ResponseService

logger = get_logger(__name__)

router = APIRouter()


@router.post("/global", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def global_query(request: GlobalQueryRequest) -> QueryResponse:
    """
    Answer a question about any topic in the book using RAG.

    This endpoint:
    1. Retrieves relevant chunks from the entire book using vector search
    2. Generates an answer using the retrieved context
    3. Returns citations to source sections

    Args:
        request: GlobalQueryRequest with question and optional conversation_history

    Returns:
        QueryResponse with answer, citations, and metadata

    Raises:
        HTTPException: If retrieval or response generation fails
    """
    start_time = time.time()

    logger.info(f"Processing global query: '{request.question[:100]}...'")

    try:
        # Initialize services
        retriever = RetrievalService()
        responder = ResponseService()

        # Retrieve relevant chunks
        chunks = await retriever.retrieve_relevant_chunks(query=request.question)

        if not chunks:
            logger.warning(f"No relevant chunks found for query: '{request.question}'")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No relevant content found in the book for your question. "
                "The collection may be empty or your question may be too specific.",
            )

        # Generate answer with citations
        answer, citations = await responder.generate_answer(
            question=request.question,
            retrieved_chunks=chunks,
            conversation_history=request.conversation_history,
        )

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        logger.info(
            f"Global query completed in {processing_time_ms:.2f}ms "
            f"({len(chunks)} chunks, {len(citations)} citations)"
        )

        return QueryResponse(
            answer=answer,
            citations=citations,
            retrieved_chunks=len(chunks),
            processing_time_ms=processing_time_ms,
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error processing global query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}",
        )


@router.post("/selection", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def selection_query(request: SelectionQueryRequest) -> QueryResponse:
    """
    Answer a question about selected text (no retrieval, strict context isolation).

    This endpoint:
    1. Uses ONLY the selected text provided by the user
    2. Does NOT perform vector search or retrieval
    3. Enforces strict context isolation (no external knowledge)

    Args:
        request: SelectionQueryRequest with question and selected_text

    Returns:
        QueryResponse with answer (no citations, retrieved_chunks=0)

    Raises:
        HTTPException: If response generation fails
    """
    start_time = time.time()

    logger.info(
        f"Processing selection query: '{request.question[:100]}...' "
        f"(selected text: {len(request.selected_text)} chars)"
    )

    try:
        # Initialize responder service
        responder = ResponseService()

        # Generate answer using only selected text (no retrieval)
        answer = await responder.generate_selection_answer(
            question=request.question,
            selected_text=request.selected_text,
        )

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        logger.info(f"Selection query completed in {processing_time_ms:.2f}ms")

        # No citations or retrieval for selection mode
        return QueryResponse(
            answer=answer,
            citations=[],  # No citations in selection mode
            retrieved_chunks=0,  # No retrieval performed
            processing_time_ms=processing_time_ms,
        )

    except Exception as e:
        logger.error(f"Error processing selection query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process selection query: {str(e)}",
        )

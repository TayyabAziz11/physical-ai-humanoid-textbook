"""Admin endpoints for RAG chatbot management.

These endpoints are for development and administrative tasks only.
In production, these should be protected with authentication.
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from app.core.logging import get_logger
from app.models.request import ReindexRequest
from app.models.response import ReindexResponse
from app.services.indexer import IndexingService

logger = get_logger(__name__)

router = APIRouter()


# Background task function
async def reindex_background_task(docs_dir: str):
    """
    Background task for re-indexing content.

    Args:
        docs_dir: Path to documentation directory
    """
    logger.info(f"[Background Task] Starting re-indexing from: {docs_dir}")

    indexer = IndexingService()

    try:
        result = await indexer.reindex_full(docs_dir)

        if result.status == "completed":
            logger.info(
                f"[Background Task] Re-indexing completed successfully: "
                f"{result.total_files} files, {result.total_chunks} chunks, "
                f"{result.duration_seconds:.2f}s"
            )
        else:
            logger.error(f"[Background Task] Re-indexing failed: {result.status}")

    except Exception as e:
        logger.error(f"[Background Task] Re-indexing error: {e}", exc_info=True)


@router.post("/reindex", response_model=ReindexResponse, status_code=status.HTTP_202_ACCEPTED)
async def reindex_content(
    request: ReindexRequest,
    background_tasks: BackgroundTasks,
) -> ReindexResponse:
    """
    Trigger content re-indexing (asynchronous).

    This endpoint starts re-indexing in the background and returns immediately.
    The actual indexing process runs asynchronously using Qdrant's atomic swap strategy:
    1. Create new temporary collection
    2. Index all documents into temp collection
    3. Swap alias to point to new collection
    4. Delete old collection

    **WARNING**: This endpoint should be protected with authentication in production.

    Args:
        request: ReindexRequest with docs_directory path
        background_tasks: FastAPI background tasks handler

    Returns:
        ReindexResponse with status="started"

    Raises:
        HTTPException: If docs_directory doesn't exist or is invalid
    """
    docs_dir = request.docs_directory

    logger.info(f"Received reindex request for directory: {docs_dir}")

    # Validate docs directory exists
    from pathlib import Path

    docs_path = Path(docs_dir)
    if not docs_path.exists():
        logger.error(f"Documentation directory not found: {docs_dir}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documentation directory not found: {docs_dir}",
        )

    if not docs_path.is_dir():
        logger.error(f"Path is not a directory: {docs_dir}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Path is not a directory: {docs_dir}",
        )

    # Add background task
    background_tasks.add_task(reindex_background_task, docs_dir)

    logger.info(f"Re-indexing task scheduled for: {docs_dir}")

    return ReindexResponse(
        status="started",
        total_files=0,
        total_chunks=0,
        duration_seconds=0.0,
    )


@router.get("/health", status_code=status.HTTP_200_OK)
async def admin_health_check():
    """
    Admin health check endpoint.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "admin",
    }

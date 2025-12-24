"""
FastAPI Production Entry Point for Railway Deployment

This is the main entry point used by Railway/Uvicorn.
Designed for production with proper async support, error handling, and monitoring.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.rag import answer_chat_request
from app.models.schemas import ChatRequest, ChatResponse
from app.db.session import get_db
from app.db.qdrant import init_collection

# Initialize settings and logger
settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup/shutdown events.

    Startup:
    - Log configuration
    - Initialize Qdrant collection

    Shutdown:
    - Cleanup resources
    """
    # Startup
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"📊 Environment: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    logger.info(f"🔗 Qdrant URL: {settings.QDRANT_URL}")
    logger.info(f"📦 Collection: {settings.QDRANT_COLLECTION}")

    # Initialize Qdrant collection
    try:
        await init_collection()
        logger.info("✅ Qdrant collection initialized")
    except Exception as e:
        logger.error(f"❌ Qdrant initialization failed: {e}")
        # Don't crash - allow app to start for health checks

    yield

    # Shutdown
    logger.info(f"👋 Shutting down {settings.APP_NAME}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="RAG-powered study assistant for Physical AI & Humanoid Robotics textbook",
    lifespan=lifespan,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# ROUTES
# ============================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information and status.

    Returns API metadata and links to documentation.
    Used by Railway health checks and browser access.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": "debug" if settings.DEBUG else "production",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": "/openapi.json",
        "endpoints": {
            "health": "/health",
            "chat": "/chat (POST)",
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for Railway and load balancers.

    Returns basic health status without external dependencies.
    Always returns 200 OK if app is running.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Chat endpoint - RAG-powered question answering.

    Supports two modes:
    - whole-book: Semantic search across entire textbook
    - selection: Answer based on user-selected text passage

    Args:
        request: ChatRequest with question, mode, and optional context
        db: Database session (injected)

    Returns:
        ChatResponse with answer, citations, and session_id

    Raises:
        HTTPException: 400 for validation errors, 500 for server errors
    """
    try:
        logger.info(f"📨 Chat request: mode={request.mode}, question_len={len(request.question)}")

        response = await answer_chat_request(
            request=request,
            db=db,
        )

        logger.info(f"✅ Chat response generated: {len(response.answer)} chars")
        return response

    except ValueError as e:
        logger.warning(f"⚠️ Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"❌ Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again."
        )


# ============================================
# APPLICATION METADATA
# ============================================

if __name__ == "__main__":
    import uvicorn

    # Local development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

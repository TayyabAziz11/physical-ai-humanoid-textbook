<<<<<<< HEAD
"""FastAPI application entry point for RAG chatbot backend."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import get_logger
from app.db.qdrant import init_collection

logger = get_logger(__name__)
=======
"""
FastAPI application entrypoint for RAG Backend & Study Assistant API
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import health, sessions
from app.api.v1 import chat as v1_chat
from app.api import chat as api_chat
from app.api.v1.router import router as api_v1_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.security import get_cors_config
from app.services.qdrant import close_qdrant_client  # fixed qdrant.py includes this


# Initialize settings and logging
settings = get_settings()
logger = setup_logging(settings.LOG_LEVEL)
>>>>>>> 002-rag-backend-study-assistant


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
<<<<<<< HEAD
    Lifespan context manager for startup and shutdown events.

    Startup:
    - Initialize Qdrant collection if not exists
    - Log application configuration

    Shutdown:
    - Clean up resources if needed
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Qdrant URL: {settings.QDRANT_URL}")
    logger.info(f"Collection: {settings.QDRANT_COLLECTION}")
    logger.info(f"OpenAI Chat Model: {settings.OPENAI_CHAT_MODEL}")
    logger.info(f"OpenAI Embedding Model: {settings.OPENAI_EMBEDDING_MODEL}")

    try:
        # Initialize Qdrant collection
        await init_collection()
        logger.info("Qdrant collection initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant collection: {e}")
        # Don't raise - allow app to start even if collection init fails
        # This lets the app run for health checks, etc.
=======
    Application lifespan events (startup/shutdown)
    """
    # Startup
    logger.info("Starting RAG Study Assistant API")
    logger.info(f"Environment: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
>>>>>>> 002-rag-backend-study-assistant

    yield

    # Shutdown
<<<<<<< HEAD
    logger.info(f"Shutting down {settings.APP_NAME}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="RAG-powered study assistant for Physical AI & Humanoid Robotics textbook",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint for health check and API information.

    Returns:
        Basic API information
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs_url": "/docs",
        "api_version": "v1",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Run with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
=======
    logger.info("Shutting down RAG Study Assistant API")
    await close_qdrant_client()  # <- await the async function
    logger.info("Cleanup completed")


app = FastAPI(
    title="RAG Study Assistant API",
    description="Backend API for Physical AI & Humanoid Robotics Textbook Study Assistant",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS middleware configuration from settings
cors_config = get_cors_config(settings.CORS_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    **cors_config
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(v1_chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(sessions.router, prefix="/api/v1", tags=["sessions"])
app.include_router(api_chat.router, prefix="/api", tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG Study Assistant API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }
>>>>>>> 002-rag-backend-study-assistant

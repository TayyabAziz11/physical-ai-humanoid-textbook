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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events (startup/shutdown)
    """
    # Startup
    logger.info("Starting RAG Study Assistant API")
    logger.info(f"Environment: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")

    yield

    # Shutdown
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

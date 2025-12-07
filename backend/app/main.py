"""
FastAPI application entrypoint for RAG Backend & Study Assistant API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import health
from app.api.v1.router import router as api_v1_router

app = FastAPI(
    title="RAG Study Assistant API",
    description="Backend API for Physical AI & Humanoid Robotics Textbook Study Assistant",
    version="0.1.0"
)

# CORS middleware configuration
# TODO: Load CORS_ORIGINS from settings in Phase 2
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Temporary defaults
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include health router directly (not through api_v1_router yet for simplicity)
app.include_router(health.router, prefix="/api/v1", tags=["health"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG Study Assistant API",
        "version": "0.1.0",
        "docs": "/docs"
    }

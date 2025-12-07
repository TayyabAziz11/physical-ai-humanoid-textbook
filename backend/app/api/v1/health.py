"""
Health check endpoint
"""
from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns:
        dict: Health status with version and timestamp
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

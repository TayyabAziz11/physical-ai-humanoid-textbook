"""
Health check endpoint
"""
from datetime import datetime, timezone
from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import SettingsDep, DBDep, QdrantDep
from app.services.qdrant_client import test_qdrant_connection

router = APIRouter()


@router.get("/health")
async def health_check(settings: SettingsDep, db: DBDep, qdrant: QdrantDep):
    """
    Health check endpoint

    Checks application health, database connectivity, and Qdrant vector DB status.

    Args:
        settings: Application settings (injected)
        db: Database session (injected)
        qdrant: Qdrant client (injected)

    Returns:
        dict: Health status with version, database status, Qdrant status, and timestamp
    """
    # Test database connection
    db_status = "disconnected"
    try:
        # Simple query to test connection
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"

    # Test Qdrant connection
    qdrant_connected, qdrant_status = test_qdrant_connection()

    # Overall health: healthy if both DB and Qdrant are connected
    overall_status = "healthy" if (db_status == "connected" and qdrant_connected) else "degraded"

    return {
        "status": overall_status,
        "version": settings.APP_VERSION,
        "database": db_status,
        "qdrant": qdrant_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

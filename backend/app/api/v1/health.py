"""
Health check endpoint
"""
from datetime import datetime, timezone
from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import SettingsDep, DBDep, QdrantDep
from app.services.qdrant import get_qdrant_client

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
    qdrant_status = "disconnected"
    qdrant_connected = False
    try:
        client = get_qdrant_client()
        collections = client.get_collections()

        # Check if our collection exists
        collection_exists = any(
            c.name == settings.QDRANT_COLLECTION
            for c in collections.collections
        )

        if collection_exists:
            collection_info = client.get_collection(settings.QDRANT_COLLECTION)
            point_count = collection_info.points_count
            qdrant_status = f"connected (collection: {settings.QDRANT_COLLECTION}, points: {point_count})"
        else:
            qdrant_status = f"connected (collection '{settings.QDRANT_COLLECTION}' not found)"

        qdrant_connected = True
    except Exception as e:
        qdrant_status = f"error: {str(e)[:50]}"
        qdrant_connected = False

    # Overall health: healthy if both DB and Qdrant are connected
    overall_status = "healthy" if (db_status == "connected" and qdrant_connected) else "degraded"

    return {
        "status": overall_status,
        "version": settings.APP_VERSION,
        "database": db_status,
        "qdrant": qdrant_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

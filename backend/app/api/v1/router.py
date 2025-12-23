<<<<<<< HEAD
"""API v1 router aggregating all endpoint modules."""

from fastapi import APIRouter

from app.api.v1.endpoints import admin, query

# Create main v1 router
api_router = APIRouter()

# Include query endpoints (global and selection)
api_router.include_router(
    query.router,
    prefix="/query",
    tags=["Query"],
)

# Include admin endpoints (re-indexing, health checks)
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin"],
)
=======
"""
API v1 router aggregator
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")

# Routers will be included here as features are implemented
# Example: router.include_router(health.router, tags=["health"])
>>>>>>> 002-rag-backend-study-assistant

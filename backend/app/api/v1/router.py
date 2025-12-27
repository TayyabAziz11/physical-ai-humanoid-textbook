"""API v1 router aggregating all endpoint modules."""

from fastapi import APIRouter

from app.api.v1.endpoints import admin, query, translate

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

# Include translation endpoints
api_router.include_router(
    translate.router,
    prefix="/translate",
    tags=["Translation"],
)

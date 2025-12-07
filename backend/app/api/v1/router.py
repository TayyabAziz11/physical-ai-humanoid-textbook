"""
API v1 router aggregator
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")

# Routers will be included here as features are implemented
# Example: router.include_router(health.router, tags=["health"])

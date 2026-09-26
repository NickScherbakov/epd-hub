"""
API routers initialization
"""
from fastapi import APIRouter
from app.api import documents, changes, notifications

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(documents.router)
api_router.include_router(changes.router)
api_router.include_router(notifications.router)

__all__ = ["api_router"]

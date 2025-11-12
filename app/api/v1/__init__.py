from fastapi import APIRouter

from app.api.v1 import profile, compatibility, transit_period

# Create v1 API router
api_router = APIRouter(prefix="/v1")

# Include all v1 endpoints
api_router.include_router(profile.router)
api_router.include_router(compatibility.router)
api_router.include_router(transit_period.router)

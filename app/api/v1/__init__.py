from fastapi import APIRouter

from app.api.v1 import compatibility, planet_house, profile, soulmate, style, transit_period

# Create v1 API router
api_router = APIRouter(prefix="/v1")

# Include all v1 endpoints
api_router.include_router(profile.router)
api_router.include_router(compatibility.router)
api_router.include_router(transit_period.router)
api_router.include_router(planet_house.router)
api_router.include_router(soulmate.router)
api_router.include_router(style.router)

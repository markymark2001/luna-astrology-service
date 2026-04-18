from fastapi import APIRouter, Depends

from app.api.internal_auth import verify_internal_service_token
from app.api.v1 import compatibility, profile, transit_period

# Create v1 API router
api_router = APIRouter(
    prefix="/v1",
    dependencies=[Depends(verify_internal_service_token)],
)

# Include all v1 endpoints
api_router.include_router(profile.router)
api_router.include_router(compatibility.router)
api_router.include_router(transit_period.router)

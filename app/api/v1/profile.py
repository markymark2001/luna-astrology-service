"""Astrological profile API endpoints with hexagonal architecture."""

import json
from fastapi import APIRouter, Depends, status
from fastapi.responses import PlainTextResponse

from app.models.requests import ProfileRequest
from app.application.profile_service import ProfileService

router = APIRouter(prefix="/astrology", tags=["Astrology Profile"])


def get_profile_service() -> ProfileService:
    """
    Dependency injection for ProfileService.

    This will be properly wired in main.py with the provider instance.
    For now, returns None (will be replaced by main.py setup).
    """
    # This will be overridden in main.py
    return None


@router.post(
    "/profile",
    status_code=status.HTTP_200_OK,
    response_class=PlainTextResponse,
    summary="Get astrological profile as JSON string",
    description="Calculate natal chart and current transits, returned as standardized JSON string for LLM consumption."
)
async def get_profile(
    request: ProfileRequest,
    profile_service: ProfileService = Depends(get_profile_service)
) -> str:
    """
    Get complete astrological profile as JSON string for LLM context.

    Returns JSON string with:
    - natal_chart: Planets, houses, points, birth data
    - aspects: natal, transits_to_natal, current_sky
    - transits: Current planetary positions

    Note: Uses CORE preset configuration (10 planets, 2 points, 6 houses, 4° orbs).

    Args:
        request: Birth data and optional transit date
        profile_service: Injected profile service

    Returns:
        JSON string optimized for LLM context

    Raises:
        HTTPException: Handled by FastAPI exception handlers
    """
    # Generate profile using application service
    profile_data = profile_service.generate_profile(
        birth_data=request,
        transit_date=request.transit_date
    )

    # Return data as JSON string directly
    return json.dumps(profile_data)

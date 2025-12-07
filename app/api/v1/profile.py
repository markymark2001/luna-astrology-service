"""Astrological profile API endpoints with hexagonal architecture."""

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
    summary="Get astrological profile as compact text",
    description="Calculate natal chart and current transits, returned as compact text for LLM consumption (~80% token reduction)."
)
async def get_profile(
    request: ProfileRequest,
    profile_service: ProfileService = Depends(get_profile_service)
) -> str:
    """
    Get complete astrological profile as compact text for LLM context.

    Returns word-based compact format with:
    - PLANETS: Sun in Aries 15 deg (H1)
    - HOUSES: 1st House: Aries
    - NATAL ASPECTS: Sun conjunct Mercury (orb 1.2)
    - CURRENT TRANSITS: Transit Sun in Capricorn 25 deg
    - TRANSIT ASPECTS TO NATAL: Transit Mars opposite natal Sun (orb 2.3)

    Note: Uses CORE preset configuration (10 planets, 2 points, 6 houses, 4° orbs).

    Args:
        request: Birth data and optional transit date
        profile_service: Injected profile service

    Returns:
        Compact text optimized for LLM context (~80% token reduction)

    Raises:
        HTTPException: Handled by FastAPI exception handlers
    """
    return profile_service.generate_profile_compact(
        birth_data=request,
        transit_date=request.transit_date
    )

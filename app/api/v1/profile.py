"""Astrological profile API endpoints with hexagonal architecture."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import PlainTextResponse

from app.application.profile_service import ProfileService
from app.models.requests import ProfileRequest

router = APIRouter(prefix="/astrology", tags=["Astrology Profile"])


def get_profile_service() -> ProfileService | None:
    """
    Dependency injection for ProfileService.

    This will be properly wired in main.py with the provider instance.
    For now, returns None (will be replaced by main.py setup).
    """
    # This will be overridden in main.py
    return None


# Called by: backend/app/infrastructure/providers/astrology_provider.py
@router.post(
    "/profile",
    status_code=status.HTTP_200_OK,
    response_class=PlainTextResponse,
    summary="Get astrological profile as compact text",
    description="Calculate natal chart and current transits, returned as compact text for LLM consumption (~80% token reduction)."
)
async def get_profile(
    request: ProfileRequest,
    profile_service: ProfileService | None = Depends(get_profile_service)
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
    assert profile_service is not None, "ProfileService not configured"
    return profile_service.generate_profile_compact(
        birth_data=request,
        transit_date=request.transit_date
    )


# Called by: backend/app/infrastructure/ai/tools/definitions/natal_chart_tool.py
@router.post(
    "/profile/lookup",
    status_code=status.HTTP_200_OK,
    response_class=PlainTextResponse,
    summary="Get profile for tool lookups, excluding current sky positions",
    description="Calculate natal chart and transit aspects to natal, excluding current sky positions (already in user's context). Use for tool calls on other people."
)
async def get_lookup_profile(
    request: ProfileRequest,
    profile_service: ProfileService = Depends(get_profile_service)
) -> str:
    """
    Get astrological profile for tool lookups (e.g., relationship profiles).

    Unlike /profile, excludes CURRENT TRANSITS section (where planets are today)
    since the user's context already contains current sky positions. Includes:
    - PLANETS: natal planet positions
    - POINTS: Ascendant, MC, etc.
    - HOUSES: house cusps
    - NATAL ASPECTS: aspects between natal planets
    - TRANSIT ASPECTS TO NATAL: how today's transits affect THIS person's chart

    Use this endpoint when looking up other people's profiles during conversation,
    avoiding redundant current sky data that's already in the user's system context.

    Args:
        request: Birth data and optional transit date
        profile_service: Injected profile service

    Returns:
        Compact text with person-specific data only

    Raises:
        HTTPException: Handled by FastAPI exception handlers
    """
    return profile_service.generate_personal_profile_compact(
        birth_data=request,
        transit_date=request.transit_date
    )


# Called by: backend/app/infrastructure/proactive/astrology_context.py
@router.post(
    "/profile/monthly",
    status_code=status.HTTP_200_OK,
    response_class=PlainTextResponse,
    summary="Get natal chart + monthly transits for proactive messages",
    description="Calculate natal chart and current month transits, excluding daily transits. Designed for proactive messages where viewing time is unknown."
)
async def get_monthly_profile(
    request: ProfileRequest,
    profile_service: ProfileService = Depends(get_profile_service)
) -> str:
    """
    Get natal chart + monthly transits as compact text for proactive messages.

    Returns word-based compact format with:
    - PLANETS: Sun in Aries 15 deg (H1)
    - POINTS: Ascendant in Cancer 10 deg
    - HOUSES: 1st House: Aries
    - NATAL ASPECTS: Sun conjunct Mercury (orb 1.2)
    - MONTHLY TRANSITS: Saturn conj Mars: Jan1-31 exact Jan15 (0.5°)

    Excludes daily transits (CURRENT TRANSITS, TRANSIT ASPECTS TO NATAL)
    since proactive messages may be viewed at any time.

    Args:
        request: Birth data (transit_date is ignored - uses current month)
        profile_service: Injected profile service

    Returns:
        Compact text with natal chart + monthly transits

    Raises:
        HTTPException: Handled by FastAPI exception handlers
    """
    return profile_service.generate_monthly_profile_compact(birth_data=request)

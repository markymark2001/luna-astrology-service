"""Astrological profile API endpoints with hexagonal architecture."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import PlainTextResponse

from app.infrastructure.compute_runtime import AstrologyComputeRuntime, get_compute_runtime
from app.models.requests import ProfileRequest
from app.models.responses import PlacementsResponse

router = APIRouter(prefix="/astrology", tags=["Astrology Profile"])


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
    compute_runtime: AstrologyComputeRuntime = Depends(get_compute_runtime),
) -> str:
    """
    Get complete astrological profile as compact text for LLM context.

    Returns word-based compact format with:
    - PLANETS: Sun in Aries 15 deg (H1)
    - HOUSES: 1st House: Aries
    - NATAL ASPECTS: Sun conjunct Mercury (orb 1.2)
    - CURRENT TRANSITS: Sun in Capricorn 25 deg, North Node in Aquarius 15 deg
    - TRANSIT ASPECTS TO NATAL: Transit Mars opposite natal Sun (orb 2.3)

    Note: Uses CORE preset configuration (11 bodies, 4 points, 12 houses, 4° orbs).
    """
    return await compute_runtime.run(
        "profile_compact",
        request.model_dump(mode="json"),
        route_name="/api/v1/astrology/profile",
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
    compute_runtime: AstrologyComputeRuntime = Depends(get_compute_runtime),
) -> str:
    """
    Get astrological profile for tool lookups (e.g., relationship profiles).

    Unlike /profile, excludes CURRENT TRANSITS section (where planets are today)
    since the user's context already contains current sky positions.
    """
    return await compute_runtime.run(
        "lookup_profile_compact",
        request.model_dump(mode="json"),
        route_name="/api/v1/astrology/profile/lookup",
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
    compute_runtime: AstrologyComputeRuntime = Depends(get_compute_runtime),
) -> str:
    """Get natal chart + monthly transits as compact text for proactive messages."""
    return await compute_runtime.run(
        "monthly_profile_compact",
        request.model_dump(mode="json"),
        route_name="/api/v1/astrology/profile/monthly",
    )


# Called by: backend/app/api/v1/profile.py
@router.post(
    "/profile/placements",
    status_code=status.HTTP_200_OK,
    response_model=PlacementsResponse,
    summary="Get natal chart placements for profile display",
    description="Calculate natal chart and return placements (sun, moon, ascendant, all 10 planets) for profile UI."
)
async def get_placements(
    request: ProfileRequest,
    compute_runtime: AstrologyComputeRuntime = Depends(get_compute_runtime),
) -> PlacementsResponse:
    """Get natal chart placements for profile page display."""
    result = await compute_runtime.run(
        "placements",
        request.model_dump(mode="json"),
        route_name="/api/v1/astrology/profile/placements",
    )
    return PlacementsResponse.model_validate(result)

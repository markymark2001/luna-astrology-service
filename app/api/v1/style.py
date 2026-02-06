"""Style chart API endpoint.

# Called by: backend/app/infrastructure/ai/tools/definitions/image_edit_tool.py (style mode)
"""

from typing import Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.application.profile_service import ProfileService
from app.domain.models.birth_data import BirthData

router = APIRouter(prefix="/astrology", tags=["Style"])


class StyleChartRequest(BirthData):
    """
    Request model for style chart calculation.

    User's birth data - used to compute natal placements for style features.
    Inherits all fields and validation from domain BirthData model.
    """

    pass


class StyleChartResponse(BaseModel):
    """
    Style chart response with natal placements needed for style feature generation.

    Returns the user's own natal chart placements (Sun, Venus, Rising) and
    planet data for element distribution calculation.
    """

    planets: dict[str, Any] = Field(
        ...,
        description="Planet positions: {sun: {name, sign, position, house}, ...}",
    )
    points: dict[str, Any] = Field(
        ...,
        description="Chart points: {ascendant: {name, sign, position}, ...}",
    )


def get_profile_service() -> ProfileService | None:
    """
    Dependency injection for ProfileService.

    This will be properly wired in main.py with the provider instance.
    For now, returns None (will be replaced by main.py setup).
    """
    return None


# Called by: backend/app/infrastructure/ai/tools/definitions/image_edit_tool.py (style mode)
@router.post(
    "/style/chart",
    status_code=status.HTTP_200_OK,
    response_model=StyleChartResponse,
    summary="Get natal chart placements for style generation",
    description="Calculate user's natal chart and return placements needed for astro style feature.",
)
async def get_style_chart(
    request: StyleChartRequest,
    profile_service: ProfileService | None = Depends(get_profile_service),
) -> StyleChartResponse:
    """
    Get user's natal chart placements for style feature generation.

    Returns Sun, Venus, Rising signs and all planet data for element distribution.
    Uses the same natal chart calculation as the profile endpoint.

    Args:
        request: User's birth data
        profile_service: Injected profile service (reuses natal chart calculation)

    Returns:
        StyleChartResponse with planets and points from user's natal chart
    """
    assert profile_service is not None, "ProfileService not configured"

    # Generate full profile (natal chart) - reuse existing service
    profile_data = profile_service.generate_profile(birth_data=request)

    natal_chart = profile_data.get("natal_chart", {})
    planets = {k: v for k, v in natal_chart.get("planets", {}).items() if k != "birth_data"}
    points = natal_chart.get("points", {})

    return StyleChartResponse(
        planets=planets,
        points=points,
    )

"""Style chart API endpoint.

# Called by: backend/app/infrastructure/ai/tools/definitions/image_edit_tool.py (style mode)
"""

from typing import Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.domain.models.birth_data import BirthData
from app.infrastructure.compute_runtime import AstrologyComputeRuntime, get_compute_runtime
from app.models.responses import ChartSystemResponse

router = APIRouter(prefix="/astrology", tags=["Style"])


class StyleChartRequest(BirthData):
    """Request model for style chart calculation."""


class StyleChartResponse(BaseModel):
    """Style chart response with natal placements needed for style feature generation."""

    planets: dict[str, Any] = Field(
        ...,
        description="Planet positions: {sun: {name, sign, position, house}, ...}",
    )
    points: dict[str, Any] = Field(
        ...,
        description="Chart points: {ascendant: {name, sign, position}, ...}",
    )
    chart_system: ChartSystemResponse = Field(
        ...,
        description="Chart-system metadata",
    )


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
    compute_runtime: AstrologyComputeRuntime = Depends(get_compute_runtime),
) -> StyleChartResponse:
    """Get user's natal chart placements for style feature generation."""
    result = await compute_runtime.run(
        "style_chart",
        request.model_dump(mode="json"),
        route_name="/api/v1/astrology/style/chart",
    )
    return StyleChartResponse.model_validate(result)

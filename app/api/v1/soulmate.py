"""Soulmate chart API endpoint.

# Called by: backend/app/infrastructure/ai/tools/definitions/soulmate_tool.py
"""

from fastapi import APIRouter, Depends, status

from app.application.soulmate_service import recalculate_soulmate_birth_year
from app.infrastructure.compute_runtime import AstrologyComputeRuntime, get_compute_runtime
from app.models.soulmate import (
    RecalculateBirthDateRequest,
    RecalculateBirthDateResponse,
    SoulmateChartResponse,
    SoulmateRequest,
)

router = APIRouter(prefix="/astrology", tags=["Soulmate"])


# Called by: backend/app/infrastructure/ai/tools/definitions/soulmate_tool.py
@router.post(
    "/soulmate/chart",
    status_code=status.HTTP_200_OK,
    response_model=SoulmateChartResponse,
    summary="Generate soulmate natal chart",
    description="Calculate an ideal soulmate's natal chart based on user's birth data using astrological compatibility principles.",
)
async def get_soulmate_chart(
    request: SoulmateRequest,
    compute_runtime: AstrologyComputeRuntime = Depends(get_compute_runtime),
) -> SoulmateChartResponse:
    """Generate a complete soulmate natal chart."""
    result = await compute_runtime.run(
        "soulmate_chart",
        request.model_dump(mode="json"),
        route_name="/api/v1/astrology/soulmate/chart",
    )
    return SoulmateChartResponse.model_validate(result)


# Called by: backend/app/infrastructure/ai/tools/definitions/soulmate_tool.py
@router.post(
    "/soulmate/recalculate-birth-date",
    status_code=status.HTTP_200_OK,
    response_model=RecalculateBirthDateResponse,
    summary="Recalculate soulmate birth year",
    description="Recalculate soulmate birth year when gender mismatch occurs during soulmate generation.",
)
async def recalculate_birth_date(
    request: RecalculateBirthDateRequest,
) -> RecalculateBirthDateResponse:
    """Recalculate soulmate birth year when gender mismatch occurs."""
    birth_year, min_age, max_age = recalculate_soulmate_birth_year(
        user_birth_year=request.user_birth_year,
        user_gender=request.user_gender,
        soulmate_sex=request.soulmate_sex,
    )
    return RecalculateBirthDateResponse(
        birth_year=birth_year,
        min_age=min_age,
        max_age=max_age,
    )

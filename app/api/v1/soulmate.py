"""Soulmate chart API endpoint.

# Called by: backend/app/infrastructure/ai/tools/definitions/soulmate_tool.py
"""

from fastapi import APIRouter, Depends, status

from app.application.soulmate_service import SoulmateService, recalculate_soulmate_birth_year
from app.models.soulmate import (
    RecalculateBirthDateRequest,
    RecalculateBirthDateResponse,
    SoulmateChartResponse,
    SoulmateRequest,
)

router = APIRouter(prefix="/astrology", tags=["Soulmate"])


def get_soulmate_service() -> SoulmateService | None:
    """
    Dependency injection for SoulmateService.

    This will be properly wired in main.py with the provider instance.
    For now, returns None (will be replaced by main.py setup).
    """
    # This will be overridden in main.py
    return None


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
    soulmate_service: SoulmateService | None = Depends(get_soulmate_service),
) -> SoulmateChartResponse:
    """
    Generate a complete soulmate natal chart.

    Uses astrological compatibility rules to derive ideal partner placements:
    - Soulmate's Ascendant is opposite user's Ascendant (user's Descendant sign)
    - Soulmate's Sun is trine user's Sun (same element, harmonious)
    - Soulmate's Moon is in same or compatible element

    Note: Venus, Mars, and outer planets will be whatever positions exist
    on the derived date, adding natural variation to soulmate charts.

    Returns JSON with:
    - planets: {sun: {name, sign, position, house, retrograde}, ...}
    - houses: {first_house: {sign}, ...}
    - points: {ascendant: {name, sign, position}, midheaven: {...}}
    - aspects: [{p1_name, p2_name, aspect, orbit}, ...]

    Args:
        request: User's birth data
        soulmate_service: Injected soulmate service

    Returns:
        SoulmateChartResponse with complete soulmate chart data

    Raises:
        HTTPException: Handled by FastAPI exception handlers
    """
    assert soulmate_service is not None, "SoulmateService not configured"
    return soulmate_service.generate_soulmate_chart(
        user_birth_data=request,
        user_gender=request.user_gender,
        soulmate_sex=request.soulmate_sex,
    )


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
    """
    Recalculate soulmate birth year when gender mismatch occurs.

    Used when user selects same-sex soulmate after background calculation
    predicted opposite-sex (which used different age range formula).

    This is a lightweight endpoint that only recalculates the birth year
    based on the corrected age range formula, without recalculating the
    full chart.

    Args:
        request: User birth year and gender information

    Returns:
        RecalculateBirthDateResponse with new birth year and age range
    """
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

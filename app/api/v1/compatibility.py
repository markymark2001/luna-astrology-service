"""Synastry API endpoints for relationship compatibility analysis."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import PlainTextResponse

from app.application.compatibility_service import SynastryService
from app.models.requests import SynastryRequest

router = APIRouter(prefix="/astrology", tags=["Synastry"])


def get_synastry_service() -> SynastryService | None:
    """
    Dependency injection for SynastryService.

    This will be properly wired in main.py with the provider instance.
    For now, returns None (will be replaced by main.py setup).
    """
    # This will be overridden in main.py
    return None


@router.post(
    "/synastry",
    status_code=status.HTTP_200_OK,
    response_class=PlainTextResponse,
    summary="Get synastry analysis as compact text",
    description="Calculate synastry aspects between two birth charts, returned as compact text for LLM consumption (~80% token reduction)."
)
async def get_synastry(
    request: SynastryRequest,
    synastry_service: SynastryService | None = Depends(get_synastry_service)
) -> str:
    """
    Get synastry analysis as compact text for LLM context.

    Returns word-based compact format with:
    - SYNASTRY ASPECTS: Person1 Sun conjunct Person2 Moon (orb 2.1)

    Note: Uses CORE preset configuration (10 planets, 2 points, 6 houses, 8° synastry orb).

    Args:
        request: Birth data for both persons
        synastry_service: Injected synastry service

    Returns:
        Compact text optimized for LLM relationship analysis (~80% token reduction)

    Raises:
        HTTPException: Handled by FastAPI exception handlers
    """
    assert synastry_service is not None, "SynastryService not configured"
    return synastry_service.analyze_synastry_compact(
        person1_data=request.person1,
        person2_data=request.person2
    )

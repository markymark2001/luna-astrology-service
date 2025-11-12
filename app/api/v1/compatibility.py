"""Synastry API endpoints for relationship compatibility analysis."""

import json
from fastapi import APIRouter, Depends, status
from fastapi.responses import PlainTextResponse

from app.models.requests import SynastryRequest
from app.application.compatibility_service import SynastryService

router = APIRouter(prefix="/astrology", tags=["Synastry"])


def get_synastry_service() -> SynastryService:
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
    summary="Get synastry analysis as JSON string",
    description="Calculate synastry aspects between two birth charts, returned as standardized JSON string for LLM consumption."
)
async def get_synastry(
    request: SynastryRequest,
    synastry_service: SynastryService = Depends(get_synastry_service)
) -> str:
    """
    Get synastry analysis as JSON string for LLM context.

    Returns JSON string with:
    - synastry: cross-chart aspects only (no redundant natal charts)

    Note: Uses CORE preset configuration (10 planets, 2 points, 6 houses, 8° synastry orb).

    Args:
        request: Birth data for both persons
        synastry_service: Injected synastry service

    Returns:
        JSON string optimized for LLM relationship analysis

    Raises:
        HTTPException: Handled by FastAPI exception handlers
    """
    # Analyze synastry using application service
    synastry_data = synastry_service.analyze_synastry(
        person1_data=request.person1,
        person2_data=request.person2
    )

    # Return data as JSON string directly
    return json.dumps(synastry_data)

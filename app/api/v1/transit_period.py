"""Transit period API endpoints with hexagonal architecture."""

import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse

from app.models.requests import TransitPeriodRequest
from app.application.transit_period_service import TransitPeriodService

router = APIRouter(prefix="/astrology", tags=["Astrology Transit Period"])


def get_transit_period_service() -> TransitPeriodService:
    """
    Dependency injection for TransitPeriodService.

    This will be properly wired in main.py with the provider instance.
    For now, returns None (will be replaced by main.py setup).
    """
    # This will be overridden in main.py
    return None


@router.post(
    "/transits/period",
    status_code=status.HTTP_200_OK,
    response_class=PlainTextResponse,
    summary="Get transit data for a date range as JSON string",
    description="Calculate transits over a date range (past or future) with automatic granularity adjustment, returned as standardized JSON string for LLM consumption."
)
async def get_transit_period(
    request: TransitPeriodRequest,
    transit_period_service: TransitPeriodService = Depends(get_transit_period_service)
) -> str:
    """
    Get transit data for any date range as JSON string for LLM context.

    Works for both past and future dates. Automatically adjusts granularity based on range:
    - 1-7 days: Daily snapshots
    - 8-60 days: Weekly snapshots
    - 61-365 days: Bi-weekly snapshots
    - 366+ days: Monthly snapshots

    Returns JSON string with:
    - period: start, end, days
    - granularity: "daily" | "weekly" | "bi-weekly" | "monthly"
    - natal_chart: Planets, houses, points, natal aspects
    - snapshots: Array of transit data at regular intervals
    - snapshot_count: Number of snapshots generated

    Note: Uses CORE preset configuration (10 planets, 2 points, 6 houses, 4° orbs).

    Args:
        request: Birth data with start_date and end_date
        transit_period_service: Injected transit period service

    Returns:
        JSON string optimized for LLM context

    Raises:
        HTTPException: Handled by FastAPI exception handlers
    """
    try:
        # Generate transit period using application service
        period_data = transit_period_service.generate_transit_period(
            birth_data=request,
            start_date=request.start_date,
            end_date=request.end_date
        )

        # Return data as JSON string directly
        return json.dumps(period_data)

    except ValueError as e:
        # Validation errors (e.g., invalid date range)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate transit period: {str(e)}"
        )

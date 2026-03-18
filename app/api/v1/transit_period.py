"""Transit period API endpoints with hexagonal architecture."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse

from app.infrastructure.compute_runtime import AstrologyComputeRuntime, get_compute_runtime
from app.models.requests import TransitPeriodRequest

router = APIRouter(prefix="/astrology", tags=["Astrology Transit Period"])


# Called by: backend/app/infrastructure/ai/tools/definitions/transit_period_tool.py
@router.post(
    "/transits/period",
    status_code=status.HTTP_200_OK,
    response_class=PlainTextResponse,
    summary="Get transit data for a date range as compact text",
    description="Calculate transits over a date range (past or future) with automatic granularity adjustment, returned as compact text for LLM consumption (~80% token reduction)."
)
async def get_transit_period(
    request: TransitPeriodRequest,
    compute_runtime: AstrologyComputeRuntime = Depends(get_compute_runtime),
) -> str:
    """Get transit data for any date range as compact text for LLM context."""
    try:
        return await compute_runtime.run(
            "transit_period_compact",
            request.model_dump(mode="json"),
            route_name="/api/v1/astrology/transits/period",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate transit period: {str(e)}"
        )

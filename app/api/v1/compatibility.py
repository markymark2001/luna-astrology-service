"""Synastry API endpoints for relationship compatibility analysis."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import PlainTextResponse

from app.infrastructure.compute_runtime import AstrologyComputeRuntime, get_compute_runtime
from app.models.requests import SynastryRequest

router = APIRouter(prefix="/astrology", tags=["Synastry"])


# Called by: backend/app/infrastructure/repositories/http_astrology_repository.py
@router.post(
    "/synastry",
    status_code=status.HTTP_200_OK,
    response_class=PlainTextResponse,
    summary="Get synastry analysis as compact text",
    description="Calculate synastry aspects between two birth charts, returned as compact text for LLM consumption (~80% token reduction)."
)
async def get_synastry(
    request: SynastryRequest,
    compute_runtime: AstrologyComputeRuntime = Depends(get_compute_runtime),
) -> str:
    """Get synastry analysis as compact text for LLM context."""
    return await compute_runtime.run(
        "synastry_compact",
        request.model_dump(mode="json"),
        route_name="/api/v1/astrology/synastry",
    )

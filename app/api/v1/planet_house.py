"""Planet house position API endpoint."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.exceptions import ChartCalculationException, InvalidBirthDataException
from app.infrastructure.compute_runtime import AstrologyComputeRuntime, get_compute_runtime
from app.models.requests import PlanetHouseRequest
from app.models.responses import PlanetHouseResponse

router = APIRouter(prefix="/astrology", tags=["Astrology Planet House"])


# Called by: backend/app/application/get_home_content.py
@router.post(
    "/planet-house",
    status_code=status.HTTP_200_OK,
    response_model=PlanetHouseResponse,
    summary="Get a planet's house position",
    description="Calculate natal chart and return a specific planet's house position and sign."
)
async def get_planet_house(
    request: PlanetHouseRequest,
    compute_runtime: AstrologyComputeRuntime = Depends(get_compute_runtime),
) -> PlanetHouseResponse:
    """Get a specific planet's house position in the natal chart."""
    try:
        result = await compute_runtime.run(
            "planet_house",
            request.model_dump(mode="json"),
            route_name="/api/v1/astrology/planet-house",
        )
        return PlanetHouseResponse.model_validate(result)
    except InvalidBirthDataException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except (ChartCalculationException, RuntimeError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

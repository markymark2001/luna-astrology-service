"""Planet house position API endpoint."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.profile_service import ProfileService
from app.core.exceptions import ChartCalculationException, InvalidBirthDataException
from app.models.requests import PlanetHouseRequest
from app.models.responses import PlanetHouseResponse

router = APIRouter(prefix="/astrology", tags=["Astrology Planet House"])

# Kerykeion house name to number mapping
HOUSE_NAME_TO_NUMBER = {
    "First_House": 1,
    "Second_House": 2,
    "Third_House": 3,
    "Fourth_House": 4,
    "Fifth_House": 5,
    "Sixth_House": 6,
    "Seventh_House": 7,
    "Eighth_House": 8,
    "Ninth_House": 9,
    "Tenth_House": 10,
    "Eleventh_House": 11,
    "Twelfth_House": 12,
}


def get_profile_service() -> ProfileService | None:
    """
    Dependency injection for ProfileService.

    This will be properly wired in main.py with the provider instance.
    For now, returns None (will be replaced by main.py setup).
    """
    # This will be overridden in main.py
    return None


@router.post(
    "/planet-house",
    status_code=status.HTTP_200_OK,
    response_model=PlanetHouseResponse,
    summary="Get a planet's house position",
    description="Calculate natal chart and return a specific planet's house position and sign."
)
async def get_planet_house(
    request: PlanetHouseRequest,
    profile_service: ProfileService | None = Depends(get_profile_service)
) -> PlanetHouseResponse:
    """
    Get a specific planet's house position in the natal chart.

    Returns:
    - planet: Planet name
    - house: House number (1-12) as integer
    - sign: Zodiac sign the planet is in

    Args:
        request: Birth data and planet name
        profile_service: Injected profile service

    Returns:
        PlanetHouseResponse with planet, house number, and sign

    Raises:
        HTTPException: 400 for invalid data, 404 if planet not found, 500 for calculation errors
    """
    assert profile_service is not None, "ProfileService not configured"
    try:
        # Generate natal chart using profile service
        profile_data = profile_service.generate_profile(
            birth_data=request,
            transit_date=None  # We only need natal chart
        )

        # Extract planet data from natal chart
        natal_chart = profile_data.get("natal_chart", {})
        planets = natal_chart.get("planets", {})
        planet_name = request.planet.lower()

        planet_data = planets.get(planet_name)
        if not planet_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planet '{request.planet}' not found in natal chart. Available planets: {list(planets.keys())}"
            )

        # Extract house and sign
        house = planet_data.get("house")
        sign = planet_data.get("sign")

        if house is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"House position not available for planet '{request.planet}'"
            )

        if sign is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Sign not available for planet '{request.planet}'"
            )

        # Convert house to integer (handle both "Sixth_House" and integer formats)
        house_int = None
        if isinstance(house, int):
            house_int = house
        elif isinstance(house, str):
            # Try mapping first (e.g., "Sixth_House" -> 6)
            house_int = HOUSE_NAME_TO_NUMBER.get(house)
            if house_int is None:
                # Try direct int conversion (e.g., "6" -> 6)
                try:
                    house_int = int(house)
                except ValueError:
                    pass

        if house_int is None or not 1 <= house_int <= 12:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid house value '{house}' - could not convert to house number (1-12)"
            )

        return PlanetHouseResponse(
            planet=planet_name,
            house=house_int,
            sign=sign
        )

    except InvalidBirthDataException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ChartCalculationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

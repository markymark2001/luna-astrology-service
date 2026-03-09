"""Standardized API response models."""

from pydantic import BaseModel, Field


class ChartSystemResponse(BaseModel):
    """Canonical chart-system metadata for astrology responses."""

    id: str = Field(..., description="Stable chart-system identifier")
    zodiac_type: str = Field(..., description="Zodiac framework used for calculations")
    house_system: str = Field(..., description="House system label")
    house_system_identifier: str = Field(..., description="Provider-specific house system code")
    perspective_type: str = Field(..., description="Coordinate perspective used for calculations")
    provider: str = Field(..., description="Underlying astrology engine")
    sidereal_mode: str | None = Field(None, description="Sidereal mode when sidereal charts are used")


class PlanetHouseResponse(BaseModel):
    """Response model for planet house position."""

    planet: str = Field(..., description="Planet name")
    house: int = Field(..., description="House number (1-12)")
    sign: str = Field(..., description="Zodiac sign the planet is in")
    chart_system: ChartSystemResponse = Field(..., description="Chart-system metadata")


class PlacementItem(BaseModel):
    """A single planetary or point placement in the natal chart."""

    name: str = Field(..., description="Name of the celestial body (e.g., 'Sun', 'Moon')")
    sign: str = Field(..., description="Zodiac sign (e.g., 'Aries', 'Cancer')")
    house: int | None = Field(None, description="House number (1-12), None for points like Ascendant")


class PlacementsResponse(BaseModel):
    """Response model for profile placements endpoint."""

    sun: PlacementItem = Field(..., description="Sun placement")
    moon: PlacementItem = Field(..., description="Moon placement")
    ascendant: PlacementItem = Field(..., description="Ascendant (Rising sign) placement")
    planets: list[PlacementItem] = Field(
        ...,
        description="All 10 planets with their signs and houses"
    )
    chart_system: ChartSystemResponse = Field(..., description="Chart-system metadata")

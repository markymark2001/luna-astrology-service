"""Standardized API response models."""

from pydantic import BaseModel, Field


class PlanetHouseResponse(BaseModel):
    """Response model for planet house position."""

    planet: str = Field(..., description="Planet name")
    house: int = Field(..., description="House number (1-12)")
    sign: str = Field(..., description="Zodiac sign the planet is in")


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

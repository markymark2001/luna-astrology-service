"""Standardized API response models."""

from pydantic import BaseModel, Field


class PlanetHouseResponse(BaseModel):
    """Response model for planet house position."""

    planet: str = Field(..., description="Planet name")
    house: int = Field(..., description="House number (1-12)")
    sign: str = Field(..., description="Zodiac sign the planet is in")

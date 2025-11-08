"""Celestial body domain models."""

from typing import Optional
from pydantic import BaseModel


class CelestialBody(BaseModel):
    """Base model for celestial bodies (planets, points, houses)."""

    name: str
    sign: Optional[str] = None
    position: Optional[float] = None
    retrograde: Optional[bool] = None
    house: Optional[str] = None


class Planet(CelestialBody):
    """Planet model (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto)."""
    pass


class Point(CelestialBody):
    """Astrological point model (North Node, South Node, Chiron, etc.)."""
    pass


class House(BaseModel):
    """Astrological house model."""

    name: str
    sign: Optional[str] = None
    position: Optional[float] = None

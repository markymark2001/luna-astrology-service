"""Celestial body domain models."""


from pydantic import BaseModel


class CelestialBody(BaseModel):
    """Base model for celestial bodies (planets, points, houses)."""

    name: str
    sign: str | None = None
    position: float | None = None
    retrograde: bool | None = None
    house: str | None = None


class Planet(CelestialBody):
    """Planet model (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto)."""
    pass


class Point(CelestialBody):
    """Astrological point model (North Node, South Node, Chiron, etc.)."""
    pass


class House(BaseModel):
    """Astrological house model."""

    name: str
    sign: str | None = None
    position: float | None = None

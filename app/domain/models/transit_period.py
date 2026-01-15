"""Transit period domain model - represents active transits with timing."""

from datetime import date

from pydantic import BaseModel


class TransitAspect(BaseModel):
    """A single transit aspect with timing information."""

    transit_planet: str
    natal_planet: str
    aspect_type: str  # conjunction, opposition, square, trine, sextile
    start_date: date
    end_date: date
    exact_date: date
    exact_orb: float  # Orb at exact date (closest approach)

    class Config:
        frozen = True


class TransitPeriodResult(BaseModel):
    """Result of transit period calculation with grouped aspects."""

    start_date: date
    end_date: date
    aspects: list[TransitAspect]

    class Config:
        arbitrary_types_allowed = True

"""Transit period domain model - represents active transits with timing."""

from datetime import date

from pydantic import BaseModel, ConfigDict


class TransitAspect(BaseModel):
    """A single transit aspect with timing information."""

    model_config = ConfigDict(frozen=True)

    transit_planet: str
    natal_planet: str
    aspect_type: str  # conjunction, opposition, square, trine, sextile
    start_date: date
    end_date: date
    exact_date: date
    exact_orb: float  # Orb at exact date (closest approach)


class TransitPeriodResult(BaseModel):
    """Result of transit period calculation with grouped aspects."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    start_date: date
    end_date: date
    aspects: list[TransitAspect]

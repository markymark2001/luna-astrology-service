"""Aspect domain model."""


from pydantic import BaseModel


class Aspect(BaseModel):
    """Astrological aspect between two celestial bodies."""

    p1_name: str
    p2_name: str
    aspect: str
    orbit: float
    aspect_degrees: float | None = None
    aid: int | None = None
    diff: float | None = None
    p1_abs_pos: float | None = None
    p2_abs_pos: float | None = None

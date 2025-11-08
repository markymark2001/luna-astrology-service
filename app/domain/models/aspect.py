"""Aspect domain model."""

from typing import Optional
from pydantic import BaseModel


class Aspect(BaseModel):
    """Astrological aspect between two celestial bodies."""

    p1_name: str
    p2_name: str
    aspect: str
    orbit: float
    aspect_degrees: Optional[float] = None
    aid: Optional[int] = None
    diff: Optional[float] = None
    p1_abs_pos: Optional[float] = None
    p2_abs_pos: Optional[float] = None

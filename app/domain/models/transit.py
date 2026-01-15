"""Transit domain model."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class Transit(BaseModel):
    """
    Transit positions and aspects at a specific date/time.

    Represents current planetary positions and their aspects to a natal chart.
    """

    date: datetime
    planets: dict[str, Any]
    aspects_to_natal: list[Any]
    current_sky_aspects: list[Any]

    class Config:
        arbitrary_types_allowed = True

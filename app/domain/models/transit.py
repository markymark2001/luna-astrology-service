"""Transit domain model."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class Transit(BaseModel):
    """
    Transit positions and aspects at a specific date/time.

    Represents current planetary positions and their aspects to a natal chart.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    date: datetime
    planets: dict[str, Any]
    aspects_to_natal: list[Any]
    current_sky_aspects: list[Any]

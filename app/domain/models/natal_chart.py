"""Natal chart domain model."""

from typing import Any, Optional
from pydantic import BaseModel, Field

from app.domain.models.birth_data import BirthData


class NatalChart(BaseModel):
    """
    Natal chart aggregate root.

    Contains all astrological data for a person's birth chart.
    """

    birth_data: BirthData
    planets: dict[str, Any]
    houses: dict[str, Any]
    points: dict[str, Any]
    aspects: list[Any]

    # Optional: keep reference to provider-specific object for advanced operations
    # This allows synastry calculations without recalculating the chart
    provider_data: Optional[Any] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

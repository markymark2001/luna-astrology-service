"""Synastry domain model."""

from typing import Any
from pydantic import BaseModel

from app.domain.models.natal_chart import NatalChart


class Synastry(BaseModel):
    """
    Synastry analysis between two natal charts.

    Represents relationship compatibility data.
    """

    chart1: NatalChart
    chart2: NatalChart
    aspects: list[Any]

    class Config:
        arbitrary_types_allowed = True

"""Synastry domain model."""

from typing import Any

from pydantic import BaseModel, ConfigDict

from app.domain.models.natal_chart import NatalChart


class RelationshipScore(BaseModel):
    """
    Relationship compatibility score using Ciro Discepolo's method.

    Calculated by Kerykeion's RelationshipScoreFactory.
    """

    score_value: int
    is_destiny_sign: bool


class Synastry(BaseModel):
    """
    Synastry analysis between two natal charts.

    Represents relationship compatibility data.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    chart1: NatalChart
    chart2: NatalChart
    aspects: list[Any]
    relationship_score: RelationshipScore | None = None

"""Shared chart payload builders for application services."""

from app.core.llm_formatter import filter_aspects, simplify_planets
from app.domain.models import NatalChart


def natal_chart_payload(natal_chart: NatalChart) -> dict:
    """Build the standard natal-chart payload used by profile-style responses."""
    return {
        "birth_data": natal_chart.planets.get("birth_data"),
        "planets": {k: v for k, v in natal_chart.planets.items() if k != "birth_data"},
        "houses": natal_chart.houses,
        "points": natal_chart.points,
    }


def llm_natal_chart_payload(natal_chart: NatalChart) -> dict:
    """Build the simplified natal-chart payload used by compact transit responses."""
    natal_planets = {k: v for k, v in natal_chart.planets.items() if k != "birth_data"}
    return {
        "birth_data": natal_chart.planets.get("birth_data"),
        "planets": simplify_planets(natal_planets),
        "houses": natal_chart.houses,
        "points": simplify_planets(natal_chart.points),
        "aspects": filter_aspects(natal_chart.aspects),
    }

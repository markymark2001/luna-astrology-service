"""Regression tests for astrology preset configuration."""

from app.config.astrology_presets import DetailLevel, get_preset
from app.config.chart_system import DEFAULT_CHART_SYSTEM
from app.domain.models import BirthData
from app.infrastructure.providers.kerykeion_provider import KerykeionProvider


def test_core_preset_includes_north_node_in_points():
    """CORE profiles should request the actual Kerykeion North Node field."""
    config = get_preset(DetailLevel.CORE)

    assert "true_north_lunar_node" in config.points


def test_core_provider_extracts_north_node_into_points():
    """CORE chart payloads should surface North Node in the points mapping."""
    provider = KerykeionProvider(
        config=get_preset(DetailLevel.CORE),
        chart_system=DEFAULT_CHART_SYSTEM,
    )

    chart = provider.calculate_natal_chart(
        BirthData(
            year=1990,
            month=3,
            day=15,
            hour=14,
            minute=30,
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York",
        )
    )

    assert "true_north_lunar_node" in chart.points

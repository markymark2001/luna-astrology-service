"""Tests for the canonical chart-system configuration."""

from datetime import date

import pytest

from app.config.astrology_presets import DEFAULT_CONFIG
from app.config.chart_system import DEFAULT_CHART_SYSTEM
from app.domain.models import BirthData
from app.infrastructure.providers.kerykeion_provider import KerykeionProvider


def _birth_data() -> BirthData:
    return BirthData(
        year=1990,
        month=6,
        day=15,
        hour=14,
        minute=30,
        latitude=40.7128,
        longitude=-74.0060,
        timezone="America/New_York",
    )


def _provider() -> KerykeionProvider:
    return KerykeionProvider(config=DEFAULT_CONFIG, chart_system=DEFAULT_CHART_SYSTEM)


def test_natal_chart_uses_explicit_tropical_placidus_settings():
    provider = _provider()

    natal_chart = provider.calculate_natal_chart(_birth_data())
    subject = natal_chart.provider_data

    assert natal_chart.chart_system["id"] == "western_tropical_placidus"
    assert subject.zodiac_type == "Tropical"
    assert subject.houses_system_identifier == "P"
    assert subject.sidereal_mode is None
    assert subject.perspective_type == "Apparent Geocentric"


def test_placidus_house_cusps_are_not_snapped_to_sign_boundaries():
    provider = _provider()

    natal_chart = provider.calculate_natal_chart(_birth_data())
    first_house_abs_pos = natal_chart.houses["first_house"]["abs_pos"]
    second_house_abs_pos = natal_chart.houses["second_house"]["abs_pos"]

    assert natal_chart.houses["first_house"]["sign"] == natal_chart.points["ascendant"]["sign"]
    assert first_house_abs_pos == pytest.approx(193.6954, abs=0.01)
    assert second_house_abs_pos == pytest.approx(220.7712, abs=0.01)


def test_ephemeris_points_use_same_chart_system_settings():
    provider = _provider()

    points = provider.generate_ephemeris_for_range(
        start_date=date(2000, 1, 1),
        end_date=date(2000, 1, 3),
        location=_birth_data(),
    )

    assert points
    assert points[0].zodiac_type == "Tropical"
    assert points[0].houses_system_identifier == "P"
    assert points[0].sidereal_mode is None

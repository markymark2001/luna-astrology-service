"""Tests for the canonical chart-system configuration."""

from datetime import date

from app.config.astrology_presets import DEFAULT_CONFIG
from app.config.chart_system import DEFAULT_CHART_SYSTEM
from app.domain.models import BirthData
from app.infrastructure.providers.kerykeion_provider import KerykeionProvider

ZODIAC_SIGNS = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]


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


def test_natal_chart_uses_explicit_tropical_whole_sign_settings():
    provider = _provider()

    natal_chart = provider.calculate_natal_chart(_birth_data())
    subject = natal_chart.provider_data

    assert natal_chart.chart_system["id"] == "western_tropical_whole_sign"
    assert subject.zodiac_type == "Tropical"
    assert subject.houses_system_identifier == "W"
    assert subject.sidereal_mode is None
    assert subject.perspective_type == "Apparent Geocentric"


def test_whole_sign_houses_follow_ascendant_sign_sequence():
    provider = _provider()

    natal_chart = provider.calculate_natal_chart(_birth_data())
    ascendant_sign = natal_chart.points["ascendant"]["sign"]
    start_index = ZODIAC_SIGNS.index(ascendant_sign)

    assert natal_chart.houses["first_house"]["sign"] == ascendant_sign

    house_names = [
        "first_house",
        "second_house",
        "third_house",
        "fourth_house",
        "fifth_house",
        "sixth_house",
        "seventh_house",
        "eighth_house",
        "ninth_house",
        "tenth_house",
        "eleventh_house",
        "twelfth_house",
    ]
    for offset, house_name in enumerate(house_names):
        expected_sign = ZODIAC_SIGNS[(start_index + offset) % len(ZODIAC_SIGNS)]
        assert natal_chart.houses[house_name]["sign"] == expected_sign


def test_ephemeris_points_use_same_chart_system_settings():
    provider = _provider()

    points = provider.generate_ephemeris_for_range(
        start_date=date(2000, 1, 1),
        end_date=date(2000, 1, 3),
        location=_birth_data(),
    )

    assert points
    assert points[0].zodiac_type == "Tropical"
    assert points[0].houses_system_identifier == "W"
    assert points[0].sidereal_mode is None

"""Timezone defaulting tests for ProfileService."""

from datetime import UTC
from types import SimpleNamespace

from app.application.profile_service import ProfileService
from app.domain.models import BirthData


class FakeProvider:
    def __init__(self):
        self.last_transit_date = None

    def calculate_natal_chart(self, birth_data):
        return SimpleNamespace(
            chart_system={
                "id": "western_tropical_placidus",
                "zodiac_type": "Tropical",
                "house_system": "Placidus",
                "house_system_identifier": "P",
                "perspective_type": "Apparent Geocentric",
                "provider": "kerykeion",
                "sidereal_mode": None,
            },
            planets={"birth_data": {"timezone": birth_data.timezone}, "sun": {}},
            houses={},
            points={},
            aspects=[],
            birth_data=birth_data,
            provider_data=None,
        )

    def calculate_transits(self, natal_chart, transit_date):
        self.last_transit_date = transit_date
        return SimpleNamespace(
            date=transit_date,
            planets={},
            points={"true_north_lunar_node": {"name": "True_North_Lunar_Node"}},
            aspects_to_natal=[],
            current_sky_aspects=[],
        )


def _birth_data(timezone_name: str) -> BirthData:
    return BirthData(
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=0,
        latitude=51.5074,
        longitude=-0.1278,
        timezone=timezone_name,
    )


def test_generate_profile_defaults_to_birth_timezone_now():
    provider = FakeProvider()
    service = ProfileService(provider=provider)

    service.generate_profile(_birth_data("America/New_York"))

    assert provider.last_transit_date is not None
    assert getattr(provider.last_transit_date.tzinfo, "key", None) == "America/New_York"


def test_resolve_now_for_birth_timezone_falls_back_to_utc():
    resolved = ProfileService._resolve_now_for_birth_timezone(_birth_data("Invalid/Timezone"))
    assert resolved.tzinfo == UTC


def test_generate_profile_includes_chart_system_metadata():
    provider = FakeProvider()
    service = ProfileService(provider=provider)

    result = service.generate_profile(_birth_data("America/New_York"))

    assert result["chart_system"]["id"] == "western_tropical_placidus"


def test_generate_profile_includes_transit_points():
    provider = FakeProvider()
    service = ProfileService(provider=provider)

    result = service.generate_profile(_birth_data("America/New_York"))

    assert result["transits"]["points"]["true_north_lunar_node"]["name"] == "True_North_Lunar_Node"

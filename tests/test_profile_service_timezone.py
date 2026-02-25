"""Timezone defaulting tests for ProfileService."""

from datetime import UTC, date, datetime
from types import SimpleNamespace

from app.application.profile_service import ProfileService
from app.domain.models import BirthData


class FakeProvider:
    def __init__(self):
        self.last_transit_date = None
        self.last_start_date = None
        self.last_end_date = None

    def calculate_natal_chart(self, birth_data):
        return SimpleNamespace(
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
            aspects_to_natal=[],
            current_sky_aspects=[],
        )

    def calculate_transit_periods(self, natal_chart, start_date, end_date):
        self.last_start_date = start_date
        self.last_end_date = end_date
        return SimpleNamespace(aspects=[])


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


def test_generate_monthly_profile_uses_birth_timezone_month(monkeypatch):
    provider = FakeProvider()

    class FixedNowProfileService(ProfileService):
        @staticmethod
        def _resolve_now_for_birth_timezone(birth_data: BirthData) -> datetime:
            return datetime(2026, 2, 3, 10, 0, tzinfo=UTC)

    service = FixedNowProfileService(provider=provider)

    import app.application.profile_service as profile_service_module

    monkeypatch.setattr(
        profile_service_module,
        "format_monthly_profile",
        lambda chart_data, transit_data: "formatted-monthly-profile",
    )

    result = service.generate_monthly_profile_compact(_birth_data("Europe/London"))

    assert result == "formatted-monthly-profile"
    assert provider.last_start_date == date(2026, 2, 1)
    assert provider.last_end_date == date(2026, 2, 28)

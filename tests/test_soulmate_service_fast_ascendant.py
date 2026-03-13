"""Tests for fast ascendant lookup edge cases."""

from datetime import date, datetime

from app.application.soulmate_service import SoulmateService
from app.domain.models import BirthData, NatalChart, Synastry, Transit, TransitPeriodResult
from app.domain.ports import IAstrologyProvider


class _DummyProvider(IAstrologyProvider):
    """Provider stub for fast ascendant tests."""

    def calculate_natal_chart(self, birth_data: BirthData) -> NatalChart:
        if birth_data.hour == 0 and birth_data.minute == 0:
            return NatalChart(
                birth_data=birth_data,
                chart_system={},
                planets={},
                houses={},
                points={"ascendant": {"abs_pos": 0.0, "sign": "Ari"}},
                aspects=[],
            )
        raise ValueError("DST gap local time")

    def calculate_synastry(self, chart1: NatalChart, chart2: NatalChart) -> Synastry:
        raise NotImplementedError

    def calculate_transits(self, natal_chart: NatalChart, transit_date: datetime) -> Transit:
        raise NotImplementedError

    def calculate_transit_periods(
        self,
        natal_chart: NatalChart,
        start_date: date,
        end_date: date,
    ) -> TransitPeriodResult:
        raise NotImplementedError


def test_find_hour_for_ascendant_fast_falls_back_when_verification_is_invalid(monkeypatch):
    """Fast search should use brute-force fallback when verification time is invalid."""
    service = SoulmateService(provider=_DummyProvider())

    def _fallback(*args, **kwargs):
        return (3, 15)

    monkeypatch.setattr(service, "_find_hour_for_ascendant", _fallback)

    result = service._find_hour_for_ascendant_fast(
        year=2024,
        month=3,
        day=10,
        target_rising_sign="Lib",
        latitude=40.73,
        longitude=-73.93,
        timezone="America/New_York",
    )

    assert result == (3, 15)

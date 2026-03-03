"""Tests for transit timezone normalization used by Kerykeion provider."""

from datetime import datetime

from app.core.temporal import normalize_transit_for_chart_timezone


def test_normalize_transit_preserves_absolute_instant_for_chart_timezone():
    """2026-03-03T10:00:00-08:00 should become 2026-03-03 18:00 in Europe/London."""
    transit_date = datetime.fromisoformat("2026-03-03T10:00:00-08:00")

    normalized = normalize_transit_for_chart_timezone(
        transit_date=transit_date,
        chart_timezone="Europe/London",
    )

    assert getattr(normalized.tzinfo, "key", None) == "Europe/London"
    assert normalized.hour == 18
    assert normalized.minute == 0

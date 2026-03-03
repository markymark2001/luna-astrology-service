"""Temporal helpers for timezone-safe transit calculations."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_UTC_TIMEZONE = ZoneInfo("UTC")


def normalize_transit_for_chart_timezone(
    transit_date: datetime,
    chart_timezone: str | None,
) -> datetime:
    """
    Normalize transit datetime to chart timezone without losing absolute instant.

    Rules:
    - Aware transit_date: preserve instant via astimezone(chart_tz)
    - Naive transit_date: treat as local clock in chart_tz (backward compatibility)
    - Invalid/missing chart timezone: fallback to UTC
    """
    target_tz = _resolve_zone(chart_timezone)

    if transit_date.tzinfo is None:
        return transit_date.replace(tzinfo=target_tz)

    return transit_date.astimezone(target_tz)


def _resolve_zone(timezone_name: str | None):
    """Resolve timezone name to ZoneInfo, with UTC fallback."""
    if timezone_name:
        try:
            return ZoneInfo(timezone_name)
        except (ZoneInfoNotFoundError, ValueError):
            pass
    return _UTC_TIMEZONE

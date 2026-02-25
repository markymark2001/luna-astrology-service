"""Profile application service - orchestrates natal chart and transit calculations."""

from calendar import monthrange
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.core.llm_formatter import format_monthly_profile, format_natal_chart, format_personal_profile
from app.domain.models import BirthData
from app.domain.ports import IAstrologyProvider


class ProfileService:
    """
    Application service for generating astrological profiles.

    Orchestrates natal chart and transit calculations for a complete profile.
    """

    def __init__(self, provider: IAstrologyProvider):
        """
        Initialize with astrology provider.

        Args:
            provider: Astrology calculation provider (injected dependency)
        """
        self.provider = provider

    @staticmethod
    def _resolve_now_for_birth_timezone(birth_data: BirthData) -> datetime:
        """
        Resolve current datetime using the subject's timezone.

        Falls back to UTC for invalid timezone strings.
        """
        timezone_name = birth_data.timezone or "UTC"
        try:
            return datetime.now(ZoneInfo(timezone_name))
        except (ZoneInfoNotFoundError, ValueError):
            return datetime.now(UTC)

    def generate_profile(self, birth_data: BirthData, transit_date: datetime | None = None) -> dict:
        """
        Generate complete astrological profile (natal chart + transits).

        Args:
            birth_data: Birth information
            transit_date: Date for transit calculation (defaults to now)

        Returns:
            Dict containing natal chart data, natal aspects, and current transits
        """
        # Calculate natal chart
        natal_chart = self.provider.calculate_natal_chart(birth_data)

        # Calculate transits (default to now if not specified)
        if transit_date is None:
            transit_date = self._resolve_now_for_birth_timezone(birth_data)

        transits = self.provider.calculate_transits(natal_chart, transit_date)

        # Build response
        return {
            "natal_chart": {
                "birth_data": natal_chart.planets.get("birth_data"),
                "planets": {k: v for k, v in natal_chart.planets.items() if k != "birth_data"},
                "houses": natal_chart.houses,
                "points": natal_chart.points
            },
            "aspects": {
                "natal": natal_chart.aspects,
                "transits_to_natal": transits.aspects_to_natal,
                "current_sky": transits.current_sky_aspects
            },
            "transits": {
                "date": transits.date.isoformat(),
                "planets": transits.planets
            }
        }

    def generate_profile_compact(self, birth_data: BirthData, transit_date: datetime | None = None) -> str:
        """
        Generate LLM-optimized compact astrological profile.

        Args:
            birth_data: Birth information
            transit_date: Date for transit calculation (defaults to now)

        Returns:
            Compact text format optimized for LLM consumption (~80% token reduction)
        """
        profile_data = self.generate_profile(birth_data, transit_date)
        return format_natal_chart(profile_data)

    def generate_personal_profile_compact(self, birth_data: BirthData, transit_date: datetime | None = None) -> str:
        """
        Generate person-specific profile, excluding current sky positions.

        Unlike generate_profile_compact, this excludes CURRENT TRANSITS (where planets
        are today) since those are identical for everyone. Includes only person-specific
        data: natal chart + how today's transits aspect THIS person's chart.

        Use this for context providers where the same transit positions would be
        redundantly included for multiple people.

        Args:
            birth_data: Birth information
            transit_date: Date for transit calculation (defaults to now)

        Returns:
            Compact text excluding current sky positions
        """
        profile_data = self.generate_profile(birth_data, transit_date)
        return format_personal_profile(profile_data)

    def generate_monthly_profile_compact(self, birth_data: BirthData) -> str:
        """
        Generate natal chart + monthly transits for proactive messages.

        Excludes daily transits since proactive messages may be viewed at any time.
        Uses current month for transit calculations.

        Args:
            birth_data: Birth information

        Returns:
            Compact text with natal chart + monthly transits (no daily transits)
        """
        # Calculate natal chart (without transits)
        natal_chart = self.provider.calculate_natal_chart(birth_data)

        # Build natal chart data structure
        chart_data = {
            "natal_chart": {
                "birth_data": natal_chart.planets.get("birth_data"),
                "planets": {k: v for k, v in natal_chart.planets.items() if k != "birth_data"},
                "houses": natal_chart.houses,
                "points": natal_chart.points
            },
            "aspects": {
                "natal": natal_chart.aspects,
            }
        }

        # Calculate current month date range
        today = self._resolve_now_for_birth_timezone(birth_data).date()
        first_day = date(today.year, today.month, 1)
        last_day = date(today.year, today.month, monthrange(today.year, today.month)[1])

        # Calculate monthly transits using transit periods
        transit_result = self.provider.calculate_transit_periods(
            natal_chart=natal_chart,
            start_date=first_day,
            end_date=last_day
        )

        # Build transit data structure
        transit_data = {
            "period": {
                "start": first_day.isoformat(),
                "end": last_day.isoformat(),
            },
            "transit_aspects": [
                {
                    "transit_planet": asp.transit_planet,
                    "natal_planet": asp.natal_planet,
                    "aspect_type": asp.aspect_type,
                    "start_date": asp.start_date.isoformat(),
                    "end_date": asp.end_date.isoformat(),
                    "exact_date": asp.exact_date.isoformat(),
                    "exact_orb": asp.exact_orb,
                }
                for asp in transit_result.aspects
            ]
        }

        return format_monthly_profile(chart_data, transit_data)

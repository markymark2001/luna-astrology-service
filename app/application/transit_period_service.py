"""Transit period application service - calculates transits over a date range."""

from datetime import datetime, timedelta, timezone
from typing import Literal

from app.domain.models import BirthData
from app.domain.ports import IAstrologyProvider


GranularityType = Literal["daily", "weekly", "monthly", "quarterly", "bi-yearly"]


class TransitPeriodService:
    """
    Application service for generating transit data over a date range.

    Automatically adjusts granularity based on range to maintain consistent context length.
    """

    def __init__(self, provider: IAstrologyProvider):
        """
        Initialize with astrology provider.

        Args:
            provider: Astrology calculation provider (injected dependency)
        """
        self.provider = provider

    def generate_transit_period(
        self,
        birth_data: BirthData,
        start_date: str,
        end_date: str
    ) -> dict:
        """
        Generate transit data for a date range with automatic granularity adjustment.

        Args:
            birth_data: Birth information
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            Dict containing period metadata, granularity, and transit snapshots
        """
        # Parse dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(
            hour=12, minute=0, second=0, tzinfo=timezone.utc
        )
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(
            hour=12, minute=0, second=0, tzinfo=timezone.utc
        )

        # Validate date range
        if start_dt > end_dt:
            raise ValueError("start_date must be before or equal to end_date")

        # Calculate days in range and determine granularity
        days_diff = (end_dt - start_dt).days
        granularity, interval_days = self._determine_granularity(days_diff)

        # Calculate natal chart once
        natal_chart = self.provider.calculate_natal_chart(birth_data)

        # Generate transit snapshots at regular intervals
        snapshots = []
        current_dt = start_dt

        while current_dt <= end_dt:
            # Calculate transits for this date
            transits = self.provider.calculate_transits(natal_chart, current_dt)

            # Build optimized snapshot
            snapshot = {
                "date": current_dt.strftime("%Y-%m-%d"),
                "transits": {
                    "planets": self._simplify_planet_data(transits.planets)
                },
                "aspects": {
                    # Only transit-to-natal aspects (most relevant for personal forecasting)
                    # Filtered to major aspects with tight orbs
                    "transits_to_natal": self._filter_aspects(transits.aspects_to_natal, 4.0)
                    # Removed current_sky aspects (less relevant for personal forecasts)
                }
            }
            snapshots.append(snapshot)

            # Move to next interval
            current_dt += timedelta(days=interval_days)

        # Build response with optimized natal chart data
        natal_planets = {k: v for k, v in natal_chart.planets.items() if k != "birth_data"}

        return {
            "period": {
                "start": start_date,
                "end": end_date,
                "days": days_diff
            },
            "granularity": granularity,
            "natal_chart": {
                "birth_data": natal_chart.planets.get("birth_data"),
                "planets": self._simplify_planet_data(natal_planets),
                "houses": natal_chart.houses,
                "points": self._simplify_planet_data(natal_chart.points),
                "aspects": self._filter_aspects(natal_chart.aspects, 4.0)
            },
            "snapshots": snapshots,
            "snapshot_count": len(snapshots)
        }

    @staticmethod
    def _simplify_planet_data(planets: dict) -> dict:
        """
        Keep only essential planet fields for forecasting.

        Removes technical fields that don't improve LLM interpretation:
        - speed, declination (technical data)
        - element, quality, sign_num, abs_pos (redundant - inferred from sign)

        Args:
            planets: Full planet data dictionary

        Returns:
            Simplified planet data with essential fields only
        """
        essential_fields = {"name", "sign", "position", "house", "retrograde"}

        simplified = {}
        for planet_key, planet_data in planets.items():
            if isinstance(planet_data, dict):
                simplified[planet_key] = {
                    k: v for k, v in planet_data.items()
                    if k in essential_fields
                }
            else:
                # Non-dict values (like birth_data) pass through unchanged
                simplified[planet_key] = planet_data

        return simplified

    @staticmethod
    def _filter_aspects(aspects: list, max_orb: float = 4.0) -> list:
        """
        Filter aspects to major types with tight orbs only.

        For transit forecasting, major aspects with tight orbs are most significant.
        Minor aspects and wide orbs add noise without improving interpretation.

        Args:
            aspects: List of aspect dictionaries
            max_orb: Maximum orb in degrees (default 4.0)

        Returns:
            Filtered list of major aspects with tight orbs
        """
        major_aspects = {"conjunction", "opposition", "square", "trine", "sextile"}

        filtered = []
        for aspect in aspects:
            aspect_name = aspect.get("aspect", "").lower()
            orbit = abs(aspect.get("orbit", 99.0))

            if aspect_name in major_aspects and orbit < max_orb:
                filtered.append(aspect)

        return filtered

    @staticmethod
    def _determine_granularity(days: int) -> tuple[GranularityType, int]:
        """
        Determine granularity and interval dynamically to achieve ~6 snapshots.

        Strategy: Target 6 snapshots regardless of range to prevent context bloat.

        Examples:
        - 7 days → daily (7 snapshots)
        - 30 days → weekly (5 snapshots)
        - 180 days → monthly (6 snapshots)
        - 365 days → bi-monthly (6 snapshots)
        - 3650 days (10 years) → bi-yearly (5 snapshots)

        Args:
            days: Number of days in the range

        Returns:
            Tuple of (granularity_name, interval_in_days)
        """
        # Target approximately 6 snapshots
        target_snapshots = 6
        interval_days = max(1, days // target_snapshots)

        # Determine human-friendly granularity label
        if interval_days <= 1:
            return "daily", 1
        elif interval_days <= 7:
            return "weekly", 7
        elif interval_days <= 30:
            return "monthly", 30
        elif interval_days <= 90:
            return "quarterly", 90
        else:
            # For multi-year ranges: every 2 years
            return "bi-yearly", 730

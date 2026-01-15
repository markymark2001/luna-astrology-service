"""Transit period application service - calculates transits over a date range."""

from datetime import date

from app.core.llm_formatter import filter_aspects, format_transit_periods, simplify_planets
from app.domain.models import BirthData
from app.domain.ports import IAstrologyProvider


class TransitPeriodService:
    """
    Application service for generating transit data over a date range.

    Uses Kerykeion's TransitsTimeRangeFactory for precise timing of transit periods.
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
        Generate transit data for a date range with precise timing.

        Args:
            birth_data: Birth information
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            Dict containing period metadata, natal chart, and transit aspects with timing
        """
        # Parse dates
        start_dt = date.fromisoformat(start_date)
        end_dt = date.fromisoformat(end_date)

        # Validate date range
        if start_dt > end_dt:
            raise ValueError("start_date must be before or equal to end_date")

        days_diff = (end_dt - start_dt).days

        # Calculate natal chart
        natal_chart = self.provider.calculate_natal_chart(birth_data)

        # Calculate transit periods with precise timing
        transit_result = self.provider.calculate_transit_periods(
            natal_chart=natal_chart,
            start_date=start_dt,
            end_date=end_dt
        )

        # Build response with natal chart data
        natal_planets = {k: v for k, v in natal_chart.planets.items() if k != "birth_data"}

        # Convert TransitAspect objects to dicts for formatting
        aspects_data = [
            {
                "transit_planet": asp.transit_planet,
                "natal_planet": asp.natal_planet,
                "aspect_type": asp.aspect_type,
                "start_date": asp.start_date.isoformat(),
                "end_date": asp.end_date.isoformat(),
                "exact_date": asp.exact_date.isoformat(),
                "exact_orb": asp.exact_orb,
                "duration_days": (asp.end_date - asp.start_date).days + 1
            }
            for asp in transit_result.aspects
        ]

        return {
            "period": {
                "start": start_date,
                "end": end_date,
                "days": days_diff
            },
            "natal_chart": {
                "birth_data": natal_chart.planets.get("birth_data"),
                "planets": simplify_planets(natal_planets),
                "houses": natal_chart.houses,
                "points": simplify_planets(natal_chart.points),
                "aspects": filter_aspects(natal_chart.aspects)
            },
            "transit_aspects": aspects_data,
            "aspect_count": len(aspects_data)
        }

    def generate_transit_period_compact(
        self,
        birth_data: BirthData,
        start_date: str,
        end_date: str
    ) -> str:
        """
        Generate LLM-optimized compact transit period data.

        Args:
            birth_data: Birth information
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            Compact text format optimized for LLM consumption
        """
        transit_data = self.generate_transit_period(birth_data, start_date, end_date)
        return format_transit_periods(transit_data)

"""Profile application service - orchestrates natal chart and transit calculations."""

from datetime import datetime, timezone

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
            transit_date = datetime.now(timezone.utc)

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

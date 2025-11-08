"""Synastry application service - orchestrates relationship compatibility calculations."""

from app.domain.models import BirthData
from app.domain.ports import IAstrologyProvider


class SynastryService:
    """
    Application service for synastry (relationship compatibility) analysis.

    Calculates cross-chart aspects between two natal charts.
    """

    def __init__(self, provider: IAstrologyProvider):
        """
        Initialize with astrology provider.

        Args:
            provider: Astrology calculation provider (injected dependency)
        """
        self.provider = provider

    def analyze_synastry(self, person1_data: BirthData, person2_data: BirthData) -> dict:
        """
        Analyze synastry between two people.

        Args:
            person1_data: First person's birth information
            person2_data: Second person's birth information

        Returns:
            Dict containing only synastry aspects (cross-chart interactions)
        """
        # Calculate both natal charts
        chart1 = self.provider.calculate_natal_chart(person1_data)
        chart2 = self.provider.calculate_natal_chart(person2_data)

        # Calculate synastry
        synastry = self.provider.calculate_synastry(chart1, chart2)

        # Return only synastry aspects (no redundant natal chart data)
        return {
            "synastry": {
                "aspects": synastry.aspects
            }
        }

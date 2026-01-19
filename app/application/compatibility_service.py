"""Synastry application service - orchestrates relationship compatibility calculations."""

from app.core.llm_formatter import format_synastry
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
            Dict containing synastry aspects and relationship score
        """
        # Calculate both natal charts
        chart1 = self.provider.calculate_natal_chart(person1_data)
        chart2 = self.provider.calculate_natal_chart(person2_data)

        # Calculate synastry
        synastry = self.provider.calculate_synastry(chart1, chart2)

        # Build relationship score dict if available
        relationship_score = None
        if synastry.relationship_score:
            relationship_score = {
                "score_value": synastry.relationship_score.score_value,
                "is_destiny_sign": synastry.relationship_score.is_destiny_sign,
            }

        # Return synastry data with relationship score
        return {
            "synastry": {
                "aspects": synastry.aspects
            },
            "relationship_score": relationship_score,
        }

    def analyze_synastry_compact(self, person1_data: BirthData, person2_data: BirthData) -> str:
        """
        Analyze synastry with LLM-optimized compact output.

        Args:
            person1_data: First person's birth information
            person2_data: Second person's birth information

        Returns:
            Compact text format optimized for LLM consumption (~80% token reduction)
        """
        synastry_data = self.analyze_synastry(person1_data, person2_data)
        return format_synastry(synastry_data)

"""
Astrology service configuration presets.

This module defines configurable granularity levels for astrological calculations.
Different API endpoints can select different presets based on their needs
(e.g., LLM-optimized vs comprehensive data).
"""
from dataclasses import dataclass
from enum import StrEnum


class DetailLevel(StrEnum):
    """Preset detail levels for astrological calculations."""

    MINIMAL = "minimal"      # Bare minimum for quick insights
    CORE = "core"           # Optimized for LLM context (current default)
    ESSENTIAL = "essential"  # More comprehensive but still optimized
    COMPREHENSIVE = "comprehensive"  # Full detailed data


@dataclass
class AstrologyConfig:
    """Configuration for astrological calculations.

    Controls which celestial bodies, houses, and aspect orbs to include
    in natal charts, transits, and synastry calculations.
    """

    # Celestial bodies
    planets: list[str]
    points: list[str]
    houses: list[str]

    # Aspect orb tolerances (in degrees)
    natal_orb: float       # For natal chart aspects
    transit_orb: float     # For transit-to-natal aspects
    synastry_orb: float    # For synastry/relationship aspects

    # Human-readable description
    description: str


def get_preset(level: DetailLevel) -> AstrologyConfig:
    """Get configuration preset for specified detail level.

    Args:
        level: The detail level preset to load

    Returns:
        AstrologyConfig with preset values

    Example:
        >>> config = get_preset(DetailLevel.CORE)
        >>> config.planets
        ['sun', 'moon', 'mercury', ...]
    """

    if level == DetailLevel.MINIMAL:
        # Ultra-lightweight: 7 personal planets, angular houses only
        return AstrologyConfig(
            planets=[
                "sun", "moon", "mercury", "venus", "mars",
                "jupiter", "saturn"
            ],
            points=["ascendant", "medium_coeli"],
            houses=["first_house", "fourth_house", "seventh_house", "tenth_house"],
            natal_orb=3.0,
            transit_orb=3.0,
            synastry_orb=6.0,
            description="Minimal configuration: 7 personal planets, 2 points, 4 angular houses, tight orbs"
        )

    elif level == DetailLevel.CORE:
        # Current LLM-optimized configuration (existing behavior)
        return AstrologyConfig(
            planets=[
                "sun", "moon", "mercury", "venus", "mars",
                "jupiter", "saturn", "uranus", "neptune", "pluto"
            ],
            points=["ascendant", "medium_coeli"],
            houses=[
                "first_house", "second_house", "third_house", "fourth_house",
                "fifth_house", "sixth_house", "seventh_house", "eighth_house",
                "ninth_house", "tenth_house", "eleventh_house", "twelfth_house"
            ],
            natal_orb=4.0,
            transit_orb=4.0,
            synastry_orb=8.0,
            description="Core configuration: 10 planets, 2 points, 12 houses, balanced orbs (LLM-optimized)"
        )

    elif level == DetailLevel.ESSENTIAL:
        # More comprehensive: adds nodes, chiron, more houses
        return AstrologyConfig(
            planets=[
                "sun", "moon", "mercury", "venus", "mars",
                "jupiter", "saturn", "uranus", "neptune", "pluto",
                "chiron"
            ],
            points=[
                "ascendant", "medium_coeli",
                "descendant", "imum_coeli",
                "mean_node"  # North Node
            ],
            houses=[
                "first_house", "second_house", "third_house", "fourth_house",
                "fifth_house", "sixth_house", "seventh_house", "eighth_house",
                "tenth_house", "eleventh_house", "twelfth_house"
            ],
            natal_orb=6.0,
            transit_orb=6.0,
            synastry_orb=8.0,
            description="Essential configuration: 11 bodies, 5 points, 11 houses, wider orbs"
        )

    elif level == DetailLevel.COMPREHENSIVE:
        # Full detailed data: all bodies, all houses, all points, wider orbs
        return AstrologyConfig(
            planets=[
                "sun", "moon", "mercury", "venus", "mars",
                "jupiter", "saturn", "uranus", "neptune", "pluto",
                "chiron", "true_node", "mean_node"
            ],
            points=[
                "ascendant", "medium_coeli",
                "descendant", "imum_coeli",
                "mean_lilith", "true_lilith"
            ],
            houses=[
                "first_house", "second_house", "third_house", "fourth_house",
                "fifth_house", "sixth_house", "seventh_house", "eighth_house",
                "ninth_house", "tenth_house", "eleventh_house", "twelfth_house"
            ],
            natal_orb=8.0,
            transit_orb=8.0,
            synastry_orb=8.0,
            description="Comprehensive configuration: 13 bodies, 6 points, all 12 houses, wide orbs"
        )

    else:
        # Fallback to core if unknown level
        return get_preset(DetailLevel.CORE)


# Convenience: Default configuration (for backward compatibility)
DEFAULT_CONFIG = get_preset(DetailLevel.CORE)

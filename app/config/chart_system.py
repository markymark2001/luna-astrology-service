"""Canonical chart-system configuration for the astrology service."""

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Literal


class ChartSystemId(StrEnum):
    """Supported chart-system identifiers."""

    WESTERN_TROPICAL_PLACIDUS = "western_tropical_placidus"


@dataclass(frozen=True)
class ChartSystemConfig:
    """Boot-time chart-system settings applied to every astrology calculation."""

    id: ChartSystemId
    zodiac_type: Literal["Tropical", "Sidereal"]
    house_system: str
    house_system_identifier: str
    perspective_type: Literal[
        "Apparent Geocentric",
        "Heliocentric",
        "Topocentric",
        "True Geocentric",
    ]
    provider: str
    sidereal_mode: str | None = None

    def to_metadata(self) -> dict[str, str | None]:
        """Serialize chart-system settings for API responses."""
        return asdict(self)


DEFAULT_CHART_SYSTEM = ChartSystemConfig(
    id=ChartSystemId.WESTERN_TROPICAL_PLACIDUS,
    zodiac_type="Tropical",
    house_system="Placidus",
    house_system_identifier="P",
    perspective_type="Apparent Geocentric",
    provider="kerykeion",
    sidereal_mode=None,
)

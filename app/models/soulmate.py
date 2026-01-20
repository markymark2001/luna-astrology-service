"""Soulmate API request and response models."""

from typing import Any

from pydantic import BaseModel, Field

from app.domain.models.birth_data import BirthData


class SoulmateRequest(BirthData):
    """
    Request model for soulmate chart calculation.

    User's birth data - follows same pattern as ProfileRequest.
    Inherits all fields and validation from domain BirthData model.

    Optional gender fields for age range calculation:
    - user_gender: User's gender ("male", "female", "non-binary", or None)
    - soulmate_sex: Desired soulmate sex ("male", "female", "non-binary", or None)
    """

    user_gender: str | None = Field(
        default=None,
        description="User's gender for age range calculation (male, female, non-binary)",
    )
    soulmate_sex: str | None = Field(
        default=None,
        description="Desired soulmate sex for age range calculation (male, female, non-binary)",
    )


class RecalculateBirthDateRequest(BaseModel):
    """
    Request model for recalculating soulmate birth date when gender mismatch occurs.

    Used when user selects same-sex soulmate after background calculation
    predicted opposite-sex (which used different age range formula).
    """

    user_birth_year: int = Field(
        ...,
        description="User's birth year for calculating their age",
    )
    user_gender: str | None = Field(
        default=None,
        description="User's gender (male, female, non-binary)",
    )
    soulmate_sex: str | None = Field(
        default=None,
        description="Desired soulmate sex (male, female, non-binary)",
    )


class RecalculateBirthDateResponse(BaseModel):
    """
    Response model for recalculated soulmate birth date.

    Contains only the new birth year since that's what changes based on age range.
    """

    birth_year: int = Field(
        ...,
        description="New soulmate birth year based on corrected age range",
    )
    min_age: int = Field(
        ...,
        description="Minimum soulmate age used for calculation",
    )
    max_age: int = Field(
        ...,
        description="Maximum soulmate age used for calculation",
    )


class SoulmateChartResponse(BaseModel):
    """
    Structured soulmate chart data.

    Returns JSON (not PlainText) because backend tool needs to extract
    specific placements for feature/personality mapping.

    Same structure as NatalChart domain model but as API response.
    Includes user's placements for physical feature derivation.
    """

    planets: dict[str, Any] = Field(
        ...,
        description="Planet positions: {sun: {name, sign, position, house, retrograde}, ...}",
    )
    houses: dict[str, Any] = Field(
        ...,
        description="House cusps: {first_house: {sign}, ...}",
    )
    points: dict[str, Any] = Field(
        ...,
        description="Chart points: {ascendant: {name, sign, position}, midheaven: {...}}",
    )
    aspects: list[dict[str, Any]] = Field(
        ...,
        description="Natal aspects: [{p1_name, p2_name, aspect, orbit}, ...]",
    )
    compatibility_percent: int = Field(
        ...,
        description="Compatibility percentage (75-99) based on comprehensive 18-point scoring",
    )
    # User's placements for physical feature derivation (what user is attracted to)
    user_venus_sign: str = Field(
        ...,
        description="User's Venus sign - determines what user finds beautiful",
    )
    user_mars_sign: str = Field(
        ...,
        description="User's Mars sign - determines what physically excites user",
    )
    user_rising_sign: str = Field(
        ...,
        description="User's Rising sign - opposite is user's Descendant (partner archetype)",
    )
    soulmate_birth_year: int = Field(
        ...,
        description="Soulmate's birth year for age calculation",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "planets": {
                    "sun": {
                        "name": "Sun",
                        "sign": "Sagittarius",
                        "position": 15.5,
                        "house": 7,
                        "retrograde": False,
                    },
                    "moon": {
                        "name": "Moon",
                        "sign": "Leo",
                        "position": 22.3,
                        "house": 5,
                        "retrograde": False,
                    },
                },
                "houses": {
                    "first_house": {"sign": "Libra"},
                    "seventh_house": {"sign": "Aries"},
                },
                "points": {
                    "ascendant": {"name": "Ascendant", "sign": "Libra", "position": 10.2},
                    "midheaven": {"name": "Midheaven", "sign": "Cancer", "position": 5.8},
                },
                "aspects": [
                    {
                        "p1_name": "Sun",
                        "p2_name": "Moon",
                        "aspect": "trine",
                        "orbit": 2.5,
                    }
                ],
                "compatibility_percent": 92,
                "user_venus_sign": "Tau",
                "user_mars_sign": "Ari",
                "user_rising_sign": "Vir",
                "soulmate_birth_year": 1998,
            }
        }

"""Birth data domain model."""


from pydantic import BaseModel, ConfigDict, Field, field_validator


class BirthData(BaseModel):
    """
    Birth data value object - single source of truth for birth information.

    This model is used across all astrology calculations to ensure
    consistent validation and defaults.
    """

    year: int = Field(..., ge=1900, le=2100, description="Birth year")
    month: int = Field(..., ge=1, le=12, description="Birth month (1-12)")
    day: int = Field(..., ge=1, le=31, description="Birth day (1-31)")
    hour: int | None = Field(12, ge=0, le=23, description="Birth hour (0-23, defaults to 12/noon)")
    minute: int | None = Field(0, ge=0, le=59, description="Birth minute (0-59, defaults to 0)")
    latitude: float | None = Field(51.5074, ge=-90, le=90, description="Birth latitude (defaults to London: 51.5074)")
    longitude: float | None = Field(-0.1278, ge=-180, le=180, description="Birth longitude (defaults to London: -0.1278)")
    timezone: str | None = Field("Europe/London", description="IANA timezone (defaults to Europe/London)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "year": 1990,
                "month": 3,
                "day": 15,
                "hour": 14,
                "minute": 30,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "America/New_York"
            }
        }
    )

    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v: str | None) -> str:
        """Validate timezone format."""
        # Use default if None or empty
        if not v:
            return "Europe/London"
        if '/' not in v:
            raise ValueError("Timezone must be in IANA format (e.g., 'America/New_York')")
        return v

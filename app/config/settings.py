from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

VALID_ENVIRONMENTS = frozenset({"dev", "test", "prod"})


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "Luna Astrology Service"
    app_version: str = "1.0.0"
    env: str = ""
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8001
    compute_pool_size: int = Field(
        1,
        validation_alias="ASTROLOGY_COMPUTE_POOL_SIZE",
        ge=1,
    )

    # Sentry
    sentry_dsn: str = ""
    internal_service_token: str = Field(
        "",
        validation_alias="ASTROLOGY_SERVICE_TOKEN",
    )

    @model_validator(mode="after")
    def validate_environment_name(self) -> "Settings":
        """Fail closed when ENV is missing or misspelled."""
        if self.env not in VALID_ENVIRONMENTS:
            allowed = ", ".join(sorted(VALID_ENVIRONMENTS))
            raise ValueError(f"ENV must be one of: {allowed}")
        return self

    @model_validator(mode="after")
    def validate_internal_service_auth(self) -> "Settings":
        """Require internal service auth in every environment."""
        if not self.internal_service_token:
            raise ValueError(
                "Missing required environment variables: "
                "ASTROLOGY_SERVICE_TOKEN"
            )
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
        populate_by_name=True,
    )


# Global settings instance
settings = Settings()

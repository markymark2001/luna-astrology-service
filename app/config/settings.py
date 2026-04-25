from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "Luna Astrology Service"
    app_version: str = "1.0.0"
    env: str = "dev"
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

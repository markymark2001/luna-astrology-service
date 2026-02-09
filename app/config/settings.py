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

    # Sentry
    sentry_dsn: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )


# Global settings instance
settings = Settings()

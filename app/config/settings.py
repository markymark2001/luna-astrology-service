import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.constants import ASTROLOGY_COMPUTE_POOL_SIZE_CAP


def _default_compute_pool_size() -> int:
    """Size the compute pool from available CPUs unless the env overrides it."""
    available_cpu_count = os.cpu_count() or 1
    return max(1, min(available_cpu_count, ASTROLOGY_COMPUTE_POOL_SIZE_CAP))


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
        default_factory=_default_compute_pool_size,
        alias="ASTROLOGY_COMPUTE_POOL_SIZE",
        ge=1,
    )

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

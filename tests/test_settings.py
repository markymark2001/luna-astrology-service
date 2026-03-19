"""Tests for astrology service environment-backed settings."""

from app.config.constants import ASTROLOGY_COMPUTE_POOL_SIZE_CAP
from app.config.settings import Settings


def test_compute_pool_size_defaults_to_available_cpu_count(
    monkeypatch,
) -> None:
    monkeypatch.delenv("ASTROLOGY_COMPUTE_POOL_SIZE", raising=False)
    monkeypatch.setattr("app.config.settings.os.cpu_count", lambda: 6)

    settings = Settings()

    assert settings.compute_pool_size == 6


def test_compute_pool_size_default_is_capped_for_large_hosts(
    monkeypatch,
) -> None:
    monkeypatch.delenv("ASTROLOGY_COMPUTE_POOL_SIZE", raising=False)
    monkeypatch.setattr("app.config.settings.os.cpu_count", lambda: 64)

    settings = Settings()

    assert settings.compute_pool_size == ASTROLOGY_COMPUTE_POOL_SIZE_CAP


def test_compute_pool_size_respects_explicit_env_override(
    monkeypatch,
) -> None:
    monkeypatch.setenv("ASTROLOGY_COMPUTE_POOL_SIZE", "3")
    monkeypatch.setattr("app.config.settings.os.cpu_count", lambda: 8)

    settings = Settings()

    assert settings.compute_pool_size == 3

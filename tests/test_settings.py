"""Tests for astrology service environment-backed settings."""

from app.config.settings import Settings


def test_compute_pool_size_defaults_to_one(
    monkeypatch,
) -> None:
    monkeypatch.delenv("ASTROLOGY_COMPUTE_POOL_SIZE", raising=False)

    settings = Settings()

    assert settings.compute_pool_size == 1


def test_compute_pool_size_respects_explicit_env_override(
    monkeypatch,
) -> None:
    monkeypatch.setenv("ASTROLOGY_COMPUTE_POOL_SIZE", "3")

    settings = Settings()

    assert settings.compute_pool_size == 3

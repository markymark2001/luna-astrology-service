"""Tests for astrology service environment-backed settings."""

import pytest

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


def test_shared_astrology_service_token_env_populates_internal_service_token(
    monkeypatch,
) -> None:
    monkeypatch.setenv("ASTROLOGY_SERVICE_TOKEN", "shared-secret")

    settings = Settings()

    assert settings.internal_service_token == "shared-secret"


def test_prod_requires_internal_service_token(
    monkeypatch,
) -> None:
    with pytest.raises(ValueError, match="ASTROLOGY_SERVICE_TOKEN"):
        Settings(env="prod", internal_service_token="")

"""Tests for astrology Sentry release derivation."""

from app.config.sentry_release import get_sentry_release


def test_prefers_explicit_sentry_release(monkeypatch) -> None:
    monkeypatch.setenv("SENTRY_RELEASE", "staia-astrology@manual")
    monkeypatch.setenv("RAILWAY_GIT_COMMIT_SHA", "abcdef123456")

    assert get_sentry_release("staia-astrology") == "staia-astrology@manual"


def test_derives_release_from_railway_commit_sha(monkeypatch) -> None:
    monkeypatch.delenv("SENTRY_RELEASE", raising=False)
    monkeypatch.setenv("RAILWAY_GIT_COMMIT_SHA", "abcdef123456")

    assert get_sentry_release("staia-astrology") == "staia-astrology@abcdef1"


def test_returns_none_without_release_inputs(monkeypatch) -> None:
    monkeypatch.delenv("SENTRY_RELEASE", raising=False)
    monkeypatch.delenv("RAILWAY_GIT_COMMIT_SHA", raising=False)

    assert get_sentry_release("staia-astrology") is None

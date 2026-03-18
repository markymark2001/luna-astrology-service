"""Helpers for deriving Sentry release identifiers from runtime environment."""

from __future__ import annotations

import os


def get_sentry_release(prefix: str) -> str | None:
    """Return explicit Sentry release or derive one from Railway commit SHA."""
    if explicit_release := os.getenv("SENTRY_RELEASE"):
        return explicit_release

    if commit_sha := os.getenv("RAILWAY_GIT_COMMIT_SHA"):
        return f"{prefix}@{commit_sha[:7]}"

    return None

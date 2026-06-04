"""Tests for astrology-service Sentry init."""

from unittest.mock import patch

from sentry_sdk.integrations.logging import LoggingIntegration

from app.main import init_astrology_sentry


def test_init_astrology_sentry_disables_log_event_promotion():
    with patch("app.main.sentry_sdk.init") as mock_init:
        init_astrology_sentry(
            dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
            environment="prod-astrology",
            release="staia-astrology@1.2.3",
        )

    integrations = mock_init.call_args.kwargs["integrations"]
    logging_integration = next(
        integration
        for integration in integrations
        if isinstance(integration, LoggingIntegration)
    )
    assert logging_integration._handler is None

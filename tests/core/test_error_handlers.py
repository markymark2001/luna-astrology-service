"""Tests for astrology service error handlers capturing to Sentry."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import status

from app.core.error_handlers import (
    handle_astrology_service_error,
    handle_chart_calculation_error,
    handle_generic_exception,
    handle_invalid_birth_data,
)
from app.core.exceptions import (
    AstrologyServiceException,
    ChartCalculationException,
    InvalidBirthDataException,
)


class TestChartCalculationErrorCapturesSentry:
    """500 chart calculation errors should be reported to Sentry."""

    @pytest.mark.asyncio
    async def test_captures_sentry(self):
        """handle_chart_calculation_error calls sentry_sdk.capture_exception."""
        exc = ChartCalculationException("calc failed")
        request = MagicMock()

        with patch("app.core.error_handlers.sentry_sdk") as mock_sentry:
            response = await handle_chart_calculation_error(request, exc)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        mock_sentry.capture_exception.assert_called_once_with(exc)


class TestGenericExceptionCapturesSentry:
    """500 generic exceptions should be reported to Sentry."""

    @pytest.mark.asyncio
    async def test_captures_sentry(self):
        """handle_generic_exception calls sentry_sdk.capture_exception."""
        exc = RuntimeError("unexpected")
        request = MagicMock()

        with patch("app.core.error_handlers.sentry_sdk") as mock_sentry:
            response = await handle_generic_exception(request, exc)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        mock_sentry.capture_exception.assert_called_once_with(exc)


class TestAstrologyServiceErrorCapturesSentry:
    """AstrologyServiceException with 500 status should be reported to Sentry."""

    @pytest.mark.asyncio
    async def test_captures_sentry_on_500(self):
        """handle_astrology_service_error calls sentry_sdk.capture_exception for 500."""
        exc = AstrologyServiceException("server error", status_code=500)
        request = MagicMock()

        with patch("app.core.error_handlers.sentry_sdk") as mock_sentry:
            response = await handle_astrology_service_error(request, exc)

        assert response.status_code == 500
        mock_sentry.capture_exception.assert_called_once_with(exc)


class TestInvalidBirthDataSkipsSentry:
    """400 client errors should NOT be reported to Sentry."""

    @pytest.mark.asyncio
    async def test_does_not_capture_sentry(self):
        """handle_invalid_birth_data does NOT call sentry_sdk.capture_exception."""
        exc = InvalidBirthDataException("bad data")
        request = MagicMock()

        with patch("app.core.error_handlers.sentry_sdk") as mock_sentry:
            response = await handle_invalid_birth_data(request, exc)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mock_sentry.capture_exception.assert_not_called()

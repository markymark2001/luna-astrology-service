"""FastAPI exception handlers for simple error responses."""

import json

from fastapi import Request, status
from fastapi.responses import PlainTextResponse

from app.core.exceptions import (
    AstrologyServiceException,
    ChartCalculationException,
    InvalidBirthDataException,
)


async def handle_invalid_birth_data(
    request: Request,
    exc: Exception
) -> PlainTextResponse:
    """Handle invalid birth data exceptions."""
    assert isinstance(exc, InvalidBirthDataException)
    return PlainTextResponse(
        content=json.dumps({"error": exc.code, "message": exc.message}),
        status_code=status.HTTP_400_BAD_REQUEST,
        media_type="text/plain"
    )


async def handle_chart_calculation_error(
    request: Request,
    exc: Exception
) -> PlainTextResponse:
    """Handle chart calculation exceptions."""
    assert isinstance(exc, ChartCalculationException)
    return PlainTextResponse(
        content=json.dumps({"error": exc.code, "message": exc.message}),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        media_type="text/plain"
    )


async def handle_astrology_service_error(
    request: Request,
    exc: Exception
) -> PlainTextResponse:
    """Handle generic astrology service exceptions."""
    assert isinstance(exc, AstrologyServiceException)
    return PlainTextResponse(
        content=json.dumps({"error": exc.code, "message": exc.message}),
        status_code=exc.status_code,
        media_type="text/plain"
    )


async def handle_generic_exception(
    request: Request,
    exc: Exception
) -> PlainTextResponse:
    """Handle unexpected exceptions."""
    return PlainTextResponse(
        content=json.dumps({
            "error": "INTERNAL_SERVER_ERROR",
            "message": f"An unexpected error occurred: {str(exc)}"
        }),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        media_type="text/plain"
    )

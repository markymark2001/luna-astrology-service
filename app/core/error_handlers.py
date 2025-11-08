"""FastAPI exception handlers for standardized error responses."""

from fastapi import Request, status
from fastapi.responses import PlainTextResponse

from app.core.exceptions import (
    AstrologyServiceException,
    ChartCalculationException,
    InvalidBirthDataException,
)
from app.core.response_builder import error_response


async def handle_invalid_birth_data(
    request: Request,
    exc: InvalidBirthDataException
) -> PlainTextResponse:
    """Handle invalid birth data exceptions."""
    return PlainTextResponse(
        content=error_response(code=exc.code, message=exc.message),
        status_code=status.HTTP_400_BAD_REQUEST,
        media_type="text/plain"
    )


async def handle_chart_calculation_error(
    request: Request,
    exc: ChartCalculationException
) -> PlainTextResponse:
    """Handle chart calculation exceptions."""
    return PlainTextResponse(
        content=error_response(code=exc.code, message=exc.message),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        media_type="text/plain"
    )


async def handle_astrology_service_error(
    request: Request,
    exc: AstrologyServiceException
) -> PlainTextResponse:
    """Handle generic astrology service exceptions."""
    return PlainTextResponse(
        content=error_response(code=exc.code, message=exc.message),
        status_code=exc.status_code,
        media_type="text/plain"
    )


async def handle_generic_exception(
    request: Request,
    exc: Exception
) -> PlainTextResponse:
    """Handle unexpected exceptions."""
    return PlainTextResponse(
        content=error_response(
            code="INTERNAL_SERVER_ERROR",
            message=f"An unexpected error occurred: {str(exc)}"
        ),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        media_type="text/plain"
    )

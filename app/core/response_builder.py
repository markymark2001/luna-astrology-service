"""Response builder utilities for standardized API responses."""

from datetime import UTC, datetime
from typing import Any

from app.models.responses import ErrorDetail, StandardResponse


def success_response(data: dict[str, Any]) -> str:
    """
    Build a standardized success response as a JSON string.

    Args:
        data: The response data payload

    Returns:
        JSON string with standardized success response
    """
    response = StandardResponse(
        status="success",
        timestamp=datetime.now(UTC).isoformat(),
        data=data,
        error=None,
    )
    return response.model_dump_json()


def error_response(code: str, message: str) -> str:
    """
    Build a standardized error response as a JSON string.

    Args:
        code: Error code for client-side handling
        message: Human-readable error message

    Returns:
        JSON string with standardized error response
    """
    response = StandardResponse(
        status="error",
        timestamp=datetime.now(UTC).isoformat(),
        data=None,
        error=ErrorDetail(code=code, message=message),
    )
    return response.model_dump_json()

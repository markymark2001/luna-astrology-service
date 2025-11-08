"""Response builder utilities for standardized API responses."""

import json
from datetime import datetime, timezone
from typing import Any

from app.models.responses import StandardResponse, ErrorDetail


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
        timestamp=datetime.now(timezone.utc).isoformat(),
        data=data,
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
        timestamp=datetime.now(timezone.utc).isoformat(),
        error=ErrorDetail(code=code, message=message),
    )
    return response.model_dump_json()

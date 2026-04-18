"""Internal request authentication for astrology-service routes."""

from __future__ import annotations

import hmac

from fastapi import Header, HTTPException, Request, status

INTERNAL_SERVICE_TOKEN_HEADER = "X-Astrology-Service-Token"


async def verify_internal_service_token(
    request: Request,
    internal_service_token: str | None = Header(
        default=None,
        alias=INTERNAL_SERVICE_TOKEN_HEADER,
    ),
) -> None:
    """Require the configured backend-to-service token when one is set."""
    expected_token = getattr(request.app.state.settings, "internal_service_token", "")
    if not expected_token:
        return

    if not internal_service_token or not hmac.compare_digest(
        internal_service_token,
        expected_token,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized internal caller",
        )

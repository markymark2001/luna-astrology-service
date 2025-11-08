"""Standardized API response models."""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error detail structure."""

    code: str = Field(..., description="Error code for client-side handling")
    message: str = Field(..., description="Human-readable error message")


class StandardResponse(BaseModel):
    """Standard API response envelope."""

    status: Literal["success", "error"] = Field(..., description="Response status")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    data: Optional[dict] = Field(None, description="Response data (success only)")
    error: Optional[ErrorDetail] = Field(None, description="Error details (error only)")

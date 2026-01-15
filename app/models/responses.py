"""Standardized API response models."""

from typing import Literal

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error detail structure."""

    code: str = Field(..., description="Error code for client-side handling")
    message: str = Field(..., description="Human-readable error message")


class StandardResponse(BaseModel):
    """Standard API response envelope."""

    status: Literal["success", "error"] = Field(..., description="Response status")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    data: dict | None = Field(None, description="Response data (success only)")
    error: ErrorDetail | None = Field(None, description="Error details (error only)")


class PlanetHouseResponse(BaseModel):
    """Response model for planet house position."""

    planet: str = Field(..., description="Planet name")
    house: int = Field(..., description="House number (1-12)")
    sign: str = Field(..., description="Zodiac sign the planet is in")

"""FastAPI application with hexagonal architecture and dependency injection.

This service is licensed under AGPL 3.0 due to the use of Kerykeion library.
Public repository: https://github.com/markymark2001/luna-astrology-service

The service is automatically synced from the private Luna repository.
"""

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.config.astrology_presets import get_preset, DetailLevel
from app.api.v1 import api_router
from app.infrastructure.providers.kerykeion_provider import KerykeionProvider
from app.application.profile_service import ProfileService
from app.application.compatibility_service import SynastryService
from app.core.exceptions import (
    AstrologyServiceException,
    ChartCalculationException,
    InvalidBirthDataException,
)
from app.core.error_handlers import (
    handle_astrology_service_error,
    handle_chart_calculation_error,
    handle_generic_exception,
    handle_invalid_birth_data,
)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Astrology calculation service with hexagonal architecture (Internal Service)",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Note: CORS middleware not needed for internal-only service
# This service only receives server-to-server requests from the backend,
# not direct browser requests, so CORS doesn't apply


# Initialize provider and services (singleton pattern)
config = get_preset(DetailLevel.CORE)
provider = KerykeionProvider(config=config)
profile_service_instance = ProfileService(provider=provider)
synastry_service_instance = SynastryService(provider=provider)


# Override dependency injection using FastAPI's built-in system
from app.api.v1 import profile, compatibility

app.dependency_overrides[profile.get_profile_service] = lambda: profile_service_instance
app.dependency_overrides[compatibility.get_synastry_service] = lambda: synastry_service_instance


# Register exception handlers
app.add_exception_handler(InvalidBirthDataException, handle_invalid_birth_data)
app.add_exception_handler(ChartCalculationException, handle_chart_calculation_error)
app.add_exception_handler(AstrologyServiceException, handle_astrology_service_error)
app.add_exception_handler(Exception, handle_generic_exception)


# Health check endpoint
@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Health check",
    description="Check if the service is running"
)
async def health_check():
    """Health check endpoint for Railway and monitoring."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.env
        }
    )


# Root endpoint
@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    tags=["Root"],
    summary="API root",
    description="Get API information"
)
async def root():
    """Root endpoint with API information."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "api": "/api/v1"
    }


# Include API router
app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

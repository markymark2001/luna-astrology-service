"""Shared bounded thread-pool execution for astrology tasks."""

from __future__ import annotations

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from time import monotonic
from typing import Any

import sentry_sdk
from fastapi import Request

from app.application.chart_payloads import natal_chart_payload
from app.application.compatibility_service import SynastryService
from app.application.profile_service import ProfileService
from app.application.soulmate_service import SoulmateService
from app.application.transit_period_service import TransitPeriodService
from app.config.astrology_presets import DetailLevel, get_preset
from app.config.chart_system import DEFAULT_CHART_SYSTEM
from app.config.constants import (
    ASTROLOGY_COMPUTE_QUEUE_WARNING_MS,
    ASTROLOGY_COMPUTE_TOTAL_WARNING_MS,
    ASTROLOGY_COMPUTE_WARNING_COOLDOWN_SECONDS,
)
from app.config.settings import Settings, settings
from app.core.exceptions import ChartCalculationException, InvalidBirthDataException
from app.domain.models.birth_data import BirthData
from app.infrastructure.providers.kerykeion_provider import KerykeionProvider
from app.models.requests import PlanetHouseRequest, ProfileRequest, SynastryRequest, TransitPeriodRequest
from app.models.soulmate import SoulmateRequest

logger = logging.getLogger(__name__)

# Kerykeion house name to number mapping
HOUSE_NAME_TO_NUMBER = {
    "First_House": 1,
    "Second_House": 2,
    "Third_House": 3,
    "Fourth_House": 4,
    "Fifth_House": 5,
    "Sixth_House": 6,
    "Seventh_House": 7,
    "Eighth_House": 8,
    "Ninth_House": 9,
    "Tenth_House": 10,
    "Eleventh_House": 11,
    "Twelfth_House": 12,
}

_WORKER_SERVICES: dict[str, Any] | None = None


def _get_worker_services() -> dict[str, Any]:
    """Lazily initialize astrology services once per executor worker thread."""
    global _WORKER_SERVICES
    if _WORKER_SERVICES is None:
        provider = KerykeionProvider(
            config=get_preset(DetailLevel.CORE),
            chart_system=DEFAULT_CHART_SYSTEM,
        )
        _WORKER_SERVICES = {
            "profile": ProfileService(provider=provider),
            "synastry": SynastryService(provider=provider),
            "soulmate": SoulmateService(provider=provider),
            "transit_period": TransitPeriodService(provider=provider),
        }
    return _WORKER_SERVICES


def _serialize_natal_chart_for_style(birth_data: BirthData) -> dict[str, Any]:
    """Return natal chart payload for style generation without transit work."""
    profile_service: ProfileService = _get_worker_services()["profile"]
    natal_chart = profile_service.provider.calculate_natal_chart(birth_data)
    natal_payload = natal_chart_payload(natal_chart)
    planets = {k: v for k, v in natal_payload["planets"].items() if k != "birth_data"}
    return {
        "planets": planets,
        "points": natal_payload["points"],
        "chart_system": natal_chart.chart_system,
    }


def _serialize_planet_house(payload: dict[str, Any]) -> dict[str, Any]:
    """Return planet house data using natal chart only."""
    request = PlanetHouseRequest.model_validate(payload)
    profile_service: ProfileService = _get_worker_services()["profile"]
    natal_chart = profile_service.provider.calculate_natal_chart(request)
    natal_payload = natal_chart_payload(natal_chart)
    planets = natal_payload["planets"]
    planet_name = request.planet.lower()
    planet_data = planets.get(planet_name)
    if not planet_data:
        raise ValueError(
            f"Planet '{request.planet}' not found in natal chart. Available planets: {list(planets.keys())}"
        )

    house = planet_data.get("house")
    sign = planet_data.get("sign")
    if house is None:
        raise RuntimeError(f"House position not available for planet '{request.planet}'")
    if sign is None:
        raise RuntimeError(f"Sign not available for planet '{request.planet}'")

    house_int = None
    if isinstance(house, int):
        house_int = house
    elif isinstance(house, str):
        house_int = HOUSE_NAME_TO_NUMBER.get(house)
        if house_int is None:
            try:
                house_int = int(house)
            except ValueError:
                house_int = None

    if house_int is None or not 1 <= house_int <= 12:
        raise RuntimeError(
            f"Invalid house value '{house}' - could not convert to house number (1-12)"
        )

    return {
        "planet": planet_name,
        "house": house_int,
        "sign": sign,
        "chart_system": natal_chart.chart_system,
    }


def _run_compute_task(task_name: str, payload: dict[str, Any], enqueued_at: float) -> dict[str, Any]:
    """Execute a serializable astrology task inside the shared worker pool."""
    started_at = time.time()
    try:
        services = _get_worker_services()
        if task_name == "profile_compact":
            request = ProfileRequest.model_validate(payload)
            result = services["profile"].generate_profile_compact(request, request.transit_date)
        elif task_name == "lookup_profile_compact":
            request = ProfileRequest.model_validate(payload)
            result = services["profile"].generate_personal_profile_compact(
                request,
                request.transit_date,
            )
        elif task_name == "monthly_profile_compact":
            request = ProfileRequest.model_validate(payload)
            result = services["profile"].generate_monthly_profile_compact(request)
        elif task_name == "placements":
            request = ProfileRequest.model_validate(payload)
            result = services["profile"].generate_placements(request).model_dump(mode="json")
        elif task_name == "synastry_compact":
            request = SynastryRequest.model_validate(payload)
            result = services["synastry"].analyze_synastry_compact(
                request.person1,
                request.person2,
            )
        elif task_name == "soulmate_chart":
            request = SoulmateRequest.model_validate(payload)
            result = services["soulmate"].generate_soulmate_chart(
                user_birth_data=request,
                user_gender=request.user_gender,
                soulmate_sex=request.soulmate_sex,
            ).model_dump(mode="json")
        elif task_name == "transit_period_compact":
            request = TransitPeriodRequest.model_validate(payload)
            result = services["transit_period"].generate_transit_period_compact(
                request,
                request.start_date,
                request.end_date,
            )
        elif task_name == "planet_house":
            result = _serialize_planet_house(payload)
        elif task_name == "style_chart":
            request = BirthData.model_validate(payload)
            result = _serialize_natal_chart_for_style(request)
        else:
            raise ValueError(f"Unknown astrology compute task: {task_name}")

        finished_at = time.time()
        return {
            "ok": True,
            "result": result,
            "queue_wait_ms": (started_at - enqueued_at) * 1000,
            "execution_ms": (finished_at - started_at) * 1000,
        }
    except Exception as exc:
        finished_at = time.time()
        return {
            "ok": False,
            "exception_type": exc.__class__.__name__,
            "message": str(exc),
            "queue_wait_ms": (started_at - enqueued_at) * 1000,
            "execution_ms": (finished_at - started_at) * 1000,
        }


class AstrologyComputeRuntime:
    """Shared bounded thread-pool runtime for astrology work."""

    def __init__(self, max_workers: int) -> None:
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._last_warning_ts: dict[tuple[str, str], float] = {}

    async def run(self, task_name: str, payload: dict[str, Any], route_name: str) -> Any:
        """Execute a task and log queue, execution, and total duration."""
        enqueued_at = time.time()
        total_started = time.perf_counter()
        try:
            loop = asyncio.get_running_loop()
            envelope = await loop.run_in_executor(
                self._executor,
                _run_compute_task,
                task_name,
                payload,
                enqueued_at,
            )
        except Exception:
            total_ms = (time.perf_counter() - total_started) * 1000
            logger.exception(
                "Astrology compute task crashed route=%s task=%s total_ms=%.1f success=false",
                route_name,
                task_name,
                total_ms,
            )
            raise

        total_ms = (time.perf_counter() - total_started) * 1000
        if envelope["ok"]:
            logger.info(
                "Astrology compute task completed route=%s task=%s queue_wait_ms=%.1f execution_ms=%.1f total_ms=%.1f success=true",
                route_name,
                task_name,
                envelope["queue_wait_ms"],
                envelope["execution_ms"],
                total_ms,
            )
            self._report_queue_pressure(
                route_name=route_name,
                task_name=task_name,
                queue_wait_ms=envelope["queue_wait_ms"],
                execution_ms=envelope["execution_ms"],
                total_ms=total_ms,
            )
            self._report_slow_task(
                route_name=route_name,
                task_name=task_name,
                queue_wait_ms=envelope["queue_wait_ms"],
                execution_ms=envelope["execution_ms"],
                total_ms=total_ms,
            )
            return envelope["result"]

        logger.warning(
                "Astrology compute task failed route=%s task=%s queue_wait_ms=%.1f execution_ms=%.1f total_ms=%.1f success=false error_type=%s",
                route_name,
                task_name,
            envelope["queue_wait_ms"],
            envelope["execution_ms"],
            total_ms,
            envelope["exception_type"],
        )
        raise _restore_exception(envelope["exception_type"], envelope["message"])

    def _report_queue_pressure(
        self,
        *,
        route_name: str,
        task_name: str,
        queue_wait_ms: float,
        execution_ms: float,
        total_ms: float,
    ) -> None:
        if queue_wait_ms < ASTROLOGY_COMPUTE_QUEUE_WARNING_MS:
            return
        if not self._warning_allowed("queue_pressure", task_name):
            return

        message = (
            "Astrology compute queue pressure detected "
            f"(task={task_name}, route={route_name}, queue_wait_ms={queue_wait_ms:.1f})"
        )
        self._capture_warning(
            message=message,
            error_type="astrology_compute_queue_pressure",
            route_name=route_name,
            task_name=task_name,
            queue_wait_ms=queue_wait_ms,
            execution_ms=execution_ms,
            total_ms=total_ms,
        )

    def _report_slow_task(
        self,
        *,
        route_name: str,
        task_name: str,
        queue_wait_ms: float,
        execution_ms: float,
        total_ms: float,
    ) -> None:
        if total_ms < ASTROLOGY_COMPUTE_TOTAL_WARNING_MS:
            return
        if not self._warning_allowed("slow_task", task_name):
            return

        message = (
            "Astrology compute slow task detected "
            f"(task={task_name}, route={route_name}, total_ms={total_ms:.1f})"
        )
        self._capture_warning(
            message=message,
            error_type="astrology_compute_slow_task",
            route_name=route_name,
            task_name=task_name,
            queue_wait_ms=queue_wait_ms,
            execution_ms=execution_ms,
            total_ms=total_ms,
        )

    def _warning_allowed(self, warning_type: str, task_name: str) -> bool:
        key = (warning_type, task_name)
        now = monotonic()
        last_sent = self._last_warning_ts.get(key, 0.0)
        if now - last_sent < ASTROLOGY_COMPUTE_WARNING_COOLDOWN_SECONDS:
            return False
        self._last_warning_ts[key] = now
        return True

    def _capture_warning(
        self,
        *,
        message: str,
        error_type: str,
        route_name: str,
        task_name: str,
        queue_wait_ms: float,
        execution_ms: float,
        total_ms: float,
    ) -> None:
        try:
            with sentry_sdk.push_scope() as scope:
                scope.set_tag("error_type", error_type)
                scope.set_tag("service_role", "astrology-service")
                scope.set_tag("astrology_task", task_name)
                scope.set_context(
                    "astrology_compute_runtime",
                    {
                        "route": route_name,
                        "task": task_name,
                        "queue_wait_ms": queue_wait_ms,
                        "execution_ms": execution_ms,
                        "total_ms": total_ms,
                        "compute_pool_size": self.max_workers,
                    },
                )
                sentry_sdk.capture_message(message, level="warning")
        except Exception as error:
            logger.debug("Failed to report astrology compute warning to Sentry: %s", error)

    def shutdown(self) -> None:
        """Shut down the shared worker pool."""
        self._executor.shutdown(wait=True)


def _restore_exception(exception_type: str, message: str) -> Exception:
    """Reconstruct common astrology exceptions in the main process."""
    if exception_type == "InvalidBirthDataException":
        return InvalidBirthDataException(message)
    if exception_type == "ChartCalculationException":
        return ChartCalculationException(message)
    if exception_type == "ValueError":
        return ValueError(message)
    return RuntimeError(message)


def create_compute_runtime(settings: Settings) -> AstrologyComputeRuntime:
    """Create the shared compute runtime from settings."""
    logger.info(
        "Initializing astrology compute runtime with %s worker thread(s)",
        settings.compute_pool_size,
    )
    return AstrologyComputeRuntime(max_workers=settings.compute_pool_size)


def get_compute_runtime(request: Request) -> AstrologyComputeRuntime:
    """Get shared astrology compute runtime from FastAPI app state."""
    runtime = getattr(request.app.state, "astrology_compute_runtime", None)
    if runtime is None:
        runtime = create_compute_runtime(settings)
        request.app.state.astrology_compute_runtime = runtime
    return runtime

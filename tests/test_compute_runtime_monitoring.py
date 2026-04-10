"""Monitoring tests for astrology compute runtime warnings."""

from __future__ import annotations

from types import SimpleNamespace

from app.infrastructure.compute_runtime import AstrologyComputeRuntime


def _patch_process_pool(monkeypatch) -> dict[str, object]:
    created: dict[str, object] = {}

    def fake_get_context(method: str):
        created["method"] = method
        return SimpleNamespace(name=method)

    class FakeProcessPoolExecutor:
        def __init__(self, *, max_workers: int, mp_context) -> None:
            created["max_workers"] = max_workers
            created["mp_context"] = mp_context

        def shutdown(self, wait: bool = True) -> None:
            created["shutdown_wait"] = wait

    monkeypatch.setattr("app.infrastructure.compute_runtime.multiprocessing.get_context", fake_get_context)
    monkeypatch.setattr("app.infrastructure.compute_runtime.ProcessPoolExecutor", FakeProcessPoolExecutor)
    return created


def test_runtime_uses_spawned_process_pool(monkeypatch) -> None:
    created = _patch_process_pool(monkeypatch)

    runtime = AstrologyComputeRuntime(max_workers=3)
    runtime.shutdown()

    assert created["method"] == "spawn"
    assert created["max_workers"] == 3
    assert created["mp_context"] == SimpleNamespace(name="spawn")
    assert created["shutdown_wait"] is True


def test_queue_pressure_warning_captures_sentry_message(monkeypatch) -> None:
    messages: list[tuple[str, str]] = []
    _patch_process_pool(monkeypatch)

    class _Scope:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def set_tag(self, key, value):
            return None

        def set_context(self, key, value):
            return None

    monkeypatch.setattr("app.infrastructure.compute_runtime.sentry_sdk.new_scope", _Scope)
    monkeypatch.setattr(
        "app.infrastructure.compute_runtime.sentry_sdk.capture_message",
        lambda message, level="info": messages.append((message, level)),
    )

    runtime = AstrologyComputeRuntime(max_workers=2)
    runtime._report_queue_pressure(
        route_name="/api/v1/astrology/profile",
        task_name="profile_compact",
        queue_wait_ms=500.0,
        execution_ms=200.0,
        total_ms=700.0,
    )

    assert messages == [
        (
            "Astrology compute queue pressure detected (task=profile_compact, route=/api/v1/astrology/profile, queue_wait_ms=500.0)",
            "warning",
        )
    ]
    runtime.shutdown()


def test_slow_task_warning_captures_sentry_message(monkeypatch) -> None:
    messages: list[tuple[str, str]] = []
    _patch_process_pool(monkeypatch)

    class _Scope:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def set_tag(self, key, value):
            return None

        def set_context(self, key, value):
            return None

    monkeypatch.setattr("app.infrastructure.compute_runtime.sentry_sdk.new_scope", _Scope)
    monkeypatch.setattr(
        "app.infrastructure.compute_runtime.sentry_sdk.capture_message",
        lambda message, level="info": messages.append((message, level)),
    )

    runtime = AstrologyComputeRuntime(max_workers=2)
    runtime._report_slow_task(
        route_name="/api/v1/astrology/profile/placements",
        task_name="placements",
        queue_wait_ms=100.0,
        execution_ms=4100.0,
        total_ms=4200.0,
    )

    assert messages == [
        (
            "Astrology compute slow task detected (task=placements, route=/api/v1/astrology/profile/placements, total_ms=4200.0)",
            "warning",
        )
    ]
    runtime.shutdown()


def test_warning_cooldown_suppresses_duplicate_task_signal(monkeypatch) -> None:
    messages: list[tuple[str, str]] = []
    _patch_process_pool(monkeypatch)

    class _Scope:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def set_tag(self, key, value):
            return None

        def set_context(self, key, value):
            return None

    monkeypatch.setattr("app.infrastructure.compute_runtime.sentry_sdk.new_scope", _Scope)
    monkeypatch.setattr(
        "app.infrastructure.compute_runtime.sentry_sdk.capture_message",
        lambda message, level="info": messages.append((message, level)),
    )

    runtime = AstrologyComputeRuntime(max_workers=2)
    runtime._report_queue_pressure(
        route_name="/api/v1/astrology/profile",
        task_name="profile_compact",
        queue_wait_ms=500.0,
        execution_ms=200.0,
        total_ms=700.0,
    )
    runtime._report_queue_pressure(
        route_name="/api/v1/astrology/profile",
        task_name="profile_compact",
        queue_wait_ms=600.0,
        execution_ms=200.0,
        total_ms=800.0,
    )

    assert len(messages) == 1
    runtime.shutdown()

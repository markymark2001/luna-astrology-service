"""Guardrails that block direct Kerykeion factory usage outside the approved wrapper."""

from pathlib import Path


def test_direct_kerykeion_factories_only_exist_in_wrapper():
    app_root = Path(__file__).resolve().parents[3] / "app"
    allowed_path = app_root / "infrastructure" / "providers" / "kerykeion_chart_factory.py"
    forbidden_markers = (
        "AstrologicalSubjectFactory.from_birth_data",
        "EphemerisDataFactory(",
    )

    offenders: list[str] = []
    for path in app_root.rglob("*.py"):
        if path == allowed_path:
            continue
        content = path.read_text()
        if any(marker in content for marker in forbidden_markers):
            offenders.append(str(path.relative_to(app_root.parent)))

    assert offenders == []

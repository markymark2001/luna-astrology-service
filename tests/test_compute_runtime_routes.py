"""Route wiring tests for astrology shared-runtime execution."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

BASE_BIRTH_DATA = {
    "year": 1990,
    "month": 6,
    "day": 15,
    "hour": 14,
    "minute": 30,
    "latitude": 51.5,
    "longitude": -0.1,
    "timezone": "Europe/London",
}

SYNASTRY_PAYLOAD = {
    "person1": BASE_BIRTH_DATA,
    "person2": {
        "year": 1992,
        "month": 7,
        "day": 22,
        "hour": 8,
        "minute": 15,
        "latitude": 34.0522,
        "longitude": -118.2437,
        "timezone": "America/Los_Angeles",
    },
}

TRANSIT_PERIOD_PAYLOAD = {
    **BASE_BIRTH_DATA,
    "start_date": "2026-01-01",
    "end_date": "2026-01-31",
}

PLANET_HOUSE_PAYLOAD = {
    **BASE_BIRTH_DATA,
    "planet": "venus",
}

STYLE_RESULT = {
    "planets": {"sun": {"name": "Sun", "sign": "Gem", "position": 1, "house": 1}},
    "points": {"ascendant": {"name": "Ascendant", "sign": "Lib", "position": 10}},
    "chart_system": {
        "id": "western_tropical_placidus",
        "zodiac_type": "Tropical",
        "house_system": "Placidus",
        "house_system_identifier": "P",
        "perspective_type": "Apparent Geocentric",
        "provider": "kerykeion",
        "sidereal_mode": None,
    },
}

PLACEMENTS_RESULT = {
    "sun": {"name": "Sun", "sign": "Gem", "house": 1},
    "moon": {"name": "Moon", "sign": "Tau", "house": 12},
    "ascendant": {"name": "Ascendant", "sign": "Lib", "house": None},
    "planets": [
        {"name": "Sun", "sign": "Gem", "house": 1},
        {"name": "Moon", "sign": "Tau", "house": 12},
    ],
    "chart_system": STYLE_RESULT["chart_system"],
}

SOULMATE_RESULT = {
    "planets": {
        "sun": {"name": "Sun", "sign": "Sag", "position": 15.5, "house": 7, "retrograde": False},
        "moon": {"name": "Moon", "sign": "Leo", "position": 22.3, "house": 5, "retrograde": False},
    },
    "houses": {"first_house": {"sign": "Libra"}},
    "points": {"ascendant": {"name": "Ascendant", "sign": "Lib", "position": 10.2}},
    "aspects": [],
    "compatibility_percent": 92,
    "user_venus_sign": "Tau",
    "user_mars_sign": "Ari",
    "user_rising_sign": "Vir",
    "soulmate_birth_year": 1998,
    "chart_system": STYLE_RESULT["chart_system"],
}

PLANET_HOUSE_RESULT = {
    "planet": "venus",
    "house": 7,
    "sign": "Taurus",
    "chart_system": STYLE_RESULT["chart_system"],
}


class FakeRuntime:
    """Async runtime stub that records calls."""

    def __init__(self, results: dict[str, object]):
        self.results = results
        self.calls: list[tuple[str, dict, str]] = []
        self.shutdown_called = False

    async def run(self, task_name: str, payload: dict, route_name: str):
        self.calls.append((task_name, payload, route_name))
        return self.results[task_name]

    def shutdown(self) -> None:
        self.shutdown_called = True


def test_cpu_bound_routes_use_shared_compute_runtime():
    fake_runtime = FakeRuntime(
        {
            "profile_compact": "profile",
            "lookup_profile_compact": "lookup",
            "monthly_profile_compact": "monthly",
            "placements": PLACEMENTS_RESULT,
            "synastry_compact": "synastry",
            "soulmate_chart": SOULMATE_RESULT,
            "transit_period_compact": "transit",
            "planet_house": PLANET_HOUSE_RESULT,
            "style_chart": STYLE_RESULT,
        }
    )
    app.state.astrology_compute_runtime = fake_runtime
    client = TestClient(app)

    routes = [
        ("/api/v1/astrology/profile", BASE_BIRTH_DATA, "profile_compact"),
        ("/api/v1/astrology/profile/lookup", BASE_BIRTH_DATA, "lookup_profile_compact"),
        ("/api/v1/astrology/profile/monthly", BASE_BIRTH_DATA, "monthly_profile_compact"),
        ("/api/v1/astrology/profile/placements", BASE_BIRTH_DATA, "placements"),
        ("/api/v1/astrology/synastry", SYNASTRY_PAYLOAD, "synastry_compact"),
        ("/api/v1/astrology/soulmate/chart", BASE_BIRTH_DATA, "soulmate_chart"),
        ("/api/v1/astrology/transits/period", TRANSIT_PERIOD_PAYLOAD, "transit_period_compact"),
        ("/api/v1/astrology/planet-house", PLANET_HOUSE_PAYLOAD, "planet_house"),
        ("/api/v1/astrology/style/chart", BASE_BIRTH_DATA, "style_chart"),
    ]

    for route, payload, task_name in routes:
        response = client.post(route, json=payload)
        assert response.status_code == 200, route
        assert fake_runtime.calls[-1][0] == task_name
        assert fake_runtime.calls[-1][2] == route


def test_lightweight_recalculate_endpoint_stays_inline():
    fake_runtime = FakeRuntime({})
    app.state.astrology_compute_runtime = fake_runtime
    client = TestClient(app)

    response = client.post(
        "/api/v1/astrology/soulmate/recalculate-birth-date",
        json={
            "user_birth_year": 1990,
            "user_gender": "female",
            "soulmate_sex": "male",
        },
    )

    assert response.status_code == 200
    assert fake_runtime.calls == []


def test_lifespan_sets_astrology_service_role(monkeypatch):
    fake_runtime = FakeRuntime({})
    monkeypatch.setattr("app.main.create_compute_runtime", lambda settings: fake_runtime)

    with TestClient(app):
        assert app.state.service_role == "astrology-service"

    assert fake_runtime.shutdown_called is True

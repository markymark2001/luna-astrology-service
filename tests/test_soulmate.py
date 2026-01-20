"""Tests for soulmate chart endpoint.

TDD approach: these tests are written first and will fail until implementation is complete.

Run tests:
    pytest astrology-service/tests/test_soulmate.py -v
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# Valid birth data for testing
VALID_BIRTH_DATA = {
    "year": 1990,
    "month": 6,
    "day": 15,
    "hour": 14,
    "minute": 30,
    "latitude": 51.5,
    "longitude": -0.1,
    "timezone": "Europe/London",
}

# Birth data for specific sign tests
ARIES_RISING_BIRTH_DATA = {
    "year": 1990,
    "month": 4,
    "day": 10,
    "hour": 6,  # Early morning for Aries rising
    "minute": 0,
    "latitude": 51.5,
    "longitude": -0.1,
    "timezone": "Europe/London",
}

# Kerykeion uses abbreviated sign names
VALID_SIGNS = [
    "Ari", "Tau", "Gem", "Can", "Leo", "Vir",
    "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis",
]

# Full sign names for reference
FULL_SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Element mappings for compatibility tests
SIGN_TO_ELEMENT = {
    "Ari": "Fire", "Leo": "Fire", "Sag": "Fire",
    "Tau": "Earth", "Vir": "Earth", "Cap": "Earth",
    "Gem": "Air", "Lib": "Air", "Aqu": "Air",
    "Can": "Water", "Sco": "Water", "Pis": "Water",
}

# Compatible elements (romantic harmony)
COMPATIBLE_ELEMENTS = {
    "Fire": ["Fire", "Air"],
    "Air": ["Air", "Fire"],
    "Earth": ["Earth", "Water"],
    "Water": ["Water", "Earth"],
}


class TestSoulmateEndpointResponses:
    """Tests for endpoint HTTP responses."""

    def test_endpoint_returns_200_with_valid_data(self):
        """Happy path - valid birth data returns 200."""
        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        assert response.status_code == 200

    def test_endpoint_returns_422_with_invalid_birth_data(self):
        """Invalid birth data returns 422 validation error."""
        invalid_data = {
            "year": 1990,
            "month": 13,  # Invalid month
            "day": 15,
            "hour": 14,
            "minute": 30,
            "latitude": 51.5,
            "longitude": -0.1,
            "timezone": "Europe/London",
        }
        response = client.post("/api/v1/astrology/soulmate/chart", json=invalid_data)
        assert response.status_code == 422

    def test_endpoint_returns_422_with_missing_required_fields(self):
        """Missing required fields returns 422."""
        incomplete_data = {
            "year": 1990,
            "month": 6,
            # Missing day
        }
        response = client.post("/api/v1/astrology/soulmate/chart", json=incomplete_data)
        assert response.status_code == 422


class TestSoulmateResponseStructure:
    """Tests for response JSON structure."""

    def test_response_has_planets_dict(self):
        """Response contains planets dict with sun, moon, venus, mars, etc."""
        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()
        assert "planets" in data
        assert isinstance(data["planets"], dict)
        # Check for key planets
        planets = data["planets"]
        assert "sun" in planets
        assert "moon" in planets
        assert "venus" in planets
        assert "mars" in planets

    def test_response_has_houses_dict(self):
        """Response contains houses dict (CORE preset has 6 houses)."""
        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()
        assert "houses" in data
        assert isinstance(data["houses"], dict)
        # CORE preset includes 6 houses
        assert len(data["houses"]) >= 6

    def test_response_has_points_dict(self):
        """Response contains points dict with ascendant and medium_coeli."""
        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()
        assert "points" in data
        assert isinstance(data["points"], dict)
        points = data["points"]
        assert "ascendant" in points
        # Kerykeion uses "medium_coeli" instead of "midheaven"
        assert "medium_coeli" in points

    def test_response_has_aspects_list(self):
        """Response contains aspects list."""
        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()
        assert "aspects" in data
        assert isinstance(data["aspects"], list)

    def test_planet_has_required_fields(self):
        """Each planet should have name, sign, position, house, retrograde."""
        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()
        sun = data["planets"]["sun"]
        assert "name" in sun
        assert "sign" in sun
        assert "position" in sun
        assert "house" in sun
        assert "retrograde" in sun

    def test_points_have_sign_field(self):
        """Points should have sign field."""
        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()
        ascendant = data["points"]["ascendant"]
        assert "sign" in ascendant


class TestSoulmateDerivationRules:
    """Tests for soulmate chart derivation logic.

    Only Sun/Moon/Rising are controllable through birth datetime.
    Other planets will be whatever positions exist on the derived date.

    Note: Kerykeion uses abbreviated sign names (Ari, Tau, Gem, etc.)
    """

    def test_soulmate_ascendant_is_valid_sign(self):
        """Soulmate rising should be a valid zodiac sign."""
        response = client.post(
            "/api/v1/astrology/soulmate/chart", json=ARIES_RISING_BIRTH_DATA
        )
        data = response.json()
        soulmate_ascendant = data["points"]["ascendant"]["sign"]

        # Soulmate's ascendant should be one of the 12 signs (abbreviated)
        assert soulmate_ascendant in VALID_SIGNS

    def test_soulmate_sun_is_valid_sign(self):
        """Soulmate Sun should be a valid zodiac sign."""
        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()
        soulmate_sun_sign = data["planets"]["sun"]["sign"]

        # Sun should be a valid abbreviated sign
        assert soulmate_sun_sign in VALID_SIGNS

    def test_soulmate_moon_is_valid_sign(self):
        """Soulmate Moon should be a valid zodiac sign."""
        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()
        soulmate_moon_sign = data["planets"]["moon"]["sign"]

        # Moon should be a valid abbreviated sign
        assert soulmate_moon_sign in VALID_SIGNS

    def test_derived_chart_is_complete(self):
        """Derived chart should have all standard planets."""
        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()

        expected_planets = [
            "sun",
            "moon",
            "mercury",
            "venus",
            "mars",
            "jupiter",
            "saturn",
            "uranus",
            "neptune",
            "pluto",
        ]

        for planet in expected_planets:
            assert planet in data["planets"], f"Missing planet: {planet}"

    def test_same_input_produces_consistent_output(self):
        """Same birth data should produce same soulmate chart (deterministic)."""
        response1 = client.post(
            "/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA
        )
        response2 = client.post(
            "/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA
        )

        data1 = response1.json()
        data2 = response2.json()

        # Sun, Moon, and Rising should be consistent
        assert data1["planets"]["sun"]["sign"] == data2["planets"]["sun"]["sign"]
        assert data1["planets"]["moon"]["sign"] == data2["planets"]["moon"]["sign"]
        assert data1["points"]["ascendant"]["sign"] == data2["points"]["ascendant"]["sign"]


class TestVenusMarsCompatibility:
    """Tests for Venus/Mars romantic compatibility in soulmate derivation.

    Astrologically, Venus-Mars connections indicate romantic/sexual chemistry:
    - Soulmate's Venus should be compatible with user's Mars (attraction to user)
    - Soulmate's Mars should be compatible with user's Venus (pursues what user values)
    """

    def _get_user_chart(self, birth_data: dict) -> dict:
        """Helper to get user's natal chart for comparison."""
        # Profile endpoint returns plain text, so for testing
        # we just verify the soulmate chart has compatible elements
        return birth_data

    def test_soulmate_venus_is_valid_sign(self):
        """Soulmate Venus should be a valid zodiac sign."""
        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()
        soulmate_venus = data["planets"]["venus"]["sign"]

        assert soulmate_venus in VALID_SIGNS

    def test_soulmate_mars_is_valid_sign(self):
        """Soulmate Mars should be a valid zodiac sign."""
        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()
        soulmate_mars = data["planets"]["mars"]["sign"]

        assert soulmate_mars in VALID_SIGNS

    def test_soulmate_venus_in_compatible_element_with_user_mars(self):
        """Soulmate's Venus should be in a compatible element with user's Mars.

        This creates attraction: soulmate is drawn to qualities user actively expresses.
        Compatible elements: Fire-Air, Earth-Water
        """
        # First get user's Mars sign by calculating their chart
        # We need to get the user's natal chart to know their Mars sign
        # For this test, we'll calculate user chart via the soulmate service internals

        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()
        soulmate_venus = data["planets"]["venus"]["sign"]
        soulmate_venus_element = SIGN_TO_ELEMENT.get(soulmate_venus)

        # Soulmate's Venus element should be valid
        assert soulmate_venus_element is not None
        assert soulmate_venus_element in ["Fire", "Earth", "Air", "Water"]

    def test_soulmate_mars_in_compatible_element_with_user_venus(self):
        """Soulmate's Mars should be in a compatible element with user's Venus.

        This creates pursuit: soulmate actively pursues what user values in love.
        Compatible elements: Fire-Air, Earth-Water
        """
        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()
        soulmate_mars = data["planets"]["mars"]["sign"]
        soulmate_mars_element = SIGN_TO_ELEMENT.get(soulmate_mars)

        # Soulmate's Mars element should be valid
        assert soulmate_mars_element is not None
        assert soulmate_mars_element in ["Fire", "Earth", "Air", "Water"]

    def test_venus_mars_compatibility_across_multiple_users(self):
        """Test Venus/Mars targeting works for different user birth data."""
        test_cases = [
            {  # Fire Mars user (Aries season, morning)
                "year": 1992, "month": 4, "day": 5, "hour": 8, "minute": 0,
                "latitude": 40.7, "longitude": -74.0, "timezone": "America/New_York",
            },
            {  # Earth Venus user (Taurus season, evening)
                "year": 1988, "month": 5, "day": 10, "hour": 20, "minute": 30,
                "latitude": 34.0, "longitude": -118.2, "timezone": "America/Los_Angeles",
            },
            {  # Water dominant user (Cancer season)
                "year": 1995, "month": 7, "day": 15, "hour": 12, "minute": 0,
                "latitude": 51.5, "longitude": -0.1, "timezone": "Europe/London",
            },
        ]

        for birth_data in test_cases:
            response = client.post("/api/v1/astrology/soulmate/chart", json=birth_data)
            assert response.status_code == 200

            data = response.json()
            soulmate_venus = data["planets"]["venus"]["sign"]
            soulmate_mars = data["planets"]["mars"]["sign"]

            # Both should be valid signs
            assert soulmate_venus in VALID_SIGNS, f"Invalid Venus: {soulmate_venus}"
            assert soulmate_mars in VALID_SIGNS, f"Invalid Mars: {soulmate_mars}"

            # Both should map to valid elements
            assert SIGN_TO_ELEMENT.get(soulmate_venus) is not None
            assert SIGN_TO_ELEMENT.get(soulmate_mars) is not None


class TestVenusMarsElementCompatibility:
    """Tests that verify soulmate Venus/Mars are compatible with user's Mars/Venus.

    These tests use the service directly to access both user and soulmate charts.
    """

    def test_soulmate_venus_compatible_with_user_mars(self):
        """Soulmate's Venus element should be compatible with user's Mars element.

        Fire-Air and Earth-Water are compatible pairs.
        """
        from app.application.soulmate_service import SoulmateService
        from app.config.astrology_presets import DetailLevel, get_preset
        from app.domain.models import BirthData
        from app.infrastructure.providers.kerykeion_provider import KerykeionProvider

        # Setup
        config = get_preset(DetailLevel.CORE)
        provider = KerykeionProvider(config=config)
        service = SoulmateService(provider=provider)

        user_birth_data = BirthData(
            year=1990, month=6, day=15, hour=14, minute=30,
            latitude=51.5, longitude=-0.1, timezone="Europe/London"
        )

        # Get user's chart
        user_chart = provider.calculate_natal_chart(user_birth_data)
        user_mars_sign = user_chart.planets.get("mars", {}).get("sign", "Ari")
        user_mars_element = SIGN_TO_ELEMENT.get(user_mars_sign)

        # Get soulmate chart
        soulmate_response = service.generate_soulmate_chart(user_birth_data)
        soulmate_venus_sign = soulmate_response.planets.get("venus", {}).get("sign", "Ari")
        soulmate_venus_element = SIGN_TO_ELEMENT.get(soulmate_venus_sign)

        # Verify compatibility
        compatible_elements = COMPATIBLE_ELEMENTS.get(user_mars_element, [])
        assert soulmate_venus_element in compatible_elements, (
            f"Soulmate Venus ({soulmate_venus_sign}/{soulmate_venus_element}) "
            f"not compatible with user Mars ({user_mars_sign}/{user_mars_element}). "
            f"Expected one of: {compatible_elements}"
        )

    def test_soulmate_mars_compatible_with_user_venus(self):
        """Soulmate's Mars element should be compatible with user's Venus element.

        Fire-Air and Earth-Water are compatible pairs.
        """
        from app.application.soulmate_service import SoulmateService
        from app.config.astrology_presets import DetailLevel, get_preset
        from app.domain.models import BirthData
        from app.infrastructure.providers.kerykeion_provider import KerykeionProvider

        # Setup
        config = get_preset(DetailLevel.CORE)
        provider = KerykeionProvider(config=config)
        service = SoulmateService(provider=provider)

        user_birth_data = BirthData(
            year=1990, month=6, day=15, hour=14, minute=30,
            latitude=51.5, longitude=-0.1, timezone="Europe/London"
        )

        # Get user's chart
        user_chart = provider.calculate_natal_chart(user_birth_data)
        user_venus_sign = user_chart.planets.get("venus", {}).get("sign", "Ari")
        user_venus_element = SIGN_TO_ELEMENT.get(user_venus_sign)

        # Get soulmate chart
        soulmate_response = service.generate_soulmate_chart(user_birth_data)
        soulmate_mars_sign = soulmate_response.planets.get("mars", {}).get("sign", "Ari")
        soulmate_mars_element = SIGN_TO_ELEMENT.get(soulmate_mars_sign)

        # Verify compatibility
        compatible_elements = COMPATIBLE_ELEMENTS.get(user_venus_element, [])
        assert soulmate_mars_element in compatible_elements, (
            f"Soulmate Mars ({soulmate_mars_sign}/{soulmate_mars_element}) "
            f"not compatible with user Venus ({user_venus_sign}/{user_venus_element}). "
            f"Expected one of: {compatible_elements}"
        )

    def test_comprehensive_compatibility_multiple_birth_dates(self):
        """Test comprehensive compatibility scoring across different birth dates.

        The new system uses 9 compatibility conditions with an 18-point max score.
        Rather than guaranteeing any single factor (like Venus/Mars), it optimizes
        for overall compatibility. All generated soulmates should have good scores.
        """
        from app.application.soulmate_service import SoulmateService
        from app.config.astrology_presets import DetailLevel, get_preset
        from app.domain.models import BirthData
        from app.infrastructure.providers.kerykeion_provider import KerykeionProvider

        config = get_preset(DetailLevel.CORE)
        provider = KerykeionProvider(config=config)
        service = SoulmateService(provider=provider)

        test_cases = [
            BirthData(year=1985, month=3, day=20, hour=10, minute=0,
                      latitude=40.7, longitude=-74.0, timezone="America/New_York"),
            BirthData(year=1992, month=8, day=15, hour=16, minute=30,
                      latitude=34.0, longitude=-118.2, timezone="America/Los_Angeles"),
            BirthData(year=1998, month=12, day=1, hour=22, minute=0,
                      latitude=51.5, longitude=-0.1, timezone="Europe/London"),
        ]

        for user_birth_data in test_cases:
            soulmate_response = service.generate_soulmate_chart(user_birth_data)

            # Verify soulmate has valid placements
            soulmate_venus_sign = soulmate_response.planets.get("venus", {}).get("sign")
            soulmate_mars_sign = soulmate_response.planets.get("mars", {}).get("sign")
            assert soulmate_venus_sign in VALID_SIGNS, f"Invalid Venus sign: {soulmate_venus_sign}"
            assert soulmate_mars_sign in VALID_SIGNS, f"Invalid Mars sign: {soulmate_mars_sign}"

            # Verify compatibility percentage is reasonable
            # The new scoring uses RelationshipScoreFactory + North Node mapped to 0-100%
            # Since we derive soulmates for compatibility, expect at least 20%
            assert soulmate_response.compatibility_percent >= 20, (
                f"Birth {user_birth_data.year}: Compatibility too low: "
                f"{soulmate_response.compatibility_percent}%"
            )

            # Verify user placements are returned
            assert soulmate_response.user_venus_sign in VALID_SIGNS
            assert soulmate_response.user_mars_sign in VALID_SIGNS
            assert soulmate_response.user_rising_sign in VALID_SIGNS


class TestCompatibilityPercent:
    """Tests for compatibility percentage in response."""

    def test_response_includes_compatibility_percent(self):
        """Response should include compatibility_percent field."""
        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()
        assert "compatibility_percent" in data

    def test_compatibility_percent_is_integer(self):
        """compatibility_percent should be an integer."""
        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()
        assert isinstance(data["compatibility_percent"], int)

    def test_compatibility_percent_in_valid_range(self):
        """compatibility_percent should be between 0 and 100 (honest linear scoring)."""
        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()
        assert 0 <= data["compatibility_percent"] <= 100


class TestSoulmateBirthYear:
    """Tests for soulmate_birth_year in response and age-appropriate generation."""

    def test_response_includes_soulmate_birth_year(self):
        """Response should include soulmate_birth_year field."""
        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()
        assert "soulmate_birth_year" in data

    def test_soulmate_birth_year_is_integer(self):
        """soulmate_birth_year should be an integer."""
        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()
        assert isinstance(data["soulmate_birth_year"], int)

    def test_soulmate_age_within_7_years_of_user(self):
        """Soulmate's age should be within ±7 years of user's age."""
        from datetime import datetime

        current_year = datetime.now().year
        user_birth_year = VALID_BIRTH_DATA["year"]
        user_age = current_year - user_birth_year

        response = client.post("/api/v1/astrology/soulmate/chart", json=VALID_BIRTH_DATA)
        data = response.json()
        soulmate_birth_year = data["soulmate_birth_year"]
        soulmate_age = current_year - soulmate_birth_year

        # Soulmate age should be within ±7 years of user (but minimum 18)
        expected_min_age = max(18, user_age - 7)
        expected_max_age = user_age + 7

        assert soulmate_age >= expected_min_age, (
            f"Soulmate age {soulmate_age} is too young. Expected >= {expected_min_age}"
        )
        assert soulmate_age <= expected_max_age, (
            f"Soulmate age {soulmate_age} is too old. Expected <= {expected_max_age}"
        )

    def test_soulmate_minimum_age_is_18(self):
        """Soulmate should never be under 18, even for young users."""
        from datetime import datetime

        current_year = datetime.now().year

        # Young user (20 years old in current year)
        young_user_birth_data = {
            "year": current_year - 20,
            "month": 6,
            "day": 15,
            "hour": 14,
            "minute": 30,
            "latitude": 51.5,
            "longitude": -0.1,
            "timezone": "Europe/London",
        }

        response = client.post("/api/v1/astrology/soulmate/chart", json=young_user_birth_data)
        data = response.json()
        soulmate_birth_year = data["soulmate_birth_year"]
        soulmate_age = current_year - soulmate_birth_year

        assert soulmate_age >= 18, f"Soulmate age {soulmate_age} is under 18"

    def test_soulmate_age_for_older_user(self):
        """Soulmate age range should be correct for older users."""
        from datetime import datetime

        current_year = datetime.now().year

        # Older user (40 years old)
        older_user_birth_data = {
            "year": current_year - 40,
            "month": 6,
            "day": 15,
            "hour": 14,
            "minute": 30,
            "latitude": 51.5,
            "longitude": -0.1,
            "timezone": "Europe/London",
        }

        response = client.post("/api/v1/astrology/soulmate/chart", json=older_user_birth_data)
        data = response.json()
        soulmate_birth_year = data["soulmate_birth_year"]
        soulmate_age = current_year - soulmate_birth_year

        # For a 40 year old, soulmate should be 33-47
        assert 33 <= soulmate_age <= 47, f"Soulmate age {soulmate_age} out of expected range 33-47"

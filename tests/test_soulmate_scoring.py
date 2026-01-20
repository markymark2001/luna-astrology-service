"""Tests for soulmate scoring system.

These tests verify that the soulmate generation algorithm produces high-quality matches
(≥95% compatibility) for any user input.

Test Structure:
1. TestEndToEndCompatibility - Verify FINAL compatibility ≥95% for diverse users (EXPECTED TO FAIL)
2. Supporting unit tests - Test calculation functions (EXPECTED TO PASS)

The end-to-end tests are EXPECTED TO FAIL with the current implementation.
They document what's broken - the algorithm produces ~55-90%, not 95%+.

Run tests:
    pytest astrology-service/tests/test_soulmate_scoring.py -v
"""

from dataclasses import dataclass

import pytest

from app.application.soulmate_service import (
    MOON_AFFINITIES,
    OPPOSITE_SIGNS,
    SUN_QUALITY,
    ZODIAC_SIGNS,
    SoulmateService,
    calculate_aspect_score,
    score_north_node_contacts,
    score_to_compatibility_percent,
)
from app.config.astrology_presets import DetailLevel, get_preset
from app.domain.models import BirthData
from app.infrastructure.providers.kerykeion_provider import KerykeionProvider

# ============ Test User Profiles ============
# 13 test users covering all Sun signs, modalities, elements, ages, and locations


@dataclass
class UserProfile:
    """User profile for compatibility testing (not a test class)."""

    name: str
    sun_sign: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    latitude: float
    longitude: float
    timezone: str


TEST_USERS = [
    # Aries - Cardinal Fire - New York
    UserProfile("Aries User", "Ari", 1990, 4, 10, 10, 0, 40.73, -73.93, "America/New_York"),
    # Taurus - Fixed Earth - London
    UserProfile("Taurus User", "Tau", 1988, 5, 15, 14, 30, 51.5, -0.1, "Europe/London"),
    # Gemini - Mutable Air - London
    UserProfile("Gemini User", "Gem", 1990, 6, 15, 14, 30, 51.5, -0.1, "Europe/London"),
    # Cancer - Cardinal Water - Tokyo
    UserProfile("Cancer User", "Can", 1995, 7, 5, 8, 0, 35.68, 139.77, "Asia/Tokyo"),
    # Leo - Fixed Fire - Sydney
    UserProfile("Leo User", "Leo", 1992, 8, 10, 16, 45, -33.87, 151.21, "Australia/Sydney"),
    # Virgo - Mutable Earth - Reykjavik (no DST, similar to UTC)
    UserProfile("Virgo User", "Vir", 1985, 9, 10, 12, 0, 64.15, -21.94, "Atlantic/Reykjavik"),
    # Libra - Cardinal Air - Berlin
    UserProfile("Libra User", "Lib", 1991, 10, 15, 20, 0, 52.52, 13.40, "Europe/Berlin"),
    # Scorpio - Fixed Water - Moscow
    UserProfile("Scorpio User", "Sco", 1987, 11, 8, 10, 30, 55.75, 37.62, "Europe/Moscow"),
    # Sagittarius - Mutable Fire - Los Angeles
    UserProfile("Sagittarius User", "Sag", 1993, 12, 5, 11, 0, 34.05, -118.24, "America/Los_Angeles"),
    # Capricorn - Cardinal Earth - London (older user)
    UserProfile("Capricorn User", "Cap", 1970, 1, 10, 6, 0, 51.5, -0.1, "Europe/London"),
    # Aquarius - Fixed Air - New York (younger user)
    UserProfile("Aquarius User", "Aqu", 2004, 2, 14, 15, 0, 40.73, -73.93, "America/New_York"),
    # Pisces - Mutable Water - Tokyo
    UserProfile("Pisces User", "Pis", 1995, 3, 1, 8, 45, 35.68, 139.77, "Asia/Tokyo"),
    # Novosibirsk - Virgo (edge case: far east timezone, early morning)
    UserProfile("Novosibirsk 5am User", "Vir", 2001, 9, 5, 5, 0, 55.03, 82.92, "Asia/Novosibirsk"),
    # Novosibirsk - Virgo (edge case: far east timezone, noon)
    UserProfile("Novosibirsk 12pm User", "Vir", 2001, 9, 5, 12, 0, 55.03, 82.92, "Asia/Novosibirsk"),
]


def _create_birth_data(user: UserProfile) -> BirthData:
    """Convert UserProfile to BirthData."""
    return BirthData(
        year=user.year,
        month=user.month,
        day=user.day,
        hour=user.hour,
        minute=user.minute,
        latitude=user.latitude,
        longitude=user.longitude,
        timezone=user.timezone,
    )


def _get_provider_and_service() -> tuple[KerykeionProvider, SoulmateService]:
    """Create provider and service instances."""
    config = get_preset(DetailLevel.CORE)
    provider = KerykeionProvider(config)
    service = SoulmateService(provider=provider)
    return provider, service


# ============ Test 1: End-to-End Compatibility ============
# EXPECTED TO FAIL - documents that algorithm produces ~55-90%, not 95%+


class TestEndToEndCompatibility:
    """Tests verifying final compatibility ≥95% for all test users.

    These tests verify the OUTCOME: that any user input produces a soulmate
    with ≥95% compatibility using the 38-point Kerykeion system.

    EXPECTED TO FAIL with current implementation - they document what's broken.
    """

    @pytest.mark.parametrize("user", TEST_USERS, ids=lambda u: u.name.replace(" ", "_"))
    def test_final_compatibility_at_least_95_percent(self, user: UserProfile):
        """Final compatibility should be ≥95% for any user.

        This is the PRIMARY success criteria. If this test passes for all users,
        the algorithm is working correctly.

        EXPECTED TO FAIL - current implementation produces lower scores.
        """
        _, service = _get_provider_and_service()
        birth_data = _create_birth_data(user)

        result = service.generate_soulmate_chart(birth_data)

        print(f"\n{user.name}: {result.compatibility_percent}%")

        assert result.compatibility_percent >= 95, (
            f"{user.name} got {result.compatibility_percent}% compatibility, expected ≥95%"
        )

    def test_deterministic_same_input_same_result(self):
        """Same user should always get the same result (deterministic)."""
        _, service = _get_provider_and_service()
        user = TEST_USERS[2]  # Gemini user
        birth_data = _create_birth_data(user)

        result1 = service.generate_soulmate_chart(birth_data)
        result2 = service.generate_soulmate_chart(birth_data)

        assert result1.compatibility_percent == result2.compatibility_percent
        assert result1.planets.get("sun", {}).get("sign") == result2.planets.get("sun", {}).get("sign")
        assert result1.planets.get("moon", {}).get("sign") == result2.planets.get("moon", {}).get("sign")


# ============ Supporting Unit Tests ============
# EXPECTED TO PASS - these test calculation functions work correctly


class TestCalculateAspectScore:
    """Tests for calculate_aspect_score function."""

    def test_exact_conjunction_scores_11(self):
        """Exact conjunction (0°) should score 11 points."""
        score, aspect, orb = calculate_aspect_score(15.0, 15.0)
        assert score == 11
        assert aspect == "conjunction"
        assert orb == 0.0

    def test_tight_conjunction_within_2_degrees_scores_11(self):
        """Conjunction within 2° should score 11 points (tight)."""
        score, aspect, _ = calculate_aspect_score(15.0, 17.0)
        assert score == 11
        assert aspect == "conjunction"

    def test_wider_conjunction_scores_10(self):
        """Conjunction beyond 2° but within 8° should score 10 points."""
        score, aspect, _ = calculate_aspect_score(15.0, 22.0)
        assert score == 10
        assert aspect == "conjunction"

    def test_trine_scores_8(self):
        """Trine (120°) should score 8 points."""
        score, aspect, _ = calculate_aspect_score(0.0, 120.0)
        assert score == 8
        assert aspect == "trine"

    def test_sextile_scores_6(self):
        """Sextile (60°) should score 6 points."""
        score, aspect, _ = calculate_aspect_score(0.0, 60.0)
        assert score == 6
        assert aspect == "sextile"

    def test_square_scores_0(self):
        """Square (90°) should score 0 points."""
        score, aspect, _ = calculate_aspect_score(0.0, 90.0)
        assert score == 0
        assert aspect == "square"

    def test_opposition_scores_4(self):
        """Opposition (180°) should score 4 points."""
        score, aspect, _ = calculate_aspect_score(0.0, 180.0)
        assert score == 4
        assert aspect == "opposition"

    def test_conjunction_across_360_boundary(self):
        """Conjunction should work across 360°/0° boundary."""
        score, aspect, orb = calculate_aspect_score(358.0, 2.0)
        assert aspect == "conjunction"
        assert orb == 4.0
        assert score == 10  # 4° orb = wider conjunction

    def test_no_aspect_returns_0(self):
        """Positions without aspect should return 0 score."""
        score, aspect, _ = calculate_aspect_score(0.0, 45.0)
        assert score == 0
        assert aspect is None


class TestScoreToCompatibilityPercent:
    """Tests for score_to_compatibility_percent function."""

    def test_score_38_maps_to_100_percent(self):
        """Score 38 (UI max) should map to 100%."""
        assert score_to_compatibility_percent(38) == 100

    def test_scores_above_38_cap_at_100_percent(self):
        """Scores above 38 should cap at 100%."""
        assert score_to_compatibility_percent(42) == 100
        assert score_to_compatibility_percent(56) == 100

    def test_score_0_maps_to_0_percent(self):
        """Score 0 should map to 0%."""
        assert score_to_compatibility_percent(0) == 0

    def test_score_19_maps_to_71_percent_with_sqrt_curve(self):
        """Score 19 maps to 71% with sqrt curve (sqrt(19/38) ≈ 0.707)."""
        assert score_to_compatibility_percent(19) == 71

    def test_negative_score_maps_to_0_percent(self):
        """Negative scores should map to 0%."""
        assert score_to_compatibility_percent(-5) == 0


class TestScoreNorthNodeContacts:
    """Tests for score_north_node_contacts function."""

    def test_sun_conjunct_north_node_scores_4(self):
        """Soulmate Sun conjunct user's North Node scores 4 points."""
        score = score_north_node_contacts(
            user_north_node_sign="Leo",
            soulmate_sun_sign="Leo",
            soulmate_moon_sign="Ari",
            soulmate_venus_sign="Gem",
        )
        assert score == 4

    def test_moon_conjunct_north_node_scores_4(self):
        """Soulmate Moon conjunct user's North Node scores 4 points."""
        score = score_north_node_contacts(
            user_north_node_sign="Leo",
            soulmate_sun_sign="Ari",
            soulmate_moon_sign="Leo",
            soulmate_venus_sign="Gem",
        )
        assert score == 4

    def test_venus_conjunct_north_node_scores_3(self):
        """Soulmate Venus conjunct user's North Node scores 3 points."""
        score = score_north_node_contacts(
            user_north_node_sign="Leo",
            soulmate_sun_sign="Ari",
            soulmate_moon_sign="Gem",
            soulmate_venus_sign="Leo",
        )
        assert score == 3

    def test_all_three_conjunct_caps_at_8(self):
        """All three (Sun+Moon+Venus) conjunct caps at 8 points, not 11."""
        score = score_north_node_contacts(
            user_north_node_sign="Leo",
            soulmate_sun_sign="Leo",
            soulmate_moon_sign="Leo",
            soulmate_venus_sign="Leo",
        )
        assert score == 8  # Capped at 8, not 4+4+3=11

    def test_no_contacts_scores_0(self):
        """No North Node contacts scores 0 points."""
        score = score_north_node_contacts(
            user_north_node_sign="Leo",
            soulmate_sun_sign="Ari",
            soulmate_moon_sign="Gem",
            soulmate_venus_sign="Sag",
        )
        assert score == 0


class TestFindHourForAscendant:
    """Tests for _find_hour_for_ascendant method."""

    def test_produces_correct_ascendant_sign(self):
        """Should find hour that produces the target Ascendant sign."""
        provider, service = _get_provider_and_service()

        for target_rising in ZODIAC_SIGNS:
            target_hour, target_minute = service._find_hour_for_ascendant(
                1995, 6, 15, target_rising, 51.5, -0.1, "Europe/London"
            )

            birth = BirthData(
                year=1995,
                month=6,
                day=15,
                hour=target_hour,
                minute=target_minute,
                latitude=51.5,
                longitude=-0.1,
                timezone="Europe/London",
            )
            chart = provider.calculate_natal_chart(birth)
            actual_sign = chart.points.get("ascendant", {}).get("sign", "")

            assert actual_sign == target_rising, (
                f"Target rising {target_rising}, got {actual_sign} at {target_hour}:{target_minute:02d}"
            )

    def test_produces_ascendant_within_15_degrees_of_sign_center(self):
        """Ascendant should be within 15° of the target sign's center."""
        provider, service = _get_provider_and_service()
        errors = []

        for target_rising in ZODIAC_SIGNS:
            sign_idx = ZODIAC_SIGNS.index(target_rising)
            target_center = (sign_idx * 30) + 15  # Middle of sign

            target_hour, target_minute = service._find_hour_for_ascendant(
                1995, 6, 15, target_rising, 51.5, -0.1, "Europe/London"
            )

            birth = BirthData(
                year=1995,
                month=6,
                day=15,
                hour=target_hour,
                minute=target_minute,
                latitude=51.5,
                longitude=-0.1,
                timezone="Europe/London",
            )
            chart = provider.calculate_natal_chart(birth)
            actual = chart.points.get("ascendant", {}).get("abs_pos", 0)

            error = abs(target_center - actual)
            if error > 180:
                error = 360 - error
            errors.append(error)

        # All should be within 15° of sign center
        for i, error in enumerate(errors):
            assert error <= 15, f"{ZODIAC_SIGNS[i]}: error {error:.1f}° exceeds 15° threshold"


class TestZodiacMappingsCompleteness:
    """Tests verifying all zodiac mappings are complete."""

    def test_all_12_signs_in_zodiac_signs(self):
        """ZODIAC_SIGNS should contain exactly 12 signs."""
        assert len(ZODIAC_SIGNS) == 12

    def test_all_signs_have_opposite(self):
        """Every sign should have an opposite sign defined."""
        for sign in ZODIAC_SIGNS:
            assert sign in OPPOSITE_SIGNS, f"Missing opposite for {sign}"
            opposite = OPPOSITE_SIGNS[sign]
            assert opposite in ZODIAC_SIGNS, f"Invalid opposite {opposite} for {sign}"

    def test_opposites_are_symmetrical(self):
        """Opposite relationships should be symmetrical (A opposite B means B opposite A)."""
        for sign in ZODIAC_SIGNS:
            opposite = OPPOSITE_SIGNS[sign]
            assert OPPOSITE_SIGNS[opposite] == sign, f"{sign} and {opposite} not symmetrical"

    def test_all_signs_have_moon_affinities(self):
        """Every sign should have moon affinities defined."""
        for sign in ZODIAC_SIGNS:
            assert sign in MOON_AFFINITIES, f"Missing moon affinities for {sign}"
            affinities = MOON_AFFINITIES[sign]
            assert len(affinities) >= 1, f"Empty affinities for {sign}"

    def test_moon_affinities_same_sign_first(self):
        """First affinity should be the same sign (strongest match)."""
        for sign in ZODIAC_SIGNS:
            assert MOON_AFFINITIES[sign][0] == sign, f"First affinity for {sign} is not itself"

    def test_all_signs_have_sun_quality(self):
        """Every sign should have a Sun quality (modality) defined."""
        for sign in ZODIAC_SIGNS:
            assert sign in SUN_QUALITY, f"Missing sun quality for {sign}"
            quality = SUN_QUALITY[sign]
            assert quality in ["Cardinal", "Fixed", "Mutable"], f"Invalid quality {quality} for {sign}"

    def test_cardinal_signs_correct(self):
        """Cardinal signs should be Ari, Can, Lib, Cap."""
        cardinal = [s for s in ZODIAC_SIGNS if SUN_QUALITY[s] == "Cardinal"]
        assert set(cardinal) == {"Ari", "Can", "Lib", "Cap"}

    def test_fixed_signs_correct(self):
        """Fixed signs should be Tau, Leo, Sco, Aqu."""
        fixed = [s for s in ZODIAC_SIGNS if SUN_QUALITY[s] == "Fixed"]
        assert set(fixed) == {"Tau", "Leo", "Sco", "Aqu"}

    def test_mutable_signs_correct(self):
        """Mutable signs should be Gem, Vir, Sag, Pis."""
        mutable = [s for s in ZODIAC_SIGNS if SUN_QUALITY[s] == "Mutable"]
        assert set(mutable) == {"Gem", "Vir", "Sag", "Pis"}

"""Soulmate chart application service - derives ideal partner chart from user's birth data."""

import math
from datetime import date, datetime
from typing import Any

from kerykeion import RelationshipScoreFactory

from app.domain.models import BirthData, NatalChart
from app.domain.ports import IAstrologyProvider
from app.infrastructure.providers.kerykeion_provider import KerykeionProvider
from app.models.soulmate import SoulmateChartResponse

# Zodiac constants for derivation logic
# Note: Kerykeion uses abbreviated sign names (Ari, Tau, Gem, etc.)
ZODIAC_SIGNS = [
    "Ari", "Tau", "Gem", "Can", "Leo", "Vir",
    "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis",
]

OPPOSITE_SIGNS: dict[str, str] = {
    "Ari": "Lib", "Tau": "Sco", "Gem": "Sag", "Can": "Cap",
    "Leo": "Aqu", "Vir": "Pis", "Lib": "Ari", "Sco": "Tau",
    "Sag": "Gem", "Cap": "Can", "Aqu": "Leo", "Pis": "Vir",
}

ELEMENT_MAP: dict[str, str] = {
    "Ari": "Fire", "Tau": "Earth", "Gem": "Air", "Can": "Water",
    "Leo": "Fire", "Vir": "Earth", "Lib": "Air", "Sco": "Water",
    "Sag": "Fire", "Cap": "Earth", "Aqu": "Air", "Pis": "Water",
}

# Sun quality (modality) - used for Destiny Sign bonus in Kerykeion RelationshipScoreFactory
SUN_QUALITY: dict[str, str] = {
    "Ari": "Cardinal", "Tau": "Fixed", "Gem": "Mutable",
    "Can": "Cardinal", "Leo": "Fixed", "Vir": "Mutable",
    "Lib": "Cardinal", "Sco": "Fixed", "Sag": "Mutable",
    "Cap": "Cardinal", "Aqu": "Fixed", "Pis": "Mutable",
}

# Compatible elements (Fire-Air, Earth-Water)
COMPATIBLE_ELEMENTS: dict[str, list[str]] = {
    "Fire": ["Fire", "Air"],
    "Earth": ["Earth", "Water"],
    "Air": ["Air", "Fire"],
    "Water": ["Water", "Earth"],
}

# Moon affinities: same sign (strongest), opposite (complementary), trines (harmony)
# First element is same sign, second is opposite, rest are trines
MOON_AFFINITIES: dict[str, list[str]] = {
    "Ari": ["Ari", "Lib", "Leo", "Sag"],
    "Tau": ["Tau", "Sco", "Vir", "Cap"],
    "Gem": ["Gem", "Sag", "Lib", "Aqu"],
    "Can": ["Can", "Cap", "Sco", "Pis"],
    "Leo": ["Leo", "Aqu", "Ari", "Sag"],
    "Vir": ["Vir", "Pis", "Tau", "Cap"],
    "Lib": ["Lib", "Ari", "Gem", "Aqu"],
    "Sco": ["Sco", "Tau", "Can", "Pis"],
    "Sag": ["Sag", "Gem", "Ari", "Leo"],
    "Cap": ["Cap", "Can", "Tau", "Vir"],
    "Aqu": ["Aqu", "Leo", "Gem", "Lib"],
    "Pis": ["Pis", "Vir", "Can", "Sco"],
}

# Maximum compatibility score with RelationshipScoreFactory + North Node
# Kerykeion RelationshipScoreFactory: up to 48 points (theoretical max with Sun-Moon cross-conjunctions)
# - Destiny Sign: 5 pts (same Sun quality)
# - Sun-Sun (conj/opp/sq, ≤2°): 11 pts
# - Sun1-Moon2 conjunction (≤2°): 11 pts
# - Moon1-Sun2 conjunction (≤2°): 11 pts
# - Moon-Asc: 4 pts each way
# - Sun-Asc: 4 pts each way
# - Venus-Mars: 4 pts each way
# North Node bonus: up to 8 points (Sun: 4, Moon: 4, Venus: 3, capped at 8)
MAX_COMPATIBILITY_SCORE = 56


def calculate_age_range(
    user_age: int,
    user_gender: str | None,
    soulmate_sex: str | None,
) -> tuple[int, int]:
    """
    Calculate soulmate age range based on gender combination.

    Always produces an 8-year range. Rules:
    - Man looking for Woman: use half-plus-seven formula
      - Min = max(18, (his_age / 2) + 7)
      - Max = min + 8
    - Woman looking for Man: inverse (man should be older)
      - Min = max(18, her_age)
      - Max = her_age + 8
    - Same-sex, non-binary, or unknown: ±4 years centered on user age
      - Min = max(18, user_age - 4)
      - Max = user_age + 4

    Args:
        user_age: User's current age
        user_gender: User's gender ("male", "female", "non-binary", or None)
        soulmate_sex: Desired soulmate sex ("male", "female", "non-binary", or None)

    Returns:
        Tuple of (min_age, max_age) for soulmate
    """
    # Handle minors: always return 18+ range
    if user_age < 18:
        return (18, 26)

    # Man looking for Woman: use half-plus-seven formula
    if user_gender == "male" and soulmate_sex == "female":
        min_age = max(18, (user_age // 2) + 7)
        max_age = min_age + 8
        return (min_age, max_age)

    # Woman looking for Man: man should be older (inverse)
    if user_gender == "female" and soulmate_sex == "male":
        min_age = max(18, user_age)
        max_age = user_age + 8
        return (min_age, max_age)

    # Same-sex, non-binary, or unknown: ±4 years centered on user age
    min_age = max(18, user_age - 4)
    max_age = user_age + 4
    return (min_age, max_age)


def score_north_node_contacts(
    user_north_node_sign: str,
    soulmate_sun_sign: str,
    soulmate_moon_sign: str,
    soulmate_venus_sign: str,
) -> int:
    """
    Score North Node contacts - the #1 soulmate indicator in synastry.

    When soulmate's Sun/Moon/Venus conjuncts user's North Node (same sign),
    it indicates a fated, destined connection.

    Args:
        user_north_node_sign: User's North Node sign (abbreviated, e.g., "Leo")
        soulmate_sun_sign: Soulmate's Sun sign
        soulmate_moon_sign: Soulmate's Moon sign
        soulmate_venus_sign: Soulmate's Venus sign

    Returns:
        Score: 0-8 points (capped at 8)
    """
    score = 0

    # Sun conjunct North Node: strong destiny indicator (+4)
    if soulmate_sun_sign == user_north_node_sign:
        score += 4

    # Moon conjunct North Node: emotional destiny (+4)
    if soulmate_moon_sign == user_north_node_sign:
        score += 4

    # Venus conjunct North Node: love destiny (+3)
    if soulmate_venus_sign == user_north_node_sign:
        score += 3

    # Cap at 8 points
    return min(score, 8)


def score_moon_compatibility(user_moon: str, soulmate_moon: str) -> int:
    """
    Score Moon-Moon compatibility.

    Args:
        user_moon: User's Moon sign (abbreviated)
        soulmate_moon: Soulmate's Moon sign (abbreviated)

    Returns:
        Score: 3 (same sign), 2 (opposite/trine), 0 (incompatible)
    """
    affinities = MOON_AFFINITIES.get(user_moon, [])
    if soulmate_moon == user_moon:
        return 3  # Same sign - deep understanding
    if soulmate_moon in affinities[1:]:  # Opposite or trine
        return 2
    return 0


def calculate_aspect_score(pos1: float, pos2: float) -> tuple[int, str | None, float]:
    """
    Calculate aspect score between two planetary positions.

    Uses degree-based aspect calculation to directly optimize for what
    RelationshipScoreFactory measures. This replaces sign-based matching
    which was too coarse (30° range vs 8° orb needed for aspects).

    Args:
        pos1: First planet's absolute position (0-360°)
        pos2: Second planet's absolute position (0-360°)

    Returns:
        Tuple of (score, aspect_name, orb_degrees) where score is:
        - Conjunction (0°): 11 points (≤2° orb, tight), 10 points (2-8° orb)
        - Trine (120°): 8 points (orb 8°)
        - Sextile (60°): 6 points (orb 6°)
        - Opposition (180°): 4 points (orb 8°) - can be challenging
        - Square (90°): 0 points - skip these
        - None: 0 points - no aspect
    """
    diff = abs(pos1 - pos2) % 360
    if diff > 180:
        diff = 360 - diff

    # Conjunction (0°) - strongest aspect, with tight orb bonus
    if diff <= 8:
        score = 11 if diff <= 2 else 10
        return (score, "conjunction", diff)
    # Sextile (60°) - harmonious
    if 54 <= diff <= 66:
        orb = abs(diff - 60)
        return (6, "sextile", orb)
    # Square (90°) - challenging, skip
    if 82 <= diff <= 98:
        orb = abs(diff - 90)
        return (0, "square", orb)
    # Trine (120°) - very harmonious
    if 112 <= diff <= 128:
        orb = abs(diff - 120)
        return (8, "trine", orb)
    # Opposition (180°) - can be complementary
    if 172 <= diff <= 188:
        orb = abs(diff - 180)
        return (4, "opposition", orb)

    return (0, None, diff)


# Scoring constants
RELATIONSHIP_SCORE_BASE = 30  # Kerykeion's "Exceptional" threshold
NORTH_NODE_BONUS_MAX = 8


def score_to_compatibility_percent(score: int) -> int:
    """
    Convert raw compatibility score to percentage using square root curve.

    Uses same approach as synastry: sqrt(score/base) * 100
    Base is 38 (30 Kerykeion base + 8 North Node max) to account for
    soulmate's additional scoring components.

    Square root curve aligns with Kerykeion's qualitative categories:
    - 0-5 (Minimal) → 0-36%
    - 5-10 (Medium) → 36-51%
    - 10-15 (Important) → 51-63%
    - 15-20 (Very Important) → 63-73%
    - 20-30 (Exceptional) → 73-89%
    - 30-38 (Exceptional + North Node) → 89-100%

    Args:
        score: Raw score (can be 0-56 internally)

    Returns:
        Compatibility percentage from 0 to 100
    """
    if score <= 0:
        return 0
    base = RELATIONSHIP_SCORE_BASE + NORTH_NODE_BONUS_MAX  # 38
    return min(100, round(math.sqrt(score / base) * 100))


def recalculate_soulmate_birth_year(
    user_birth_year: int,
    user_gender: str | None,
    soulmate_sex: str | None,
) -> tuple[int, int, int]:
    """
    Recalculate soulmate birth year when gender mismatch occurs.

    Used when user selects same-sex soulmate after background calculation
    predicted opposite-sex (which used different age range formula).

    Args:
        user_birth_year: User's birth year
        user_gender: User's gender (male, female, non-binary)
        soulmate_sex: Desired soulmate sex (male, female, non-binary)

    Returns:
        Tuple of (birth_year, min_age, max_age)
    """
    current_year = datetime.now().year
    user_age = current_year - user_birth_year

    min_age, max_age = calculate_age_range(
        user_age=user_age,
        user_gender=user_gender,
        soulmate_sex=soulmate_sex,
    )

    # Pick middle of range for birth year
    soulmate_age = (min_age + max_age) // 2
    birth_year = current_year - soulmate_age

    return (birth_year, min_age, max_age)


class SoulmateService:
    """
    Application service for generating soulmate natal charts.

    Derives an ideal partner's chart based on user's birth data using
    astrological compatibility principles.
    """

    def __init__(self, provider: IAstrologyProvider):
        """
        Initialize with astrology provider.

        Args:
            provider: Astrology calculation provider (injected dependency)
        """
        self.provider = provider

    def generate_soulmate_chart(
        self,
        user_birth_data: BirthData,
        user_gender: str | None = None,
        soulmate_sex: str | None = None,
    ) -> SoulmateChartResponse:
        """
        Generate a soulmate natal chart based on user's birth data.

        Uses brute-force optimization to find birth dates that maximize
        RelationshipScoreFactory scores. The key insight is that Sun-Moon
        cross-conjunctions (≤2° orb) give 22 pts (11 each way), which alone
        gets us 58% of the way to 95% compatibility.

        Strategy:
        1. Pre-filter ephemeris for Sun-Moon conjunction candidates
        2. For each candidate, build full chart with optimal Ascendant
        3. Score with actual RelationshipScoreFactory + North Node bonus
        4. Return highest scoring candidate

        Args:
            user_birth_data: User's birth information
            user_gender: User's gender for age range calculation (male, female, non-binary)
            soulmate_sex: Desired soulmate sex for age range calculation (male, female, non-binary)

        Returns:
            SoulmateChartResponse with complete soulmate chart data and user placements
        """
        # Calculate user's natal chart
        user_chart = self.provider.calculate_natal_chart(user_birth_data)

        # Extract user's key placements for response
        user_rising_sign = self._get_ascendant_sign(user_chart)
        user_venus_sign = self._get_planet_sign(user_chart, "venus")
        user_mars_sign = self._get_planet_sign(user_chart, "mars")

        # Target rising = opposite of user's rising (for Descendant attraction)
        target_rising = OPPOSITE_SIGNS.get(user_rising_sign, "Lib")

        # Find best birth date using actual RelationshipScoreFactory scoring
        soulmate_birth_data, soulmate_chart, compatibility_score = self._find_best_birth_date(
            user_chart=user_chart,
            user_birth_data=user_birth_data,
            target_rising=target_rising,
            user_gender=user_gender,
            soulmate_sex=soulmate_sex,
        )

        # Build response with compatibility score, user placements, and birth year
        return self._build_response(
            soulmate_chart=soulmate_chart,
            compatibility_score=compatibility_score,
            user_venus_sign=user_venus_sign,
            user_mars_sign=user_mars_sign,
            user_rising_sign=user_rising_sign,
            soulmate_birth_year=soulmate_birth_data.year,
        )

    def _calculate_relationship_score(
        self,
        user_chart: NatalChart,
        soulmate_chart: NatalChart,
    ) -> int:
        """
        Calculate compatibility using Kerykeion's RelationshipScoreFactory + North Node bonus.

        RelationshipScoreFactory evaluates:
        - Sun-Sun aspects
        - Sun-Moon aspects (both directions - key to high scores!)
        - Moon-Ascendant aspects
        - Sun-Ascendant aspects
        - Venus-Mars aspects

        Score ranges (theoretical max 48 with Sun-Moon cross-conjunctions):
        - Minimal: <10
        - Medium: 10-20
        - Important: 20-30
        - Very Important: 30-40
        - Exceptional: 40-48+

        North Node bonus adds 0-8 points for fated connections.

        Args:
            user_chart: User's natal chart (must have provider_data)
            soulmate_chart: Soulmate's natal chart (must have provider_data)

        Returns:
            Total score (0-56 range): RelationshipScoreFactory (0-48) + North Node (0-8)
        """
        base_score = 0

        # Use RelationshipScoreFactory if both charts have Kerykeion subjects
        user_subject = user_chart.provider_data
        soulmate_subject = soulmate_chart.provider_data

        if user_subject and soulmate_subject:
            try:
                score_factory = RelationshipScoreFactory(user_subject, soulmate_subject)
                result = score_factory.get_relationship_score()
                base_score = result.score_value
            except Exception:
                # Fallback to sign-based scoring if RelationshipScoreFactory fails
                base_score = self._fallback_relationship_score(user_chart, soulmate_chart)
        else:
            base_score = self._fallback_relationship_score(user_chart, soulmate_chart)

        # Cap base score at 48 (theoretical max with Sun-Moon cross-conjunctions)
        base_score = min(base_score, 48)

        # Add North Node bonus (not included in RelationshipScoreFactory)
        user_north_node = self._get_user_north_node(user_chart)
        soulmate_sun = self._get_planet_sign(soulmate_chart, "sun")
        soulmate_moon = self._get_planet_sign(soulmate_chart, "moon")
        soulmate_venus = self._get_planet_sign(soulmate_chart, "venus")

        north_node_bonus = score_north_node_contacts(
            user_north_node_sign=user_north_node,
            soulmate_sun_sign=soulmate_sun,
            soulmate_moon_sign=soulmate_moon,
            soulmate_venus_sign=soulmate_venus,
        )

        # Total capped at MAX_COMPATIBILITY_SCORE (38) for percentage calculation
        return min(base_score + north_node_bonus, MAX_COMPATIBILITY_SCORE)

    def _fallback_relationship_score(
        self,
        user_chart: NatalChart,
        soulmate_chart: NatalChart,
    ) -> int:
        """
        Fallback scoring when RelationshipScoreFactory is unavailable.

        Uses sign-based element compatibility checks (similar to old scoring).
        Returns score in 0-20 range to approximate RelationshipScoreFactory scale.
        """
        score = 0

        # Extract signs
        user_sun = self._get_planet_sign(user_chart, "sun")
        user_moon = self._get_planet_sign(user_chart, "moon")
        soulmate_sun = self._get_planet_sign(soulmate_chart, "sun")
        soulmate_moon = self._get_planet_sign(soulmate_chart, "moon")
        soulmate_venus = self._get_planet_sign(soulmate_chart, "venus")
        soulmate_mars = self._get_planet_sign(soulmate_chart, "mars")

        # Sun-Sun trine/sextile (+5)
        user_sun_element = ELEMENT_MAP.get(user_sun, "Fire")
        soulmate_sun_element = ELEMENT_MAP.get(soulmate_sun, "Fire")
        if soulmate_sun_element in COMPATIBLE_ELEMENTS.get(user_sun_element, []):
            score += 5

        # Moon compatibility (+5)
        score += score_moon_compatibility(user_moon, soulmate_moon)

        # Venus-Mars chemistry (+5)
        user_venus = self._get_planet_sign(user_chart, "venus")
        user_mars = self._get_planet_sign(user_chart, "mars")
        user_mars_element = ELEMENT_MAP.get(user_mars, "Fire")
        soulmate_venus_element = ELEMENT_MAP.get(soulmate_venus, "Fire")
        if soulmate_venus_element in COMPATIBLE_ELEMENTS.get(user_mars_element, []):
            score += 3

        user_venus_element = ELEMENT_MAP.get(user_venus, "Fire")
        soulmate_mars_element = ELEMENT_MAP.get(soulmate_mars, "Fire")
        if soulmate_mars_element in COMPATIBLE_ELEMENTS.get(user_venus_element, []):
            score += 2

        return score

    def _get_planet_sign(self, chart: NatalChart, planet_key: str) -> str:
        """Extract planet sign from chart (abbreviated format)."""
        planet_data = chart.planets.get(planet_key, {})
        return planet_data.get("sign", "Ari")

    def _get_ascendant_sign(self, chart: NatalChart) -> str:
        """Extract ascendant sign from chart (abbreviated format)."""
        ascendant = chart.points.get("ascendant", {})
        return ascendant.get("sign", "Ari")

    def _find_best_birth_date(
        self,
        user_chart: NatalChart,
        user_birth_data: BirthData,
        target_rising: str,
        user_gender: str | None = None,
        soulmate_sex: str | None = None,
    ) -> tuple[BirthData, NatalChart, int]:
        """
        Find birth date that maximizes RelationshipScoreFactory score.

        This is the core algorithm that replaces sign-based derivation with
        brute-force optimization. The key insight is that Sun-Moon cross-
        conjunctions (≤2° orb) give 22 pts (11 each way), which alone
        gets us 58% of the way to 95% compatibility.

        Strategy:
        1. Calculate age range based on gender combination
        2. Generate ephemeris for entire date range
        3. Pre-filter for Sun-Moon conjunction candidates (within 10°)
        4. Build full chart for each candidate (with target Ascendant)
        5. Score with actual RelationshipScoreFactory + North Node bonus
        6. Return highest scoring candidate

        Args:
            user_chart: User's natal chart with planetary positions
            user_birth_data: User's birth data (for location reference)
            target_rising: Target Ascendant sign (opposite of user's rising)
            user_gender: User's gender for age range calculation
            soulmate_sex: Desired soulmate sex for age range calculation

        Returns:
            Tuple of (BirthData, NatalChart, score) for highest scoring candidate
        """
        # Calculate age range based on gender combination
        current_year = datetime.now().year
        user_age = current_year - user_birth_data.year
        min_soulmate_age, max_soulmate_age = calculate_age_range(
            user_age=user_age,
            user_gender=user_gender,
            soulmate_sex=soulmate_sex,
        )

        # Convert to birth years (younger soulmate = higher birth year)
        max_birth_year = current_year - min_soulmate_age
        min_birth_year = current_year - max_soulmate_age

        # Extract user positions for pre-filtering
        user_sun_pos = user_chart.planets.get("sun", {}).get("abs_pos", 0.0)
        user_moon_pos = user_chart.planets.get("moon", {}).get("abs_pos", 0.0)

        # Generate ephemeris for entire search range
        if isinstance(self.provider, KerykeionProvider):
            ephemeris_points = self.provider.generate_ephemeris_for_range(
                start_date=date(min_birth_year, 1, 1),
                end_date=date(max_birth_year, 12, 31),
                location=user_birth_data,
            )
        else:
            ephemeris_points = []

        # Pre-filter for Sun-Moon conjunction candidates
        # We want dates where:
        #   - Soulmate Sun is within 10° of user Moon, OR
        #   - Soulmate Moon is within 10° of user Sun
        # This gives the best chance of hitting 11-point cross-conjunctions
        candidates = []
        for point in ephemeris_points:
            sm_sun_pos = point.sun.abs_pos
            sm_moon_pos = point.moon.abs_pos

            # Check Sun-Moon conjunction potential (within 10°)
            sun_moon_diff = abs(sm_sun_pos - user_moon_pos) % 360
            if sun_moon_diff > 180:
                sun_moon_diff = 360 - sun_moon_diff

            moon_sun_diff = abs(sm_moon_pos - user_sun_pos) % 360
            if moon_sun_diff > 180:
                moon_sun_diff = 360 - moon_sun_diff

            # Prioritize tight conjunctions, but include wider candidates too
            # Score by how close we are to perfect conjunction
            conjunction_score = 0
            if sun_moon_diff <= 10:
                conjunction_score += 20 - sun_moon_diff  # 10-20 points
            if moon_sun_diff <= 10:
                conjunction_score += 20 - moon_sun_diff  # 10-20 points

            # Also include dates with good Sun-Sun aspects (same modality = Destiny Sign)
            user_sun_sign = user_chart.planets.get("sun", {}).get("sign", "Ari")
            user_sun_quality = SUN_QUALITY.get(user_sun_sign, "Fixed")
            point_sun_quality = SUN_QUALITY.get(point.sun.sign, "Fixed")
            if point_sun_quality == user_sun_quality:
                conjunction_score += 5  # Destiny Sign bonus

            if conjunction_score > 0:
                candidates.append((conjunction_score, point))

        # Sort by pre-score descending, take top 100 candidates
        candidates.sort(key=lambda x: -x[0])
        top_candidates = candidates[:100]

        # If no good candidates, include all ephemeris points (O(n) with set)
        if len(top_candidates) < 50:
            existing_ids = {id(p) for _, p in top_candidates}
            for point in ephemeris_points:
                if id(point) not in existing_ids:
                    top_candidates.append((0, point))
                    if len(top_candidates) >= 100:
                        break

        # Score each candidate with actual RelationshipScoreFactory
        best_birth_data = None
        best_chart = None
        best_score = -1

        for _, point in top_candidates:
            # Find hour that produces target Ascendant
            target_hour, target_minute = self._find_hour_for_ascendant_fast(
                point.year,
                point.month,
                point.day,
                target_rising,
                user_birth_data.latitude,
                user_birth_data.longitude,
                user_birth_data.timezone,
            )

            # Build birth data and chart
            birth_data = BirthData(
                year=point.year,
                month=point.month,
                day=point.day,
                hour=target_hour,
                minute=target_minute,
                latitude=user_birth_data.latitude,
                longitude=user_birth_data.longitude,
                timezone=user_birth_data.timezone,
            )
            soulmate_chart = self.provider.calculate_natal_chart(birth_data)

            # Score with actual RelationshipScoreFactory + North Node
            score = self._calculate_relationship_score(user_chart, soulmate_chart)

            if score > best_score:
                best_score = score
                best_birth_data = birth_data
                best_chart = soulmate_chart

            # Early termination if we found a perfect score
            if score >= 38:  # 38 = 100% compatibility
                break

        # Fallback if no valid candidates found
        if best_birth_data is None:
            fallback_year = (min_birth_year + max_birth_year) // 2
            target_hour, target_minute = self._find_hour_for_ascendant_fast(
                fallback_year, 6, 15, target_rising,
                user_birth_data.latitude,
                user_birth_data.longitude,
                user_birth_data.timezone,
            )
            best_birth_data = BirthData(
                year=fallback_year,
                month=6,
                day=15,
                hour=target_hour,
                minute=target_minute,
                latitude=user_birth_data.latitude,
                longitude=user_birth_data.longitude,
                timezone=user_birth_data.timezone,
            )
            best_chart = self.provider.calculate_natal_chart(best_birth_data)
            best_score = self._calculate_relationship_score(user_chart, best_chart)

        return (best_birth_data, best_chart, best_score)

    def _get_user_north_node(self, user_chart: NatalChart) -> str:
        """Extract user's North Node sign from chart."""
        # North Node is stored in planets dict as "true_node" or in points
        north_node = user_chart.planets.get("true_node", {})
        if not north_node:
            north_node = user_chart.points.get("true_node", {})
        return north_node.get("sign", "Leo")

    def _get_user_north_node_pos(self, user_chart: NatalChart | None) -> float:
        """Extract user's North Node absolute position from chart."""
        if not user_chart:
            return 0.0
        # North Node is stored in planets dict as "true_node" or in points
        north_node = user_chart.planets.get("true_node", {})
        if not north_node:
            north_node = user_chart.points.get("true_node", {})
        return north_node.get("abs_pos", 0.0)

    def _find_hour_for_ascendant_fast(
        self,
        year: int,
        month: int,
        day: int,
        target_rising_sign: str,
        latitude: float,
        longitude: float,
        timezone: str,
    ) -> tuple[int, int]:
        """Find birth time for target Ascendant using math, not brute force.

        The Ascendant moves ~1° every 4 minutes (360°/24h = 15°/hour).
        We calculate the time mathematically instead of iterating through
        96 chart calculations.

        Algorithm:
        1. Calculate Ascendant at midnight (1 chart calculation)
        2. Mathematically compute when target sign's center rises
        3. Verify with 1 chart calculation, optionally refine

        Result: 96 chart calculations → 2-3 per candidate = ~40x speedup

        Args:
            year: Birth year
            month: Birth month
            day: Birth day
            target_rising_sign: Target Ascendant sign (abbreviated, e.g., "Aqu")
            latitude: Birth latitude
            longitude: Birth longitude
            timezone: Birth timezone

        Returns:
            Tuple of (hour, minute) that produces the target Ascendant sign
        """
        # Get target sign's center degree (0-360)
        sign_idx = ZODIAC_SIGNS.index(target_rising_sign) if target_rising_sign in ZODIAC_SIGNS else 6
        target_center = sign_idx * 30 + 15

        # Get midnight Ascendant as reference (1 chart calculation)
        midnight_birth = BirthData(
            year=year,
            month=month,
            day=day,
            hour=0,
            minute=0,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone,
        )
        try:
            midnight_chart = self.provider.calculate_natal_chart(midnight_birth)
            midnight_asc = midnight_chart.points.get("ascendant", {}).get("abs_pos", 0.0)
        except Exception:
            return (12, 0)  # Fallback to noon

        # Calculate time mathematically: Ascendant moves 1° every 4 minutes
        degrees_to_rotate = (target_center - midnight_asc) % 360
        minutes_from_midnight = int(degrees_to_rotate * 4)
        est_hour = (minutes_from_midnight // 60) % 24
        est_minute = minutes_from_midnight % 60

        # Verify with actual chart (1 chart calculation)
        verify_birth = BirthData(
            year=year,
            month=month,
            day=day,
            hour=est_hour,
            minute=est_minute,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone,
        )
        try:
            chart = self.provider.calculate_natal_chart(verify_birth)
            actual_sign = chart.points.get("ascendant", {}).get("sign", "")
            if actual_sign == target_rising_sign:
                return (est_hour, est_minute)

            # Refine if sign mismatch (1 more chart calculation)
            actual_asc = chart.points.get("ascendant", {}).get("abs_pos", 0.0)
            error_degrees = (target_center - actual_asc) % 360
            if error_degrees > 180:
                error_degrees = error_degrees - 360
            correction_minutes = int(error_degrees * 4)
            refined_total = (est_hour * 60 + est_minute + correction_minutes) % 1440
            return (refined_total // 60, refined_total % 60)
        except Exception:
            return (est_hour, est_minute)

    def _find_hour_for_ascendant(
        self,
        year: int,
        month: int,
        day: int,
        target_rising_sign: str,
        latitude: float,
        longitude: float,
        timezone: str,
    ) -> tuple[int, int]:
        """Find birth time that produces target Ascendant sign.

        DEPRECATED: Kept for testing/comparison. Use _find_hour_for_ascendant_fast().

        Searches 24 hours with 15-minute resolution (~96 checks).
        Returns (hour, minute) tuple.

        Args:
            year: Birth year
            month: Birth month
            day: Birth day
            target_rising_sign: Target Ascendant sign (abbreviated, e.g., "Aqu")
            latitude: Birth latitude
            longitude: Birth longitude
            timezone: Birth timezone

        Returns:
            Tuple of (hour, minute) that produces the target Ascendant sign
        """
        sign_idx = ZODIAC_SIGNS.index(target_rising_sign) if target_rising_sign in ZODIAC_SIGNS else 6
        target_center = sign_idx * 30 + 15  # Middle of sign

        best_hour, best_minute = 12, 0
        best_error = 360.0

        for hour in range(24):
            for minute in range(0, 60, 15):
                birth = BirthData(
                    year=year,
                    month=month,
                    day=day,
                    hour=hour,
                    minute=minute,
                    latitude=latitude,
                    longitude=longitude,
                    timezone=timezone,
                )
                try:
                    chart = self.provider.calculate_natal_chart(birth)
                except Exception:
                    # Skip times that hit DST transitions or other timezone issues
                    continue

                actual_asc = chart.points.get("ascendant", {}).get("abs_pos", 0.0)

                error = abs(target_center - actual_asc)
                if error > 180:
                    error = 360 - error

                if error < best_error:
                    best_error = error
                    best_hour, best_minute = hour, minute

        return (best_hour, best_minute)

    def _build_response(
        self,
        soulmate_chart: NatalChart,
        compatibility_score: int,
        user_venus_sign: str,
        user_mars_sign: str,
        user_rising_sign: str,
        soulmate_birth_year: int,
    ) -> SoulmateChartResponse:
        """Build response from natal chart domain model.

        Args:
            soulmate_chart: The calculated soulmate natal chart
            compatibility_score: Score from 0-56 (RelationshipScoreFactory + North Node)
            user_venus_sign: User's Venus sign for physical feature derivation
            user_mars_sign: User's Mars sign for physical feature derivation
            user_rising_sign: User's Rising sign for physical feature derivation
            soulmate_birth_year: Soulmate's birth year for age calculation

        Returns:
            SoulmateChartResponse with compatibility_percent (0-100), user placements, and birth year
        """
        # Extract planets (excluding birth_data if present)
        planets: dict[str, Any] = {}
        for key, value in soulmate_chart.planets.items():
            if key != "birth_data" and isinstance(value, dict):
                planets[key] = value

        # Use new percentage calculation (75-99 range)
        compatibility_percent = score_to_compatibility_percent(compatibility_score)

        return SoulmateChartResponse(
            planets=planets,
            houses=soulmate_chart.houses,
            points=soulmate_chart.points,
            aspects=soulmate_chart.aspects,
            compatibility_percent=compatibility_percent,
            user_venus_sign=user_venus_sign,
            user_mars_sign=user_mars_sign,
            user_rising_sign=user_rising_sign,
            soulmate_birth_year=soulmate_birth_year,
        )

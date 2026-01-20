"""Analyze how many 95%+ scoring soulmate candidates exist for each test user."""

from dataclasses import dataclass
from datetime import date, datetime

from app.application.soulmate_service import (
    SUN_QUALITY,
    ZODIAC_SIGNS,
    SoulmateService,
    calculate_aspect_score,
)
from app.config.astrology_presets import DetailLevel, get_preset
from app.domain.models import BirthData
from app.infrastructure.providers.kerykeion_provider import KerykeionProvider


@dataclass
class UserProfile:
    """User profile for compatibility testing."""

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
    UserProfile("Aries User", "Ari", 1990, 4, 10, 10, 0, 40.73, -73.93, "America/New_York"),
    UserProfile("Taurus User", "Tau", 1988, 5, 15, 14, 30, 51.5, -0.1, "Europe/London"),
    UserProfile("Gemini User", "Gem", 1990, 6, 15, 14, 30, 51.5, -0.1, "Europe/London"),
    UserProfile("Cancer User", "Can", 1995, 7, 5, 8, 0, 35.68, 139.77, "Asia/Tokyo"),
    UserProfile("Leo User", "Leo", 1992, 8, 10, 16, 45, -33.87, 151.21, "Australia/Sydney"),
    UserProfile("Virgo User", "Vir", 1985, 9, 10, 12, 0, 64.15, -21.94, "Atlantic/Reykjavik"),
    UserProfile("Libra User", "Lib", 1991, 10, 15, 20, 0, 52.52, 13.40, "Europe/Berlin"),
    UserProfile("Scorpio User", "Sco", 1987, 11, 8, 10, 30, 55.75, 37.62, "Europe/Moscow"),
    UserProfile("Sagittarius User", "Sag", 1993, 12, 5, 11, 0, 34.05, -118.24, "America/Los_Angeles"),
    UserProfile("Capricorn User", "Cap", 1970, 1, 10, 6, 0, 51.5, -0.1, "Europe/London"),
    UserProfile("Aquarius User", "Aqu", 2004, 2, 14, 15, 0, 40.73, -73.93, "America/New_York"),
    UserProfile("Pisces User", "Pis", 1995, 3, 1, 8, 45, 35.68, 139.77, "Asia/Tokyo"),
    UserProfile("Novosibirsk 5am User", "Vir", 2001, 9, 5, 5, 0, 55.03, 82.92, "Asia/Novosibirsk"),
    UserProfile("Novosibirsk 12pm User", "Vir", 2001, 9, 5, 12, 0, 55.03, 82.92, "Asia/Novosibirsk"),
]


def _create_birth_data(user: UserProfile) -> BirthData:
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


def score_ephemeris_point_simple(
    point,
    user_sun_pos: float,
    user_moon_pos: float,
    user_venus_pos: float,
    user_mars_pos: float,
    user_ascendant_pos: float,
    user_north_node_pos: float,
    user_north_node_sign: str,
    user_sun_quality: str,
    target_rising: str,
) -> int:
    """Score ephemeris point (simplified version for analysis)."""
    score = 0

    # 1. Destiny Sign: 5 pts
    point_sun_quality = SUN_QUALITY.get(point.sun.sign, "Fixed")
    if point_sun_quality == user_sun_quality:
        score += 5

    # 2. Sun-Sun aspect
    _, sun_sun_aspect, sun_sun_orb = calculate_aspect_score(point.sun.abs_pos, user_sun_pos)
    if sun_sun_aspect in ("conjunction", "opposition", "square"):
        score += 11 if sun_sun_orb <= 2 else 8
    elif sun_sun_aspect in ("trine", "sextile"):
        score += 4

    # 3. Sun-Moon cross aspects - THE KEY!
    _, sun_moon_aspect, sun_moon_orb = calculate_aspect_score(point.sun.abs_pos, user_moon_pos)
    if sun_moon_aspect == "conjunction":
        score += 11 if sun_moon_orb <= 2 else 8
    elif sun_moon_aspect:
        score += 4

    _, moon_sun_aspect, moon_sun_orb = calculate_aspect_score(point.moon.abs_pos, user_sun_pos)
    if moon_sun_aspect == "conjunction":
        score += 11 if moon_sun_orb <= 2 else 8
    elif moon_sun_aspect:
        score += 4

    # 4. Sun-Ascendant: 4 pts each way
    _, sun_asc_aspect, _ = calculate_aspect_score(point.sun.abs_pos, user_ascendant_pos)
    if sun_asc_aspect:
        score += 4

    # 5. Moon-Ascendant
    _, moon_asc_aspect, _ = calculate_aspect_score(point.moon.abs_pos, user_ascendant_pos)
    if moon_asc_aspect:
        score += 4

    # Bidirectional Asc scoring
    target_rising_index = ZODIAC_SIGNS.index(target_rising) if target_rising in ZODIAC_SIGNS else 6
    estimated_soulmate_asc_pos = (target_rising_index * 30) + 15

    _, user_sun_sm_asc_aspect, _ = calculate_aspect_score(user_sun_pos, estimated_soulmate_asc_pos)
    if user_sun_sm_asc_aspect:
        score += 4

    _, user_moon_sm_asc_aspect, _ = calculate_aspect_score(user_moon_pos, estimated_soulmate_asc_pos)
    if user_moon_sm_asc_aspect:
        score += 4

    # 6. Venus-Mars: 4 pts each way
    _, venus_mars_aspect, _ = calculate_aspect_score(point.venus.abs_pos, user_mars_pos)
    if venus_mars_aspect:
        score += 4

    _, mars_venus_aspect, _ = calculate_aspect_score(point.mars.abs_pos, user_venus_pos)
    if mars_venus_aspect:
        score += 4

    # North Node bonus (capped at 8)
    nn_bonus = 0
    _, sun_nn_aspect, _ = calculate_aspect_score(point.sun.abs_pos, user_north_node_pos)
    if sun_nn_aspect == "conjunction":
        nn_bonus += 4

    _, moon_nn_aspect, _ = calculate_aspect_score(point.moon.abs_pos, user_north_node_pos)
    if moon_nn_aspect == "conjunction":
        nn_bonus += 4

    _, venus_nn_aspect, _ = calculate_aspect_score(point.venus.abs_pos, user_north_node_pos)
    if venus_nn_aspect == "conjunction":
        nn_bonus += 3

    score += min(nn_bonus, 8)

    return score


def analyze_user(user: UserProfile, provider: KerykeionProvider, service: SoulmateService):
    """Analyze how many 95%+ candidates exist for a user."""
    birth_data = _create_birth_data(user)
    user_chart = provider.calculate_natal_chart(birth_data)

    # Calculate age range
    current_year = datetime.now().year
    user_age = current_year - user.year

    max_soulmate_age = user_age + 10
    min_soulmate_age = 18 if user_age < 28 else max(18, user_age - 10)

    max_birth_year = current_year - min_soulmate_age
    min_birth_year = current_year - max_soulmate_age

    # Extract user positions
    user_sun_pos = user_chart.planets.get("sun", {}).get("abs_pos", 0.0)
    user_moon_pos = user_chart.planets.get("moon", {}).get("abs_pos", 0.0)
    user_venus_pos = user_chart.planets.get("venus", {}).get("abs_pos", 0.0)
    user_mars_pos = user_chart.planets.get("mars", {}).get("abs_pos", 0.0)
    user_ascendant_pos = user_chart.points.get("ascendant", {}).get("abs_pos", 0.0)
    user_sun_sign = user_chart.planets.get("sun", {}).get("sign", "Ari")
    user_sun_quality = SUN_QUALITY.get(user_sun_sign, "Fixed")
    user_rising_sign = user_chart.points.get("ascendant", {}).get("sign", "Ari")
    target_rising = {
        "Ari": "Lib", "Tau": "Sco", "Gem": "Sag", "Can": "Cap",
        "Leo": "Aqu", "Vir": "Pis", "Lib": "Ari", "Sco": "Tau",
        "Sag": "Gem", "Cap": "Can", "Aqu": "Leo", "Pis": "Vir",
    }.get(user_rising_sign, "Lib")

    # Get North Node
    north_node = user_chart.planets.get("true_node", {})
    if not north_node:
        north_node = user_chart.points.get("true_node", {})
    user_north_node_sign = north_node.get("sign", "Leo")
    user_north_node_pos = north_node.get("abs_pos", 0.0)

    # Generate ephemeris
    ephemeris_points = provider.generate_ephemeris_for_range(
        start_date=date(min_birth_year, 1, 1),
        end_date=date(max_birth_year, 12, 31),
        location=birth_data,
    )

    # Score all candidates
    matches_95_plus = []
    score_distribution = {}

    for point in ephemeris_points:
        score = score_ephemeris_point_simple(
            point=point,
            user_sun_pos=user_sun_pos,
            user_moon_pos=user_moon_pos,
            user_venus_pos=user_venus_pos,
            user_mars_pos=user_mars_pos,
            user_ascendant_pos=user_ascendant_pos,
            user_north_node_pos=user_north_node_pos,
            user_north_node_sign=user_north_node_sign,
            user_sun_quality=user_sun_quality,
            target_rising=target_rising,
        )

        # Track distribution
        bucket = (score // 5) * 5
        score_distribution[bucket] = score_distribution.get(bucket, 0) + 1

        # 95% = score >= 36 (since 36/38 = 94.7% rounds to 95%)
        if score >= 36:
            age_gap = point.year - user.year
            matches_95_plus.append({
                "date": f"{point.year}-{point.month:02d}-{point.day:02d}",
                "score": score,
                "percent": round(min(score, 38) / 38 * 100),
                "age_gap": age_gap,
            })

    return {
        "user": user.name,
        "user_age": user_age,
        "search_range": f"{min_birth_year}-{max_birth_year}",
        "age_range": f"-{user_age - (current_year - max_birth_year)} to +{(current_year - min_birth_year) - user_age}",
        "total_candidates": len(ephemeris_points),
        "matches_95_plus": len(matches_95_plus),
        "score_distribution": dict(sorted(score_distribution.items())),
        "top_matches": sorted(matches_95_plus, key=lambda x: -x["score"])[:10],
    }


def main():
    config = get_preset(DetailLevel.CORE)
    provider = KerykeionProvider(config)
    service = SoulmateService(provider=provider)

    print("=" * 80)
    print("SOULMATE 95%+ MATCH ANALYSIS")
    print("=" * 80)
    print()

    for user in TEST_USERS:
        print(f"Analyzing {user.name}...")
        result = analyze_user(user, provider, service)

        print(f"\n{'=' * 60}")
        print(f"USER: {result['user']}")
        print(f"{'=' * 60}")
        print(f"User Age: {result['user_age']}")
        print(f"Search Range: {result['search_range']} (years)")
        print(f"Age Gap Range: {result['age_range']} years")
        print(f"Total Candidates Evaluated: {result['total_candidates']}")
        print(f"95%+ Matches Found: {result['matches_95_plus']}")
        print()

        print("Score Distribution:")
        for bucket, count in result["score_distribution"].items():
            pct = round(min(bucket, 38) / 38 * 100) if bucket > 0 else 0
            bar = "█" * (count // 50) if count >= 50 else "▪" if count > 0 else ""
            print(f"  {bucket:2d}-{bucket+4:2d} pts ({pct:3d}%+): {count:5d} {bar}")

        if result["top_matches"]:
            print()
            print("Top 10 Matches (95%+):")
            for i, match in enumerate(result["top_matches"], 1):
                gap_str = f"+{match['age_gap']}" if match["age_gap"] >= 0 else str(match["age_gap"])
                print(f"  {i:2d}. {match['date']} - Score: {match['score']} ({match['percent']}%) - Age gap: {gap_str} years")
        else:
            print("\n  No 95%+ matches found in search range!")

        print()

    # Summary table
    print("\n" + "=" * 80)
    print("SUMMARY TABLE")
    print("=" * 80)
    print(f"{'User':<25} {'Age':<5} {'Range':<12} {'Total':<8} {'95%+':<8} {'Best Age Gaps':<20}")
    print("-" * 80)

    for user in TEST_USERS:
        result = analyze_user(user, provider, service)
        age_gaps = sorted(set(m["age_gap"] for m in result["top_matches"][:5])) if result["top_matches"] else []
        gap_str = ", ".join(f"{g:+d}" for g in age_gaps[:5]) if age_gaps else "N/A"
        print(f"{result['user']:<25} {result['user_age']:<5} {result['age_range']:<12} {result['total_candidates']:<8} {result['matches_95_plus']:<8} {gap_str:<20}")


if __name__ == "__main__":
    main()

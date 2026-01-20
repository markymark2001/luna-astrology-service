"""Analyze 95%+ matches at different age windows to find optimal approach."""

from dataclasses import dataclass
from datetime import date, datetime

from app.application.soulmate_service import (
    SUN_QUALITY,
    ZODIAC_SIGNS,
    calculate_aspect_score,
)
from app.config.astrology_presets import DetailLevel, get_preset
from app.domain.models import BirthData
from app.infrastructure.providers.kerykeion_provider import KerykeionProvider


@dataclass
class UserProfile:
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
    UserProfile("Novosibirsk 5am", "Vir", 2001, 9, 5, 5, 0, 55.03, 82.92, "Asia/Novosibirsk"),
    UserProfile("Novosibirsk 12pm", "Vir", 2001, 9, 5, 12, 0, 55.03, 82.92, "Asia/Novosibirsk"),
]


def _create_birth_data(user: UserProfile) -> BirthData:
    return BirthData(
        year=user.year, month=user.month, day=user.day,
        hour=user.hour, minute=user.minute,
        latitude=user.latitude, longitude=user.longitude, timezone=user.timezone,
    )


def score_point(point, user_sun_pos, user_moon_pos, user_venus_pos, user_mars_pos,
                user_ascendant_pos, user_north_node_pos, user_sun_quality, target_rising) -> int:
    """Score ephemeris point."""
    score = 0

    # Destiny Sign
    if SUN_QUALITY.get(point.sun.sign, "Fixed") == user_sun_quality:
        score += 5

    # Sun-Sun
    _, asp, orb = calculate_aspect_score(point.sun.abs_pos, user_sun_pos)
    if asp in ("conjunction", "opposition", "square"):
        score += 11 if orb <= 2 else 8
    elif asp in ("trine", "sextile"):
        score += 4

    # Sun-Moon cross (KEY)
    _, asp, orb = calculate_aspect_score(point.sun.abs_pos, user_moon_pos)
    if asp == "conjunction":
        score += 11 if orb <= 2 else 8
    elif asp:
        score += 4

    _, asp, orb = calculate_aspect_score(point.moon.abs_pos, user_sun_pos)
    if asp == "conjunction":
        score += 11 if orb <= 2 else 8
    elif asp:
        score += 4

    # Sun-Asc, Moon-Asc
    _, asp, _ = calculate_aspect_score(point.sun.abs_pos, user_ascendant_pos)
    if asp:
        score += 4
    _, asp, _ = calculate_aspect_score(point.moon.abs_pos, user_ascendant_pos)
    if asp:
        score += 4

    # Bidirectional Asc
    target_idx = ZODIAC_SIGNS.index(target_rising) if target_rising in ZODIAC_SIGNS else 6
    est_asc = (target_idx * 30) + 15
    _, asp, _ = calculate_aspect_score(user_sun_pos, est_asc)
    if asp:
        score += 4
    _, asp, _ = calculate_aspect_score(user_moon_pos, est_asc)
    if asp:
        score += 4

    # Venus-Mars
    _, asp, _ = calculate_aspect_score(point.venus.abs_pos, user_mars_pos)
    if asp:
        score += 4
    _, asp, _ = calculate_aspect_score(point.mars.abs_pos, user_venus_pos)
    if asp:
        score += 4

    # North Node bonus (capped at 8)
    nn = 0
    _, asp, _ = calculate_aspect_score(point.sun.abs_pos, user_north_node_pos)
    if asp == "conjunction":
        nn += 4
    _, asp, _ = calculate_aspect_score(point.moon.abs_pos, user_north_node_pos)
    if asp == "conjunction":
        nn += 4
    _, asp, _ = calculate_aspect_score(point.venus.abs_pos, user_north_node_pos)
    if asp == "conjunction":
        nn += 3
    score += min(nn, 8)

    return score


def analyze_user_by_age_window(user: UserProfile, provider: KerykeionProvider):
    """Analyze matches at different age windows."""
    birth_data = _create_birth_data(user)
    user_chart = provider.calculate_natal_chart(birth_data)
    current_year = datetime.now().year
    user_age = current_year - user.year

    # Full search range (respecting 18+ constraint)
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
    user_rising = user_chart.points.get("ascendant", {}).get("sign", "Ari")
    target_rising = {"Ari": "Lib", "Tau": "Sco", "Gem": "Sag", "Can": "Cap",
                     "Leo": "Aqu", "Vir": "Pis", "Lib": "Ari", "Sco": "Tau",
                     "Sag": "Gem", "Cap": "Can", "Aqu": "Leo", "Pis": "Vir"}.get(user_rising, "Lib")

    nn = user_chart.planets.get("true_node", {}) or user_chart.points.get("true_node", {})
    user_north_node_pos = nn.get("abs_pos", 0.0)

    # Generate full ephemeris
    ephemeris = provider.generate_ephemeris_for_range(
        start_date=date(min_birth_year, 1, 1),
        end_date=date(max_birth_year, 12, 31),
        location=birth_data,
    )

    # Score all and track by age gap
    all_matches = []
    for point in ephemeris:
        score = score_point(point, user_sun_pos, user_moon_pos, user_venus_pos, user_mars_pos,
                           user_ascendant_pos, user_north_node_pos, user_sun_quality, target_rising)
        age_gap = point.year - user.year
        all_matches.append({"score": score, "age_gap": age_gap, "date": f"{point.year}-{point.month:02d}-{point.day:02d}"})

    # Analyze different windows
    windows = [2, 3, 4, 5, 6, 7, 10]
    thresholds = [36, 34, 32, 30, 28]  # 95%, 89%, 84%, 79%, 74%

    results = {}
    for window in windows:
        filtered = [m for m in all_matches if abs(m["age_gap"]) <= window]
        results[window] = {
            "total": len(filtered),
            "best_score": max((m["score"] for m in filtered), default=0),
            "best_match": max(filtered, key=lambda x: x["score"], default=None),
        }
        for thresh in thresholds:
            pct = round(min(thresh, 38) / 38 * 100)
            count = len([m for m in filtered if m["score"] >= thresh])
            results[window][f"count_{pct}pct"] = count

    return {
        "user": user.name,
        "user_age": user_age,
        "results": results,
    }


def main():
    config = get_preset(DetailLevel.CORE)
    provider = KerykeionProvider(config)

    print("=" * 100)
    print("AGE WINDOW ANALYSIS: How many 95%+/90%+/85%+/80%+ matches exist at different age windows?")
    print("=" * 100)
    print()

    # Header
    print(f"{'User':<20} {'Age':<4} | {'±2yr':<12} | {'±3yr':<12} | {'±4yr':<12} | {'±5yr':<12} | {'±7yr':<12} | {'±10yr':<12}")
    print(f"{'':<20} {'':<4} | {'95/90/85/80':<12} | {'95/90/85/80':<12} | {'95/90/85/80':<12} | {'95/90/85/80':<12} | {'95/90/85/80':<12} | {'95/90/85/80':<12}")
    print("-" * 100)

    all_results = []
    for user in TEST_USERS:
        print(f"Analyzing {user.name}...", end="\r")
        result = analyze_user_by_age_window(user, provider)
        all_results.append(result)

        r = result["results"]
        row = f"{result['user']:<20} {result['user_age']:<4} |"
        for w in [2, 3, 4, 5, 7, 10]:
            c95 = r[w].get("count_95pct", 0)
            c89 = r[w].get("count_89pct", 0)
            c84 = r[w].get("count_84pct", 0)
            c79 = r[w].get("count_79pct", 0)
            row += f" {c95:>2}/{c89:>2}/{c84:>2}/{c79:>2} |"
        print(row)

    # Best match analysis per window
    print()
    print("=" * 100)
    print("BEST MATCH SCORE per age window (score / percent)")
    print("=" * 100)
    print(f"{'User':<20} | {'±2yr':<10} | {'±3yr':<10} | {'±4yr':<10} | {'±5yr':<10} | {'±7yr':<10} | {'±10yr':<10}")
    print("-" * 100)

    for result in all_results:
        r = result["results"]
        row = f"{result['user']:<20} |"
        for w in [2, 3, 4, 5, 7, 10]:
            best = r[w]["best_score"]
            pct = round(min(best, 38) / 38 * 100)
            row += f" {best:>2} ({pct:>3}%) |"
        print(row)

    # Summary: How many users can get 95%+ at each window?
    print()
    print("=" * 100)
    print("SUMMARY: Users with at least one 95%+ match at each window")
    print("=" * 100)

    for w in [2, 3, 4, 5, 7, 10]:
        users_with_95 = [r for r in all_results if r["results"][w].get("count_95pct", 0) > 0]
        users_with_90 = [r for r in all_results if r["results"][w]["best_score"] >= 34]
        users_with_85 = [r for r in all_results if r["results"][w]["best_score"] >= 32]
        print(f"±{w} years: {len(users_with_95):>2}/14 users get 95%+, {len(users_with_90):>2}/14 get 90%+, {len(users_with_85):>2}/14 get 85%+")

    # Approach comparison
    print()
    print("=" * 100)
    print("APPROACH COMPARISON")
    print("=" * 100)
    print()
    print("Approach 1: NARROW WINDOW (±3 years, take best score)")
    print("-" * 60)
    for r in all_results:
        best = r["results"][3]["best_match"]
        if best:
            pct = round(min(best["score"], 38) / 38 * 100)
            print(f"  {r['user']:<20}: {pct:>3}% (gap: {best['age_gap']:+d})")
        else:
            print(f"  {r['user']:<20}: NO MATCH")

    print()
    print("Approach 2: TIERED SEARCH (expand until 90%+ found)")
    print("-" * 60)
    for r in all_results:
        for w in [2, 3, 4, 5, 7, 10]:
            best = r["results"][w]["best_score"]
            if best >= 34:  # 90%
                match = r["results"][w]["best_match"]
                pct = round(min(best, 38) / 38 * 100)
                print(f"  {r['user']:<20}: {pct:>3}% at ±{w}yr (gap: {match['age_gap']:+d})")
                break
        else:
            best = r["results"][10]["best_match"]
            pct = round(min(best["score"], 38) / 38 * 100) if best else 0
            print(f"  {r['user']:<20}: {pct:>3}% (best at ±10yr)")

    print()
    print("Approach 3: AGE-WEIGHTED SCORING (score - |age_gap| * 2)")
    print("-" * 60)
    for result in all_results:
        # Recalculate with age penalty
        r = result["results"][10]  # Use full range
        # We need to access all_matches... let's simulate
        # Best would be: find match that maximizes (score - abs(age_gap) * 2)
        pass
    print("  (Would need to re-run scoring with penalty - skipped for now)")


if __name__ == "__main__":
    main()

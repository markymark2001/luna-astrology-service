"""Analyze the actual birth dates of 95%+ matches within ±3 years."""

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

    if SUN_QUALITY.get(point.sun.sign, "Fixed") == user_sun_quality:
        score += 5

    _, asp, orb = calculate_aspect_score(point.sun.abs_pos, user_sun_pos)
    if asp in ("conjunction", "opposition", "square"):
        score += 11 if orb <= 2 else 8
    elif asp in ("trine", "sextile"):
        score += 4

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

    _, asp, _ = calculate_aspect_score(point.sun.abs_pos, user_ascendant_pos)
    if asp:
        score += 4
    _, asp, _ = calculate_aspect_score(point.moon.abs_pos, user_ascendant_pos)
    if asp:
        score += 4

    target_idx = ZODIAC_SIGNS.index(target_rising) if target_rising in ZODIAC_SIGNS else 6
    est_asc = (target_idx * 30) + 15
    _, asp, _ = calculate_aspect_score(user_sun_pos, est_asc)
    if asp:
        score += 4
    _, asp, _ = calculate_aspect_score(user_moon_pos, est_asc)
    if asp:
        score += 4

    _, asp, _ = calculate_aspect_score(point.venus.abs_pos, user_mars_pos)
    if asp:
        score += 4
    _, asp, _ = calculate_aspect_score(point.mars.abs_pos, user_venus_pos)
    if asp:
        score += 4

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


def analyze_user_dates(user: UserProfile, provider: KerykeionProvider):
    """Get all 95%+ matches within ±3 years with their dates."""
    birth_data = _create_birth_data(user)
    user_chart = provider.calculate_natal_chart(birth_data)
    current_year = datetime.now().year
    user_age = current_year - user.year

    # ±3 year window (respecting 18+ constraint)
    min_soulmate_age = max(18, user_age - 3)
    max_soulmate_age = user_age + 3
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

    # Generate ephemeris for ±3 years
    ephemeris = provider.generate_ephemeris_for_range(
        start_date=date(min_birth_year, 1, 1),
        end_date=date(max_birth_year, 12, 31),
        location=birth_data,
    )

    # Collect all 95%+ matches
    matches = []
    for point in ephemeris:
        score = score_point(point, user_sun_pos, user_moon_pos, user_venus_pos, user_mars_pos,
                           user_ascendant_pos, user_north_node_pos, user_sun_quality, target_rising)
        if score >= 36:  # 95%+
            age_gap = point.year - user.year
            same_month = point.month == user.month
            same_day = point.day == user.day
            same_birthday = same_month and same_day
            days_from_birthday = abs((point.month * 30 + point.day) - (user.month * 30 + user.day))
            if days_from_birthday > 182:
                days_from_birthday = 365 - days_from_birthday

            matches.append({
                "date": f"{point.year}-{point.month:02d}-{point.day:02d}",
                "month_day": f"{point.month:02d}-{point.day:02d}",
                "score": score,
                "percent": round(min(score, 38) / 38 * 100),
                "age_gap": age_gap,
                "same_birthday": same_birthday,
                "same_month": same_month,
                "days_from_birthday": days_from_birthday,
                "sun_sign": point.sun.sign,
                "moon_sign": point.moon.sign,
            })

    return {
        "user": user.name,
        "user_birthday": f"{user.month:02d}-{user.day:02d}",
        "user_sun": user.sun_sign,
        "matches": sorted(matches, key=lambda x: -x["score"]),
        "total_95plus": len(matches),
    }


def main():
    config = get_preset(DetailLevel.CORE)
    provider = KerykeionProvider(config)

    print("=" * 100)
    print("BIRTH DATE ANALYSIS: What dates are the 95%+ matches within ±3 years?")
    print("=" * 100)
    print()

    all_results = []
    for user in TEST_USERS:
        print(f"Analyzing {user.name}...", end="\r")
        result = analyze_user_dates(user, provider)
        all_results.append(result)

    # Detailed output per user
    for result in all_results:
        print(f"\n{'=' * 80}")
        print(f"USER: {result['user']} (birthday: {result['user_birthday']}, Sun: {result['user_sun']})")
        print(f"{'=' * 80}")
        print(f"Total 95%+ matches in ±3 years: {result['total_95plus']}")

        matches = result["matches"]
        if not matches:
            print("  NO MATCHES")
            continue

        # Same birthday matches
        same_bday = [m for m in matches if m["same_birthday"]]
        same_month = [m for m in matches if m["same_month"] and not m["same_birthday"]]

        print(f"\nSame birthday matches: {len(same_bday)}")
        for m in same_bday[:5]:
            print(f"  {m['date']} - {m['percent']}% (Sun: {m['sun_sign']}, Moon: {m['moon_sign']})")

        print(f"\nSame month (different day) matches: {len(same_month)}")
        for m in same_month[:5]:
            print(f"  {m['date']} - {m['percent']}% (Sun: {m['sun_sign']}, Moon: {m['moon_sign']})")

        # Distance distribution
        close_matches = [m for m in matches if m["days_from_birthday"] <= 7]
        week_matches = [m for m in matches if 7 < m["days_from_birthday"] <= 14]
        month_matches = [m for m in matches if 14 < m["days_from_birthday"] <= 30]
        far_matches = [m for m in matches if m["days_from_birthday"] > 30]

        print("\nBy distance from user's birthday:")
        print(f"  Within 1 week:  {len(close_matches):3d} matches")
        print(f"  1-2 weeks:      {len(week_matches):3d} matches")
        print(f"  2-4 weeks:      {len(month_matches):3d} matches")
        print(f"  > 1 month away: {len(far_matches):3d} matches")

        # Show top 10 matches with details
        print("\nTop 10 matches:")
        print(f"  {'Date':<12} {'Score':<6} {'Gap':<5} {'Sun':<5} {'Moon':<5} {'Days from bday':<15}")
        print(f"  {'-'*50}")
        for m in matches[:10]:
            print(f"  {m['date']:<12} {m['percent']:>3}%   {m['age_gap']:+2}    {m['sun_sign']:<5} {m['moon_sign']:<5} {m['days_from_birthday']:>3} days")

    # Summary statistics
    print("\n" + "=" * 100)
    print("SUMMARY: Same birthday vs different dates")
    print("=" * 100)
    print(f"{'User':<20} {'Birthday':<10} {'Total':<8} {'Same Bday':<10} {'Same Mo':<10} {'<1wk':<8} {'Far(>1mo)':<10}")
    print("-" * 100)

    total_matches = 0
    total_same_bday = 0
    total_same_month = 0
    total_close = 0
    total_far = 0

    for result in all_results:
        matches = result["matches"]
        same_bday = len([m for m in matches if m["same_birthday"]])
        same_month = len([m for m in matches if m["same_month"]])
        close = len([m for m in matches if m["days_from_birthday"] <= 7])
        far = len([m for m in matches if m["days_from_birthday"] > 30])

        total_matches += len(matches)
        total_same_bday += same_bday
        total_same_month += same_month
        total_close += close
        total_far += far

        print(f"{result['user']:<20} {result['user_birthday']:<10} {len(matches):<8} {same_bday:<10} {same_month:<10} {close:<8} {far:<10}")

    print("-" * 100)
    print(f"{'TOTAL':<20} {'':<10} {total_matches:<8} {total_same_bday:<10} {total_same_month:<10} {total_close:<8} {total_far:<10}")
    print()
    print(f"Percentage same birthday: {total_same_bday/total_matches*100:.1f}%")
    print(f"Percentage same month:    {total_same_month/total_matches*100:.1f}%")
    print(f"Percentage within 1 week: {total_close/total_matches*100:.1f}%")
    print(f"Percentage > 1 month:     {total_far/total_matches*100:.1f}%")


if __name__ == "__main__":
    main()

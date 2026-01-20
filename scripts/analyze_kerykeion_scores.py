#!/usr/bin/env python3
"""
Analyze Kerykeion RelationshipScoreFactory to understand what gives high scores.

This script tests various chart configurations to find what maximizes compatibility.
"""

from kerykeion import AstrologicalSubjectFactory, RelationshipScoreFactory


def create_subject(name: str, year: int, month: int, day: int, hour: int = 12, minute: int = 0):
    """Create an AstrologicalSubjectModel for testing."""
    return AstrologicalSubjectFactory.from_birth_data(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        lat=40.7128,  # NYC
        lng=-74.0060,
        tz_str="America/New_York",
    )


def analyze_score(person1, person2):
    """Analyze and print the relationship score breakdown."""
    factory = RelationshipScoreFactory(person1, person2)
    score = factory.get_relationship_score()

    print(f"\n{'='*60}")
    print(f"Person 1: {person1.name}")
    print(f"  Sun: {person1.sun['sign']} ({person1.sun['quality']}) @ {person1.sun['abs_pos']:.2f}°")
    print(f"  Moon: {person1.moon['sign']} @ {person1.moon['abs_pos']:.2f}°")
    print(f"  Venus: {person1.venus['sign']} @ {person1.venus['abs_pos']:.2f}°")
    print(f"  Mars: {person1.mars['sign']} @ {person1.mars['abs_pos']:.2f}°")
    print(f"  Asc: {person1.ascendant['sign']} @ {person1.ascendant['abs_pos']:.2f}°")

    print(f"\nPerson 2: {person2.name}")
    print(f"  Sun: {person2.sun['sign']} ({person2.sun['quality']}) @ {person2.sun['abs_pos']:.2f}°")
    print(f"  Moon: {person2.moon['sign']} @ {person2.moon['abs_pos']:.2f}°")
    print(f"  Venus: {person2.venus['sign']} @ {person2.venus['abs_pos']:.2f}°")
    print(f"  Mars: {person2.mars['sign']} @ {person2.mars['abs_pos']:.2f}°")
    print(f"  Asc: {person2.ascendant['sign']} @ {person2.ascendant['abs_pos']:.2f}°")

    print(f"\n>>> SCORE: {score.score_value} ({score.score_description})")
    print(f">>> Destiny Sign: {score.is_destiny_sign}")
    print("\nAspects contributing to score:")
    for aspect in score.aspects:
        print(f"  - {aspect.p1_name} {aspect.aspect} {aspect.p2_name} (orb: {aspect.orbit:.2f}°)")

    return score.score_value


def test_identical_charts():
    """Test what happens with nearly identical charts (same birthday, same time)."""
    print("\n" + "="*70)
    print("TEST: IDENTICAL CHARTS (same birthday, same time)")
    print("="*70)

    person1 = create_subject("User", 1990, 6, 15, 12, 0)
    person2 = create_subject("Clone", 1990, 6, 15, 12, 0)

    return analyze_score(person1, person2)


def test_same_day_different_year():
    """Test charts with same birthday but different year."""
    print("\n" + "="*70)
    print("TEST: SAME DAY, DIFFERENT YEAR (Sun conjunction)")
    print("="*70)

    person1 = create_subject("User", 1990, 6, 15, 12, 0)
    person2 = create_subject("Partner", 1985, 6, 15, 12, 0)

    return analyze_score(person1, person2)


def test_trine_sun():
    """Test charts with Sun trine (same element, 120° apart)."""
    print("\n" + "="*70)
    print("TEST: SUN TRINE (same element, 120° apart)")
    print("="*70)

    # User: Gemini Sun (Jun 15)
    person1 = create_subject("User (Gemini)", 1990, 6, 15, 12, 0)
    # Partner: Libra Sun (Oct 15) - Libra is trine Gemini (both Air)
    person2 = create_subject("Partner (Libra)", 1990, 10, 15, 12, 0)

    return analyze_score(person1, person2)


def test_opposition_sun():
    """Test charts with Sun opposition (180° apart)."""
    print("\n" + "="*70)
    print("TEST: SUN OPPOSITION (180° apart)")
    print("="*70)

    # User: Gemini Sun (Jun 15)
    person1 = create_subject("User (Gemini)", 1990, 6, 15, 12, 0)
    # Partner: Sagittarius Sun (Dec 15) - opposite Gemini
    person2 = create_subject("Partner (Sagittarius)", 1990, 12, 15, 12, 0)

    return analyze_score(person1, person2)


def test_square_sun():
    """Test charts with Sun square (90° apart)."""
    print("\n" + "="*70)
    print("TEST: SUN SQUARE (90° apart)")
    print("="*70)

    # User: Gemini Sun (Jun 15)
    person1 = create_subject("User (Gemini)", 1990, 6, 15, 12, 0)
    # Partner: Virgo Sun (Sep 15) - square Gemini
    person2 = create_subject("Partner (Virgo)", 1990, 9, 15, 12, 0)

    return analyze_score(person1, person2)


def test_sextile_sun():
    """Test charts with Sun sextile (60° apart)."""
    print("\n" + "="*70)
    print("TEST: SUN SEXTILE (60° apart)")
    print("="*70)

    # User: Gemini Sun (Jun 15)
    person1 = create_subject("User (Gemini)", 1990, 6, 15, 12, 0)
    # Partner: Leo Sun (Aug 15) - sextile Gemini
    person2 = create_subject("Partner (Leo)", 1990, 8, 15, 12, 0)

    return analyze_score(person1, person2)


def find_maximum_score():
    """Try to find the theoretical maximum score configuration."""
    print("\n" + "="*70)
    print("TEST: FINDING MAXIMUM SCORE CONFIGURATION")
    print("="*70)

    # Kerykeion scores:
    # - Destiny Sign: 5 pts (same quality)
    # - Sun-Sun (conj/opp/sq tight): 11 pts
    # - Sun-Moon conjunction: 11 pts (both ways = 22 pts max?)
    # - Sun-Moon other: 4 pts (both ways = 8 pts max)
    # - Sun-Asc: 4 pts (both ways = 8 pts max)
    # - Moon-Asc: 4 pts (both ways = 8 pts max)
    # - Venus-Mars: 4 pts (both ways = 8 pts max)

    best_score = 0
    best_config = None

    # Test many date combinations to find max score
    import itertools

    # Test dates around various positions
    base_year = 1990
    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    days = [1, 8, 15, 22]
    hours = [6, 12, 18]

    test_count = 0
    for m1, d1, h1, m2, d2, h2 in itertools.product(
        [6], [15], [12],  # Fix person 1
        months, days, hours  # Vary person 2
    ):
        try:
            person1 = create_subject("P1", base_year, m1, d1, h1)
            person2 = create_subject("P2", base_year, m2, d2, h2)

            factory = RelationshipScoreFactory(person1, person2)
            score = factory.get_relationship_score()
            test_count += 1

            if score.score_value > best_score:
                best_score = score.score_value
                best_config = ((m1, d1, h1, m2, d2, h2), person1, person2, score)
                print(f"  New best: {best_score} pts (P2: {m2}/{d2} {h2}:00)")

        except Exception:
            pass

    print(f"\nTested {test_count} configurations")

    if best_config:
        print(f"\nBest score found: {best_score}")
        analyze_score(best_config[1], best_config[2])

    return best_score


def test_theoretical_max():
    """Test what the theoretical maximum should be."""
    print("\n" + "="*70)
    print("THEORETICAL MAXIMUM ANALYSIS")
    print("="*70)

    print("""
Kerykeion scoring breakdown:
- Destiny Sign (same quality): 5 pts
- Sun-Sun (conj/opp/sq, ≤2° orb): 11 pts
- Sun-Sun (conj/opp/sq, >2° orb): 8 pts
- Sun-Sun (trine/sextile): 4 pts
- Sun-Moon conjunction (≤2° orb): 11 pts each way
- Sun-Moon other aspects: 4 pts each way
- Sun-Ascendant: 4 pts each way
- Moon-Ascendant: 4 pts each way
- Venus-Mars: 4 pts each way

Maximum theoretical:
- Destiny: 5
- Sun-Sun tight: 11
- Sun-Moon conj x2: 22 (if both ways have tight conjunction)
- Sun-Asc x2: 8
- Moon-Asc x2: 8
- Venus-Mars x2: 8
TOTAL: 62 pts

But realistically you can't have ALL of these simultaneously!
The planets move together, so if Sun1-Moon2 is conjunction,
then Sun2-Moon1 might be something else.

Let's see what we can actually achieve...
""")

    # Try to find a configuration that maximizes multiple aspect pairs
    # Person 1: Jun 15, 1990 (Gemini Sun)
    # We want Person 2's Moon near Person 1's Sun (Gemini, ~84°)
    # We want Person 2's Sun forming aspect with Person 1's Moon (Pisces, ~348°)

    # Pisces Moon would be around Feb/Mar
    # Gemini Sun would be around Jun

    # Let's try someone born when Moon is in Gemini (near person 1's Sun)
    # and Sun is opposite to person 1's Moon (Virgo, near 168°)

    print("Testing: Person 1 Sun in Gemini, Moon in Pisces")
    print("         Person 2 needs Moon in Gemini + Sun forming aspect to Pisces")

    # Find dates when Moon is in Gemini
    # Moon cycles ~27 days, so check different months

    best_overall = 0

    for year2 in [1988, 1989, 1990, 1991, 1992]:
        for month2 in range(1, 13):
            for day2 in range(1, 29):
                for hour2 in [6, 12, 18]:
                    try:
                        person1 = create_subject("User", 1990, 6, 15, 12)
                        person2 = create_subject("Partner", year2, month2, day2, hour2)

                        factory = RelationshipScoreFactory(person1, person2)
                        score = factory.get_relationship_score()

                        if score.score_value > best_overall:
                            best_overall = score.score_value
                            print(f"  New best: {score.score_value} pts - {year2}/{month2}/{day2} {hour2}:00")
                            if score.score_value >= 35:
                                print("   Aspects:")
                                for asp in score.aspects:
                                    print(f"     {asp.p1_name} {asp.aspect} {asp.p2_name} ({asp.orbit:.1f}°)")

                    except Exception:
                        pass

    print(f"\nBest found: {best_overall} pts")
    return best_overall


def test_current_algorithm_output():
    """Test what our current soulmate algorithm produces."""
    print("\n" + "="*70)
    print("TEST: CURRENT ALGORITHM OUTPUT")
    print("="*70)

    # Simulate a user born Jun 15, 1990
    # Our algorithm finds a soulmate - let's test with a typical output
    # (based on what the user reported - nearly identical chart)

    person1 = create_subject("User", 1990, 6, 15, 14, 30)

    # Our algorithm currently finds dates with Sun at same position
    # Let's test with exact same birthday different year (what we're producing)
    person2 = create_subject("Algorithm Output", 1992, 6, 14, 14, 30)

    return analyze_score(person1, person2)


if __name__ == "__main__":
    print("="*70)
    print("KERYKEION RELATIONSHIP SCORE ANALYSIS")
    print("="*70)

    scores = {}

    scores["Identical"] = test_identical_charts()
    scores["Same day diff year"] = test_same_day_different_year()
    scores["Sun Trine"] = test_trine_sun()
    scores["Sun Opposition"] = test_opposition_sun()
    scores["Sun Square"] = test_square_sun()
    scores["Sun Sextile"] = test_sextile_sun()
    scores["Current algo"] = test_current_algorithm_output()
    scores["Maximum search"] = find_maximum_score()
    scores["Theoretical max"] = test_theoretical_max()

    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    for name, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {name}: {score} pts")

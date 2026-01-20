"""Tests for soulmate age range calculation by gender combination.

TDD approach: these tests are written first and will fail until implementation is complete.

Run tests:
    pytest astrology-service/tests/test_soulmate_age_range.py -v
"""

from app.application.soulmate_service import calculate_age_range


class TestManWomanAgeRange:
    """Tests for man-woman combinations using half-plus-seven formula.

    Formula: Min age = max(18, (his_age / 2) + 7), Max age = min + 8
    """

    def test_man_30_looking_for_woman(self):
        """30yo man looking for woman should get range 22-30."""
        min_age, max_age = calculate_age_range(
            user_age=30,
            user_gender="male",
            soulmate_sex="female",
        )
        assert min_age == 22  # (30/2)+7 = 22
        assert max_age == 30  # 22+8 = 30

    def test_man_20_looking_for_woman(self):
        """20yo man looking for woman should get range 18-26 (min clamped to 18)."""
        min_age, max_age = calculate_age_range(
            user_age=20,
            user_gender="male",
            soulmate_sex="female",
        )
        assert min_age == 18  # max(18, (20/2)+7=17) = 18
        assert max_age == 26  # 18+8 = 26

    def test_man_25_looking_for_woman(self):
        """25yo man looking for woman should get range 19-27."""
        min_age, max_age = calculate_age_range(
            user_age=25,
            user_gender="male",
            soulmate_sex="female",
        )
        assert min_age == 19  # (25/2)+7 = 19
        assert max_age == 27  # 19+8 = 27

    def test_man_40_looking_for_woman(self):
        """40yo man looking for woman should get range 27-35."""
        min_age, max_age = calculate_age_range(
            user_age=40,
            user_gender="male",
            soulmate_sex="female",
        )
        assert min_age == 27  # (40/2)+7 = 27
        assert max_age == 35  # 27+8 = 35

    def test_man_50_looking_for_woman(self):
        """50yo man looking for woman should get range 32-40."""
        min_age, max_age = calculate_age_range(
            user_age=50,
            user_gender="male",
            soulmate_sex="female",
        )
        assert min_age == 32  # (50/2)+7 = 32
        assert max_age == 40  # 32+8 = 40

    def test_man_18_looking_for_woman(self):
        """18yo man looking for woman should get range 18-26 (min clamped)."""
        min_age, max_age = calculate_age_range(
            user_age=18,
            user_gender="male",
            soulmate_sex="female",
        )
        assert min_age == 18  # max(18, (18/2)+7=16) = 18
        assert max_age == 26  # 18+8 = 26


class TestWomanManAgeRange:
    """Tests for woman-man combinations using inverse formula.

    Formula: Min age = max(18, her_age), Max age = her_age + 8
    """

    def test_woman_30_looking_for_man(self):
        """30yo woman looking for man should get range 30-38."""
        min_age, max_age = calculate_age_range(
            user_age=30,
            user_gender="female",
            soulmate_sex="male",
        )
        assert min_age == 30  # her_age
        assert max_age == 38  # 30+8 = 38

    def test_woman_20_looking_for_man(self):
        """20yo woman looking for man should get range 20-28."""
        min_age, max_age = calculate_age_range(
            user_age=20,
            user_gender="female",
            soulmate_sex="male",
        )
        assert min_age == 20  # her_age
        assert max_age == 28  # 20+8 = 28

    def test_woman_25_looking_for_man(self):
        """25yo woman looking for man should get range 25-33."""
        min_age, max_age = calculate_age_range(
            user_age=25,
            user_gender="female",
            soulmate_sex="male",
        )
        assert min_age == 25  # her_age
        assert max_age == 33  # 25+8 = 33

    def test_woman_40_looking_for_man(self):
        """40yo woman looking for man should get range 40-48."""
        min_age, max_age = calculate_age_range(
            user_age=40,
            user_gender="female",
            soulmate_sex="male",
        )
        assert min_age == 40  # her_age
        assert max_age == 48  # 40+8 = 48

    def test_woman_18_looking_for_man(self):
        """18yo woman looking for man should get range 18-26."""
        min_age, max_age = calculate_age_range(
            user_age=18,
            user_gender="female",
            soulmate_sex="male",
        )
        assert min_age == 18  # max(18, 18) = 18
        assert max_age == 26  # 18+8 = 26


class TestSameSexAgeRange:
    """Tests for same-sex combinations using ±4 years centered on user's age."""

    def test_man_25_looking_for_man(self):
        """25yo man looking for man should get range 21-29."""
        min_age, max_age = calculate_age_range(
            user_age=25,
            user_gender="male",
            soulmate_sex="male",
        )
        assert min_age == 21  # 25-4 = 21
        assert max_age == 29  # 25+4 = 29

    def test_woman_25_looking_for_woman(self):
        """25yo woman looking for woman should get range 21-29."""
        min_age, max_age = calculate_age_range(
            user_age=25,
            user_gender="female",
            soulmate_sex="female",
        )
        assert min_age == 21  # 25-4 = 21
        assert max_age == 29  # 25+4 = 29

    def test_man_20_looking_for_man_clamps_to_18(self):
        """20yo man looking for man should clamp min to 18."""
        min_age, max_age = calculate_age_range(
            user_age=20,
            user_gender="male",
            soulmate_sex="male",
        )
        assert min_age == 18  # max(18, 20-4=16) = 18
        assert max_age == 24  # 20+4 = 24

    def test_woman_40_looking_for_woman(self):
        """40yo woman looking for woman should get range 36-44."""
        min_age, max_age = calculate_age_range(
            user_age=40,
            user_gender="female",
            soulmate_sex="female",
        )
        assert min_age == 36  # 40-4 = 36
        assert max_age == 44  # 40+4 = 44


class TestNonBinaryAndUnknownGender:
    """Tests for non-binary and unknown gender combinations (fallback to ±4 years)."""

    def test_nonbinary_user_looking_for_woman(self):
        """Non-binary user looking for woman should use ±4 years."""
        min_age, max_age = calculate_age_range(
            user_age=30,
            user_gender="non-binary",
            soulmate_sex="female",
        )
        assert min_age == 26  # 30-4 = 26
        assert max_age == 34  # 30+4 = 34

    def test_male_user_looking_for_nonbinary(self):
        """Male user looking for non-binary should use ±4 years."""
        min_age, max_age = calculate_age_range(
            user_age=30,
            user_gender="male",
            soulmate_sex="non-binary",
        )
        assert min_age == 26  # 30-4 = 26
        assert max_age == 34  # 30+4 = 34

    def test_none_user_gender(self):
        """None user gender should use ±4 years fallback."""
        min_age, max_age = calculate_age_range(
            user_age=30,
            user_gender=None,
            soulmate_sex="female",
        )
        assert min_age == 26  # 30-4 = 26
        assert max_age == 34  # 30+4 = 34

    def test_none_soulmate_sex(self):
        """None soulmate sex should use ±4 years fallback."""
        min_age, max_age = calculate_age_range(
            user_age=30,
            user_gender="male",
            soulmate_sex=None,
        )
        assert min_age == 26  # 30-4 = 26
        assert max_age == 34  # 30+4 = 34

    def test_both_genders_none(self):
        """Both genders None should use ±4 years fallback."""
        min_age, max_age = calculate_age_range(
            user_age=30,
            user_gender=None,
            soulmate_sex=None,
        )
        assert min_age == 26  # 30-4 = 26
        assert max_age == 34  # 30+4 = 34


class TestMinorUsers:
    """Tests for users under 18 (soulmate should always be 18+)."""

    def test_minor_user_gets_adult_soulmate(self):
        """Users under 18 should always get 18+ soulmate range."""
        min_age, max_age = calculate_age_range(
            user_age=16,
            user_gender="male",
            soulmate_sex="female",
        )
        assert min_age == 18  # Always 18+
        assert max_age == 26  # 18+8 = 26

    def test_minor_user_same_sex(self):
        """Minor user with same-sex preference should still get 18+ range."""
        min_age, max_age = calculate_age_range(
            user_age=17,
            user_gender="female",
            soulmate_sex="female",
        )
        assert min_age == 18  # Always 18+
        assert max_age == 26  # 18+8 = 26


class TestEdgeCases:
    """Edge case tests for age range calculation."""

    def test_exactly_18_man_looking_for_woman(self):
        """18yo man looking for woman - boundary case."""
        min_age, max_age = calculate_age_range(
            user_age=18,
            user_gender="male",
            soulmate_sex="female",
        )
        # (18/2)+7 = 16, clamped to 18
        assert min_age == 18
        assert max_age == 26

    def test_exactly_18_woman_looking_for_man(self):
        """18yo woman looking for man - boundary case."""
        min_age, max_age = calculate_age_range(
            user_age=18,
            user_gender="female",
            soulmate_sex="male",
        )
        assert min_age == 18
        assert max_age == 26

    def test_range_always_8_years(self):
        """All gender combinations should produce an 8-year range."""
        test_cases = [
            (30, "male", "female"),
            (30, "female", "male"),
            (30, "male", "male"),
            (30, "female", "female"),
            (30, None, "female"),
            (30, "male", None),
        ]
        for user_age, user_gender, soulmate_sex in test_cases:
            min_age, max_age = calculate_age_range(user_age, user_gender, soulmate_sex)
            assert max_age - min_age == 8, (
                f"Range not 8 years for {user_gender} -> {soulmate_sex}: "
                f"got {min_age}-{max_age} ({max_age - min_age} years)"
            )

"""Tests for llm_formatter synastry formatting with relationship score."""

from app.core.llm_formatter import _score_to_percentage, format_synastry


class TestScoreToPercentage:
    """Tests for _score_to_percentage using the Kerykeion sqrt curve."""

    def test_score_0_maps_to_0_percent(self):
        """Score 0 maps to 0%."""
        assert _score_to_percentage(0) == 0

    def test_score_15_maps_to_50_percent(self):
        """Score 15 maps to 71% (sqrt curve)."""
        assert _score_to_percentage(15) == 71

    def test_score_30_maps_to_100_percent(self):
        """Score 30 maps to 100% (sqrt curve)."""
        assert _score_to_percentage(30) == 100

    def test_score_above_30_caps_at_100_percent(self):
        """Score above 30 caps at 100% (sqrt curve)."""
        assert _score_to_percentage(35) == 100
        assert _score_to_percentage(50) == 100

    def test_negative_score_caps_at_0_percent(self):
        """Negative scores cap at 0%."""
        assert _score_to_percentage(-5) == 0
        assert _score_to_percentage(-20) == 0

    def test_score_24_maps_to_80_percent(self):
        """Score 24 maps to 89% (sqrt curve)."""
        assert _score_to_percentage(24) == 89

    def test_score_12_maps_to_40_percent(self):
        """Score 12 maps to 63% (sqrt curve)."""
        assert _score_to_percentage(12) == 63


class TestFormatSynastryWithScore:
    """Tests for format_synastry with Kerykeion sqrt-curve compatibility."""

    def test_format_synastry_includes_percentage(self):
        """format_synastry includes sqrt-curve COMPATIBILITY when score present."""
        synastry_data = {
            "synastry": {
                "aspects": [
                    {"p1_name": "Sun", "p2_name": "Moon", "aspect": "conjunction", "orbit": 2.3}
                ]
            },
            "relationship_score": {
                "score_value": 15,
                "is_destiny_sign": False,
            },
        }

        result = format_synastry(synastry_data)

        assert "COMPATIBILITY: 71%" in result

    def test_format_synastry_shows_destiny_sign_when_true(self):
        """format_synastry shows Destiny Sign: Yes when is_destiny_sign is True."""
        synastry_data = {
            "synastry": {
                "aspects": []
            },
            "relationship_score": {
                "score_value": 10,
                "is_destiny_sign": True,
            },
        }

        result = format_synastry(synastry_data)

        assert "Destiny Sign: Yes" in result

    def test_format_synastry_omits_destiny_sign_when_false(self):
        """format_synastry omits Destiny Sign line when is_destiny_sign is False."""
        synastry_data = {
            "synastry": {
                "aspects": []
            },
            "relationship_score": {
                "score_value": 10,
                "is_destiny_sign": False,
            },
        }

        result = format_synastry(synastry_data)

        assert "Destiny Sign" not in result

    def test_format_synastry_works_without_score(self):
        """format_synastry works without relationship_score (backwards compatibility)."""
        synastry_data = {
            "synastry": {
                "aspects": [
                    {"p1_name": "Sun", "p2_name": "Moon", "aspect": "conjunction", "orbit": 2.3}
                ]
            },
        }

        result = format_synastry(synastry_data)

        assert "SYNASTRY ASPECTS" in result
        assert "COMPATIBILITY" not in result

    def test_format_synastry_works_with_none_score(self):
        """format_synastry works when relationship_score is None."""
        synastry_data = {
            "synastry": {
                "aspects": [
                    {"p1_name": "Sun", "p2_name": "Moon", "aspect": "conjunction", "orbit": 2.3}
                ]
            },
            "relationship_score": None,
        }

        result = format_synastry(synastry_data)

        assert "SYNASTRY ASPECTS" in result
        assert "COMPATIBILITY" not in result

    def test_format_synastry_score_appears_before_aspects(self):
        """COMPATIBILITY appears before SYNASTRY ASPECTS."""
        synastry_data = {
            "synastry": {
                "aspects": [
                    {"p1_name": "Sun", "p2_name": "Moon", "aspect": "conjunction", "orbit": 2.3}
                ]
            },
            "relationship_score": {
                "score_value": 15,
                "is_destiny_sign": True,
            },
        }

        result = format_synastry(synastry_data)

        score_pos = result.find("COMPATIBILITY")
        aspects_pos = result.find("SYNASTRY ASPECTS")

        assert score_pos < aspects_pos, "COMPATIBILITY should appear before SYNASTRY ASPECTS"

    def test_format_synastry_high_score_shows_high_percentage(self):
        """High score (24) shows 89% (sqrt curve)."""
        synastry_data = {
            "synastry": {
                "aspects": []
            },
            "relationship_score": {
                "score_value": 24,
                "is_destiny_sign": False,
            },
        }

        result = format_synastry(synastry_data)

        assert "COMPATIBILITY: 89%" in result

    def test_format_synastry_capped_score_shows_100_percent(self):
        """Score above 30 shows 100%."""
        synastry_data = {
            "synastry": {
                "aspects": []
            },
            "relationship_score": {
                "score_value": 35,
                "is_destiny_sign": False,
            },
        }

        result = format_synastry(synastry_data)

        assert "COMPATIBILITY: 100%" in result

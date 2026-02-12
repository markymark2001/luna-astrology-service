"""Tests for transit planet house correction in llm_formatter."""

from app.core.llm_formatter import _find_natal_house, format_natal_chart


class TestFindNatalHouse:
    """Tests for _find_natal_house which computes correct natal house from ecliptic position."""

    def _make_houses(self, cusps: dict[int, float]) -> dict[str, dict]:
        """Helper: build natal houses dict from {house_num: abs_pos} mapping."""
        num_to_name = {
            1: "first_house", 2: "second_house", 3: "third_house",
            4: "fourth_house", 5: "fifth_house", 6: "sixth_house",
            7: "seventh_house", 8: "eighth_house", 9: "ninth_house",
            10: "tenth_house", 11: "eleventh_house", 12: "twelfth_house",
        }
        return {
            num_to_name[num]: {"name": num_to_name[num].replace("_", " ").title(), "sign": "Aries", "abs_pos": pos}
            for num, pos in cusps.items()
        }

    def test_planet_between_h1_and_h2_returns_1(self):
        """Planet at 15 deg with H1=10 and H2=40 => house 1."""
        houses = self._make_houses({
            1: 10.0, 2: 40.0, 3: 70.0, 4: 100.0, 5: 130.0, 6: 160.0,
            7: 190.0, 8: 220.0, 9: 250.0, 10: 280.0, 11: 310.0, 12: 340.0,
        })
        assert _find_natal_house(15.0, houses) == 1

    def test_planet_between_h6_and_h7_returns_6(self):
        """Planet at 175 deg with H6=160 and H7=190 => house 6."""
        houses = self._make_houses({
            1: 10.0, 2: 40.0, 3: 70.0, 4: 100.0, 5: 130.0, 6: 160.0,
            7: 190.0, 8: 220.0, 9: 250.0, 10: 280.0, 11: 310.0, 12: 340.0,
        })
        assert _find_natal_house(175.0, houses) == 6

    def test_wrap_around_planet_at_355_with_h12_at_340_h1_at_10(self):
        """Planet at 355 deg with H12=340 and H1=10 => house 12 (wrap-around)."""
        houses = self._make_houses({
            1: 10.0, 2: 40.0, 3: 70.0, 4: 100.0, 5: 130.0, 6: 160.0,
            7: 190.0, 8: 220.0, 9: 250.0, 10: 280.0, 11: 310.0, 12: 340.0,
        })
        assert _find_natal_house(355.0, houses) == 12

    def test_wrap_around_planet_at_5_with_h12_at_340_h1_at_10(self):
        """Planet at 5 deg with H12=340 and H1=10 => house 12 (wrap past 360)."""
        houses = self._make_houses({
            1: 10.0, 2: 40.0, 3: 70.0, 4: 100.0, 5: 130.0, 6: 160.0,
            7: 190.0, 8: 220.0, 9: 250.0, 10: 280.0, 11: 310.0, 12: 340.0,
        })
        assert _find_natal_house(5.0, houses) == 12

    def test_planet_exactly_on_cusp_returns_that_house(self):
        """Planet exactly at H4 cusp (100 deg) => house 4."""
        houses = self._make_houses({
            1: 10.0, 2: 40.0, 3: 70.0, 4: 100.0, 5: 130.0, 6: 160.0,
            7: 190.0, 8: 220.0, 9: 250.0, 10: 280.0, 11: 310.0, 12: 340.0,
        })
        assert _find_natal_house(100.0, houses) == 4

    def test_empty_houses_returns_none(self):
        """Empty houses dict => None."""
        assert _find_natal_house(100.0, {}) is None

    def test_houses_without_abs_pos_returns_none(self):
        """Houses missing abs_pos field => None."""
        houses = {"first_house": {"name": "First House", "sign": "Aries"}}
        assert _find_natal_house(100.0, houses) is None

    def test_uneven_house_sizes(self):
        """Houses with uneven sizes (intercepted signs) still work correctly."""
        # H1 spans 50 degrees, H2 spans 20 degrees
        houses = self._make_houses({
            1: 0.0, 2: 50.0, 3: 70.0, 4: 100.0, 5: 130.0, 6: 160.0,
            7: 180.0, 8: 230.0, 9: 250.0, 10: 280.0, 11: 310.0, 12: 340.0,
        })
        assert _find_natal_house(25.0, houses) == 1
        assert _find_natal_house(55.0, houses) == 2


class TestFormatNatalChartTransitHouses:
    """Integration tests: format_natal_chart uses natal houses for transit planets."""

    def test_transit_planet_shows_correct_natal_house(self):
        """Transit planet house is computed from natal houses, not transit chart houses."""
        chart_data = {
            "natal_chart": {
                "planets": {
                    "sun": {"name": "Sun", "sign": "Aries", "position": 15.0, "house": 1, "retrograde": False},
                },
                "houses": {
                    "first_house": {"name": "First House", "sign": "Aries", "abs_pos": 0.0},
                    "second_house": {"name": "Second House", "sign": "Taurus", "abs_pos": 30.0},
                    "third_house": {"name": "Third House", "sign": "Gemini", "abs_pos": 60.0},
                    "fourth_house": {"name": "Fourth House", "sign": "Cancer", "abs_pos": 90.0},
                    "fifth_house": {"name": "Fifth House", "sign": "Leo", "abs_pos": 120.0},
                    "sixth_house": {"name": "Sixth House", "sign": "Virgo", "abs_pos": 150.0},
                    "seventh_house": {"name": "Seventh House", "sign": "Libra", "abs_pos": 180.0},
                    "eighth_house": {"name": "Eighth House", "sign": "Scorpio", "abs_pos": 210.0},
                    "ninth_house": {"name": "Ninth House", "sign": "Sagittarius", "abs_pos": 240.0},
                    "tenth_house": {"name": "Tenth House", "sign": "Capricorn", "abs_pos": 270.0},
                    "eleventh_house": {"name": "Eleventh House", "sign": "Aquarius", "abs_pos": 300.0},
                    "twelfth_house": {"name": "Twelfth House", "sign": "Pisces", "abs_pos": 330.0},
                },
                "points": {},
            },
            "aspects": {},
            "transits": {
                "date": "2025-01-15",
                "planets": {
                    # Transit Mars at 200 deg abs_pos, transit chart says H5
                    # but natal H7 starts at 180 and H8 at 210, so correct house is 7
                    "mars": {
                        "name": "Mars", "sign": "Libra", "position": 20.0,
                        "house": 5, "retrograde": False, "abs_pos": 200.0,
                    },
                },
            },
        }
        result = format_natal_chart(chart_data)
        assert "CURRENT TRANSITS" in result
        # Should show H7 (natal house), NOT H5 (transit chart house)
        assert "Mars in Libra 20° (H7)" in result

    def test_transit_planet_without_abs_pos_strips_house(self):
        """Transit planet without abs_pos has house stripped (better none than wrong)."""
        chart_data = {
            "natal_chart": {
                "planets": {},
                "houses": {
                    "first_house": {"name": "First House", "sign": "Aries", "abs_pos": 0.0},
                    "second_house": {"name": "Second House", "sign": "Taurus", "abs_pos": 30.0},
                    "third_house": {"name": "Third House", "sign": "Gemini", "abs_pos": 60.0},
                    "fourth_house": {"name": "Fourth House", "sign": "Cancer", "abs_pos": 90.0},
                    "fifth_house": {"name": "Fifth House", "sign": "Leo", "abs_pos": 120.0},
                    "sixth_house": {"name": "Sixth House", "sign": "Virgo", "abs_pos": 150.0},
                    "seventh_house": {"name": "Seventh House", "sign": "Libra", "abs_pos": 180.0},
                    "eighth_house": {"name": "Eighth House", "sign": "Scorpio", "abs_pos": 210.0},
                    "ninth_house": {"name": "Ninth House", "sign": "Sagittarius", "abs_pos": 240.0},
                    "tenth_house": {"name": "Tenth House", "sign": "Capricorn", "abs_pos": 270.0},
                    "eleventh_house": {"name": "Eleventh House", "sign": "Aquarius", "abs_pos": 300.0},
                    "twelfth_house": {"name": "Twelfth House", "sign": "Pisces", "abs_pos": 330.0},
                },
                "points": {},
            },
            "aspects": {},
            "transits": {
                "date": "2025-01-15",
                "planets": {
                    # No abs_pos - can't compute natal house
                    "mars": {
                        "name": "Mars", "sign": "Libra", "position": 20.0,
                        "house": 5, "retrograde": False,
                    },
                },
            },
        }
        result = format_natal_chart(chart_data)
        # Should NOT show H5 (wrong transit house), should show no house
        assert "Mars in Libra 20°" in result
        assert "(H5)" not in result

    def test_transit_planet_without_natal_houses_strips_house(self):
        """Transit planet without natal houses available has house stripped."""
        chart_data = {
            "natal_chart": {
                "planets": {},
                "houses": {},
                "points": {},
            },
            "aspects": {},
            "transits": {
                "date": "2025-01-15",
                "planets": {
                    "mars": {
                        "name": "Mars", "sign": "Libra", "position": 20.0,
                        "house": 5, "retrograde": False, "abs_pos": 200.0,
                    },
                },
            },
        }
        result = format_natal_chart(chart_data)
        assert "Mars in Libra 20°" in result
        assert "(H5)" not in result

    def test_retrograde_transit_preserves_rx_with_corrected_house(self):
        """Retrograde transit planet shows both corrected house and Rx."""
        chart_data = {
            "natal_chart": {
                "planets": {},
                "houses": {
                    "first_house": {"name": "First House", "sign": "Aries", "abs_pos": 0.0},
                    "second_house": {"name": "Second House", "sign": "Taurus", "abs_pos": 30.0},
                    "third_house": {"name": "Third House", "sign": "Gemini", "abs_pos": 60.0},
                    "fourth_house": {"name": "Fourth House", "sign": "Cancer", "abs_pos": 90.0},
                    "fifth_house": {"name": "Fifth House", "sign": "Leo", "abs_pos": 120.0},
                    "sixth_house": {"name": "Sixth House", "sign": "Virgo", "abs_pos": 150.0},
                    "seventh_house": {"name": "Seventh House", "sign": "Libra", "abs_pos": 180.0},
                    "eighth_house": {"name": "Eighth House", "sign": "Scorpio", "abs_pos": 210.0},
                    "ninth_house": {"name": "Ninth House", "sign": "Sagittarius", "abs_pos": 240.0},
                    "tenth_house": {"name": "Tenth House", "sign": "Capricorn", "abs_pos": 270.0},
                    "eleventh_house": {"name": "Eleventh House", "sign": "Aquarius", "abs_pos": 300.0},
                    "twelfth_house": {"name": "Twelfth House", "sign": "Pisces", "abs_pos": 330.0},
                },
                "points": {},
            },
            "aspects": {},
            "transits": {
                "date": "2025-01-15",
                "planets": {
                    "saturn": {
                        "name": "Saturn", "sign": "Pisces", "position": 12.0,
                        "house": 3, "retrograde": True, "abs_pos": 342.0,
                    },
                },
            },
        }
        result = format_natal_chart(chart_data)
        # abs_pos 342 is between H12 (330) and H1 (0+360), so natal house = 12
        assert "Saturn in Pisces 12° (H12, Rx)" in result

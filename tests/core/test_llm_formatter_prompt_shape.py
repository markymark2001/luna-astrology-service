"""Tests for prompt-facing chart formatting shape."""

from app.core.llm_formatter import format_aspect, format_natal_chart


def test_format_natal_chart_keeps_points_out_of_planets_section():
    chart_data = {
        "natal_chart": {
            "planets": {
                "sun": {"name": "Sun", "sign": "Ari", "position": 15.0, "house": 1, "retrograde": False},
                "chiron": {"name": "Chiron", "sign": "Gem", "position": 2.0, "house": 11, "retrograde": False},
            },
            "points": {
                "ascendant": {"name": "Ascendant", "sign": "Leo", "position": 14.0, "house": 1, "retrograde": False},
                "medium_coeli": {"name": "Medium_Coeli", "sign": "Tau", "position": 3.0, "house": 10, "retrograde": False},
                "true_north_lunar_node": {
                    "name": "True_North_Lunar_Node",
                    "sign": "Aqu",
                    "position": 15.0,
                    "house": 7,
                    "retrograde": True,
                },
                "true_south_lunar_node": {
                    "name": "True_South_Lunar_Node",
                    "sign": "Leo",
                    "position": 15.0,
                    "house": 1,
                    "retrograde": True,
                },
            },
            "houses": {},
        },
        "aspects": {},
        "transits": {"date": "2025-01-15", "planets": {}, "points": {}},
    }

    result = format_natal_chart(chart_data)

    assert "PLANETS\nSun in Ari 15° (H1)\nChiron in Gem 2° (H11)\n" in result
    assert "POINTS\nAscendant in Leo 14° (H1)\nMidheaven in Tau 3° (H10)\nNorth Node in Aqu 15° (H7, Rx)\nSouth Node in Leo 15° (H1, Rx)" in result
    assert result.count("North Node in Aqu 15° (H7, Rx)") == 1
    assert result.count("South Node in Leo 15° (H1, Rx)") == 1


def test_format_natal_chart_surfaces_current_transit_points():
    chart_data = {
        "natal_chart": {
            "planets": {},
            "points": {},
            "houses": {},
        },
        "aspects": {},
        "transits": {
            "date": "2025-01-15",
            "planets": {
                "chiron": {"name": "Chiron", "sign": "Tau", "position": 10.0, "retrograde": False},
            },
            "points": {
                "medium_coeli": {"name": "Medium_Coeli", "sign": "Can", "position": 8.0, "retrograde": False},
                "true_north_lunar_node": {
                    "name": "True_North_Lunar_Node",
                    "sign": "Aqu",
                    "position": 15.0,
                    "retrograde": True,
                },
                "true_south_lunar_node": {
                    "name": "True_South_Lunar_Node",
                    "sign": "Leo",
                    "position": 15.0,
                    "retrograde": True,
                },
            },
        },
    }

    result = format_natal_chart(chart_data)

    assert "CURRENT TRANSITS" in result
    assert "Chiron in Tau 10°" in result
    assert "Midheaven in Can 8°" in result
    assert "North Node in Aqu 15° (Rx)" in result
    assert "South Node in Leo 15° (Rx)" in result


def test_format_aspect_humanizes_nodes_and_angles():
    result = format_aspect({
        "p1_name": "True_North_Lunar_Node",
        "p2_name": "Medium_Coeli",
        "aspect": "opposition",
        "orbit": -0.6,
    })

    assert result == "North Node opposition Midheaven (orb 0.6)"

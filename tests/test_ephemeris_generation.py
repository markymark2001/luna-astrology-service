"""Tests for ephemeris-based derivation using EphemerisDataFactory.

TDD approach: these tests are written first and will fail until implementation is complete.

Run tests:
    pytest astrology-service/tests/test_ephemeris_generation.py -v
"""

from datetime import date

import pytest


class TestEphemerisGeneration:
    """Tests for ephemeris generation method in KerykeionProvider."""

    def test_generate_ephemeris_for_range_returns_list(self):
        """Should return list of AstrologicalSubject objects."""
        from app.config.astrology_presets import DetailLevel, get_preset
        from app.domain.models import BirthData
        from app.infrastructure.providers.kerykeion_provider import KerykeionProvider

        config = get_preset(DetailLevel.CORE)
        provider = KerykeionProvider(config=config)

        location = BirthData(
            year=1990, month=1, day=1, hour=12, minute=0,
            latitude=40.7, longitude=-74.0, timezone="America/New_York"
        )

        result = provider.generate_ephemeris_for_range(
            start_date=date(2000, 1, 1),
            end_date=date(2000, 12, 31),
            location=location
        )

        assert isinstance(result, list)
        # Should have ~365 daily positions (2000 is not a leap year for this purpose)
        assert len(result) >= 360

    def test_generate_ephemeris_for_range_leap_year(self):
        """Should handle leap year correctly (366 days)."""
        from app.config.astrology_presets import DetailLevel, get_preset
        from app.domain.models import BirthData
        from app.infrastructure.providers.kerykeion_provider import KerykeionProvider

        config = get_preset(DetailLevel.CORE)
        provider = KerykeionProvider(config=config)

        location = BirthData(
            year=1990, month=1, day=1, hour=12, minute=0,
            latitude=40.7, longitude=-74.0, timezone="America/New_York"
        )

        # 2000 is a leap year
        result = provider.generate_ephemeris_for_range(
            start_date=date(2000, 1, 1),
            end_date=date(2001, 1, 1),
            location=location
        )

        assert isinstance(result, list)
        # Should have 366 daily positions (leap year) plus 1 for Jan 1 2001
        assert len(result) >= 366

    def test_ephemeris_points_have_sun_sign(self):
        """Each ephemeris point should have sun.sign attribute."""
        from app.config.astrology_presets import DetailLevel, get_preset
        from app.domain.models import BirthData
        from app.infrastructure.providers.kerykeion_provider import KerykeionProvider

        config = get_preset(DetailLevel.CORE)
        provider = KerykeionProvider(config=config)

        location = BirthData(
            year=1990, month=1, day=1, hour=12, minute=0,
            latitude=40.7, longitude=-74.0, timezone="America/New_York"
        )

        result = provider.generate_ephemeris_for_range(
            start_date=date(2000, 1, 1),
            end_date=date(2000, 1, 31),
            location=location
        )

        assert len(result) > 0
        for point in result[:5]:  # Check first 5 points
            assert hasattr(point, 'sun')
            assert hasattr(point.sun, 'sign')

    def test_ephemeris_points_have_moon_sign(self):
        """Each ephemeris point should have moon.sign attribute."""
        from app.config.astrology_presets import DetailLevel, get_preset
        from app.domain.models import BirthData
        from app.infrastructure.providers.kerykeion_provider import KerykeionProvider

        config = get_preset(DetailLevel.CORE)
        provider = KerykeionProvider(config=config)

        location = BirthData(
            year=1990, month=1, day=1, hour=12, minute=0,
            latitude=40.7, longitude=-74.0, timezone="America/New_York"
        )

        result = provider.generate_ephemeris_for_range(
            start_date=date(2000, 1, 1),
            end_date=date(2000, 1, 31),
            location=location
        )

        assert len(result) > 0
        for point in result[:5]:
            assert hasattr(point, 'moon')
            assert hasattr(point.moon, 'sign')

    def test_ephemeris_points_have_venus_sign(self):
        """Each ephemeris point should have venus.sign attribute."""
        from app.config.astrology_presets import DetailLevel, get_preset
        from app.domain.models import BirthData
        from app.infrastructure.providers.kerykeion_provider import KerykeionProvider

        config = get_preset(DetailLevel.CORE)
        provider = KerykeionProvider(config=config)

        location = BirthData(
            year=1990, month=1, day=1, hour=12, minute=0,
            latitude=40.7, longitude=-74.0, timezone="America/New_York"
        )

        result = provider.generate_ephemeris_for_range(
            start_date=date(2000, 1, 1),
            end_date=date(2000, 1, 31),
            location=location
        )

        assert len(result) > 0
        for point in result[:5]:
            assert hasattr(point, 'venus')
            assert hasattr(point.venus, 'sign')

    def test_ephemeris_points_have_mars_sign(self):
        """Each ephemeris point should have mars.sign attribute."""
        from app.config.astrology_presets import DetailLevel, get_preset
        from app.domain.models import BirthData
        from app.infrastructure.providers.kerykeion_provider import KerykeionProvider

        config = get_preset(DetailLevel.CORE)
        provider = KerykeionProvider(config=config)

        location = BirthData(
            year=1990, month=1, day=1, hour=12, minute=0,
            latitude=40.7, longitude=-74.0, timezone="America/New_York"
        )

        result = provider.generate_ephemeris_for_range(
            start_date=date(2000, 1, 1),
            end_date=date(2000, 1, 31),
            location=location
        )

        assert len(result) > 0
        for point in result[:5]:
            assert hasattr(point, 'mars')
            assert hasattr(point.mars, 'sign')

    def test_ephemeris_points_have_north_node(self):
        """Each ephemeris point should have true_north_lunar_node (True Node)."""
        from app.config.astrology_presets import DetailLevel, get_preset
        from app.domain.models import BirthData
        from app.infrastructure.providers.kerykeion_provider import KerykeionProvider

        config = get_preset(DetailLevel.CORE)
        provider = KerykeionProvider(config=config)

        location = BirthData(
            year=1990, month=1, day=1, hour=12, minute=0,
            latitude=40.7, longitude=-74.0, timezone="America/New_York"
        )

        result = provider.generate_ephemeris_for_range(
            start_date=date(2000, 1, 1),
            end_date=date(2000, 1, 31),
            location=location
        )

        assert len(result) > 0
        for point in result[:5]:
            # Kerykeion uses true_north_lunar_node for North Node
            assert hasattr(point, 'true_north_lunar_node')
            assert hasattr(point.true_north_lunar_node, 'sign')

    @pytest.mark.skip(reason="Performance test for internal reference only")
    def test_ephemeris_performance_large_range(self):
        """Should handle 14-year range efficiently (for soulmate search)."""
        import time

        from app.config.astrology_presets import DetailLevel, get_preset
        from app.domain.models import BirthData
        from app.infrastructure.providers.kerykeion_provider import KerykeionProvider

        config = get_preset(DetailLevel.CORE)
        provider = KerykeionProvider(config=config)

        location = BirthData(
            year=1990, month=1, day=1, hour=12, minute=0,
            latitude=40.7, longitude=-74.0, timezone="America/New_York"
        )

        start_time = time.time()
        result = provider.generate_ephemeris_for_range(
            start_date=date(2000, 1, 1),
            end_date=date(2014, 12, 31),  # 14+ years
            location=location
        )
        elapsed = time.time() - start_time

        # Should have ~5475 daily positions (15 years)
        assert len(result) >= 5000
        # Should complete in under 10 seconds (much faster than 56 chart calculations)
        assert elapsed < 10.0, f"Ephemeris generation took {elapsed:.2f}s, expected < 10s"

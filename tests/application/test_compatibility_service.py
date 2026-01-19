"""Tests for SynastryService (compatibility service)."""

import pytest

from app.application.compatibility_service import SynastryService
from app.config.astrology_presets import DEFAULT_CONFIG
from app.domain.models import BirthData
from app.infrastructure.providers.kerykeion_provider import KerykeionProvider


class TestSynastryServiceRelationshipScore:
    """Tests for SynastryService returning relationship_score in dict."""

    @pytest.fixture
    def service(self) -> SynastryService:
        """Create a SynastryService with KerykeionProvider."""
        provider = KerykeionProvider(config=DEFAULT_CONFIG)
        return SynastryService(provider=provider)

    @pytest.fixture
    def person1_data(self) -> BirthData:
        """Birth data for person 1."""
        return BirthData(
            year=1990,
            month=3,
            day=15,
            hour=14,
            minute=30,
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York",
        )

    @pytest.fixture
    def person2_data(self) -> BirthData:
        """Birth data for person 2."""
        return BirthData(
            year=1992,
            month=7,
            day=22,
            hour=10,
            minute=15,
            latitude=34.0522,
            longitude=-118.2437,
            timezone="America/Los_Angeles",
        )

    def test_analyze_synastry_returns_relationship_score_dict(
        self, service: SynastryService, person1_data: BirthData, person2_data: BirthData
    ):
        """analyze_synastry returns dict containing relationship_score."""
        result = service.analyze_synastry(person1_data, person2_data)

        assert "relationship_score" in result
        assert result["relationship_score"] is not None

    def test_relationship_score_dict_has_score_value(
        self, service: SynastryService, person1_data: BirthData, person2_data: BirthData
    ):
        """relationship_score dict contains score_value."""
        result = service.analyze_synastry(person1_data, person2_data)

        assert "score_value" in result["relationship_score"]
        assert isinstance(result["relationship_score"]["score_value"], int)

    def test_relationship_score_dict_has_is_destiny_sign(
        self, service: SynastryService, person1_data: BirthData, person2_data: BirthData
    ):
        """relationship_score dict contains is_destiny_sign."""
        result = service.analyze_synastry(person1_data, person2_data)

        assert "is_destiny_sign" in result["relationship_score"]
        assert isinstance(result["relationship_score"]["is_destiny_sign"], bool)

    def test_analyze_synastry_maintains_synastry_aspects(
        self, service: SynastryService, person1_data: BirthData, person2_data: BirthData
    ):
        """analyze_synastry still returns synastry aspects."""
        result = service.analyze_synastry(person1_data, person2_data)

        assert "synastry" in result
        assert "aspects" in result["synastry"]
        assert isinstance(result["synastry"]["aspects"], list)

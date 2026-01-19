"""Tests for synastry domain models."""

from app.domain.models.birth_data import BirthData
from app.domain.models.natal_chart import NatalChart
from app.domain.models.synastry import RelationshipScore, Synastry


def create_test_natal_chart(year: int = 1990) -> NatalChart:
    """Create a minimal NatalChart for testing."""
    birth_data = BirthData(year=year, month=3, day=15)
    return NatalChart(
        birth_data=birth_data,
        planets={},
        houses={},
        points={},
        aspects=[],
    )


class TestRelationshipScore:
    """Tests for RelationshipScore model."""

    def test_stores_score_value_and_is_destiny_sign(self):
        """RelationshipScore stores score_value and is_destiny_sign."""
        score = RelationshipScore(score_value=15, is_destiny_sign=True)

        assert score.score_value == 15
        assert score.is_destiny_sign is True

    def test_stores_negative_score(self):
        """RelationshipScore can store negative score values."""
        score = RelationshipScore(score_value=-5, is_destiny_sign=False)

        assert score.score_value == -5
        assert score.is_destiny_sign is False


class TestSynastryWithScore:
    """Tests for Synastry model with relationship score."""

    def test_synastry_accepts_optional_relationship_score(self):
        """Synastry accepts optional relationship_score field."""
        chart1 = create_test_natal_chart(1990)
        chart2 = create_test_natal_chart(1992)
        score = RelationshipScore(score_value=10, is_destiny_sign=True)

        synastry = Synastry(
            chart1=chart1,
            chart2=chart2,
            aspects=[],
            relationship_score=score,
        )

        assert synastry.relationship_score is not None
        assert synastry.relationship_score.score_value == 10
        assert synastry.relationship_score.is_destiny_sign is True

    def test_synastry_relationship_score_defaults_to_none(self):
        """Synastry relationship_score defaults to None."""
        chart1 = create_test_natal_chart(1990)
        chart2 = create_test_natal_chart(1992)

        synastry = Synastry(
            chart1=chart1,
            chart2=chart2,
            aspects=[],
        )

        assert synastry.relationship_score is None

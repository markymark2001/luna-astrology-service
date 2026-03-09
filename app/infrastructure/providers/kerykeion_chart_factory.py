"""Centralized Kerykeion chart construction with explicit chart-system settings."""

from datetime import datetime

from kerykeion import AstrologicalSubjectFactory, EphemerisDataFactory
from kerykeion.schemas.kr_models import AstrologicalSubjectModel

from app.config.chart_system import ChartSystemConfig
from app.domain.models import BirthData


class KerykeionChartFactory:
    """Create Kerykeion subjects and ephemerides with one canonical chart system."""

    def __init__(self, chart_system: ChartSystemConfig):
        self.chart_system = chart_system

    def metadata(self) -> dict[str, str | None]:
        """Return serialized chart-system metadata for responses."""
        return self.chart_system.to_metadata()

    def create_subject(self, name: str, birth_data: BirthData) -> AstrologicalSubjectModel:
        """Create a natal subject with the canonical chart-system settings."""
        subject = AstrologicalSubjectFactory.from_birth_data(
            name=name,
            year=birth_data.year,
            month=birth_data.month,
            day=birth_data.day,
            hour=birth_data.hour,
            minute=birth_data.minute,
            lng=birth_data.longitude,
            lat=birth_data.latitude,
            tz_str=birth_data.timezone,
            online=False,
            zodiac_type=self.chart_system.zodiac_type,
            sidereal_mode=self.chart_system.sidereal_mode,
            houses_system_identifier=self.chart_system.house_system_identifier,
            perspective_type=self.chart_system.perspective_type,
        )
        self._assert_chart_system(subject)
        return subject

    def create_ephemeris(
        self,
        start_datetime: datetime,
        end_datetime: datetime,
        location: BirthData,
        step_days: int,
        max_days: int,
    ) -> EphemerisDataFactory:
        """Create ephemeris data with the canonical chart-system settings."""
        return EphemerisDataFactory(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            lng=location.longitude,
            lat=location.latitude,
            tz_str=location.timezone,
            step_type="days",
            step=step_days,
            zodiac_type=self.chart_system.zodiac_type,
            sidereal_mode=self.chart_system.sidereal_mode,
            houses_system_identifier=self.chart_system.house_system_identifier,
            perspective_type=self.chart_system.perspective_type,
            max_days=max_days,
        )

    def _assert_chart_system(self, subject: AstrologicalSubjectModel) -> None:
        """Fail fast if a subject was built with the wrong chart system."""
        if subject.zodiac_type != self.chart_system.zodiac_type:
            raise ValueError(
                f"Unexpected zodiac_type {subject.zodiac_type!r}; expected {self.chart_system.zodiac_type!r}"
            )
        if subject.houses_system_identifier != self.chart_system.house_system_identifier:
            raise ValueError(
                "Unexpected houses_system_identifier "
                f"{subject.houses_system_identifier!r}; expected {self.chart_system.house_system_identifier!r}"
            )
        if subject.sidereal_mode != self.chart_system.sidereal_mode:
            raise ValueError(
                f"Unexpected sidereal_mode {subject.sidereal_mode!r}; expected {self.chart_system.sidereal_mode!r}"
            )
        if subject.perspective_type != self.chart_system.perspective_type:
            raise ValueError(
                f"Unexpected perspective_type {subject.perspective_type!r}; expected {self.chart_system.perspective_type!r}"
            )

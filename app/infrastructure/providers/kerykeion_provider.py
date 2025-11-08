"""Kerykeion astrology provider implementation."""

from datetime import datetime
from kerykeion import AstrologicalSubjectFactory, AspectsFactory

from app.core.exceptions import ChartCalculationException, InvalidBirthDataException
from app.core.extractors import extract_celestial_objects, filter_aspects_by_orb, filter_personal_synastry_aspects
from app.config.astrology_presets import AstrologyConfig
from app.domain.models import BirthData, NatalChart, Synastry, Transit
from app.domain.ports import IAstrologyProvider


class KerykeionProvider(IAstrologyProvider):
    """
    Kerykeion-based implementation of the astrology provider port.

    This adapter isolates all Kerykeion-specific code, allowing easy
    substitution with other astrology libraries (Swiss Ephemeris, AstroAPI, etc.)
    """

    def __init__(self, config: AstrologyConfig):
        """
        Initialize the Kerykeion provider with configuration.

        Args:
            config: Astrology configuration (planets, houses, orbs, etc.)
        """
        self.config = config

    def calculate_natal_chart(self, birth_data: BirthData) -> NatalChart:
        """
        Calculate a natal chart using Kerykeion.

        Args:
            birth_data: Birth information

        Returns:
            NatalChart domain model

        Raises:
            InvalidBirthDataException: If birth data is invalid
            ChartCalculationException: If calculation fails
        """
        try:
            # Create Kerykeion astrological subject
            subject = AstrologicalSubjectFactory.from_birth_data(
                name="Subject",
                year=birth_data.year,
                month=birth_data.month,
                day=birth_data.day,
                hour=birth_data.hour,
                minute=birth_data.minute,
                lng=birth_data.longitude,
                lat=birth_data.latitude,
                tz_str=birth_data.timezone,
                online=False
            )

            # Calculate aspects
            aspects_result = AspectsFactory.single_chart_aspects(subject)

            # Extract data using DRY utilities
            planets = extract_celestial_objects(subject, self.config.planets)
            points = extract_celestial_objects(subject, self.config.points)
            houses = extract_celestial_objects(subject, self.config.houses)
            aspects = filter_aspects_by_orb(aspects_result, self.config.natal_orb)

            # Add birth metadata
            birth_metadata = {
                "name": subject.name,
                "date": subject.iso_formatted_local_datetime,
                "location": {
                    "city": subject.city if hasattr(subject, 'city') else None,
                    "nation": subject.nation if hasattr(subject, 'nation') else None,
                    "lat": subject.lat,
                    "lng": subject.lng,
                    "timezone": subject.tz_str
                },
                "lunar_phase": subject.lunar_phase.model_dump() if hasattr(subject, 'lunar_phase') else None
            }

            # Build domain model
            natal_chart = NatalChart(
                birth_data=birth_data,
                planets={**planets, **points, "birth_data": birth_metadata},
                houses=houses,
                points=points,
                aspects=aspects,
                provider_data=subject  # Keep Kerykeion subject for synastry
            )

            return natal_chart

        except ValueError as e:
            raise InvalidBirthDataException(f"Invalid birth data: {str(e)}")
        except Exception as e:
            raise ChartCalculationException(f"Failed to calculate chart: {str(e)}")

    def calculate_synastry(self, chart1: NatalChart, chart2: NatalChart) -> Synastry:
        """
        Calculate synastry aspects using Kerykeion.

        Args:
            chart1: First person's natal chart
            chart2: Second person's natal chart

        Returns:
            Synastry domain model

        Raises:
            ChartCalculationException: If synastry calculation fails
        """
        try:
            # Extract Kerykeion subjects from provider data
            subject1 = chart1.provider_data
            subject2 = chart2.provider_data

            if not subject1 or not subject2:
                raise ChartCalculationException("Charts missing provider data for synastry calculation")

            # Calculate dual chart aspects
            aspects_result = AspectsFactory.dual_chart_aspects(subject1, subject2)

            # Filter aspects by orb
            aspects = filter_aspects_by_orb(aspects_result, self.config.synastry_orb)

            # Filter to personally relevant aspects (remove generational outer-to-outer)
            aspects = filter_personal_synastry_aspects(aspects)

            # Build domain model
            synastry = Synastry(
                chart1=chart1,
                chart2=chart2,
                aspects=aspects
            )

            return synastry

        except Exception as e:
            raise ChartCalculationException(f"Failed to calculate synastry: {str(e)}")

    def calculate_transits(
        self,
        natal_chart: NatalChart,
        transit_date: datetime,
    ) -> Transit:
        """
        Calculate transits using Kerykeion.

        Args:
            natal_chart: The natal chart to calculate transits for
            transit_date: Date/time for transit calculation

        Returns:
            Transit domain model

        Raises:
            ChartCalculationException: If transit calculation fails
        """
        try:
            # Create transit subject for the given date
            birth_data = natal_chart.birth_data
            transit_subject = AstrologicalSubjectFactory.from_birth_data(
                name="Transit",
                year=transit_date.year,
                month=transit_date.month,
                day=transit_date.day,
                hour=transit_date.hour,
                minute=transit_date.minute,
                lng=birth_data.longitude,
                lat=birth_data.latitude,
                tz_str=birth_data.timezone,
                online=False
            )

            # Extract transit planets
            transit_planets = extract_celestial_objects(transit_subject, self.config.planets)

            # Calculate transit-to-natal aspects
            natal_subject = natal_chart.provider_data
            if natal_subject:
                aspects_result = AspectsFactory.dual_chart_aspects(transit_subject, natal_subject)
                transit_to_natal_aspects = filter_aspects_by_orb(aspects_result, self.config.transit_orb)
            else:
                transit_to_natal_aspects = []

            # Calculate current sky aspects (transiting planets to each other)
            sky_aspects_result = AspectsFactory.single_chart_aspects(transit_subject)
            current_sky_aspects = filter_aspects_by_orb(sky_aspects_result, self.config.transit_orb)

            # Build domain model
            transit = Transit(
                date=transit_date,
                planets=transit_planets,
                aspects_to_natal=transit_to_natal_aspects,
                current_sky_aspects=current_sky_aspects
            )

            return transit

        except Exception as e:
            raise ChartCalculationException(f"Failed to calculate transits: {str(e)}")

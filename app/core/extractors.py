"""Shared extraction utilities for DRY compliance."""

from typing import Any


def extract_celestial_objects(
    subject: Any,
    object_names: list[str],
    exclude_fields: set[str] | None = None
) -> dict[str, Any]:
    """
    Extract celestial objects (planets, points, houses) from Kerykeion subject.

    This utility eliminates duplication across extraction patterns in services.

    Args:
        subject: Kerykeion astrological subject
        object_names: List of attribute names to extract (e.g., ['sun', 'moon'])
        exclude_fields: Fields to exclude from model_dump

    Returns:
        Dict mapping object names to their data

    Example:
        planets = extract_celestial_objects(subject, ['sun', 'moon', 'mercury'])
    """
    if exclude_fields is None:
        exclude_fields = {'emoji', 'point_type'}
    result = {}
    for name in object_names:
        obj = getattr(subject, name, None)
        if obj:
            result[name] = obj.model_dump(exclude=exclude_fields)
    return result


def filter_aspects_by_orb(
    aspects_result: Any,
    max_orb: float,
    exclude_fields: set[str] | None = None
) -> list[dict[str, Any]]:
    """
    Extract and filter aspects by orb tolerance.

    This utility eliminates duplication of aspect filtering logic.

    Args:
        aspects_result: AspectsFactory result object
        max_orb: Maximum orb to include (degrees)
        exclude_fields: Fields to exclude from model_dump

    Returns:
        List of aspect dicts filtered by orb tolerance

    Example:
        aspects = filter_aspects_by_orb(aspects_result, max_orb=10.0)
    """
    if exclude_fields is None:
        exclude_fields = {'emoji', 'point_type'}
    aspects = []
    for aspect_obj in aspects_result.aspects:
        if abs(aspect_obj.orbit) < max_orb:
            aspects.append(aspect_obj.model_dump(exclude=exclude_fields))
    return aspects


def filter_personal_synastry_aspects(aspects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Filter synastry aspects to include only personally relevant interactions.

    Removes outer-to-outer planetary aspects (Uranus, Neptune, Pluto),
    which are generational and not specific to individual relationships.

    Keeps:
    - Personal to personal (Sun, Moon, Mercury, Venus, Mars)
    - Personal to outer (e.g., Sun-Pluto, Venus-Neptune)
    - Outer to personal (e.g., Neptune-Moon, Pluto-Venus)

    Removes:
    - Outer to outer (e.g., Uranus-Neptune, Neptune-Pluto)

    Args:
        aspects: List of synastry aspect dicts

    Returns:
        Filtered list excluding generational outer-to-outer aspects

    Example:
        filtered = filter_personal_synastry_aspects(synastry_aspects)
    """
    outer_planets = {'uranus', 'neptune', 'pluto'}

    return [
        aspect for aspect in aspects
        if not (
            aspect['p1_name'].lower() in outer_planets
            and aspect['p2_name'].lower() in outer_planets
        )
    ]

#!/usr/bin/env python3
"""Benchmark soulmate algorithm performance.

Usage:
    cd astrology-service
    python scripts/benchmark_soulmate.py [--compare]

Options:
    --compare    Compare fast vs brute-force method (slow!)
"""

import sys
import time

sys.path.insert(0, ".")

from app.application.soulmate_service import SoulmateService
from app.config.astrology_presets import DetailLevel, get_preset
from app.domain.models import BirthData
from app.infrastructure.providers.kerykeion_provider import KerykeionProvider


def benchmark_ascendant_methods(service: SoulmateService, n_iterations: int = 10):
    """Compare fast vs brute-force ascendant finding methods."""
    print(f"\nComparing _find_hour_for_ascendant methods ({n_iterations} iterations each)...\n")

    # Test parameters
    test_params = (1990, 6, 15, "Lib", 51.5074, -0.1278, "Europe/London")

    # Benchmark fast method
    start = time.perf_counter()
    for _ in range(n_iterations):
        service._find_hour_for_ascendant_fast(*test_params)
    fast_time = time.perf_counter() - start

    # Benchmark brute-force method
    start = time.perf_counter()
    for _ in range(n_iterations):
        service._find_hour_for_ascendant(*test_params)
    brute_time = time.perf_counter() - start

    print(f"  Fast method:        {fast_time:.3f}s total, {fast_time/n_iterations*1000:.1f}ms per call")
    print(f"  Brute-force method: {brute_time:.3f}s total, {brute_time/n_iterations*1000:.1f}ms per call")
    print(f"  Speedup:            {brute_time/fast_time:.1f}x faster")

    # Verify both produce correct sign
    year, month, day, target_sign, lat, lon, tz = test_params
    fast_result = service._find_hour_for_ascendant_fast(*test_params)
    brute_result = service._find_hour_for_ascendant(*test_params)

    # Get actual Ascendant signs for verification
    fast_birth = BirthData(year=year, month=month, day=day, hour=fast_result[0],
                           minute=fast_result[1], latitude=lat, longitude=lon, timezone=tz)
    brute_birth = BirthData(year=year, month=month, day=day, hour=brute_result[0],
                            minute=brute_result[1], latitude=lat, longitude=lon, timezone=tz)

    fast_chart = service.provider.calculate_natal_chart(fast_birth)
    brute_chart = service.provider.calculate_natal_chart(brute_birth)

    fast_asc = fast_chart.points.get("ascendant", {})
    brute_asc = brute_chart.points.get("ascendant", {})

    print(f"\n  Target sign:   {target_sign}")
    print(f"  Fast result:   {fast_result[0]:02d}:{fast_result[1]:02d} -> {fast_asc.get('sign')} ({fast_asc.get('abs_pos', 0):.1f}°)")
    print(f"  Brute result:  {brute_result[0]:02d}:{brute_result[1]:02d} -> {brute_asc.get('sign')} ({brute_asc.get('abs_pos', 0):.1f}°)")


def benchmark_full_algorithm(service: SoulmateService):
    """Benchmark full soulmate chart generation."""
    test_cases = [
        ("London 1990", BirthData(
            year=1990, month=6, day=15, hour=12, minute=0,
            latitude=51.5074, longitude=-0.1278, timezone="Europe/London"
        )),
        ("NYC 1985", BirthData(
            year=1985, month=3, day=21, hour=8, minute=30,
            latitude=40.7128, longitude=-74.0060, timezone="America/New_York"
        )),
        ("Tokyo 1995", BirthData(
            year=1995, month=12, day=1, hour=23, minute=45,
            latitude=35.6762, longitude=139.6503, timezone="Asia/Tokyo"
        )),
        ("Sydney 2000", BirthData(
            year=2000, month=7, day=4, hour=6, minute=15,
            latitude=-33.8688, longitude=151.2093, timezone="Australia/Sydney"
        )),
    ]

    print(f"\nBenchmarking full algorithm ({len(test_cases)} charts)...\n")

    times = []
    for label, birth in test_cases:
        start = time.perf_counter()
        result = service.generate_soulmate_chart(birth)
        elapsed = time.perf_counter() - start
        print(f"  {label}: {elapsed:.2f}s (compatibility: {result.compatibility_percent}%)")
        times.append(elapsed)

    print(f"\n{'='*50}")
    print(f"Total time: {sum(times):.2f}s")
    print(f"Average time: {sum(times)/len(times):.2f}s per chart")
    print(f"Min: {min(times):.2f}s, Max: {max(times):.2f}s")


def main():
    compare_mode = "--compare" in sys.argv

    print("Initializing provider...")
    provider = KerykeionProvider(get_preset(DetailLevel.CORE))
    service = SoulmateService(provider)

    if compare_mode:
        benchmark_ascendant_methods(service, n_iterations=10)
    else:
        benchmark_full_algorithm(service)
        print("\nTip: Run with --compare to compare fast vs brute-force ascendant methods")


if __name__ == "__main__":
    main()

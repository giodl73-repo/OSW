"""Test M2 Drake pathways against small deterministic release-position shifts."""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import statistics

from analyze_pathway_timestep_sensitivity import distance_km
from simulate_oscar_pathways import (
    DEFAULT_RELEASE_TIMES,
    VelocityField,
    gate_releases,
    integrate,
    load_assignment,
    parse_time,
)


KM_PER_DEGREE = 111.195


def gate_basis(releases: list[tuple[float, float]]) -> tuple[tuple[float, float], tuple[float, float]]:
    latitude = sum(point[0] for point in releases) / len(releases)
    north_km = (releases[-1][0] - releases[0][0]) * KM_PER_DEGREE
    east_km = (releases[-1][1] - releases[0][1]) * KM_PER_DEGREE * math.cos(math.radians(latitude))
    length = math.hypot(east_km, north_km)
    tangent = (east_km / length, north_km / length)
    normal = (-tangent[1], tangent[0])
    return tangent, normal


def offset_point(
    latitude: float, longitude: float,
    along_km: float, across_km: float,
    tangent: tuple[float, float], normal: tuple[float, float],
) -> tuple[float, float]:
    east_km = along_km * tangent[0] + across_km * normal[0]
    north_km = along_km * tangent[1] + across_km * normal[1]
    return (
        latitude + north_km / KM_PER_DEGREE,
        longitude + east_km / (KM_PER_DEGREE * math.cos(math.radians(latitude))),
    )


def analyze(
    payload: dict, release_times: tuple[str, ...] = DEFAULT_RELEASE_TIMES,
    release_count: int = 10, offset_km: float = 15,
    duration_days: int = 30, timestep_hours: int = 6,
) -> dict:
    field = VelocityField(payload)
    releases = gate_releases(release_count)
    tangent, normal = gate_basis(releases)
    offsets = (-offset_km, 0.0, offset_km)
    trials = []
    groups = []
    for release_time_text in release_times:
        release_time = parse_time(release_time_text)
        for release_index, (latitude, longitude) in enumerate(releases, 1):
            group_trials = []
            for along_km in offsets:
                for across_km in offsets:
                    shifted_latitude, shifted_longitude = offset_point(
                        latitude, longitude, along_km, across_km, tangent, normal,
                    )
                    result = integrate(
                        field, release_time, shifted_latitude, shifted_longitude,
                        duration_days, timestep_hours, 24,
                    )
                    trial = {
                        "id": f"{release_time_text[:10]}-{release_index:02d}-{along_km:+g}-{across_km:+g}",
                        "base_id": f"{release_time_text[:10]}-{release_index:02d}",
                        "release_time": release_time_text,
                        "release_index": release_index,
                        "along_offset_km": along_km,
                        "across_offset_km": across_km,
                        "release_latitude": shifted_latitude,
                        "release_longitude": shifted_longitude,
                        "status": result["status"],
                        "integrated_hours": result["integrated_hours"],
                        "travelled_km": result["travelled_km"],
                        "endpoint": result["points"][-1],
                    }
                    trials.append(trial); group_trials.append(trial)
            central = next(item for item in group_trials if item["along_offset_km"] == item["across_offset_km"] == 0)
            completed = [item for item in group_trials if item["status"] == "completed"]
            distances = []
            if central["status"] == "completed":
                distances = [distance_km(central["endpoint"], item["endpoint"]) for item in completed]
            groups.append({
                "base_id": central["base_id"],
                "release_time": release_time_text,
                "release_index": release_index,
                "completed": len(completed),
                "terminated": len(group_trials) - len(completed),
                "completion_fraction": len(completed) / len(group_trials),
                "central_status": central["status"],
                "completed_endpoint_separation_from_central_km": None if not distances else {
                    "median": statistics.median(distances), "maximum": max(distances),
                },
            })
    completed_trials = sum(trial["status"] == "completed" for trial in trials)
    fully_stable = sum(group["completed"] == 9 for group in groups)
    fully_lost = sum(group["completed"] == 0 for group in groups)
    mixed = len(groups) - fully_stable - fully_lost
    endpoint_maxima = [
        group["completed_endpoint_separation_from_central_km"]["maximum"]
        for group in groups if group["completed_endpoint_separation_from_central_km"] is not None
    ]
    endpoint_medians = [
        group["completed_endpoint_separation_from_central_km"]["median"]
        for group in groups if group["completed_endpoint_separation_from_central_km"] is not None
    ]
    return {
        "schema": "oceanlines.osw.m2-release-sensitivity.v1",
        "status": "deterministic release-position sensitivity for historical surface-pathway method pilot",
        "velocity_source": {
            "source_sha256": payload["source_sha256"], "field_sha256": payload["field_sha256"],
            "shape": payload["shape"], "space_stride": payload["display_stride"],
        },
        "experiment": {
            "release_times": list(release_times), "base_releases_per_time": release_count,
            "position_design": "3 by 3 deterministic local grid in along-section/across-section coordinates",
            "offset_values_km": list(offsets), "duration_days": duration_days,
            "timestep_hours": timestep_hours, "diffusion": "none",
        },
        "summary": {
            "base_releases": len(groups), "perturbed_trials": len(trials),
            "completed_trials": completed_trials, "terminated_trials": len(trials) - completed_trials,
            "completion_fraction": completed_trials / len(trials),
            "fully_completed_neighborhoods": fully_stable,
            "mixed_neighborhoods": mixed,
            "fully_terminated_neighborhoods": fully_lost,
            "central_completed_neighborhoods": len(endpoint_medians),
            "median_of_completed_endpoint_medians_km": statistics.median(endpoint_medians),
            "p90_nearest_rank_of_completed_endpoint_medians_km": sorted(endpoint_medians)[round((len(endpoint_medians) - 1) * .9)],
            "maximum_completed_endpoint_separation_from_central_km": max(endpoint_maxima),
            "neighborhoods_with_maximum_endpoint_separation_over_200_km": sum(value > 200 for value in endpoint_maxima),
        },
        "groups": groups,
        "trials": trials,
        "interpretation": (
            "Small deterministic release shifts test local pathway robustness only. Equal trial "
            "counts are not probability, water-mass volume, exchange, residence, or heat transport."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-drake-native-2018.js"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-release-sensitivity-2018.json"))
    parser.add_argument("--offset-km", type=float, default=15)
    args = parser.parse_args()
    result = analyze(load_assignment(args.input), offset_km=args.offset_km)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {result['summary']}")


if __name__ == "__main__":
    main()

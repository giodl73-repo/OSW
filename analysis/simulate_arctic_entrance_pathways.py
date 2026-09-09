"""Run deterministic surface pathways from the paired Arctic entrance lanes."""

from __future__ import annotations

import argparse
import json
import pathlib

try:
    from simulate_oscar_pathways import DEFAULT_RELEASE_TIMES, VelocityField, integrate, load_assignment, parse_time
    from analyze_arctic_entrances_motion import sha256_file
except ModuleNotFoundError:
    from analysis.simulate_oscar_pathways import DEFAULT_RELEASE_TIMES, VelocityField, integrate, load_assignment, parse_time
    from analysis.analyze_arctic_entrances_motion import sha256_file


RELEASE_GROUPS = {
    "fram_west_export": {
        "source": "fram", "name": "Fram western export lane", "positive_fate": "southward",
        "points": tuple((78.3333333, 353.0 + index * 5.0 / 7) for index in range(8)), "duration_days": 20,
    },
    "fram_east_inflow": {
        "source": "fram", "name": "Fram eastern inflow lane", "positive_fate": "northward",
        "points": tuple((78.3333333, 365.0 + index * 7.5 / 9) for index in range(10)), "duration_days": 20,
    },
    "barents_inflow": {
        "source": "barents", "name": "Barents eastward entrance", "positive_fate": "eastward",
        "points": tuple((71.0 + index * 3.75 / 9, 20.6666667) for index in range(10)), "duration_days": 30,
    },
}


def fate(group: str, release_latitude: float, release_longitude: float, track: dict) -> str:
    endpoint = track["points"][-1]
    if track["status"] != "completed":
        return "terminated"
    if group == "fram_west_export":
        return "southward" if endpoint["latitude"] < release_latitude else "other"
    if group == "fram_east_inflow":
        return "northward" if endpoint["latitude"] > release_latitude else "other"
    return "eastward" if endpoint["longitude"] > release_longitude else "other"


def simulate(fram: dict, barents: dict, release_times: tuple[str, ...] = DEFAULT_RELEASE_TIMES) -> dict:
    fields = {"fram": VelocityField(fram), "barents": VelocityField(barents)}
    tracks = []
    for group_name, group in RELEASE_GROUPS.items():
        field = fields[group["source"]]
        for release_time_text in release_times:
            release_time = parse_time(release_time_text)
            for index, (latitude, longitude) in enumerate(group["points"], 1):
                if field.sample(release_time, latitude, longitude) is None:
                    raise ValueError(f"release lacks wet stencil: {group_name} {release_time_text} {index}")
                result = integrate(field, release_time, latitude, longitude, group["duration_days"], 6, 24)
                tracks.append({
                    "id": f"{group_name}-{release_time_text[:10]}-{index:02d}",
                    "group": group_name,
                    "group_name": group["name"],
                    "release_time": release_time_text,
                    "release_index": index,
                    "release_latitude": latitude,
                    "release_longitude": longitude,
                    "declared_duration_days": group["duration_days"],
                    **result,
                    "fate": fate(group_name, latitude, longitude, result),
                })
    summaries = []
    for group_name, group in RELEASE_GROUPS.items():
        selected = [track for track in tracks if track["group"] == group_name]
        fates = {name: sum(track["fate"] == name for track in selected) for name in (group["positive_fate"], "other", "terminated")}
        summaries.append({
            "group": group_name,
            "name": group["name"],
            "released": len(selected),
            "completed": sum(track["status"] == "completed" for track in selected),
            "fates": fates,
            "median_completed_distance_km": sorted(track["travelled_km"] for track in selected if track["status"] == "completed")[sum(track["status"] == "completed" for track in selected) // 2] if any(track["status"] == "completed" for track in selected) else None,
        })
    return {
        "schema": "oceanlines.osw.m2-arctic-entrance-pathways.v1",
        "status": "paired_historical_deterministic_surface_pathways",
        "release_times": list(release_times),
        "solver_contract": {"integration": "forward RK4", "timestep_hours": 6, "output_hours": 24, "spatial_interpolation": "strict four-wet-corner bilinear", "temporal_interpolation": "linear", "diffusion": "none", "coastal_behavior": "terminate at invalid stencil or domain"},
        "release_groups": [{key: value for key, value in group.items() if key != "points"} | {"group": name, "points": [{"latitude": lat, "longitude": lon} for lat, lon in group["points"]]} for name, group in RELEASE_GROUPS.items()],
        "summaries": summaries,
        "tracks": tracks,
        "boundary": "Deterministic equal-count surface pathways through one historical year of older OSCAR 2017.0 data. Track fate and completion are not probability, volume, residence, Atlantic Water identity, full-depth circulation, temperature advection, or heat transport. Fram runs are limited to 20 days by the 80N product boundary; Barents runs use 30 days.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fram", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-fram-native-2018.js"))
    parser.add_argument("--barents", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-barents-native-2018.js"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m2-arctic-entrance-pathways-2018.json"))
    args = parser.parse_args()
    fram = load_assignment(args.fram); barents = load_assignment(args.barents)
    result = simulate(fram, barents)
    result["sources"] = [
        {"path": str(args.fram), "sha256": sha256_file(args.fram), "field_sha256": fram["field_sha256"]},
        {"path": str(args.barents), "sha256": sha256_file(args.barents), "field_sha256": barents["field_sha256"]},
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {[(item['group'], item['completed']) for item in result['summaries']]}")


if __name__ == "__main__":
    main()

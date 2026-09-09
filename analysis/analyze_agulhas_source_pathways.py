"""Run a source-tagged Agulhas pathway and fate-definition sensitivity audit."""

from __future__ import annotations

import argparse
import json
import pathlib

try:
    from analyze_agulhas_motion import sha256_file
    from simulate_oscar_pathways import VelocityField, integrate, load_assignment, parse_time
except ModuleNotFoundError:
    from analysis.analyze_agulhas_motion import sha256_file
    from analysis.simulate_oscar_pathways import VelocityField, integrate, load_assignment, parse_time


RELEASE_TIMES = ("2018-01-15T00:00:00Z", "2018-03-15T00:00:00Z", "2018-06-15T00:00:00Z")
CENTERS = (
    {"id": "A", "latitude": -32.5, "longitude": 30.5},
    {"id": "B", "latitude": -33.0, "longitude": 30.0},
    {"id": "C", "latitude": -33.5, "longitude": 29.5},
    {"id": "D", "latitude": -34.0, "longitude": 29.0},
)
OFFSETS = (-0.1, 0.0, 0.1)
WEST_GATES = (12.0, 15.0, 18.0)
EAST_GATES = (33.0, 35.0, 37.0)
BASELINE_WEST = 15.0
BASELINE_EAST = 35.0


def crossing_flags(points: list[dict], west_gate: float, east_gate: float) -> tuple[bool, bool]:
    cape = any(point["longitude"] <= west_gate and -42 <= point["latitude"] <= -28 for point in points)
    returning = any(point["longitude"] >= east_gate and point["latitude"] <= -34 for point in points)
    return cape, returning


def classify(track: dict, west_gate: float, east_gate: float) -> str:
    cape, returning = crossing_flags(track["points"], west_gate, east_gate)
    if cape and returning:
        return "both_thresholds"
    if cape:
        return "cape_basin"
    if returning:
        return "return_corridor"
    if track["status"] != "completed":
        return "terminated"
    return "unresolved"


def count_fates(tracks: list[dict], west_gate: float, east_gate: float) -> dict:
    names = ("cape_basin", "return_corridor", "both_thresholds", "unresolved", "terminated")
    counts = {name: 0 for name in names}
    for track in tracks:
        counts[classify(track, west_gate, east_gate)] += 1
    return counts


def simulate(payload: dict, duration_days: int = 150) -> list[dict]:
    field = VelocityField(payload)
    tracks = []
    for release_time in RELEASE_TIMES:
        for center in CENTERS:
            for latitude_offset in OFFSETS:
                for longitude_offset in OFFSETS:
                    result = integrate(
                        field,
                        parse_time(release_time),
                        center["latitude"] + latitude_offset,
                        center["longitude"] + longitude_offset,
                        duration_days=duration_days,
                        timestep_hours=6,
                        output_hours=24,
                    )
                    track = {
                        "id": f"{release_time[:10]}-{center['id']}-{latitude_offset:+.1f}-{longitude_offset:+.1f}",
                        "release_time": release_time,
                        "center_id": center["id"],
                        "release_latitude": center["latitude"] + latitude_offset,
                        "release_longitude": center["longitude"] + longitude_offset,
                        "latitude_offset_degrees": latitude_offset,
                        "longitude_offset_degrees": longitude_offset,
                        **result,
                    }
                    track["baseline_fate"] = classify(track, BASELINE_WEST, BASELINE_EAST)
                    tracks.append(track)
    return tracks


def run(path: pathlib.Path, duration_days: int = 150) -> dict:
    payload = load_assignment(path)
    tracks = simulate(payload, duration_days)
    baseline = count_fates(tracks, BASELINE_WEST, BASELINE_EAST)
    release_summaries = []
    for release_time in RELEASE_TIMES:
        group = [track for track in tracks if track["release_time"] == release_time]
        release_summaries.append({"release_time": release_time, "released": len(group), "fates": count_fates(group, BASELINE_WEST, BASELINE_EAST)})
    sensitivity = [
        {"west_gate_east": west, "east_gate_east": east, "fates": count_fates(tracks, west, east)}
        for west in WEST_GATES for east in EAST_GATES
    ]
    return {
        "schema": "oceanlines.osw.m2-agulhas-source-pathways.v1",
        "status": "historical_source_tagged_pathway_fate_sensitivity",
        "period": {"release_start": RELEASE_TIMES[0], "release_stop": RELEASE_TIMES[-1], "duration_days": duration_days},
        "release_contract": {
            "centers": list(CENTERS),
            "neighborhood": "3 × 3 deterministic latitude/longitude offsets around each center",
            "offset_degrees": list(OFFSETS),
            "release_times": list(RELEASE_TIMES),
            "count": len(tracks),
            "weighting": "equal-count method ensemble; not area, current-speed, volume, or transport weighted",
        },
        "baseline_gate_contract": {
            "cape_basin": "first sampled point at or west of 15E between 42S and 28S",
            "return_corridor": "first sampled point at or east of 35E and south of 34S",
            "both_thresholds": "track reaches both declared thresholds; retained instead of forcing one fate",
        },
        "baseline_fates": baseline,
        "release_summaries": release_summaries,
        "gate_sensitivity": sensitivity,
        "tracks": tracks,
        "source": {
            "path": str(path),
            "sha256": sha256_file(path),
            "source_sha256": payload["source_sha256"],
            "field_sha256": payload["field_sha256"],
            "shape": payload["shape"],
            "nominal_depth_m": payload["nominal_depth_m"],
        },
        "solver_contract": "Forward deterministic RK4; six-hour steps; daily saved positions; strict jointly wet four-corner bilinear stencil; linear time interpolation; no diffusion.",
        "boundary": "The ensemble tests release-position, release-time, and fate-gate sensitivity in one historical nominal-15-m OSCAR year. Counts are method outcomes, not leakage percentages, probabilities, volume or heat transports, water-mass identities, eddy tracking, climatology, or overturning estimates. Unresolved means neither declared threshold was reached within 150 days.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-agulhas-native-2018.js"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m2-agulhas-source-pathways-2018.json"))
    parser.add_argument("--duration-days", type=int, default=150)
    args = parser.parse_args()
    result = run(args.input, args.duration_days)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

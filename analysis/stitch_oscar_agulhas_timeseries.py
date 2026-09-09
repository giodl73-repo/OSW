"""Stitch the two OSCAR longitude halves around the Agulhas archive seam."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

try:
    from fetch_oscar_timeseries_pilot import write_artifact
    from simulate_oscar_pathways import load_assignment
    from analyze_arctic_entrances_motion import sha256_file
except ModuleNotFoundError:
    from analysis.fetch_oscar_timeseries_pilot import write_artifact
    from analysis.simulate_oscar_pathways import load_assignment
    from analysis.analyze_arctic_entrances_motion import sha256_file


def stitch_rows(values_west: list, values_east: list, rows: int, west_columns: int, east_columns: int) -> list:
    merged = []
    for row in range(rows):
        merged.extend(values_west[row * west_columns:(row + 1) * west_columns])
        merged.extend(values_east[row * east_columns:(row + 1) * east_columns])
    return merged


def run(west_path: pathlib.Path, east_path: pathlib.Path) -> dict:
    west = load_assignment(west_path); east = load_assignment(east_path)
    if west["period_start"] != east["period_start"] or west["period_stop"] != east["period_stop"]:
        raise ValueError("source periods do not match")
    if west["latitude_values"] != east["latitude_values"]:
        raise ValueError("source latitude axes do not match")
    if [frame["time"] for frame in west["frames"]] != [frame["time"] for frame in east["frames"]]:
        raise ValueError("source time axes do not match")
    rows = len(west["latitude_values"]); west_columns = len(west["longitude_values"]); east_columns = len(east["longitude_values"])
    west_longitudes = [round(value - 360, 10) for value in west["longitude_values"]]
    longitudes = west_longitudes + east["longitude_values"]
    if any(b <= a for a, b in zip(longitudes, longitudes[1:])):
        raise ValueError("stitched longitude axis is not strictly increasing")
    frames = []
    for west_frame, east_frame in zip(west["frames"], east["frames"]):
        u = stitch_rows(west_frame["u_mm_s"], east_frame["u_mm_s"], rows, west_columns, east_columns)
        v = stitch_rows(west_frame["v_mm_s"], east_frame["v_mm_s"], rows, west_columns, east_columns)
        frames.append({"time": west_frame["time"], "valid_cells": sum(a is not None and b is not None for a, b in zip(u, v)), "u_mm_s": u, "v_mm_s": v})
    field_sha = hashlib.sha256(json.dumps(frames, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
    sources = [{"path": str(path), "sha256": sha256_file(path), "source_sha256": payload["source_sha256"], "field_sha256": payload["field_sha256"], "query_url": payload["query_url"]} for path, payload in ((west_path, west), (east_path, east))]
    combined_source_sha = hashlib.sha256(json.dumps(sources, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    result = {key: value for key, value in east.items() if key not in ("frames", "longitude_values", "shape", "sampled_extent", "source_sha256", "field_sha256", "query_url", "source")}
    result.update({
        "schema": "oceanlines.oscar.stitched-historical-timeseries.v1",
        "status": "historical one-year seam-stitched surface-velocity solver input",
        "source": "Two checksum-pinned NOAA PIFSC ERDDAP OSCAR subsets joined without interpolation",
        "source_sha256": combined_source_sha,
        "field_sha256": field_sha,
        "query_url": [source["query_url"] for source in sources],
        "shape": [len(frames), rows, len(longitudes)],
        "longitude_values": longitudes,
        "sampled_extent": {"north": max(west["latitude_values"]), "south": min(west["latitude_values"]), "west": min(longitudes), "east": max(longitudes)},
        "frames": frames,
        "stitched_sources": sources,
        "stitch_contract": "Convert 365–379.666667 degrees east to 5–19.666667 degrees east, then concatenate each latitude row before the untouched 20–55 degree east subset. No interpolation, averaging, or duplicate seam column.",
        "boundary": west["boundary"] + " The 20E archive seam is a storage artifact; this stitch changes longitude labels and row layout only.",
    })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--west", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-agulhas-west-native-2018.js"))
    parser.add_argument("--east", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-agulhas-east-native-2018.js"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-agulhas-native-2018.js"))
    args = parser.parse_args()
    payload = run(args.west, args.east)
    write_artifact(payload, args.output)
    print(f"wrote {args.output} ({payload['shape'][0]} x {payload['shape'][1]} x {payload['shape'][2]})")
    print(f"field sha256 {payload['field_sha256']}")


if __name__ == "__main__":
    main()

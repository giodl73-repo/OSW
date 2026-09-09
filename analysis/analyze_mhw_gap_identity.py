"""Test whether OSW-D3 and the post-gap footprint reconnect under declared policies."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import tempfile
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "atlas" / "data" / "noaa-crw-mhw-point-north-atlantic-2026.json"
DEFAULT_POINT = ROOT / "research" / "osw-d1-noaa-crw-mhw-point-2026.json"
DEFAULT_LINEAGE = ROOT / "research" / "osw-d3-noaa-crw-mhw-lineage-2026.json"
DEFAULT_OUTPUT = ROOT / "research" / "osw-d4-noaa-crw-mhw-gap-identity-2026.json"
PRE_GAP_DATE = "2026-08-10"
GAP_DATE = "2026-08-11"
POST_GAP_DATE = "2026-08-12"
POST_GAP_END = "2026-08-18"


def load_module(filename, name):
    path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FOOTPRINT = load_module("derive_noaa_crw_mhw_footprint.py", "osw_footprint")
TRACK = load_module("track_noaa_crw_mhw_footprint.py", "osw_tracker")


def decode_runs(rows, latitudes, longitudes):
    lat_index = {round(float(value), 3): index for index, value in enumerate(latitudes)}
    lon_index = {round(float(value), 3): index for index, value in enumerate(longitudes)}
    component = set()
    for latitude, runs in rows:
        y = lat_index[round(latitude, 3)]
        for west, east, _category in runs:
            x = lon_index[round(west, 3)]
            stop = lon_index[round(east, 3)]
            component.update((y, index) for index in range(x, stop + 1))
    return component


def bridge_metrics(before, after):
    intersection = len(before & after)
    union = len(before | after)
    return {
        "intersection_pixels": intersection,
        "iou": round(intersection / union, 4),
        "pre_gap_retained_fraction": round(intersection / len(before), 4),
        "post_gap_inherited_fraction": round(intersection / len(after), 4),
        "spatial_dilation_cells_required": 0 if intersection else None,
    }


def build(source_path=DEFAULT_SOURCE, point_path=DEFAULT_POINT, lineage_path=DEFAULT_LINEAGE, output_path=DEFAULT_OUTPUT):
    source_path, point_path, lineage_path, output_path = map(Path, (source_path, point_path, lineage_path, output_path))
    source = json.loads(source_path.read_text(encoding="utf-8"))
    point = json.loads(point_path.read_text(encoding="utf-8"))
    lineage = json.loads(lineage_path.read_text(encoding="utf-8"))
    wanted_dates = [item["date"] for item in source["files"] if PRE_GAP_DATE <= item["date"] <= POST_GAP_END]
    files = [item for item in source["files"] if item["date"] in wanted_dates]
    fields = {}
    with tempfile.TemporaryDirectory(prefix="osw-crw-gap-") as temporary:
        paths = TRACK.download_and_verify(files, Path(temporary))
        for date in wanted_dates:
            fields[date] = TRACK.read_field(paths[date])
    latitudes, longitudes, _, _ = fields[PRE_GAP_DATE]
    anchor_position = source["coordinate"]
    anchor = (
        int(abs(latitudes - anchor_position["latitude_degrees_north"]).argmin()),
        int(abs(longitudes - anchor_position["longitude_degrees_east"]).argmin()),
    )
    pre_rows = next(item["component_rows"] for item in lineage["daily_footprints"] if item["date"] == PRE_GAP_DATE)
    before = decode_runs(pre_rows, latitudes, longitudes)
    gap_active = fields[GAP_DATE][3]
    post_categories, post_active = fields[POST_GAP_DATE][2], fields[POST_GAP_DATE][3]
    after = FOOTPRINT.connected_component(post_active, anchor)
    if not after:
        raise ValueError("post-gap anchor component is missing")
    bridge = bridge_metrics(before, after)
    if bridge["intersection_pixels"] == 0:
        raise ValueError("expected exact spatial overlap across the declared one-day gap")

    post_daily = []
    current = after
    for date in wanted_dates[wanted_dates.index(POST_GAP_DATE) :]:
        categories, active = fields[date][2], fields[date][3]
        if date != POST_GAP_DATE:
            selected, _ = TRACK.select_successor(active, current)
            if selected is None:
                break
            current = selected["component"]
        post_daily.append({
            "date": date,
            "summary": FOOTPRINT.summarize(current, categories, latitudes, longitudes),
            "component_rows": FOOTPRINT.encode_runs(current, categories, latitudes, longitudes),
        })
    if post_daily[-1]["date"] != POST_GAP_END:
        raise ValueError("post-gap qualified run did not form the expected exact lineage")
    overlap_rows = FOOTPRINT.encode_runs(before & after, post_categories, latitudes, longitudes)
    gap_intersection = sum(1 for cell in before if gap_active[cell])
    point_event = point["events"][0]
    payload = {
        "schema": "osw.ocean-object-identity-sensitivity.v1",
        "detection_id": "OSW-D4",
        "status": "policy_dependent_reconnection",
        "object_id": "OBJ046",
        "object_name": "marine heatwave",
        "source_artifacts": [
            {"path": source_path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(source_path.read_bytes()).hexdigest()},
            {"path": point_path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(point_path.read_bytes()).hexdigest()},
            {"path": lineage_path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(lineage_path.read_bytes()).hexdigest()},
        ],
        "gap": {"date": GAP_DATE, "days": 1, "active_pre_gap_pixels_remaining_on_gap_day": gap_intersection},
        "qualified_runs": {
            "pre_gap": {"start": point_event["start_date"], "end": PRE_GAP_DATE, "days": 19},
            "post_gap": {"start": POST_GAP_DATE, "end": POST_GAP_END, "days": 7},
        },
        "bridge_metrics": bridge,
        "policy_bakeoff": [
            {"policy": "daily exact-pixel inheritance", "reconnects": False, "reason": "the August 11 threshold field contains none of the August 10 footprint pixels"},
            {"policy": "skip one gap day, then require exact spatial overlap", "reconnects": True, "reason": f'{bridge["intersection_pixels"]} exact pixels are shared by the August 10 and August 12 components'},
            {"policy": "skip one gap day and require spatial dilation", "reconnects": True, "reason": "zero dilation cells are required because exact overlap already exists"},
        ],
        "pre_gap_footprint": {"date": PRE_GAP_DATE, "component_rows": pre_rows},
        "post_gap_lineage": {"start": POST_GAP_DATE, "end": POST_GAP_END, "day_count": len(post_daily), "daily_footprints": post_daily},
        "exact_overlap_rows": overlap_rows,
        "identity_evaluation": {
            "result": "policy_dependent",
            "finding": "The two duration-qualified runs are separate under uninterrupted daily inheritance and one event under a declared one-day temporal-gap rule; no spatial displacement allowance is needed.",
        },
        "boundary": "This is an identity-policy sensitivity, not evidence that threshold-state pixels contain the same water parcels or causal mechanism. The reconnection is supported by strong exact geographic overlap but still crosses one day with no threshold-active inheritance. Different minimum-overlap, duration, connectivity, and gap rules can change the answer.",
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--point", type=Path, default=DEFAULT_POINT)
    parser.add_argument("--lineage", type=Path, default=DEFAULT_LINEAGE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build(args.source, args.point, args.lineage, args.output)
    print(f'wrote {args.output}: {payload["bridge_metrics"]["intersection_pixels"]} exact bridge pixels')


if __name__ == "__main__":
    main()

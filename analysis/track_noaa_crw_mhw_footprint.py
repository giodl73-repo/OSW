"""Track OSW-D2 through daily NOAA CRW fields by explicit pixel inheritance."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import tempfile
import urllib.request
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "atlas" / "data" / "noaa-crw-mhw-point-north-atlantic-2026.json"
DEFAULT_SEED = ROOT / "research" / "osw-d2-noaa-crw-mhw-footprint-20260801.json"
DEFAULT_OUTPUT = ROOT / "research" / "osw-d3-noaa-crw-mhw-lineage-2026.json"
ANCHOR_START = "2026-07-23"


def footprint_module():
    path = Path(__file__).with_name("derive_noaa_crw_mhw_footprint.py")
    spec = importlib.util.spec_from_file_location("osw_footprint", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FOOTPRINT = footprint_module()


def overlapping_components(active, previous):
    candidates = []
    consumed = set()
    for seed in sorted(cell for cell in previous if active[cell]):
        if seed in consumed:
            continue
        component = FOOTPRINT.connected_component(active, seed)
        consumed.update(component)
        intersection = len(component & previous)
        union = len(component | previous)
        candidates.append({
            "component": component,
            "intersection_pixels": intersection,
            "iou": intersection / union,
            "previous_retained_fraction": intersection / len(previous),
            "current_inherited_fraction": intersection / len(component),
        })
    return sorted(
        candidates,
        key=lambda item: (-item["intersection_pixels"], -item["iou"], min(item["component"])),
    )


def select_successor(active, previous):
    candidates = overlapping_components(active, previous)
    return (candidates[0], candidates) if candidates else (None, [])


def haversine_km(first, second):
    lat1, lon1 = map(math.radians, first)
    lat2, lon2 = map(math.radians, second)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    value = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * FOOTPRINT.EARTH_RADIUS_KM * math.asin(math.sqrt(value))


def download_and_verify(files, directory):
    paths = {}
    for index, item in enumerate(files, 1):
        print(f'downloading tracking field {index}/{len(files)} - {item["date"]}', flush=True)
        path = directory / item["url"].rsplit("/", 1)[-1]
        request = urllib.request.Request(item["url"], headers={"User-Agent": "OSW evidence receipt/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response, path.open("wb") as handle:
            while chunk := response.read(1024 * 1024):
                handle.write(chunk)
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["raw_file_sha256"]:
            raise ValueError(f'raw checksum mismatch for {item["date"]}')
        paths[item["date"]] = path
    return paths


def read_field(path):
    from netCDF4 import Dataset
    with Dataset(path) as dataset:
        latitudes = np.asarray(dataset.variables["lat"][:])
        longitudes = np.asarray(dataset.variables["lon"][:])
        categories = np.asarray(dataset.variables["heatwave_category"][0])
        masks = np.asarray(dataset.variables["mask"][0])
    return latitudes, longitudes, categories, (categories > 0) & (masks == 0)


def build(source_path=DEFAULT_SOURCE, seed_path=DEFAULT_SEED, output_path=DEFAULT_OUTPUT):
    source_path, seed_path, output_path = Path(source_path), Path(seed_path), Path(output_path)
    source = json.loads(source_path.read_text(encoding="utf-8"))
    seed_receipt = json.loads(seed_path.read_text(encoding="utf-8"))
    dates = [item["date"] for item in source["files"]]
    anchor_position = source["coordinate"]
    with tempfile.TemporaryDirectory(prefix="osw-crw-lineage-") as temporary:
        paths = download_and_verify(source["files"], Path(temporary))
        latitudes, longitudes, categories, active = read_field(paths[ANCHOR_START])
        anchor = (
            int(abs(latitudes - anchor_position["latitude_degrees_north"]).argmin()),
            int(abs(longitudes - anchor_position["longitude_degrees_east"]).argmin()),
        )
        start_component = FOOTPRINT.connected_component(active, anchor)
        if not start_component:
            raise ValueError("anchor is inactive on its duration-qualified start date")
        tracked = {ANCHOR_START: {"component": start_component, "categories": categories}}
        diagnostics = {}
        forward_stop = None
        backward_stop = None

        start_index = dates.index(ANCHOR_START)
        previous = start_component
        for date in dates[start_index + 1 :]:
            _, _, categories, active = read_field(paths[date])
            selected, candidates = select_successor(active, previous)
            if selected is None:
                forward_stop = {"date": date, "reason": "no active component inherits any exact pixel from the preceding lineage footprint"}
                break
            tracked[date] = {"component": selected["component"], "categories": categories}
            diagnostics[(dates[dates.index(date) - 1], date)] = (selected, candidates, "forward")
            previous = selected["component"]

        following = start_component
        for date in reversed(dates[:start_index]):
            _, _, categories, active = read_field(paths[date])
            selected, candidates = select_successor(active, following)
            if selected is None:
                backward_stop = {"date": date, "reason": "no active component shares any exact pixel with the following lineage footprint"}
                break
            tracked[date] = {"component": selected["component"], "categories": categories}
            diagnostics[(date, dates[dates.index(date) + 1])] = (selected, candidates, "backward")
            following = selected["component"]

    ordered_dates = [date for date in dates if date in tracked]
    seed_date = seed_receipt["date"]
    seed_rows = FOOTPRINT.encode_runs(tracked[seed_date]["component"], tracked[seed_date]["categories"], latitudes, longitudes)
    if seed_rows != seed_receipt["component_rows"]:
        raise ValueError("tracked lineage does not reproduce the OSW-D2 seed footprint")

    daily = []
    for date in ordered_dates:
        item = tracked[date]
        daily.append({
            "date": date,
            "summary": FOOTPRINT.summarize(item["component"], item["categories"], latitudes, longitudes),
            "component_rows": FOOTPRINT.encode_runs(item["component"], item["categories"], latitudes, longitudes),
        })
    transitions = []
    for first, second in zip(ordered_dates, ordered_dates[1:]):
        previous = tracked[first]["component"]
        current = tracked[second]["component"]
        intersection = len(previous & current)
        diagnostic = diagnostics[(first, second)]
        candidates = diagnostic[1]
        first_centroid = daily[ordered_dates.index(first)]["summary"]["centroid"]
        second_centroid = daily[ordered_dates.index(second)]["summary"]["centroid"]
        transitions.append({
            "from": first,
            "to": second,
            "intersection_pixels": intersection,
            "iou": round(intersection / len(previous | current), 4),
            "previous_retained_fraction": round(intersection / len(previous), 4),
            "current_inherited_fraction": round(intersection / len(current), 4),
            "overlapping_component_candidates": len(candidates),
            "branch_ambiguity": len(candidates) > 1,
            "extension_direction": diagnostic[2],
            "centroid_displacement_km": round(haversine_km(
                (first_centroid["latitude_degrees_north"], first_centroid["longitude_degrees_east"]),
                (second_centroid["latitude_degrees_north"], second_centroid["longitude_degrees_east"]),
            ), 2),
        })
    areas = [item["summary"]["area_km2"] for item in daily]
    displacements = [item["centroid_displacement_km"] for item in transitions]
    payload = {
        "schema": "osw.tracked-ocean-footprint.v1",
        "detection_id": "OSW-D3",
        "status": "primary_overlap_lineage",
        "object_id": "OBJ046",
        "object_name": "marine heatwave",
        "source_artifact": source_path.relative_to(ROOT).as_posix(),
        "source_artifact_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "seed_artifact": seed_path.relative_to(ROOT).as_posix(),
        "seed_artifact_sha256": hashlib.sha256(seed_path.read_bytes()).hexdigest(),
        "method": {
            "daily_footprint": "unmasked category > 0, native-grid four-neighbor component",
            "seed": "component containing the OSW-D1 anchor on its 2026-07-23 qualifying start date",
            "lineage": "in each adjacent daily field, select the component inheriting the greatest number of exact pixels",
            "minimum_overlap": "at least one exact native-grid pixel; all overlap fractions are reported",
            "longitude_periodicity": True,
            "split_policy": "follow the greatest-intersection child and report the number of overlapping candidates",
            "merge_policy": "accept the inherited component and expose overlap dilution through current-inherited fraction",
        },
        "tracked_window": {
            "start": ordered_dates[0], "end": ordered_dates[-1], "day_count": len(ordered_dates),
            "left_censored": ordered_dates[0] == dates[0], "right_censored": ordered_dates[-1] == dates[-1],
        },
        "summary": {
            "minimum_daily_area_km2": min(areas), "maximum_daily_area_km2": max(areas),
            "mean_daily_area_km2": round(sum(areas) / len(areas), 1),
            "total_centroid_path_km": round(sum(displacements), 1),
            "maximum_daily_centroid_displacement_km": max(displacements),
            "minimum_daily_iou": min(item["iou"] for item in transitions),
            "minimum_intersection_pixels": min(item["intersection_pixels"] for item in transitions),
            "minimum_previous_retained_fraction": min(item["previous_retained_fraction"] for item in transitions),
            "branch_ambiguous_transition_count": sum(item["branch_ambiguity"] for item in transitions),
            "maximum_overlapping_component_candidates": max(item["overlapping_component_candidates"] for item in transitions),
        },
        "lineage_limits": {"preceding": backward_stop, "following": forward_stop},
        "daily_footprints": daily,
        "transitions": transitions,
        "identity_evaluation": {
            "result": "pass",
            "test": "Every adjacent daily footprint in the declared lineage inherits native pixels from its predecessor under one governed split/merge rule.",
            "finding": f'{len(ordered_dates)} daily footprints form one explicit primary-overlap lineage from {ordered_dates[0]} through {ordered_dates[-1]}.',
        },
        "boundary": "A grid-overlap lineage of thresholded surface states, not a materially advected water body. One-pixel overlap is permissive; reported IoU and inheritance minima reveal weak links. The lineage is censored wherever it reaches the 32-day source window. Alternative connectivity, size, overlap, split, and merge policies may produce different systems.",
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build(args.source, args.seed, args.output)
    window = payload["tracked_window"]
    print(f'wrote {args.output}: {window["day_count"]} days, {window["start"]} through {window["end"]}')


if __name__ == "__main__":
    main()

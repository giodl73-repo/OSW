"""Extract the connected peak-day footprint containing OSW-D1's anchor pixel."""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
import math
import tempfile
import urllib.request
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "atlas" / "data" / "noaa-crw-mhw-point-north-atlantic-2026.json"
DEFAULT_OUTPUT = ROOT / "research" / "osw-d2-noaa-crw-mhw-footprint-20260801.json"
TARGET_DATE = "2026-08-01"
EARTH_RADIUS_KM = 6371.0088


def connected_component(active, start, periodic_longitude=True):
    height, width = active.shape
    if not active[start]:
        return set()
    found = {start}
    queue = deque([start])
    while queue:
        y, x = queue.popleft()
        neighbors = [(y - 1, x), (y + 1, x)]
        if periodic_longitude:
            neighbors.extend([(y, (x - 1) % width), (y, (x + 1) % width)])
        else:
            neighbors.extend([(y, x - 1), (y, x + 1)])
        for yy, xx in neighbors:
            if 0 <= yy < height and 0 <= xx < width and active[yy, xx] and (yy, xx) not in found:
                found.add((yy, xx))
                queue.append((yy, xx))
    return found


def encode_runs(component, categories, latitudes, longitudes):
    rows = []
    by_y = {}
    for y, x in component:
        by_y.setdefault(y, []).append(x)
    for y in sorted(by_y):
        xs = sorted(by_y[y])
        runs = []
        start = previous = xs[0]
        category = int(categories[y, start])
        for x in xs[1:]:
            next_category = int(categories[y, x])
            if x != previous + 1 or next_category != category:
                runs.append([round(float(longitudes[start]), 3), round(float(longitudes[previous]), 3), category])
                start, category = x, next_category
            previous = x
        runs.append([round(float(longitudes[start]), 3), round(float(longitudes[previous]), 3), category])
        rows.append([round(float(latitudes[y]), 3), runs])
    return rows


def cell_area_km2(latitude, resolution=0.05):
    south = math.radians(latitude - resolution / 2)
    north = math.radians(latitude + resolution / 2)
    return EARTH_RADIUS_KM ** 2 * math.radians(resolution) * (math.sin(north) - math.sin(south))


def summarize(component, categories, latitudes, longitudes, resolution=0.05):
    areas = {(y, x): cell_area_km2(float(latitudes[y]), resolution) for y, x in component}
    total_area = sum(areas.values())
    category_counts = {}
    category_areas = {}
    for cell, area in areas.items():
        category = int(categories[cell])
        category_counts[str(category)] = category_counts.get(str(category), 0) + 1
        category_areas[str(category)] = category_areas.get(str(category), 0.0) + area
    centroid_lat = sum(float(latitudes[y]) * area for (y, _x), area in areas.items()) / total_area
    centroid_lon = sum(float(longitudes[x]) * area for (_y, x), area in areas.items()) / total_area
    ys = [cell[0] for cell in component]
    xs = [cell[1] for cell in component]
    return {
        "pixel_count": len(component),
        "area_km2": round(total_area, 1),
        "centroid": {"latitude_degrees_north": round(centroid_lat, 3), "longitude_degrees_east": round(centroid_lon, 3)},
        "bounds_cell_centers": {
            "south": round(float(latitudes[min(ys)]), 3), "north": round(float(latitudes[max(ys)]), 3),
            "west": round(float(longitudes[min(xs)]), 3), "east": round(float(longitudes[max(xs)]), 3),
        },
        "category_pixel_counts": category_counts,
        "category_areas_km2": {key: round(value, 1) for key, value in category_areas.items()},
        "maximum_category": max(int(categories[cell]) for cell in component),
        "touches_global_grid_edge": min(ys) == 0 or max(ys) == len(latitudes) - 1 or min(xs) == 0 or max(xs) == len(longitudes) - 1,
    }


def build(source_path=DEFAULT_SOURCE, output_path=DEFAULT_OUTPUT):
    try:
        from netCDF4 import Dataset
    except ImportError as error:
        raise RuntimeError("footprint extraction requires requirements-observations.txt") from error
    source_path, output_path = Path(source_path), Path(output_path)
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source_file = next(item for item in source["files"] if item["date"] == TARGET_DATE)
    with tempfile.TemporaryDirectory(prefix="osw-crw-footprint-") as temporary:
        raw_path = Path(temporary) / source_file["url"].rsplit("/", 1)[-1]
        request = urllib.request.Request(source_file["url"], headers={"User-Agent": "OSW evidence receipt/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response, raw_path.open("wb") as handle:
            while chunk := response.read(1024 * 1024):
                handle.write(chunk)
        if hashlib.sha256(raw_path.read_bytes()).hexdigest() != source_file["raw_file_sha256"]:
            raise ValueError("downloaded daily field does not match the point-source receipt")
        with Dataset(raw_path) as dataset:
            latitudes = np.asarray(dataset.variables["lat"][:])
            longitudes = np.asarray(dataset.variables["lon"][:])
            categories = np.asarray(dataset.variables["heatwave_category"][0])
            masks = np.asarray(dataset.variables["mask"][0])
    latitude_index = int(abs(latitudes - source["coordinate"]["latitude_degrees_north"]).argmin())
    longitude_index = int(abs(longitudes - source["coordinate"]["longitude_degrees_east"]).argmin())
    active = (categories > 0) & (masks == 0)
    component = connected_component(active, (latitude_index, longitude_index))
    if not component:
        raise ValueError("anchor pixel is not active on the target date")
    summary = summarize(component, categories, latitudes, longitudes)
    payload = {
        "schema": "osw.detected-ocean-footprint.v1",
        "detection_id": "OSW-D2",
        "status": "connected_daily_footprint",
        "object_id": "OBJ046",
        "object_name": "marine heatwave",
        "date": TARGET_DATE,
        "anchor_coordinate": source["coordinate"],
        "source_artifact": source_path.relative_to(ROOT).as_posix(),
        "source_artifact_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "raw_daily_file": source_file,
        "method": {
            "active_pixel": "unmasked NOAA CRW marine heatwave category greater than zero",
            "spatial_connectivity": "four-neighbor edge connectivity on the native 0.05-degree global grid",
            "longitude_periodicity": True,
            "component_selection": "the component containing OSW-D1's independently selected anchor pixel",
            "area": "spherical latitude-band cell areas using Earth radius 6371.0088 km",
        },
        "summary": summary,
        "row_run_encoding": "[latitude cell center, [[west cell center, east cell center, category], ...]]",
        "component_rows": encode_runs(component, categories, latitudes, longitudes),
        "identity_evaluation": {
            "result": "pass",
            "test": "A spatially contiguous set of active marine-heatwave pixels contains the duration-qualified OSW-D1 anchor on the declared day.",
            "finding": f'{summary["pixel_count"]} connected pixels cover {summary["area_km2"]:,.1f} km2 on {TARGET_DATE}.',
        },
        "boundary": "One daily surface footprint connected by grid-edge adjacency and anchored to OSW-D1. It is not yet a tracked spatiotemporal object, material water mass, subsurface volume, heat inventory, transport estimate, mechanism, attribution, or impact. Connectivity and resolution choices can merge or split patches.",
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build(args.source, args.output)
    print(f'wrote {args.output}: {payload["summary"]["pixel_count"]} pixels, {payload["summary"]["area_km2"]:,.1f} km2')


if __name__ == "__main__":
    main()

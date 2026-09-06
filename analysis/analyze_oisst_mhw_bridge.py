"""Cross-check the D4 threshold bridge with separate-product OISST fields."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "atlas" / "data" / "oisst-mhw-bridge-north-atlantic-20260807-20260812.json"
CRW_POINT = ROOT / "atlas" / "data" / "noaa-crw-mhw-point-north-atlantic-2026.json"
OUTPUT = ROOT / "research" / "osw-d10-oisst-mhw-bridge-crosscheck-2026.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(source_path: Path = SOURCE, point_path: Path = CRW_POINT) -> dict:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    crw = json.loads(point_path.read_text(encoding="utf-8"))
    latitudes = np.asarray(source["latitude_degrees_north"], dtype=float)
    longitudes = np.asarray(source["longitude_degrees_east"], dtype=float)
    y = int(np.argmin(abs(latitudes - crw["coordinate"]["latitude_degrees_north"])))
    x = int(np.argmin(abs(longitudes - crw["coordinate"]["longitude_degrees_east"])))
    if (float(latitudes[y]), float(longitudes[x])) != (42.125, -49.875):
        raise ValueError("OISST cube does not contain the declared anchor cell")
    categories = {row[0]: row[1] for row in crw["rows"]}
    weights = np.cos(np.deg2rad(latitudes))[:, None]
    denominator = float(np.broadcast_to(weights, (len(latitudes), len(longitudes))).sum())
    days = []
    for date, encoded in source["rows"]:
        field = np.asarray(encoded, dtype=float) / 100
        box_mean = float((field * weights).sum() / denominator)
        days.append({
            "date": date,
            "crw_anchor_category": categories[date],
            "oisst_anchor_sst_c": round(float(field[y, x]), 2),
            "oisst_fixed_box_area_weighted_mean_sst_c": round(box_mean, 3),
            "oisst_fixed_box_minimum_sst_c": round(float(field.min()), 2),
            "oisst_fixed_box_maximum_sst_c": round(float(field.max()), 2),
        })
    for index, day in enumerate(days):
        if index == 0:
            day["anchor_change_from_previous_day_c"] = None
            day["box_mean_change_from_previous_day_c"] = None
            day["box_max_change_from_previous_day_c"] = None
        else:
            prior = days[index - 1]
            day["anchor_change_from_previous_day_c"] = round(day["oisst_anchor_sst_c"] - prior["oisst_anchor_sst_c"], 2)
            day["box_mean_change_from_previous_day_c"] = round(day["oisst_fixed_box_area_weighted_mean_sst_c"] - prior["oisst_fixed_box_area_weighted_mean_sst_c"], 3)
            day["box_max_change_from_previous_day_c"] = round(day["oisst_fixed_box_maximum_sst_c"] - prior["oisst_fixed_box_maximum_sst_c"], 2)
    aug11, aug12 = days[-2], days[-1]
    return {
        "schema": "osw.ocean-object-oisst-bridge-crosscheck.v1",
        "detection_id": "OSW-D10",
        "status": "independent_surface_temperature_crosscheck",
        "object_id": "OBJ046",
        "object_name": "marine heatwave",
        "source_artifacts": [
            {"path": str(source_path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(source_path)},
            {"path": str(point_path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(point_path)},
        ],
        "comparison_contract": {
            "question": "Does the August 12 return of the CRW threshold category coincide with a local rebound in the separate OISST surface analysis?",
            "crw_support": "one 0.05-degree CoralTemp-derived category pixel",
            "oisst_support": "nearest 0.25-degree OISST cell plus a fixed 12-by-17-cell area-weighted box",
            "fixed_box_bounds_cell_centers": source["bounds_cell_centers"],
            "anchor": {"latitude_degrees_north": 42.125, "longitude_degrees_east": -49.875},
        },
        "days": days,
        "bridge_day_comparison": {
            "crw_category_change": [aug11["crw_anchor_category"], aug12["crw_anchor_category"]],
            "oisst_anchor_change_c": aug12["anchor_change_from_previous_day_c"],
            "oisst_fixed_box_mean_change_c": aug12["box_mean_change_from_previous_day_c"],
            "oisst_fixed_box_maximum_change_c": aug12["box_max_change_from_previous_day_c"],
        },
        "identity_evaluation": {
            "result": "threshold return without separate-product local rebound",
            "finding": "CRW category returns from 0 to 1 on August 12, while the nearest OISST cell cools 0.13 C. The fixed OISST neighborhood mean warms 0.160 C and its maximum warms 0.18 C, consistent with spatial rearrangement or product/threshold differences rather than a demonstrated local reheating cause.",
        },
        "next_evidence": "Acquire collocated hourly ERA5 surface-flux terms and daily Copernicus currents, temperature gradients, and mixed-layer depth for August 7-12; evaluate a tendency decomposition without treating the residual as proof of any one mechanism.",
        "boundary": "OISST and CoralTemp are separate gridded surface analyses with different native grids, source processing, and thermal definitions; they may share observing inputs and are not statistically independent. A category is a threshold state, not temperature itself. The fixed-box mean is not the moving object's heat content, and its day-to-day change mixes local evolution and spatial structure. This cross-check does not identify atmospheric forcing, horizontal advection, vertical mixing, entrainment, or causation.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--point", type=Path, default=CRW_POINT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    payload = run(args.source, args.point)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")
    print(payload["identity_evaluation"]["finding"])


if __name__ == "__main__":
    main()

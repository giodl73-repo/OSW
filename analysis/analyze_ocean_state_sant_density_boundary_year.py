"""Measure twelve monthly horizontal density-bin flux screens for the fixed SANT box."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import netCDF4
import numpy as np

from analyze_ocean_state_sant_closed_box_density_boundary import measure as centered_measure
from analyze_ocean_state_sant_density_boundary_collocation import measure as collocation_measure
from audit_nemo_face_thickness_reconstruction import reconstruct_t
from fetch_ocean_state_sant_closed_box_monthly_fields import FIELDS, MONTHS, ROOT, SELECTION, crop, sha256


SOURCE = ROOT / "research" / "ocean-state-sant-closed-box-monthly-fields-2018.json"
MESH = ROOT / "atlas" / "data" / "oras5-drake-mesh.nc"
BASELINE = ROOT / "research" / "ocean-state-sant-closed-box-density-boundary-screen-2018.json"
SENSITIVITY_BASELINE = ROOT / "research" / "ocean-state-sant-density-boundary-collocation-sensitivity-2018.json"
OUTPUT = ROOT / "research" / "ocean-state-sant-density-boundary-monthly-series-2018.json"


def local_box(box: dict, rectangle: dict) -> dict:
    shifted = dict(box)
    for axis in ("x", "y"):
        for suffix in ("start", "stop_exclusive"):
            key = f"{axis}_{suffix}"
            shifted[key] -= rectangle[f"{axis}_start"]
    return shifted


def read_mesh(rectangle: dict) -> dict:
    y = slice(rectangle["y_start"], rectangle["y_stop_exclusive"])
    x = slice(rectangle["x_start"], rectangle["x_stop_exclusive"])
    with netCDF4.Dataset(MESH) as mesh:
        reference = np.asarray(mesh["e3t_0"][:], dtype=float)
        mbathy = np.asarray(mesh["mbathy"][y, x], dtype=int)
        partial = np.asarray(mesh["e3t_ps"][y, x], dtype=float)
        thickness, fallback = reconstruct_t(reference, mbathy, partial)
        midpoint = np.where(thickness > 0, np.cumsum(thickness, axis=0) - thickness / 2, np.nan)
        longitude = np.asarray(mesh["glamt"][y, x], dtype=float)
        latitude = np.asarray(mesh["gphit"][y, x], dtype=float)
        metrics = {"U": {"width": np.asarray(mesh["e2u"][y, x], dtype=float), "wet": np.asarray(mesh["umask"][:, y, x], dtype=bool)},
                   "V": {"width": np.asarray(mesh["e1v"][y, x], dtype=float), "wet": np.asarray(mesh["vmask"][:, y, x], dtype=bool)}}
    return {"thickness": thickness, "midpoint": midpoint, "longitude": longitude, "latitude": latitude,
            "metrics": metrics, "partial_cell_fallback_count": fallback}


def build(source_path: Path = SOURCE, selection_path: Path = SELECTION, baseline_path: Path = BASELINE, sensitivity_baseline_path: Path = SENSITIVITY_BASELINE) -> dict:
    source_path, selection_path, baseline_path, sensitivity_baseline_path = map(Path, (source_path, selection_path, baseline_path, sensitivity_baseline_path))
    source = json.loads(source_path.read_text(encoding="utf-8"))
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    sensitivity_baseline = json.loads(sensitivity_baseline_path.read_text(encoding="utf-8"))
    if source["selection"]["sha256"] != sha256(selection_path) or source["mesh"]["output_sha256"] != sha256(MESH):
        raise ValueError("compact fields must bind to the frozen box and native mesh")
    rectangle = crop(selection)
    if rectangle != source["local_crop"]:
        raise ValueError("compact crop does not cover the selected boxes")
    mesh = read_mesh(rectangle)
    boxes = [local_box(box, rectangle) for box in [selection["primary"], *selection["one_cell_displaced_controls"]]]
    baseline_by_month = {item["valid_time"][:7].replace("-", ""): item for item in baseline["months"]}
    sensitivity_by_month = {item["valid_time"][:7].replace("-", ""): item for item in sensitivity_baseline["months"]}
    if set(baseline_by_month) != set(sensitivity_by_month):
        raise ValueError("four-month centered and upstream baselines disagree")
    months = []
    with netCDF4.Dataset(ROOT / source["output"]["path"]) as dataset:
        if sha256(ROOT / source["output"]["path"]) != source["output"]["sha256"]:
            raise ValueError("compact field archive checksum mismatch")
        for index, month in enumerate(MONTHS):
            fields = {name: np.asarray(np.ma.filled(dataset[name][index], np.nan), dtype=float) for name in FIELDS}
            for name in FIELDS:
                digest = sha256_array(fields[name])
                if digest != source["months"][index]["fields"][name]["extracted_slab_sha256"]:
                    raise ValueError(f"compact {month} {name} slab changed")
            velocity = {"U": fields["vozocrtx"], "V": fields["vomecrty"]}
            outcomes = []
            for box in boxes:
                args = (box, fields["votemper"], fields["vosaline"], velocity, mesh["thickness"], mesh["midpoint"], mesh["metrics"], mesh["longitude"], mesh["latitude"])
                centered = centered_measure(*args)
                sensitivity = collocation_measure(*args)
                outcomes.append({"box": box["id"], "horizontal_density_boundary": centered, "collocation_sensitivity": sensitivity})
            if month in baseline_by_month:
                for new, old, old_sensitivity in zip(outcomes, baseline_by_month[month]["outcomes"], sensitivity_by_month[month]["outcomes"], strict=True):
                    if new["box"] != old["box"] or new["horizontal_density_boundary"] != old["horizontal_density_boundary"]:
                        raise ValueError(f"{month} compact crop does not reproduce the admitted baseline")
                    if new["collocation_sensitivity"] != {key: value for key, value in old_sensitivity.items() if key != "box"}:
                        raise ValueError(f"{month} compact crop does not reproduce the upstream sensitivity")
            months.append({"valid_time": f"2018-{month[-2:]}-01/P1M", "outcomes": outcomes})
    return {"schema": "osw-ocean-state-sant-density-boundary-monthly-series-v1",
            "status": "twelve_month_horizontal_density_bin_screen_not_transformation_or_budget",
            "source": {"path": source_path.relative_to(ROOT).as_posix(), "sha256": sha256(source_path)},
            "baseline": {"path": baseline_path.relative_to(ROOT).as_posix(), "sha256": sha256(baseline_path), "reproduced_months": list(baseline_by_month)},
            "sensitivity_baseline": {"path": sensitivity_baseline_path.relative_to(ROOT).as_posix(), "sha256": sha256(sensitivity_baseline_path)},
            "selection": {"path": selection_path.relative_to(ROOT).as_posix(), "sha256": sha256(selection_path)},
            "method": {"density_bins": baseline["method"]["numeric_strata_sigma0_kg_m3"],
                       "centered_collocation": baseline["method"]["tracer_collocation"],
                       "upstream_check": "fraction of valid face levels assigned to a different bin by upstream T-cell collocation",
                       "temporal_support": "monthly mean T/S/U/V products; products of means omit submonthly covariance"},
            "partial_cell_fallback_count": mesh["partial_cell_fallback_count"], "months": months,
            "boundary": "The complete horizontal native-face box perimeter is partitioned into fixed numerical density bins for each 2018 monthly field. This is not a density-class transformation rate, a mean native advective flux, or a closed budget. Vertical/mixing/assimilation terms and matched class-volume tendencies remain absent."}


def sha256_array(array: np.ndarray) -> str:
    import hashlib
    return hashlib.sha256(np.asarray(array, dtype="<f4").tobytes()).hexdigest()


def validate(payload: dict) -> None:
    if len(payload["months"]) != 12 or len(payload["baseline"]["reproduced_months"]) != 4:
        raise ValueError("complete 2018 extension and four baseline matches required")
    for month in payload["months"]:
        if len(month["outcomes"]) != 4:
            raise ValueError("primary box and three controls required")
        for outcome in month["outcomes"]:
            boundary = outcome["horizontal_density_boundary"]
            if boundary["boundary_face_count"] != 64 or sum(item["wet_face_level_count"] for item in boundary["strata"]) != boundary["all_valid_wet_face_level_count"]:
                raise ValueError("incomplete density-bin perimeter")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    payload = build()
    validate(payload)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

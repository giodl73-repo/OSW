"""Record fixed-box column-heat-content endpoints without making a budget residual."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import netCDF4
import numpy as np

from analyze_ocean_state_sant_closed_box import MONTHS


ROOT = Path(__file__).resolve().parents[1]
SELECTION = ROOT / "research" / "ocean-state-sant-closed-box-selection-current-geometry-v1.json"
FAMILY = ROOT / "research" / "ocean-state-sant-current-geometry-physical-source-family-2018.json"
METRICS = ROOT / "atlas" / "data" / "oras5-drake-t-metrics.nc"
TERMS = ROOT / "atlas" / "data" / "oras5-drake-current-geometry-surface-terms-2018.nc"
OUTPUT = ROOT / "research" / "ocean-state-sant-closed-box-inventory-change-screen-2018.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def record(box: dict, month: str, content: np.ndarray, area: np.ndarray) -> dict:
    selection = np.s_[box["y_start"]:box["y_stop_exclusive"], box["x_start"]:box["x_stop_exclusive"]]
    local_content, local_area = content[selection], area[selection]
    valid = np.isfinite(local_content) & np.isfinite(local_area)
    return {
        "valid_time": f"2018-{month[-2:]}-01/P1M",
        "valid_cells": int(valid.sum()),
        "area_km2": round(float(local_area[valid].sum() / 1e6), 6),
        "column_heat_content_J": round(float(np.sum(local_content[valid] * local_area[valid])), 3),
    }


def build(selection_path: Path = SELECTION, family_path: Path = FAMILY, metrics_path: Path = METRICS, terms_path: Path = TERMS) -> dict:
    selection_path, family_path, metrics_path, terms_path = map(Path, (selection_path, family_path, metrics_path, terms_path))
    selection, family = load(selection_path), load(family_path)
    if selection["status"] != "geometry_selected_before_flux_outcomes" or selection["assignment"]["sha256"] != family["assignment"]["sha256"]:
        raise ValueError("inventory geometry must bind to the preselected physical source family")
    with netCDF4.Dataset(metrics_path) as metrics:
        area = np.asarray(metrics["e1t"][:], dtype=float) * np.asarray(metrics["e2t"][:], dtype=float)
    with netCDF4.Dataset(terms_path) as terms:
        source_months = list(map(str, np.asarray(terms["month"][:], dtype=int)))
        contents = np.asarray(np.ma.filled(terms["sohtcbtm"][:], np.nan), dtype=float)
    boxes = [selection["primary"], *selection["one_cell_displaced_controls"]]
    box_records = []
    for box in boxes:
        endpoints = [record(box, month, contents[source_months.index(month)], area) for month in MONTHS]
        changes = [{
            "from_valid_time": first["valid_time"],
            "to_valid_time": second["valid_time"],
            "column_heat_content_change_J": round(second["column_heat_content_J"] - first["column_heat_content_J"], 3),
            "boundary": "An endpoint difference between monthly column-heat-content fields, not a native tendency or a budget residual.",
        } for first, second in zip(endpoints, endpoints[1:])]
        box_records.append({"box": box["id"], "endpoints": endpoints, "successive_endpoint_differences": changes})
    return {
        "schema": "osw-ocean-state-closed-box-inventory-change-screen-v1",
        "status": "fixed_box_column_heat_content_endpoints_not_tendency_or_budget",
        "source_family": family["source_family"],
        "join_status": "not_joined_to_archived_2018_contents_or_boundary_accounts",
        "selection": {"path": selection_path.relative_to(ROOT).as_posix(), "sha256": sha256(selection_path), "frozen_before_inventory_outcomes": True},
        "sources": {"t_metrics": {"path": metrics_path.relative_to(ROOT).as_posix(), "sha256": sha256(metrics_path)}, "surface_terms": {"path": terms_path.relative_to(ROOT).as_posix(), "sha256": sha256(terms_path)}},
        "boxes": box_records,
        "boundary": "This preserves fixed-geometry column-heat-content snapshots and endpoint differences for the preselected box and controls. The monthly field timestamp/averaging convention has not been demonstrated as a matched inventory-tendency interval, and vertical flux, mixing/diffusion, assimilation/restoring, free-surface/volume terms, and compatible full boundary fluxes remain absent. It is not a tendency, residual, total convergence, or closed budget.",
    }


def validate(payload: dict) -> None:
    if payload["status"] != "fixed_box_column_heat_content_endpoints_not_tendency_or_budget" or len(payload["boxes"]) != 4:
        raise ValueError("four fixed boxes with bounded endpoint scope required")
    for box in payload["boxes"]:
        if len(box["endpoints"]) != 4 or len(box["successive_endpoint_differences"]) != 3:
            raise ValueError("each box needs four endpoints and three changes")
        if any(item["valid_cells"] != 256 for item in box["endpoints"]):
            raise ValueError("the preselected 16x16 box must be fully valid")


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

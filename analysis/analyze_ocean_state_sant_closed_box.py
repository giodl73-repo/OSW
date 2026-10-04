"""Measure a geometry-selected SANT box's closed horizontal advective boundary term."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import netCDF4
import numpy as np

from analyze_ocean_state_sant_partial_perimeter import DEPTH_BANDS, face_values, summarize
from audit_nemo_face_thickness_reconstruction import reconstruct_t


ROOT = Path(__file__).resolve().parents[1]
SELECTION = ROOT / "research" / "ocean-state-sant-closed-box-selection-current-geometry-v1.json"
FAMILY = ROOT / "research" / "ocean-state-sant-current-geometry-physical-source-family-2018.json"
MESH = ROOT / "atlas" / "data" / "oras5-drake-mesh.nc"
METRICS = ROOT / "atlas" / "data" / "oras5-drake-t-metrics.nc"
TERMS = ROOT / "atlas" / "data" / "oras5-drake-current-geometry-surface-terms-2018.nc"
MONTHS = ("201802", "201805", "201808", "201811")
OUTPUT = ROOT / "research" / "ocean-state-sant-closed-box-horizontal-account-2018.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def faces(box: dict) -> list[dict]:
    y0, y1, x0, x1 = box["y_start"], box["y_stop_exclusive"], box["x_start"], box["x_stop_exclusive"]
    return ([{"face": "U", "y": y, "x": x0 - 1, "outward_sign": -1} for y in range(y0, y1)] + [{"face": "U", "y": y, "x": x1 - 1, "outward_sign": 1} for y in range(y0, y1)] + [{"face": "V", "y": y0 - 1, "x": x, "outward_sign": -1} for x in range(x0, x1)] + [{"face": "V", "y": y1 - 1, "x": x, "outward_sign": 1} for x in range(x0, x1)])


def measure(box: dict, arrays: dict, thickness: np.ndarray, midpoint: np.ndarray, metrics: dict) -> dict:
    parts = [face_values(face, arrays["temperature"], arrays["salinity"], arrays["velocity"][face["face"]][:, face["y"], face["x"]], thickness, midpoint, metrics[face["face"]]["width"][face["y"], face["x"]], metrics[face["face"]]["wet"][:, face["y"], face["x"]]) for face in faces(box)]
    all_masks = [part["valid"] for part in parts]
    total = summarize(parts, all_masks)
    by_depth = []
    for label, lower, upper in DEPTH_BANDS:
        masks = [part["valid"] & (part["depth"] >= lower) & (part["depth"] < upper) for part in parts]
        if any(mask.any() for mask in masks): by_depth.append({"depth_support": label, **summarize(parts, masks)})
    return {"boundary_face_count": len(parts), "all_depths": total, "horizontal_advective_volume_convergence_Sv": round(-total["net_outward_volume_Sv"], 9), "horizontal_advective_reference_relative_thermal_convergence_PW_at_0C": round(-total["net_outward_reference_relative_thermal_PW_at_0C"], 9), "by_depth": by_depth}


def surface_record(box: dict, index: int, fields: dict, area: np.ndarray) -> dict:
    selection = np.s_[box["y_start"]:box["y_stop_exclusive"], box["x_start"]:box["x_stop_exclusive"]]
    valid = np.isfinite(area[selection]) & np.isfinite(fields["sohefldo"][index, selection[0], selection[1]]) & np.isfinite(fields["sowaflup"][index, selection[0], selection[1]]) & np.isfinite(fields["sohtcbtm"][index, selection[0], selection[1]])
    local_area = area[selection]
    return {"valid_cells": int(valid.sum()), "area_km2": round(float(local_area[valid].sum() / 1e6), 6), "net_downward_surface_heat_power_W": round(float(np.sum(fields["sohefldo"][index, selection[0], selection[1]][valid] * local_area[valid])), 3), "net_upward_surface_water_mass_flux_kg_s": round(float(np.sum(fields["sowaflup"][index, selection[0], selection[1]][valid] * local_area[valid])), 6), "column_heat_content_J": round(float(np.sum(fields["sohtcbtm"][index, selection[0], selection[1]][valid] * local_area[valid])), 3)}


def build(selection_path: Path = SELECTION, family_path: Path = FAMILY) -> dict:
    selection_path, family_path = Path(selection_path), Path(family_path)
    selection, family = load(selection_path), load(family_path)
    if selection["status"] != "geometry_selected_before_flux_outcomes" or selection["assignment"]["sha256"] != family["assignment"]["sha256"]:
        raise ValueError("box selection must precede outcomes and bind to the physical source family")
    with netCDF4.Dataset(MESH) as mesh:
        reference, mbathy, partial = np.asarray(mesh["e3t_0"][:], dtype=float), np.asarray(mesh["mbathy"][:], dtype=int), np.asarray(mesh["e3t_ps"][:], dtype=float)
        thickness, fallback = reconstruct_t(reference, mbathy, partial)
        midpoint = np.where(thickness > 0, np.cumsum(thickness, axis=0) - thickness / 2, np.nan)
        metrics = {"U": {"width": np.asarray(mesh["e2u"][:], dtype=float), "wet": np.asarray(mesh["umask"][:], dtype=bool)}, "V": {"width": np.asarray(mesh["e1v"][:], dtype=float), "wet": np.asarray(mesh["vmask"][:], dtype=bool)}}
    with netCDF4.Dataset(METRICS) as metric_file: area = np.asarray(metric_file["e1t"][:], dtype=float) * np.asarray(metric_file["e2t"][:], dtype=float)
    with netCDF4.Dataset(TERMS) as term_file:
        source_months = list(map(str, np.asarray(term_file["month"][:], dtype=int))); fields = {name: np.asarray(np.ma.filled(term_file[name][:], np.nan), dtype=float) for name in ("sohefldo", "sowaflup", "sohtcbtm")}
    boxes = [selection["primary"], *selection["one_cell_displaced_controls"]]
    months = []
    for month in MONTHS:
        state_path, salt_path = ROOT / "atlas" / "data" / f"oras5-drake-state-{month}.nc", ROOT / "atlas" / "data" / f"oras5-drake-salinity-current-geometry-{month}.nc"
        with netCDF4.Dataset(state_path) as state, netCDF4.Dataset(salt_path) as salt:
            arrays = {"temperature": np.asarray(np.ma.filled(state["votemper"][:], np.nan), dtype=float), "salinity": np.asarray(np.ma.filled(salt["vosaline"][:], np.nan), dtype=float), "velocity": {"U": np.asarray(np.ma.filled(state["vozocrtx"][:], np.nan), dtype=float), "V": np.asarray(np.ma.filled(state["vomecrty"][:], np.nan), dtype=float)}}
        index = source_months.index(month)
        outcomes = [{"box": box["id"], "horizontal_boundary": measure(box, arrays, thickness, midpoint, metrics), "surface_storage": surface_record(box, index, fields, area)} for box in boxes]
        months.append({"valid_time": f"2018-{month[-2:]}-01/P1M", "outcomes": outcomes})
    return {"schema": "osw-ocean-state-closed-box-horizontal-account-v1", "status": "closed_horizontal_advective_boundary_screen_not_total_convergence_or_budget", "source_family": family["source_family"], "join_status": "not_joined_to_archived_2018_contents_or_boundary_accounts", "selection": {"path": selection_path.relative_to(ROOT).as_posix(), "sha256": sha256(selection_path), "frozen_before_flux_outcomes": True}, "sources": {"mesh": {"path": MESH.relative_to(ROOT).as_posix(), "sha256": sha256(MESH)}, "t_metrics": {"path": METRICS.relative_to(ROOT).as_posix(), "sha256": sha256(METRICS)}, "surface_terms": {"path": TERMS.relative_to(ROOT).as_posix(), "sha256": sha256(TERMS)}}, "partial_cell_fallback_count": fallback, "months": months, "boundary": "The box has a closed horizontal native-face perimeter and therefore measures only its horizontal advective boundary term (negative net outward flux). It still lacks vertical velocity/flux, mixing/diffusion, submonthly covariance, model tracer tendencies, assimilation/restoring terms, and compatible storage-interval accounting. Horizontal advective convergence is not total convergence, heat convergence, salt balance, transformation, causal attribution, or a closed budget."}


def validate(payload: dict) -> None:
    if payload["status"] != "closed_horizontal_advective_boundary_screen_not_total_convergence_or_budget" or len(payload["months"]) != 4:
        raise ValueError("four-month bounded horizontal screen required")
    for month in payload["months"]:
        if len(month["outcomes"]) < 2 or any(item["horizontal_boundary"]["boundary_face_count"] != 64 for item in month["outcomes"]):
            raise ValueError("primary and control boxes require complete 64-face boundaries")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(); payload = build(); validate(payload)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

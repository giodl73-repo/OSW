"""Measure fixed-box TEOS-10 density-stratum volumes without diagnosing transformation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import gsw
import netCDF4
import numpy as np

from analyze_ocean_state_interior_density_structure import STRATA
from audit_nemo_face_thickness_reconstruction import reconstruct_t


ROOT = Path(__file__).resolve().parents[1]
SELECTION = ROOT / "research" / "ocean-state-sant-closed-box-selection-current-geometry-v1.json"
FAMILY = ROOT / "research" / "ocean-state-sant-current-geometry-physical-source-family-2018.json"
MESH = ROOT / "atlas" / "data" / "oras5-drake-mesh.nc"
METRICS = ROOT / "atlas" / "data" / "oras5-drake-t-metrics.nc"
MONTHS = ("201802", "201805", "201808", "201811")
OUTPUT = ROOT / "research" / "ocean-state-sant-closed-box-density-inventory-2018.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def inventory(box: dict, temperature: np.ndarray, practical_salinity: np.ndarray, thickness: np.ndarray, midpoint: np.ndarray, area: np.ndarray, longitude: np.ndarray, latitude: np.ndarray) -> dict:
    selection = np.s_[:, box["y_start"]:box["y_stop_exclusive"], box["x_start"]:box["x_stop_exclusive"]]
    t, sp, dz, z = temperature[selection], practical_salinity[selection], thickness[selection], midpoint[selection]
    a, lon, lat = area[selection[1:]], longitude[selection[1:]], latitude[selection[1:]]
    pressure = gsw.p_from_z(-z, lat[None, :, :])
    absolute_salinity = gsw.SA_from_SP(sp, pressure, lon[None, :, :], lat[None, :, :])
    conservative_temperature = gsw.CT_from_pt(absolute_salinity, t)
    sigma0 = gsw.sigma0(absolute_salinity, conservative_temperature)
    volume = dz * a[None, :, :]
    valid = np.isfinite(volume) & (volume > 0) & np.isfinite(sigma0)
    valid_volume = float(np.sum(volume[valid]))
    strata = []
    for identifier, lower, upper in STRATA:
        mask = valid & (sigma0 >= lower) & (sigma0 < upper)
        strata.append({"id": identifier, "volume_m3": round(float(np.sum(volume[mask])), 3), "volume_fraction": round(float(np.sum(volume[mask]) / valid_volume), 9), "wet_cell_count": int(mask.sum())})
    return {"valid_volume_m3": round(valid_volume, 3), "valid_wet_cell_count": int(valid.sum()), "strata": strata}


def build(selection_path: Path = SELECTION, family_path: Path = FAMILY, mesh_path: Path = MESH, metrics_path: Path = METRICS) -> dict:
    selection_path, family_path, mesh_path, metrics_path = map(Path, (selection_path, family_path, mesh_path, metrics_path))
    selection, family = load(selection_path), load(family_path)
    if selection["status"] != "geometry_selected_before_flux_outcomes" or selection["assignment"]["sha256"] != family["assignment"]["sha256"]:
        raise ValueError("density inventory requires the preselected physical source family")
    with netCDF4.Dataset(mesh_path) as mesh:
        reference, mbathy, partial = np.asarray(mesh["e3t_0"][:], dtype=float), np.asarray(mesh["mbathy"][:], dtype=int), np.asarray(mesh["e3t_ps"][:], dtype=float)
        thickness, fallback = reconstruct_t(reference, mbathy, partial)
        midpoint = np.where(thickness > 0, np.cumsum(thickness, axis=0) - thickness / 2, np.nan)
        longitude, latitude = np.asarray(mesh["glamt"][:], dtype=float), np.asarray(mesh["gphit"][:], dtype=float)
    with netCDF4.Dataset(metrics_path) as metrics:
        area = np.asarray(metrics["e1t"][:], dtype=float) * np.asarray(metrics["e2t"][:], dtype=float)
    boxes = [selection["primary"], *selection["one_cell_displaced_controls"]]
    records = [{"box": box["id"], "months": []} for box in boxes]
    for month in MONTHS:
        state_path = ROOT / "atlas" / "data" / f"oras5-drake-state-{month}.nc"
        salinity_path = ROOT / "atlas" / "data" / f"oras5-drake-salinity-current-geometry-{month}.nc"
        with netCDF4.Dataset(state_path) as state, netCDF4.Dataset(salinity_path) as salinity:
            temperature = np.asarray(np.ma.filled(state["votemper"][:], np.nan), dtype=float)
            practical_salinity = np.asarray(np.ma.filled(salinity["vosaline"][:], np.nan), dtype=float)
        for box_record, box in zip(records, boxes):
            box_record["months"].append({"valid_time": f"2018-{month[-2:]}-01/P1M", "temperature_state": {"path": state_path.relative_to(ROOT).as_posix(), "sha256": sha256(state_path)}, "salinity_state": {"path": salinity_path.relative_to(ROOT).as_posix(), "sha256": sha256(salinity_path)}, **inventory(box, temperature, practical_salinity, thickness, midpoint, area, longitude, latitude)})
    for box in records:
        changes = []
        for first, second in zip(box["months"], box["months"][1:]):
            by_id = {item["id"]: item for item in first["strata"]}
            changes.append({"from_valid_time": first["valid_time"], "to_valid_time": second["valid_time"], "stratum_volume_changes_m3": [{"id": item["id"], "change_m3": round(item["volume_m3"] - by_id[item["id"]]["volume_m3"], 3)} for item in second["strata"]], "boundary": "Difference in fixed density-bin occupancy between endpoint fields, not a class-volume flux or transformation rate."})
        box["successive_endpoint_stratum_volume_differences"] = changes
    return {"schema": "osw-ocean-state-closed-box-density-inventory-v1", "status": "fixed_box_TEOS10_density_stratum_occupancy_not_transformation", "source_family": family["source_family"], "join_status": "not_joined_to_archived_2018_contents_or_boundary_accounts", "selection": {"path": selection_path.relative_to(ROOT).as_posix(), "sha256": sha256(selection_path), "frozen_before_density_outcomes": True}, "method": {"equation_of_state": "TEOS-10 GSW 3.6.23", "conversion": "SA_from_SP using local longitude, latitude, and pressure from reconstructed native T-cell midpoint depth; CT_from_pt; sigma0", "numeric_strata_sigma0_kg_m3": [{"id": identifier, "lower_inclusive": None if not np.isfinite(lower) else lower, "upper_exclusive": None if not np.isfinite(upper) else upper} for identifier, lower, upper in STRATA]}, "sources": {"mesh": {"path": mesh_path.relative_to(ROOT).as_posix(), "sha256": sha256(mesh_path)}, "t_metrics": {"path": metrics_path.relative_to(ROOT).as_posix(), "sha256": sha256(metrics_path)}}, "partial_cell_fallback_count": fallback, "boxes": records, "boundary": "The numerical strata are fixed analysis bins, not named water masses. Their volumes and endpoint differences do not establish class-volume flux, transformation, vertical transfer, mixing, convergence, or a closed budget. Such claims require matched density-class boundary fluxes, vertical/mixing terms, and compatible temporal support."}


def validate(payload: dict) -> None:
    if payload["status"] != "fixed_box_TEOS10_density_stratum_occupancy_not_transformation" or len(payload["boxes"]) != 4:
        raise ValueError("four bounded density inventories required")
    for box in payload["boxes"]:
        if len(box["months"]) != 4 or len(box["successive_endpoint_stratum_volume_differences"]) != 3:
            raise ValueError("four endpoint samples and three changes required")
        for month in box["months"]:
            assert len(month["strata"]) == 4
            if not np.isclose(sum(item["volume_fraction"] for item in month["strata"]), 1.0, atol=1e-7):
                raise ValueError("density strata must partition the valid box volume")


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

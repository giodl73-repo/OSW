"""Partition closed-box horizontal volume flux by TEOS-10 density strata without diagnosing transformation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import gsw
import netCDF4
import numpy as np

from analyze_ocean_state_interior_density_structure import STRATA
from analyze_ocean_state_sant_closed_box import MONTHS, faces
from analyze_ocean_state_sant_partial_perimeter import face_values
from audit_nemo_face_thickness_reconstruction import reconstruct_t


ROOT = Path(__file__).resolve().parents[1]
SELECTION = ROOT / "research" / "ocean-state-sant-closed-box-selection-current-geometry-v1.json"
FAMILY = ROOT / "research" / "ocean-state-sant-current-geometry-physical-source-family-2018.json"
MESH = ROOT / "atlas" / "data" / "oras5-drake-mesh.nc"
OUTPUT = ROOT / "research" / "ocean-state-sant-closed-box-density-boundary-screen-2018.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def face_position(face: dict, longitude: np.ndarray, latitude: np.ndarray) -> tuple[float, float]:
    y, x = face["y"], face["x"]
    if face["face"] == "U":
        return float((longitude[y, x] + longitude[y, x + 1]) / 2), float((latitude[y, x] + latitude[y, x + 1]) / 2)
    return float((longitude[y, x] + longitude[y + 1, x]) / 2), float((latitude[y, x] + latitude[y + 1, x]) / 2)


def summarize(parts: list[dict], masks: list[np.ndarray]) -> dict:
    q = np.concatenate([part["q"][mask] for part, mask in zip(parts, masks)])
    outward, inward = q > 0, q < 0
    return {"wet_face_level_count": int(q.size), "outward_volume_Sv": round(float(q[outward].sum() / 1e6), 9), "inward_volume_Sv": round(float(q[inward].sum() / 1e6), 9), "net_outward_volume_Sv": round(float(q.sum() / 1e6), 9), "gross_volume_exchange_Sv": round(float(np.abs(q).sum() / 1e6), 9)}


def measure(box: dict, temperature: np.ndarray, practical_salinity: np.ndarray, velocity: dict, thickness: np.ndarray, midpoint: np.ndarray, metrics: dict, longitude: np.ndarray, latitude: np.ndarray) -> dict:
    parts = []
    for face in faces(box):
        part = face_values(face, temperature, practical_salinity, velocity[face["face"]][:, face["y"], face["x"]], thickness, midpoint, metrics[face["face"]]["width"][face["y"], face["x"]], metrics[face["face"]]["wet"][:, face["y"], face["x"]])
        lon, lat = face_position(face, longitude, latitude)
        pressure = gsw.p_from_z(-part["depth"], lat)
        absolute_salinity = gsw.SA_from_SP(part["salt"], pressure, lon, lat)
        conservative_temperature = gsw.CT_from_pt(absolute_salinity, part["temp"])
        part["sigma0"] = gsw.sigma0(absolute_salinity, conservative_temperature)
        parts.append(part)
    strata = []
    for identifier, lower, upper in STRATA:
        masks = [part["valid"] & np.isfinite(part["sigma0"]) & (part["sigma0"] >= lower) & (part["sigma0"] < upper) for part in parts]
        strata.append({"id": identifier, **summarize(parts, masks)})
    all_valid_count = sum(int(part["valid"].sum()) for part in parts)
    if sum(item["wet_face_level_count"] for item in strata) != all_valid_count:
        raise ValueError("density strata must partition every valid native face level")
    return {"boundary_face_count": len(parts), "all_valid_wet_face_level_count": all_valid_count, "strata": strata}


def build(selection_path: Path = SELECTION, family_path: Path = FAMILY, mesh_path: Path = MESH) -> dict:
    selection_path, family_path, mesh_path = map(Path, (selection_path, family_path, mesh_path))
    selection, family = load(selection_path), load(family_path)
    if selection["status"] != "geometry_selected_before_flux_outcomes" or selection["assignment"]["sha256"] != family["assignment"]["sha256"]:
        raise ValueError("density boundary screen requires the preselected physical source family")
    with netCDF4.Dataset(mesh_path) as mesh:
        reference, mbathy, partial = np.asarray(mesh["e3t_0"][:], dtype=float), np.asarray(mesh["mbathy"][:], dtype=int), np.asarray(mesh["e3t_ps"][:], dtype=float)
        thickness, fallback = reconstruct_t(reference, mbathy, partial)
        midpoint = np.where(thickness > 0, np.cumsum(thickness, axis=0) - thickness / 2, np.nan)
        longitude, latitude = np.asarray(mesh["glamt"][:], dtype=float), np.asarray(mesh["gphit"][:], dtype=float)
        metrics = {"U": {"width": np.asarray(mesh["e2u"][:], dtype=float), "wet": np.asarray(mesh["umask"][:], dtype=bool)}, "V": {"width": np.asarray(mesh["e1v"][:], dtype=float), "wet": np.asarray(mesh["vmask"][:], dtype=bool)}}
    boxes = [selection["primary"], *selection["one_cell_displaced_controls"]]
    months = []
    for month in MONTHS:
        state_path = ROOT / "atlas" / "data" / f"oras5-drake-state-{month}.nc"
        salinity_path = ROOT / "atlas" / "data" / f"oras5-drake-salinity-current-geometry-{month}.nc"
        with netCDF4.Dataset(state_path) as state, netCDF4.Dataset(salinity_path) as salinity:
            temperature = np.asarray(np.ma.filled(state["votemper"][:], np.nan), dtype=float)
            practical_salinity = np.asarray(np.ma.filled(salinity["vosaline"][:], np.nan), dtype=float)
            velocity = {"U": np.asarray(np.ma.filled(state["vozocrtx"][:], np.nan), dtype=float), "V": np.asarray(np.ma.filled(state["vomecrty"][:], np.nan), dtype=float)}
        outcomes = [{"box": box["id"], "horizontal_density_boundary": measure(box, temperature, practical_salinity, velocity, thickness, midpoint, metrics, longitude, latitude)} for box in boxes]
        months.append({"valid_time": f"2018-{month[-2:]}-01/P1M", "temperature_state": {"path": state_path.relative_to(ROOT).as_posix(), "sha256": sha256(state_path)}, "salinity_state": {"path": salinity_path.relative_to(ROOT).as_posix(), "sha256": sha256(salinity_path)}, "outcomes": outcomes})
    return {"schema": "osw-ocean-state-closed-box-density-boundary-screen-v1", "status": "closed_horizontal_density_stratum_boundary_terms_not_transformation_or_budget", "source_family": family["source_family"], "join_status": "not_joined_to_archived_2018_contents_or_boundary_accounts", "selection": {"path": selection_path.relative_to(ROOT).as_posix(), "sha256": sha256(selection_path), "frozen_before_density_boundary_outcomes": True}, "method": {"equation_of_state": "TEOS-10 GSW 3.6.23", "tracer_collocation": "adjacent T-cell mean at each native U/V face", "conversion": "SA_from_SP using face-mean longitude/latitude and face depth; CT_from_pt; sigma0", "numeric_strata_sigma0_kg_m3": [{"id": identifier, "lower_inclusive": None if not np.isfinite(lower) else lower, "upper_exclusive": None if not np.isfinite(upper) else upper} for identifier, lower, upper in STRATA], "outward_sign": "positive is oriented out of the selected box"}, "sources": {"mesh": {"path": mesh_path.relative_to(ROOT).as_posix(), "sha256": sha256(mesh_path)}}, "partial_cell_fallback_count": fallback, "months": months, "boundary": "This partitions the complete native horizontal box perimeter's volume-flux screen by fixed numerical density bins. Face-averaged density-bin fluxes are not density-class transformation rates, because vertical flux, mixing/diffusion, assimilation/restoring, and a matched temporal class-volume account remain absent. It is not a water-mass classification, total convergence, or closed budget."}


def validate(payload: dict) -> None:
    if payload["status"] != "closed_horizontal_density_stratum_boundary_terms_not_transformation_or_budget" or len(payload["months"]) != 4:
        raise ValueError("four-month bounded density-boundary screen required")
    for month in payload["months"]:
        if len(month["outcomes"]) != 4:
            raise ValueError("primary and three controls required")
        for outcome in month["outcomes"]:
            if outcome["horizontal_density_boundary"]["boundary_face_count"] != 64 or len(outcome["horizontal_density_boundary"]["strata"]) != 4:
                raise ValueError("complete perimeter and four density bins required")
            if sum(item["wet_face_level_count"] for item in outcome["horizontal_density_boundary"]["strata"]) != outcome["horizontal_density_boundary"]["all_valid_wet_face_level_count"]:
                raise ValueError("strata must partition the horizontal face support")


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

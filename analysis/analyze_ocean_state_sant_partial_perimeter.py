"""Measure the in-domain SANT perimeter flux screen while preserving missing subset-edge sides."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import netCDF4
import numpy as np

from audit_nemo_face_thickness_reconstruction import reconstruct_t
from prepare_ocean_state_interior_current_geometry import rle_decode


ROOT = Path(__file__).resolve().parents[1]
ASSIGNMENT = ROOT / "research" / "ocean-state-interior-sant-current-geometry-assignment-2026-09-12.json"
FAMILY = ROOT / "research" / "ocean-state-sant-current-geometry-physical-source-family-2018.json"
MESH = ROOT / "atlas" / "data" / "oras5-drake-mesh.nc"
MONTHS = ("201802", "201805", "201808", "201811")
RHO0, CP0 = 1026.0, 3990.0
DEPTH_BANDS = (("0-200m", 0, 200), ("200-1000m", 200, 1000), ("1000-4000m", 1000, 4000), ("4000m+", 4000, np.inf))
OUTPUT = ROOT / "research" / "ocean-state-sant-current-geometry-partial-perimeter-2018.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def perimeter_faces(membership: np.ndarray) -> tuple[list[dict], dict]:
    faces = []
    for y in range(membership.shape[0]):
        for x in range(membership.shape[1] - 1):
            left, right = membership[y, x], membership[y, x + 1]
            if left != right:
                faces.append({"face": "U", "y": y, "x": x, "outward_sign": 1 if left else -1})
    for y in range(membership.shape[0] - 1):
        for x in range(membership.shape[1]):
            south, north = membership[y, x], membership[y + 1, x]
            if south != north:
                faces.append({"face": "V", "y": y, "x": x, "outward_sign": 1 if south else -1})
    missing = {"south_subset_edge_member_sides": int(membership[0, :].sum()), "north_subset_edge_member_sides": int(membership[-1, :].sum()), "west_subset_edge_member_sides": int(membership[:, 0].sum()), "east_subset_edge_member_sides": int(membership[:, -1].sum())}
    missing["total_missing_subset_edge_sides"] = sum(missing.values())
    return faces, missing


def face_values(face: dict, temperature: np.ndarray, salinity: np.ndarray, velocity: np.ndarray, thickness: np.ndarray, midpoint: np.ndarray, width: float, wet: np.ndarray) -> dict:
    y, x, sign = face["y"], face["x"], face["outward_sign"]
    if face["face"] == "U":
        first_t, second_t = temperature[:, y, x], temperature[:, y, x + 1]
        first_s, second_s = salinity[:, y, x], salinity[:, y, x + 1]
        face_thickness, depth = np.minimum(thickness[:, y, x], thickness[:, y, x + 1]), np.minimum(midpoint[:, y, x], midpoint[:, y, x + 1])
    else:
        first_t, second_t = temperature[:, y, x], temperature[:, y + 1, x]
        first_s, second_s = salinity[:, y, x], salinity[:, y + 1, x]
        face_thickness, depth = np.minimum(thickness[:, y, x], thickness[:, y + 1, x]), np.minimum(midpoint[:, y, x], midpoint[:, y + 1, x])
    q = sign * velocity * face_thickness * width
    temp, salt = 0.5 * (first_t + second_t), 0.5 * (first_s + second_s)
    valid = wet & np.isfinite(q) & np.isfinite(temp) & np.isfinite(salt) & np.isfinite(depth) & (face_thickness > 0)
    return {"q": q, "temp": temp, "salt": salt, "depth": depth, "valid": valid}


def summarize(parts: list[dict], selection: list[np.ndarray]) -> dict:
    q = np.concatenate([part["q"][mask] for part, mask in zip(parts, selection)])
    temp = np.concatenate([part["temp"][mask] for part, mask in zip(parts, selection)])
    salt = np.concatenate([part["salt"][mask] for part, mask in zip(parts, selection)])
    out, incoming = q > 0, q < 0
    heat = RHO0 * CP0 * q * temp
    return {"wet_face_level_count": int(q.size), "outward_volume_Sv": round(float(q[out].sum() / 1e6), 9), "inward_volume_Sv": round(float(q[incoming].sum() / 1e6), 9), "net_outward_volume_Sv": round(float(q.sum() / 1e6), 9), "gross_volume_exchange_Sv": round(float(np.abs(q).sum() / 1e6), 9), "net_outward_reference_relative_thermal_PW_at_0C": round(float(heat.sum() / 1e15), 9), "net_outward_practical_salinity_flux_PSU_m3_s": round(float((q * salt).sum()), 3)}


def build(assignment_path: Path = ASSIGNMENT, family_path: Path = FAMILY, mesh_path: Path = MESH) -> dict:
    assignment_path, family_path, mesh_path = map(Path, (assignment_path, family_path, mesh_path))
    assignment, family = load(assignment_path), load(family_path)
    if family["assignment"]["sha256"] != sha256(assignment_path):
        raise ValueError("perimeter screen requires the bound current-geometry source family")
    membership = rle_decode(assignment["membership"]["rle_row_major"], tuple(assignment["mesh"]["shape_yx"]))
    faces, missing = perimeter_faces(membership)
    with netCDF4.Dataset(mesh_path) as mesh:
        reference, mbathy, partial = np.asarray(mesh["e3t_0"][:], dtype=float), np.asarray(mesh["mbathy"][:], dtype=int), np.asarray(mesh["e3t_ps"][:], dtype=float)
        thickness, fallback = reconstruct_t(reference, mbathy, partial)
        midpoint = np.where(thickness > 0, np.cumsum(thickness, axis=0) - thickness / 2, np.nan)
        metrics = {"U": {"width": np.asarray(mesh["e2u"][:], dtype=float), "wet": np.asarray(mesh["umask"][:], dtype=bool)}, "V": {"width": np.asarray(mesh["e1v"][:], dtype=float), "wet": np.asarray(mesh["vmask"][:], dtype=bool)}}
    months = []
    for month in MONTHS:
        state_path, salinity_path = ROOT / "atlas" / "data" / f"oras5-drake-state-{month}.nc", ROOT / "atlas" / "data" / f"oras5-drake-salinity-current-geometry-{month}.nc"
        with netCDF4.Dataset(state_path) as state, netCDF4.Dataset(salinity_path) as salinity_state:
            temperature = np.asarray(np.ma.filled(state["votemper"][:], np.nan), dtype=float); salinity = np.asarray(np.ma.filled(salinity_state["vosaline"][:], np.nan), dtype=float)
            velocities = {"U": np.asarray(np.ma.filled(state["vozocrtx"][:], np.nan), dtype=float), "V": np.asarray(np.ma.filled(state["vomecrty"][:], np.nan), dtype=float)}
        parts = [face_values(face, temperature, salinity, velocities[face["face"]][:, face["y"], face["x"]], thickness, midpoint, metrics[face["face"]]["width"][face["y"], face["x"]], metrics[face["face"]]["wet"][:, face["y"], face["x"]]) for face in faces]
        all_masks = [part["valid"] for part in parts]
        by_depth = []
        for label, lower, upper in DEPTH_BANDS:
            masks = [part["valid"] & (part["depth"] >= lower) & (part["depth"] < upper) for part in parts]
            if any(mask.any() for mask in masks): by_depth.append({"depth_support": label, **summarize(parts, masks)})
        months.append({"valid_time": f"2018-{month[-2:]}-01/P1M", "state": {"path": state_path.relative_to(ROOT).as_posix(), "sha256": sha256(state_path)}, "salinity": {"path": salinity_path.relative_to(ROOT).as_posix(), "sha256": sha256(salinity_path)}, "all_depths": summarize(parts, all_masks), "by_depth": by_depth})
    return {"schema": "osw-ocean-state-current-geometry-partial-perimeter-screen-v1", "status": "partial_in_domain_lateral_perimeter_screen_not_closed_volume_or_convergence", "source_family": family["source_family"], "join_status": "not_joined_to_archived_2018_contents_or_boundary_accounts", "state": assignment["state"], "geometry": {"in_domain_face_count": len(faces), "U_face_count": sum(face["face"] == "U" for face in faces), "V_face_count": sum(face["face"] == "V" for face in faces), "missing_subset_edge_sides": missing, "partial_cell_fallback_count": fallback, "outward_sign": "positive velocity is oriented out of the SANT membership; negative is inward"}, "method": {"tracer_collocation": "adjacent T-cell mean", "thermal_convention": {"rho0_kg_m3": RHO0, "cp0_J_kg_K": CP0, "reference_temperature_C": 0.0}, "salinity_convention": "practical-salinity times volume flux; not a conservative salt flux"}, "months": months, "boundary": "All measurable in-domain membership-perimeter faces, not a closed SANT boundary. SANT intersects the north, west, and east subset edges, leaving named unmeasured perimeter sides. The screen omits those lateral fluxes and all vertical/surface/storage closure terms; its net flux is not convergence, a mass balance, heat convergence, salt balance, transformation, or a budget."}


def validate(payload: dict) -> None:
    if payload["status"] != "partial_in_domain_lateral_perimeter_screen_not_closed_volume_or_convergence" or payload["geometry"]["missing_subset_edge_sides"]["total_missing_subset_edge_sides"] <= 0:
        raise ValueError("partial perimeter scope and missing sides must be explicit")
    if len(payload["months"]) != 4 or any(not month["by_depth"] for month in payload["months"]):
        raise ValueError("four depth-resolved months are required")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(); payload = build(); validate(payload)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

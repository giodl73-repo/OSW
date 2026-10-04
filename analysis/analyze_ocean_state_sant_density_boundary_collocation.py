"""Challenge closed-box density-bin fluxes with upstream tracer collocation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import gsw
import netCDF4
import numpy as np

from analyze_ocean_state_interior_density_structure import STRATA
from analyze_ocean_state_sant_closed_box import MONTHS, faces
from analyze_ocean_state_sant_closed_box_density_boundary import (
    FAMILY, MESH, ROOT, SELECTION, face_position, load, sha256,
)
from analyze_ocean_state_sant_partial_perimeter import face_values
from audit_nemo_face_thickness_reconstruction import reconstruct_t


BASELINE = ROOT / "research" / "ocean-state-sant-closed-box-density-boundary-screen-2018.json"
OUTPUT = ROOT / "research" / "ocean-state-sant-density-boundary-collocation-sensitivity-2018.json"


def upstream_pair(face: dict, temperature: np.ndarray, salinity: np.ndarray, velocity: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Positive native U/V velocity flows from the first T cell to the second."""
    y, x = face["y"], face["x"]
    second = (y, x + 1) if face["face"] == "U" else (y + 1, x)
    choose_first = velocity >= 0
    return (np.where(choose_first, temperature[:, y, x], temperature[:, second[0], second[1]]),
            np.where(choose_first, salinity[:, y, x], salinity[:, second[0], second[1]]))


def measure(box: dict, temperature: np.ndarray, salinity: np.ndarray, velocity: dict, thickness: np.ndarray, midpoint: np.ndarray, metrics: dict, longitude: np.ndarray, latitude: np.ndarray) -> dict:
    centered = np.zeros(len(STRATA))
    upstream = np.zeros(len(STRATA))
    switched_count = 0
    switched_abs_flux = 0.0
    all_abs_flux = 0.0
    valid_count = 0
    for face in faces(box):
        axis = face["face"]
        native_velocity = velocity[axis][:, face["y"], face["x"]]
        part = face_values(face, temperature, salinity, native_velocity, thickness, midpoint,
                           metrics[axis]["width"][face["y"], face["x"]],
                           metrics[axis]["wet"][:, face["y"], face["x"]])
        upstream_t, upstream_s = upstream_pair(face, temperature, salinity, native_velocity)
        lon, lat = face_position(face, longitude, latitude)
        pressure = gsw.p_from_z(-part["depth"], lat)

        def bin_index(t: np.ndarray, sp: np.ndarray) -> np.ndarray:
            sa = gsw.SA_from_SP(sp, pressure, lon, lat)
            sigma = gsw.sigma0(sa, gsw.CT_from_pt(sa, t))
            return np.searchsorted([item[2] for item in STRATA[:-1]], sigma, side="right")

        middle_bin = bin_index(part["temp"], part["salt"])
        upstream_bin = bin_index(upstream_t, upstream_s)
        valid = part["valid"] & np.isfinite(upstream_t) & np.isfinite(upstream_s)
        q = part["q"][valid]
        middle_bin, upstream_bin = middle_bin[valid], upstream_bin[valid]
        if not np.all((middle_bin >= 0) & (middle_bin < len(STRATA)) & (upstream_bin >= 0) & (upstream_bin < len(STRATA))):
            raise ValueError("unclassified valid face level")
        for index in range(len(STRATA)):
            centered[index] += q[middle_bin == index].sum()
            upstream[index] += q[upstream_bin == index].sum()
        switched = middle_bin != upstream_bin
        switched_count += int(switched.sum())
        switched_abs_flux += float(np.abs(q[switched]).sum())
        all_abs_flux += float(np.abs(q).sum())
        valid_count += q.size
    return {
        "valid_wet_face_level_count": valid_count,
        "changed_bin_face_level_count": switched_count,
        "changed_bin_fraction": round(switched_count / valid_count, 9),
        "changed_bin_abs_volume_flux_Sv": round(switched_abs_flux / 1e6, 9),
        "changed_bin_abs_flux_fraction": round(switched_abs_flux / all_abs_flux, 9),
        "strata": [{"id": item[0], "centered_net_outward_Sv": round(centered[index] / 1e6, 9),
                    "upstream_net_outward_Sv": round(upstream[index] / 1e6, 9),
                    "upstream_minus_centered_Sv": round((upstream[index] - centered[index]) / 1e6, 9)}
                   for index, item in enumerate(STRATA)],
    }


def build(selection_path: Path = SELECTION, family_path: Path = FAMILY, mesh_path: Path = MESH, baseline_path: Path = BASELINE) -> dict:
    selection_path, family_path, mesh_path, baseline_path = map(Path, (selection_path, family_path, mesh_path, baseline_path))
    selection, family, baseline = map(load, (selection_path, family_path, baseline_path))
    if selection["status"] != "geometry_selected_before_flux_outcomes" or selection["assignment"]["sha256"] != family["assignment"]["sha256"]:
        raise ValueError("preselected geometry and source family required")
    if baseline["selection"]["sha256"] != sha256(selection_path) or baseline["sources"]["mesh"]["sha256"] != sha256(mesh_path):
        raise ValueError("centered baseline has incompatible geometry or mesh")
    with netCDF4.Dataset(mesh_path) as mesh:
        thickness, fallback = reconstruct_t(np.asarray(mesh["e3t_0"][:], dtype=float), np.asarray(mesh["mbathy"][:], dtype=int), np.asarray(mesh["e3t_ps"][:], dtype=float))
        midpoint = np.where(thickness > 0, np.cumsum(thickness, axis=0) - thickness / 2, np.nan)
        longitude, latitude = np.asarray(mesh["glamt"][:], dtype=float), np.asarray(mesh["gphit"][:], dtype=float)
        metrics = {"U": {"width": np.asarray(mesh["e2u"][:], dtype=float), "wet": np.asarray(mesh["umask"][:], dtype=bool)},
                   "V": {"width": np.asarray(mesh["e1v"][:], dtype=float), "wet": np.asarray(mesh["vmask"][:], dtype=bool)}}
    boxes = [selection["primary"], *selection["one_cell_displaced_controls"]]
    months = []
    for month, baseline_month in zip(MONTHS, baseline["months"], strict=True):
        state_path = ROOT / "atlas" / "data" / f"oras5-drake-state-{month}.nc"
        salt_path = ROOT / "atlas" / "data" / f"oras5-drake-salinity-current-geometry-{month}.nc"
        if baseline_month["temperature_state"]["sha256"] != sha256(state_path) or baseline_month["salinity_state"]["sha256"] != sha256(salt_path):
            raise ValueError("centered baseline has incompatible T/S fields")
        with netCDF4.Dataset(state_path) as state, netCDF4.Dataset(salt_path) as salt:
            temperature = np.asarray(np.ma.filled(state["votemper"][:], np.nan), dtype=float)
            salinity = np.asarray(np.ma.filled(salt["vosaline"][:], np.nan), dtype=float)
            velocity = {"U": np.asarray(np.ma.filled(state["vozocrtx"][:], np.nan), dtype=float),
                        "V": np.asarray(np.ma.filled(state["vomecrty"][:], np.nan), dtype=float)}
        outcomes = []
        for box, original in zip(boxes, baseline_month["outcomes"], strict=True):
            result = measure(box, temperature, salinity, velocity, thickness, midpoint, metrics, longitude, latitude)
            if box["id"] != original["box"] or result["valid_wet_face_level_count"] != original["horizontal_density_boundary"]["all_valid_wet_face_level_count"]:
                raise ValueError("collocation support differs from centered baseline")
            for item, reference in zip(result["strata"], original["horizontal_density_boundary"]["strata"], strict=True):
                if item["id"] != reference["id"] or abs(item["centered_net_outward_Sv"] - reference["net_outward_volume_Sv"]) > 2e-9:
                    raise ValueError("centered result does not reproduce the admitted baseline")
            outcomes.append({"box": box["id"], **result})
        months.append({"valid_time": baseline_month["valid_time"], "outcomes": outcomes})
    return {"schema": "osw-ocean-state-density-boundary-collocation-sensitivity-v1",
            "status": "method_sensitivity_only_not_transformation_or_budget",
            "source_family": family["source_family"],
            "selection": {"path": selection_path.relative_to(ROOT).as_posix(), "sha256": sha256(selection_path)},
            "centered_baseline": {"path": baseline_path.relative_to(ROOT).as_posix(), "sha256": sha256(baseline_path)},
            "partial_cell_fallback_count": fallback,
            "method": {"centered": "mean of adjacent T-cell potential temperature and practical salinity before TEOS-10 conversion",
                       "upstream": "native positive U/V velocity selects first T cell; negative velocity selects second T cell before TEOS-10 conversion",
                       "same_support": "same native faces, wet levels, velocity, geometry, bins, and monthly fields as centered baseline",
                       "outward_sign": "positive is out of the box"},
            "months": months,
            "boundary": "Changed bin assignments and bin-wise net fluxes measure tracer-collocation sensitivity. Neither version supplies vertical or mixing fluxes, native class tendencies, or assimilation terms. No density-class transformation, closure, or water-mass identity follows."}


def validate(payload: dict) -> None:
    if len(payload["months"]) != 4 or any(len(month["outcomes"]) != 4 for month in payload["months"]):
        raise ValueError("four months and four boxes required")
    for month in payload["months"]:
        for outcome in month["outcomes"]:
            if len(outcome["strata"]) != 4 or not 0 <= outcome["changed_bin_fraction"] <= 1:
                raise ValueError("invalid density-bin sensitivity result")
            if abs(sum(item["upstream_minus_centered_Sv"] for item in outcome["strata"])) > 4e-9:
                raise ValueError("reassignment changed total native volume flux")


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

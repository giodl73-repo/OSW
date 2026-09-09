"""Measure the frozen SANT--SSTC province-edge pilot and matched controls."""

from __future__ import annotations

import argparse
import calendar
import json
from pathlib import Path

import netCDF4
import numpy as np

try:
    from audit_nemo_face_thickness_reconstruction import reconstruct_t
    from acquire_ocean_state_hydrography_pilot import portable_path, sha256_file, sha256_text_file
except ImportError:  # pragma: no cover
    from analysis.audit_nemo_face_thickness_reconstruction import reconstruct_t
    from analysis.acquire_ocean_state_hydrography_pilot import portable_path, sha256_file, sha256_text_file


ROOT = Path(__file__).resolve().parents[1]
RHO0 = 1026.0
CP0 = 3990.0
REFERENCES = (-2.0, 0.0, 2.0)
DEPTH_BANDS = (("0-200m", 0.0, 200.0), ("200-1000m", 200.0, 1000.0), ("1000-4000m", 1000.0, 4000.0), ("4000-6000m", 4000.0, 6000.0), ("6000m+", 6000.0, float("inf")))
COLLOCATIONS = ("adjacent_mean", "upwind", "first_cell", "second_cell")


def scalar(value: float) -> float:
    return round(float(value), 9)


def face_arrays(face: dict, arrays: dict, thickness: np.ndarray, midpoint: np.ndarray, metrics: dict) -> dict:
    y, x = int(face["y"]), int(face["x"])
    sign = int(face.get("sign_first_to_second", face.get("sign_parallel_to_first_to_second")))
    if face["face"] == "U":
        velocity = arrays["u"][:, y, x]
        negative, positive = arrays["temperature"][:, y, x], arrays["temperature"][:, y, x + 1]
        wet = metrics["umask"][:, y, x]
        face_thickness = np.minimum(thickness[:, y, x], thickness[:, y, x + 1])
        face_midpoint = np.minimum(midpoint[:, y, x], midpoint[:, y, x + 1])
        width = metrics["e2u"][y, x]
        lon, lat = metrics["ulon"][y, x], metrics["ulat"][y, x]
    else:
        velocity = arrays["v"][:, y, x]
        negative, positive = arrays["temperature"][:, y, x], arrays["temperature"][:, y + 1, x]
        wet = metrics["vmask"][:, y, x]
        face_thickness = np.minimum(thickness[:, y, x], thickness[:, y + 1, x])
        face_midpoint = np.minimum(midpoint[:, y, x], midpoint[:, y + 1, x])
        width = metrics["e1v"][y, x]
        lon, lat = metrics["vlon"][y, x], metrics["vlat"][y, x]
    first, second = (negative, positive) if sign == 1 else (positive, negative)
    q = sign * velocity * face_thickness * width
    collocations = {
        "adjacent_mean": 0.5 * (negative + positive),
        "upwind": np.where(velocity >= 0, negative, positive),
        "first_cell": first,
        "second_cell": second,
    }
    valid = wet & np.isfinite(q) & np.isfinite(first) & np.isfinite(second) & (face_thickness > 0)
    return {"q": q, "temperature": collocations, "valid": valid, "depth": face_midpoint, "width": width, "lon": lon, "lat": lat, "face_area": face_thickness * width}


def summarize_flux(q: np.ndarray, temperature: np.ndarray, reference: float) -> dict:
    positive = q > 0
    negative = q < 0
    heat = RHO0 * CP0 * q * (temperature - reference)
    return {
        "positive_first_to_second_Sv": scalar(np.sum(q[positive]) / 1e6),
        "negative_second_to_first_Sv": scalar(np.sum(q[negative]) / 1e6),
        "gross_exchange_Sv": scalar(np.sum(np.abs(q)) / 1e6),
        "net_first_to_second_Sv": scalar(np.sum(q) / 1e6),
        "positive_first_to_second_PW": scalar(np.sum(heat[positive]) / 1e15),
        "negative_second_to_first_PW": scalar(np.sum(heat[negative]) / 1e15),
        "gross_absolute_heat_PW": scalar(np.sum(np.abs(heat)) / 1e15),
        "net_first_to_second_PW": scalar(np.sum(heat) / 1e15),
    }


def measure_faces(faces: list[dict], arrays: dict, thickness: np.ndarray, midpoint: np.ndarray, metrics: dict) -> tuple[list[dict], dict]:
    parts = [face_arrays(face, arrays, thickness, midpoint, metrics) for face in faces]
    if any(np.any(~part["valid"] & metrics["umask"][:, face["y"], face["x"]]) if face["face"] == "U" else np.any(~part["valid"] & metrics["vmask"][:, face["y"], face["x"]]) for face, part in zip(faces, parts)):
        raise ValueError("missing value on a selected wet face")
    records = []
    for band, lower, upper in DEPTH_BANDS:
        selections = [part["valid"] & (part["depth"] >= lower) & (part["depth"] < upper) for part in parts]
        count = sum(int(np.count_nonzero(mask)) for mask in selections)
        if not count:
            continue
        q = np.concatenate([part["q"][mask] for part, mask in zip(parts, selections)])
        temperatures = {method: np.concatenate([part["temperature"][method][mask] for part, mask in zip(parts, selections)]) for method in COLLOCATIONS}
        cases = {}
        for method in COLLOCATIONS:
            cases[method] = {str(reference): summarize_flux(q, temperatures[method], reference) for reference in REFERENCES}
        records.append({"depth_support": band, "wet_face_level_count": count, "reference_and_collocation_cases": cases})
    all_q = np.concatenate([part["q"][part["valid"]] for part in parts])
    all_temperature = {method: np.concatenate([part["temperature"][method][part["valid"]] for part in parts]) for method in COLLOCATIONS}
    totals = {method: {str(reference): summarize_flux(all_q, all_temperature[method], reference) for reference in REFERENCES} for method in COLLOCATIONS}
    return records, totals


def build(root: Path = ROOT) -> dict:
    root = Path(root)
    selection_path = root / "research/ocean-state-exchange-pilot-selection-v1.json"
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    if selection["status"] != "pilot_selected_before_transport_outcomes":
        raise ValueError("pilot must be frozen before transport analysis")
    selected = selection["selected_edge"]
    pairs = selection["selected_face_pairs"]
    boundary_faces = [pair["boundary"] for pair in pairs]
    control_faces = [pair["control"] for pair in pairs]

    mesh_path = root / selection["native_grid"]["path"]
    with netCDF4.Dataset(mesh_path) as mesh:
        reference = np.asarray(mesh.variables["e3t_0"][:], dtype=float)
        mbathy = np.asarray(mesh.variables["mbathy"][:], dtype=int)
        partial = np.asarray(mesh.variables["e3t_ps"][:], dtype=float)
        thickness, fallback = reconstruct_t(reference, mbathy, partial)
        top = np.cumsum(thickness, axis=0) - thickness
        midpoint = np.where(thickness > 0, top + thickness / 2, np.nan)
        metrics = {
            "umask": np.asarray(mesh.variables["umask"][:], dtype=bool), "vmask": np.asarray(mesh.variables["vmask"][:], dtype=bool),
            "e2u": np.asarray(mesh.variables["e2u"][:], dtype=float), "e1v": np.asarray(mesh.variables["e1v"][:], dtype=float),
            "ulon": np.asarray(mesh.variables["glamu"][:], dtype=float), "ulat": np.asarray(mesh.variables["gphiu"][:], dtype=float),
            "vlon": np.asarray(mesh.variables["glamv"][:], dtype=float), "vlat": np.asarray(mesh.variables["gphiv"][:], dtype=float),
        }

    months = []
    sources = []
    for source in selection["state_sources"]:
        month = source["month"]
        state_path = root / source["path"]
        if sha256_file(state_path) != source["sha256"]:
            raise ValueError(f"state source changed after selection: {month}")
        with netCDF4.Dataset(state_path) as state:
            arrays = {
                "temperature": np.asarray(np.ma.filled(state.variables["votemper"][:], np.nan), dtype=float),
                "u": np.asarray(np.ma.filled(state.variables["vozocrtx"][:], np.nan), dtype=float),
                "v": np.asarray(np.ma.filled(state.variables["vomecrty"][:], np.nan), dtype=float),
            }
        boundary_depth, boundary_total = measure_faces(boundary_faces, arrays, thickness, midpoint, metrics)
        control_depth, control_total = measure_faces(control_faces, arrays, thickness, midpoint, metrics)
        months.append({"month": month, "days": calendar.monthrange(2018, int(month[-2:]))[1], "boundary": {"by_depth": boundary_depth, "all_depths": boundary_total}, "matched_displaced_control": {"by_depth": control_depth, "all_depths": control_total}})
        sources.append(source)

    primary = "adjacent_mean"
    reference = "0.0"
    net = [item["boundary"]["all_depths"][primary][reference]["net_first_to_second_Sv"] for item in months]
    control_net = [item["matched_displaced_control"]["all_depths"][primary][reference]["net_first_to_second_Sv"] for item in months]
    heat = [item["boundary"]["all_depths"][primary][reference]["net_first_to_second_PW"] for item in months]
    collocation_heat = {
        method: [item["boundary"]["all_depths"][method][reference]["net_first_to_second_PW"] for item in months]
        for method in COLLOCATIONS
    }
    volume_residuals = []
    reference_residuals = []
    for month in months:
        for section_name in ("boundary", "matched_displaced_control"):
            totals = month[section_name]["all_depths"]
            for method in COLLOCATIONS:
                zero = totals[method]["0.0"]
                volume_residuals.append(zero["positive_first_to_second_Sv"] + zero["negative_second_to_first_Sv"] - zero["net_first_to_second_Sv"])
                two = totals[method]["2.0"]
                expected_two_pw = zero["net_first_to_second_PW"] - RHO0 * CP0 * 2.0 * zero["net_first_to_second_Sv"] * 1e6 / 1e15
                reference_residuals.append(two["net_first_to_second_PW"] - expected_two_pw)
    face_geometry = []
    for pair in pairs:
        item = face_arrays(pair["boundary"], {"temperature": np.zeros_like(thickness), "u": np.zeros_like(thickness), "v": np.zeros_like(thickness)}, thickness, midpoint, metrics)
        control = face_arrays(pair["control"], {"temperature": np.zeros_like(thickness), "u": np.zeros_like(thickness), "v": np.zeros_like(thickness)}, thickness, midpoint, metrics)
        face_geometry.append({**pair["boundary"], "longitude_deg": scalar(item["lon"]), "latitude_deg": scalar(item["lat"]), "width_m": scalar(item["width"]), "wet_cross_section_area_m2": scalar(np.sum(item["face_area"][item["valid"]])), "control_longitude_deg": scalar(control["lon"]), "control_latitude_deg": scalar(control["lat"])})
    return {
        "schema": "osw-ocean-state-boundary-exchange-pilot-v1",
        "status": "stage_4_regional_native_grid_pilot_passes_internal_gates",
        "selection": {"path": selection_path.relative_to(root).as_posix(), "sha256": sha256_text_file(selection_path), "selected_before_outcomes": True, "edge_id": selected["edge_id"], "provinces": selected["provinces"]},
        "sign_convention": f"positive is {selected['provinces'][0]} to {selected['provinces'][1]}; negative is the reverse; control uses the parallel local direction inside {selected['provinces'][0]}",
        "thermal_convention": {"density_kg_m3": RHO0, "heat_capacity_J_kg_K": CP0, "reference_temperatures_degC": list(REFERENCES), "primary_reference_degC": 0.0, "meaning": "reference-relative advective thermal transport, not absolute heat flow or convergence"},
        "geometry": {"source_boundary_face_count": selected["native_boundary_face_count"], "measured_matched_face_count": len(pairs), "measured_face_fraction": scalar(len(pairs) / selected["native_boundary_face_count"]), "control": selection["control_geometry"], "faces": face_geometry, "partial_cell_fallback_count": fallback},
        "months": months,
        "summary": {"net_volume_Sv_by_month": net, "net_control_volume_Sv_by_month": control_net, "net_heat_PW_at_0C_by_month": heat, "seasonal_volume_sign_reversal": min(net) < 0 < max(net), "seasonal_heat_sign_reversal_at_0C": min(heat) < 0 < max(heat), "collocation_net_heat_PW_at_0C_by_month": collocation_heat, "maximum_collocation_range_PW": scalar(max(max(values[i] for values in collocation_heat.values()) - min(values[i] for values in collocation_heat.values()) for i in range(len(months))))},
        "checks": {"native_grid": True, "sign_declared": True, "units_declared": True, "partial_cell_thickness_audited": True, "tracer_collocation_sensitivity": True, "missing_wet_values": 0, "matched_control": True, "maximum_volume_component_identity_residual_Sv": scalar(max(abs(value) for value in volume_residuals)), "maximum_reference_change_identity_residual_W": scalar(max(abs(value) for value in reference_residuals) * 1e15), "closure_scope": "open-edge transport only; no convergence or closed budget", "product_sensitivity": "unsupported_single_ORAS5_product"},
        "unsupported": ["observational transport", "second-product sensitivity", "submonthly velocity-temperature covariance", "native conservative tracer advection", "full source-edge coverage", "closed-volume convergence", "climatology", "zoning disposition"],
        "sources": {"mesh": {"path": mesh_path.relative_to(root).as_posix(), "sha256": sha256_file(mesh_path)}, "states": sources},
        "boundary": "Sixteen preselected native faces and one-to-one displaced controls measure a bounded ORAS5 method pilot on the static SANT--SSTC source edge. Results are one-member four-month open-edge model transports, not observational truth, full-edge transport, heat convergence, a material barrier, or a zoning decision.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=Path("research/ocean-state-boundary-exchange-pilot-2018.json"))
    parser.add_argument("--browser-output", type=Path, default=Path("exchange/exchange.js"))
    args = parser.parse_args()
    result = build(args.root)
    output = args.output if args.output.is_absolute() else args.root / args.output
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    browser = args.browser_output if args.browser_output.is_absolute() else args.root / args.browser_output
    browser.write_text("window.OSW_EXCHANGE = " + json.dumps(result, separators=(",", ":")) + ";\n", encoding="utf-8", newline="\n")
    print(json.dumps({"edge": result["selection"]["edge_id"], **result["summary"]}, indent=2))


if __name__ == "__main__":
    main()

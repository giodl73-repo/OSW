"""Test the frozen source edge against independently diagnosed temperature gradients."""

from __future__ import annotations

import argparse
import json
import math
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
EARTH_RADIUS_KM = 6371.0088


def haversine_km(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, (lon1, lat1, lon2, lat2))
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.minimum(1, np.sqrt(a)))


def band_profile(faces: list[dict], temperature: np.ndarray, midpoint: np.ndarray, lon: np.ndarray, lat: np.ndarray, offsets: list[int], lower: float, upper: float) -> list[dict]:
    profile = []
    for offset in offsets:
        gradients, differences, distances = [], [], []
        for face in faces:
            y, x, sign = int(face["y"]), int(face["x"]), int(face["sign_first_to_second"])
            if face["face"] == "U":
                x += offset
                if x < 0 or x + 1 >= temperature.shape[2]:
                    continue
                negative, positive = temperature[:, y, x], temperature[:, y, x + 1]
                depth = np.minimum(midpoint[:, y, x], midpoint[:, y, x + 1])
                distance = float(haversine_km(lon[y, x], lat[y, x], lon[y, x + 1], lat[y, x + 1]))
            else:
                y += offset
                if y < 0 or y + 1 >= temperature.shape[1]:
                    continue
                negative, positive = temperature[:, y, x], temperature[:, y + 1, x]
                depth = np.minimum(midpoint[:, y, x], midpoint[:, y + 1, x])
                distance = float(haversine_km(lon[y, x], lat[y, x], lon[y + 1, x], lat[y + 1, x]))
            valid = np.isfinite(negative) & np.isfinite(positive) & np.isfinite(depth) & (depth >= lower) & (depth < upper) & (distance > 0)
            if not np.any(valid):
                continue
            signed = sign * (positive[valid] - negative[valid])
            differences.extend(signed.tolist())
            gradients.extend((np.abs(signed) / distance).tolist())
            distances.append(distance)
        profile.append({
            "offset_native_faces": offset,
            "sample_count": len(gradients),
            "median_absolute_gradient_degC_per_km": round(float(np.median(gradients)), 9) if gradients else None,
            "median_first_minus_second_temperature_degC": round(float(-np.median(differences)), 9) if differences else None,
            "median_normal_face_spacing_km": round(float(np.median(distances)), 6) if distances else None,
        })
    return profile


def diagnose(profile: list[dict], thresholds: dict) -> dict:
    valid = [item for item in profile if item["median_absolute_gradient_degC_per_km"] is not None]
    ordered = sorted(valid, key=lambda item: (-item["median_absolute_gradient_degC_per_km"], abs(item["offset_native_faces"]), item["offset_native_faces"]))
    peak = ordered[0]
    values = np.asarray([item["median_absolute_gradient_degC_per_km"] for item in valid])
    local_median = float(np.median(values))
    prominence = peak["median_absolute_gradient_degC_per_km"] / local_median if local_median > 0 else math.inf
    detected = peak["median_absolute_gradient_degC_per_km"] >= thresholds["minimum_gradient_degC_per_km"] and prominence >= thresholds["minimum_peak_to_local_median_ratio"]
    envelope = [item["offset_native_faces"] for item in valid if item["median_absolute_gradient_degC_per_km"] >= thresholds["front_envelope_fraction_of_peak"] * peak["median_absolute_gradient_degC_per_km"]]
    spacing = peak["median_normal_face_spacing_km"]
    return {
        "front_detected": bool(detected),
        "diagnosed_peak_offset_native_faces": peak["offset_native_faces"],
        "diagnosed_peak_displacement_km": round(peak["offset_native_faces"] * spacing, 6),
        "peak_gradient_degC_per_km": peak["median_absolute_gradient_degC_per_km"],
        "peak_to_local_median_ratio": round(prominence, 6),
        "front_envelope_offsets_native_faces": [min(envelope), max(envelope)],
        "static_edge_match": bool(detected and abs(peak["offset_native_faces"]) <= thresholds["static_match_maximum_absolute_offset_faces"]),
        "displaced_control_match": bool(detected and abs(peak["offset_native_faces"] - 1) <= thresholds["static_match_maximum_absolute_offset_faces"]),
    }


def build(root: Path = ROOT) -> dict:
    root = Path(root)
    thresholds_path = root / "research/ocean-state-boundary-stability-thresholds-v1.json"
    thresholds = json.loads(thresholds_path.read_text(encoding="utf-8"))
    if thresholds["status"] != "frozen_before_stability_outcomes":
        raise ValueError("thresholds must be frozen before analysis")
    selection_path = root / thresholds["selection_path"]
    if sha256_text_file(selection_path) != thresholds["selection_canonical_lf_sha256"]:
        raise ValueError("selection changed after stability thresholds were frozen")
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    if selection["selected_edge"]["edge_id"] != thresholds["selected_edge"]:
        raise ValueError("threshold and selection edge differ")
    faces = [pair["boundary"] for pair in selection["selected_face_pairs"]]
    if any(pair["control"]["x"] - pair["boundary"]["x"] != 1 for pair in selection["selected_face_pairs"]):
        raise ValueError("frozen control offset does not match selected faces")

    mesh_path = root / selection["native_grid"]["path"]
    with netCDF4.Dataset(mesh_path) as mesh:
        thickness, _ = reconstruct_t(np.asarray(mesh.variables["e3t_0"][:], dtype=float), np.asarray(mesh.variables["mbathy"][:], dtype=int), np.asarray(mesh.variables["e3t_ps"][:], dtype=float))
        midpoint = np.where(thickness > 0, np.cumsum(thickness, axis=0) - thickness / 2, np.nan)
        lon = np.asarray(mesh.variables["glamt"][:], dtype=float)
        lat = np.asarray(mesh.variables["gphit"][:], dtype=float)

    offsets = thresholds["diagnostic"]["normal_search_offsets_native_faces"]
    bands = [("0-200m", 0, 200), ("200-1000m", 200, 1000), ("1000-4000m", 1000, 4000), ("4000-6000m", 4000, 6000)]
    records, sources = [], []
    for source in selection["state_sources"]:
        state_path = root / source["path"]
        if sha256_file(state_path) != source["sha256"]:
            raise ValueError("state source changed after threshold freeze")
        with netCDF4.Dataset(state_path) as state:
            temperature = np.asarray(np.ma.filled(state.variables["votemper"][:], np.nan), dtype=float)
        for band, lower, upper in bands:
            profile = band_profile(faces, temperature, midpoint, lon, lat, offsets, lower, upper)
            diagnosis = diagnose(profile, thresholds["detection_thresholds"])
            static = next(item for item in profile if item["offset_native_faces"] == 0)
            records.append({"month": source["month"], "depth_support": band, "normal_gradient_profile": profile, "static_edge_contrast_degC": static["median_first_minus_second_temperature_degC"], **diagnosis})
        sources.append(source)

    season_summary = []
    for month in thresholds["diagnostic"]["seasonal_samples"]:
        group = [item for item in records if item["month"] == month]
        fraction = sum(item["static_edge_match"] for item in group) / len(group)
        season_summary.append({"month": month, "matched_depth_count": sum(item["static_edge_match"] for item in group), "depth_count": len(group), "matched_depth_fraction": round(fraction, 6), "passing_season": fraction >= thresholds["disposition_thresholds"]["minimum_matched_depth_fraction_per_passing_season"]})
    matched_season_fraction = sum(item["passing_season"] for item in season_summary) / len(season_summary)
    static_fraction = sum(item["static_edge_match"] for item in records) / len(records)
    control_fraction = sum(item["displaced_control_match"] for item in records) / len(records)
    direction_agreements = []
    for month in thresholds["diagnostic"]["seasonal_samples"]:
        group = [item for item in records if item["month"] == month]
        surface_sign = np.sign(group[0]["static_edge_contrast_degC"])
        direction_agreements.extend(bool(np.sign(item["static_edge_contrast_degC"]) == surface_sign) for item in group[1:] if item["static_edge_contrast_degC"] != 0)
    direction_agreement = sum(direction_agreements) / len(direction_agreements) if direction_agreements else 0
    dispositions = thresholds["disposition_thresholds"]
    tests = {
        "season_persistence": matched_season_fraction >= dispositions["minimum_matched_season_fraction"],
        "static_advantage_over_control": static_fraction - control_fraction >= dispositions["minimum_static_advantage_over_control_fraction"],
        "surface_to_depth_direction_agreement": direction_agreement >= dispositions["minimum_surface_to_depth_direction_agreement"],
    }
    disposition = "retain_as_temperature_front_candidate" if all(tests.values()) else dispositions["failure_disposition"]
    return {
        "schema": "osw-ocean-state-boundary-stability-pilot-v1",
        "status": "stage_5_single_year_temperature_gradient_test_complete",
        "edge_id": thresholds["selected_edge"],
        "thresholds": {"path": thresholds_path.relative_to(root).as_posix(), "sha256": sha256_text_file(thresholds_path), "frozen_before_outcomes": True},
        "method": thresholds["diagnostic"],
        "records": records,
        "season_summary": season_summary,
        "summary": {"static_edge_match_fraction": round(static_fraction, 6), "displaced_control_match_fraction": round(control_fraction, 6), "static_advantage_over_control_fraction": round(static_fraction - control_fraction, 6), "matched_season_fraction": round(matched_season_fraction, 6), "surface_to_depth_temperature_contrast_direction_agreement": round(direction_agreement, 6), "threshold_tests": tests, "temperature_front_disposition": disposition, "interannual_stability": "unknown_single_year"},
        "sources": {"mesh": {"path": mesh_path.relative_to(root).as_posix(), "sha256": sha256_file(mesh_path)}, "states": sources},
        "unsupported": ["interannual persistence", "salinity or density fronts", "observational front position", "second-product stability", "material-barrier identity", "transport causation", "global source-edge disposition"],
        "boundary": "A frozen local temperature-gradient search tests whether this short source-edge segment coincides with a prominent front in four 2018 monthly means and four depth bands. It does not test other fields or years, and failure does not erase the static reference edge.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=Path("research/ocean-state-boundary-stability-pilot-2018.json"))
    parser.add_argument("--browser-output", type=Path, default=Path("exchange/stability.js"))
    args = parser.parse_args()
    result = build(args.root)
    output = args.output if args.output.is_absolute() else args.root / args.output
    browser = args.browser_output if args.browser_output.is_absolute() else args.root / args.browser_output
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    browser.write_text("window.OSW_STABILITY = " + json.dumps(result, separators=(",", ":")) + ";\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()

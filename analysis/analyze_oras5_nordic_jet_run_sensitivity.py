"""Test contiguous Nordic heat-jet segmentation across along-gate smoothing scales."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

import numpy as np

from analyze_oras5_nordic_face_jet_runs import distance_km


WINDOWS = (1, 3, 5, 7)
RADII_KM = (0, 20, 30, 50)


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify(values: np.ndarray, window: int) -> np.ndarray:
    half = window // 2
    local_sums = [np.sum(values[max(0, index - half):min(len(values), index + half + 1)]) for index in range(len(values))]
    return np.where(np.asarray(local_sums) >= 0, 1, -1)


def classify_distance(faces: list[dict], values: np.ndarray, radius_km: float) -> np.ndarray:
    arc = np.concatenate(([0.0], np.cumsum([distance_km(first, second) for first, second in zip(faces, faces[1:])])))
    local_sums = [np.sum(values[np.abs(arc - position) <= radius_km + 1e-9]) for position in arc]
    return np.where(np.asarray(local_sums) >= 0, 1, -1)


def runs_from_signs(section: dict, signs: np.ndarray) -> list[dict]:
    faces = section["faces"]
    values = np.asarray([face["net_heat_convergence_TW_at_0C"] for face in faces])
    runs = []
    start = 0
    for end in range(1, len(faces) + 1):
        if end == len(faces) or signs[end] != signs[start]:
            heat = float(np.sum(values[start:end]))
            runs.append({
                "section_id": section["id"],
                "classification_sign": "inward_heat" if signs[start] > 0 else "outward_heat",
                "start_face_index": start,
                "end_face_index": end - 1,
                "face_count": end - start,
                "net_heat_convergence_TW_at_0C": heat,
                "contains_annual_leader": section["id"] == "iceland_scotland_ridge" and start <= 8 < end,
            })
            start = end
    return runs


def section_runs(section: dict, window: int) -> list[dict]:
    values = np.asarray([face["net_heat_convergence_TW_at_0C"] for face in section["faces"]])
    return runs_from_signs(section, classify(values, window))


def describe_case(payload: dict, signs_by_section: dict[str, np.ndarray], scale: dict) -> dict:
    runs = [run for section in payload["sections"] for run in runs_from_signs(section, signs_by_section[section["id"]])]
    raw = {section["id"]: np.where(np.asarray([face["net_heat_convergence_TW_at_0C"] for face in section["faces"]]) >= 0, 1, -1) for section in payload["sections"]}
    inward = [run for run in runs if run["classification_sign"] == "inward_heat"]
    outward = [run for run in runs if run["classification_sign"] == "outward_heat"]
    return scale | {
        "run_count": len(runs),
        "single_face_run_count": sum(run["face_count"] == 1 for run in runs),
        "face_classification_changes_from_raw": sum(int(np.sum(signs_by_section[key] != raw[key])) for key in raw),
        "strongest_inward_run": max(inward, key=lambda run: run["net_heat_convergence_TW_at_0C"]),
        "strongest_outward_run": min(outward, key=lambda run: run["net_heat_convergence_TW_at_0C"]),
        "annual_leader_component": next(run for run in runs if run["contains_annual_leader"]),
        "sections": [{"id": section["id"], "signs": signs_by_section[section["id"]].tolist()} for section in payload["sections"]],
    }


def analyze(input_path: pathlib.Path) -> dict:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    cases = []
    for window in WINDOWS:
        signs = {section["id"]: classify(np.asarray([face["net_heat_convergence_TW_at_0C"] for face in section["faces"]]), window) for section in payload["sections"]}
        cases.append(describe_case(payload, signs, {"window_faces": window}))
    distance_cases = []
    for radius in RADII_KM:
        signs = {section["id"]: classify_distance(section["faces"], np.asarray([face["net_heat_convergence_TW_at_0C"] for face in section["faces"]]), radius) for section in payload["sections"]}
        distance_cases.append(describe_case(payload, signs, {"radius_km": radius}))
    agreements = []
    for window, radius in ((3, 20), (5, 30), (7, 50)):
        face_case = next(case for case in cases if case["window_faces"] == window)
        distance_case = next(case for case in distance_cases if case["radius_km"] == radius)
        agreement = sum(sum(a == b for a, b in zip(face_section["signs"], distance_section["signs"])) for face_section, distance_section in zip(face_case["sections"], distance_case["sections"]))
        agreements.append({"window_faces": window, "radius_km": radius, "agreement_face_count": agreement, "agreement_fraction": agreement / 284})
    return {
        "schema": "osw.oras5.nordic-jet-run-sensitivity.v1",
        "status": "four_along_gate_scales_compared",
        "method": "Each face is classified by the sign of the centered local sum over 1, 3, 5, or 7 ordered faces; truncated windows are used at section ends. Runs partition faces by the resulting sign, while reported TW always sums the original unsmoothed face transports.",
        "cases": cases,
        "distance_cases": distance_cases,
        "summary": {
            "windows_faces": list(WINDOWS),
            "run_counts": [case["run_count"] for case in cases],
            "single_face_run_counts": [case["single_face_run_count"] for case in cases],
            "leader_component_is_strongest_inward": [case["annual_leader_component"] == case["strongest_inward_run"] for case in cases],
            "radii_km": list(RADII_KM),
            "distance_run_counts": [case["run_count"] for case in distance_cases],
            "distance_single_face_run_counts": [case["single_face_run_count"] for case in distance_cases],
            "matched_face_distance_agreement": agreements,
        },
        "checks": {
            "all_cases_partition_284_faces": all(sum(len(section["signs"]) for section in case["sections"]) == 284 for case in cases),
            "raw_case_matches_95_runs": cases[0]["run_count"] == 95,
            "all_windows_odd": all(window % 2 == 1 for window in WINDOWS),
            "all_distance_cases_partition_284_faces": all(sum(len(section["signs"]) for section in case["sections"]) == 284 for case in distance_cases),
        },
        "source": {"face_heat_receipt": sha256_file(input_path)},
        "boundary": "Smoothing scale changes component identity and is not an objective current detector. Face-index windows are topological rather than uniform distance; distance radii use cumulative face-center spacing rather than physical face edges; endpoint neighborhoods truncate, and no scale is selected as uniquely correct.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-face-heat-map-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-jet-run-sensitivity-2018.json"))
    args = parser.parse_args()
    result = analyze(args.input)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()

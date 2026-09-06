"""Segment ordered Nordic boundary faces into contiguous same-sign heat jets."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def distance_km(first: dict, second: dict) -> float:
    lat1, lat2 = map(math.radians, (first["latitude_deg"], second["latitude_deg"]))
    delta_lat = lat2 - lat1
    delta_lon = math.radians(second["longitude_deg"] - first["longitude_deg"])
    haversine = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    return 12742.0 * math.asin(math.sqrt(haversine))


def analyze(input_path: pathlib.Path) -> dict:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    runs = []
    for section in payload["sections"]:
        grouped = []
        sign = None
        for face in section["faces"]:
            face_sign = 1 if face["net_heat_convergence_TW_at_0C"] > 0 else -1
            if sign is not None and face_sign != sign:
                runs.append(make_run(section, len(runs), sign, grouped))
                grouped = []
            grouped.append(face)
            sign = face_sign
        if grouped:
            runs.append(make_run(section, len(runs), sign, grouped))

    ranked = sorted(runs, key=lambda run: abs(run["net_heat_convergence_TW_at_0C"]), reverse=True)
    gross = sum(abs(run["net_heat_convergence_TW_at_0C"]) for run in runs)
    net = sum(run["net_heat_convergence_TW_at_0C"] for run in runs)
    return {
        "schema": "osw.oras5.nordic-face-jet-runs.v1",
        "status": "annual_same_sign_contiguous_runs",
        "definition": "A jet run is a maximal sequence of adjacent faces within one ordered section sharing the sign of annual net heat convergence.",
        "runs": runs,
        "summary": {
            "run_count": len(runs),
            "single_face_run_count": sum(run["face_count"] == 1 for run in runs),
            "positive_run_count": sum(run["sign"] == "inward_heat" for run in runs),
            "negative_run_count": sum(run["sign"] == "outward_heat" for run in runs),
            "gross_absolute_run_heat_TW": gross,
            "net_run_heat_convergence_TW": net,
            "top_10_absolute_run_share": sum(abs(run["net_heat_convergence_TW_at_0C"]) for run in ranked[:10]) / gross,
            "top_10_same_sign_all_12_months_count": sum(run["same_sign_month_count"] == 12 for run in ranked[:10]),
            "strongest_inward_run": max(runs, key=lambda run: run["net_heat_convergence_TW_at_0C"]),
            "strongest_outward_run": min(runs, key=lambda run: run["net_heat_convergence_TW_at_0C"]),
        },
        "checks": {
            "all_284_faces_assigned_once": sum(run["face_count"] for run in runs) == 284,
            "gross_heat_recovered": abs(gross - payload["summary"]["gross_absolute_face_heat_TW"]) < 1e-9,
            "net_heat_recovered": abs(net - payload["summary"]["net_face_heat_convergence_TW"]) < 1e-9,
        },
        "source": {"face_heat_receipt": sha256_file(input_path)},
        "boundary": "Run boundaries follow annual sign on the declared ordered section path. Tiny sign changes can create single-face runs; runs are descriptive connected components, not objectively identified currents, water masses, climatology, or uncertainty.",
    }


def make_run(section: dict, run_index: int, sign: int, faces: list[dict]) -> dict:
    monthly = [sum(face["monthly"][month_index]["net_heat_convergence_TW_at_0C"] for face in faces) for month_index in range(12)]
    heat = sum(face["net_heat_convergence_TW_at_0C"] for face in faces)
    return {
        "id": f"{section['id']}-run-{run_index:02d}",
        "section_id": section["id"],
        "section_name": section["name"],
        "sign": "inward_heat" if sign > 0 else "outward_heat",
        "start_face_index": faces[0]["index"],
        "end_face_index": faces[-1]["index"],
        "face_count": len(faces),
        "centerline_span_km": sum(distance_km(first, second) for first, second in zip(faces, faces[1:])),
        "net_heat_convergence_TW_at_0C": heat,
        "wet_cross_sectional_area_km2": sum(face["wet_cross_sectional_area_m2"] for face in faces) / 1e6,
        "monthly_net_heat_convergence_TW_at_0C": monthly,
        "same_sign_month_count": sum((value > 0) == (sign > 0) for value in monthly),
        "faces": [{"index": face["index"], "longitude_deg": face["longitude_deg"], "latitude_deg": face["latitude_deg"]} for face in faces],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-face-heat-map-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-face-jet-runs-2018.json"))
    args = parser.parse_args()
    result = analyze(args.input)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()

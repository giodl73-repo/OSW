"""Compare OSCAR and HYCOM support at five Indonesian candidate gates."""

from __future__ import annotations

import argparse
import json
import pathlib

try:
    from analyze_indonesian_gate_readiness import sha256_file
except ModuleNotFoundError:
    from analysis.analyze_indonesian_gate_readiness import sha256_file


def mean(values):
    finite = [value for value in values if value is not None]
    return sum(finite) / len(finite) if finite else None


def run(oscar_path: pathlib.Path, hycom_path: pathlib.Path) -> dict:
    oscar = json.loads(oscar_path.read_text(encoding="utf-8"))
    hycom = json.loads(hycom_path.read_text(encoding="utf-8"))
    oscar_gates = {gate["code"]: gate for gate in oscar["gates"]}
    gates = []
    for gate in hycom["gates"]:
        code = gate["code"]; component = gate["component"]; multiplier = gate["positive_multiplier"]
        profiles = []
        for depth, velocity, temperature, salinity in zip(hycom["depth_m"], gate["values"][component], gate["values"]["temperature"], gate["values"]["salinity"]):
            velocity_mean = mean(velocity)
            profiles.append({
                "depth_m": depth,
                "wet_points": sum(value is not None for value in temperature),
                "mean_declared_positive_velocity_m_s": multiplier * velocity_mean if velocity_mean is not None else None,
                "mean_temperature_degC": mean(temperature),
                "mean_salinity_psu": mean(salinity),
            })
        wet_profiles = [profile for profile in profiles if profile["wet_points"]]
        surface = profiles[0]
        gates.append({
            "code": code,
            "name": gate["name"],
            "role": gate["role"],
            "declared_positive": gate["positive"],
            "oscar": {
                "nominal_resolution": "1/3 degree",
                "candidate_points": oscar_gates[code]["candidate_grid_points"],
                "surface_wet_points": oscar_gates[code]["finite_points_per_frame"]["minimum"],
                "surface_mean_declared_positive_velocity_m_s": oscar_gates[code]["annual_frame_weighted_mean_declared_positive_velocity_m_s"],
                "basis": "minimum support and annual mean across 71 five-day fields",
            },
            "hycom": {
                "nominal_resolution": "1/12 degree",
                "candidate_points": len(gate["points"]),
                "surface_wet_points": surface["wet_points"],
                "surface_mean_declared_positive_velocity_m_s": surface["mean_declared_positive_velocity_m_s"],
                "deepest_wet_standard_level_m": max(profile["depth_m"] for profile in wet_profiles),
                "wet_standard_levels": len(wet_profiles),
                "basis": f"one daily field, {hycom['date']}",
            },
            "profiles": profiles,
            "verdict": "candidate_full_depth_section_supported" if surface["wet_points"] >= 3 and len(wet_profiles) >= 3 else "still_underresolved",
        })
    return {
        "schema": "oceanlines.osw.m3-indonesian-grid-bakeoff.v1",
        "status": "cross_product_candidate_gate_support_comparison",
        "gates": gates,
        "sources": [
            {"path": str(oscar_path), "sha256": sha256_file(oscar_path)},
            {"path": str(hycom_path), "sha256": sha256_file(hycom_path), "remote_request_sha256": hycom["source"]["request_sha256"]},
        ],
        "boundary": "OSCAR values are annual nominal-15-m diagnostics; HYCOM values are one 2018-11-16 daily field on standard z levels. Their velocities must not be treated as a like-for-like skill comparison. The bakeoff tests grid support only. HYCOM sections remain provisional axis-aligned, collocated standard-grid samples rather than native-face fluxes or INSTANT mooring arrays; no area-weighted volume or heat transport is calculated.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oscar", type=pathlib.Path, default=pathlib.Path("research/osw-m2-indonesian-gate-readiness-2018.json"))
    parser.add_argument("--hycom", type=pathlib.Path, default=pathlib.Path("atlas/data/hycom-indonesian-gates-20181116.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m3-indonesian-grid-bakeoff-2018.json"))
    args = parser.parse_args()
    result = run(args.oscar, args.hycom)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")
    for gate in result["gates"]:
        print(f"{gate['code']}: OSCAR {gate['oscar']['surface_wet_points']}/{gate['oscar']['candidate_points']} -> HYCOM {gate['hycom']['surface_wet_points']}/{gate['hycom']['candidate_points']} · deepest {gate['hycom']['deepest_wet_standard_level_m']:.0f} m")


if __name__ == "__main__":
    main()

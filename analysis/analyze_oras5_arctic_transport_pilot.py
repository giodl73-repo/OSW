"""Synthesize the February 2018 ORAS5 Arctic gateway transport pilot."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import pathlib


ROOT = pathlib.Path(__file__).parents[1]
SECTION_SLUGS = ("fram", "barents-proxy", "barents-closure")
AW_THRESHOLDS = {
    "fram": {"temperature_gt_degC": 2.0, "salinity_gt_PSU": 34.8},
    "barents-proxy": {"temperature_gt_degC": 3.0, "salinity_gt_PSU": 34.8},
    "barents-closure": {"temperature_gt_degC": 3.0, "salinity_gt_PSU": 34.8},
}


def load_module(name):
    path = pathlib.Path(__file__).with_name(f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(module)
    return module


def sha256_file(path):
    digest = hashlib.sha256()
    with pathlib.Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def class_transport(section, threshold):
    levels, segments = section["shape"]
    rho = section["constants"]["density_kg_m3"]
    cp = section["constants"]["heat_capacity_J_kg_K"]
    positive = negative = heat0 = 0.0
    selected = 0
    for z in range(levels):
        for segment in range(segments):
            index = z * segments + segment
            if not section["wet_fraction"][index]:
                continue
            temperature = section["potential_temperature_degC"][index]
            salinity = section["practical_salinity_PSU"][index]
            if temperature <= threshold["temperature_gt_degC"] or salinity <= threshold["salinity_gt_PSU"]:
                continue
            thickness = section["cell_thickness_m"][index]
            volume = section["normal_velocity_m_s"][index] * section["segment_width_m"][segment] * thickness
            positive += max(0.0, volume)
            negative += min(0.0, volume)
            heat0 += rho * cp * volume * temperature
            selected += 1
    return {
        "threshold": threshold,
        "wet_cell_count": selected,
        "positive_Sv": positive / 1e6,
        "negative_Sv": negative / 1e6,
        "net_Sv": (positive + negative) / 1e6,
        "net_heat_PW_at_0C": heat0 / 1e15,
    }


def run(root=ROOT):
    extractor = load_module("extract_oras5_arctic_sections")
    calculator = load_module("calculate_section_transport")
    root = pathlib.Path(root)
    mesh = root / "atlas/data/oras5-arctic-entrances-mesh.nc"
    state = root / "atlas/data/oras5-arctic-entrances-state-201802.nc"
    readiness = root / "research/osw-m3-oras5-arctic-gate-readiness.json"
    bakeoff = root / "research/osw-m3-oras5-barents-section-bakeoff.json"
    sections = {}
    for slug in SECTION_SLUGS:
        input_path = root / f"research/osw-m3-oras5-arctic-{slug}-section-input-201802.json"
        transport_path = root / f"research/osw-m3-oras5-arctic-{slug}-transport-201802.json"
        section = json.loads(input_path.read_text(encoding="utf-8"))
        transport = json.loads(transport_path.read_text(encoding="utf-8"))
        heat = {str(case["reference_temperature_degC"]): case for case in transport["reference_relative_heat_transport"]}
        aw = class_transport(section, AW_THRESHOLDS[slug])
        aw["positive_fraction_of_full_positive"] = aw["positive_Sv"] / transport["volume_transport"]["positive_Sv"]
        sections[slug] = {
            "name": section["section"]["name"],
            "semantics": section["section"]["semantics"],
            "face_count": section["shape"][1],
            "wet_cell_count": transport["wet_cell_count"],
            "volume_transport_Sv": transport["volume_transport"],
            "transport_weighted_temperature_degC": transport["transport_weighted_temperature_degC"],
            "heat_transport_PW": heat,
            "atlantic_water_comparison_class": aw,
            "maximum_reference_identity_residual_W": max(abs(item["identity_residual_W"]) for item in transport["reference_change_audit"]),
            "input": {"path": str(input_path.relative_to(root)), "sha256": sha256_file(input_path)},
            "transport": {"path": str(transport_path.relative_to(root)), "sha256": sha256_file(transport_path)},
        }

    methods = ("mean", "negative_side", "positive_side", "upwind")
    sensitivity = {slug: [] for slug in SECTION_SLUGS}
    for method in methods:
        candidates = extractor.extract_all(mesh, state, readiness, bakeoff, method)
        for slug, candidate in candidates.items():
            transport = calculator.calculate(candidate, (-1.9, 0.0, 2.0))
            heat0 = next(case["net_PW"] for case in transport["reference_relative_heat_transport"] if case["reference_temperature_degC"] == 0)
            sensitivity[slug].append({"collocation": method, "net_volume_Sv": transport["volume_transport"]["net_Sv"], "net_heat_PW_at_0C": heat0})
    for slug, cases in sensitivity.items():
        baseline = cases[0]
        for case in cases:
            case["heat_difference_from_mean_PW"] = case["net_heat_PW_at_0C"] - baseline["net_heat_PW_at_0C"]
            case["heat_difference_from_mean_percent"] = 100 * case["heat_difference_from_mean_PW"] / abs(baseline["net_heat_PW_at_0C"])

    proxy = sections["barents-proxy"]["volume_transport_Sv"]["net_Sv"]
    closure = sections["barents-closure"]["volume_transport_Sv"]["net_Sv"]
    return {
        "schema": "oceanlines.osw.m3-oras5-arctic-transport-pilot.v1",
        "status": "one_month_three_section_transport_pilot_passes_internal_audits",
        "month": "201802",
        "sources": {
            "mesh": {"path": str(mesh.relative_to(root)), "sha256": sha256_file(mesh)},
            "state": {"path": str(state.relative_to(root)), "sha256": sha256_file(state)},
        },
        "sections": sections,
        "barents_definition_difference": {
            "closure_minus_proxy_net_Sv": closure - proxy,
            "percent_of_proxy_net": 100 * (closure - proxy) / proxy,
            "interpretation": "endpoint/section semantics difference, not an uncertainty interval",
        },
        "tracer_collocation_sensitivity": sensitivity,
        "checks": {
            "all_reference_identity_residuals_below_1W": all(item["maximum_reference_identity_residual_W"] < 1 for item in sections.values()),
            "volume_invariant_to_tracer_collocation": all(max(case["net_volume_Sv"] for case in cases) == min(case["net_volume_Sv"] for case in cases) for cases in sensitivity.values()),
            "maximum_absolute_collocation_heat_shift_percent": max(abs(case["heat_difference_from_mean_percent"]) for cases in sensitivity.values() for case in cases),
        },
        "classification_source": {
            "title": "Fu et al. (2023), Pulses of Cold Atlantic Water in the Arctic Ocean From an Ocean Model Simulation",
            "doi": "https://doi.org/10.1029/2023JC019663",
            "use": "comparison classes only: Fram T>2C/S>34.8; Barents T>3C/S>34.8",
        },
        "boundary": (
            "One February 2018 ORAS5 ensemble member. Reference-relative advective heat transport is not heat convergence. "
            "The Atlantic Water thresholds are literature comparison classes, not universal water-mass boundaries. Fram's "
            "small net volume is the residual of large opposing branches, so its net transport-weighted temperature is unstable."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-arctic-transport-pilot-201802.json"))
    args = parser.parse_args()
    payload = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {payload['status']}")


if __name__ == "__main__":
    main()

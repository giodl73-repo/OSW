"""Synthesize four 2018 ORAS5 snapshots across three Arctic sections."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import pathlib
import statistics


MONTHS = ("201802", "201805", "201808", "201811")
SLUGS = ("fram", "barents-proxy", "barents-closure")
ROOT = pathlib.Path(__file__).parents[1]


def load_pilot_module():
    path = pathlib.Path(__file__).with_name("analyze_oras5_arctic_transport_pilot.py")
    spec = importlib.util.spec_from_file_location("arctic_pilot", path)
    module = importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(module)
    return module


def sha256_file(path):
    digest = hashlib.sha256()
    with pathlib.Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def mean_range(values):
    return {"sample_mean": statistics.fmean(values), "minimum": min(values), "maximum": max(values)}


def run(root=ROOT):
    root = pathlib.Path(root)
    pilot = load_pilot_module()
    state_files = []
    for month in MONTHS:
        receipt_path = root / f"research/osw-m3-oras5-arctic-entrances-state-{month}.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        state_path = root / receipt["output"]["path"]
        if sha256_file(state_path) != receipt["output"]["sha256"]:
            raise ValueError(f"{month} state file does not match its retrieval receipt")
        state_files.append({
            "month": month,
            "path": str(state_path.relative_to(root)),
            "sha256": receipt["output"]["sha256"],
            "receipt_path": str(receipt_path.relative_to(root)),
            "receipt_sha256": sha256_file(receipt_path),
        })
    sections = {}
    receipts = []
    for slug in SLUGS:
        rows = []
        for month in MONTHS:
            input_path = root / f"research/osw-m3-oras5-arctic-{slug}-section-input-{month}.json"
            transport_path = root / f"research/osw-m3-oras5-arctic-{slug}-transport-{month}.json"
            section = json.loads(input_path.read_text(encoding="utf-8"))
            transport = json.loads(transport_path.read_text(encoding="utf-8"))
            canonical = json.dumps(section, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            if hashlib.sha256(canonical).hexdigest() != transport["input_sha256"]:
                raise ValueError(f"{slug} {month} transport is not pinned to its section input")
            heat = {str(case["reference_temperature_degC"]): case["net_PW"] for case in transport["reference_relative_heat_transport"]}
            aw = pilot.class_transport(section, pilot.AW_THRESHOLDS[slug])
            rows.append({
                "month": month,
                "positive_volume_Sv": transport["volume_transport"]["positive_Sv"],
                "negative_volume_Sv": transport["volume_transport"]["negative_Sv"],
                "net_volume_Sv": transport["volume_transport"]["net_Sv"],
                "heat_transport_PW": heat,
                "atlantic_water_net_Sv": aw["net_Sv"],
                "atlantic_water_positive_Sv": aw["positive_Sv"],
                "atlantic_water_negative_Sv": aw["negative_Sv"],
                "maximum_reference_identity_residual_W": max(abs(item["identity_residual_W"]) for item in transport["reference_change_audit"]),
            })
            receipts += [
                {"path": str(input_path.relative_to(root)), "sha256": sha256_file(input_path)},
                {"path": str(transport_path.relative_to(root)), "sha256": sha256_file(transport_path)},
            ]
        net = [row["net_volume_Sv"] for row in rows]
        heat0 = [row["heat_transport_PW"]["0.0"] for row in rows]
        aw_net = [row["atlantic_water_net_Sv"] for row in rows]
        sections[slug] = {
            "name": json.loads((root / f"research/osw-m3-oras5-arctic-{slug}-section-input-201802.json").read_text(encoding="utf-8"))["section"]["name"],
            "months": rows,
            "sample_summary": {
                "net_volume_Sv": mean_range(net),
                "net_heat_PW_at_0C": mean_range(heat0),
                "atlantic_water_net_Sv": mean_range(aw_net),
                "net_volume_sign_persistent": all(value > 0 for value in net) or all(value < 0 for value in net),
                "net_heat_0C_sign_persistent": all(value > 0 for value in heat0) or all(value < 0 for value in heat0),
            },
            "atlantic_water_threshold": pilot.AW_THRESHOLDS[slug],
        }
    differences = []
    for index, month in enumerate(MONTHS):
        proxy = sections["barents-proxy"]["months"][index]
        closure = sections["barents-closure"]["months"][index]
        differences.append({
            "month": month,
            "closure_minus_proxy_net_Sv": closure["net_volume_Sv"] - proxy["net_volume_Sv"],
            "closure_minus_proxy_heat_PW_at_0C": closure["heat_transport_PW"]["0.0"] - proxy["heat_transport_PW"]["0.0"],
        })
    return {
        "schema": "oceanlines.osw.m3-oras5-arctic-seasons.v1",
        "status": "four_snapshot_three_section_arctic_transport_synthesis",
        "sampling": {"year": 2018, "months": list(MONTHS), "interpretation": "four seasonal snapshots, not an annual mean"},
        "state_files": state_files,
        "sections": sections,
        "barents_definition_difference_by_month": differences,
        "receipts": receipts,
        "checks": {
            "all_section_inputs_pin_their_transports": True,
            "all_state_files_match_retrieval_receipts": True,
            "all_reference_identity_residuals_below_1W": all(row["maximum_reference_identity_residual_W"] < 1 for section in sections.values() for row in section["months"]),
            "all_three_net_volume_signs_persist": all(section["sample_summary"]["net_volume_sign_persistent"] for section in sections.values()),
            "all_three_0C_heat_signs_persist": all(section["sample_summary"]["net_heat_0C_sign_persistent"] for section in sections.values()),
            "closure_exceeds_proxy_net_volume_every_month": all(item["closure_minus_proxy_net_Sv"] > 0 for item in differences),
        },
        "interpretation": (
            "Across these four snapshots, Fram exports net volume while retaining positive 0C-reference advective heat because warm northward flow opposes colder southward export. "
            "Both Barents sections import volume and reference-relative heat, and the broader closure exceeds the proxy every month."
        ),
        "boundary": (
            "Four sampled months from one ORAS5 ensemble member are not a time-weighted annual mean, climatology, observational estimate, uncertainty range, heat convergence, or Arctic heat budget. "
            "Reference-relative heat across an open section depends on reference temperature when net volume is nonzero."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-arctic-seasons-2018.json"))
    args = parser.parse_args()
    payload = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {payload['status']}")


if __name__ == "__main__":
    main()

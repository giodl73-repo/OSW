"""Screen all selected July 2017 ORAS5 members against the frozen sign rule."""

from __future__ import annotations

import json

import netCDF4
import numpy as np

from analyze_ocean_state_sant_density_boundary_year import MESH, local_box, read_mesh
from analyze_ocean_state_sant_density_cutoff_sensitivity import METRICS, measure
from analyze_ocean_state_sant_july_repeat import sign_pass
from fetch_ocean_state_sant_closed_box_monthly_fields import ROOT, SELECTION, crop, sha256, slab_digest
from fetch_ocean_state_sant_2017_july_ensemble_fields import RECEIPT as FIELDS, RULE


REFERENCE = ROOT / "research" / "ocean-state-sant-july-repeat-sign-screen-2016-2018.json"
OUTPUT = ROOT / "research" / "ocean-state-sant-2017-july-ensemble-sign-screen.json"
METHODS = ("centered_net_outward_Sv", "upstream_net_outward_Sv")


def summarize(member: str, outcomes: list[dict]) -> dict:
    cases = [{"box": outcome["box"], "scheme": scheme["id"], "method": method,
              "net_outward_Sv": scheme["bins"][2][method]}
             for outcome in outcomes for scheme in outcome["schemes"] for method in METHODS]
    primary = outcomes[0]["schemes"][1]["bins"][2]
    east = outcomes[3]["schemes"][1]["bins"][2]
    return {"member": member, "outcomes": outcomes, "predeclared_sign_pass": sign_pass(outcomes),
            "primary_baseline_centered_Sv": primary[METHODS[0]],
            "primary_baseline_upstream_Sv": primary[METHODS[1]],
            "east_control_baseline_upstream_Sv": east[METHODS[1]],
            "minimum_tested_case": min(cases, key=lambda case: case["net_outward_Sv"]),
            "failed_cases": [case for case in cases if case["net_outward_Sv"] <= 0]}


def build() -> dict:
    rule = json.loads(RULE.read_text(encoding="utf-8"))
    fields_receipt = json.loads(FIELDS.read_text(encoding="utf-8"))
    reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    rectangle = crop(selection)
    if fields_receipt["selection_rule"]["sha256"] != sha256(RULE) or fields_receipt["fixed_box"]["sha256"] != sha256(SELECTION) or fields_receipt["mesh"]["output_sha256"] != sha256(MESH) or rectangle != fields_receipt["local_crop"]:
        raise ValueError("ensemble source differs from frozen selection or mesh")
    if rule["fixed_support"]["density_cutoffs_sigma0_kg_m3"] != [26.5, 27.0, 27.5] or rule["fixed_support"]["cutoff_challenges_sigma0_kg_m3"] != [-0.1, 0.0, 0.1]:
        raise ValueError("ensemble cutoff schemes changed")
    if reference["selection_rule"]["path"] != "research/ocean-state-sant-july-repeat-selection-v1.json" or reference["fixed_box"]["sha256"] != sha256(SELECTION):
        raise ValueError("opa0 July 2017 reference changed")
    mesh = read_mesh(rectangle)
    y = slice(rectangle["y_start"], rectangle["y_stop_exclusive"])
    x = slice(rectangle["x_start"], rectangle["x_stop_exclusive"])
    with netCDF4.Dataset(METRICS) as metrics:
        area = np.asarray(metrics["e1t"][y, x], dtype=float) * np.asarray(metrics["e2t"][y, x], dtype=float)
    boxes = [local_box(box, rectangle) for box in [selection["primary"], *selection["one_cell_displaced_controls"]]]
    opa0 = next(year for year in reference["years"] if year["month"] == "201707")
    members = [summarize("opa0", opa0["outcomes"])]
    archive = ROOT / fields_receipt["output"]["path"]
    if sha256(archive) != fields_receipt["output"]["sha256"]:
        raise ValueError("ensemble compact archive checksum changed")
    with netCDF4.Dataset(archive) as dataset:
        for index, source in enumerate(fields_receipt["members"]):
            if source["member"] != rule["selected_members"][index]:
                raise ValueError("source member order changed")
            fields = {}
            for name in ("votemper", "vosaline", "vozocrtx", "vomecrty"):
                value = np.asarray(np.ma.filled(dataset[name][index], np.nan), dtype=float)
                if slab_digest(value) != source["fields"][name]["extracted_slab_sha256"]:
                    raise ValueError(f"{source['member']} {name} slab changed")
                fields[name] = value
            members.append(summarize(source["member"], [{"box": box["id"], **measure(box, fields, mesh, area)} for box in boxes]))
    pass_count = sum(item["predeclared_sign_pass"] for item in members)
    east_signs = [item["east_control_baseline_upstream_Sv"] > 0 for item in members]
    return {"schema": "osw-ocean-state-sant-2017-july-ensemble-sign-screen-v1",
            "status": "preselected_within_product_member_sign_challenge_not_independent_replication",
            "selection_rule": {"path": RULE.relative_to(ROOT).as_posix(), "sha256": sha256(RULE)},
            "ensemble_fields": {"path": FIELDS.relative_to(ROOT).as_posix(), "sha256": sha256(FIELDS)},
            "opa0_reference": {"path": REFERENCE.relative_to(ROOT).as_posix(), "sha256": sha256(REFERENCE)},
            "fixed_box": {"path": SELECTION.relative_to(ROOT).as_posix(), "sha256": sha256(SELECTION)},
            "test": {"month": "201707", "bin_index": 2, "rule": rule["test"]},
            "members": members,
            "decision": {"pass_count": pass_count, "member_count": len(members),
                         "east_control_baseline_upstream_sign_varies": len(set(east_signs)) > 1},
            "boundary": rule["interpretation"]}


def validate(payload: dict) -> None:
    if [item["member"] for item in payload["members"]] != ["opa0", "opa1", "opa2", "opa3", "opa4"]:
        raise ValueError("all five ORAS5 members required")
    for member in payload["members"]:
        if len(member["outcomes"]) != 4 or any(len(outcome["schemes"]) != 3 for outcome in member["outcomes"]):
            raise ValueError("fixed geometry and cutoffs required")
        if member["predeclared_sign_pass"] != (len(member["failed_cases"]) == 0):
            raise ValueError("member sign decision mismatch")
        for outcome in member["outcomes"]:
            for scheme in outcome["schemes"]:
                for method in METHODS:
                    if abs(sum(bin_[method] for bin_ in scheme["bins"]) - outcome["net_outward_all_density_Sv"]) > 4e-9:
                        raise ValueError("density bins do not preserve native total flux")
    if payload["decision"]["pass_count"] != sum(item["predeclared_sign_pass"] for item in payload["members"]):
        raise ValueError("pass count mismatch")


if __name__ == "__main__":
    payload = build()
    validate(payload)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT}: {payload['decision']}")

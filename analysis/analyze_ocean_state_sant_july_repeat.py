"""Test the preselected prior Julys against the fixed 2018 density-bin sign rule."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import netCDF4
import numpy as np

from analyze_ocean_state_sant_density_boundary_year import MESH, local_box, read_mesh
from analyze_ocean_state_sant_density_cutoff_sensitivity import METRICS, OUTPUT as CUTOFF, measure
from fetch_ocean_state_sant_closed_box_monthly_fields import ROOT, SELECTION, crop, sha256, slab_digest
from fetch_ocean_state_sant_july_repeat_fields import MONTHS, RECEIPT as FIELDS, SELECTION_RULE


OUTPUT = ROOT / "research" / "ocean-state-sant-july-repeat-sign-screen-2016-2018.json"


def sign_pass(outcomes: list[dict]) -> bool:
    return all(scheme["bins"][2][method] > 0 for outcome in outcomes for scheme in outcome["schemes"]
               for method in ("centered_net_outward_Sv", "upstream_net_outward_Sv"))


def build(fields_path: Path = FIELDS, selection_path: Path = SELECTION, rule_path: Path = SELECTION_RULE, cutoff_path: Path = CUTOFF) -> dict:
    fields_path, selection_path, rule_path, cutoff_path = map(Path, (fields_path, selection_path, rule_path, cutoff_path))
    fields_receipt = json.loads(fields_path.read_text(encoding="utf-8"))
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    rule = json.loads(rule_path.read_text(encoding="utf-8"))
    cutoff = json.loads(cutoff_path.read_text(encoding="utf-8"))
    if fields_receipt["selection_rule"]["sha256"] != sha256(rule_path) or fields_receipt["fixed_box"]["sha256"] != sha256(selection_path) or cutoff["selection"]["sha256"] != sha256(selection_path):
        raise ValueError("repeat-year screen requires the preselected years and unchanged box")
    if rule["fixed_support"]["density_cutoffs_sigma0_kg_m3"] != cutoff["method"]["baseline_cutoffs_sigma0_kg_m3"] or rule["fixed_support"]["cutoff_challenges_sigma0_kg_m3"] != cutoff["method"]["cutoff_shifts_sigma0_kg_m3"]:
        raise ValueError("repeat-year cutoffs differ from the selected method")
    rectangle = crop(selection)
    if rectangle != fields_receipt["local_crop"] or fields_receipt["mesh"]["output_sha256"] != sha256(MESH):
        raise ValueError("repeat-year fields have incompatible native support")
    mesh = read_mesh(rectangle)
    y = slice(rectangle["y_start"], rectangle["y_stop_exclusive"])
    x = slice(rectangle["x_start"], rectangle["x_stop_exclusive"])
    with netCDF4.Dataset(METRICS) as metrics:
        area = np.asarray(metrics["e1t"][y, x], dtype=float) * np.asarray(metrics["e2t"][y, x], dtype=float)
    boxes = [local_box(box, rectangle) for box in [selection["primary"], *selection["one_cell_displaced_controls"]]]
    archive = ROOT / fields_receipt["output"]["path"]
    if sha256(archive) != fields_receipt["output"]["sha256"]:
        raise ValueError("repeat-year compact archive checksum changed")
    years = []
    with netCDF4.Dataset(archive) as dataset:
        for index, month in enumerate(MONTHS):
            fields = {}
            for name in ("votemper", "vosaline", "vozocrtx", "vomecrty"):
                value = np.asarray(np.ma.filled(dataset[name][index], np.nan), dtype=float)
                if slab_digest(value) != fields_receipt["months"][index]["fields"][name]["extracted_slab_sha256"]:
                    raise ValueError(f"{month} {name} slab changed")
                fields[name] = value
            outcomes = [{"box": box["id"], **measure(box, fields, mesh, area)} for box in boxes]
            years.append({"month": month, "outcomes": outcomes, "predeclared_sign_pass": sign_pass(outcomes)})
    july_2018 = cutoff["months"][6]
    if july_2018["valid_time"] != "2018-07-01/P1M" or [item["box"] for item in july_2018["outcomes"]] != [box["id"] for box in boxes]:
        raise ValueError("2018 comparison is not the same fixed July support")
    years.append({"month": "201807", "outcomes": july_2018["outcomes"], "predeclared_sign_pass": sign_pass(july_2018["outcomes"])})
    all_pass = all(item["predeclared_sign_pass"] for item in years)
    return {"schema": "osw-ocean-state-sant-july-repeat-sign-screen-v1",
            "status": "predeclared_three_July_sign_screen_not_climatology_or_boundary_validation",
            "selection_rule": {"path": rule_path.relative_to(ROOT).as_posix(), "sha256": sha256(rule_path)},
            "prior_july_fields": {"path": fields_path.relative_to(ROOT).as_posix(), "sha256": sha256(fields_path)},
            "july_2018_cutoff_screen": {"path": cutoff_path.relative_to(ROOT).as_posix(), "sha256": sha256(cutoff_path)},
            "fixed_box": {"path": selection_path.relative_to(ROOT).as_posix(), "sha256": sha256(selection_path)},
            "test": {"bin_index": 2, "rule": "net outward > 0 in all four boxes, both collocation methods, and three cutoff shifts for each selected July",
                     "selected_julys": list(MONTHS) + ["201807"]},
            "years": years,
            "decision": "repeat_year_sign_screen_pass" if all_pass else "repeat_year_sign_screen_fails",
            "boundary": "This is a three-July sign challenge in one assimilative reanalysis product and one fixed neighborhood. Passing it would not establish year-round persistence, a physical state boundary, independent-product agreement, native mean advective flux, density-class transformation, or a closed budget. Failing it would limit the July 2018 result to the sampled year and method support."}


def validate(payload: dict) -> None:
    if [item["month"] for item in payload["years"]] != ["201607", "201707", "201807"]:
        raise ValueError("three preselected Julys required")
    if any(len(item["outcomes"]) != 4 or len(item["outcomes"][0]["schemes"]) != 3 for item in payload["years"]):
        raise ValueError("fixed boxes and cutoff schemes required")
    if (payload["decision"] == "repeat_year_sign_screen_pass") != all(item["predeclared_sign_pass"] for item in payload["years"]):
        raise ValueError("decision disagrees with the predeclared sign rule")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    payload = build()
    validate(payload)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {payload['decision']}")


if __name__ == "__main__":
    main()

"""Derive non-composite motion fingerprints for the frozen 22 OSW regions."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


FAMILY_ORDER = (
    ("POLAR", ("AAP", "NPP", "ANP")),
    ("PACIFIC", ("NPW", "TAW", "PT", "OCT", "EPC", "WPC", "SWPC")),
    ("ATLANTIC", ("NAW", "MW", "OAT", "CT", "NWAC", "WAC", "EAC")),
    ("INDIAN", ("ARW", "IT", "AIC", "SEIC")),
    ("SOUTHERN", ("SW",)),
)


def derive(audit: dict) -> dict:
    regions = {item["region_code"]: item for item in audit["regions"]}
    incident = {code: [] for code in regions}
    for boundary in audit["boundary_pairs"]:
        incident[boundary["region_a"]].append(boundary)
        incident[boundary["region_b"]].append(boundary)
    rows = []
    for family, codes in FAMILY_ORDER:
        for code in codes:
            region = regions[code]
            boundaries = incident[code]
            screened = [item for item in boundaries if item["support_class"] == "screened"]
            provisional = [item for item in boundaries if item["support_class"] == "provisional"]
            screened_weight = sum(item["neighbor_pairs"] for item in screened)
            weighted_margin = (
                sum(item["orientation_margin"] * item["neighbor_pairs"] for item in screened) / screened_weight
                if screened_weight else None
            )
            rows.append({
                "family": family,
                "region_code": code,
                "region": region["region"],
                "supported_cells": region["supported_cells"],
                "mean_cross_season_alignment": region["mean_cross_season_alignment"],
                "mean_maximum_seasonal_turn_degrees": region["mean_maximum_seasonal_turn_degrees"],
                "mean_internal_direction_similarity": region["mean_internal_direction_similarity"],
                "low_similarity_internal_fraction": region["low_similarity_internal_fraction"],
                "incident_boundaries": len(boundaries),
                "screened_boundaries": len(screened),
                "provisional_boundaries": len(provisional),
                "screened_neighbor_pairs": screened_weight,
                "screened_weighted_orientation_margin": weighted_margin,
                "maximum_screened_cut_through_score": max((item["cut_through_score"] for item in screened), default=None),
                "screened_crossed_boundaries": sum(item["orientation_class"] == "crossed" for item in screened),
                "screened_followed_boundaries": sum(item["orientation_class"] == "followed" for item in screened),
            })
    return {
        "schema": "oceanlines.osw.motion-region-passports.v1",
        "status": "comparative fingerprint; frozen zoning; no composite rank or revision",
        "region_system": audit["region_system"],
        "source_artifact_sha256": audit["source_artifact_sha256"],
        "source_data_sha256": audit["source_data_sha256"],
        "source_period_start": audit["source_period_start"],
        "source_period_stop": audit["source_period_stop"],
        "family_order": [family for family, _ in FAMILY_ORDER],
        "regions": rows,
        "boundary": "Columns are deliberately not combined into one score. Different diagnostics can disagree, and missing screened borders are evidence limits rather than zero values.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--csv-output", type=Path, required=True)
    args = parser.parse_args()
    result = derive(json.loads(args.input.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    args.csv_output.parent.mkdir(parents=True, exist_ok=True)
    with args.csv_output.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(result["regions"][0]))
        writer.writeheader()
        writer.writerows(result["regions"])
    print(f"wrote {args.output} ({len(result['regions'])} region passports)")


if __name__ == "__main__":
    main()

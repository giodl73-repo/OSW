"""Extend fixed-box TEOS-10 density-bin occupancy to all twelve monthly means."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import netCDF4
import numpy as np

from analyze_ocean_state_sant_closed_box_density_inventory import inventory
from analyze_ocean_state_sant_density_boundary_year import MESH, SOURCE, local_box, read_mesh
from fetch_ocean_state_sant_closed_box_monthly_fields import MONTHS, ROOT, SELECTION, crop, sha256, slab_digest


METRICS = ROOT / "atlas" / "data" / "oras5-drake-t-metrics.nc"
BASELINE = ROOT / "research" / "ocean-state-sant-closed-box-density-inventory-2018.json"
OUTPUT = ROOT / "research" / "ocean-state-sant-density-inventory-monthly-series-2018.json"


def build(source_path: Path = SOURCE, selection_path: Path = SELECTION, baseline_path: Path = BASELINE) -> dict:
    source_path, selection_path, baseline_path = map(Path, (source_path, selection_path, baseline_path))
    source = json.loads(source_path.read_text(encoding="utf-8"))
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    if source["selection"]["sha256"] != sha256(selection_path) or source["mesh"]["output_sha256"] != sha256(MESH):
        raise ValueError("annual inventory requires the fixed geometry and mesh")
    rectangle = crop(selection)
    if rectangle != source["local_crop"]:
        raise ValueError("source crop does not cover the selected boxes")
    mesh = read_mesh(rectangle)
    y = slice(rectangle["y_start"], rectangle["y_stop_exclusive"])
    x = slice(rectangle["x_start"], rectangle["x_stop_exclusive"])
    with netCDF4.Dataset(METRICS) as metrics:
        area = np.asarray(metrics["e1t"][y, x], dtype=float) * np.asarray(metrics["e2t"][y, x], dtype=float)
    boxes = [local_box(box, rectangle) for box in [selection["primary"], *selection["one_cell_displaced_controls"]]]
    baseline_by_box = {record["box"]: {month["valid_time"][:7].replace("-", ""): month for month in record["months"]} for record in baseline["boxes"]}
    records = [{"box": box["id"], "months": []} for box in boxes]
    archive = ROOT / source["output"]["path"]
    if sha256(archive) != source["output"]["sha256"]:
        raise ValueError("compact source checksum changed")
    with netCDF4.Dataset(archive) as dataset:
        for index, month in enumerate(MONTHS):
            fields = {}
            for name in ("votemper", "vosaline"):
                value = np.asarray(np.ma.filled(dataset[name][index], np.nan), dtype=float)
                if slab_digest(value) != source["months"][index]["fields"][name]["extracted_slab_sha256"]:
                    raise ValueError(f"{month} {name} slab changed")
                fields[name] = value
            for record, box in zip(records, boxes, strict=True):
                result = inventory(box, fields["votemper"], fields["vosaline"], mesh["thickness"], mesh["midpoint"], area, mesh["longitude"], mesh["latitude"])
                if month in baseline_by_box[box["id"]]:
                    old = baseline_by_box[box["id"]][month]
                    if any(result[key] != old[key] for key in ("valid_volume_m3", "valid_wet_cell_count", "strata")):
                        raise ValueError(f"{month} {box['id']} does not reproduce the admitted density inventory")
                record["months"].append({"valid_time": f"2018-{month[-2:]}-01/P1M", **result})
    for record in records:
        changes = []
        for first, second in zip(record["months"], record["months"][1:]):
            previous = {item["id"]: item["volume_m3"] for item in first["strata"]}
            changes.append({"from_valid_time": first["valid_time"], "to_valid_time": second["valid_time"],
                            "stratum_volume_change_m3": [{"id": item["id"], "change_m3": round(item["volume_m3"] - previous[item["id"]], 3)} for item in second["strata"]]})
        record["successive_monthly_mean_differences"] = changes
    return {"schema": "osw-ocean-state-sant-density-inventory-monthly-series-v1",
            "status": "twelve_month_density_bin_occupancy_not_tendency_or_transformation",
            "source": {"path": source_path.relative_to(ROOT).as_posix(), "sha256": sha256(source_path)},
            "baseline": {"path": baseline_path.relative_to(ROOT).as_posix(), "sha256": sha256(baseline_path), "reproduced_months": list(baseline_by_box["primary"])},
            "selection": {"path": selection_path.relative_to(ROOT).as_posix(), "sha256": sha256(selection_path)},
            "sources": {"mesh": {"path": MESH.relative_to(ROOT).as_posix(), "sha256": sha256(MESH)}, "t_metrics": {"path": METRICS.relative_to(ROOT).as_posix(), "sha256": sha256(METRICS)}},
            "method": {"equation_of_state": baseline["method"]["equation_of_state"], "conversion": baseline["method"]["conversion"], "numeric_strata_sigma0_kg_m3": baseline["method"]["numeric_strata_sigma0_kg_m3"], "temporal_support": "monthly mean T/S samples, not instantaneous endpoint states"},
            "partial_cell_fallback_count": mesh["partial_cell_fallback_count"], "boxes": records,
            "boundary": "These are fixed-box density-bin occupancies and differences between monthly means. They are not matched class-volume tendencies, density-class conversion rates, water-mass identities, or a budget. The separately receipted horizontal bin fluxes cannot be subtracted from these differences without compatible time bounds, native mean fluxes, vertical/mixing terms, and assimilation/restoring treatment."}


def validate(payload: dict) -> None:
    if len(payload["boxes"]) != 4 or len(payload["baseline"]["reproduced_months"]) != 4:
        raise ValueError("primary and controls with four baseline matches required")
    for box in payload["boxes"]:
        if len(box["months"]) != 12 or len(box["successive_monthly_mean_differences"]) != 11:
            raise ValueError("complete monthly density inventory required")
        for month in box["months"]:
            if len(month["strata"]) != 4 or abs(sum(item["volume_fraction"] for item in month["strata"]) - 1) > 1e-7:
                raise ValueError("density bins must partition valid volume")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    payload = build()
    validate(payload)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

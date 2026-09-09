"""Build the deterministic browser data bundle for the Ocean Column Address viewer."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROVINCES = ROOT / "research" / "longhurst-province-reference.csv"
CONTRACT = ROOT / "research" / "ocean-column-address-v1.json"
SEED_DEPTHS = ROOT / "research" / "gebco-2026-province-seed-depths.csv"
SEED_SOURCE = ROOT / "research" / "gebco-2026-province-seed-depths-source.json"
OUTPUT = ROOT / "column" / "data.js"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(output: Path = OUTPUT) -> dict:
    with PROVINCES.open(encoding="utf-8", newline="") as handle:
        provinces = list(csv.DictReader(handle))
    with SEED_DEPTHS.open(encoding="utf-8", newline="") as handle:
        seed_depths = {row["code"]: row for row in csv.DictReader(handle)}
    seed_source = json.loads(SEED_SOURCE.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    if len(provinces) != 56 or len({row["code"] for row in provinces}) != 56:
        raise ValueError("province directory must contain 56 unique codes")
    if len(contract["bands"]) != 5:
        raise ValueError("column-address edition 1 must contain five bands")
    if set(seed_depths) != {row["code"] for row in provinces}:
        raise ValueError("GEBCO seed-depth table must cover the 56-code directory")

    for province in provinces:
        sample = seed_depths[province["code"]]
        province["seed_measurement"] = {
            "seed_longitude": float(sample["seed_longitude"]),
            "seed_latitude": float(sample["seed_latitude"]),
            "sampled_longitude": float(sample["sampled_longitude"]),
            "sampled_latitude": float(sample["sampled_latitude"]),
            "elevation_m": int(sample["elevation_m"]),
            "water_depth_m": int(sample["water_depth_m"]) if sample["water_depth_m"] else None,
            "cell_state": sample["cell_state"],
            "deepest_edition1_band": sample["deepest_edition1_band"],
            "tid_code": int(sample["tid_code"]),
            "tid_class": sample["tid_class"],
            "tid_definition": sample["tid_definition"],
            "response_sha256": sample["response_sha256"],
            "tid_response_sha256": sample["tid_response_sha256"],
        }

    payload = {
        "schema": "osw-ocean-column-viewer-data-v1",
        "claim_stage": "reference geography and conceptual teaching overlays",
        "provinces": provinces,
        "column_address": contract,
        "teaching_columns": [
            {"id": "shelf", "name": "Shelf example", "bottom_m": 90},
            {"id": "basin", "name": "Basin example", "bottom_m": 4800},
            {"id": "trench", "name": "Trench example", "bottom_m": 8000},
        ],
        "physical_overlays": [
            {"id": "mixed", "name": "Mixed layer example", "range_m": [0, 80]},
            {"id": "thermocline", "name": "Thermocline example", "range_m": [100, 800]},
            {"id": "watermass", "name": "Water-mass example", "range_m": [600, 3200]},
            {"id": "bottom", "name": "Bottom-boundary example", "height_above_bottom_m": 250},
        ],
        "provenance": {
            "province_directory": str(PROVINCES.relative_to(ROOT)).replace("\\", "/"),
            "province_directory_sha256": sha256(PROVINCES),
            "column_contract": str(CONTRACT.relative_to(ROOT)).replace("\\", "/"),
            "column_contract_sha256": sha256(CONTRACT),
            "seed_depth_table": str(SEED_DEPTHS.relative_to(ROOT)).replace("\\", "/"),
            "seed_depth_table_sha256": sha256(SEED_DEPTHS),
            "seed_source_receipt": str(SEED_SOURCE.relative_to(ROOT)).replace("\\", "/"),
            "seed_source_receipt_sha256": sha256(SEED_SOURCE),
            "seed_source_release": seed_source["source"]["release"],
            "seed_source_doi": seed_source["source"]["doi"],
            "seed_source_acquired_utc": seed_source["acquired_utc"],
        },
        "boundary": (
            "Each GEBCO value is one grid cell nearest an approximate OSW display seed; it is not a province mean, range, profile, or occupancy fraction. "
            "The other three displayed seabeds and all physical overlays are conceptual teaching examples, not observations, detected regimes, heat content, or transport."
        ),
    }
    text = "window.OSW_COLUMN_DATA = " + json.dumps(payload, indent=2, ensure_ascii=False) + ";\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8", newline="\n")
    return payload


if __name__ == "__main__":
    result = build()
    print(f"wrote {len(result['provinces'])} provinces and {len(result['column_address']['bands'])} bands")

"""Build the deterministic browser data bundle for the Ocean Column Address viewer."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROVINCES = ROOT / "research" / "longhurst-province-reference.csv"
CONTRACT = ROOT / "research" / "ocean-column-address-v1.json"
OUTPUT = ROOT / "column" / "data.js"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(output: Path = OUTPUT) -> dict:
    with PROVINCES.open(encoding="utf-8", newline="") as handle:
        provinces = list(csv.DictReader(handle))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    if len(provinces) != 56 or len({row["code"] for row in provinces}) != 56:
        raise ValueError("province directory must contain 56 unique codes")
    if len(contract["bands"]) != 5:
        raise ValueError("column-address edition 1 must contain five bands")

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
        },
        "boundary": (
            "Province identities are a classic reference directory with OSW approximate geometry. "
            "The three displayed seabeds and all physical overlays are conceptual teaching examples, "
            "not local bathymetry, observations, detected regimes, heat content, or transport."
        ),
    }
    text = "window.OSW_COLUMN_DATA = " + json.dumps(payload, indent=2, ensure_ascii=False) + ";\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8", newline="\n")
    return payload


if __name__ == "__main__":
    result = build()
    print(f"wrote {len(result['provinces'])} provinces and {len(result['column_address']['bands'])} bands")

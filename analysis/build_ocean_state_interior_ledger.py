"""Build the first bounded ocean-state interior ledger from committed receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HYDROGRAPHY = ROOT / "research" / "ocean-state-hydrography-pilot-2018.json"
EXCHANGE = ROOT / "research" / "ocean-state-boundary-exchange-pilot-2018.json"
SCHEMA = ROOT / "research" / "ocean-state-interior-ledger-schema-v1.json"
OUTPUT = ROOT / "research" / "ocean-state-interior-ledger-sant-201808.json"
ADDRESS = {"geometry_edition": "longhurst-v4-54", "province": "SANT", "depth_support": "0-200m"}
VALID_TIME = "2018-08-01/P1M"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def compatible(record: dict, address: dict, valid_time: str, label: str) -> None:
    if record.get("address") != address:
        raise ValueError(f"{label} address is incompatible with ledger address")
    if record.get("valid_time") != valid_time:
        raise ValueError(f"{label} time is incompatible with ledger valid time")


def validate(payload: dict) -> None:
    required = {"schema", "status", "address", "valid_time", "contents", "overlays", "internal_links", "boundary_context", "unknowns", "boundary"}
    missing = required - payload.keys()
    if missing:
        raise ValueError(f"ledger is missing required fields: {sorted(missing)}")
    if payload["schema"] != "osw-ocean-state-interior-ledger-v1":
        raise ValueError("unexpected ledger schema")
    if not payload["contents"]:
        raise ValueError("ledger requires at least one admitted contents record")
    for item in payload["contents"]:
        compatible(item, payload["address"], payload["valid_time"], "contents")
        if item["evidence_class"] != "assimilative_reanalysis_model_screen":
            raise ValueError("this pilot admits only the declared model-screen contents class")
    for item in payload["internal_links"]:
        compatible(item, payload["address"], payload["valid_time"], "internal link")
    for item in payload["overlays"]:
        compatible(item, payload["address"], payload["valid_time"], "overlay")
    if payload["boundary_context"]["join_status"] != "not_joined_to_interior_account":
        raise ValueError("boundary context must not be silently joined to the interior account")
    if not payload["unknowns"] or not all(item.get("reason") for item in payload["unknowns"]):
        raise ValueError("ledger must retain named unknowns with reasons")


def build(hydrography_path: Path = HYDROGRAPHY, exchange_path: Path = EXCHANGE, schema_path: Path = SCHEMA) -> dict:
    hydrography_path, exchange_path, schema_path = map(Path, (hydrography_path, exchange_path, schema_path))
    hydrography = load(hydrography_path)
    exchange = load(exchange_path)
    schema = load(schema_path)
    if schema["schema"] != "osw-ocean-state-interior-ledger-schema-v1":
        raise ValueError("unexpected ledger schema contract")
    passport = next((item for item in hydrography["property_passports"] if item["address"] == ADDRESS and item["valid_time"] == VALID_TIME), None)
    if passport is None:
        raise ValueError("pre-registered SANT August 2018 0-200 m passport is unavailable")
    content = {
        "address": passport["address"], "valid_time": passport["valid_time"],
        "property": passport["property"], "units": passport["units"],
        "evidence_class": passport["evidence_class"], "method_version": passport["method_version"],
        "support": passport["support"], "distribution": passport["distribution"],
        "uncertainty": passport["uncertainty"],
        "source_artifact": hydrography_path.relative_to(ROOT).as_posix(),
        "source_artifact_sha256": sha256(hydrography_path),
    }
    payload = {
        "schema": "osw-ocean-state-interior-ledger-v1",
        "status": "first_sparse_contents_and_unknowns_pilot",
        "selection": {
            "frozen_before_result_inspection": True,
            "address": ADDRESS,
            "valid_time": VALID_TIME,
            "rule": "First existing state that participates in the separately selected SANT--SSTC exchange pilot, at the shallowest complete hydrography support and its August 2018 monthly sample.",
        },
        "address": ADDRESS,
        "valid_time": VALID_TIME,
        "contents": [content],
        "overlays": [],
        "internal_links": [],
        "boundary_context": {
            "relation": "has_separately_receipted_boundary_pilot",
            "counterpart_state": "SSTC",
            "source_artifact": exchange_path.relative_to(ROOT).as_posix(),
            "source_artifact_sha256": sha256(exchange_path),
            "evidence_class": "assimilative_reanalysis_model_screen",
            "join_status": "not_joined_to_interior_account",
            "reason": "The exchange pilot uses an open 16-face boundary segment and all-depth transport anatomy. It is not a closed SANT volume, a 0-200 m interior measurement, or a compatible state-budget term.",
        },
        "unknowns": [
            {"relation": "vertical_transfer", "reason": "No admitted vertical velocity, diapycnal flux, mixing, entrainment, or closed compatible budget."},
            {"relation": "lateral_interior_pathway", "reason": "No pre-registered interior seeds, destinations, trajectory control, or tracer pathway is admitted."},
            {"relation": "interior_convergence", "reason": "No closed control-volume geometry and matched boundary/surface/storage terms are admitted."},
            {"relation": "transformation", "reason": "Temperature alone cannot define a water-mass class change; salinity, density, and class-volume flux are unavailable."},
            {"relation": "event_perturbation", "reason": "The admitted 2026 surface heatwave route is spatially and temporally incompatible with this 2018 Drake account."},
        ],
        "boundary": "This ledger indexes one declared reference state, depth support, and month. It reports one temperature distribution and named absences; it does not infer a uniform state interior, a water mass, a pathway, mixing, convergence, heat content, transport, causal mechanism, or budget closure.",
    }
    validate(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hydrography", type=Path, default=HYDROGRAPHY)
    parser.add_argument("--exchange", type=Path, default=EXCHANGE)
    parser.add_argument("--schema", type=Path, default=SCHEMA)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    payload = build(args.hydrography, args.exchange, args.schema)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

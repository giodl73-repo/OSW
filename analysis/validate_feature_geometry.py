"""Offline gate for OSW feature-geometry admission records."""

from __future__ import annotations

import csv
import hashlib
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "research" / "feature-geometry-register.csv"
APP = ROOT / "atlas" / "app.js"
SHA256 = re.compile(r"^[a-f0-9]{64}$")
ALLOWED_EVIDENCE = {"CONCEPTUAL", "SYNTHESIS", "OBSERVATIONAL", "MODELED/MIXED"}
ALLOWED_BASIS = {"illustrative", "observed", "diagnosed", "modeled"}
ALLOWED_LONGITUDE = {"-180_to_180", "0_to_360"}
ALLOWED_STATUS = {"draft", "reviewed", "admitted", "rejected"}


def catalog_ids() -> set[str]:
    return set(re.findall(r'\bid: "([a-z0-9-]+)"', APP.read_text(encoding="utf-8"))[:36])


def validate_register(path: Path = REGISTER) -> list[str]:
    errors: list[str] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = reader.fieldnames or []
    required = {
        "feature_id", "geometry_edition", "evidence_class", "geometry_basis", "provider",
        "product", "variable", "version", "source_url", "license_id", "compatibility",
        "decision_authority", "decision_date", "citation", "acquired_at", "source_checksum",
        "crs", "longitude_convention", "depth_layer", "time_interval", "baseline_threshold",
        "missing_values", "simplification_tolerance", "transform_command", "output_checksum",
        "reviewer_status", "geometry_path"
    }
    missing_columns = sorted(required - set(fields))
    if missing_columns:
        return [f"missing columns: {', '.join(missing_columns)}"]
    known = catalog_ids()
    seen: set[str] = set()
    for line, row in enumerate(rows, 2):
        feature_id = row["feature_id"]
        prefix = f"line {line} ({feature_id or 'missing ID'})"
        for field in required:
            if not row[field].strip():
                errors.append(f"{prefix}: missing {field}")
        if feature_id not in known:
            errors.append(f"{prefix}: unknown feature ID")
        if feature_id in seen:
            errors.append(f"{prefix}: duplicate feature ID")
        seen.add(feature_id)
        if row["evidence_class"] not in ALLOWED_EVIDENCE:
            errors.append(f"{prefix}: invalid evidence class")
        if row["geometry_basis"] not in ALLOWED_BASIS:
            errors.append(f"{prefix}: invalid geometry basis")
        if row["compatibility"] != "compatible":
            errors.append(f"{prefix}: license is not approved as compatible")
        if not row["license_id"].strip():
            errors.append(f"{prefix}: missing SPDX-style license identifier")
        if not row["crs"].strip():
            errors.append(f"{prefix}: undeclared CRS")
        if row["longitude_convention"] not in ALLOWED_LONGITUDE:
            errors.append(f"{prefix}: invalid longitude convention")
        if row["reviewer_status"] not in ALLOWED_STATUS:
            errors.append(f"{prefix}: invalid reviewer status")
        for checksum in ("source_checksum", "output_checksum"):
            if not SHA256.fullmatch(row[checksum]):
                errors.append(f"{prefix}: invalid {checksum}")
        geometry_path = (path.parent / row["geometry_path"]).resolve()
        if geometry_path.is_file():
            actual_checksum = hashlib.sha256(geometry_path.read_bytes()).hexdigest()
            if actual_checksum != row["output_checksum"]:
                errors.append(f"{prefix}: output checksum does not match geometry_path")
        else:
            errors.append(f"{prefix}: geometry_path does not resolve to a file")
        if row["geometry_basis"] == "illustrative" and row["reviewer_status"] == "admitted" and row["evidence_class"] != "CONCEPTUAL":
            errors.append(f"{prefix}: illustrative geometry cannot be admitted as evidence-backed geometry")
        for field in ("simplification_tolerance",):
            value = row[field].strip().lower()
            if value not in {"not applicable", "none"}:
                try:
                    if not math.isfinite(float(value)):
                        raise ValueError
                except ValueError:
                    errors.append(f"{prefix}: non-finite {field}")
    absent = sorted(known - seen)
    if absent:
        errors.append(f"missing catalog IDs: {', '.join(absent)}")
    if len(rows) != 36:
        errors.append(f"expected 36 rows; found {len(rows)}")
    return errors


if __name__ == "__main__":
    failures = validate_register(Path(sys.argv[1]) if len(sys.argv) > 1 else REGISTER)
    if failures:
        print("Feature geometry register rejected:")
        print("\n".join(f"- {failure}" for failure in failures))
        raise SystemExit(1)
    print("Feature geometry register valid: 36 draft/admitted records checked.")

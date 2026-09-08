"""Build the compact offline GEBCO province-seed depth table from raw receipts."""

from __future__ import annotations

import csv
from collections import Counter
import hashlib
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "gebco-2026-province-seed-depths-source.json"
PROVINCES = ROOT / "research" / "longhurst-province-reference.csv"
OUTPUT = ROOT / "research" / "gebco-2026-province-seed-depths.csv"
SUMMARY = ROOT / "research" / "gebco-2026-province-seed-depths-summary.json"


FIELDS = (
    "code", "province", "basin", "biome", "seed_longitude", "seed_latitude",
    "sampled_longitude", "sampled_latitude", "elevation_m", "water_depth_m",
    "cell_state", "deepest_edition1_band", "tid_code", "tid_class",
    "tid_definition", "response_sha256", "tid_response_sha256",
)


def deepest_band(depth: int | None) -> str:
    if depth is None:
        return "unavailable"
    if depth < 200:
        return "epipelagic"
    if depth < 1000:
        return "mesopelagic"
    if depth < 4000:
        return "bathypelagic"
    if depth < 6000:
        return "abyssopelagic"
    return "hadalpelagic"


def tid_class(code: int) -> str:
    if code == 0:
        return "land"
    if 10 <= code <= 17:
        return "direct_measurement"
    if 40 <= code <= 46:
        return "indirect_or_interpolated"
    return "mixed_or_unknown"


def build(source: Path = SOURCE, output: Path = OUTPUT, summary_output: Path = SUMMARY) -> list[dict]:
    payload = json.loads(source.read_text(encoding="utf-8"))
    with PROVINCES.open(encoding="utf-8", newline="") as handle:
        provinces = {row["code"]: row for row in csv.DictReader(handle)}
    rows = []
    for record in payload["records"]:
        raw = record["response_ascii"].encode("utf-8")
        if hashlib.sha256(raw).hexdigest() != record["response_sha256"]:
            raise ValueError(f"response checksum mismatch for {record['code']}")
        tid_raw = record["tid_response_ascii"].encode("utf-8")
        if hashlib.sha256(tid_raw).hexdigest() != record["tid_response_sha256"]:
            raise ValueError(f"TID response checksum mismatch for {record['code']}")
        province = provinces[record["code"]]
        depth = -record["elevation_m"] if record["elevation_m"] < 0 else None
        rows.append({
            "code": record["code"], "province": province["province"],
            "basin": province["basin"], "biome": province["biome"],
            "seed_longitude": record["seed_longitude"], "seed_latitude": record["seed_latitude"],
            "sampled_longitude": record["sampled_longitude"], "sampled_latitude": record["sampled_latitude"],
            "elevation_m": record["elevation_m"], "water_depth_m": "" if depth is None else depth,
            "cell_state": "wet" if depth is not None else "non_wet_seed",
            "deepest_edition1_band": deepest_band(depth),
            "tid_code": record["tid_code"], "tid_class": tid_class(record["tid_code"]),
            "tid_definition": record["tid_definition"],
            "response_sha256": record["response_sha256"],
            "tid_response_sha256": record["tid_response_sha256"],
        })
    rows.sort(key=lambda row: row["code"])
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    output.write_text(stream.getvalue(), encoding="utf-8", newline="\n")
    wet_rows = [row for row in rows if row["cell_state"] == "wet"]
    summary = {
        "schema": "osw-gebco-province-seed-depth-summary-v1",
        "source_release": payload["source"]["release"],
        "source_doi": payload["source"]["doi"],
        "source_receipt_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "record_count": len(rows),
        "wet_count": len(wet_rows),
        "non_wet_count": len(rows) - len(wet_rows),
        "non_wet_codes": [row["code"] for row in rows if row["cell_state"] != "wet"],
        "counts_by_tid_class": dict(sorted(Counter(row["tid_class"] for row in rows).items())),
        "counts_by_deepest_band": dict(sorted(Counter(row["deepest_edition1_band"] for row in rows).items())),
        "boundary": payload["boundary"],
    }
    summary_output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    return rows


if __name__ == "__main__":
    result = build()
    wet = sum(row["cell_state"] == "wet" for row in result)
    print(f"wrote {len(result)} seed cells ({wet} wet, {len(result)-wet} non-wet)")

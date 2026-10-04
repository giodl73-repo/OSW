"""Receipt the provider time metadata behind the SANT monthly box screens."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import requests


ROOT = Path(__file__).resolve().parents[1]
FAMILY = ROOT / "research" / "ocean-state-sant-current-geometry-physical-source-family-2018.json"
OUTPUT = ROOT / "research" / "ocean-state-sant-temporal-support-audit-2018.json"
FIELDS = ("votemper", "vosaline", "vozocrtx", "vomecrty", "sohtcbtm", "sohefldo", "sowaflup")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_receipt(bound: dict) -> dict:
    path = ROOT / bound["path"]
    if sha256(path) != bound["sha256"]:
        raise ValueError(f"source receipt changed: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def source_urls(family: dict) -> dict[str, dict[str, str]]:
    surface = load_receipt(family["surface_storage_terms"]["receipt"])
    urls = {}
    for entry in family["months"]:
        month = entry["month"]
        motion = load_receipt(entry["temperature_velocity"]["receipt"])
        salinity = load_receipt(entry["salinity"]["receipt"])
        if motion["month"] != month or salinity["month"] != month:
            raise ValueError("month mismatch in bound source receipts")
        urls[month] = {name: motion["fields"][name]["url"] for name in ("votemper", "vozocrtx", "vomecrty")}
        urls[month]["vosaline"] = salinity["field"]["url"]
        for name in ("sohtcbtm", "sohefldo", "sowaflup"):
            urls[month][name] = next(item["url"] for item in surface["sources"][name] if item["month"] == month)
    return urls


def attribute(block: str, name: str) -> str | None:
    match = re.search(r"(?:String|Float32|Float64)\s+" + re.escape(name) + r"\s+([^;]+);", block)
    return match.group(1).strip(' "') if match else None


def parse_das(das: str, field: str) -> dict:
    def section(name: str) -> str:
        match = re.search(r"\b" + re.escape(name) + r"\s*\{([^{}]*)\}", das)
        if not match:
            raise ValueError(f"missing {name} DAS section")
        return match.group(1)
    variable, time = section(field), section("time_counter")
    return {
        "time_units": attribute(time, "units"),
        "time_calendar": attribute(time, "calendar"),
        "time_bounds_attribute": attribute(time, "bounds"),
        "online_operation": attribute(variable, "online_operation"),
        "offline_operation": attribute(variable, "offline_operation"),
        "interval_operation_seconds": float(attribute(variable, "interval_operation")),
        "interval_write_seconds": float(attribute(variable, "interval_write")),
    }


def fetch_text(session: requests.Session, url: str) -> tuple[str, str]:
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return response.text, hashlib.sha256(response.content).hexdigest()


def build(session: requests.Session | None = None) -> dict:
    family = json.loads(FAMILY.read_text(encoding="utf-8"))
    urls = source_urls(family)
    session = session or requests.Session()
    months = []
    for month, fields in urls.items():
        records = {}
        for field in FIELDS:
            url = fields[field]
            das, digest = fetch_text(session, url + ".das")
            records[field] = {"source_url": url, "das_sha256": digest, **parse_das(das, field)}
        # The original time coordinate and available dimensions are checked on
        # the heat-content source; all seven DAS time units must agree below.
        source = fields["sohtcbtm"]
        ascii_text, ascii_sha = fetch_text(session, source + ".ascii?time_counter")
        dds, dds_sha = fetch_text(session, source + ".dds")
        values = ascii_text.split("time_counter[1]")
        if len(values) != 2:
            raise ValueError("expected one provider time value")
        time_value = float(values[1].strip())
        months.append({"month": month, "fields": records,
                       "heat_content_time_value": time_value,
                       "heat_content_time_ascii_sha256": ascii_sha,
                       "heat_content_dds_sha256": dds_sha,
                       "heat_content_has_time_bounds_variable": bool(re.search(r"\b(?:time_bnds|time_bounds|time_counter_bounds)\b", dds))})
    payload = {
        "schema": "osw-ocean-state-sant-temporal-support-audit-v1",
        "status": "coindexed_monthly_means_not_matched_tendency_support",
        "source_family": {"path": FAMILY.relative_to(ROOT).as_posix(), "sha256": sha256(FAMILY)},
        "official_variable_inventory": "https://icdc.cen.uni-hamburg.de/thredds/fileServer/ftpthredds/EASYInit/oras5/DOCS/ORAS5_ICDC_variable_list_1x1.pdf",
        "months": months,
        "finding": "All seven probed provider fields in each sampled month share a midmonth time coordinate and averaging-operation attributes. The local derivatives omit these source time coordinates. Provider DAS/DDS metadata do not declare exact averaging bounds; interval_write is 31 days even for February 2018. These monthly means cannot be treated as endpoint states or a matched three-month class-volume tendency.",
        "next_gate": "For a class budget, obtain native time bounds or producer processing documentation, a continuous flux series over matching intervals, and vertical/mixing/assimilation terms; account separately for products of monthly mean velocity and tracers versus native mean advective flux.",
        "boundary": "This audits time metadata and source custody only. It does not estimate a tendency, transformation, flux covariance, residual, or budget closure.",
    }
    validate(payload)
    return payload


def validate(payload: dict) -> None:
    if payload["status"] != "coindexed_monthly_means_not_matched_tendency_support" or len(payload["months"]) != 4:
        raise ValueError("four-month temporal audit required")
    for month in payload["months"]:
        if set(month["fields"]) != set(FIELDS) or month["heat_content_time_value"] != 0 or month["heat_content_has_time_bounds_variable"]:
            raise ValueError("incomplete or unexpected provider time support")
        metadata = list(month["fields"].values())
        if len({item["time_units"] for item in metadata}) != 1:
            raise ValueError("provider fields are not coindexed within month")
        if any(item["online_operation"] != "ave(x)" or item["offline_operation"] != "ave(x)" or item["time_bounds_attribute"] is not None for item in metadata):
            raise ValueError("provider temporal metadata changed")
        expected_midday = 15 if month["month"] == "201802" else 16
        stamp = f"{month['month'][:4]}-{month['month'][4:]}-{expected_midday:02d} 00:00:00 UTC"
        if metadata[0]["time_units"] != f"seconds since {stamp}":
            raise ValueError("unexpected provider time coordinate")
        if any(item["interval_write_seconds"] != 2678400 for item in metadata):
            raise ValueError("provider write interval changed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    payload = build()
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

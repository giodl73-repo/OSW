"""Pure projection for the next cloud delivery; never opens installed artifacts."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "research/atlantic-ax08-goes-2013-seasonal-core-speeds-v1.json"
COLLECTION = "current_core_velocity_estimates"
JOIN = "core_velocity_estimate_ids"
KEY = "published_seasonal_core_velocities_v1"
PARENT = "037ef0045d75dac4b8893df9bf200bd55e049d4708ceaa56195df9d6da9f5cc4"


def document():
    raw = (ROOT / SOURCE).read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def records():
    doc, pin = document()
    scopes = {r["current_id"]: r for r in doc["current_scopes"]}
    rows = []
    for index, original in enumerate(doc["records"]):
        row = copy.deepcopy(original)
        scope = scopes[row["current_id"]]
        row.update(entity_id="current:" + row["current_id"],
                   label=scope["source_label"] + " / " + row["season_label"],
                   quantity="geostrophic_core_velocity_seasonal_fit", unit="m/s",
                   current_scope=copy.deepcopy(scope),
                   common_support=copy.deepcopy(doc["common_support"]),
                   method_discrepancies=[copy.deepcopy(r) for r in doc["method_discrepancies"]
                                         if r["current_id"] == row["current_id"]],
                   source_file=SOURCE, source_file_sha256=pin,
                   source_pointer=f"/records/{index}",
                   source_doi=doc["source"]["doi"], source_url=doc["source"]["url"],
                   observation_count=None, confidence_interval=None,
                   whole_current=False, geometry=None)
        rows.append(row)
    return rows


def prepare(bundle, *, logical_parent_sha256):
    if bundle.get("schema") != "osw.query-bundle.v1" or logical_parent_sha256 != PARENT:
        raise ValueError("Exact installed logical parent required")
    if COLLECTION in bundle["collections"] or KEY in bundle["manifest"]:
        raise ValueError("Seasonal core evidence already present; explicit migration required")
    rows = records()
    expected_owners = {r["entity_id"] for r in rows}
    objects = bundle["collections"]["objects"]
    if any(JOIN in obj for obj in objects):
        raise ValueError("Owner join already present")
    if any(sum(obj["id"] == owner for obj in objects) != 1 for owner in expected_owners):
        raise ValueError("Missing or duplicate seasonal core owner")
    _, pin = document()
    if SOURCE in bundle["manifest"].get("input_sha256", {}):
        raise ValueError("Source already bound; explicit source migration required")
    result = copy.deepcopy(bundle)
    result["collections"][COLLECTION] = rows
    for obj in result["collections"]["objects"]:
        if obj["id"] in expected_owners:
            obj[JOIN] = [r["id"] for r in rows if r["entity_id"] == obj["id"]]
    result["manifest"].setdefault("input_sha256", {})[SOURCE] = pin
    result["manifest"][KEY] = {
        "logical_parent_sha256": PARENT, "source_file": SOURCE,
        "source_file_sha256": pin, "records_added": len(rows),
        "length_or_width_records_added": 0}
    return result

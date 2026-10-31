"""Source-only projection of regional published statistics for a future bundle.

Call prepare only on the verified installed parent in the sequential cloud job.
This module never opens the installed packet or changes length/width records.
"""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "research/eacc-pemba-semba-2019-seasonal-speed-v1.json"
COLLECTION = "current_speed_statistics"
PARENT = "9d35ca1c8cebee0f48e49dd66bb83321b506fa43260f1dd5db4b1e06102293da"
OWNER = "current:east-african-coastal"


def document():
    raw = (ROOT / SOURCE).read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def validate_source(doc):
    if doc["entity_id"] != OWNER:
        raise ValueError("Changed regional source owner")
    monthly = doc["monthly_records"]
    seasonal = doc["records"]
    if sorted(r["month"] for r in monthly) != list(range(1, 13)):
        raise ValueError("Incomplete monthly summaries")
    if sorted(m for r in seasonal for m in r["months"]) != list(range(1, 13)):
        raise ValueError("Overlapping or incomplete seasonal windows")
    if sum(r["observation_count"] for r in monthly) != doc["method"]["observations"]:
        raise ValueError("Monthly count mismatch")
    for row in seasonal + monthly:
        if not (row["minimum"] <= row["median"] <= row["maximum"]
                and row["minimum"] <= row["mean"] <= row["maximum"]
                and row["standard_deviation"] >= 0 and row["observation_count"] > 0):
            raise ValueError("Invalid statistic bounds or sample count")
    for row in seasonal:
        group = [r for r in monthly if r["month"] in row["months"]]
        if (sum(r["observation_count"] for r in group) != row["observation_count"]
                or min(r["minimum"] for r in group) != row["minimum"]
                or max(r["maximum"] for r in group) != row["maximum"]):
            raise ValueError("Monthly/seasonal support mismatch")
        # Rounded means can be cross-checked; medians cannot be averaged.
        mean = sum(r["mean"] * r["observation_count"] for r in group) / row["observation_count"]
        if abs(mean - row["mean"]) > 0.011:
            raise ValueError("Monthly/seasonal mean mismatch beyond printed precision")


def records(doc=None, pin=None):
    if doc is None:
        doc, pin = document()
    validate_source(doc)
    output = []
    for key, period in [("records", "seasonal"), ("monthly_records", "monthly")]:
        for index, original in enumerate(doc[key]):
            row = copy.deepcopy(original)
            row.update(entity_id=OWNER, current_id="east-african-coastal",
                       label="Pemba Channel / " + str(row.get("season", row.get("month"))),
                       region="Pemba Channel", statistic_period=period,
                       observation_support_group="semba-2019-pemba-gdp-1986-2017",
                       overlapping_summary_groups=True,
                       quantity="near_surface_speed_magnitude", unit="m/s",
                       time_support=doc["method"]["window"], fixed_depth_m=None,
                       source_file=SOURCE, source_file_sha256=pin,
                       source_pointer=f"/{key}/{index}", source_doi=doc["source"]["doi"],
                       range_meaning=doc["admission"]["range_meaning"],
                       independent_drifter_count=None, confidence_interval=None,
                       whole_current=False, geometry=None,
                       source_conflicts=doc["source_conflicts"])
            output.append(row)
    return output


def prepare(bundle, *, logical_parent_sha256):
    if logical_parent_sha256 != PARENT or bundle.get("schema") != "osw.query-bundle.v1":
        raise ValueError("Exact installed parent required")
    if COLLECTION in bundle["collections"]:
        raise ValueError("Speed statistics collection already exists; explicit merge required")
    owners = [r for r in bundle["collections"]["objects"] if r["id"] == OWNER]
    if len(owners) != 1 or "speed_statistic_ids" in owners[0]:
        raise ValueError("Missing, duplicate or already joined source owner")
    doc, pin = document()
    rows = records(doc, pin)
    result = copy.deepcopy(bundle)
    result["collections"][COLLECTION] = rows
    owner = next(r for r in result["collections"]["objects"] if r["id"] == OWNER)
    owner["speed_statistic_ids"] = [r["id"] for r in rows]
    manifest = result["manifest"]
    hashes = manifest.setdefault("input_sha256", {})
    if SOURCE in hashes and hashes[SOURCE] != pin:
        raise ValueError("Historical source pin would change")
    hashes[SOURCE] = pin
    manifest["published_current_speed_statistics_v1"] = {
        "logical_parent_sha256": PARENT, "source_file": SOURCE,
        "source_file_sha256": pin, "records_added": len(rows),
        "length_or_width_records_added": 0}
    return result

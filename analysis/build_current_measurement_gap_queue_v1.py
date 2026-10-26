"""Summarize a small historical coverage receipt; never load the query packet."""
import ctypes
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "research/current-measurement-coverage-baseline-v1.json"
OUT = "research/current-measurement-gap-queue-v1.json"


def build():
    raw = (ROOT / BASE).read_bytes()
    assert len(raw) == 129417
    assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == "5531fe006488f17e09b7bf6f7beb6bd95081defd"
    data = json.loads(raw)
    rows = data["records"]
    assert len(rows) == data["currents"] == 106
    assert len({r["id"] for r in rows}) == len(rows)
    counts = Counter()
    records = []
    for row in rows:
        route = bool(row["route_ids"])
        reported = row["published_length_km"] is not None
        widths = bool(row["width_ids"])
        dated_widths = bool(row["width_sample_ids"])
        category = ("route_and_reported" if route and reported else
                    "route_only" if route else "reported_only" if reported else
                    "neither_route_nor_reported")
        counts[category] += 1
        counts["reference_route_owners"] += route
        counts["published_length_owners"] += reported
        counts["scoped_width_id_owners"] += widths
        counts["width_sample_id_owners"] += dated_widths
        if category == "neither_route_nor_reported":
            counts["no_length_" + row["identity_level"]] += 1
        if category != "neither_route_nor_reported":
            action = "Retain existing length scope; inspect seasonal and uncertainty support separately."
        elif row["identity_level"] == "family":
            action = "Identify basin-specific members and measure each supported member separately."
        elif row["identity_level"] == "system":
            action = "Define a source-supported branch graph and length convention before a system total."
        elif row["id"] in {"current:norwegian", "current:spitsbergen-atlantic"}:
            action = "Resolve naming and branch scope before adopting neighbouring current geometry."
        elif row["id"] == "current:loop":
            action = "Finish pending delivery of two published contour summaries; retain method-specific scope and no whole-current rank."
        elif row["id"] == "current:west-australian":
            action = "Review saved regional trace identity and failed connections; do not promote regional numerical paths to a whole-current length."
        else:
            action = "Review primary source for explicit alongflow gates, layer, season and continuous path; then construct a declared reference route."
        records.append({
            "entity_id": row["id"], "label": row["label"],
            "identity_level": row["identity_level"], "length_coverage": category,
            "reference_route_ids": row["route_ids"],
            "published_length_km": row["published_length_km"],
            "scoped_width_ids": row["width_ids"],
            "width_sample_ids": row["width_sample_ids"],
            "whole_current_length_complete": None,
            "whole_current_width_complete": None,
            "seasonal_dimension_ranges_complete": None,
            "next_length_action": action,
        })
    assert counts["reference_route_owners"] == 72
    assert counts["published_length_owners"] == 13
    assert counts["route_and_reported"] == 2
    assert counts["neither_route_nor_reported"] == 23
    assert counts["scoped_width_id_owners"] == 86
    assert counts["width_sample_id_owners"] == 14
    assert counts["no_length_current"] == 10
    assert counts["no_length_family"] == 8
    assert counts["no_length_system"] == 4
    assert counts["no_length_segment"] == 1
    result = {
        "schema": "osw.current-measurement-gap-queue.v1",
        "status": "HISTORICAL_METADATA_TRIAGE_NOT_NEW_MEASUREMENTS",
        "baseline_file": BASE,
        "baseline_sha256": hashlib.sha256(raw).hexdigest(),
        "baseline_git_blob_oid": "5531fe006488f17e09b7bf6f7beb6bd95081defd",
        "baseline_remote_commit": "6dfc3248dc1cf8df3d2cb8090584a53df56136cc",
        "baseline_logical_sha256": data["bundle_sha256"],
        "baseline_source_run_id": data["source_run_id"],
        "current_packet_requeried": False,
        "named_currents": 106, "counts": dict(sorted(counts.items())),
        "length_evidence_or_route_owners": 83,
        "limitations": [
            "Counts describe the pinned historical coverage snapshot, not a newly queried installed packet.",
            "Reference routes, published estimates and local studied reaches differ in physical scope; coverage is not ranking eligibility.",
            "Scoped width IDs and dated sample IDs do not prove paired boundaries, whole-current width, annual extrema or uncertainty.",
            "Missing metadata does not establish that published measurements do not exist.",
            "No catalog-wide depth or seasonal completeness percentage can be derived from this snapshot.",
            "The pending Loop evidence batch adds summaries/events, not reference-route or published whole-current length coverage.",
        ],
        "new_measurements": 0,
        "records": records,
    }
    (ROOT / OUT).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": OUT, "counts": result["counts"]}, indent=2))


if __name__ == "__main__":
    kernel = ctypes.windll.kernel32
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    kernel.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
    kernel.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    assert kernel.SetProcessAffinityMask(kernel.GetCurrentProcess(), 1)
    assert kernel.SetPriorityClass(kernel.GetCurrentProcess(), 0x4000)
    build()

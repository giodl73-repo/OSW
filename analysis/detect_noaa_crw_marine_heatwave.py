"""Apply OSW's duration identity test to a NOAA CRW heatwave-category point series."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "atlas" / "data" / "noaa-crw-mhw-point-north-atlantic-2026.json"
DEFAULT_OUTPUT = ROOT / "research" / "osw-d1-noaa-crw-mhw-point-2026.json"


def load_run_finder():
    path = Path(__file__).with_name("detect_oisst_marine_heatwave.py")
    spec = importlib.util.spec_from_file_location("osw_mhw_detector", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.qualifying_runs


QUALIFYING_RUNS = load_run_finder()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def detect(rows, minimum_duration=5, maximum_gap=2):
    runs = QUALIFYING_RUNS([category > 0 and mask == 0 for _, category, mask in rows], minimum_duration, maximum_gap)
    events = []
    for start, end in runs:
        span = rows[start : end + 1]
        categories = [category for _, category, _ in span]
        events.append({
            "start_date": span[0][0],
            "end_date": span[-1][0],
            "duration_days": len(span),
            "maximum_category": max(categories),
            "category_day_counts": {str(category): categories.count(category) for category in sorted(set(categories))},
            "left_censored": start == 0,
            "right_censored": end == len(rows) - 1,
        })
    return events


def build(source_path=DEFAULT_SOURCE, output_path=DEFAULT_OUTPUT):
    source_path, output_path = Path(source_path), Path(output_path)
    source = json.loads(source_path.read_text(encoding="utf-8"))
    events = detect(source["rows"])
    payload = {
        "schema": "osw.detected-ocean-object.v1",
        "detection_id": "OSW-D1",
        "status": "detected_object" if events else "no_event_detected",
        "object_id": "OBJ046",
        "object_name": "marine heatwave",
        "evidence_origin": "derived_observation_product",
        "source_artifact": source_path.relative_to(ROOT).as_posix(),
        "source_artifact_sha256": sha256(source_path),
        "coordinate": source["coordinate"],
        "method": {
            "upstream_threshold": "NOAA CRW seasonally varying local 90th-percentile category product",
            "upstream_climatology": "CoralTemp SST, 1985-01-01 through 2012-12-31; 11-day daily windows",
            "minimum_duration_days": 5,
            "join_events_across_gaps_days": 2,
            "osw_event_rule": "unmasked category greater than zero for at least five contiguous days; retain qualifying runs before joining across gaps",
        },
        "event_window": source["window"],
        "event_count": len(events),
        "events": events,
        "identity_evaluation": {
            "result": "pass" if events else "fail",
            "test": "SST exceeds a seasonally varying local high-percentile threshold for the required duration under a declared gap rule.",
            "finding": f"{len(events)} duration-qualified event(s) detected at the declared NOAA CRW pixel." if events else "No duration-qualified event was detected in the declared window.",
        },
        "daily_categories": source["rows"],
        "boundary": "A duration-qualified detection at one 0.05-degree pixel of a NOAA derived surface product. It is not a spatial footprint, independent raw-SST reimplementation, subsurface heatwave, heat content, transport, causal attribution, or ecological-impact estimate. An event touching a window edge is explicitly censored.",
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build(args.source, args.output)
    print(f'wrote {args.output}: {payload["status"]}, {payload["event_count"]} event(s)')


if __name__ == "__main__":
    main()

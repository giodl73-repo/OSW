"""Pair spatial and temporal release sensitivities without a composite score."""

from __future__ import annotations

import argparse
import collections
import json
import pathlib


def completion_class(completed: int, total: int) -> str:
    if completed == total:
        return "full"
    if completed == 0:
        return "lost"
    return "mixed"


def synthesize(position: dict, time: dict) -> dict:
    position_groups = {group["base_id"]: group for group in position["groups"]}
    time_groups = {group["base_id"]: group for group in time["groups"]}
    if set(position_groups) != set(time_groups):
        raise ValueError("position and time studies do not contain identical base releases")
    releases = []
    patterns = collections.Counter()
    for base_id in sorted(position_groups):
        spatial = position_groups[base_id]
        temporal = time_groups[base_id]
        spatial_class = completion_class(spatial["completed"], 9)
        temporal_class = completion_class(temporal["completed"], 5)
        pattern = f"{spatial_class}/{temporal_class}"
        patterns[pattern] += 1
        releases.append({
            "base_id": base_id,
            "release_time": spatial["release_time"],
            "release_index": spatial["release_index"],
            "central_status": spatial["central_status"],
            "position": {
                "completed": spatial["completed"], "total": 9,
                "class": spatial_class,
                "endpoint_separation_from_central_km": spatial["completed_endpoint_separation_from_central_km"],
            },
            "time": {
                "completed": temporal["completed"], "total": 5,
                "class": temporal_class,
                "endpoint_separation_from_central_km": temporal["completed_endpoint_separation_from_central_km"],
            },
            "paired_pattern": pattern,
        })
    dual_full = patterns["full/full"]
    dual_lost = patterns["lost/lost"]
    return {
        "schema": "oceanlines.osw.m2-release-sensitivity-pair.v1",
        "status": "paired release-position and release-time diagnostics without composite scoring",
        "source_receipts": {
            "position_schema": position["schema"], "time_schema": time["schema"],
            "position_field_sha256": position["velocity_source"]["field_sha256"],
            "time_field_sha256": time["velocity_source"]["field_sha256"],
        },
        "summary": {
            "base_releases": len(releases),
            "full_under_both": dual_full,
            "lost_under_both": dual_lost,
            "other_or_mixed": len(releases) - dual_full - dual_lost,
            "paired_pattern_counts": dict(sorted(patterns.items())),
        },
        "releases": releases,
        "interpretation": (
            "The paired passport preserves position and time sensitivity as separate diagnostics. "
            "Full/full marks completion stability under the declared tests, not probability, "
            "trajectory certainty, exchange, residence, or heat transport."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--position", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-release-sensitivity-2018.json"))
    parser.add_argument("--time", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-release-time-sensitivity-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-release-sensitivity-pair-2018.json"))
    args = parser.parse_args()
    result = synthesize(
        json.loads(args.position.read_text(encoding="utf-8")),
        json.loads(args.time.read_text(encoding="utf-8")),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {result['summary']}")


if __name__ == "__main__":
    main()

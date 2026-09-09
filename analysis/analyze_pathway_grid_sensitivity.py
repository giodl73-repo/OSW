"""Compare matching M2 pathway releases on two spatial samplings."""

from __future__ import annotations

import argparse
import json
import pathlib

from analyze_pathway_timestep_sensitivity import distance_km, percentile


def analyze(reference: dict, comparison: dict, reference_label: str, comparison_label: str) -> dict:
    reference_tracks = {track["id"]: track for track in reference["tracks"]}
    comparison_tracks = {track["id"]: track for track in comparison["tracks"]}
    if set(reference_tracks) != set(comparison_tracks):
        raise ValueError("runs do not contain identical release identities")
    identities = sorted(reference_tracks)
    status_disagreements = [
        {"id": identity, "reference_status": reference_tracks[identity]["status"], "comparison_status": comparison_tracks[identity]["status"]}
        for identity in identities
        if reference_tracks[identity]["status"] != comparison_tracks[identity]["status"]
    ]
    common_completed = [
        identity for identity in identities
        if reference_tracks[identity]["status"] == comparison_tracks[identity]["status"] == "completed"
    ]
    separations = [
        distance_km(reference_tracks[identity]["points"][-1], comparison_tracks[identity]["points"][-1])
        for identity in common_completed
    ]
    ordered = sorted(separations)
    middle = len(ordered) // 2
    median = ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2
    return {
        "schema": "oceanlines.osw.m2-grid-sensitivity.v1",
        "status": "spatial-sampling sensitivity diagnostic for historical surface-pathway method pilot",
        "reference": {"label": reference_label, "velocity_source": reference["velocity_source"], "summary": reference["summary"]},
        "comparison": {"label": comparison_label, "velocity_source": comparison["velocity_source"], "summary": comparison["summary"]},
        "release_count": len(identities),
        "status_disagreement_count": len(status_disagreements),
        "status_disagreements": status_disagreements,
        "common_completed_tracks": len(common_completed),
        "common_completed_endpoint_separation_km": {
            "median": median,
            "p95_nearest_rank": percentile(separations, .95),
            "maximum": max(separations),
        },
        "interpretation": (
            "The coarsened and native-resolution fields yield the same aggregate completion count "
            "but not the same track identities or endpoint geography. Aggregate agreement therefore "
            "does not validate coarse path shapes; the native regional field remains primary."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-pathways-2018.json"))
    parser.add_argument("--comparison", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-pathways-coarse-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-grid-sensitivity-2018.json"))
    args = parser.parse_args()
    result = analyze(
        json.loads(args.reference.read_text(encoding="utf-8")),
        json.loads(args.comparison.read_text(encoding="utf-8")),
        "native approximately one-third degree", "coarsened approximately two-thirds degree",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {result['status_disagreement_count']} status disagreements; max endpoint separation {result['common_completed_endpoint_separation_km']['maximum']:.2f} km")


if __name__ == "__main__":
    main()

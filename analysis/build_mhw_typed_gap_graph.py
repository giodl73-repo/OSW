"""Extend OSW-D7 with an explicitly typed temporal bridge to the D4 post-gap lineage."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FAMILY = ROOT / "research" / "osw-d7-noaa-crw-mhw-lineage-family-2026.json"
DEFAULT_GAP = ROOT / "research" / "osw-d4-noaa-crw-mhw-gap-identity-2026.json"
DEFAULT_PRIMARY = ROOT / "research" / "osw-d3-noaa-crw-mhw-lineage-2026.json"
DEFAULT_OUTPUT = ROOT / "research" / "osw-d9-noaa-crw-mhw-typed-gap-graph-2026.json"


def coordinate_cells(rows, resolution=0.05):
    cells = set()
    for latitude, runs in rows:
        for west, east, _category in runs:
            steps = round((east - west) / resolution)
            cells.update((round(latitude, 3), round(west + index * resolution, 3)) for index in range(steps + 1))
    return cells


def cells_sha256(cells):
    encoded = ";".join(f"{lat:.3f},{lon:.3f}" for lat, lon in sorted(cells)).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def overlap_metrics(before, after):
    intersection = len(before & after)
    return {
        "intersection_pixels": intersection,
        "iou": round(intersection / len(before | after), 4),
        "source_retained_fraction": round(intersection / len(before), 4),
        "target_inherited_fraction": round(intersection / len(after), 4),
    }


def build(family_path=DEFAULT_FAMILY, gap_path=DEFAULT_GAP, primary_path=DEFAULT_PRIMARY, output_path=DEFAULT_OUTPUT):
    family_path, gap_path, primary_path, output_path = map(Path, (family_path, gap_path, primary_path, output_path))
    family = json.loads(family_path.read_text(encoding="utf-8"))
    gap = json.loads(gap_path.read_text(encoding="utf-8"))
    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    primary_aug10 = next(item for item in primary["daily_footprints"] if item["date"] == "2026-08-10")
    if primary_aug10["component_rows"] != gap["pre_gap_footprint"]["component_rows"]:
        raise ValueError("D4 pre-gap footprint does not reproduce the D3 August 10 component")
    family_aug10 = next(
        item for item in family["nodes"]
        if item["date"] == "2026-08-10" and item["on_d3_primary_branch"]
    )
    pre_cells = coordinate_cells(gap["pre_gap_footprint"]["component_rows"])
    post_daily = gap["post_gap_lineage"]["daily_footprints"]
    post_nodes = []
    post_cells = {}
    for index, item in enumerate(post_daily, 1):
        cells = coordinate_cells(item["component_rows"])
        post_cells[item["date"]] = cells
        post_nodes.append({
            "node_id": f'{item["date"]}-POST-C{index:02d}',
            "date": item["date"],
            "component_coordinate_sha256": cells_sha256(cells),
            "summary": item["summary"],
            "source_role": "D4 post-gap primary lineage",
        })
    post_edges = []
    for before, after in zip(post_nodes, post_nodes[1:]):
        metrics = overlap_metrics(post_cells[before["date"]], post_cells[after["date"]])
        if metrics["intersection_pixels"] == 0:
            raise ValueError("D4 post-gap lineage contains a non-overlapping adjacent transition")
        post_edges.append({
            "from": before["node_id"],
            "to": after["node_id"],
            "edge_type": "adjacent_day_exact_overlap",
            "elapsed_days": 1,
            "threshold_inactive_days": 0,
            **metrics,
        })
    bridge_metrics = overlap_metrics(pre_cells, post_cells["2026-08-12"])
    expected = gap["bridge_metrics"]
    if any(bridge_metrics[key] != expected[key] for key in ("intersection_pixels", "iou")):
        raise ValueError("typed bridge does not reproduce D4 exact overlap")
    bridge = {
        "from": family_aug10["node_id"],
        "to": post_nodes[0]["node_id"],
        "edge_type": "one_day_threshold_gap_exact_spatial_overlap",
        "elapsed_days": 2,
        "threshold_inactive_days": 1,
        "inactive_date": gap["gap"]["date"],
        "active_source_pixels_remaining_on_inactive_date": gap["gap"]["active_pre_gap_pixels_remaining_on_gap_day"],
        "spatial_dilation_cells_required": expected["spatial_dilation_cells_required"],
        **bridge_metrics,
        "policy": "permit one threshold-inactive day between duration-qualified runs, then require exact spatial overlap",
    }
    strict_nodes = family["summary"]["node_count"]
    strict_edges = family["summary"]["edge_count"]
    payload = {
        "schema": "osw.ocean-object-typed-gap-graph.v1",
        "detection_id": "OSW-D9",
        "status": "policy_conditioned_graph_extension",
        "object_id": "OBJ046",
        "object_name": "marine heatwave",
        "source_artifacts": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in (family_path, gap_path, primary_path)
        ],
        "edge_vocabulary": {
            "adjacent_day_exact_overlap": "solid evidence edge between threshold-active components on consecutive daily fields",
            "one_day_threshold_gap_exact_spatial_overlap": "conditional bridge spanning one threshold-inactive day; endpoints overlap geographically but no daily inheritance exists on the intervening field",
        },
        "base_family": {
            "source_detection_id": family["detection_id"],
            "start": family["tracked_window"]["start"],
            "end": family["tracked_window"]["end"],
            "node_count": strict_nodes,
            "edge_count": strict_edges,
            "primary_branch_node_count": family["summary"]["primary_branch_node_count"],
            "side_component_count": family["summary"]["off_primary_node_count"],
            "split_node_count": family["summary"]["split_node_count"],
            "merge_node_count": family["summary"]["merge_node_count"],
        },
        "post_gap_primary_lineage": {
            "source_detection_id": gap["detection_id"],
            "start": gap["post_gap_lineage"]["start"],
            "end": gap["post_gap_lineage"]["end"],
            "day_count": gap["post_gap_lineage"]["day_count"],
            "completeness": "one governed primary lineage, not a complete post-gap branch family",
            "nodes": post_nodes,
            "edges": post_edges,
        },
        "typed_bridge": bridge,
        "policy_bakeoff": [
            {
                "policy": "adjacent daily exact-overlap edges only",
                "reconnects": False,
                "graph_start": family["tracked_window"]["start"],
                "graph_end": family["tracked_window"]["end"],
                "node_count": strict_nodes,
                "edge_count": strict_edges,
            },
            {
                "policy": "allow one typed threshold-gap edge with exact endpoint overlap",
                "reconnects": True,
                "graph_start": family["tracked_window"]["start"],
                "graph_end": gap["post_gap_lineage"]["end"],
                "node_count": strict_nodes + len(post_nodes),
                "edge_count": strict_edges + len(post_edges) + 1,
            },
        ],
        "identity_evaluation": {
            "result": "policy_dependent",
            "finding": "The exact daily family ends August 10; one explicitly typed gap edge conditionally connects its primary trunk to a seven-day post-gap primary lineage through August 18.",
        },
        "boundary": "The bridge records a declared event-identity policy, not threshold evidence on August 11, interpolation, or material continuity. Its endpoints share exact grid locations, but the intervening day has zero inherited active pixels. The pre-gap side branches are complete under D7's rule; the post-gap addition is only D4's primary lineage, not a complete branch-family expansion. Forcing, advection, subsurface extent, attribution, and impacts remain untested.",
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", type=Path, default=DEFAULT_FAMILY)
    parser.add_argument("--gap", type=Path, default=DEFAULT_GAP)
    parser.add_argument("--primary", type=Path, default=DEFAULT_PRIMARY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build(args.family, args.gap, args.primary, args.output)
    joined = payload["policy_bakeoff"][1]
    print(f'wrote {args.output}: {joined["node_count"]} nodes, {joined["edge_count"]} edges with typed bridge')


if __name__ == "__main__":
    main()

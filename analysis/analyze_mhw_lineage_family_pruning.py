"""Test how minimum component area changes the OSW-D7 lineage family."""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "research" / "osw-d7-noaa-crw-mhw-lineage-family-2026.json"
DEFAULT_OUTPUT = ROOT / "research" / "osw-d8-noaa-crw-mhw-family-pruning-2026.json"
THRESHOLDS_KM2 = [0, 25, 250, 500, 1000, 1500]
ANCHOR_PREFIX = "2026-07-23-"


def retained_graph(payload, minimum_area_km2):
    nodes = {item["node_id"]: item for item in payload["nodes"]}
    eligible = {
        node_id for node_id, node in nodes.items()
        if node["summary"]["area_km2"] >= minimum_area_km2
    }
    anchor = next(node_id for node_id in nodes if node_id.startswith(ANCHOR_PREFIX) and nodes[node_id]["on_d3_primary_branch"])
    if anchor not in eligible:
        raise ValueError("minimum area removes the anchor component")
    adjacency = {node_id: set() for node_id in eligible}
    for edge in payload["edges"]:
        if edge["from"] in eligible and edge["to"] in eligible:
            adjacency[edge["from"]].add(edge["to"])
            adjacency[edge["to"]].add(edge["from"])
    reached = {anchor}
    queue = deque([anchor])
    while queue:
        node_id = queue.popleft()
        for neighbor in adjacency[node_id]:
            if neighbor not in reached:
                reached.add(neighbor)
                queue.append(neighbor)
    edges = [edge for edge in payload["edges"] if edge["from"] in reached and edge["to"] in reached]
    indegree = {node_id: 0 for node_id in reached}
    outdegree = {node_id: 0 for node_id in reached}
    for edge in edges:
        outdegree[edge["from"]] += 1
        indegree[edge["to"]] += 1
    primary = {node_id for node_id in reached if nodes[node_id]["on_d3_primary_branch"]}
    side = reached - primary
    merge_back = {
        node_id for node_id in side
        if any(edge["from"] == node_id and edge["to"] in primary for edge in edges)
    }
    return {
        "minimum_component_area_km2": minimum_area_km2,
        "node_count": len(reached),
        "edge_count": len(edges),
        "primary_node_count": len(primary),
        "side_component_count": len(side),
        "split_node_count": sum(value > 1 for value in outdegree.values()),
        "merge_node_count": sum(value > 1 for value in indegree.values()),
        "side_terminal_count": sum(outdegree[node_id] == 0 for node_id in side),
        "side_merge_back_count": len(merge_back),
        "smallest_retained_side_area_km2": min((nodes[node_id]["summary"]["area_km2"] for node_id in side), default=None),
        "largest_removed_component_area_km2": max(
            (node["summary"]["area_km2"] for node_id, node in nodes.items() if node_id not in reached),
            default=None,
        ),
        "retained_node_ids": sorted(reached),
    }


def build(input_path=DEFAULT_INPUT, output_path=DEFAULT_OUTPUT):
    input_path, output_path = Path(input_path), Path(output_path)
    family = json.loads(input_path.read_text(encoding="utf-8"))
    results = [retained_graph(family, threshold) for threshold in THRESHOLDS_KM2]
    if results[0]["node_count"] != family["summary"]["node_count"] or results[0]["edge_count"] != family["summary"]["edge_count"]:
        raise ValueError("zero-threshold policy does not reproduce OSW-D7")
    primary_counts = {result["primary_node_count"] for result in results}
    if primary_counts != {family["summary"]["primary_branch_node_count"]}:
        raise ValueError("declared pruning ladder unexpectedly removes primary-trunk nodes")
    payload = {
        "schema": "osw.ocean-object-lineage-pruning-sensitivity.v1",
        "detection_id": "OSW-D8",
        "status": "family_scale_bakeoff",
        "object_id": "OBJ046",
        "object_name": "marine heatwave",
        "source_artifact": {
            "path": input_path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        },
        "method": {
            "threshold_variable": "daily connected-component area",
            "threshold_units": "km2",
            "threshold_values": THRESHOLDS_KM2,
            "pruning": "remove nodes below the declared area, remove incident edges, then retain only the weakly connected graph containing the July 23 anchor",
            "primary_trunk_override": False,
            "threshold_selection": "illustrative diagnostic ladder chosen to span one-cell branches through the largest 54-cell side component; not a calibrated universal rule",
        },
        "results": results,
        "identity_evaluation": {
            "result": "policy_dependent",
            "finding": "The 21-node primary trunk survives every tested area threshold, while side-branch and split/merge topology changes with the declared minimum component scale.",
        },
        "boundary": "Area pruning tests representation stability, not whether small components are physically unreal, erroneous, or unimportant. Thresholds are illustrative and specific to this product, grid, latitude, cadence, and event. The analysis preserves the anchor-connected induced graph and does not test temporal gaps, material parcels, forcing, advection, subsurface extent, impacts, or a uniquely correct minimum size.",
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build(args.input, args.output)
    print(f'wrote {args.output}: {len(payload["results"])} area thresholds')


if __name__ == "__main__":
    main()

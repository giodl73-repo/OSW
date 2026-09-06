"""Test whether seasonal surface direction supports a stable natural partition count."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from pathlib import Path

from audit_regions_against_motion import cell_seasons, load_javascript


class UnionFind:
    def __init__(self, items):
        self.parent = {item: item for item in items}
        self.size = {item: 1 for item in items}

    def find(self, item):
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left, right):
        left_root, right_root = self.find(left), self.find(right)
        if left_root == right_root:
            return
        if self.size[left_root] < self.size[right_root]:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root
        self.size[left_root] += self.size[right_root]


def directional_similarity(left, right) -> float:
    values = []
    for (left_u, left_v, left_speed), (right_u, right_v, right_speed) in zip(left, right):
        dot = (left_u * right_u + left_v * right_v) / (left_speed * right_speed)
        values.append(max(-1.0, min(1.0, dot)))
    return sum(values) / len(values)


def supported_grid(payload: dict):
    rows, columns = payload["shape"]
    vectors = {}
    for index in range(rows * columns):
        seasons = cell_seasons(payload, index)
        if seasons:
            vectors[index] = seasons
    edges = []
    for row in range(rows):
        for column in range(columns):
            index = row * columns + column
            if index not in vectors:
                continue
            east = row * columns + ((column + 1) % columns)
            south = (row + 1) * columns + column if row + 1 < rows else None
            for neighbor in (east, south):
                if neighbor is not None and neighbor in vectors:
                    edges.append((index, neighbor, directional_similarity(vectors[index], vectors[neighbor])))
    return vectors, edges


def partition(vectors: dict, edges: list[tuple[int, int, float]], threshold: float) -> tuple[dict[int, int], list[int]]:
    union = UnionFind(vectors)
    for left, right, similarity in edges:
        if similarity >= threshold:
            union.union(left, right)
    roots = {index: union.find(index) for index in vectors}
    ordered_roots = sorted(set(roots.values()), key=lambda root: (-union.size[root], root))
    labels = {root: label for label, root in enumerate(ordered_roots)}
    assignments = {index: labels[root] for index, root in roots.items()}
    sizes = [union.size[root] for root in ordered_roots]
    return assignments, sizes


def analyze(payload: dict, source_artifact_sha256: str, analyzed_at: str, thresholds: list[float]) -> dict:
    vectors, edges = supported_grid(payload)
    results = []
    assignments = {}
    for threshold in thresholds:
        labels, sizes = partition(vectors, edges, threshold)
        key = f"{threshold:.2f}"
        assignments[key] = [labels.get(index) for index in range(payload["shape"][0] * payload["shape"][1])]
        results.append({
            "direction_similarity_threshold": threshold,
            "all_components": len(sizes),
            "components_at_least_3_cells": sum(size >= 3 for size in sizes),
            "components_at_least_5_cells": sum(size >= 5 for size in sizes),
            "components_at_least_10_cells": sum(size >= 10 for size in sizes),
            "largest_component_cells": sizes[0],
            "largest_component_fraction": sizes[0] / len(vectors),
            "cells_in_components_at_least_5": sum(size for size in sizes if size >= 5),
            "fraction_in_components_at_least_5": sum(size for size in sizes if size >= 5) / len(vectors),
        })
    return {
        "schema": "oceanlines.osw.motion-partition-sensitivity.v1",
        "status": "zoning-free diagnostic; no proposed partition",
        "source_artifact_sha256": source_artifact_sha256,
        "source_data_sha256": payload["source_sha256"],
        "source_period_start": payload["period_start"],
        "source_period_stop": payload["period_stop"],
        "analyzed_at": analyzed_at,
        "shape": payload["shape"],
        "latitude_values": payload["latitude_values"],
        "longitude_values": payload["longitude_values"],
        "supported_cells": len(vectors),
        "supported_neighbor_edges": len(edges),
        "definition": "neighboring supported cells join when their mean cosine similarity across DJF, MAM, JJA, and SON meets the declared threshold",
        "results": results,
        "assignments": assignments,
        "boundary": "Connected components depend on grid, neighborhood, temporal sample, direction metric, and threshold. They are sensitivity objects, not ocean regions or natural kinds.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--csv-output", type=Path, required=True)
    parser.add_argument("--analyzed-at")
    parser.add_argument("--thresholds", default="0.00,0.10,0.20,0.30,0.40,0.50,0.60,0.70,0.80,0.90")
    args = parser.parse_args()
    payload, digest = load_javascript(args.input)
    thresholds = [float(value) for value in args.thresholds.split(",")]
    analyzed_at = args.analyzed_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    result = analyze(payload, digest, analyzed_at, thresholds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    args.csv_output.parent.mkdir(parents=True, exist_ok=True)
    with args.csv_output.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(result["results"][0]))
        writer.writeheader()
        writer.writerows(result["results"])
    print(f"wrote {args.output} ({len(thresholds)} thresholds)")


if __name__ == "__main__":
    main()

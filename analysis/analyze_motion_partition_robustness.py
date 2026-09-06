"""Stress-test motion partition counts across neighborhoods and seasonal subsets."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from pathlib import Path

from analyze_motion_partition_sensitivity import directional_similarity, partition
from audit_regions_against_motion import cell_seasons, load_javascript


CONFIGURATIONS = (
    ("4N_ALL", "4-neighbor · all seasons", ((0, 1), (1, 0)), (0, 1, 2, 3)),
    ("8N_ALL", "8-neighbor · all seasons", ((0, 1), (1, 0), (1, 1), (1, -1)), (0, 1, 2, 3)),
    ("4N_NO_DJF", "4-neighbor · omit DJF", ((0, 1), (1, 0)), (1, 2, 3)),
    ("4N_NO_MAM", "4-neighbor · omit MAM", ((0, 1), (1, 0)), (0, 2, 3)),
    ("4N_NO_JJA", "4-neighbor · omit JJA", ((0, 1), (1, 0)), (0, 1, 3)),
    ("4N_NO_SON", "4-neighbor · omit SON", ((0, 1), (1, 0)), (0, 1, 2)),
)


def configured_grid(payload: dict, offsets, season_indices):
    rows, columns = payload["shape"]
    vectors = {}
    for index in range(rows * columns):
        seasons = cell_seasons(payload, index)
        if seasons:
            vectors[index] = [seasons[position] for position in season_indices]
    edges = []
    for row in range(rows):
        for column in range(columns):
            index = row * columns + column
            if index not in vectors:
                continue
            for row_delta, column_delta in offsets:
                neighbor_row = row + row_delta
                if not 0 <= neighbor_row < rows:
                    continue
                neighbor_column = (column + column_delta) % columns
                neighbor = neighbor_row * columns + neighbor_column
                if neighbor in vectors:
                    edges.append((index, neighbor, directional_similarity(vectors[index], vectors[neighbor])))
    return vectors, edges


def analyze(payload: dict, source_artifact_sha256: str, analyzed_at: str, thresholds: list[float]) -> dict:
    configurations = []
    comparison_rows = []
    for code, label, offsets, seasons in CONFIGURATIONS:
        vectors, edges = configured_grid(payload, offsets, seasons)
        results = []
        assignments = {}
        for threshold in thresholds:
            labels, sizes = partition(vectors, edges, threshold)
            key = f"{threshold:.2f}"
            assignments[key] = [labels.get(index) for index in range(payload["shape"][0] * payload["shape"][1])]
            result = {
                "direction_similarity_threshold": threshold,
                "components_at_least_5_cells": sum(size >= 5 for size in sizes),
                "largest_component_cells": sizes[0],
                "fraction_in_components_at_least_5": sum(size for size in sizes if size >= 5) / len(vectors),
            }
            results.append(result)
            comparison_rows.append({"configuration": code, "label": label, **result})
        configurations.append({
            "code": code,
            "label": label,
            "neighbor_offsets": [list(offset) for offset in offsets],
            "season_indices": list(seasons),
            "supported_neighbor_edges": len(edges),
            "results": results,
            "assignments": assignments,
        })
    return {
        "schema": "oceanlines.osw.motion-partition-robustness.v1",
        "status": "zoning-free robustness diagnostic; no proposed partition",
        "source_artifact_sha256": source_artifact_sha256,
        "source_data_sha256": payload["source_sha256"],
        "source_period_start": payload["period_start"],
        "source_period_stop": payload["period_stop"],
        "analyzed_at": analyzed_at,
        "shape": payload["shape"],
        "latitude_values": payload["latitude_values"],
        "longitude_values": payload["longitude_values"],
        "supported_cells": sum(cell_seasons(payload, index) is not None for index in range(payload["shape"][0] * payload["shape"][1])),
        "configurations": configurations,
        "boundary": "Counts depend on adjacency, included seasons, threshold, grid, and minimum component size. Leave-one-season-out cases are sensitivity checks, not independent replicates.",
        "comparison_rows": comparison_rows,
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
    result = analyze(
        payload, digest,
        args.analyzed_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        [float(value) for value in args.thresholds.split(",")],
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    args.csv_output.parent.mkdir(parents=True, exist_ok=True)
    with args.csv_output.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(result["comparison_rows"][0]))
        writer.writeheader()
        writer.writerows(result["comparison_rows"])
    print(f"wrote {args.output} ({len(result['configurations'])} configurations)")


if __name__ == "__main__":
    main()

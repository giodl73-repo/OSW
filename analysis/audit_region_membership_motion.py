"""Audit how 56 province-level seasonal signatures agree inside 22 OSW regions."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

from analyze_motion_partition_sensitivity import directional_similarity
from audit_regions_against_motion import cell_seasons, load_javascript, nearest_state
from build_province_cartogram import CONTIGUOUS_REGIONS, PROVINCES


def state_directory() -> dict[str, str]:
    return {code: name for provinces in PROVINCES.values() for code, name, _ in provinces}


def state_signatures(payload: dict) -> tuple[dict[str, dict], dict[str, int]]:
    rows, columns = payload["shape"]
    seasonal_vectors = defaultdict(lambda: [[] for _ in payload["season_order"]])
    cell_counts = defaultdict(int)
    for row, latitude in enumerate(payload["latitude_values"]):
        for column, longitude in enumerate(payload["longitude_values"]):
            index = row * columns + column
            seasons = cell_seasons(payload, index)
            if not seasons:
                continue
            state = nearest_state(longitude, latitude)
            cell_counts[state] += 1
            for season_index, (u, v, _) in enumerate(seasons):
                seasonal_vectors[state][season_index].append((u, v))
    signatures = {}
    for state, seasons in seasonal_vectors.items():
        units = []
        means = []
        for samples in seasons:
            mean_u = sum(item[0] for item in samples) / len(samples)
            mean_v = sum(item[1] for item in samples) / len(samples)
            speed = math.hypot(mean_u, mean_v)
            means.append((mean_u, mean_v, speed))
            units.append((mean_u / speed, mean_v / speed) if speed > 1e-12 else None)
        if any(unit is None for unit in units):
            continue
        alignment = math.hypot(
            sum(unit[0] for unit in units) / len(units),
            sum(unit[1] for unit in units) / len(units),
        )
        maximum_turn = 0.0
        for left in range(len(units)):
            for right in range(left + 1, len(units)):
                dot = units[left][0] * units[right][0] + units[left][1] * units[right][1]
                maximum_turn = max(maximum_turn, math.degrees(math.acos(max(-1.0, min(1.0, dot)))))
        signatures[state] = {
            "seasonal_mean_vectors": means,
            "cross_season_alignment": alignment,
            "maximum_seasonal_turn_degrees": maximum_turn,
        }
    return signatures, dict(cell_counts)


def signature_similarity(left: dict, right: dict) -> float:
    values = []
    for left_vector, right_vector in zip(left["seasonal_mean_vectors"], right["seasonal_mean_vectors"]):
        left_u, left_v, left_speed = left_vector
        right_u, right_v, right_speed = right_vector
        values.append((left_u * right_u + left_v * right_v) / (left_speed * right_speed))
    return sum(values) / len(values)


def sampled_state_adjacencies(payload: dict) -> dict[tuple[str, str], dict]:
    """Aggregate seasonal direction similarity across sampled state interfaces."""
    rows, columns = payload["shape"]
    cell_states = {}
    cell_vectors = {}
    for row, latitude in enumerate(payload["latitude_values"]):
        for column, longitude in enumerate(payload["longitude_values"]):
            index = row * columns + column
            seasons = cell_seasons(payload, index)
            if seasons:
                cell_states[index] = nearest_state(longitude, latitude)
                cell_vectors[index] = seasons
    samples = defaultdict(list)
    seasonal_samples = defaultdict(lambda: [[] for _ in payload["season_order"]])
    for row in range(rows):
        for column in range(columns):
            index = row * columns + column
            if index not in cell_vectors:
                continue
            neighbors = [row * columns + ((column + 1) % columns)]
            if row + 1 < rows:
                neighbors.append((row + 1) * columns + column)
            for neighbor in neighbors:
                if neighbor not in cell_vectors or cell_states[index] == cell_states[neighbor]:
                    continue
                pair = tuple(sorted((cell_states[index], cell_states[neighbor])))
                samples[pair].append(directional_similarity(cell_vectors[index], cell_vectors[neighbor]))
                for season_index in range(len(payload["season_order"])):
                    seasonal_samples[pair][season_index].append(directional_similarity(
                        [cell_vectors[index][season_index]], [cell_vectors[neighbor][season_index]],
                    ))
    result = {}
    for pair, values in samples.items():
        seasonal_means = {
            season: sum(seasonal_samples[pair][index]) / len(seasonal_samples[pair][index])
            for index, season in enumerate(payload["season_order"])
        }
        result[pair] = {
            "state_a": pair[0], "state_b": pair[1],
            "neighbor_pairs": len(values),
            "mean_direction_similarity": sum(values) / len(values),
            "minimum_direction_similarity": min(values),
            **{f"direction_similarity_{season}": value for season, value in seasonal_means.items()},
            "seasonal_similarity_range": max(seasonal_means.values()) - min(seasonal_means.values()),
        }
    return result


def audit(payload: dict, source_artifact_sha256: str) -> dict:
    names = state_directory()
    signatures, cell_counts = state_signatures(payload)
    adjacency = sampled_state_adjacencies(payload)
    regions = []
    state_rows = []
    for region_code, region_name, _, members, _ in CONTIGUOUS_REGIONS:
        supported = [code for code in members if code in signatures]
        pairs = []
        for left_index, left in enumerate(supported):
            for right in supported[left_index + 1:]:
                pairs.append({"state_a": left, "state_b": right, "direction_similarity": signature_similarity(signatures[left], signatures[right])})
        pairs.sort(key=lambda item: item["direction_similarity"])
        member_set = set(members)
        adjacent_pairs = [value for pair, value in adjacency.items() if set(pair) <= member_set]
        adjacent_pairs.sort(key=lambda item: item["mean_direction_similarity"])
        adjacent_weight = sum(item["neighbor_pairs"] for item in adjacent_pairs)
        regions.append({
            "region_code": region_code,
            "region": region_name,
            "member_states": list(members),
            "supported_states": supported,
            "supported_state_fraction": len(supported) / len(members),
            "state_pair_comparisons": len(pairs),
            "mean_between_state_direction_similarity": sum(item["direction_similarity"] for item in pairs) / len(pairs) if pairs else None,
            "minimum_between_state_direction_similarity": pairs[0]["direction_similarity"] if pairs else None,
            "minimum_similarity_pair": [pairs[0]["state_a"], pairs[0]["state_b"]] if pairs else None,
            "sampled_adjacent_state_pairs": len(adjacent_pairs),
            "sampled_adjacent_neighbor_pairs": adjacent_weight,
            "weighted_mean_adjacent_direction_similarity": (
                sum(item["mean_direction_similarity"] * item["neighbor_pairs"] for item in adjacent_pairs) / adjacent_weight
                if adjacent_weight else None
            ),
            "minimum_adjacent_direction_similarity": adjacent_pairs[0]["mean_direction_similarity"] if adjacent_pairs else None,
            "minimum_adjacent_similarity_pair": [adjacent_pairs[0]["state_a"], adjacent_pairs[0]["state_b"]] if adjacent_pairs else None,
        })
        for code in members:
            signature = signatures.get(code)
            state_rows.append({
                "region_code": region_code,
                "state_code": code,
                "state": names[code],
                "supported_cells": cell_counts.get(code, 0),
                "cross_season_alignment": signature["cross_season_alignment"] if signature else None,
                "maximum_seasonal_turn_degrees": signature["maximum_seasonal_turn_degrees"] if signature else None,
            })
    return {
        "schema": "oceanlines.osw.motion-region-membership-audit.v1",
        "status": "province-signature comparison; frozen zoning; no membership revision",
        "source_artifact_sha256": source_artifact_sha256,
        "source_data_sha256": payload["source_sha256"],
        "source_period_start": payload["period_start"],
        "source_period_stop": payload["period_stop"],
        "regions": regions,
        "states": state_rows,
        "sampled_state_adjacencies": sorted(adjacency.values(), key=lambda item: item["mean_direction_similarity"]),
        "summary": {
            "regions": len(regions),
            "states": len(state_rows),
            "states_with_supported_cells": sum(item["supported_cells"] > 0 for item in state_rows),
        },
        "boundary": "Province signatures are unweighted means of supported coarse display-grid cells. Sampled adjacency uses four-neighbor display-grid contacts and is not validated province geometry, boundary exchange, area-weighted transport, or a split instruction.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--region-csv-output", type=Path, required=True)
    parser.add_argument("--state-csv-output", type=Path, required=True)
    args = parser.parse_args()
    payload, digest = load_javascript(args.input)
    result = audit(payload, digest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    for rows, output in ((result["regions"], args.region_csv_output), (result["states"], args.state_csv_output)):
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8", newline="") as destination:
            writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    print(f"wrote {args.output} ({result['summary']['states_with_supported_cells']}/56 supported states)")


if __name__ == "__main__":
    main()

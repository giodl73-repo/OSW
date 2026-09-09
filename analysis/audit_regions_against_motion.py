"""Audit provisional OSW regions against seasonal surface-motion diagnostics.

The audit samples the coarse historical OSCAR pilot grid. It does not revise
regions. Boundary cut-through is defined as normal-flow fraction multiplied by
rescaled directional similarity across adjacent cells. The geometry remains
OSW's flat nearest-seed construction, not published Longhurst boundaries.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import pathlib
from collections import defaultdict

from build_province_cartogram import CONTIGUOUS_REGIONS, PROVINCE_SEEDS, REGION_CODES, STATE_REGIONS


REGION_CODE_BY_NAME = REGION_CODES


def load_javascript(path: pathlib.Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    return json.loads(text.split("=", 1)[1].strip().removesuffix(";")), hashlib.sha256(raw).hexdigest()


def nearest_state(longitude: float, latitude: float) -> str:
    best_code = ""
    best_distance = float("inf")
    for code, (seed_longitude, seed_latitude) in PROVINCE_SEEDS.items():
        longitude_distance = min(
            abs(longitude - seed_longitude),
            abs(longitude - (seed_longitude - 360)),
            abs(longitude - (seed_longitude + 360)),
        )
        distance = longitude_distance * longitude_distance + (latitude - seed_latitude) ** 2
        if distance < best_distance:
            best_code, best_distance = code, distance
    return best_code


def region_code(longitude: float, latitude: float) -> str:
    return REGION_CODE_BY_NAME[STATE_REGIONS[nearest_state(longitude, latitude)]]


def boundary_normal(left_state: str, right_state: str) -> tuple[float, float]:
    """Return the flat nearest-seed boundary normal from left seed to right seed."""
    left_longitude, left_latitude = PROVINCE_SEEDS[left_state]
    right_longitude, right_latitude = PROVINCE_SEEDS[right_state]
    longitude_delta = (right_longitude - left_longitude + 180.0) % 360.0 - 180.0
    latitude_delta = right_latitude - left_latitude
    length = math.hypot(longitude_delta, latitude_delta)
    if length <= 1e-12:
        raise ValueError(f"coincident province seeds: {left_state}, {right_state}")
    return longitude_delta / length, latitude_delta / length


def cell_seasons(payload: dict, index: int) -> list[tuple[float, float, float]] | None:
    result = []
    for season in payload["season_order"]:
        data = payload["seasons"][season]
        u_value, v_value = data["mean_u_mm_s"][index], data["mean_v_mm_s"][index]
        if u_value is None or v_value is None:
            return None
        u, v = u_value / 1000, v_value / 1000
        speed = math.hypot(u, v)
        if speed <= 1e-12:
            return None
        result.append((u, v, speed))
    return result


def pair_diagnostics(
    left: list[tuple[float, float, float]],
    right: list[tuple[float, float, float]],
    normal: str | tuple[float, float],
) -> tuple[float, float, float]:
    crossings = []
    similarities = []
    contrasts = []
    for (left_u, left_v, left_speed), (right_u, right_v, right_speed) in zip(left, right):
        mean_u, mean_v = (left_u + right_u) / 2, (left_v + right_v) / 2
        mean_speed = math.hypot(mean_u, mean_v)
        if isinstance(normal, str):
            normal_vector = (1.0, 0.0) if normal == "east-west" else (0.0, 1.0)
        else:
            normal_vector = normal
        component = mean_u * normal_vector[0] + mean_v * normal_vector[1]
        crossings.append(0.0 if mean_speed <= 1e-12 else min(1.0, abs(component) / mean_speed))
        similarities.append(max(-1.0, min(1.0, (left_u * right_u + left_v * right_v) / (left_speed * right_speed))))
        contrasts.append(abs(left_speed - right_speed) / max(1e-12, (left_speed + right_speed) / 2))
    return (
        sum(crossings) / len(crossings),
        sum(similarities) / len(similarities),
        sum(contrasts) / len(contrasts),
    )


def seasonal_pair_diagnostics(
    left: list[tuple[float, float, float]],
    right: list[tuple[float, float, float]],
    normal: tuple[float, float],
) -> list[tuple[float, float, float]]:
    """Return crossing, directional similarity, and speed contrast per season."""
    return [pair_diagnostics([left_item], [right_item], normal) for left_item, right_item in zip(left, right)]


def pair_orientation_diagnostics(
    left: list[tuple[float, float, float]],
    right: list[tuple[float, float, float]],
    normal: tuple[float, float],
) -> tuple[float, float, float, float]:
    """Return normal, tangential, direction-similarity, and speed-contrast means."""
    tangent = (-normal[1], normal[0])
    normal_values = pair_diagnostics(left, right, normal)
    tangent_values = pair_diagnostics(left, right, tangent)
    return normal_values[0], tangent_values[0], normal_values[1], normal_values[2]


def cell_structure(seasons: list[tuple[float, float, float]]) -> tuple[float, float]:
    units = [(u / speed, v / speed) for u, v, speed in seasons]
    alignment = math.hypot(
        sum(item[0] for item in units) / len(units),
        sum(item[1] for item in units) / len(units),
    )
    maximum_turn = 0.0
    for left in range(len(units)):
        for right in range(left + 1, len(units)):
            dot = units[left][0] * units[right][0] + units[left][1] * units[right][1]
            maximum_turn = max(maximum_turn, math.degrees(math.acos(max(-1.0, min(1.0, dot)))))
    return alignment, maximum_turn


def audit(payload: dict, source_artifact_sha256: str, audited_at: str) -> dict:
    rows, columns = payload["shape"]
    latitudes, longitudes = payload["latitude_values"], payload["longitude_values"]
    cell_vectors: dict[int, list[tuple[float, float, float]]] = {}
    cell_states: dict[int, str] = {}
    cell_regions: dict[int, str] = {}
    region_cells: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row, latitude in enumerate(latitudes):
        for column, longitude in enumerate(longitudes):
            index = row * columns + column
            seasons = cell_seasons(payload, index)
            if seasons is None:
                continue
            state = nearest_state(longitude, latitude)
            code = REGION_CODE_BY_NAME[STATE_REGIONS[state]]
            cell_vectors[index] = seasons
            cell_states[index] = state
            cell_regions[index] = code
            region_cells[code].append(cell_structure(seasons))

    boundary_samples: dict[tuple[str, str], list[tuple[float, float, float, float]]] = defaultdict(list)
    boundary_season_samples: dict[tuple[str, str], list[list[tuple[float, float, float, float]]]] = defaultdict(
        lambda: [[] for _ in payload["season_order"]]
    )
    internal_samples: dict[str, list[float]] = defaultdict(list)

    def consider(left_index: int, right_index: int) -> None:
        if left_index not in cell_vectors or right_index not in cell_vectors:
            return
        left_region, right_region = cell_regions[left_index], cell_regions[right_index]
        normal = (
            boundary_normal(cell_states[left_index], cell_states[right_index])
            if cell_states[left_index] != cell_states[right_index]
            else (1.0, 0.0)
        )
        crossing, tangency, similarity, contrast = pair_orientation_diagnostics(
            cell_vectors[left_index], cell_vectors[right_index], normal,
        )
        if left_region == right_region:
            internal_samples[left_region].append(similarity)
        else:
            pair = tuple(sorted((left_region, right_region)))
            boundary_samples[pair].append(
                (crossing, tangency, similarity, contrast)
            )
            for season_index in range(len(payload["season_order"])):
                diagnostic = pair_orientation_diagnostics(
                    [cell_vectors[left_index][season_index]],
                    [cell_vectors[right_index][season_index]], normal,
                )
                boundary_season_samples[pair][season_index].append(diagnostic)

    for row in range(rows):
        for column in range(columns):
            index = row * columns + column
            consider(index, row * columns + ((column + 1) % columns))
            if row + 1 < rows:
                consider(index, (row + 1) * columns + column)

    boundaries = []
    for (region_a, region_b), samples in boundary_samples.items():
        crossing = sum(item[0] for item in samples) / len(samples)
        tangency = sum(item[1] for item in samples) / len(samples)
        similarity = sum(item[2] for item in samples) / len(samples)
        contrast = sum(item[3] for item in samples) / len(samples)
        cut_through = crossing * (similarity + 1) / 2
        along_border = tangency * (similarity + 1) / 2
        orientation_margin = cut_through - along_border
        orientation_class = "crossed" if orientation_margin >= .10 else "followed" if orientation_margin <= -.10 else "oblique_or_mixed"
        neighbor_scores = [item[0] * (item[2] + 1) / 2 for item in samples]
        score_mean = sum(neighbor_scores) / len(neighbor_scores)
        score_sd = math.sqrt(
            sum((value - score_mean) ** 2 for value in neighbor_scores) / (len(neighbor_scores) - 1)
        ) if len(neighbor_scores) > 1 else None
        seasonal_scores = {}
        for season, season_samples in zip(payload["season_order"], boundary_season_samples[(region_a, region_b)]):
            season_crossing = sum(item[0] for item in season_samples) / len(season_samples)
            season_similarity = sum(item[2] for item in season_samples) / len(season_samples)
            seasonal_scores[season] = season_crossing * (season_similarity + 1) / 2
        seasonal_values = list(seasonal_scores.values())
        boundaries.append({
            "region_a": region_a,
            "region_b": region_b,
            "neighbor_pairs": len(samples),
            "seasonal_pair_samples": len(samples) * len(payload["season_order"]),
            "mean_normal_flow_fraction": crossing,
            "mean_tangential_flow_fraction": tangency,
            "mean_direction_similarity": similarity,
            "mean_relative_speed_contrast": contrast,
            "cut_through_score": cut_through,
            "along_border_score": along_border,
            "orientation_margin": orientation_margin,
            "orientation_class": orientation_class,
            "neighbor_score_mean": score_mean,
            "neighbor_score_standard_deviation": score_sd,
            "support_class": "screened" if len(samples) >= 8 else "provisional" if len(samples) >= 3 else "sparse",
            **{f"cut_through_{season}": seasonal_scores[season] for season in payload["season_order"]},
            "seasonal_cut_through_floor": min(seasonal_values),
            "seasonal_cut_through_ceiling": max(seasonal_values),
            "seasonal_cut_through_range": max(seasonal_values) - min(seasonal_values),
        })
    boundaries.sort(key=lambda item: item["cut_through_score"], reverse=True)

    regions = []
    region_names = {code: name for code, name, _, _, _ in CONTIGUOUS_REGIONS}
    for code, name in region_names.items():
        structures = region_cells.get(code, [])
        similarities = internal_samples.get(code, [])
        regions.append({
            "region_code": code,
            "region": name,
            "supported_cells": len(structures),
            "internal_neighbor_pairs": len(similarities),
            "mean_cross_season_alignment": (
                sum(item[0] for item in structures) / len(structures) if structures else None
            ),
            "mean_maximum_seasonal_turn_degrees": (
                sum(item[1] for item in structures) / len(structures) if structures else None
            ),
            "mean_internal_direction_similarity": (
                sum(similarities) / len(similarities) if similarities else None
            ),
            "low_similarity_internal_fraction": (
                sum(value < 0.5 for value in similarities) / len(similarities) if similarities else None
            ),
        })
    regions.sort(key=lambda item: (
        item["mean_internal_direction_similarity"] is None,
        item["mean_internal_direction_similarity"] if item["mean_internal_direction_similarity"] is not None else 2,
    ))
    return {
        "schema": "oceanlines.osw.motion-boundary-audit.v3",
        "status": "diagnostic audit; frozen zoning; no boundary revision",
        "region_system": "osw-regions-v0.1",
        "source_artifact_sha256": source_artifact_sha256,
        "source_data_sha256": payload["source_sha256"],
        "source_period_start": payload["period_start"],
        "source_period_stop": payload["period_stop"],
        "audited_at": audited_at,
        "definitions": {
            "normal_flow_fraction": "absolute component of the mean neighboring seasonal vector along the flat nearest-seed border normal, divided by vector magnitude",
            "direction_similarity": "cosine similarity between seasonal mean vectors in neighboring cells; -1 opposed, 1 aligned",
            "cut_through_score": "mean normal-flow fraction multiplied by (mean direction similarity + 1) / 2",
            "along_border_score": "mean tangential-flow fraction multiplied by (mean direction similarity + 1) / 2",
            "orientation_margin": "cut-through score minus along-border score; positive favors crossing, negative favors following",
            "orientation_class": "crossed at margin >= 0.10; followed at margin <= -0.10; otherwise oblique_or_mixed; thresholds are declared screening bins, not natural kinds",
            "support_class": "sparse: 1–2 neighboring cell pairs; provisional: 3–7; screened: 8 or more; classes describe sample support, not statistical independence or confidence",
            "seasonal_cut_through": "the same cut-through calculation applied separately to DJF, MAM, JJA, and SON; floor and ceiling are descriptive extrema, not uncertainty intervals",
        },
        "boundary_pairs": boundaries,
        "regions": regions,
        "summary": {
            "supported_cells": len(cell_vectors),
            "supported_boundary_pairs": len(boundaries),
            "regions_with_supported_cells": sum(bool(region_cells.get(code)) for code in region_names),
        },
        "boundary": (
            "The audit uses coarse one-year historical surface velocity and flat nearest-seed border normals. "
            "Scores are screening diagnostics, not evidence that a boundary must merge, split, or move."
        ),
    }


def write_json(payload: dict, output: pathlib.Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def write_csv(rows: list[dict], output: pathlib.Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, required=True)
    parser.add_argument("--audited-at")
    parser.add_argument("--json-output", type=pathlib.Path, required=True)
    parser.add_argument("--boundary-csv-output", type=pathlib.Path, required=True)
    parser.add_argument("--region-csv-output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    source, digest = load_javascript(args.input)
    audited_at = args.audited_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    payload = audit(source, digest, audited_at)
    write_json(payload, args.json_output)
    write_csv(payload["boundary_pairs"], args.boundary_csv_output)
    write_csv(payload["regions"], args.region_csv_output)
    print(f"wrote {args.json_output} ({len(payload['boundary_pairs'])} boundary pairs)")


if __name__ == "__main__":
    main()

"""Bake off connectivity and overlap thresholds for the OSW-D3 lineage."""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "atlas" / "data" / "noaa-crw-mhw-point-north-atlantic-2026.json"
DEFAULT_LINEAGE = ROOT / "research" / "osw-d3-noaa-crw-mhw-lineage-2026.json"
DEFAULT_GAP = ROOT / "research" / "osw-d4-noaa-crw-mhw-gap-identity-2026.json"
DEFAULT_OUTPUT = ROOT / "research" / "osw-d5-noaa-crw-mhw-tracking-sensitivity-2026.json"
ANCHOR_DATE = "2026-07-23"
PRE_GAP_DATE = "2026-08-10"
POST_GAP_DATE = "2026-08-12"


def load_module(filename, name):
    path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TRACK = load_module("track_noaa_crw_mhw_footprint.py", "osw_tracker_sensitivity")


POLICIES = [
    {"policy_id": "any_exact_overlap", "metric": "intersection_pixels", "minimum": 1},
    {"policy_id": "iou_0_10", "metric": "iou", "minimum": 0.10},
    {"policy_id": "iou_0_20", "metric": "iou", "minimum": 0.20},
    {"policy_id": "iou_0_25", "metric": "iou", "minimum": 0.25},
    {"policy_id": "iou_0_50", "metric": "iou", "minimum": 0.50},
]


def connected_component(active, start, connectivity=4, periodic_longitude=True):
    """Return the native-grid component using edge or edge-plus-corner adjacency."""
    if connectivity not in {4, 8}:
        raise ValueError("connectivity must be 4 or 8")
    height, width = active.shape
    if not active[start]:
        return set()
    offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if connectivity == 8:
        offsets += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    found = {start}
    queue = deque([start])
    while queue:
        y, x = queue.popleft()
        for dy, dx in offsets:
            yy = y + dy
            xx = (x + dx) % width if periodic_longitude else x + dx
            if 0 <= yy < height and 0 <= xx < width and active[yy, xx] and (yy, xx) not in found:
                found.add((yy, xx))
                queue.append((yy, xx))
    return found


def overlapping_components(active, previous, connectivity):
    candidates = []
    consumed = set()
    for seed in sorted(cell for cell in previous if active[cell]):
        if seed in consumed:
            continue
        component = connected_component(active, seed, connectivity)
        consumed.update(component)
        intersection = len(component & previous)
        candidates.append({
            "component": component,
            "intersection_pixels": intersection,
            "iou": intersection / len(component | previous),
            "previous_retained_fraction": intersection / len(previous),
            "current_inherited_fraction": intersection / len(component),
        })
    return sorted(candidates, key=lambda item: (-item["intersection_pixels"], -item["iou"], min(item["component"])))


def track_unconstrained(paths, dates, anchor, connectivity):
    """Track the greatest-intersection branch while at least one exact cell overlaps."""
    _, _, categories, active = TRACK.read_field(paths[ANCHOR_DATE])
    seed = connected_component(active, anchor, connectivity)
    if not seed:
        raise ValueError("anchor is inactive on the seed date")
    tracked = {ANCHOR_DATE: seed}
    transitions = {}
    start_index = dates.index(ANCHOR_DATE)

    previous = seed
    for date in dates[start_index + 1:]:
        _, _, _, active = TRACK.read_field(paths[date])
        candidates = overlapping_components(active, previous, connectivity)
        if not candidates:
            break
        selected = candidates[0]
        current = selected.pop("component")
        prior_date = dates[dates.index(date) - 1]
        transitions[(prior_date, date)] = selected
        tracked[date] = current
        previous = current

    following = seed
    for date in reversed(dates[:start_index]):
        _, _, _, active = TRACK.read_field(paths[date])
        candidates = overlapping_components(active, following, connectivity)
        if not candidates:
            break
        selected = candidates[0]
        current = selected.pop("component")
        next_date = dates[dates.index(date) + 1]
        # Fractions were calculated in reverse. Re-express them in chronological order.
        intersection = selected["intersection_pixels"]
        selected = {
            "intersection_pixels": intersection,
            "iou": selected["iou"],
            "previous_retained_fraction": intersection / len(current),
            "current_inherited_fraction": intersection / len(following),
        }
        transitions[(date, next_date)] = selected
        tracked[date] = current
        following = current

    return tracked, transitions


def passes(transition, policy):
    return transition[policy["metric"]] >= policy["minimum"]


def component_sha256(component):
    encoded = ";".join(f"{y},{x}" for y, x in sorted(component)).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def anchored_window(dates, tracked, transitions, policy):
    """Find the policy-valid contiguous tracked interval containing ANCHOR_DATE."""
    anchor_index = dates.index(ANCHOR_DATE)
    start = end = anchor_index
    while start > 0 and dates[start - 1] in tracked:
        edge = transitions[(dates[start - 1], dates[start])]
        if not passes(edge, policy):
            break
        start -= 1
    while end + 1 < len(dates) and dates[end + 1] in tracked:
        edge = transitions[(dates[end], dates[end + 1])]
        if not passes(edge, policy):
            break
        end += 1
    window_dates = dates[start:end + 1]
    used = [transitions[(first, second)] for first, second in zip(window_dates, window_dates[1:])]
    before_edge = (dates[start - 1], dates[start]) if start > 0 and dates[start - 1] in tracked else None
    after_edge = (dates[end], dates[end + 1]) if end + 1 < len(dates) and dates[end + 1] in tracked else None

    def break_receipt(edge):
        if edge is None:
            return None
        metrics = transitions[edge]
        return {
            "from": edge[0],
            "to": edge[1],
            "intersection_pixels": metrics["intersection_pixels"],
            "iou": round(metrics["iou"], 4),
            "tested_metric": policy["metric"],
            "tested_value": round(metrics[policy["metric"]], 4),
            "required_minimum": policy["minimum"],
        }

    return {
        "start": window_dates[0],
        "end": window_dates[-1],
        "day_count": len(window_dates),
        "minimum_intersection_pixels": min((item["intersection_pixels"] for item in used), default=None),
        "minimum_iou": round(min((item["iou"] for item in used), default=1.0), 4),
        "break_before": break_receipt(before_edge),
        "break_after": break_receipt(after_edge),
    }


def gap_metrics(paths, anchor, connectivity):
    _, _, _, pre_active = TRACK.read_field(paths[PRE_GAP_DATE])
    _, _, _, post_active = TRACK.read_field(paths[POST_GAP_DATE])
    before = connected_component(pre_active, anchor, connectivity)
    after = connected_component(post_active, anchor, connectivity)
    intersection = len(before & after)
    return {
        "pre_gap_pixels": len(before),
        "post_gap_pixels": len(after),
        "intersection_pixels": intersection,
        "iou": round(intersection / len(before | after), 4),
        "pre_gap_retained_fraction": round(intersection / len(before), 4),
        "post_gap_inherited_fraction": round(intersection / len(after), 4),
        "pre_gap_component_sha256": component_sha256(before),
        "post_gap_component_sha256": component_sha256(after),
    }


def build(source_path=DEFAULT_SOURCE, lineage_path=DEFAULT_LINEAGE, gap_path=DEFAULT_GAP, output_path=DEFAULT_OUTPUT):
    source_path, lineage_path, gap_path, output_path = map(Path, (source_path, lineage_path, gap_path, output_path))
    source = json.loads(source_path.read_text(encoding="utf-8"))
    dates = [item["date"] for item in source["files"]]
    results = []
    tracked_by_connectivity = {}
    with tempfile.TemporaryDirectory(prefix="osw-crw-sensitivity-") as temporary:
        paths = TRACK.download_and_verify(source["files"], Path(temporary))
        latitudes, longitudes, _, _ = TRACK.read_field(paths[ANCHOR_DATE])
        anchor = (
            int(abs(latitudes - source["coordinate"]["latitude_degrees_north"]).argmin()),
            int(abs(longitudes - source["coordinate"]["longitude_degrees_east"]).argmin()),
        )
        for connectivity in (4, 8):
            tracked, transitions = track_unconstrained(paths, dates, anchor, connectivity)
            tracked_by_connectivity[connectivity] = tracked
            results.append({
                "connectivity": connectivity,
                "adjacency": "edge" if connectivity == 4 else "edge_or_corner",
                "unconstrained_greatest_intersection_window": {
                    "start": min(tracked, key=dates.index),
                    "end": max(tracked, key=dates.index),
                    "day_count": len(tracked),
                },
                "tracked_component_sha256_by_date": {
                    date_value: component_sha256(tracked[date_value])
                    for date_value in sorted(tracked, key=dates.index)
                },
                "threshold_windows": [dict(policy, **anchored_window(dates, tracked, transitions, policy)) for policy in POLICIES],
                "gap_bridge": gap_metrics(paths, anchor, connectivity),
            })

    baseline = next(item for item in results if item["connectivity"] == 4)["threshold_windows"][0]
    prior_lineage = json.loads(lineage_path.read_text(encoding="utf-8"))["tracked_window"]
    if {key: baseline[key] for key in ("start", "end", "day_count")} != {key: prior_lineage[key] for key in ("start", "end", "day_count")}:
        raise ValueError("four-neighbor any-overlap sensitivity does not reproduce OSW-D3")
    prior_gap = json.loads(gap_path.read_text(encoding="utf-8"))["bridge_metrics"]
    four_gap = next(item for item in results if item["connectivity"] == 4)["gap_bridge"]
    if any(four_gap[key] != prior_gap[key] for key in ("intersection_pixels", "iou", "pre_gap_retained_fraction", "post_gap_inherited_fraction")):
        raise ValueError("four-neighbor gap sensitivity does not reproduce OSW-D4")
    four_hashes = results[0]["tracked_component_sha256_by_date"]
    eight_hashes = results[1]["tracked_component_sha256_by_date"]
    common_dates = [date_value for date_value in dates if date_value in tracked_by_connectivity[4] and date_value in tracked_by_connectivity[8]]
    differences = []
    for date_value in common_dates:
        four_component = tracked_by_connectivity[4][date_value]
        eight_component = tracked_by_connectivity[8][date_value]
        if four_component != eight_component:
            intersection = len(four_component & eight_component)
            differences.append({
                "date": date_value,
                "four_neighbor_pixels": len(four_component),
                "eight_neighbor_pixels": len(eight_component),
                "intersection_pixels": intersection,
                "iou": round(intersection / len(four_component | eight_component), 4),
                "symmetric_difference_pixels": len(four_component ^ eight_component),
            })
    comparison = {
        "tracked_dates_equal": list(four_hashes) == list(eight_hashes),
        "daily_components_equal": four_hashes == eight_hashes,
        "tracked_day_count": len(common_dates),
        "equal_daily_component_count": len(common_dates) - len(differences),
        "differing_daily_component_count": len(differences),
        "daily_component_differences": differences,
        "pre_gap_components_equal": results[0]["gap_bridge"]["pre_gap_component_sha256"] == results[1]["gap_bridge"]["pre_gap_component_sha256"],
        "post_gap_components_equal": results[0]["gap_bridge"]["post_gap_component_sha256"] == results[1]["gap_bridge"]["post_gap_component_sha256"],
    }

    payload = {
        "schema": "osw.ocean-object-tracking-sensitivity.v1",
        "detection_id": "OSW-D5",
        "status": "tracking_policy_bakeoff",
        "object_id": "OBJ046",
        "object_name": "marine heatwave",
        "source_artifacts": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in (source_path, lineage_path, gap_path)
        ],
        "controlled_choices": {
            "seed": f"component containing the OSW-D1 anchor on {ANCHOR_DATE}",
            "branch_selection": "greatest exact native-pixel intersection; held fixed before applying acceptance thresholds",
            "connectivity_values": [4, 8],
            "threshold_policies": POLICIES,
            "threshold_selection": "illustrative diagnostic sweep, not a literature-calibrated or uniquely preferred set",
            "longitude_periodicity": True,
        },
        "results": results,
        "cross_connectivity_comparison": comparison,
        "identity_evaluation": {
            "result": "policy_dependent",
            "finding": "The lineage lifetime is evaluated under ten declared connectivity-by-overlap policies; agreement identifies robust days and divergence identifies convention-sensitive edges.",
        },
        "boundary": "This sensitivity concerns the identity of connected threshold-state footprints, not material water parcels. Eight-neighbor adjacency can join corner-touching cells, and stricter overlap can truncate a lineage even when some exact cells persist. The experiment holds greatest-intersection branch selection fixed and does not test forcing, advection, subsurface continuity, impacts, or a uniquely correct tracking policy.",
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--lineage", type=Path, default=DEFAULT_LINEAGE)
    parser.add_argument("--gap", type=Path, default=DEFAULT_GAP)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build(args.source, args.lineage, args.gap, args.output)
    print(f'wrote {args.output}: {sum(len(item["threshold_windows"]) for item in payload["results"])} policy outcomes')


if __name__ == "__main__":
    main()

"""Build a multi-branch marine-heatwave lineage family around the OSW-D1 anchor."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "atlas" / "data" / "noaa-crw-mhw-point-north-atlantic-2026.json"
DEFAULT_PRIMARY = ROOT / "research" / "osw-d3-noaa-crw-mhw-lineage-2026.json"
DEFAULT_OUTPUT = ROOT / "research" / "osw-d7-noaa-crw-mhw-lineage-family-2026.json"
ANCHOR_DATE = "2026-07-23"


def load_module(filename, name):
    path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TRACK = load_module("track_noaa_crw_mhw_footprint.py", "osw_tracker_lineage_family")


def component_sha256(component):
    encoded = ";".join(f"{y},{x}" for y, x in sorted(component)).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def decode_runs(rows, latitudes, longitudes):
    lat_index = {round(float(value), 3): index for index, value in enumerate(latitudes)}
    lon_index = {round(float(value), 3): index for index, value in enumerate(longitudes)}
    component = set()
    for latitude, runs in rows:
        y = lat_index[round(latitude, 3)]
        for west, east, _category in runs:
            start = lon_index[round(west, 3)]
            stop = lon_index[round(east, 3)]
            component.update((y, x) for x in range(start, stop + 1))
    return component


def discover_candidates(active, seed_side_components):
    """Return every distinct active component touching any seed-side component."""
    candidates = {}
    for seed_side in seed_side_components:
        for candidate in TRACK.overlapping_components(active, seed_side):
            component = candidate["component"]
            candidates.setdefault(component_sha256(component), component)
    return sorted(candidates.values(), key=lambda component: (-len(component), min(component)))


def chronological_edge(before, after):
    intersection = len(before & after)
    return {
        "intersection_pixels": intersection,
        "iou": round(intersection / len(before | after), 4),
        "source_retained_fraction": round(intersection / len(before), 4),
        "target_inherited_fraction": round(intersection / len(after), 4),
    }


def extend_family(components_by_date, summaries_by_key, edges, paths, dates, start_index, latitudes, longitudes, direction):
    if direction == "forward":
        sequence = dates[start_index + 1:]
        seed_side_date = lambda value: dates[dates.index(value) - 1]
    else:
        sequence = reversed(dates[:start_index])
        seed_side_date = lambda value: dates[dates.index(value) + 1]
    stop = None
    for date_value in sequence:
        adjacent_date = seed_side_date(date_value)
        _, _, categories, active = TRACK.read_field(paths[date_value])
        candidates = discover_candidates(active, components_by_date[adjacent_date])
        if not candidates:
            stop = {"date": date_value, "reason": "no exact-overlap component is reachable from the adjacent family nodes"}
            break
        components_by_date[date_value] = candidates
        for component in candidates:
            digest = component_sha256(component)
            summaries_by_key[(date_value, digest)] = TRACK.FOOTPRINT.summarize(component, categories, latitudes, longitudes)
        if direction == "forward":
            before_date, after_date = adjacent_date, date_value
        else:
            before_date, after_date = date_value, adjacent_date
        for before in components_by_date[before_date]:
            for after in components_by_date[after_date]:
                if before & after:
                    edges.append({
                        "from_date": before_date,
                        "from_hash": component_sha256(before),
                        "to_date": after_date,
                        "to_hash": component_sha256(after),
                        **chronological_edge(before, after),
                    })
    return stop


def build(source_path=DEFAULT_SOURCE, primary_path=DEFAULT_PRIMARY, output_path=DEFAULT_OUTPUT):
    source_path, primary_path, output_path = map(Path, (source_path, primary_path, output_path))
    source = json.loads(source_path.read_text(encoding="utf-8"))
    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    dates = [item["date"] for item in source["files"]]
    with tempfile.TemporaryDirectory(prefix="osw-crw-family-") as temporary:
        paths = TRACK.download_and_verify(source["files"], Path(temporary))
        latitudes, longitudes, categories, active = TRACK.read_field(paths[ANCHOR_DATE])
        anchor = (
            int(abs(latitudes - source["coordinate"]["latitude_degrees_north"]).argmin()),
            int(abs(longitudes - source["coordinate"]["longitude_degrees_east"]).argmin()),
        )
        seed = TRACK.FOOTPRINT.connected_component(active, anchor)
        seed_hash = component_sha256(seed)
        components_by_date = {ANCHOR_DATE: [seed]}
        summaries_by_key = {(ANCHOR_DATE, seed_hash): TRACK.FOOTPRINT.summarize(seed, categories, latitudes, longitudes)}
        edges = []
        start_index = dates.index(ANCHOR_DATE)
        forward_stop = extend_family(
            components_by_date, summaries_by_key, edges, paths, dates, start_index,
            latitudes, longitudes, "forward",
        )
        backward_stop = extend_family(
            components_by_date, summaries_by_key, edges, paths, dates, start_index,
            latitudes, longitudes, "backward",
        )

    primary_hash_by_date = {
        item["date"]: component_sha256(decode_runs(item["component_rows"], latitudes, longitudes))
        for item in primary["daily_footprints"]
    }
    ordered_dates = [date_value for date_value in dates if date_value in components_by_date]
    node_id_by_key = {}
    nodes = []
    for date_value in ordered_dates:
        components = sorted(components_by_date[date_value], key=lambda component: (-len(component), min(component)))
        for index, component in enumerate(components, 1):
            digest = component_sha256(component)
            node_id = f'{date_value}-C{index:02d}'
            node_id_by_key[(date_value, digest)] = node_id
            nodes.append({
                "node_id": node_id,
                "date": date_value,
                "component_rank_by_size": index,
                "component_sha256": digest,
                "on_d3_primary_branch": primary_hash_by_date.get(date_value) == digest,
                "summary": summaries_by_key[(date_value, digest)],
            })
    edge_records = []
    for edge in sorted(edges, key=lambda item: (dates.index(item["from_date"]), item["from_hash"], item["to_hash"])):
        edge_records.append({
            "from": node_id_by_key[(edge.pop("from_date"), edge.pop("from_hash"))],
            "to": node_id_by_key[(edge.pop("to_date"), edge.pop("to_hash"))],
            **edge,
        })

    indegree = {node["node_id"]: 0 for node in nodes}
    outdegree = {node["node_id"]: 0 for node in nodes}
    for edge in edge_records:
        outdegree[edge["from"]] += 1
        indegree[edge["to"]] += 1
    split_nodes = [node_id for node_id, degree in outdegree.items() if degree > 1]
    merge_nodes = [node_id for node_id, degree in indegree.items() if degree > 1]
    primary_nodes = [node for node in nodes if node["on_d3_primary_branch"]]
    if len(primary_nodes) != primary["tracked_window"]["day_count"]:
        raise ValueError("family graph does not contain every D3 primary component")
    off_primary = [node for node in nodes if not node["on_d3_primary_branch"]]
    off_primary_terminal = [node for node in off_primary if outdegree[node["node_id"]] == 0]
    off_primary_merge_back = [
        node for node in off_primary
        if any(edge["from"] == node["node_id"] and next(item for item in nodes if item["node_id"] == edge["to"])["on_d3_primary_branch"] for edge in edge_records)
    ]
    payload = {
        "schema": "osw.ocean-object-lineage-family.v1",
        "detection_id": "OSW-D7",
        "status": "exact_overlap_lineage_family",
        "object_id": "OBJ046",
        "object_name": "marine heatwave",
        "source_artifacts": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in (source_path, primary_path)
        ],
        "method": {
            "seed": f"four-neighbor component containing the OSW-D1 anchor on {ANCHOR_DATE}",
            "family_expansion": "retain every distinct four-neighbor component on the adjacent day that shares at least one exact native-grid cell with any current family node",
            "edge": "directed chronological exact-overlap relation with two-sided overlap metrics",
            "longitude_periodicity": True,
            "pruning": "none beyond reachability from the seed and exact adjacent-day overlap",
        },
        "tracked_window": {
            "start": ordered_dates[0], "end": ordered_dates[-1], "day_count": len(ordered_dates),
            "preceding_stop": backward_stop, "following_stop": forward_stop,
        },
        "summary": {
            "node_count": len(nodes),
            "edge_count": len(edge_records),
            "primary_branch_node_count": len(primary_nodes),
            "off_primary_node_count": len(off_primary),
            "maximum_components_on_one_day": max(len(components_by_date[date_value]) for date_value in ordered_dates),
            "split_node_count": len(split_nodes),
            "merge_node_count": len(merge_nodes),
            "off_primary_terminal_node_count": len(off_primary_terminal),
            "off_primary_merge_back_node_count": len(off_primary_merge_back),
            "largest_off_primary_component_pixels": max((node["summary"]["pixel_count"] for node in off_primary), default=0),
        },
        "components_per_day": [
            {"date": date_value, "component_count": len(components_by_date[date_value])}
            for date_value in ordered_dates
        ],
        "split_nodes": split_nodes,
        "merge_nodes": merge_nodes,
        "nodes": nodes,
        "edges": edge_records,
        "identity_evaluation": {
            "result": "pass",
            "finding": "Every adjacent-day branch reachable from the anchor under the declared exact-overlap rule is retained as a lineage family; D3 remains one explicit primary path through it.",
        },
        "boundary": "This graph is a genealogy of connected threshold-state footprints, not a materially conserved body of water. Graph membership depends on four-neighbor connectivity, daily cadence, exact-overlap reachability, source window, and no size pruning. Tiny branches remain visible by design. The graph does not bridge the August 11 threshold gap or establish forcing, advection, subsurface extent, impacts, or a unique event ontology.",
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--primary", type=Path, default=DEFAULT_PRIMARY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build(args.source, args.primary, args.output)
    print(f'wrote {args.output}: {payload["summary"]["node_count"]} nodes, {payload["summary"]["edge_count"]} edges')


if __name__ == "__main__":
    main()

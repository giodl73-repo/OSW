"""Build a state-first join with explicit evidence levels.

Current crossings use only existing OSW *schematic* feature centerlines. Other
names get locator-in-state candidates. Individual eddies need dated footprints
or tracks, which the Horizon name register does not supply.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union


ROOT = Path(__file__).resolve().parents[1]
PROVINCES = ROOT / "figures" / "osw-province-atlas-interactive.svg"
FEATURES = ROOT / "figures" / "osw-atlas-feature-shapes.svg"
INDEX = ROOT / "research" / "ocean-current-atlas-index.json"
OBJECTS = ROOT / "research" / "nasa-perpetual-ocean-objects.json"
EDITORIAL_PATHS = ROOT / "research" / "nasa-motion-editorial-paths.json"
NAMED_EDITORIAL_PATHS = ROOT / "research" / "ocean-current-editorial-paths.json"
OUTPUT = ROOT / "research" / "ocean-motion-state-join.json"
NUMBER = re.compile(r"-?\d+(?:\.\d+)?")
TOKEN = re.compile(r"[MLCZ]|-?\d+(?:\.\d+)?")
FEATURE_CURRENT_IDS = {
    "gulf-stream": "gulf-stream",
    "kuroshio": "kuroshio",
    "agulhas": "agulhas",
    "antarctic-circumpolar-current": "acc",
    "indonesian-throughflow": None,
}


def polygon_parts(path: str) -> list[Polygon]:
    """Province and Natural Earth land paths contain only M, L, and Z."""
    parts = []
    for subpath in re.findall(r"M[^M]+", path):
        points = [(float(x), float(y)) for x, y in re.findall(r"(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)", subpath)]
        if len(points) >= 3:
            shape = Polygon(points)
            if not shape.is_valid:
                shape = shape.buffer(0)
            if not shape.is_empty:
                parts.append(shape)
    return parts


def centerline(path: str) -> LineString:
    """Sample M/L/C commands in the existing schematic centerlines."""
    tokens = TOKEN.findall(path)
    points: list[tuple[float, float]] = []
    i = 0
    current = (0.0, 0.0)
    while i < len(tokens):
        command = tokens[i]
        i += 1
        if command in ("M", "L"):
            current = (float(tokens[i]), float(tokens[i + 1]))
            points.append(current)
            i += 2
        elif command == "C":
            p0 = current
            p1 = (float(tokens[i]), float(tokens[i + 1]))
            p2 = (float(tokens[i + 2]), float(tokens[i + 3]))
            p3 = (float(tokens[i + 4]), float(tokens[i + 5]))
            i += 6
            for step in range(1, 21):
                t = step / 20
                u = 1 - t
                points.append((u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
                               u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]))
            current = p3
        else:
            raise ValueError(f"Unexpected path command {command}")
    return LineString(points)


def project(point: list[float]) -> Point:
    longitude, latitude = point
    return Point(60 + (longitude + 180) / 360 * 1480, 90 + (90 - latitude) / 180 * 740)


def main() -> None:
    province_root = ET.parse(PROVINCES).getroot()
    land_path = next(item.get("d") for item in province_root.iter() if item.get("class") == "land-context")
    land = unary_union(polygon_parts(land_path))
    states = {}
    for group in province_root.iter():
        if "province " not in group.get("class", ""):
            continue
        path = next(item.get("d") for item in group if item.tag.endswith("path"))
        states[group.get("data-code")] = {"name": group.get("data-name"), "shape": unary_union(polygon_parts(path)).difference(land)}
    if len(states) != 56:
        raise ValueError(f"Expected 56 states, found {len(states)}")
    features = {}
    for group in ET.parse(FEATURES).getroot().iter():
        feature_id = group.get("data-id")
        if feature_id not in FEATURE_CURRENT_IDS:
            continue
        path = next(item.get("d") for item in group if item.tag.endswith("path") and item.get("class") == "hit")
        features[feature_id] = centerline(path)
    if set(features) != set(FEATURE_CURRENT_IDS):
        raise ValueError("Missing an expected OSW schematic flow shape")
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    nasa = json.loads(OBJECTS.read_text(encoding="utf-8"))
    editorial = json.loads(EDITORIAL_PATHS.read_text(encoding="utf-8"))["paths"]
    editorial_lines = {current_id: LineString([project(point) for point in record["coordinates_lon_lat"]])
                       for current_id, record in editorial.items()}
    named_editorial = json.loads(NAMED_EDITORIAL_PATHS.read_text(encoding="utf-8"))["paths"]
    if not set(named_editorial) <= set(index["entries"]) or set(named_editorial) & set(editorial):
        raise ValueError("Named editorial paths must map to distinct indexed currents")
    named_lines = {current_id: LineString([project(point) for point in record["coordinates_lon_lat"]])
                   for current_id, record in named_editorial.items()}
    result = {}
    for code, state in states.items():
        shape = state["shape"]
        current_paths = sorted({current_id for feature_id, current_id in FEATURE_CURRENT_IDS.items()
                                if current_id and shape.intersects(features[feature_id])})
        editorial_paths = sorted(current_id for current_id, line in editorial_lines.items() if shape.intersects(line))
        named_editorial_paths = sorted(current_id for current_id, line in named_lines.items() if shape.intersects(line))
        current_locators = sorted({current_id for current_id, item in index["entries"].items()
                                   if code not in item.get("state_exclusions", [])
                                   and any(shape.covers(project(point)) for point in item["locators"])})
        nasa_paths = sorted(feature_id for feature_id, current_id in FEATURE_CURRENT_IDS.items()
                            if feature_id == "indonesian-throughflow" and shape.intersects(features[feature_id]))
        nasa_locators = sorted(item["id"] for item in nasa["objects"]
                               if item["locator"] and shape.covers(project(item["locator"])))
        result[code] = {
            "name": state["name"],
            "schematic_current_centerline_crossings": current_paths,
            "editorial_nasa_current_line_crossings": editorial_paths,
            "editorial_named_current_line_crossings": named_editorial_paths,
            "current_locator_candidates": current_locators,
            "schematic_nasa_object_crossings": nasa_paths,
            "nasa_object_locator_candidates": nasa_locators,
            "individual_named_eddy_containment": "unknown_no_dated_footprints",
            "individual_named_eddy_intersection": "unknown_no_dated_tracks_or_footprints",
        }
    payload = {
        "schema": "osw.almanac.motion-state-join.v1",
        "state_count": len(states),
        "state_geometry": str(PROVINCES.relative_to(ROOT)).replace("\\", "/"),
        "schematic_flow_geometry": str(FEATURES.relative_to(ROOT)).replace("\\", "/"),
        "current_index": str(INDEX.relative_to(ROOT)).replace("\\", "/"),
        "nasa_objects": str(OBJECTS.relative_to(ROOT)).replace("\\", "/"),
        "editorial_paths": str(EDITORIAL_PATHS.relative_to(ROOT)).replace("\\", "/"),
        "named_editorial_paths": str(NAMED_EDITORIAL_PATHS.relative_to(ROOT)).replace("\\", "/"),
        "rules": {
            "schematic_current_centerline_crossings": "OSW drawn line intersects the coast-masked approximate state polygon. This is an atlas shape relation, not a measured current core or observed passage.",
            "editorial_nasa_current_line_crossings": "A coarse OSW editorial path for a NASA-named current intersects the approximate state. The path is a visual index, not a digitized NASA model streamline.",
            "editorial_named_current_line_crossings": "A coarse OSW editorial route for an independently named downstream current intersects the approximate state. The line is neither an observed core nor a NASA-identified path, and cannot establish a physical crossing or length.",
            "current_locator_candidates": "An editorial point for a named current falls in the approximate state and has no explicit semantic state exclusion. A point alone does not establish that the current passes through the state.",
            "schematic_nasa_object_crossings": "OSW's Indonesian Throughflow gate line intersects the approximate state polygon.",
            "nasa_object_locator_candidates": "A regional point for an NASA-identified motion object falls in the state; no footprint or containment claim.",
            "individual_named_eddy_containment": "Requires dated closed footprint entirely within a state polygon; unavailable for the named Loop Current register.",
            "individual_named_eddy_intersection": "Requires dated track or footprint intersecting a state polygon; unavailable for the named Loop Current register."
        },
        "states": result,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(states)} states, {sum(len(s['schematic_current_centerline_crossings']) for s in result.values())} schematic current-state crossings")


if __name__ == "__main__":
    main()

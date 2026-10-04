"""Join a pinned, dated Gulf Stream surface-front analysis to OSW states."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from pyproj import Geod
from shapely.geometry import LineString
from shapely.ops import unary_union

from build_motion_state_join import polygon_parts, project


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "gulf-stream-navo-front-20260928.json"
STATES = ROOT / "figures" / "osw-province-atlas-interactive.svg"
OUTPUT = ROOT / "research" / "gulf-stream-navo-state-snapshot-20260928.json"
GEOD = Geod(ellps="WGS84")


def unproject(point: tuple[float, float]) -> tuple[float, float]:
    x, y = point
    return ((x - 60) / 1480 * 360 - 180, 90 - (y - 90) / 740 * 180)


def geographic_line_length_km(geometry) -> float:
    if geometry.is_empty:
        return 0.0
    if geometry.geom_type == "LineString":
        coords = [unproject(point) for point in geometry.coords]
        if len(coords) < 2:
            return 0.0
        longitudes, latitudes = zip(*coords)
        return abs(GEOD.line_length(longitudes, latitudes)) / 1000
    if hasattr(geometry, "geoms"):
        return sum(geographic_line_length_km(part) for part in geometry.geoms)
    return 0.0


def build() -> dict:
    receipt = json.loads(SOURCE.read_text(encoding="utf-8"))
    if receipt["date"] != "2026-09-28" or set(receipt["fronts"]) != {"north_wall", "south_wall"}:
        raise ValueError("Unexpected frontal receipt")
    root = ET.parse(STATES).getroot()
    land_path = next(item.get("d") for item in root.iter() if item.get("class") == "land-context")
    land = unary_union(polygon_parts(land_path))
    state_shapes = {}
    for group in root.iter():
        if "province " not in group.get("class", ""):
            continue
        path = next(item.get("d") for item in group if item.tag.endswith("path"))
        state_shapes[group.get("data-code")] = {
            "name": group.get("data-name"),
            "shape": unary_union(polygon_parts(path)).difference(land),
        }
    if len(state_shapes) != 56:
        raise ValueError(f"Expected 56 OSW states, found {len(state_shapes)}")
    lines = {
        key: LineString([project(coordinate) for coordinate in front["geometry"]["coordinates"]])
        for key, front in receipt["fronts"].items()
    }
    front_lengths_km = {key: round(geographic_line_length_km(line), 1)
                        for key, line in lines.items()}
    states = {}
    for code, state in sorted(state_shapes.items()):
        observations = {}
        observed_lengths_km = {}
        for key, line in lines.items():
            intersection = state["shape"].intersection(line)
            if intersection.is_empty:
                continue
            observations[key] = "line_segment_intersection" if intersection.length > 0 else "boundary_touch_only"
            observed_lengths_km[key] = round(geographic_line_length_km(intersection), 1)
        states[code] = {"name": state["name"], "front_observations": observations,
                        "front_intersection_lengths_km": observed_lengths_km}
    for side, total in front_lengths_km.items():
        allocated = sum(state["front_intersection_lengths_km"].get(side, 0)
                        for state in states.values())
        if abs(allocated - total) > 0.5:
            raise ValueError(f"OSW states do not partition the {side} front: {allocated} vs {total} km")
    return {
        "schema": "osw.almanac.navo-gulf-stream-front-state-snapshot.v1",
        "date": receipt["date"],
        "source_receipt": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_url": receipt["source_url"],
        "source_response_sha256": receipt["source_response_sha256"],
        "state_geometry": str(STATES.relative_to(ROOT)).replace("\\", "/"),
        "current_identity": "gulf-stream-system",
        "observation_role": "dated_surface_front_intersection",
        "method": "Project the NAVO north and south wall coordinate lines to OSW's equirectangular SVG frame and intersect each with coast-masked approximate state polygons. A positive-length overlap is a line-segment intersection; a point contact is a boundary touch. Convert clipped line vertices back to longitude and latitude, sum WGS84 geodesic segment lengths, and round to 0.1 km.",
        "length_limit": "Lengths measure the drawn analyzed fronts and approximate front segments inside OSW atlas polygons on this date. They are not along-current centerline lengths or whole-current estimates. Coordinate rounding, front age, and approximate state boundaries are not represented by the decimal precision.",
        "front_lengths_km": front_lengths_km,
        "claim_limit": "These are analyzed surface-temperature fronts for one date, not an observed current axis, a complete Gulf Stream System footprint, or a perennial current/state passage claim. State boundaries are OSW approximate regions. Absence of a front intersection on this date is not absence of the current.",
        "state_count": len(states),
        "states_with_front": sum(bool(state["front_observations"]) for state in states.values()),
        "states": states,
    }


def main() -> None:
    result = build()
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    matched = {code: state["front_observations"] for code, state in result["states"].items()
               if state["front_observations"]}
    print(f"Wrote {OUTPUT.relative_to(ROOT)}: {len(matched)} state front intersections")
    for code, fronts in matched.items():
        print(f"  {code}: {', '.join(fronts)}")


if __name__ == "__main__":
    main()

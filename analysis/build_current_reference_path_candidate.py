"""Measure and display an explicitly editorial current reference-route candidate.

No provider acquisition and no promotion into the published-length ranking.
"""
from __future__ import annotations

import hashlib
import argparse
import itertools
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

from pyproj import Geod
from shapely.geometry import LineString, box
from shapely.affinity import translate
from shapely.ops import unary_union

from build_cartographic_current_state_join import load_states, project
from build_motion_state_join import PROVINCES, polygon_parts

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "research" / "east-australian-reference-path-input.json"
TILES = ROOT / "almanac" / "release" / "v0.1.0" / "tiles.json"
GEOD = Geod(ellps="WGS84")


def length_km(coordinates: list[list[float]], *, allow_seam: bool = False) -> float:
    if len(coordinates) < 2:
        raise ValueError("A reference path needs at least two vertices")
    if any(not (math.isfinite(lon) and math.isfinite(lat) and -180 <= lon <= 180 and -90 <= lat <= 90) for lon, lat in coordinates):
        raise ValueError("Invalid longitude/latitude")
    if any(abs(a[0] - b[0]) == 180 for a, b in zip(coordinates, coordinates[1:])):
        raise ValueError("A 180-degree longitude leg needs intermediate waypoints")
    if not allow_seam and any(abs(a[0] - b[0]) > 180 for a, b in zip(coordinates, coordinates[1:])):
        raise ValueError("Explicit seam handling required")
    return sum(GEOD.inv(*a, *b)[2] for a, b in zip(coordinates, coordinates[1:])) / 1000


def display_coordinates(coordinates: list[list[float]], *, allow_seam: bool = False) -> list[tuple[float, float]]:
    """Densify the measured geodesic legs at no more than 10 km spacing."""
    length_km(coordinates, allow_seam=allow_seam)  # Validate before interpolating.
    points = [tuple(coordinates[0])]
    for a, b in zip(coordinates, coordinates[1:]):
        steps = max(1, math.ceil(GEOD.inv(*a, *b)[2] / 10000))
        if steps > 1:
            points.extend(GEOD.npts(*a, *b, steps - 1))
        points.append(tuple(b))
    if allow_seam:
        unwrapped = [points[0]]
        for lon, lat in points[1:]:
            previous = unwrapped[-1][0]
            lon += 360 * round((previous - lon) / 360)
            unwrapped.append((lon, lat))
        if max(lon for lon, _ in unwrapped) - min(lon for lon, _ in unwrapped) >= 360:
            raise ValueError("A route spanning a full revolution needs explicit circuit handling")
        points = unwrapped
    return [project(*point) for point in points]


def periodic_geometry(geometry):
    """Copies of an OSW display geometry on adjacent longitude periods."""
    return unary_union([translate(geometry, xoff=offset) for offset in [-1480, 0, 1480]])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT)
    args = parser.parse_args()
    input_path = args.input.resolve()
    source_name = input_path.name.removesuffix("-input.json")
    if not input_path.name.endswith("-input.json"):
        raise ValueError("Expected a named -input.json candidate file")
    output_path = ROOT / "research" / f"{source_name}-candidate.json"
    figure_path = ROOT / "figures" / f"{source_name}-candidate.svg"
    raw = input_path.read_bytes()
    source = json.loads(raw)
    x0, y0, width, height = source["map_view_box"]
    text_size = source.get("map_label_size", max(3, width * .015))
    legend_spacing = source.get("legend_line_spacing", max(5, text_size * 1.3))
    symbol_scale = source.get("map_symbol_scale", 1)
    if any(not math.isfinite(value) or value <= 0 for value in [text_size, legend_spacing, symbol_scale]):
        raise ValueError("Figure label size, legend spacing and symbol scale must be positive and finite")
    seam_policy = source.get('longitude_seam_policy')
    if seam_policy not in [None, 'shortest_geodesic_periodic_display']:
        raise ValueError('Unsupported longitude seam policy')
    allow_seam = seam_policy == 'shortest_geodesic_periodic_display'
    coordinates = source["coordinates_lon_lat"]
    nominal = length_km(coordinates, allow_seam=allow_seam)
    atlas = ET.parse(PROVINCES).getroot()
    land_d = next(row.get("d") for row in atlas.iter() if row.get("class") == "land-context")
    land = unary_union(polygon_parts(land_d))
    states = load_states()
    if allow_seam:
        land = periodic_geometry(land)
        states = {code: periodic_geometry(polygon) for code, polygon in states.items()}
    scenarios = []
    variants = [{"id": "nominal", "coordinates_lon_lat": coordinates}] + source.get("alternative_routes", [])
    if len({row['id'] for row in variants}) != len(variants):
        raise ValueError("Route variant IDs must be unique")
    if any(0 not in values for values in [source["longitude_offsets_degrees"], source["endpoint_latitude_offsets_degrees"], source.get("start_longitude_offsets_degrees", [0]), source.get("end_longitude_offsets_degrees", [0])]):
        raise ValueError("Scenario grid must include the nominal route")
    for variant, longitude_shift, start_shift, end_shift, start_lon_shift, end_lon_shift in itertools.product(variants, source["longitude_offsets_degrees"], source["endpoint_latitude_offsets_degrees"], source["endpoint_latitude_offsets_degrees"], source.get("start_longitude_offsets_degrees", [0]), source.get("end_longitude_offsets_degrees", [0])):
        path = [[lon + longitude_shift, lat] for lon, lat in variant["coordinates_lon_lat"]]
        path[0][1] += start_shift
        path[-1][1] += end_shift
        path[0][0] += start_lon_shift
        path[-1][0] += end_lon_shift
        if allow_seam:
            path = [[(lon + 180) % 360 - 180, lat] for lon, lat in path]
        display_line = LineString(display_coordinates(path, allow_seam=allow_seam))
        if display_line.intersection(land).length > 1e-8:
            raise ValueError("Editorial scenario crosses the coarse OSW atlas land mask")
        scenarios.append({
            "route_variant_id": variant["id"],
            "longitude_offset_degrees": longitude_shift,
            "start_latitude_offset_degrees": start_shift,
            "end_latitude_offset_degrees": end_shift,
            "start_longitude_offset_degrees": start_lon_shift,
            "end_longitude_offset_degrees": end_lon_shift,
            "coordinates_lon_lat": path,
            "length_km": round(length_km(path, allow_seam=allow_seam), 3),
            "atlas_state_crossings": sorted(code for code, polygon in states.items() if display_line.intersection(polygon).length > 1e-8),
        })
    smallest = min(row["length_km"] for row in scenarios)
    largest = max(row["length_km"] for row in scenarios)
    rounding = source["report_rounding_km"]
    if not math.isfinite(rounding) or rounding <= 0:
        raise ValueError("Report rounding must be positive and finite")
    nominal_display_line = LineString(display_coordinates(coordinates, allow_seam=allow_seam))
    tiles_raw = TILES.read_bytes()
    scenario_display_lines = [LineString(display_coordinates(row["coordinates_lon_lat"], allow_seam=allow_seam)) for row in scenarios]
    movie_context = []
    for tile in json.loads(tiles_raw):
        west, east = tile["longitude_range_unwrapped"]
        south, north = tile["latitude_range"]
        crop = box(*project(west, north), *project(east, south))
        fractions = []
        for line in scenario_display_lines:
            fractions.append(max(translate(line, xoff=offset).intersection(crop).length / line.length for offset in [-1480, 0, 1480]))
        nominal_fraction = max(translate(nominal_display_line, xoff=offset).intersection(crop).length / nominal_display_line.length for offset in [-1480, 0, 1480])
        if max(fractions) <= 1e-8:
            continue
        movie_context.append({
            "tile_id": tile["tile_id"], "url": tile["url"], "source_id": tile["source_id"], "zoom": tile["zoom"],
            "nominal_display_route_fraction": round(nominal_fraction, 6),
            "scenario_display_route_fraction_range": [round(min(fractions), 6), round(max(fractions), 6)],
            "complete_display_route_in_all_scenarios": min(fractions) >= 1 - 1e-8,
            "interpretation": "Editorial reference-route/crop display overlap only; not physical current identification or dated event matching. Fraction measures equirectangular display line, not physical kilometres.",
        })
    movie_context.sort(key=lambda row: (-row["zoom"], -row["nominal_display_route_fraction"], row["tile_id"]))
    complete_tiles = [row for row in movie_context if row["complete_display_route_in_all_scenarios"]]
    report = {
        **source,
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "generator_file": "analysis/build_current_reference_path_candidate.py",
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "method": "Sum shortest WGS84 geodesic distances between successive OSW editorial vertices; no velocity field or current core is reconstructed." + (" Explicit date-line policy: longitude-normalized scenario vertices, continuously unwrapped geodesic display, and periodic land/state/crop joins." if allow_seam else ""),
        "nominal_reference_path_km": round(nominal, 3),
        "reported_approximate_reference_path_km": round(nominal / rounding) * rounding,
        "scenario_range_km": [smallest, largest],
        "reported_scenario_range_km": [math.floor(smallest / rounding) * rounding, math.ceil(largest / rounding) * rounding],
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "map_land_check": f"All {len(scenarios)} routes, geodesically densified at spacing no greater than 10 km, avoid the coarse OSW atlas land mask in display coordinates. This is not a shelf-break, reef, bathymetric or high-resolution land-clearance verification.",
        "state_relation_role": "Editorial line/display-region crossing; physical current passage unresolved.",
        "atlas_map_sha256": hashlib.sha256(PROVINCES.read_bytes()).hexdigest(),
        "nominal_atlas_state_crossings": sorted(code for code, polygon in states.items() if nominal_display_line.intersection(polygon).length > 1e-8),
        "nasa_movie_context": movie_context,
        "nasa_tiles_sha256": hashlib.sha256(tiles_raw).hexdigest(),
        "recommended_nasa_tile_id": complete_tiles[0]["tile_id"] if complete_tiles else None,
        "nasa_crop_recommendation_rule": "Highest zoom crop covering the entire display route in every retained scenario, with tile ID as deterministic tie-break. No physical identification asserted.",
        "input_file": input_path.relative_to(ROOT).as_posix(),
        "figure": figure_path.relative_to(ROOT).as_posix(),
    }
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Use the OSW equirectangular atlas ground; retain a clearly schematic role.
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    svg = ET.Element("{http://www.w3.org/2000/svg}svg", {"viewBox": f"{x0} {y0} {width} {height}", "width": "800", "height": str(round(800 * height / width)), "role": "img", "aria-labelledby": "title description"})
    ET.SubElement(svg, "title", {"id": "title"}).text = f"{source['name']}: OSW editorial reference-route candidate"
    ET.SubElement(svg, "desc", {"id": "description"}).text = f"Equirectangular schematic. Approximately {report['reported_approximate_reference_path_km']} km. {source['scope']} Source describes regional geography; OSW selects the drawn route. No measured current axis."
    ET.SubElement(svg, "rect", {"x": str(x0), "y": str(y0), "width": str(width), "height": str(height), "fill": "#e7f2f7"})
    ET.SubElement(svg, "path", {"d": land_d, "fill": "#dedbd0", "stroke": "#7c888a", "stroke-width": ".25"})
    if allow_seam:
        for offset in [-1480, 1480]:
            ET.SubElement(svg, "path", {"d": land_d, "transform": f"translate({offset} 0)", "fill": "#dedbd0", "stroke": "#7c888a", "stroke-width": ".25"})
    for row in scenarios:
        points = " ".join(f"{x:.5f},{y:.5f}" for x, y in display_coordinates(row["coordinates_lon_lat"], allow_seam=allow_seam))
        ET.SubElement(svg, "polyline", {"points": points, "fill": "none", "stroke": "#789cae", "stroke-width": str(.35 * symbol_scale), "opacity": ".35"})
    displayed = display_coordinates(coordinates, allow_seam=allow_seam)
    points = " ".join(f"{x:.5f},{y:.5f}" for x, y in displayed)
    ET.SubElement(svg, "polyline", {"points": points, "fill": "none", "stroke": "#a14613", "stroke-width": str(.9 * symbol_scale), "stroke-dasharray": f"{2 * symbol_scale} {symbol_scale}"})
    for (x, y), label in zip([displayed[0], displayed[-1]], source["endpoint_labels"]):
        ET.SubElement(svg, "circle", {"cx": str(x), "cy": str(y), "r": str(1.3 * symbol_scale), "fill": "#a14613"})
        align_left = x + 3 + len(label) * text_size * .6 <= x0 + width - 2
        ET.SubElement(svg, "text", {"x": str(x + 3 if align_left else x - 3), "y": str(y), "text-anchor": "start" if align_left else "end", "font-size": str(text_size), "font-family": "sans-serif"}).text = label
    # Small islands may be absent from the coarse atlas ground. Reference points
    # provide orientation only; they never alter land clearance or route joins.
    landmarks = source.get("context_landmarks", [])
    for landmark in landmarks:
        lon, lat = landmark["coordinates_lon_lat"]
        if not (math.isfinite(lon) and math.isfinite(lat) and -180 <= lon <= 180 and -90 <= lat <= 90) or not landmark["label"].strip():
            raise ValueError("Invalid context landmark")
        x, y = project(lon, lat)
        if not x0 <= x <= x0 + width or not y0 <= y <= y0 + height:
            raise ValueError("Context landmark outside map")
        ET.SubElement(svg, "circle", {"cx": str(x), "cy": str(y), "r": str(.7 * symbol_scale), "fill": "#51616a"})
        ET.SubElement(svg, "text", {"x": str(x + text_size), "y": str(y + text_size), "font-size": str(text_size), "font-family": "sans-serif", "fill": "#394851"}).text = landmark["label"]
    if landmarks:
        ET.SubElement(svg, "text", {"x": str(x0 + 4), "y": str(y0 + height - 2), "font-size": str(text_size), "font-family": "sans-serif"}).text = "Dots: island-centre references; outlines unresolved"
    for i, label in enumerate([f"OSW approximate {source['route_extent_kind']} — candidate", f"≈ {report['reported_approximate_reference_path_km']:,} km · scenario range {report['reported_scenario_range_km'][0]:,}–{report['reported_scenario_range_km'][1]:,} km", f"Dashed: nominal route · pale: {len(scenarios)} editorial scenarios", "Not an observed axis or statistical confidence interval", f"Source: {source['figure_source_label']}; OSW selects vertices", "Equirectangular OSW atlas ground · scientific review pending"]):
        ET.SubElement(svg, "text", {"x": str(x0 + 4), "y": str(y0 + 8 + i * legend_spacing), "font-size": str(text_size), "font-family": "sans-serif"}).text = label
    if allow_seam:
        for seam_x in [60, 1540]:
            if x0 <= seam_x <= x0 + width:
                ET.SubElement(svg, "line", {"x1": str(seam_x), "x2": str(seam_x), "y1": str(y0 + 45), "y2": str(y0 + height - 8), "stroke": "#71838a", "stroke-width": ".3", "stroke-dasharray": "1 2"})
                ET.SubElement(svg, "text", {"x": str(seam_x + 2), "y": str(y0 + height - 4), "font-size": str(text_size), "font-family": "sans-serif"}).text = "180° date line"
    ET.ElementTree(svg).write(figure_path, encoding="utf-8", xml_declaration=True)
    print(f"Built editorial candidate: approximately {report['reported_approximate_reference_path_km']} km; {len(scenarios)} scenarios; range {report['reported_scenario_range_km']} km")


if __name__ == "__main__":
    main()

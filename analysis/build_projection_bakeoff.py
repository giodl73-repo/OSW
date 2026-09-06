"""Build ocean-first projection prototypes and local heatmass plates.

The output is explanatory cartography, not a gridded heat product. Natural
Earth supplies pinned coastline reference geometry. Fluid features are one
shared schematic longitude/latitude overlay projected identically in each
candidate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Iterator, Sequence

from pyproj import CRS, Transformer

from build_province_cartogram import REGION_CODES, REGION_COUNTS, REGION_MARKERS, REGION_TONES, PROVINCES, PROVINCE_SEEDS, clip_half_plane, realm_name, region_class_slug, region_name, region_slug


SOURCE_COMMIT = "ca96624a56bd078437bca8184e78163e5039ad19"
SOURCE_URL = f"https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{SOURCE_COMMIT}/geojson/ne_110m_land.geojson"
EXPECTED_SOURCE_SHA256 = "9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9"
WIDTH = 900
HEIGHT = 760
MAP_BOX = (42.0, 112.0, 816.0, 530.0)
STATE_CANVAS = (1200, 1360)
STATE_MAP_BOX = (56.0, 360.0, 1088.0, 706.0)
NORTH_POLAR_BOX = (660.0, 150.0, 156.0, 156.0)
SOUTH_POLAR_BOX = (902.0, 150.0, 156.0, 156.0)
NORTH_POLAR_CUTOFF = 48.0
SOUTH_POLAR_CUTOFF = -45.0
Point = tuple[float, float]
Projector = Callable[[float, float], Point]


@dataclass(frozen=True)
class Candidate:
    slug: str
    title: str
    subtitle: str
    property_label: str
    tradeoff: str
    projector: Projector
    frame: str


@dataclass(frozen=True)
class StateCandidate:
    slug: str
    title: str
    subtitle: str
    property_label: str
    tradeoff: str
    proj4: str


HEAT_POLYGONS: list[list[Point]] = [
    [(96, -3), (103, 5), (114, 9), (126, 7), (136, 11), (149, 8), (159, 3), (172, 1), (180, -3), (180, -14), (167, -16), (154, -12), (142, -15), (129, -10), (116, -12), (105, -8), (96, -3)],
    [(-180, -3), (-169, -4), (-158, -8), (-145, -12), (-151, -18), (-163, -18), (-175, -14), (-180, -14), (-180, -3)],
    [(-115, 5), (-108, 12), (-98, 15), (-88, 13), (-82, 18), (-72, 20), (-63, 16), (-56, 10), (-61, 4), (-72, 2), (-82, 6), (-91, 3), (-103, 6), (-115, 5)],
]
HEAT_SHELVES: list[list[Point]] = [
    [(105, -2), (115, 4), (126, 3), (137, 7), (149, 4), (160, -1), (173, -3)],
    [(-177, -7), (-166, -8), (-155, -12), (-149, -14)],
    [(-108, 8), (-98, 11), (-89, 9), (-80, 14), (-70, 15), (-62, 10)],
]
EL_NINO_POLYGON: list[Point] = [(172, 5), (190, 6), (215, 4), (240, 2), (267, -1), (280, -4), (274, -10), (248, -8), (220, -6), (194, -4), (172, -1), (172, 5)]
ARCTIC_WATER_POLYGON: list[Point] = [(-24, 55), (-8, 63), (10, 71), (39, 77), (74, 82), (113, 79), (126, 72), (97, 69), (60, 72), (28, 68), (4, 59), (-24, 55)]


def transformer(proj4: str) -> Transformer:
    spherical_geographic = CRS.from_proj4("+proj=longlat +R=1 +no_defs")
    return Transformer.from_crs(spherical_geographic, CRS.from_proj4(proj4), always_xy=True)


def spilhaus_projector() -> Projector:
    """Published Spilhaus oblique rotation followed by Adams Square II.

    The constants match the Spilhaus implementation added to PROJ 9.8. The
    installed Adams operator performs the final conformal square mapping.
    """

    adams = transformer("+proj=adams_ws2 +R=1 +units=m +no_defs")
    phi0 = math.radians(-49.56371678)
    azimuth = math.radians(40.17823482)
    rotation = math.radians(45.0)
    sin_alpha = -math.cos(phi0) * math.cos(azimuth)
    cos_alpha = math.sqrt(1.0 - sin_alpha * sin_alpha)
    lambda0 = math.atan2(math.tan(azimuth), -math.sin(phi0))
    beta = math.pi + math.atan2(-math.sin(azimuth), -math.tan(phi0))
    cos_rotation = math.cos(rotation)
    sin_rotation = math.sin(rotation)

    def project(longitude: float, latitude: float) -> Point:
        lam = math.radians(longitude)
        phi = math.radians(latitude)
        cos_phi = math.cos(phi)
        sin_phi = math.sin(phi)
        cos_lam = math.cos(lam - lambda0)
        sin_lam = math.sin(lam - lambda0)
        adams_phi = math.asin(max(-1.0, min(1.0, sin_alpha * sin_phi - cos_alpha * cos_phi * cos_lam)))
        adams_lam = beta + math.atan2(
            cos_phi * sin_lam,
            sin_alpha * cos_phi * cos_lam + cos_alpha * sin_phi,
        )
        adams_lam = (adams_lam + math.pi) % (2.0 * math.pi) - math.pi
        x_adams, y_adams = adams.transform(math.degrees(adams_lam), math.degrees(adams_phi))
        return (
            -(x_adams * cos_rotation + y_adams * sin_rotation),
            -(x_adams * -sin_rotation + y_adams * cos_rotation),
        )

    return project


def pyproj_projector(proj4: str) -> Projector:
    operation = transformer(proj4)

    def project(longitude: float, latitude: float) -> Point:
        return operation.transform(longitude, latitude)

    return project


def candidates() -> list[Candidate]:
    return [
        Candidate(
            "spilhaus",
            "SPILHAUS",
            "The continuity benchmark",
            "CONFORMAL · OCEAN UNBROKEN",
            "Local shape wins; apparent heatmass area does not.",
            spilhaus_projector(),
            "square",
        ),
        Candidate(
            "oceanic-goode",
            "OCEANIC GOODE",
            "The area benchmark",
            "EQUAL-AREA · INTERRUPTED",
            "Area compares honestly; ocean pathways meet lobe cuts.",
            pyproj_projector("+proj=igh_o +lon_0=-160 +R=1 +units=m +no_defs"),
            "wide",
        ),
        Candidate(
            "equal-earth",
            "EQUAL EARTH",
            "The flat-world benchmark",
            "EQUAL-AREA · FLAT",
            "Heatmass areas read clearly; the Africa seam still splits polar water.",
            pyproj_projector("+proj=eqearth +lon_0=-165 +R=1 +units=m +no_defs"),
            "wide",
        ),
        Candidate(
            "pelagos",
            "PELAGOS",
            "The OSW experiment",
            "EQUAL-AREA · SAHARA EDGE",
            "Ocean continuity leads; shape distortion grows toward Africa.",
            pyproj_projector("+proj=laea +lat_0=-20 +lon_0=-165 +R=1 +units=m +no_defs"),
            "circle",
        ),
    ]


def geometry_rings(geometry: dict) -> Iterator[list[Point]]:
    if geometry["type"] == "Polygon":
        polygons = [geometry["coordinates"]]
    elif geometry["type"] == "MultiPolygon":
        polygons = geometry["coordinates"]
    else:
        return
    for polygon in polygons:
        for ring in polygon:
            yield [(float(longitude), float(latitude)) for longitude, latitude in ring]


def all_rings(geojson: dict) -> Iterator[list[Point]]:
    for feature in geojson["features"]:
        yield from geometry_rings(feature["geometry"])


def densify(points: Sequence[Point], step: float = 2.0, close: bool = False) -> list[Point]:
    if len(points) < 2:
        return list(points)
    source = list(points)
    if close and source[0] != source[-1]:
        source.append(source[0])
    output: list[Point] = []
    for index, (start_lon, start_lat) in enumerate(source[:-1]):
        end_lon, end_lat = source[index + 1]
        delta_lon = (end_lon - start_lon + 180.0) % 360.0 - 180.0
        delta_lat = end_lat - start_lat
        count = max(1, math.ceil(max(abs(delta_lon), abs(delta_lat)) / step))
        for sample in range(count):
            fraction = sample / count
            output.append((start_lon + delta_lon * fraction, start_lat + delta_lat * fraction))
    output.append(source[-1])
    return output


def raw_bounds(project: Projector) -> tuple[float, float, float, float]:
    coordinates: list[Point] = []
    for latitude in range(-89, 90, 2):
        for longitude in range(-180, 181, 2):
            try:
                x, y = project(longitude, latitude)
            except (ValueError, OverflowError):
                continue
            if math.isfinite(x) and math.isfinite(y):
                coordinates.append((x, y))
    xs = [point[0] for point in coordinates]
    ys = [point[1] for point in coordinates]
    return min(xs), min(ys), max(xs), max(ys)


def screen_transform(
    bounds: tuple[float, float, float, float],
    box: tuple[float, float, float, float] = MAP_BOX,
) -> Callable[[Point], Point]:
    minimum_x, minimum_y, maximum_x, maximum_y = bounds
    box_x, box_y, box_width, box_height = box
    span_x = maximum_x - minimum_x
    span_y = maximum_y - minimum_y
    scale = min(box_width / span_x, box_height / span_y) * 0.95
    offset_x = box_x + (box_width - span_x * scale) / 2.0 - minimum_x * scale
    offset_y = box_y + (box_height - span_y * scale) / 2.0 + maximum_y * scale

    def transform(point: Point) -> Point:
        return offset_x + point[0] * scale, offset_y - point[1] * scale

    return transform


def local_bounds(project: Projector, extent: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    west, south, east, north = extent
    coordinates: list[Point] = []
    for row in range(31):
        latitude = south + (north - south) * row / 30
        for column in range(61):
            longitude = west + (east - west) * column / 60
            point = project(longitude, latitude)
            if math.isfinite(point[0]) and math.isfinite(point[1]):
                coordinates.append(point)
    xs = [point[0] for point in coordinates]
    ys = [point[1] for point in coordinates]
    return min(xs), min(ys), max(xs), max(ys)


def projected_segments(
    points: Sequence[Point],
    project: Projector,
    bounds: tuple[float, float, float, float],
    close: bool = False,
) -> list[list[Point]]:
    dense = densify(points, close=close)
    span = max(bounds[2] - bounds[0], bounds[3] - bounds[1])
    jump_limit = span * 0.16
    segments: list[list[Point]] = []
    segment: list[Point] = []
    previous: Point | None = None
    for longitude, latitude in dense:
        try:
            point = project(longitude, max(-89.999, min(89.999, latitude)))
        except (ValueError, OverflowError):
            point = (math.nan, math.nan)
        valid = math.isfinite(point[0]) and math.isfinite(point[1])
        jumped = previous is not None and valid and math.dist(previous, point) > jump_limit
        if not valid or jumped:
            if len(segment) >= 2:
                segments.append(segment)
            segment = []
        if valid:
            segment.append(point)
            previous = point
        else:
            previous = None
    if len(segment) >= 2:
        segments.append(segment)
    return segments


def svg_path(segments: Iterable[Sequence[Point]], screen: Callable[[Point], Point], close: bool = False) -> str:
    commands: list[str] = []
    for segment in segments:
        if len(segment) < 2:
            continue
        first_x, first_y = screen(segment[0])
        commands.append(f"M{first_x:.1f},{first_y:.1f}")
        for point in segment[1:]:
            x, y = screen(point)
            commands.append(f"L{x:.1f},{y:.1f}")
        if close and math.dist(segment[0], segment[-1]) < 1e-6:
            commands.append("Z")
    return "".join(commands)


def filled_svg_path(segments: Iterable[Sequence[Point]], screen: Callable[[Point], Point]) -> str:
    """Close every visible projected fragment against its projection seam."""
    commands: list[str] = []
    for segment in segments:
        if len(segment) < 3:
            continue
        first_x, first_y = screen(segment[0])
        commands.append(f"M{first_x:.1f},{first_y:.1f}")
        for point in segment[1:]:
            x, y = screen(point)
            commands.append(f"L{x:.1f},{y:.1f}")
        commands.append("Z")
    return "".join(commands)


def state_projection_candidates() -> list[StateCandidate]:
    return [
        StateCandidate(
            "mollweide-oceanic",
            "OCEANIC MOLLWEIDE",
            "Six ocean-emphasis lobes",
            "EQUAL-AREA · INTERRUPTED",
            "More room for ocean states; continuity pays at the lobe cuts.",
            "+proj=imoll_o +lon_0=-160 +R=1 +units=m +no_defs",
        ),
        StateCandidate(
            "oblique-cea",
            "OBLIQUE OCEAN STRIP",
            "Drake Passage to Indonesian Throughflow axis",
            "EQUAL-AREA · GREAT-CIRCLE AXIS",
            "A long connected ocean corridor; polar and off-axis shape is strongly transformed.",
            "+proj=ocea +lat_1=-56 +lon_1=-68 +lat_2=-3 +lon_2=123 +R=1 +units=m +no_defs",
        ),
    ]


def geographic_state_geometry() -> tuple[list[dict], list[tuple[Point, Point]], list[tuple[Point, Point]]]:
    """Create periodic nearest-seed cells directly in longitude/latitude space."""
    seeds = []
    for basin, provinces in PROVINCES.items():
        for code, name, biome in provinces:
            longitude, latitude = PROVINCE_SEEDS[code]
            seeds.append((code, name, biome, basin, longitude, latitude))

    states: list[dict] = []
    edge_owners: dict[tuple[Point, Point], list[tuple[str, str, str]]] = {}
    for code, name, biome, basin, seed_lon, seed_lat in seeds:
        pieces: list[list[Point]] = []
        for target_lon in (seed_lon - 360.0, seed_lon, seed_lon + 360.0):
            polygon: list[Point] = [(-180.0, -89.5), (180.0, -89.5), (180.0, 89.5), (-180.0, 89.5)]
            for other_code, _, _, _, other_lon, other_lat in seeds:
                for competitor_lon in (other_lon - 360.0, other_lon, other_lon + 360.0):
                    if other_code == code and abs(competitor_lon - target_lon) < 0.01:
                        continue
                    normal_x = competitor_lon - target_lon
                    normal_y = other_lat - seed_lat
                    limit = ((competitor_lon * competitor_lon + other_lat * other_lat)
                             - (target_lon * target_lon + seed_lat * seed_lat)) / 2.0
                    polygon = clip_half_plane(polygon, normal_x, normal_y, limit)
                    if not polygon:
                        break
                if not polygon:
                    break
            if len(polygon) < 3:
                continue
            pieces.append(polygon)
            rounded = [(round(x, 5), round(y, 5)) for x, y in polygon]
            for start, end in zip(rounded, rounded[1:] + rounded[:1]):
                if start == end:
                    continue
                key = (start, end) if start < end else (end, start)
                edge_owners.setdefault(key, []).append((code, basin, biome))
        states.append({
            "code": code, "name": name, "biome": biome, "basin": basin,
            "seed": (seed_lon, seed_lat), "pieces": pieces,
        })

    realm_edges: list[tuple[Point, Point]] = []
    region_edges: list[tuple[Point, Point]] = []
    adjacency: dict[str, set[str]] = {state["code"]: set() for state in states}
    for edge, owners in edge_owners.items():
        unique = set(owners)
        owner_codes = {code for code, _, _ in unique}
        if len(owner_codes) < 2:
            continue
        for code in owner_codes:
            adjacency[code].update(owner_codes - {code})
        realms = {realm_name(basin, biome) for _, basin, biome in unique}
        regions = {region_name(code) for code, _, _ in unique}
        if len(realms) > 1:
            realm_edges.append(edge)
        elif len(regions) > 1:
            region_edges.append(edge)

    for region in REGION_TONES:
        members = {state["code"] for state in states if region_name(state["code"]) == region}
        reached = set()
        stack = [next(iter(members))]
        while stack:
            current = stack.pop()
            if current in reached:
                continue
            reached.add(current)
            stack.extend((adjacency[current] & members) - reached)
        if reached != members:
            raise ValueError(f"Mapped region is multipart: {region}: {sorted(members - reached)}")
    return states, realm_edges, region_edges


def clip_geographic_polygon(
    polygon: Sequence[Point], west: float, east: float, south: float, north: float,
) -> list[Point]:
    """Sutherland–Hodgman clip used to cut fills at projection zone seams."""
    points = list(polygon)
    if points and points[0] == points[-1]:
        points.pop()

    def clip_edge(source, inside, intersection):
        if not source:
            return []
        output = []
        previous = source[-1]
        previous_inside = inside(previous)
        for current in source:
            current_inside = inside(current)
            if current_inside:
                if not previous_inside:
                    output.append(intersection(previous, current))
                output.append(current)
            elif previous_inside:
                output.append(intersection(previous, current))
            previous, previous_inside = current, current_inside
        return output

    def vertical(boundary):
        def intersect(start, end):
            fraction = (boundary - start[0]) / (end[0] - start[0]) if end[0] != start[0] else 0
            return boundary, start[1] + fraction * (end[1] - start[1])
        return intersect

    def horizontal(boundary):
        def intersect(start, end):
            fraction = (boundary - start[1]) / (end[1] - start[1]) if end[1] != start[1] else 0
            return start[0] + fraction * (end[0] - start[0]), boundary
        return intersect

    points = clip_edge(points, lambda point: point[0] >= west, vertical(west))
    points = clip_edge(points, lambda point: point[0] <= east, vertical(east))
    points = clip_edge(points, lambda point: point[1] >= south, horizontal(south))
    return clip_edge(points, lambda point: point[1] <= north, horizontal(north))


def oceanic_mollweide_pieces(polygon: Sequence[Point], central_longitude: float = -160.0) -> list[list[Point]]:
    """Clip a geographic polygon into the six PROJ imoll_o zones."""
    relative: list[Point] = []
    previous_longitude: float | None = None
    for longitude, latitude in polygon:
        value = (longitude - central_longitude + 180.0) % 360.0 - 180.0
        if previous_longitude is not None:
            while value - previous_longitude > 180.0:
                value -= 360.0
            while value - previous_longitude < -180.0:
                value += 360.0
        relative.append((value, latitude))
        previous_longitude = value

    zones = [
        (-180.0, -90.0, 0.0, 89.5), (-90.0, 60.0, 0.0, 89.5), (60.0, 180.0, 0.0, 89.5),
        (-180.0, -60.0, -89.5, 0.0), (-60.0, 90.0, -89.5, 0.0), (90.0, 180.0, -89.5, 0.0),
    ]
    pieces: list[list[Point]] = []
    for shift in (-360.0, 0.0, 360.0):
        shifted = [(longitude + shift, latitude) for longitude, latitude in relative]
        for west, east, south, north in zones:
            clipped = clip_geographic_polygon(shifted, west, east, south, north)
            if len(clipped) >= 3:
                # PROJ assigns exact seam coordinates to one neighboring zone.
                # Nudge clipped vertices into their intended zone so a fill
                # cannot jump horizontally to a different Mollweide lobe.
                epsilon = 1e-5
                interior = []
                for longitude, latitude in clipped:
                    if abs(longitude - west) < epsilon:
                        longitude += epsilon
                    if abs(longitude - east) < epsilon:
                        longitude -= epsilon
                    if north == 0.0 and abs(latitude) < epsilon:
                        latitude = -epsilon
                    interior.append((longitude + central_longitude, latitude))
                pieces.append(interior)
    return pieces


def projected_polygon_fill(
    polygon: Sequence[Point],
    candidate: StateCandidate,
    project: Projector,
    bounds: tuple[float, float, float, float],
    screen: Callable[[Point], Point],
) -> str:
    geographic_pieces = oceanic_mollweide_pieces(polygon) if candidate.slug == "mollweide-oceanic" else [list(polygon)]
    commands = []
    for piece in geographic_pieces:
        if candidate.slug == "mollweide-oceanic":
            projected = []
            for longitude, latitude in densify(piece, step=1.0, close=True):
                point = project(longitude, max(-89.499, min(89.499, latitude)))
                if math.isfinite(point[0]) and math.isfinite(point[1]):
                    projected.append(point)
            segments = [projected]
        else:
            segments = projected_segments(piece, project, bounds, close=True)
        commands.append(filled_svg_path(segments, screen))
    return "".join(commands)


def projected_edge_path(
    edges: Sequence[tuple[Point, Point]],
    candidate: StateCandidate,
    project: Projector,
    bounds: tuple[float, float, float, float],
    screen: Callable[[Point], Point],
) -> str:
    if candidate.slug != "mollweide-oceanic":
        return "".join(line_path([start, end], project, bounds, screen) for start, end in edges)

    commands = []
    for start, end in edges:
        segments: list[list[Point]] = []
        segment: list[Point] = []
        previous_zone = None
        for longitude, latitude in densify([start, end], step=0.5):
            relative = (longitude + 160.0 + 180.0) % 360.0 - 180.0
            if latitude >= 0:
                zone = 1 if relative <= -90 else 3 if relative >= 60 else 2
            else:
                zone = 4 if relative <= -60 else 6 if relative >= 90 else 5
            if previous_zone is not None and zone != previous_zone:
                if len(segment) >= 2:
                    segments.append(segment)
                segment = []
            point = project(longitude, latitude)
            if math.isfinite(point[0]) and math.isfinite(point[1]):
                segment.append(point)
            previous_zone = zone
        if len(segment) >= 2:
            segments.append(segment)
        commands.append(svg_path(segments, screen))
    return "".join(commands)


def render_state_projection(
    candidate: StateCandidate,
    geojson: dict,
    source_sha256: str,
    show_hairlines: bool = True,
) -> str:
    project = pyproj_projector(candidate.proj4)
    bounds = raw_bounds(project)
    state_map_box = STATE_MAP_BOX
    map_x, map_y, map_width, map_height = state_map_box
    screen = screen_transform(bounds, box=state_map_box)
    states, realm_edges, region_edges = geographic_state_geometry()

    province_groups = []
    province_labels = []
    for state in states:
        paths = []
        for polygon in state["pieces"]:
            paths.append(projected_polygon_fill(polygon, candidate, project, bounds, screen))
        province_groups.append(
            f'<g class="province {state["biome"].lower()} basin-{state["basin"].lower()} region-{region_slug(state["code"])}" '
            f'data-code="{state["code"]}" data-basin="{state["basin"]}" data-biome="{state["biome"]}" data-realm="{realm_name(state["basin"], state["biome"])}" data-region="{region_name(state["code"])}">'
            f'<title>{state["code"]} — {state["name"]} · {region_name(state["code"])} · approximate nearest-seed state</title>'
            f'<path d="{"".join(paths)}"/></g>'
        )
        label_point = project(*state["seed"])
        if math.isfinite(label_point[0]) and math.isfinite(label_point[1]):
            label_x, label_y = screen(label_point)
            province_labels.append(f'<text x="{label_x:.1f}" y="{label_y + 2.5:.1f}">{state["code"]}</text>')

    land_paths = []
    for ring in all_rings(geojson):
        land_paths.append(projected_polygon_fill(ring, candidate, project, bounds, screen))
    land = "".join(land_paths)
    realm_path = projected_edge_path(realm_edges, candidate, project, bounds, screen)
    region_path = projected_edge_path(region_edges, candidate, project, bounds, screen)

    map_region_labels = []
    for label, name, code in REGION_MARKERS:
        longitude, latitude = PROVINCE_SEEDS[code]
        point = project(longitude, latitude)
        if math.isfinite(point[0]) and math.isfinite(point[1]):
            x, y = screen(point)
            map_region_labels.append(
                f'<text x="{x:.1f}" y="{y - 6:.1f}" aria-label="{name}"><title>{name}</title>{label}</text>'
            )

    hairline_rule = "stroke:#71878a; stroke-width:.25; stroke-opacity:.55;" if show_hairlines else "stroke-width:1; stroke-opacity:1;"
    region_strokes = {
        name: f" stroke:{tone};" if not show_hairlines else ""
        for name, tone in REGION_TONES.items()
    }
    hairline_label = "STATE HAIRLINES ON" if show_hairlines else "STATE HAIRLINES OFF"
    fill_rules = "\n".join(
        f'.province.region-{region_class_slug(name)} path {{ fill:{tone};{region_strokes[name]} }}'
        for name, tone in REGION_TONES.items()
    )
    legend_items = []
    for index, (name, tone) in enumerate(REGION_TONES.items()):
        row, column = divmod(index, 4)
        x, y = column * 272, row * 24
        legend_items.append(
            f'<g aria-label="{REGION_CODES[name]} — {name}, {REGION_COUNTS[name]} states">'
            f'<rect x="{x}" y="{y}" width="14" height="14" rx="2" fill="{tone}"/>'
            f'<text class="legend-code" x="{x + 21}" y="{y + 11}">{REGION_CODES[name]}</text>'
            f'<text class="legend-name" x="{x + 61}" y="{y + 11}">{name.upper()}</text>'
            f'<text class="legend-count" x="{x + 260}" y="{y + 11}">{REGION_COUNTS[name]}</text></g>'
        )
    legend = "".join(legend_items)
    north_cap = render_polar_cap(
        states, geojson, north=True, box=NORTH_POLAR_BOX, show_hairlines=show_hairlines,
    )
    south_cap = render_polar_cap(
        states, geojson, north=False, box=SOUTH_POLAR_BOX, show_hairlines=show_hairlines,
    )
    state_key_opacity = "1" if show_hairlines else ".22"
    state_key_label = "STATE BORDER" if show_hairlines else "STATE BORDER · HIDDEN"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{STATE_CANVAS[0]}" height="{STATE_CANVAS[1]}" viewBox="0 0 {STATE_CANVAS[0]} {STATE_CANVAS[1]}" role="img" aria-labelledby="title desc">
  <title id="title">{candidate.title} 56-state projection study</title>
  <desc id="desc">A provisional OSW hierarchy of 11 organizational realms, 22 contiguous schematic regions, and 56 classic province identities transformed into {candidate.title}. The 22 regions are connected before land masking and projection interruption; visible pieces can be separated by continents or lobe seams. White hatched continents are background context. Province cells are an original nearest-seed approximation, not published Longhurst boundaries, and do not support area or boundary measurement. State hairlines are {'shown' if show_hairlines else 'hidden'}.</desc>
  <metadata>Natural Earth 1:110m land, public domain, commit {SOURCE_COMMIT}, SHA-256 {source_sha256}. Original OSW geographic nearest-seed state geometry; no geographic Longhurst boundary dataset is reproduced. Main projection: {candidate.proj4}. North inset: Lambert azimuthal equal-area, +proj=laea +lat_0=90 +lon_0=0, 48N to 90N. South inset: Lambert azimuthal equal-area, +proj=laea +lat_0=-90 +lon_0=0, 45S to 90S. Region system: provisional osw-regions-v0.1; connected in the unmasked, pre-projection seed topology.</metadata>
  <defs>
    <clipPath id="state-map-clip"><rect x="{map_x:g}" y="{map_y:g}" width="{map_width:g}" height="{map_height:g}" rx="20"/></clipPath>
    <clipPath id="north-polar-clip"><circle cx="738" cy="228" r="78"/></clipPath>
    <clipPath id="south-polar-clip"><circle cx="980" cy="228" r="78"/></clipPath>
    <pattern id="state-land-hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="9" height="9" fill="#f3f4f1"/><path d="M0 0V9" stroke="#aebbb7" stroke-width=".7" stroke-opacity=".16"/></pattern>
    <style>
      text {{ font-family:Inter,ui-sans-serif,system-ui,sans-serif; }}
      .province path {{ {hairline_rule} stroke-linejoin:round; vector-effect:non-scaling-stroke; }}
      {fill_rules}
      .realm-casing {{ fill:none; stroke:#f2f4ee; stroke-width:4.3; stroke-linejoin:round; vector-effect:non-scaling-stroke; }}
      .realm-boundaries {{ fill:none; stroke:#09232a; stroke-width:1.7; stroke-linejoin:round; vector-effect:non-scaling-stroke; }}
      .region-casing {{ fill:none; stroke:#f2f4ee; stroke-width:2.8; stroke-linejoin:round; vector-effect:non-scaling-stroke; }}
      .region-boundaries {{ fill:none; stroke:#304b51; stroke-width:.9; stroke-linejoin:round; vector-effect:non-scaling-stroke; }}
      .land {{ fill:url(#state-land-hatch); stroke:#899a96; stroke-width:.8; stroke-opacity:.45; vector-effect:non-scaling-stroke; }}
      .state-labels text {{ fill:#19353b; fill-opacity:.62; font:650 7.4px ui-monospace,Consolas,monospace; text-anchor:middle; paint-order:stroke; stroke:#edf2ed; stroke-opacity:.82; stroke-width:1.8px; pointer-events:none; }}
      .region-labels text {{ fill:#102d34; fill-opacity:.94; font:950 10px ui-monospace,Consolas,monospace; letter-spacing:1px; text-anchor:middle; paint-order:stroke; stroke:#f3f5f1; stroke-opacity:.96; stroke-width:2.8px; pointer-events:none; }}
      .polar-cap-land {{ fill:url(#state-land-hatch); stroke:#899a96; stroke-width:.55; stroke-opacity:.55; vector-effect:non-scaling-stroke; }}
      .polar-cap-labels text {{ fill:#102d34; font:900 10px ui-monospace,Consolas,monospace; text-anchor:middle; paint-order:stroke; stroke:#f3f5f1; stroke-width:2.2px; }}
      .legend-code {{ fill:#eef9f7; font-weight:950; }}
      .legend-name {{ fill:#9bb2b1; font-weight:650; }}
      .legend-count {{ fill:#67e4da; font-weight:900; text-anchor:end; }}
    </style>
  </defs>
  <rect width="{STATE_CANVAS[0]}" height="{STATE_CANVAS[1]}" fill="#06171c"/>
  <text x="56" y="45" fill="#67e4da" font-size="15" font-weight="900" letter-spacing="3">OSW / OCEAN STATES OF THE WORLD</text>
  <text x="56" y="82" fill="#eef9f7" font-size="32" font-weight="900">{candidate.title}</text>
  <text x="56" y="108" fill="#8da9a9" font-size="12">56 classic province identities · provisional OSW organization and geometry</text>
  <rect x="904" y="31" width="240" height="27" rx="13.5" fill="#2b2420" stroke="#ffb454" stroke-opacity=".7"/>
  <text x="1024" y="49" text-anchor="middle" fill="#ffb454" font-size="10" font-weight="950" letter-spacing="1.5">SCHEMATIC · PROVISIONAL</text>
  <text x="1144" y="82" text-anchor="end" fill="#eef9f7" font-size="12" font-weight="900" letter-spacing="1.4">{candidate.property_label}</text>
  <text x="1144" y="104" text-anchor="end" fill="#8da9a9" font-size="11">{candidate.subtitle} · {hairline_label}</text>
  <g class="polar-inset" aria-label="Polar Realm top-down views">
    <rect x="56" y="124" width="1088" height="210" rx="20" fill="#0d252b" stroke="#49666b" stroke-width="1.2"/>
    <text x="78" y="157" fill="#67e4da" font-size="11" font-weight="900" letter-spacing="1.6">POLAR REALM · EQUAL-AREA TOP-DOWN</text>
    <text x="78" y="184" fill="#eef9f7" font-size="18" font-weight="850">Three schematic regions at two ends of Earth</text>
    <text x="78" y="214" fill="#b8cbca" font-size="11"><tspan font-weight="900">AAP</tspan> · Arctic–Atlantic Polar</text>
    <text x="78" y="237" fill="#b8cbca" font-size="11"><tspan font-weight="900">NPP</tspan> · North Pacific Polar</text>
    <text x="78" y="260" fill="#b8cbca" font-size="11"><tspan font-weight="900">ANP</tspan> · Antarctic Polar</text>
    <text x="78" y="294" fill="#718d8f" font-size="9.5">Insets restore polar adjacency hidden by the interrupted world view.</text>
    <text x="78" y="313" fill="#718d8f" font-size="9.5">They do not repair lobe seams or convert schematic cells into measured boundaries.</text>
    <g clip-path="url(#north-polar-clip)">{north_cap}</g><circle cx="738" cy="228" r="78" fill="none" stroke="#9ab0b0" stroke-width="1"/>
    <text x="738" y="321" text-anchor="middle" fill="#8da9a9" font-size="9" font-weight="800" letter-spacing="1">NORTH · LAEA · 48°N–90°N</text>
    <g clip-path="url(#south-polar-clip)">{south_cap}</g><circle cx="980" cy="228" r="78" fill="none" stroke="#9ab0b0" stroke-width="1"/>
    <text x="980" y="321" text-anchor="middle" fill="#8da9a9" font-size="9" font-weight="800" letter-spacing="1">SOUTH · LAEA · 45°S–90°S</text>
  </g>
  <g clip-path="url(#state-map-clip)">
    <rect x="{map_x:g}" y="{map_y:g}" width="{map_width:g}" height="{map_height:g}" fill="#112a30"/>
    {''.join(province_groups)}
    <path class="region-casing" d="{region_path}"/><path class="region-boundaries" d="{region_path}"/><path class="realm-casing" d="{realm_path}"/><path class="realm-boundaries" d="{realm_path}"/>
    <path class="land" d="{land}" fill-rule="evenodd"/>
    <g class="state-labels">{''.join(province_labels)}</g>
    <g class="region-labels">{''.join(map_region_labels)}</g>
  </g>
  <rect x="{map_x:g}" y="{map_y:g}" width="{map_width:g}" height="{map_height:g}" rx="20" fill="none" stroke="#49666b" stroke-width="1.5"/>
  <text x="56" y="1104" fill="#eef9f7" font-size="16" font-weight="800">Equal-area ocean view; lobe cuts interrupt some neighborhoods.</text>
  <g transform="translate(56 1128)" aria-label="Boundary hierarchy key" font-size="10" font-weight="800">
    <path d="M0 0H46" stroke="#f2f4ee" stroke-width="5"/><path d="M0 0H46" stroke="#09232a" stroke-width="1.7"/><text x="58" y="4" fill="#b9cdca">REALM</text>
    <path d="M170 0H216" stroke="#f2f4ee" stroke-width="3"/><path d="M170 0H216" stroke="#304b51" stroke-width=".9"/><text x="228" y="4" fill="#b9cdca">SCHEMATIC REGION</text>
    <path d="M410 0H456" stroke="#71878a" stroke-width=".35" stroke-opacity="{state_key_opacity}"/><text x="468" y="4" fill="#b9cdca">{state_key_label}</text>
    <text x="1144" y="4" text-anchor="end" fill="#718d8f">WHITE LAND = GEOGRAPHIC ANCHOR</text>
  </g>
  <g transform="translate(56 1170)" font-size="10">
    <text y="-14" fill="#b9cdca" font-size="11" font-weight="900" letter-spacing="1.2">11 ORGANIZATIONAL REALMS · 22 CONTIGUOUS SCHEMATIC REGIONS · 56 CLASSIC PROVINCE IDENTITIES</text>
    {legend}
  </g>
  <text x="56" y="1328" fill="#718d8f" font-size="9.5">CONTIGUITY IS DEFINED BEFORE LAND MASKING AND PROJECTION INTERRUPTION · VISIBLE PIECES MAY SEPARATE AT LAND OR LOBE SEAMS</text>
  <text x="56" y="1349" fill="#718d8f" font-size="9.5">NOT PUBLISHED LONGHURST BOUNDARIES · NO AREA OR BOUNDARY MEASUREMENT FROM APPROXIMATE CELLS · SAME WHITE-LAND TREATMENT</text>
</svg>'''


def line_path(points: Sequence[Point], project: Projector, bounds: tuple[float, float, float, float], screen: Callable[[Point], Point]) -> str:
    return svg_path(projected_segments(points, project, bounds), screen)


def geographic_circle(longitude: float, latitude: float, radius_degrees: float) -> list[Point]:
    points: list[Point] = []
    longitude_scale = max(0.25, math.cos(math.radians(latitude)))
    for angle in range(0, 361, 6):
        radians = math.radians(angle)
        points.append((longitude + radius_degrees * math.cos(radians) / longitude_scale, latitude + radius_degrees * math.sin(radians)))
    return points


def render_polar_cap(
    states: list[dict],
    geojson: dict,
    *,
    north: bool,
    box: tuple[float, float, float, float],
    show_hairlines: bool,
) -> str:
    """Render a top-down polar cap using the same state and region system."""
    latitude_edge = NORTH_POLAR_CUTOFF if north else SOUTH_POLAR_CUTOFF
    extent = (-180.0, latitude_edge if north else -89.5, 180.0, 89.5 if north else latitude_edge)
    latitude_0 = 90 if north else -90
    project = pyproj_projector(f"+proj=laea +lat_0={latitude_0} +lon_0=0 +R=1 +units=m +no_defs")
    bounds = local_bounds(project, extent)
    screen = screen_transform(bounds, box=box)
    south, north_edge = (latitude_edge, 89.5) if north else (-89.5, latitude_edge)

    cells = []
    for state in states:
        commands = []
        for polygon in state["pieces"]:
            clipped = clip_geographic_polygon(polygon, -180.0, 180.0, south, north_edge)
            if len(clipped) >= 3:
                commands.append(filled_svg_path(projected_segments(clipped, project, bounds, close=True), screen))
        if not any(commands):
            continue
        tone = REGION_TONES[region_name(state["code"])]
        stroke = "#71878a" if show_hairlines else tone
        opacity = ".58" if show_hairlines else "1"
        cells.append(
            f'<path d="{"".join(commands)}" fill="{tone}" stroke="{stroke}" stroke-width=".35" '
            f'stroke-opacity="{opacity}" vector-effect="non-scaling-stroke"><title>{state["code"]} — {state["name"]}</title></path>'
        )

    land_commands = []
    for ring in all_rings(geojson):
        clipped = clip_geographic_polygon(ring, -180.0, 180.0, south, north_edge)
        if len(clipped) >= 3:
            land_commands.append(filled_svg_path(projected_segments(clipped, project, bounds, close=True), screen))

    labels = []
    polar_markers = (("AAP", "SARC"), ("NPP", "BERS")) if north else (("ANP", "ANTA"),)
    for label, code in polar_markers:
        point = project(*PROVINCE_SEEDS[code])
        x, y = screen(point)
        labels.append(f'<text x="{x:.1f}" y="{y:.1f}">{label}</text>')

    return (
        f'<g class="polar-cap-cells">{"".join(cells)}</g>'
        f'<path class="polar-cap-land" d="{"".join(land_commands)}" fill-rule="evenodd"/>'
        f'<g class="polar-cap-labels">{"".join(labels)}</g>'
    )


def geographic_blob(longitude: float, latitude: float, radius_degrees: float) -> list[Point]:
    points: list[Point] = []
    longitude_scale = max(0.25, math.cos(math.radians(latitude)))
    for angle in range(0, 361, 6):
        radians = math.radians(angle)
        local_radius = radius_degrees * (1.0 + 0.14 * math.sin(radians * 3.0) + 0.08 * math.cos(radians * 5.0))
        points.append((longitude + local_radius * math.cos(radians) / longitude_scale, latitude + local_radius * math.sin(radians)))
    return points


def render_candidate(candidate: Candidate, geojson: dict, source_sha256: str) -> str:
    bounds = raw_bounds(candidate.projector)
    screen = screen_transform(bounds)
    coastline_commands: list[str] = []
    for ring in all_rings(geojson):
        segments = projected_segments(ring, candidate.projector, bounds, close=True)
        coastline_commands.append(svg_path(segments, screen))
    coastlines = "".join(coastline_commands)

    graticule_commands: list[str] = []
    for latitude in range(-60, 61, 30):
        graticule_commands.append(line_path([(longitude, latitude) for longitude in range(-180, 181, 2)], candidate.projector, bounds, screen))
    for longitude in range(-150, 181, 30):
        graticule_commands.append(line_path([(longitude, latitude) for latitude in range(-88, 89, 2)], candidate.projector, bounds, screen))
    graticule = "".join(graticule_commands)

    heatmass_paths = "".join(
        f'<path class="heatmass" d="{svg_path(projected_segments(polygon, candidate.projector, bounds, close=True), screen, close=True)}"/>'
        for polygon in HEAT_POLYGONS
    )
    shelf_paths = "".join(
        f'<path class="shelf" d="{line_path(shelf, candidate.projector, bounds, screen)}"/>'
        for shelf in HEAT_SHELVES
    )

    fluid_lines = {
        "elnino": [(175, 0), (200, 0), (230, -1), (260, -2)],
        "gulf": [(-80, 25), (-73, 35), (-58, 43), (-38, 49)],
        "kuroshio": [(128, 22), (138, 34), (154, 40), (178, 43)],
        "agulhas": [(31, -29), (26, -38), (18, -43), (8, -42)],
        "arctic": [(-20, 58), (-5, 68), (22, 76), (62, 80), (105, 78)],
        "acc": [(longitude, -55 + 2.5 * math.sin(math.radians(longitude * 2))) for longitude in range(-180, 181, 2)],
    }
    paths = {name: line_path(points, candidate.projector, bounds, screen) for name, points in fluid_lines.items()}
    blob_segments = projected_segments(geographic_blob(-145, 45, 12), candidate.projector, bounds, close=True)
    blob = svg_path(blob_segments, screen, close=True)

    gate_symbols: list[str] = []
    for longitude, latitude in [(-68, -56), (123, -3)]:
        gate_x, gate_y = screen(candidate.projector(longitude, latitude))
        gate_symbols.append(f'<path class="gate" d="M{gate_x:.1f},{gate_y - 9:.1f}l9,9l-9,9l-9,-9Z"/>')
    gates = "".join(gate_symbols)

    singularity_note = "ANTIPODAL EDGE: SAHARA" if candidate.slug == "pelagos" else ""
    if candidate.frame == "circle":
        frame_shape = '<circle cx="450" cy="377" r="269"/>'
    elif candidate.frame == "square":
        frame_shape = '<rect x="185" y="112" width="530" height="530" rx="24"/>'
    else:
        frame_shape = '<rect x="42" y="112" width="816" height="530" rx="24"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">{candidate.title} ocean projection prototype</title>
  <desc id="desc">The {candidate.title} candidate projects the same schematic OSW heat reservoirs, transient anomaly, currents, and Antarctic Circumpolar Current over checksum-pinned Natural Earth coastlines. {candidate.tradeoff}</desc>
  <metadata>Natural Earth 1:110m land, public domain, commit {SOURCE_COMMIT}, SHA-256 {source_sha256}, {SOURCE_URL}. Projection rendering and conceptual overlays are original MIT-licensed OSW work. PELAGOS is an experimental aspect of Lambert azimuthal equal-area, not a new projection equation.</metadata>
  <defs>
    <linearGradient id="ocean" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#123f4c"/><stop offset="1" stop-color="#061922"/></linearGradient>
    <linearGradient id="heat" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#ffd46b"/><stop offset="1" stop-color="#ff8f4d"/></linearGradient>
    <radialGradient id="blob"><stop stop-color="#ff756d" stop-opacity=".72"/><stop offset="1" stop-color="#ff756d" stop-opacity=".08"/></radialGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <clipPath id="map-clip">{frame_shape}</clipPath>
    <style>
      text {{ font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
      .grid {{ fill:none; stroke:#aad4d6; stroke-opacity:.12; stroke-width:1; }}
      .coast {{ fill:none; stroke:#a7c2c1; stroke-opacity:.32; stroke-width:1.15; vector-effect:non-scaling-stroke; }}
      .heatmass {{ fill:url(#heat); fill-opacity:.72; stroke:#ffd06b; stroke-width:3; stroke-linejoin:round; }}
      .shelf {{ fill:none; stroke:#ffe6a5; stroke-width:2; stroke-dasharray:12 8; stroke-linecap:round; stroke-opacity:.8; }}
      .anomaly {{ fill:url(#blob); stroke:#ff8d84; stroke-width:2.5; stroke-dasharray:9 7; }}
      .tongue {{ fill:none; stroke:#ff8178; stroke-width:26; stroke-linecap:round; stroke-dasharray:10 7; stroke-opacity:.7; }}
      .current {{ fill:none; stroke:#ffb454; stroke-width:8; stroke-linecap:round; filter:url(#glow); }}
      .acc {{ fill:none; stroke:#8eeaf2; stroke-width:9; stroke-dasharray:18 10; filter:url(#glow); }}
      .buried {{ fill:none; stroke:#b7a7ff; stroke-width:13; stroke-dasharray:10 7; stroke-linecap:round; stroke-opacity:.62; }}
      .gate {{ fill:#071b22; stroke:#67e4da; stroke-width:3; }}
    </style>
  </defs>
  <rect width="900" height="760" fill="#06171c"/>
  <text x="42" y="44" fill="#67e4da" font-size="15" font-weight="900" letter-spacing="3">OSW / PROJECTION LAB</text>
  <text x="42" y="79" fill="#eef9f7" font-size="30" font-weight="900">{candidate.title}</text>
  <text x="858" y="56" text-anchor="end" fill="#ffb454" font-size="12" font-weight="900" letter-spacing="1.8">{candidate.property_label}</text>
  <text x="858" y="79" text-anchor="end" fill="#8da9a9" font-size="13">{candidate.subtitle}</text>
  <g clip-path="url(#map-clip)">
    <rect x="42" y="108" width="816" height="538" fill="url(#ocean)"/>
    <path class="grid" d="{graticule}"/>
    {heatmass_paths}{shelf_paths}
    <path class="anomaly" d="{blob}"/>
    <path class="tongue" d="{paths['elnino']}"/>
    <path class="coast" d="{coastlines}"/>
    <path class="current" d="{paths['gulf']}"/><path class="current" d="{paths['kuroshio']}"/><path class="current" d="{paths['agulhas']}"/>
    <path class="buried" d="{paths['arctic']}"/>
    <path class="acc" d="{paths['acc']}"/>
    {gates}
  </g>
  <g fill="none" stroke="#49666b" stroke-width="1.5">{frame_shape}</g>
  <text x="42" y="680" fill="#eef9f7" font-size="16" font-weight="800">{candidate.tradeoff}</text>
  <text x="42" y="710" fill="#8da9a9" font-size="12">Same schematic features · same coastline source · projection changes only</text>
  <text x="858" y="710" text-anchor="end" fill="#ffb454" font-size="11" font-weight="800" letter-spacing="1.4">{singularity_note}</text>
  <g transform="translate(42 730)" font-size="9" font-weight="800"><path d="M0-3h25" stroke="#ffb454" stroke-width="12" stroke-linecap="round"/><text x="34" fill="#8da9a9">HEATMASS</text><circle cx="125" cy="-3" r="5" fill="#ff8d84"/><text x="137" fill="#8da9a9">ANOMALY</text><path d="M218-3h25" stroke="#ffb454" stroke-width="5"/><text x="251" fill="#8da9a9">CURRENT</text><path d="M324-3h27" stroke="#8eeaf2" stroke-width="5" stroke-dasharray="8 5"/><text x="359" fill="#8da9a9">ACC</text><path d="M405-3h25" stroke="#b7a7ff" stroke-width="7" stroke-dasharray="6 4"/><text x="438" fill="#8da9a9">BURIED INFLOW</text><path d="M560-10l7 7-7 7-7-7Z" fill="none" stroke="#67e4da" stroke-width="2"/><text x="575" fill="#8da9a9">GATE</text></g>
</svg>'''


def render_heatplates(geojson: dict, source_sha256: str) -> str:
    plate_width = 366
    plate_height = 346
    plate_gap = 18
    start_x = 30
    start_y = 132
    definitions = [
        {
            "number": "01", "title": "INDO-PACIFIC WARM POOL", "kind": "RESERVOIR",
            "center": (145, -5), "extent": (78, -30, 218, 28),
            "polygons": HEAT_POLYGONS[:2], "shelves": HEAT_SHELVES[:2], "class": "reservoir",
        },
        {
            "number": "02", "title": "WESTERN WARM POOL", "kind": "SEASONAL RESERVOIR",
            "center": (-85, 12), "extent": (-130, -8, -38, 35),
            "polygons": [HEAT_POLYGONS[2]], "shelves": [HEAT_SHELVES[2]], "class": "reservoir",
        },
        {
            "number": "03", "title": "NORTHEAST PACIFIC BLOB", "kind": "TRANSIENT ANOMALY",
            "center": (-145, 45), "extent": (-180, 20, -105, 70),
            "polygons": [geographic_blob(-145, 45, 12)], "shelves": [], "class": "anomaly",
        },
        {
            "number": "04", "title": "EL NIÑO TONGUE", "kind": "EQUATORIAL ANOMALY",
            "center": (-130, 0), "extent": (165, -22, 285, 22),
            "polygons": [EL_NINO_POLYGON], "shelves": [[(180, 1), (205, 1), (232, -1), (260, -4)]], "class": "tongue",
        },
        {
            "number": "05", "title": "ATLANTIC WATER / ARCTIC", "kind": "BURIED HEATMASS",
            "center": (48, 72), "extent": (-35, 48, 145, 89),
            "polygons": [ARCTIC_WATER_POLYGON], "shelves": [[(-12, 61), (14, 69), (45, 75), (80, 78), (112, 75)]], "class": "buried",
        },
        {
            "number": "06", "title": "CIRCUMPOLAR DEEP WATER", "kind": "ANNULAR HEATMASS",
            "center": (0, -90), "extent": (-180, -90, 180, -34),
            "polygons": [], "shelves": [], "class": "belt",
        },
    ]

    panels: list[str] = []
    for index, definition in enumerate(definitions):
        column = index % 3
        row = index // 3
        x = start_x + column * (plate_width + plate_gap)
        y = start_y + row * (plate_height + plate_gap)
        map_box = (x + 16, y + 70, plate_width - 32, plate_height - 88)
        center_lon, center_lat = definition["center"]
        project = pyproj_projector(f"+proj=laea +lat_0={center_lat} +lon_0={center_lon} +R=1 +units=m +no_defs")
        bounds = local_bounds(project, definition["extent"])
        screen = screen_transform(bounds, map_box)

        coastline_commands: list[str] = []
        for ring in all_rings(geojson):
            coastline_commands.append(svg_path(projected_segments(ring, project, bounds, close=True), screen))
        coastlines = "".join(coastline_commands)

        region_paths = "".join(
            f'<path class="plate-region {definition["class"]}" d="{svg_path(projected_segments(polygon, project, bounds, close=True), screen, close=True)}"/>'
            for polygon in definition["polygons"]
        )
        shelf_paths = "".join(
            f'<path class="plate-shelf" d="{line_path(shelf, project, bounds, screen)}"/>'
            for shelf in definition["shelves"]
        )
        if definition["class"] == "belt":
            outer = [(longitude, -46) for longitude in range(-180, 181, 3)]
            inner = [(longitude, -66) for longitude in range(180, -181, -3)]
            outer_segments = projected_segments(outer, project, bounds, close=True)
            inner_segments = projected_segments(inner, project, bounds, close=True)
            annulus = svg_path(outer_segments, screen, close=True) + svg_path(inner_segments, screen, close=True)
            region_paths = f'<path class="plate-region belt" fill-rule="evenodd" d="{annulus}"/>'
            shelf_paths = f'<path class="plate-shelf" d="{line_path([(longitude, -56) for longitude in range(-180, 181, 3)], project, bounds, screen)}"/>'

        clip_id = f"plate-clip-{index + 1}"
        panels.append(f'''
    <g class="plate">
      <rect x="{x}" y="{y}" width="{plate_width}" height="{plate_height}" rx="18" fill="#092129" stroke="#29484f"/>
      <text x="{x + 18}" y="{y + 28}" fill="#ffb454" font-size="11" font-weight="900">{definition["number"]}</text>
      <text x="{x + 48}" y="{y + 28}" fill="#eef9f7" font-size="14" font-weight="900">{definition["title"]}</text>
      <text x="{x + 48}" y="{y + 48}" fill="#8da9a9" font-size="10" font-weight="800" letter-spacing="1">{definition["kind"]}</text>
      <defs><clipPath id="{clip_id}"><rect x="{map_box[0]}" y="{map_box[1]}" width="{map_box[2]}" height="{map_box[3]}" rx="12"/></clipPath></defs>
      <g clip-path="url(#{clip_id})">
        <rect x="{map_box[0]}" y="{map_box[1]}" width="{map_box[2]}" height="{map_box[3]}" fill="url(#plate-ocean)"/>
        {region_paths}{shelf_paths}<path class="plate-coast" d="{coastlines}"/>
      </g>
      <rect x="{map_box[0]}" y="{map_box[1]}" width="{map_box[2]}" height="{map_box[3]}" rx="12" fill="none" stroke="#365961"/>
      <text x="{x + 18}" y="{y + plate_height - 9}" fill="#789497" font-size="9">LOCAL LAMBERT EQUAL-AREA · PANEL-SPECIFIC ZOOM</text>
    </g>''')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900" role="img" aria-labelledby="title desc">
  <title id="title">OSW HEATPLATES</title>
  <desc id="desc">Six flat local equal-area panels show the individual schematic shapes of the Indo-Pacific warm pool, Western Hemisphere warm pool, Northeast Pacific Blob, El Niño tongue, buried Atlantic Water in the Arctic, and Circumpolar Deep Water. Every panel uses its own zoom, so footprint areas must not be compared.</desc>
  <metadata>Natural Earth 1:110m land, public domain, commit {SOURCE_COMMIT}, SHA-256 {source_sha256}, {SOURCE_URL}. Local Lambert equal-area views and schematic heat polygons are original MIT-licensed OSW work.</metadata>
  <defs>
    <linearGradient id="plate-ocean" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#123f4c"/><stop offset="1" stop-color="#061922"/></linearGradient>
    <linearGradient id="plate-heat" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#ffd46b"/><stop offset="1" stop-color="#ff8f4d"/></linearGradient>
    <style>
      text {{ font-family:Inter,ui-sans-serif,system-ui,sans-serif; }}
      .plate-coast {{ fill:none; stroke:#a7c2c1; stroke-opacity:.42; stroke-width:1.1; vector-effect:non-scaling-stroke; }}
      .plate-region {{ stroke-width:3; stroke-linejoin:round; }}
      .plate-region.reservoir {{ fill:url(#plate-heat); fill-opacity:.78; stroke:#ffd06b; }}
      .plate-region.anomaly,.plate-region.tongue {{ fill:#ff766c; fill-opacity:.48; stroke:#ff8d84; stroke-dasharray:9 7; }}
      .plate-region.buried {{ fill:#9c8bf2; fill-opacity:.4; stroke:#c5baff; stroke-dasharray:10 7; }}
      .plate-region.belt {{ fill:#8eeaf2; fill-opacity:.25; stroke:#8eeaf2; stroke-dasharray:14 9; }}
      .plate-shelf {{ fill:none; stroke:#fff0b8; stroke-opacity:.78; stroke-width:2; stroke-dasharray:12 8; stroke-linecap:round; }}
    </style>
  </defs>
  <rect width="1200" height="900" fill="#06171c"/>
  <text x="30" y="40" fill="#67e4da" font-size="15" font-weight="900" letter-spacing="3">OSW / SHAPE ATLAS</text>
  <text x="30" y="82" fill="#eef9f7" font-size="38" font-weight="950">HEATPLATES</text>
  <text x="1170" y="48" text-anchor="end" fill="#ffb454" font-size="12" font-weight="900" letter-spacing="1.8">SHAPE FIRST · NOT ONE WORLD MAP</text>
  <text x="1170" y="76" text-anchor="end" fill="#8da9a9" font-size="12">Schematic boundaries · local equal-area · zoom varies by panel</text>
  <rect x="30" y="96" width="1140" height="24" rx="12" fill="#112e34"/>
  <text x="600" y="112" text-anchor="middle" fill="#ffcf70" font-size="10" font-weight="900" letter-spacing="1.3">DO NOT COMPARE FOOTPRINT AREA ACROSS PANELS · EACH VIEW USES ITS OWN ZOOM</text>
  {''.join(panels)}
  <text x="30" y="882" fill="#789497" font-size="10">CONCEPTUAL SHAPE DIRECTORY · NOT OBSERVED THRESHOLDS · NOT HEAT CONTENT · NOT TRANSPORT</text>
</svg>'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--land-geojson", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    payload = args.land_geojson.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"Natural Earth source checksum mismatch: {digest}")
    geojson = json.loads(payload)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for candidate in candidates():
        output = args.output_dir / f"osw-projection-{candidate.slug}.svg"
        output.write_text(render_candidate(candidate, geojson, digest), encoding="utf-8", newline="\n")
    for candidate in state_projection_candidates():
        output = args.output_dir / f"osw-state-projection-{candidate.slug}.svg"
        output.write_text(render_state_projection(candidate, geojson, digest), encoding="utf-8", newline="\n")
        no_hairlines_output = args.output_dir / f"osw-state-projection-{candidate.slug}-no-hairlines.svg"
        no_hairlines_output.write_text(
            render_state_projection(candidate, geojson, digest, show_hairlines=False),
            encoding="utf-8",
            newline="\n",
        )
    heatplates_output = args.output_dir / "osw-heatplates.svg"
    heatplates_output.write_text(render_heatplates(geojson, digest), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()

"""Render OSW observational fields through the Oceanic Mollweide state map.

The output is a matched-view experiment: one projection, one state hierarchy,
and seven existing Atlas data products.  Data cells are projected directly;
the provisional OSW state system is a reference overlay, never an aggregation
or substitute for the source grid.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

from build_projection_bakeoff import (
    EXPECTED_SOURCE_SHA256,
    NORTH_POLAR_CUTOFF,
    SOUTH_POLAR_CUTOFF,
    SOURCE_COMMIT,
    StateCandidate,
    all_rings,
    clip_geographic_polygon,
    densify,
    filled_svg_path,
    geographic_state_geometry,
    local_bounds,
    projected_edge_path,
    projected_polygon_fill,
    pyproj_projector,
    raw_bounds,
    screen_transform,
)
from build_province_cartogram import PROVINCE_SEEDS, REGION_MARKERS


Point = tuple[float, float]
Palette = tuple[tuple[float, tuple[int, int, int]], ...]

CANVAS = (1200, 1210)
MAP_BOX = (56.0, 296.0, 1088.0, 706.0)
NORTH_POLAR_BOX = (778.0, 137.0, 126.0, 126.0)
SOUTH_POLAR_BOX = (970.0, 137.0, 126.0, 126.0)
MOLLWEIDE = StateCandidate(
    "mollweide-oceanic",
    "OCEANIC MOLLWEIDE",
    "Six ocean-emphasis lobes",
    "EQUAL-AREA · INTERRUPTED",
    "Equal-area ocean view; lobe cuts interrupt some neighborhoods.",
    "+proj=imoll_o +lon_0=-160 +R=1 +units=m +no_defs",
)

TEMPERATURE_PALETTE: Palette = (
    (-2, (216, 244, 255)), (0, (141, 211, 232)), (8, (43, 156, 189)),
    (16, (56, 182, 138)), (22, (242, 207, 91)), (28, (240, 120, 66)),
    (32, (185, 39, 53)),
)
ANOMALY_PALETTE: Palette = (
    (-5, (35, 59, 131)), (-3, (61, 119, 184)), (-1, (155, 203, 225)),
    (0, (238, 233, 216)), (1, (241, 187, 120)), (3, (207, 91, 71)),
    (5, (124, 35, 69)),
)
ERROR_PALETTE: Palette = (
    (0.1, (244, 241, 222)), (0.2, (184, 216, 186)), (0.3, (110, 182, 167)),
    (0.4, (223, 179, 92)), (0.5, (184, 76, 76)), (0.6, (99, 44, 85)),
)


@dataclass(frozen=True)
class DataView:
    slug: str
    filename: str
    title: str
    eyebrow: str
    field_label: str
    palette: Palette
    coverage_note: str


VIEWS = (
    DataView("sst", "oisst-2026-08-01.js", "SEA SURFACE TEMPERATURE", "OBSERVATIONAL · SURFACE", "ABSOLUTE TEMPERATURE · °C", TEMPERATURE_PALETTE, "Global 2° display grid; missing and land cells remain dark or white."),
    DataView("sst-anomaly", "oisst-anomaly-2026-08-01.js", "SEA SURFACE TEMPERATURE ANOMALY", "OBSERVATIONAL · SURFACE", "ANOMALY FROM 1971–2000 · °C", ANOMALY_PALETTE, "Global 2° display grid; anomaly is relative to the declared 1971–2000 baseline."),
    DataView("sst-error", "oisst-error-2026-08-01.js", "ESTIMATED SST ANALYSIS ERROR", "OBSERVATIONAL · SURFACE", "ESTIMATED ERROR · °C", ERROR_PALETTE, "Time-matched OISST analysis-error field; not forecast error or total uncertainty."),
    DataView("argo-10", "argo-temperature-anomaly-10dbar-2026-07.js", "ARGO ANOMALY · 10 DBAR", "OBSERVATIONALLY CONSTRAINED · DEPTH", "POTENTIAL-TEMPERATURE ANOMALY · °C", ANOMALY_PALETTE, "RG Argo 2° display grid ends at 64.5°S and 79.5°N; blank polar areas are outside coverage."),
    DataView("argo-300", "argo-temperature-anomaly-300dbar-2026-07.js", "ARGO ANOMALY · 300 DBAR", "OBSERVATIONALLY CONSTRAINED · DEPTH", "POTENTIAL-TEMPERATURE ANOMALY · °C", ANOMALY_PALETTE, "RG Argo 2° display grid ends at 64.5°S and 79.5°N; blank polar areas are outside coverage."),
    DataView("argo-700", "argo-temperature-anomaly-700dbar-2026-07.js", "ARGO ANOMALY · 700 DBAR", "OBSERVATIONALLY CONSTRAINED · DEPTH", "POTENTIAL-TEMPERATURE ANOMALY · °C", ANOMALY_PALETTE, "RG Argo 2° display grid ends at 64.5°S and 79.5°N; blank polar areas are outside coverage."),
    DataView("argo-1000", "argo-temperature-anomaly-1000dbar-2026-07.js", "ARGO ANOMALY · 1000 DBAR", "OBSERVATIONALLY CONSTRAINED · DEPTH", "POTENTIAL-TEMPERATURE ANOMALY · °C", ANOMALY_PALETTE, "RG Argo 2° display grid ends at 64.5°S and 79.5°N; blank polar areas are outside coverage."),
)


def load_javascript_payload(path: Path) -> dict:
    source = path.read_text(encoding="utf-8")
    if "=" not in source:
        raise ValueError(f"Expected one JavaScript assignment in {path}")
    payload = json.loads(source.split("=", 1)[1].strip().removesuffix(";"))
    rows, columns = payload["shape"]
    if len(payload["values_c_hundredths"]) != rows * columns:
        raise ValueError(f"Grid shape mismatch in {path}")
    return payload


def color_for_value(value: float, palette: Palette) -> str:
    bounded = max(palette[0][0], min(palette[-1][0], value))
    upper = next((index for index, stop in enumerate(palette) if stop[0] >= bounded), len(palette) - 1)
    upper = max(1, upper)
    low_value, low_color = palette[upper - 1]
    high_value, high_color = palette[upper]
    mix = (bounded - low_value) / (high_value - low_value)
    channels = tuple(round(low + (high - low) * mix) for low, high in zip(low_color, high_color))
    return "#" + "".join(f"{channel:02x}" for channel in channels)


def normalized_longitude(longitude: float) -> float:
    return (longitude + 180.0) % 360.0 - 180.0


def cell_pieces(longitude: float, latitude: float, longitude_step: float, latitude_step: float) -> list[list[Point]]:
    center = normalized_longitude(longitude)
    half_lon = abs(longitude_step) / 2.0
    half_lat = abs(latitude_step) / 2.0
    south = max(-89.5, latitude - half_lat)
    north = min(89.5, latitude + half_lat)
    west, east = center - half_lon, center + half_lon
    intervals = [(west, east)]
    if west < -180.0:
        intervals = [(west + 360.0, 180.0), (-180.0, east)]
    elif east > 180.0:
        intervals = [(west, 180.0), (-180.0, east - 360.0)]
    return [[(left, south), (right, south), (right, north), (left, north)] for left, right in intervals]


def grouped_main_field(payload: dict, palette: Palette, project, bounds, screen) -> str:
    grouped: dict[str, list[str]] = defaultdict(list)
    rows, columns = payload["shape"]
    lat_start, lat_step = payload["latitude"]["start"], payload["latitude"]["step"]
    lon_start, lon_step = payload["longitude"]["start"], payload["longitude"]["step"]
    for row in range(rows):
        latitude = lat_start + row * lat_step
        for column in range(columns):
            encoded = payload["values_c_hundredths"][row * columns + column]
            if encoded is None:
                continue
            color = color_for_value(encoded / 100.0, palette)
            longitude = lon_start + column * lon_step
            for polygon in cell_pieces(longitude, latitude, lon_step, lat_step):
                command = projected_polygon_fill(polygon, MOLLWEIDE, project, bounds, screen)
                if command:
                    grouped[color].append(command)
    return "".join(
        f'<path fill="{color}" stroke="{color}" stroke-width=".35" d="{"".join(commands)}"/>'
        for color, commands in grouped.items()
    )


def grouped_polar_field(payload: dict, palette: Palette, *, north: bool, box: tuple[float, float, float, float]) -> str:
    cutoff = NORTH_POLAR_CUTOFF if north else SOUTH_POLAR_CUTOFF
    extent = (-180.0, cutoff if north else -89.5, 180.0, 89.5 if north else cutoff)
    project = pyproj_projector(f"+proj=laea +lat_0={90 if north else -90} +lon_0=0 +R=1 +units=m +no_defs")
    bounds = local_bounds(project, extent)
    screen = screen_transform(bounds, box=box)
    south, north_edge = (cutoff, 89.5) if north else (-89.5, cutoff)
    grouped: dict[str, list[str]] = defaultdict(list)
    rows, columns = payload["shape"]
    lat_start, lat_step = payload["latitude"]["start"], payload["latitude"]["step"]
    lon_start, lon_step = payload["longitude"]["start"], payload["longitude"]["step"]
    for row in range(rows):
        latitude = lat_start + row * lat_step
        if latitude + abs(lat_step) / 2 < south or latitude - abs(lat_step) / 2 > north_edge:
            continue
        for column in range(columns):
            encoded = payload["values_c_hundredths"][row * columns + column]
            if encoded is None:
                continue
            color = color_for_value(encoded / 100.0, palette)
            longitude = lon_start + column * lon_step
            for polygon in cell_pieces(longitude, latitude, lon_step, lat_step):
                clipped = clip_geographic_polygon(polygon, -180.0, 180.0, south, north_edge)
                if len(clipped) < 3:
                    continue
                projected = [project(lon, lat) for lon, lat in densify(clipped, step=0.75, close=True)]
                grouped[color].append(filled_svg_path([projected], screen))
    return "".join(
        f'<path fill="{color}" stroke="{color}" stroke-width=".25" d="{"".join(commands)}"/>'
        for color, commands in grouped.items()
    )


def projected_state_paths(states: Sequence[dict], project, bounds, screen) -> str:
    commands = []
    for state in states:
        for polygon in state["pieces"]:
            commands.append(projected_polygon_fill(polygon, MOLLWEIDE, project, bounds, screen))
    return "".join(commands)


def polar_land_path(geojson: dict, *, north: bool, box: tuple[float, float, float, float]) -> str:
    cutoff = NORTH_POLAR_CUTOFF if north else SOUTH_POLAR_CUTOFF
    extent = (-180.0, cutoff if north else -89.5, 180.0, 89.5 if north else cutoff)
    project = pyproj_projector(f"+proj=laea +lat_0={90 if north else -90} +lon_0=0 +R=1 +units=m +no_defs")
    bounds = local_bounds(project, extent)
    screen = screen_transform(bounds, box=box)
    south, north_edge = (cutoff, 89.5) if north else (-89.5, cutoff)
    commands = []
    for ring in all_rings(geojson):
        clipped = clip_geographic_polygon(ring, -180.0, 180.0, south, north_edge)
        if len(clipped) >= 3:
            projected = [project(lon, lat) for lon, lat in densify(clipped, step=0.75, close=True)]
            commands.append(filled_svg_path([projected], screen))
    return "".join(commands)


def gradient_definition(palette: Palette) -> str:
    low, high = palette[0][0], palette[-1][0]
    stops = []
    for value, color in palette:
        offset = (value - low) / (high - low) * 100
        stops.append(f'<stop offset="{offset:.2f}%" stop-color="#{"".join(f"{channel:02x}" for channel in color)}"/>')
    return "".join(stops)


def legend_ticks(palette: Palette) -> str:
    low, high = palette[0][0], palette[-1][0]
    items = []
    for value, _ in palette:
        x = 56 + (value - low) / (high - low) * 720
        label = f"{value:g}"
        if value > 0 and palette == ANOMALY_PALETTE:
            label = "+" + label
        items.append(f'<path d="M{x:.1f} 1080V1087" stroke="#b7cbca"/><text x="{x:.1f}" y="1102" text-anchor="middle">{label}</text>')
    return "".join(items)


def render_data_view(view: DataView, payload: dict, geojson: dict, land_sha256: str) -> str:
    project = pyproj_projector(MOLLWEIDE.proj4)
    bounds = raw_bounds(project)
    screen = screen_transform(bounds, box=MAP_BOX)
    states, realm_edges, region_edges = geographic_state_geometry()
    data_field = grouped_main_field(payload, view.palette, project, bounds, screen)
    state_path = projected_state_paths(states, project, bounds, screen)
    realm_path = projected_edge_path(realm_edges, MOLLWEIDE, project, bounds, screen)
    region_path = projected_edge_path(region_edges, MOLLWEIDE, project, bounds, screen)
    land_path = "".join(projected_polygon_fill(ring, MOLLWEIDE, project, bounds, screen) for ring in all_rings(geojson))

    state_labels = []
    for state in states:
        point = project(*state["seed"])
        x, y = screen(point)
        state_labels.append(f'<text x="{x:.1f}" y="{y + 2.5:.1f}">{state["code"]}</text>')
    region_labels = []
    for code, name, anchor in REGION_MARKERS:
        point = project(*PROVINCE_SEEDS[anchor])
        x, y = screen(point)
        region_labels.append(f'<text x="{x:.1f}" y="{y - 7:.1f}"><title>{html.escape(name)}</title>{code}</text>')

    north_field = grouped_polar_field(payload, view.palette, north=True, box=NORTH_POLAR_BOX)
    south_field = grouped_polar_field(payload, view.palette, north=False, box=SOUTH_POLAR_BOX)
    north_land = polar_land_path(geojson, north=True, box=NORTH_POLAR_BOX)
    south_land = polar_land_path(geojson, north=False, box=SOUTH_POLAR_BOX)

    observed_on = payload.get("date") or payload.get("month") or "date not declared"
    source = payload.get("source", "source not declared")
    baseline = payload.get("baseline") or "none; absolute field"
    boundary = payload.get("boundary", "See source metadata and OSW source register.")
    summary = payload.get("summary", {})
    minimum = summary.get("minimum_c")
    maximum = summary.get("maximum_c")
    range_label = f"DISPLAYED DATA RANGE {minimum:+.2f} TO {maximum:+.2f} °C" if minimum is not None and maximum is not None else "DISPLAYED DATA RANGE NOT DECLARED"
    source_digest = payload.get("source_sha256", "not packaged")
    source_terms = payload.get("source_data_terms", "Follow the source citation and terms declared in the packaged Atlas data artifact.")

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS[0]}" height="{CANVAS[1]}" viewBox="0 0 {CANVAS[0]} {CANVAS[1]}" role="img" aria-labelledby="title desc" data-view="{view.slug}" data-source-grid="direct">
  <title id="title">{html.escape(view.title)} on the OSW Oceanic Mollweide state map</title>
  <desc id="desc">{html.escape(view.title)} for {html.escape(str(observed_on))}, projected directly from its packaged grid into Oceanic Interrupted Mollweide. The provisional OSW 11-realm, 22-region, 56-identity state system is a reference overlay and does not aggregate or alter the field. Polar mirrors use Lambert azimuthal equal-area. {html.escape(view.coverage_note)} {html.escape(boundary)}</desc>
  <metadata>Data source: {html.escape(source)}. Source artifact SHA-256: {html.escape(source_digest)}. Baseline: {html.escape(str(baseline))}. Main projection: {MOLLWEIDE.proj4}. Polar mirrors: LAEA centered at 90N and 90S. Natural Earth land commit {SOURCE_COMMIT}, SHA-256 {land_sha256}. State overlay: provisional osw-regions-v0.1, original nearest-seed geometry, not published Longhurst boundaries. Source terms: {html.escape(source_terms)}</metadata>
  <defs>
    <clipPath id="data-map-clip"><rect x="56" y="296" width="1088" height="706" rx="20"/></clipPath>
    <clipPath id="data-north-clip"><circle cx="841" cy="200" r="63"/></clipPath>
    <clipPath id="data-south-clip"><circle cx="1033" cy="200" r="63"/></clipPath>
    <linearGradient id="data-scale" x1="0" x2="1">{gradient_definition(view.palette)}</linearGradient>
    <pattern id="data-land" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="9" height="9" fill="#f3f4f1"/><path d="M0 0V9" stroke="#aebbb7" stroke-width=".7" stroke-opacity=".16"/></pattern>
    <style>
      text {{ font-family:Inter,ui-sans-serif,system-ui,sans-serif; }}
      .state-lines {{ fill:none; stroke:#18383f; stroke-width:.34; stroke-opacity:.65; vector-effect:non-scaling-stroke; }}
      .region-casing {{ fill:none; stroke:#edf3ef; stroke-width:2.8; stroke-opacity:.82; vector-effect:non-scaling-stroke; }}
      .region-lines {{ fill:none; stroke:#304b51; stroke-width:.9; vector-effect:non-scaling-stroke; }}
      .realm-casing {{ fill:none; stroke:#edf3ef; stroke-width:4.4; stroke-opacity:.9; vector-effect:non-scaling-stroke; }}
      .realm-lines {{ fill:none; stroke:#09232a; stroke-width:1.7; vector-effect:non-scaling-stroke; }}
      .land {{ fill:url(#data-land); stroke:#899a96; stroke-width:.7; stroke-opacity:.5; vector-effect:non-scaling-stroke; }}
      .state-labels text {{ fill:#15353c; fill-opacity:.58; font:650 7.2px ui-monospace,Consolas,monospace; text-anchor:middle; paint-order:stroke; stroke:#f3f5f1; stroke-opacity:.72; stroke-width:1.7px; }}
      .region-labels text {{ fill:#102d34; font:950 9.5px ui-monospace,Consolas,monospace; letter-spacing:.9px; text-anchor:middle; paint-order:stroke; stroke:#f3f5f1; stroke-opacity:.94; stroke-width:2.7px; }}
      .legend text {{ fill:#9bb2b1; font:800 10px ui-monospace,Consolas,monospace; }}
    </style>
  </defs>
  <rect width="1200" height="1210" fill="#06171c"/>
  <text x="56" y="44" fill="#67e4da" font-size="14" font-weight="900" letter-spacing="2.5">OSW / OCEAN STATES DATA VIEW  ·  {html.escape(view.eyebrow)}</text>
  <text x="56" y="82" fill="#eef9f7" font-size="31" font-weight="950">{html.escape(view.title)}</text>
  <text x="56" y="108" fill="#8da9a9" font-size="11.5">{html.escape(source)} · {html.escape(str(observed_on))}</text>
  <rect x="898" y="31" width="246" height="27" rx="13.5" fill="#112d33" stroke="#67e4da" stroke-opacity=".6"/>
  <text x="1021" y="49" text-anchor="middle" fill="#67e4da" font-size="10" font-weight="950" letter-spacing="1.4">DATA PRIMARY · STATES REFERENCE</text>
  <text x="1144" y="83" text-anchor="end" fill="#ffb454" font-size="11" font-weight="900">{html.escape(view.field_label)}</text>
  <text x="1144" y="105" text-anchor="end" fill="#718d8f" font-size="9.5">{html.escape(range_label)}</text>
  <g aria-label="Polar data mirrors">
    <rect x="56" y="124" width="1088" height="150" rx="18" fill="#0d252b" stroke="#49666b"/>
    <text x="78" y="154" fill="#67e4da" font-size="11" font-weight="900" letter-spacing="1.4">POLAR MIRRORS · SAME FIELD · EQUAL-AREA TOP-DOWN</text>
    <text x="78" y="181" fill="#eef9f7" font-size="17" font-weight="850">The poles are data views, not decorative insets.</text>
    <text x="78" y="210" fill="#9bb2b1" font-size="10.5">North: 48°N–90°N · South: 45°S–90°S</text>
    <text x="78" y="233" fill="#718d8f" font-size="9.5">{html.escape(view.coverage_note)}</text>
    <g clip-path="url(#data-north-clip)"><rect x="778" y="137" width="126" height="126" fill="#10292f"/>{north_field}<path class="land" d="{north_land}" fill-rule="evenodd"/></g>
    <circle cx="841" cy="200" r="63" fill="none" stroke="#9ab0b0"/><text x="841" y="268" text-anchor="middle" fill="#8da9a9" font-size="8.5" font-weight="900">NORTH</text>
    <g clip-path="url(#data-south-clip)"><rect x="970" y="137" width="126" height="126" fill="#10292f"/>{south_field}<path class="land" d="{south_land}" fill-rule="evenodd"/></g>
    <circle cx="1033" cy="200" r="63" fill="none" stroke="#9ab0b0"/><text x="1033" y="268" text-anchor="middle" fill="#8da9a9" font-size="8.5" font-weight="900">SOUTH</text>
  </g>
  <g clip-path="url(#data-map-clip)">
    <rect x="56" y="296" width="1088" height="706" fill="#10292f"/>
    <g class="data-field">{data_field}</g>
    <path class="state-lines" data-state-count="56" d="{state_path}"/>
    <path class="region-casing" d="{region_path}"/><path class="region-lines" d="{region_path}"/>
    <path class="realm-casing" d="{realm_path}"/><path class="realm-lines" d="{realm_path}"/>
    <path class="land" d="{land_path}" fill-rule="evenodd"/>
    <g class="state-labels">{"".join(state_labels)}</g><g class="region-labels">{"".join(region_labels)}</g>
  </g>
  <rect x="56" y="296" width="1088" height="706" rx="20" fill="none" stroke="#49666b" stroke-width="1.5"/>
  <text x="56" y="1034" fill="#eef9f7" font-size="15" font-weight="850">{html.escape(view.field_label)}</text>
  <rect x="56" y="1050" width="720" height="30" rx="4" fill="url(#data-scale)"/>
  <g class="legend">{legend_ticks(view.palette)}</g>
  <g transform="translate(820 1050)" font-size="9.5" font-weight="800">
    <path d="M0 8H52" stroke="#edf3ef" stroke-width="4.4"/><path d="M0 8H52" stroke="#09232a" stroke-width="1.7"/><text x="63" y="12" fill="#b9cdca">REALM</text>
    <path d="M0 31H52" stroke="#edf3ef" stroke-width="2.8"/><path d="M0 31H52" stroke="#304b51" stroke-width=".9"/><text x="63" y="35" fill="#b9cdca">SCHEMATIC REGION</text>
    <path d="M0 54H52" stroke="#18383f" stroke-width=".34"/><text x="63" y="58" fill="#b9cdca">STATE</text>
  </g>
  <text x="56" y="1142" fill="#8da9a9" font-size="9.5">{html.escape(view.coverage_note)}</text>
  <text x="56" y="1165" fill="#718d8f" font-size="9.2">{html.escape(boundary)}</text>
  <text x="56" y="1190" fill="#617d80" font-size="9">DIRECT GRID PROJECTION · NO STATE AGGREGATION · PROVISIONAL OSW BORDERS · NOT HEAT CONTENT OR TRANSPORT</text>
</svg>'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--land-geojson", required=True, type=Path)
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[1] / "atlas" / "data")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "figures")
    args = parser.parse_args()

    land_payload = args.land_geojson.read_bytes()
    land_sha256 = hashlib.sha256(land_payload).hexdigest()
    if land_sha256 != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"Natural Earth source checksum mismatch: {land_sha256}")
    geojson = json.loads(land_payload)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for view in VIEWS:
        payload = load_javascript_payload(args.data_dir / view.filename)
        output = args.output_dir / f"osw-state-data-{view.slug}.svg"
        output.write_text(render_data_view(view, payload, geojson, land_sha256), encoding="utf-8", newline="\n")
        print(output)


if __name__ == "__main__":
    main()

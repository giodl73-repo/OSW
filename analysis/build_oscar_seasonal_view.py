"""Render four matched seasonal OSCAR surface-motion panels."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from collections import defaultdict
from pathlib import Path

from build_oscar_motion_view import MOLLWEIDE, SPEED_CLASSES, normalize_longitude, speed_class
from build_oscar_persistence_view import PERSISTENCE_BANDS, persistence_band
from build_projection_bakeoff import (
    EXPECTED_SOURCE_SHA256, SOURCE_COMMIT, all_rings, projected_polygon_fill,
    pyproj_projector, raw_bounds, screen_transform,
)


CANVAS = (1400, 1050)
PANELS = {
    "DJF": (38.0, 145.0, 650.0, 370.0),
    "MAM": (712.0, 145.0, 650.0, 370.0),
    "JJA": (38.0, 535.0, 650.0, 370.0),
    "SON": (712.0, 535.0, 650.0, 370.0),
}
SEASON_CONTEXT = {
    "DJF": "NORTHERN WINTER · SOUTHERN SUMMER",
    "MAM": "BOREAL SPRING · AUSTRAL AUTUMN",
    "JJA": "NORTHERN SUMMER · SOUTHERN WINTER",
    "SON": "BOREAL AUTUMN · AUSTRAL SPRING",
}


def load_payload(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    payload = json.loads(text.split("=", 1)[1].strip().removesuffix(";"))
    rows, columns = payload["shape"]
    for season in payload["season_order"]:
        for field in ("mean_u_mm_s", "mean_v_mm_s", "mean_instantaneous_speed_mm_s", "directional_persistence_thousandths"):
            if len(payload["seasons"][season][field]) != rows * columns:
                raise ValueError(f"seasonal grid shape mismatch: {season} {field}")
    return payload


def vector_layers(payload: dict, season: str, project, screen) -> tuple[str, int]:
    data = payload["seasons"][season]
    rows, columns = payload["shape"]
    grouped: dict[tuple[int, int], list[str]] = defaultdict(list)
    count = 0
    for row, latitude in enumerate(payload["latitude_values"]):
        if abs(latitude) > 79.9:
            continue
        cosine = max(0.2, math.cos(math.radians(latitude)))
        for column, longitude_source in enumerate(payload["longitude_values"]):
            index = row * columns + column
            values = (
                data["mean_u_mm_s"][index], data["mean_v_mm_s"][index],
                data["mean_instantaneous_speed_mm_s"][index],
                data["directional_persistence_thousandths"][index],
            )
            if any(value is None for value in values):
                continue
            u, v, mean_speed, persistence = values[0] / 1000, values[1] / 1000, values[2] / 1000, values[3] / 1000
            resultant = math.hypot(u, v)
            if resultant < 0.008:
                continue
            longitude = normalize_longitude(longitude_source)
            angular_length = 1.1 + min(mean_speed, 1.5) * 4.2
            end_latitude = latitude + v / resultant * angular_length
            end_longitude = normalize_longitude(longitude + u / resultant * angular_length / cosine)
            if abs(end_latitude) >= 89 or abs(end_longitude - longitude) > 40:
                continue
            try:
                start = screen(project(longitude, latitude))
                end = screen(project(end_longitude, end_latitude))
            except Exception:
                continue
            distance = math.hypot(end[0] - start[0], end[1] - start[1])
            if not math.isfinite(distance) or distance < .7 or distance > 18:
                continue
            speed_bucket, _ = speed_class(mean_speed)
            band = persistence_band(persistence)
            grouped[(speed_bucket, band)].append(f"M{start[0]:.1f},{start[1]:.1f}L{end[0]:.1f},{end[1]:.1f}")
            count += 1
    layers = []
    for (speed_bucket, band), commands in sorted(grouped.items()):
        color = SPEED_CLASSES[speed_bucket][1]
        _, opacity, width, _ = PERSISTENCE_BANDS[band]
        layers.append(
            f'<path d="{"".join(commands)}" fill="none" stroke="{color}" stroke-width="{max(.7, width * .8):.2f}" '
            f'opacity="{opacity}" marker-end="url(#arrow-{speed_bucket})"/>'
        )
    return "".join(layers), count


def panel(payload: dict, season: str, geojson: dict, project, bounds) -> tuple[str, int]:
    x, y, width, height = PANELS[season]
    map_box = (x + 12, y + 50, width - 24, height - 65)
    screen = screen_transform(bounds, box=map_box)
    land = "".join(
        projected_polygon_fill(ring, MOLLWEIDE, project, bounds, screen)
        for ring in all_rings(geojson)
    )
    vectors, count = vector_layers(payload, season, project, screen)
    data = payload["seasons"][season]
    return f'''<g aria-label="{season} surface motion">
    <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="18" fill="#0b252c" stroke="#49666b"/>
    <text x="{x + 18}" y="{y + 28}" fill="#eef9f7" font-size="19" font-weight="950">{season} · {html.escape(data['name'].upper())}</text>
    <text x="{x + width - 18}" y="{y + 27}" text-anchor="end" fill="#7e9b9d" font-size="8.5" font-weight="850">{SEASON_CONTEXT[season]}</text>
    <g>{vectors}<path d="{land}" fill="url(#quiet-land)" fill-rule="evenodd"/></g>
    <text x="{x + 18}" y="{y + height - 10}" fill="#617d80" font-size="8">{len(data['sample_times'])} FIVE-DAY FIELDS · MIN {data['minimum_samples']} VALID/CELL · {count} VECTORS</text>
  </g>''', count


def legends() -> str:
    speed_items = []
    for index, (_, color, label) in enumerate(SPEED_CLASSES):
        x = 48 + index * 128
        speed_items.append(
            f'<path d="M{x} 954H{x + 31}" stroke="{color}" stroke-width="2" marker-end="url(#arrow-{index})"/>'
            f'<text x="{x + 40}" y="958">{label}</text>'
        )
    persistence_items = []
    for index, (_, opacity, width, label) in enumerate(PERSISTENCE_BANDS):
        x = 790 + index * 177
        persistence_items.append(
            f'<path d="M{x} 954H{x + 31}" stroke="#62d7ce" stroke-width="{width + .5}" opacity="{opacity}"/>'
            f'<text x="{x + 40}" y="958">{html.escape(label)}</text>'
        )
    return "".join(speed_items + persistence_items)


def render(payload: dict, geojson: dict, land_sha256: str) -> str:
    project = pyproj_projector(MOLLWEIDE.proj4)
    bounds = raw_bounds(project)
    panels = []
    counts = []
    for season in payload["season_order"]:
        rendered, count = panel(payload, season, geojson, project, bounds)
        panels.append(rendered); counts.append(f"{season}:{count}")
    markers = "".join(
        f'<marker id="arrow-{index}" viewBox="0 0 4 4" refX="3.4" refY="2" markerWidth="3" markerHeight="3" orient="auto"><path d="M0 0L4 2L0 4Z" fill="{color}"/></marker>'
        for index, (_, color, _) in enumerate(SPEED_CLASSES)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1050" viewBox="0 0 1400 1050" role="img" aria-labelledby="title desc" data-motion-level="seasonal-persistence" data-zoning="off">
  <title id="title">Surface motion changes with the seasons</title>
  <desc id="desc">Four matched Oceanic Mollweide panels show seasonal mean historical OSCAR surface-current direction, speed, and directional persistence across one meteorological year. {html.escape(payload['boundary'])}</desc>
  <metadata>Source: {html.escape(payload['source'])}. Source SHA-256: {payload['source_sha256']}. Query: {html.escape(payload['query_url'])}. Diagnostic: {html.escape(payload['diagnostic_definition'])}. Natural Earth commit {SOURCE_COMMIT}, SHA-256 {land_sha256}. Vector counts: {', '.join(counts)}. No OSW zones are drawn.</metadata>
  <defs>{markers}<pattern id="quiet-land" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="8" height="8" fill="#f7f7f4"/><path d="M0 0V8" stroke="#526d70" stroke-width=".5" stroke-opacity=".12"/></pattern><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.legend text{{fill:#a9bfbe;font:800 8.5px ui-monospace,Consolas,monospace}}</style></defs>
  <rect width="1400" height="1050" fill="#06171c"/>
  <text x="38" y="42" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.5">OSW / MOTION STUDY  ·  M1 SEASONAL PILOT</text>
  <text x="38" y="84" fill="#eef9f7" font-size="32" font-weight="950">SURFACE MOTION CHANGES WITH THE SEASONS</text>
  <text x="38" y="113" fill="#9db3b2" font-size="11.5">71 historical five-day fields · December 2017–November 2018 · four matched views · zoning off</text>
  <rect x="1133" y="34" width="229" height="30" rx="15" fill="#102a30" stroke="#f0cf70" stroke-opacity=".65"/>
  <text x="1247.5" y="54" text-anchor="middle" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.3">ZONING OFF · SEASON TEST</text>
  {''.join(panels)}
  <g class="legend"><text x="38" y="925" fill="#edf8f6" font-size="10.5" font-weight="900">MEAN SAMPLED SPEED · m s⁻¹</text><text x="790" y="925" fill="#edf8f6" font-size="10.5" font-weight="900">WITHIN-SEASON DIRECTIONAL PERSISTENCE</text>{legends()}</g>
  <text x="38" y="1000" fill="#62d7ce" font-size="9.5" font-weight="950">READ</text><text x="82" y="1000" fill="#afc3c1" font-size="10">seasonal shifts, reversals, and persistent corridors</text>
  <text x="500" y="1000" fill="#f0cf70" font-size="9.5" font-weight="950">DO NOT READ</text><text x="600" y="1000" fill="#afc3c1" font-size="10">climatology · permanent borders · deep flow · heat transport</text>
  <text x="38" y="1030" fill="#617d80" font-size="8.5">ONE HISTORICAL METEOROLOGICAL YEAR · OLDER OSCAR VERSION 2017.0 · NOMINAL 15 m · PRODUCTION STUDY REQUIRES MULTIYEAR OSCAR V2.0</text>
</svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--land-geojson", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    land_raw = args.land_geojson.read_bytes()
    land_sha256 = hashlib.sha256(land_raw).hexdigest()
    if land_sha256 != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"Natural Earth source checksum mismatch: {land_sha256}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(load_payload(args.data), json.loads(land_raw), land_sha256), encoding="utf-8", newline="\n")
    print(args.output)


if __name__ == "__main__":
    main()


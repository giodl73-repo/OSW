"""Render cross-season directional agreement and maximum seasonal turning."""

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


CANVAS = (1400, 790)
LEFT_PANEL = (38.0, 145.0, 650.0, 450.0)
RIGHT_PANEL = (712.0, 145.0, 650.0, 450.0)
TURN_PALETTE = (
    (0.0, (65, 207, 194)), (45.0, (139, 213, 161)),
    (90.0, (240, 207, 112)), (135.0, (244, 144, 91)),
    (180.0, (226, 80, 126)),
)


def load_payload(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    payload = json.loads(text.split("=", 1)[1].strip().removesuffix(";"))
    cells = payload["shape"][0] * payload["shape"][1]
    for field in (
        "mean_u_mm_s", "mean_v_mm_s", "mean_speed_mm_s",
        "cross_season_alignment_thousandths",
        "maximum_seasonal_turn_degrees_tenths",
        "mean_within_season_persistence_thousandths",
    ):
        if len(payload[field]) != cells:
            raise ValueError(f"agreement grid shape mismatch: {field}")
    return payload


def turn_color(angle: float) -> str:
    bounded = max(0.0, min(180.0, angle))
    upper = next(index for index, stop in enumerate(TURN_PALETTE) if stop[0] >= bounded)
    if upper == 0:
        color = TURN_PALETTE[0][1]
    else:
        low_value, low_color = TURN_PALETTE[upper - 1]
        high_value, high_color = TURN_PALETTE[upper]
        fraction = (bounded - low_value) / (high_value - low_value)
        color = tuple(round(low + (high - low) * fraction) for low, high in zip(low_color, high_color))
    return "#" + "".join(f"{channel:02x}" for channel in color)


def projected_context(geojson: dict, project, bounds, panel_box):
    x, y, width, height = panel_box
    map_box = (x + 12, y + 58, width - 24, height - 78)
    screen = screen_transform(bounds, box=map_box)
    land = "".join(
        projected_polygon_fill(ring, MOLLWEIDE, project, bounds, screen)
        for ring in all_rings(geojson)
    )
    return screen, land


def agreement_vectors(payload: dict, project, screen) -> tuple[str, int]:
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
                payload["mean_u_mm_s"][index], payload["mean_v_mm_s"][index],
                payload["mean_speed_mm_s"][index], payload["cross_season_alignment_thousandths"][index],
            )
            if any(value is None for value in values):
                continue
            u, v, speed, alignment = values[0] / 1000, values[1] / 1000, values[2] / 1000, values[3] / 1000
            resultant = math.hypot(u, v)
            if resultant < 0.008:
                continue
            longitude = normalize_longitude(longitude_source)
            angular_length = 1.1 + min(speed, 1.5) * 4.2
            end_latitude = latitude + v / resultant * angular_length
            end_longitude = normalize_longitude(longitude + u / resultant * angular_length / cosine)
            if abs(end_latitude) >= 89 or abs(end_longitude - longitude) > 40:
                continue
            start = screen(project(longitude, latitude)); end = screen(project(end_longitude, end_latitude))
            distance = math.hypot(end[0] - start[0], end[1] - start[1])
            if not math.isfinite(distance) or distance < .7 or distance > 18:
                continue
            speed_bucket, _ = speed_class(speed)
            band = persistence_band(alignment)
            grouped[(speed_bucket, band)].append(f"M{start[0]:.1f},{start[1]:.1f}L{end[0]:.1f},{end[1]:.1f}")
            count += 1
    paths = []
    for (speed_bucket, band), commands in sorted(grouped.items()):
        color = SPEED_CLASSES[speed_bucket][1]
        _, opacity, width, _ = PERSISTENCE_BANDS[band]
        paths.append(
            f'<path d="{"".join(commands)}" fill="none" stroke="{color}" stroke-width="{max(.7, width * .8):.2f}" '
            f'opacity="{opacity}" marker-end="url(#arrow-{speed_bucket})"/>'
        )
    return "".join(paths), count


def turning_points(payload: dict, project, screen) -> tuple[str, int]:
    rows, columns = payload["shape"]
    circles = []
    count = 0
    for row, latitude in enumerate(payload["latitude_values"]):
        for column, longitude_source in enumerate(payload["longitude_values"]):
            index = row * columns + column
            turn = payload["maximum_seasonal_turn_degrees_tenths"][index]
            speed = payload["mean_speed_mm_s"][index]
            within = payload["mean_within_season_persistence_thousandths"][index]
            if turn is None or speed is None or within is None:
                continue
            x, y = screen(project(normalize_longitude(longitude_source), latitude))
            if not math.isfinite(x) or not math.isfinite(y):
                continue
            radius = 1.25 + min(speed / 1000, 1.5) * 1.8
            opacity = 0.25 + 0.75 * within / 1000
            circles.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.2f}" fill="{turn_color(turn / 10)}" opacity="{opacity:.2f}"/>'
            )
            count += 1
    return "".join(circles), count


def legends() -> str:
    speed_items = []
    for index, (_, color, label) in enumerate(SPEED_CLASSES):
        x = 48 + index * 126
        speed_items.append(
            f'<path d="M{x} 679H{x + 30}" stroke="{color}" stroke-width="2" marker-end="url(#arrow-{index})"/>'
            f'<text x="{x + 39}" y="683">{label}</text>'
        )
    turn_items = []
    for angle, _ in TURN_PALETTE:
        x = 754 + angle / 180 * 570
        turn_items.append(f'<circle cx="{x:.1f}" cy="679" r="3" fill="{turn_color(angle)}"/><text x="{x:.1f}" y="698" text-anchor="middle">{angle:g}°</text>')
    return "".join(speed_items + turn_items)


def render(payload: dict, geojson: dict, land_sha256: str) -> str:
    project = pyproj_projector(MOLLWEIDE.proj4)
    bounds = raw_bounds(project)
    left_screen, left_land = projected_context(geojson, project, bounds, LEFT_PANEL)
    right_screen, right_land = projected_context(geojson, project, bounds, RIGHT_PANEL)
    arrows, arrow_count = agreement_vectors(payload, project, left_screen)
    points, point_count = turning_points(payload, project, right_screen)
    markers = "".join(
        f'<marker id="arrow-{index}" viewBox="0 0 4 4" refX="3.4" refY="2" markerWidth="3" markerHeight="3" orient="auto"><path d="M0 0L4 2L0 4Z" fill="{color}"/></marker>'
        for index, (_, color, _) in enumerate(SPEED_CLASSES)
    )
    summary = payload["summary"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="790" viewBox="0 0 1400 790" role="img" aria-labelledby="title desc" data-motion-level="cross-season-agreement" data-zoning="off">
  <title id="title">What surface motion holds and what turns</title>
  <desc id="desc">Two matched zoning-free Oceanic Mollweide panels show cross-season directional agreement and maximum seasonal turning derived from four seasonal OSCAR means. {html.escape(payload['boundary'])}</desc>
  <metadata>Source data SHA-256: {payload['source_data_sha256']}. Source artifact SHA-256: {payload['source_artifact_sha256']}. Cross-season alignment: {html.escape(payload['diagnostics']['cross_season_alignment'])}. Maximum turn: {html.escape(payload['diagnostics']['maximum_seasonal_turn'])}. Natural Earth commit {SOURCE_COMMIT}, SHA-256 {land_sha256}. Rendered arrows: {arrow_count}; turning points: {point_count}. No OSW zones are drawn.</metadata>
  <defs>{markers}<pattern id="quiet-land" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="8" height="8" fill="#f7f7f4"/><path d="M0 0V8" stroke="#526d70" stroke-width=".5" stroke-opacity=".12"/></pattern><linearGradient id="turn-scale" x1="0" x2="1">{''.join(f'<stop offset="{angle / 1.8:.2f}%" stop-color="{turn_color(angle)}"/>' for angle, _ in TURN_PALETTE)}</linearGradient><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.legend text{{fill:#a9bfbe;font:800 8.5px ui-monospace,Consolas,monospace}}</style></defs>
  <rect width="1400" height="790" fill="#06171c"/>
  <text x="38" y="42" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.5">OSW / MOTION STUDY  ·  M1 CROSS-SEASON SKELETON</text>
  <text x="38" y="84" fill="#eef9f7" font-size="32" font-weight="950">WHAT HOLDS / WHAT TURNS</text>
  <text x="38" y="113" fill="#9db3b2" font-size="11.5">four seasonal mean directions · one historical year · continuous diagnostics · zoning off</text>
  <rect x="1133" y="34" width="229" height="30" rx="15" fill="#102a30" stroke="#f0cf70" stroke-opacity=".65"/>
  <text x="1247.5" y="54" text-anchor="middle" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.3">ZONING OFF · SKELETON TEST</text>
  <g aria-label="Cross-season agreement"><rect x="38" y="145" width="650" height="450" rx="18" fill="#0b252c" stroke="#49666b"/><text x="56" y="179" fill="#eef9f7" font-size="20" font-weight="950">WHAT HOLDS</text><text x="670" y="178" text-anchor="end" fill="#7e9b9d" font-size="8.5" font-weight="850">OPACITY · CROSS-SEASON ALIGNMENT</text>{arrows}<path d="{left_land}" fill="url(#quiet-land)" fill-rule="evenodd"/><text x="56" y="578" fill="#617d80" font-size="8">{arrow_count} MEAN-DIRECTION GLYPHS · COLOR IS MEAN SPEED · OPACITY IS 0–1 AGREEMENT</text></g>
  <g aria-label="Maximum seasonal turning"><rect x="712" y="145" width="650" height="450" rx="18" fill="#0b252c" stroke="#49666b"/><text x="730" y="179" fill="#eef9f7" font-size="20" font-weight="950">WHAT TURNS</text><text x="1344" y="178" text-anchor="end" fill="#7e9b9d" font-size="8.5" font-weight="850">COLOR · MAXIMUM PAIRWISE SEASONAL ANGLE</text>{points}<path d="{right_land}" fill="url(#quiet-land)" fill-rule="evenodd"/><text x="730" y="578" fill="#617d80" font-size="8">{point_count} SUPPORTED CELLS · DOT SIZE IS MEAN SPEED · OPACITY IS WITHIN-SEASON PERSISTENCE</text></g>
  <g class="legend"><text x="38" y="645" fill="#edf8f6" font-size="10.5" font-weight="900">MEAN SPEED · m s⁻¹ / ALIGNMENT FADES</text><text x="712" y="645" fill="#edf8f6" font-size="10.5" font-weight="900">MAXIMUM SEASONAL TURN · degrees</text>{legends()}<rect x="754" y="712" width="570" height="8" rx="4" fill="url(#turn-scale)"/></g>
  <text x="38" y="749" fill="#62d7ce" font-size="9.5" font-weight="950">DIAGNOSTIC COUNTS</text><text x="155" y="749" fill="#afc3c1" font-size="10">{summary['aligned_candidate_cells']} aligned candidates · {summary['turning_candidate_cells']} turning candidates · {summary['diffuse_or_other_cells']} diffuse/other · thresholds declared, not natural kinds</text>
  <text x="38" y="776" fill="#617d80" font-size="8.5">ONE HISTORICAL YEAR · OLDER OSCAR 2017.0 · NOT CLIMATOLOGY, LAGRANGIAN COHERENCE, FULL-DEPTH FLOW, OR HEAT TRANSPORT</text>
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


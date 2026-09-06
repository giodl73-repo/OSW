"""Render whether a motion-partition count survives reasonable method changes."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from collections import Counter
from pathlib import Path

from build_oscar_motion_view import MOLLWEIDE, normalize_longitude
from build_projection_bakeoff import (
    EXPECTED_SOURCE_SHA256, SOURCE_COMMIT, all_rings, projected_polygon_fill,
    pyproj_projector, raw_bounds, screen_transform,
)


COMPONENT_COLORS = ("#62d7ce", "#f0cf70", "#f49a62", "#e76f9f", "#8cc4ff", "#a7d77b", "#c5a4ed", "#efb572", "#56b4a6", "#d98f8f", "#9dbbdb", "#bdd47b")
CURVE_COLORS = {"4N_ALL": "#62d7ce", "8N_ALL": "#f0cf70", "4N_NO_DJF": "#e76f9f", "4N_NO_MAM": "#f49a62", "4N_NO_JJA": "#8cc4ff", "4N_NO_SON": "#a7d77b"}


def configuration(payload: dict, code: str) -> dict:
    return next(item for item in payload["configurations"] if item["code"] == code)


def map_points(payload: dict, config: dict, threshold: str, project, screen) -> str:
    assignments = config["assignments"][threshold]
    sizes = Counter(value for value in assignments if value is not None)
    columns = payload["shape"][1]
    circles = []
    for index, component in enumerate(assignments):
        if component is None:
            continue
        row, column = divmod(index, columns)
        x, y = screen(project(normalize_longitude(payload["longitude_values"][column]), payload["latitude_values"][row]))
        if not math.isfinite(x) or not math.isfinite(y):
            continue
        large = sizes[component] >= 5
        circles.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{2.2 if large else 1.15}" fill="{COMPONENT_COLORS[component % len(COMPONENT_COLORS)] if large else "#49666b"}" opacity="{.86 if large else .30}"/>')
    return "".join(circles)


def chart(payload: dict) -> str:
    x0, y0, width, height = 74.0, 555.0, 842.0, 205.0
    x = lambda value: x0 + value / .9 * width
    y = lambda value: y0 + height - value / 30 * height
    grid = []
    for count in range(0, 31, 5):
        yy = y(count)
        grid.append(f'<path d="M{x0} {yy:.1f}H{x0 + width}" stroke="#345157" stroke-width=".6"/><text x="{x0 - 12}" y="{yy + 3:.1f}" class="axis" text-anchor="end">{count}</text>')
    for threshold in [index / 10 for index in range(10)]:
        xx = x(threshold)
        grid.append(f'<text x="{xx:.1f}" y="{y0 + height + 20}" class="axis" text-anchor="middle">{threshold:.1f}</text>')
    curves = []
    for config in payload["configurations"]:
        path = " ".join(f'{"M" if index == 0 else "L"}{x(item["direction_similarity_threshold"]):.1f},{y(item["components_at_least_5_cells"]):.1f}' for index, item in enumerate(config["results"]))
        primary = config["code"] in ("4N_ALL", "8N_ALL")
        curves.append(f'<path d="{path}" fill="none" stroke="{CURVE_COLORS[config["code"]]}" stroke-width="{2.8 if primary else 1.2}" opacity="{1 if primary else .58}"/>')
    marker_x = x(.3)
    return f'''<g aria-label="Robustness curves">{''.join(grid)}<path d="M{marker_x:.1f} {y0}V{y0 + height}" stroke="#eef9f7" stroke-width="1" stroke-dasharray="3 4" opacity=".55"/>{''.join(curves)}<text x="{x0}" y="{y0 - 28}" fill="#eef9f7" font-size="17" font-weight="950">COUNT ACROSS THRESHOLDS</text><text x="{x0}" y="{y0 - 8}" fill="#789596" font-size="8.5">COMPONENTS ≥5 CELLS · HEAVY LINES CHANGE NEIGHBORHOOD · THIN LINES OMIT ONE SEASON</text><text x="{x0}" y="{y0 + height + 46}" fill="#789596" font-size="9">MEAN INCLUDED-SEASON NEIGHBOR DIRECTION SIMILARITY THRESHOLD</text></g>'''


def render(payload: dict, geojson: dict, land_sha256: str) -> str:
    project = pyproj_projector(MOLLWEIDE.proj4)
    bounds = raw_bounds(project)
    panels = []
    for box, code in (((38.0, 160.0, 610.0, 315.0), "4N_ALL"), ((686.0, 160.0, 610.0, 315.0), "8N_ALL")):
        config = configuration(payload, code)
        screen = screen_transform(bounds, box=(box[0] + 10, box[1] + 50, box[2] - 20, box[3] - 68))
        points = map_points(payload, config, "0.30", project, screen)
        land = "".join(projected_polygon_fill(ring, MOLLWEIDE, project, bounds, screen) for ring in all_rings(geojson))
        result = next(item for item in config["results"] if item["direction_similarity_threshold"] == .3)
        panels.append(f'<g><rect x="{box[0]}" y="{box[1]}" width="{box[2]}" height="{box[3]}" rx="17" fill="#0b252c" stroke="#49666b"/><text x="{box[0] + 18}" y="{box[1] + 31}" fill="#eef9f7" font-size="17" font-weight="950">{html.escape(config["label"].upper())}</text><text x="{box[0] + box[2] - 18}" y="{box[1] + 31}" text-anchor="end" fill="{CURVE_COLORS[code]}" font-size="13" font-weight="950">{result["components_at_least_5_cells"]} COMPONENTS · {result["fraction_in_components_at_least_5"]:.0%} COVERAGE</text>{points}<path d="{land}" fill="#fafaf7" fill-rule="evenodd"/><text x="{box[0] + 18}" y="{box[1] + box[3] - 12}" fill="#617d80" font-size="8">SAME DATA · SAME 0.30 THRESHOLD · ONLY NEIGHBOR DEFINITION CHANGES</text></g>')
    baseline = configuration(payload, "4N_ALL")
    diagonal = configuration(payload, "8N_ALL")
    base_point = next(item for item in baseline["results"] if item["direction_similarity_threshold"] == .3)
    diagonal_point = next(item for item in diagonal["results"] if item["direction_similarity_threshold"] == .3)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900" role="img" aria-labelledby="title desc" data-motion-level="partition-robustness" data-zoning="off"><title id="title">The motion partition count does not survive the method</title><desc id="desc">Two matched maps show that changing four-neighbor connectivity to eight-neighbor connectivity changes the count from 20 to 9 at the same threshold. Curves compare both neighborhoods and four leave-one-season-out tests. No partition is proposed.</desc><metadata>Source artifact SHA-256 {payload['source_artifact_sha256']}; Natural Earth commit {SOURCE_COMMIT}, SHA-256 {land_sha256}. {html.escape(payload['boundary'])}</metadata><defs><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.axis{{fill:#789596;font:800 8px ui-monospace,Consolas,monospace}}</style></defs><rect width="1400" height="900" fill="#06171c"/><text x="38" y="42" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.5">OSW / MOTION STUDY  ·  M1 PARTITION ROBUSTNESS</text><text x="38" y="84" fill="#eef9f7" font-size="32" font-weight="950">THE COUNT DOES NOT SURVIVE THE METHOD</text><text x="38" y="113" fill="#9db3b2" font-size="11.5">same seasonal directions · same threshold · different reasonable graph topology</text><rect x="1128" y="34" width="234" height="30" rx="15" fill="#102a30" stroke="#f0cf70" stroke-opacity=".7"/><text x="1245" y="54" text-anchor="middle" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.3">ROBUSTNESS · NOT ZONING</text>{''.join(panels)}{chart(payload)}<g aria-label="Method verdict"><rect x="954" y="520" width="408" height="264" rx="16" fill="#0b252c" stroke="#49666b"/><text x="978" y="556" fill="#eef9f7" font-size="18" font-weight="950">ONE CHANGE, TWO COUNTS</text><text x="978" y="610" fill="#62d7ce" font-size="42" font-weight="950">{base_point['components_at_least_5_cells']}</text><text x="1032" y="608" fill="#a9bfbe" font-size="11">four-neighbor</text><text x="1152" y="610" fill="#f0cf70" font-size="42" font-weight="950">{diagonal_point['components_at_least_5_cells']}</text><text x="1196" y="608" fill="#a9bfbe" font-size="11">eight-neighbor</text><path d="M978 634H1338" stroke="#345157"/><text x="978" y="667" fill="#eef9f7" font-size="12" font-weight="900">SEASON REMOVAL: 20–21</text><text x="978" y="692" fill="#9db3b2" font-size="10">Graph topology dominates the leave-one-season-out change.</text><text x="978" y="716" fill="#9db3b2" font-size="10">Diagonal contact reconnects large swaths of the field.</text><text x="978" y="752" fill="#f0cf70" font-size="9.5" font-weight="900">THE COUNT IS A METHOD OUTPUT, NOT AN OCEAN FACT</text></g><text x="38" y="838" fill="#62d7ce" font-size="9.5" font-weight="950">READING</text><text x="102" y="838" fill="#afc3c1" font-size="10">component colors are panel-local · leave-one-season-out cases are sensitivity checks, not independent replicates</text><text x="38" y="866" fill="#617d80" font-size="8.5">ONE HISTORICAL YEAR · COARSE GRID · DIRECTION ONLY · COMPONENT MINIMUM 5 CELLS · NOT A CLIMATOLOGY, NATURAL PARTITION, OR OCEAN-STATE REVISION</text></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--land-geojson", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.data.read_text(encoding="utf-8"))
    raw_land = args.land_geojson.read_bytes()
    digest = hashlib.sha256(raw_land).hexdigest()
    if digest != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"Natural Earth source checksum mismatch: {digest}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(payload, json.loads(raw_land), digest), encoding="utf-8", newline="\n")
    print(args.output)


if __name__ == "__main__":
    main()

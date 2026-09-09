"""Render connected-motion partition sensitivity without proposing zones."""

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


MAP_BOXES = ((38.0, 168.0, 414.0, 250.0), (493.0, 168.0, 414.0, 250.0), (948.0, 168.0, 414.0, 250.0))
MAP_THRESHOLDS = ("0.10", "0.30", "0.70")
COLORS = ("#62d7ce", "#f0cf70", "#f49a62", "#e76f9f", "#8cc4ff", "#a7d77b", "#c5a4ed", "#efb572", "#56b4a6", "#d98f8f", "#9dbbdb", "#bdd47b")


def component_points(payload: dict, threshold: str, project, screen) -> tuple[str, int]:
    assignments = payload["assignments"][threshold]
    sizes = Counter(value for value in assignments if value is not None)
    circles = []
    colored = 0
    columns = payload["shape"][1]
    for index, component in enumerate(assignments):
        if component is None:
            continue
        row, column = divmod(index, columns)
        x, y = screen(project(normalize_longitude(payload["longitude_values"][column]), payload["latitude_values"][row]))
        if not math.isfinite(x) or not math.isfinite(y):
            continue
        if sizes[component] >= 5:
            fill, opacity, radius = COLORS[component % len(COLORS)], .86, 2.25
            colored += 1
        else:
            fill, opacity, radius = "#49666b", .34, 1.25
        circles.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{fill}" opacity="{opacity}"/>')
    return "".join(circles), colored


def chart(payload: dict) -> str:
    results = payload["results"]
    x0, y0, width, height = 76.0, 530.0, 820.0, 228.0
    x = lambda threshold: x0 + threshold / .9 * width
    y_count = lambda count: y0 + height - count / 25 * height
    y_coverage = lambda value: y0 + height - value * height
    grids = []
    for count in (0, 5, 10, 15, 20, 25):
        y = y_count(count)
        grids.append(f'<path d="M{x0} {y:.1f}H{x0 + width}" stroke="#345157" stroke-width=".6"/><text x="{x0 - 12}" y="{y + 3:.1f}" class="axis" text-anchor="end">{count}</text>')
    for threshold in (0, .1, .2, .3, .4, .5, .6, .7, .8, .9):
        xx = x(threshold)
        grids.append(f'<text x="{xx:.1f}" y="{y0 + height + 22}" class="axis" text-anchor="middle">{threshold:.1f}</text>')
    count_path = " ".join(f'{"M" if index == 0 else "L"}{x(item["direction_similarity_threshold"]):.1f},{y_count(item["components_at_least_5_cells"]):.1f}' for index, item in enumerate(results))
    coverage_path = " ".join(f'{"M" if index == 0 else "L"}{x(item["direction_similarity_threshold"]):.1f},{y_coverage(item["fraction_in_components_at_least_5"]):.1f}' for index, item in enumerate(results))
    dots = "".join(
        f'<circle cx="{x(item["direction_similarity_threshold"]):.1f}" cy="{y_count(item["components_at_least_5_cells"]):.1f}" r="3" fill="#62d7ce"/>'
        f'<circle cx="{x(item["direction_similarity_threshold"]):.1f}" cy="{y_coverage(item["fraction_in_components_at_least_5"]):.1f}" r="3" fill="#f0cf70"/>'
        for item in results
    )
    return f'''<g aria-label="Sensitivity curves">{''.join(grids)}<path d="{count_path}" fill="none" stroke="#62d7ce" stroke-width="2.5"/>{dots}<path d="{coverage_path}" fill="none" stroke="#f0cf70" stroke-width="2.5"/><text x="{x0}" y="{y0 - 22}" fill="#eef9f7" font-size="17" font-weight="950">NO STABLE NATURAL COUNT</text><text x="{x0}" y="{y0 - 5}" fill="#789596" font-size="8.5">CONNECTED COMPONENTS CHANGE WITH ONE DECLARED DIRECTION-SIMILARITY THRESHOLD</text><text x="{x0}" y="{y0 + height + 48}" fill="#789596" font-size="9">MEAN FOUR-SEASON NEIGHBOR DIRECTION SIMILARITY THRESHOLD</text><path d="M{650} {y0 - 18}H{678}" stroke="#62d7ce" stroke-width="2.5"/><text x="686" y="{y0 - 14}" fill="#a9bfbe" font-size="9">COMPONENTS ≥5 CELLS · LEFT AXIS</text><path d="M{650} {y0 + 2}H{678}" stroke="#f0cf70" stroke-width="2.5"/><text x="686" y="{y0 + 6}" fill="#a9bfbe" font-size="9">CELL COVERAGE · RIGHT AXIS</text><text x="{x0 + width + 12}" y="{y0 + 3}" class="axis">100%</text><text x="{x0 + width + 12}" y="{y0 + height + 3}" class="axis">0%</text></g>'''


def render(payload: dict, geojson: dict, land_sha256: str) -> str:
    project = pyproj_projector(MOLLWEIDE.proj4)
    bounds = raw_bounds(project)
    result_by_threshold = {f'{item["direction_similarity_threshold"]:.2f}': item for item in payload["results"]}
    panels = []
    for box, threshold in zip(MAP_BOXES, MAP_THRESHOLDS):
        screen = screen_transform(bounds, box=(box[0] + 8, box[1] + 44, box[2] - 16, box[3] - 58))
        points, colored = component_points(payload, threshold, project, screen)
        land = "".join(projected_polygon_fill(ring, MOLLWEIDE, project, bounds, screen) for ring in all_rings(geojson))
        result = result_by_threshold[threshold]
        panels.append(
            f'<g><rect x="{box[0]}" y="{box[1]}" width="{box[2]}" height="{box[3]}" rx="15" fill="#0b252c" stroke="#49666b"/>'
            f'<text x="{box[0] + 16}" y="{box[1] + 27}" fill="#eef9f7" font-size="14" font-weight="950">THRESHOLD {threshold}</text>'
            f'<text x="{box[0] + box[2] - 16}" y="{box[1] + 27}" text-anchor="end" fill="#9db3b2" font-size="9">{result["components_at_least_5_cells"]} COMPONENTS ≥5 · {result["fraction_in_components_at_least_5"]:.0%} COVERAGE</text>'
            f'{points}<path d="{land}" fill="#fafaf7" fill-rule="evenodd"/>'
            f'<text x="{box[0] + 16}" y="{box[1] + box[3] - 10}" fill="#617d80" font-size="7.5">{colored} CELLS IN COLORED COMPONENTS · SMALL FRAGMENTS GRAY</text></g>'
        )
    at_point_three = result_by_threshold["0.30"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900" role="img" aria-labelledby="title desc" data-motion-level="partition-sensitivity" data-zoning="off">
  <title id="title">Does seasonal surface motion prefer a natural number of regions?</title>
  <desc id="desc">Three zoning-free Oceanic Mollweide maps and a sensitivity curve show connected seasonal-direction components at changing similarity thresholds. Component count and coverage change sharply; this pilot does not identify a stable natural partition count.</desc>
  <metadata>Source artifact SHA-256 {payload['source_artifact_sha256']}; Natural Earth commit {SOURCE_COMMIT}, SHA-256 {land_sha256}; {payload['supported_cells']} supported cells and {payload['supported_neighbor_edges']} neighbor edges. {html.escape(payload['boundary'])}</metadata>
  <defs><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.axis{{fill:#789596;font:800 8px ui-monospace,Consolas,monospace}}</style></defs><rect width="1400" height="900" fill="#06171c"/>
  <text x="38" y="42" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.5">OSW / MOTION STUDY  ·  M1 PARTITION SENSITIVITY</text><text x="38" y="84" fill="#eef9f7" font-size="32" font-weight="950">DOES THE WATER CHOOSE A NUMBER?</text><text x="38" y="113" fill="#9db3b2" font-size="11.5">zoning off · connected neighbors by four-season directional agreement · threshold bakeoff</text><rect x="1128" y="34" width="234" height="30" rx="15" fill="#102a30" stroke="#f0cf70" stroke-opacity=".7"/><text x="1245" y="54" text-anchor="middle" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.3">SENSITIVITY · NOT ZONING</text>
  {''.join(panels)}{chart(payload)}
  <g aria-label="Interpretation"><rect x="948" y="492" width="414" height="292" rx="16" fill="#0b252c" stroke="#49666b"/><text x="972" y="528" fill="#eef9f7" font-size="18" font-weight="950">THE 20-REGION MIRAGE</text><text x="972" y="559" fill="#62d7ce" font-size="34" font-weight="950">{at_point_three['components_at_least_5_cells']}</text><text x="1022" y="558" fill="#a9bfbe" font-size="11">components ≥5 cells at threshold 0.30</text><text x="972" y="598" fill="#f0cf70" font-size="34" font-weight="950">{at_point_three['fraction_in_components_at_least_5']:.0%}</text><text x="1044" y="597" fill="#a9bfbe" font-size="11">of supported cells retained in them</text><path d="M972 622H1338" stroke="#345157"/><text x="972" y="654" fill="#eef9f7" font-size="12" font-weight="900">WHY THIS IS NOT A 20-REGION RESULT</text><text x="972" y="681" fill="#9db3b2" font-size="10">Change the threshold by 0.10 and the count changes.</text><text x="972" y="702" fill="#9db3b2" font-size="10">Forty percent of cells are already in smaller fragments.</text><text x="972" y="723" fill="#9db3b2" font-size="10">Direction alone ignores speed, depth, exchange, and heat.</text><text x="972" y="756" fill="#f0cf70" font-size="9.5" font-weight="900">NO PLATEAU · NO PRIVILEGED COUNT · NO REDRAW</text></g>
  <text x="38" y="838" fill="#62d7ce" font-size="9.5" font-weight="950">READING</text><text x="102" y="838" fill="#afc3c1" font-size="10">color identifies connected components only within each panel · colors do not correspond between thresholds</text><text x="38" y="866" fill="#617d80" font-size="8.5">ONE HISTORICAL YEAR · FOUR SEASONAL MEANS · 4-NEIGHBOR COARSE GRID · DIRECTION ONLY · NOT A CLIMATOLOGY, LAGRANGIAN PARTITION, OR OCEAN-STATE REVISION</text>
</svg>'''


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

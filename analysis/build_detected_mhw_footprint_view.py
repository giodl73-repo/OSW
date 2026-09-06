"""Render OSW-D2's native-grid connected marine-heatwave footprint."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "research" / "osw-d2-noaa-crw-mhw-footprint-20260801.json"
DEFAULT_OUTPUT = ROOT / "figures" / "osw-d2-noaa-crw-mhw-footprint-20260801.svg"
COLORS = {1: "#ffc857", 2: "#f47a37", 3: "#c93c3c", 4: "#681c33", 5: "#28111e"}


def build(input_path=DEFAULT_INPUT, output_path=DEFAULT_OUTPUT):
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    rows = payload["component_rows"]
    summary = payload["summary"]
    west, east = summary["bounds_cell_centers"]["west"] - 0.45, summary["bounds_cell_centers"]["east"] + 0.45
    south, north = summary["bounds_cell_centers"]["south"] - 0.45, summary["bounds_cell_centers"]["north"] + 0.45
    map_x, map_y, map_w, map_h = 72, 212, 730, 472
    cosine = math.cos(math.radians((south + north) / 2))
    scale = min(map_w / ((east - west) * cosine), map_h / (north - south))
    used_w, used_h = (east - west) * cosine * scale, (north - south) * scale
    origin_x, origin_y = map_x + (map_w - used_w) / 2, map_y + (map_h - used_h) / 2

    def xy(longitude, latitude):
        return origin_x + (longitude - west) * cosine * scale, origin_y + (north - latitude) * scale

    cells = []
    component = set()
    for latitude, runs in rows:
        for run_west, run_east, category in runs:
            x, y = xy(run_west - 0.025, latitude + 0.025)
            x2, y2 = xy(run_east + 0.025, latitude - 0.025)
            cells.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{x2-x:.2f}" height="{y2-y:.2f}" fill="{COLORS[category]}"/>')
            count = round((run_east - run_west) / 0.05) + 1
            for index in range(count):
                component.add((round(latitude, 3), round(run_west + index * 0.05, 3)))
    edges = []
    for latitude, longitude in component:
        x1, y1 = xy(longitude - 0.025, latitude + 0.025)
        x2, y2 = xy(longitude + 0.025, latitude - 0.025)
        if (round(latitude + 0.05, 3), longitude) not in component:
            edges.append(f'M{x1:.2f},{y1:.2f}H{x2:.2f}')
        if (round(latitude - 0.05, 3), longitude) not in component:
            edges.append(f'M{x1:.2f},{y2:.2f}H{x2:.2f}')
        if (latitude, round(longitude - 0.05, 3)) not in component:
            edges.append(f'M{x1:.2f},{y1:.2f}V{y2:.2f}')
        if (latitude, round(longitude + 0.05, 3)) not in component:
            edges.append(f'M{x2:.2f},{y1:.2f}V{y2:.2f}')
    grid = []
    for longitude in range(math.ceil(west), math.floor(east) + 1):
        x, _ = xy(longitude, south)
        grid.append(f'<path d="M{x:.2f},{origin_y:.2f}V{origin_y+used_h:.2f}"/><text x="{x:.2f}" y="{origin_y+used_h+23:.2f}" class="axis" text-anchor="middle">{abs(longitude)}°W</text>')
    for latitude in range(math.ceil(south), math.floor(north) + 1):
        _, y = xy(west, latitude)
        grid.append(f'<path d="M{origin_x:.2f},{y:.2f}H{origin_x+used_w:.2f}"/><text x="{origin_x-12:.2f}" y="{y+4:.2f}" class="axis" text-anchor="end">{latitude}°N</text>')
    anchor = payload["anchor_coordinate"]
    anchor_x, anchor_y = xy(anchor["longitude_degrees_east"], anchor["latitude_degrees_north"])
    centroid = summary["centroid"]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="760" viewBox="0 0 1200 760" role="img">
<title>OSW-D2 connected North Atlantic marine heatwave footprint</title>
<desc>An irregular 41,025 square kilometre connected footprint of 1,769 active NOAA Coral Reef Watch pixels on August 1, 2026. Moderate and strong categories are shown.</desc>
<style>
 .eyebrow{{font:700 15px Inter,"Segoe UI",sans-serif;letter-spacing:2.3px;fill:#327184}} .title{{font:700 42px Georgia,serif;fill:#112c38}} .lead{{font:400 18px Inter,"Segoe UI",sans-serif;fill:#425d67}} .axis{{font:500 11px Inter,"Segoe UI",sans-serif;fill:#6f8288}} .label{{font:650 14px Inter,"Segoe UI",sans-serif;fill:#173946}} .metric{{font:700 34px Georgia,serif;fill:#112c38}} .metriclabel{{font:600 12px Inter,"Segoe UI",sans-serif;letter-spacing:1px;fill:#60747d}} .body{{font:400 14px Inter,"Segoe UI",sans-serif;fill:#536a74}}
</style>
<rect width="1200" height="760" fill="#f8fbfa"/><path d="M0 0H1200V12H0Z" fill="#1f7085"/>
<text x="72" y="67" class="eyebrow">OSW · DETECTED OBJECT 02 · DAILY FOOTPRINT</text>
<text x="72" y="122" class="title">The point becomes a place</text>
<text x="72" y="157" class="lead">Connected marine-heatwave pixels · open North Atlantic · 01 August 2026</text>
<rect x="{origin_x:.2f}" y="{origin_y:.2f}" width="{used_w:.2f}" height="{used_h:.2f}" fill="#edf5f6" stroke="#adc4ca"/>
<g fill="none" stroke="#c9dadd" stroke-width="0.7">{''.join(grid)}</g>
<g>{''.join(cells)}</g><path d="{''.join(edges)}" fill="none" stroke="#843b2f" stroke-width="1.15" stroke-linecap="square"/>
<circle cx="{anchor_x:.2f}" cy="{anchor_y:.2f}" r="5.5" fill="#f8fbfa" stroke="#143844" stroke-width="2"/><path d="M{anchor_x:.2f},{anchor_y-13:.2f}V{anchor_y-7:.2f}" stroke="#143844" stroke-width="1.5"/>
<text x="{anchor_x+10:.2f}" y="{anchor_y-9:.2f}" class="label">OSW-D1 anchor</text>
<g transform="translate(864 238)">
 <text class="metric">{summary['area_km2']:,.0f}</text><text y="28" x="145" class="metriclabel">KM²</text><text y="51" class="metriclabel">SPHERICAL CELL AREA</text>
 <line y1="76" x2="270" y2="76" stroke="#cadadc"/>
 <text y="122" class="metric">{summary['pixel_count']:,}</text><text y="151" class="metriclabel">CONNECTED 0.05° PIXELS</text>
 <line y1="177" x2="270" y2="177" stroke="#cadadc"/>
 <text y="220" class="metric">{summary['maximum_category']}</text><text y="247" class="metriclabel">MAXIMUM · STRONG</text>
 <line y1="273" x2="270" y2="273" stroke="#cadadc"/>
 <text y="307" class="label">CENTROID</text><text y="332" class="body">{centroid['latitude_degrees_north']:.3f}°N · {abs(centroid['longitude_degrees_east']):.3f}°W</text>
 <rect y="365" width="18" height="18" rx="3" fill="{COLORS[1]}"/><text x="27" y="379" class="body">moderate · {summary['category_pixel_counts']['1']} px</text>
 <rect y="395" width="18" height="18" rx="3" fill="{COLORS[2]}"/><text x="27" y="409" class="body">strong · {summary['category_pixel_counts']['2']} px</text>
</g>
<text x="72" y="728" class="body">Native-grid, four-neighbor connectivity containing the duration-qualified anchor. Daily surface footprint—not yet a tracked volume, heat inventory, transport, cause, or impact.</text>
</svg>'''
    Path(output_path).write_text(svg, encoding="utf-8", newline="\n")
    return svg


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build(args.input, args.output)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

"""Render six exact snapshots and diagnostics for OSW-D3's footprint lineage."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "research" / "osw-d3-noaa-crw-mhw-lineage-2026.json"
DEFAULT_OUTPUT = ROOT / "figures" / "osw-d3-noaa-crw-mhw-lineage-2026.svg"
COLORS = {1: "#ffc857", 2: "url(#strong-category)", 3: "#c93c3c", 4: "#681c33", 5: "#28111e"}
SNAPSHOTS = ["2026-07-21", "2026-07-25", "2026-08-02", "2026-08-07", "2026-08-08", "2026-08-10"]


def build(input_path=DEFAULT_INPUT, output_path=DEFAULT_OUTPUT):
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    daily = {item["date"]: item for item in payload["daily_footprints"]}
    west, east, south, north = -53.25, -46.55, 39.2, 43.9
    cosine = math.cos(math.radians((south + north) / 2))
    panel_w, panel_h = 248, 174

    def panel(date, x0, y0):
        item = daily[date]
        scale = min(panel_w / ((east - west) * cosine), panel_h / (north - south))
        used_w, used_h = (east - west) * cosine * scale, (north - south) * scale
        ox, oy = x0 + (panel_w - used_w) / 2, y0 + (panel_h - used_h) / 2
        cells = []
        for latitude, runs in item["component_rows"]:
            for run_west, run_east, category in runs:
                x = ox + (run_west - 0.025 - west) * cosine * scale
                y = oy + (north - latitude - 0.025) * scale
                width = (run_east - run_west + 0.05) * cosine * scale
                height = 0.05 * scale
                cells.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{width:.2f}" height="{height:.2f}" fill="{COLORS[category]}"/>')
        centroid = item["summary"]["centroid"]
        cx = ox + (centroid["longitude_degrees_east"] - west) * cosine * scale
        cy = oy + (north - centroid["latitude_degrees_north"]) * scale
        label = date[5:].replace("-", " · ")
        scale_bar = ""
        if date == SNAPSHOTS[0]:
            bar_width = 100 / 111.195 * scale
            scale_bar = f'<path d="M{x0+14},{y0+153}h{bar_width:.1f}" stroke="#395660" stroke-width="2"/><text x="{x0+14+bar_width/2:.1f}" y="{y0+168}" class="scale" text-anchor="middle">100 km</text>'
        return f'''<g><rect x="{x0}" y="{y0}" width="{panel_w}" height="{panel_h}" fill="#edf5f6" stroke="#b8ccd1"/>{''.join(cells)}
<circle cx="{cx:.2f}" cy="{cy:.2f}" r="3.2" fill="#f8fbfa" stroke="#143844" stroke-width="1.4"/>
{scale_bar}<text x="{x0}" y="{y0-11}" class="paneldate">{label}</text><text x="{x0+panel_w}" y="{y0-11}" class="panelmetric" text-anchor="end">{item['summary']['area_km2']:,.0f} km²</text></g>'''

    panels = []
    for index, date in enumerate(SNAPSHOTS):
        panels.append(panel(date, 72 + (index % 3) * 270, 235 + (index // 3) * 230))

    chart_x, chart_y, chart_w, chart_h = 895, 655, 230, 60
    values = [item["summary"]["area_km2"] for item in payload["daily_footprints"]]
    maximum = max(values)
    points = []
    for index, value in enumerate(values):
        points.append((chart_x + index * chart_w / (len(values) - 1), chart_y + chart_h - value / maximum * chart_h))
    area_path = " ".join(("M" if index == 0 else "L") + f"{x:.1f},{y:.1f}" for index, (x, y) in enumerate(points))
    summary = payload["summary"]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="820" viewBox="0 0 1200 820" role="img">
<title>OSW-D3 tracked North Atlantic marine heatwave footprint lineage</title>
<desc>Six snapshots show a connected marine heatwave footprint growing from 2,622 to nearly 49,439 square kilometres, then collapsing to a small remnant before its exact-overlap lineage breaks on August 11, 2026.</desc>
<style>.eyebrow{{font:700 15px Inter,"Segoe UI",sans-serif;letter-spacing:2.3px;fill:#327184}}.title{{font:700 42px Georgia,serif;fill:#112c38}}.lead{{font:400 18px Inter,"Segoe UI",sans-serif;fill:#425d67}}.paneldate{{font:700 13px Inter,"Segoe UI",sans-serif;fill:#173946;letter-spacing:.8px}}.panelmetric{{font:500 12px Inter,"Segoe UI",sans-serif;fill:#61777f}}.scale{{font:500 9px Inter,"Segoe UI",sans-serif;fill:#526b74}}.metric{{font:700 31px Georgia,serif;fill:#112c38}}.metriclabel{{font:600 11px Inter,"Segoe UI",sans-serif;letter-spacing:.9px;fill:#60747d}}.body{{font:400 13px Inter,"Segoe UI",sans-serif;fill:#536a74}}.callout{{font:650 14px Inter,"Segoe UI",sans-serif;fill:#873927}}</style>
<defs><pattern id="strong-category" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><rect width="5" height="5" fill="#f47a37"/><path d="M0 0V5" stroke="#a53c29" stroke-width="1.2"/></pattern></defs>
<rect width="1200" height="820" fill="#f8fbfa"/><path d="M0 0H1200V12H0Z" fill="#1f7085"/>
<text x="72" y="66" class="eyebrow">OSW · DETECTED OBJECT 03 · PRIMARY-OVERLAP LINEAGE</text>
<text x="72" y="121" class="title">The shape has a life of its own</text>
<text x="72" y="157" class="lead">21 inherited daily footprints · 21 July—10 August 2026 · identical local equirectangular frames</text>
<g transform="translate(895 174)"><rect width="14" height="14" rx="2" fill="{COLORS[1]}"/><text x="21" y="11" class="body">moderate</text><rect x="103" width="14" height="14" rx="2" fill="{COLORS[2]}"/><text x="124" y="11" class="body">strong</text></g>
{''.join(panels)}
<g transform="translate(895 225)">
 <text class="metric">21</text><text x="52" y="-1" class="metriclabel">TRACKED DAYS</text><text x="52" y="17" class="body">starts before the anchor event</text>
 <line y1="39" x2="230" y2="39" stroke="#cadadc"/>
 <text y="80" class="metric">{summary['maximum_daily_area_km2']:,.0f}</text><text y="105" class="metriclabel">KM² MAXIMUM DAILY AREA</text>
 <line y1="126" x2="230" y2="126" stroke="#cadadc"/>
 <text y="168" class="metric">{summary['total_centroid_path_km']:,.0f}</text><text y="193" class="metriclabel">KM CENTROID PATH</text>
 <line y1="214" x2="230" y2="214" stroke="#cadadc"/>
 <text y="255" class="metric">{summary['minimum_daily_iou']:.3f}</text><text y="280" class="metriclabel">WEAKEST IoU · {summary['branch_ambiguous_transition_count']} AMBIGUOUS STEPS</text>
 <line y1="302" x2="230" y2="302" stroke="#cadadc"/>
 <text y="341" class="callout">BREAK · 11 AUGUST</text>
 <text y="365" class="body">No active component inherited</text><text y="383" class="body">even one exact pixel.</text>
</g>
<text x="895" y="637" class="metriclabel">DAILY FOOTPRINT AREA</text><path d="{area_path}" fill="none" stroke="#e06232" stroke-width="3"/><path d="M{chart_x},{chart_y+chart_h}H{chart_x+chart_w}" stroke="#b9cbcf"/>
<text x="72" y="778" class="body">Local equirectangular · standard parallel 41.55°N. Each successor inherits exact native pixels; greatest intersection chooses the primary branch—not parcels, heat transport, or one inevitable “blob.”</text>
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

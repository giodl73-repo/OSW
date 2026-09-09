"""Render OSW-D1 as a self-contained SVG evidence receipt."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "research" / "osw-d1-noaa-crw-mhw-point-2026.json"
DEFAULT_OUTPUT = ROOT / "figures" / "osw-d1-noaa-crw-mhw-point-2026.svg"
COLORS = {0: "#d9e3e8", 1: "#ffc857", 2: "#f47a37", 3: "#c93c3c", 4: "#681c33", 5: "#28111e"}


def build(input_path=DEFAULT_INPUT, output_path=DEFAULT_OUTPUT):
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    event = payload["events"][0]
    rows = payload["daily_categories"]
    x0, y0, cell_width, cell_height = 112, 365, 30, 70
    cells = []
    labels = []
    for index, (date, category, _mask) in enumerate(rows):
        x = x0 + index * cell_width
        cells.append(f'<rect x="{x}" y="{y0}" width="27" height="{cell_height}" rx="4" fill="{COLORS[category]}"/>')
        if index % 4 == 0 or index == len(rows) - 1:
            labels.append(f'<text x="{x + 13}" y="{y0 + 91}" class="date" text-anchor="middle">{html.escape(date[5:])}</text>')
    event_start = next(index for index, row in enumerate(rows) if row[0] == event["start_date"])
    event_end = next(index for index, row in enumerate(rows) if row[0] == event["end_date"])
    bracket_x = x0 + event_start * cell_width
    bracket_width = (event_end - event_start + 1) * cell_width - 3
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="700" viewBox="0 0 1200 700" role="img">
<title>OSW-D1 North Atlantic marine heatwave evidence receipt</title>
<desc>A 32-day category timeline shows a duration-qualified 27-day linked marine heatwave from July 23 through August 18, 2026, at 42.125 degrees north and 49.875 degrees west.</desc>
<style>
  .sans {{ font-family: Inter, "Segoe UI", Arial, sans-serif; }}
  .eyebrow {{ font: 700 15px Inter, "Segoe UI", sans-serif; letter-spacing: 2.4px; fill: #327184; }}
  .title {{ font: 700 42px Georgia, serif; fill: #112c38; }}
  .lead {{ font: 400 19px Inter, "Segoe UI", sans-serif; fill: #38515d; }}
  .metric {{ font: 700 36px Georgia, serif; fill: #112c38; }}
  .metric-label {{ font: 600 13px Inter, "Segoe UI", sans-serif; letter-spacing: 1px; fill: #60747d; }}
  .date {{ font: 500 11px Inter, "Segoe UI", sans-serif; fill: #60747d; }}
  .small {{ font: 400 14px Inter, "Segoe UI", sans-serif; fill: #536a74; }}
  .strong {{ font: 650 15px Inter, "Segoe UI", sans-serif; fill: #173946; }}
</style>
<rect width="1200" height="700" fill="#f8fbfa"/>
<path d="M0 0H1200V12H0Z" fill="#1f7085"/>
<text x="72" y="72" class="eyebrow">OSW · DETECTED OBJECT 01 · EVIDENCE RECEIPT</text>
<text x="72" y="128" class="title">A marine heatwave earns its name</text>
<text x="72" y="165" class="lead">One surface pixel · 42.125°N, 49.875°W · NOAA Coral Reef Watch · 2026</text>
<line x1="72" y1="204" x2="1128" y2="204" stroke="#c9d8dc"/>
<g transform="translate(72 245)">
  <text class="metric">27</text><text y="25" x="62" class="metric-label">LINKED DAYS</text>
  <text x="285" class="metric">2</text><text y="25" x="326" class="metric-label">MAXIMUM CATEGORY · STRONG</text>
  <text x="725" class="metric">PASS</text><text y="25" x="832" class="metric-label">OBJ046 IDENTITY TEST</text>
</g>
<text x="72" y="337" class="strong">DAILY MARINE-HEATWAVE CATEGORY</text>
{''.join(cells)}
{''.join(labels)}
<path d="M{bracket_x} {y0-12}v-10h{bracket_width}v10" fill="none" stroke="#173946" stroke-width="2"/>
<text x="{bracket_x + bracket_width/2}" y="{y0-31}" class="strong" text-anchor="middle">23 JUL — 18 AUG · two qualified runs joined across one cool day</text>
<g transform="translate(112 505)">
  <rect width="16" height="16" rx="3" fill="{COLORS[0]}"/><text x="24" y="13" class="small">none</text>
  <rect x="105" width="16" height="16" rx="3" fill="{COLORS[1]}"/><text x="129" y="13" class="small">1 moderate</text>
  <rect x="245" width="16" height="16" rx="3" fill="{COLORS[2]}"/><text x="269" y="13" class="small">2 strong</text>
</g>
<rect x="72" y="555" width="1056" height="92" rx="8" fill="#eaf2f2"/>
<text x="96" y="586" class="strong">WHAT THIS EARNS</text>
<text x="96" y="612" class="small">A duration-qualified surface marine heatwave at one exact pixel. Five-day runs are required; gaps ≤2 days may join them.</text>
<text x="96" y="634" class="small">Not yet earned: a spatial footprint, subsurface extent, heat content, transport, cause, or ecological impact.</text>
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

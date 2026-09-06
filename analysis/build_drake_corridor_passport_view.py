"""Render paired position/time passports for the Drake pathway corridor."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import pathlib

from build_drake_pathways_view import (
    EXPECTED_LAND_SHA256, LAND_COMMIT, PANELS, PANEL_SIZE, TRACK_COLORS,
    grid, land_path, normalize_longitude, project, track_path,
)


WIDTH, HEIGHT = 1500, 1180
CLASS_COLORS = {"full": "#62d7ce", "mixed": "#f0cf70", "lost": "#f05d67"}


def passport_matrix(releases: list[dict]) -> str:
    by_key = {(item["release_time"], item["release_index"]): item for item in releases}
    times = sorted({item["release_time"] for item in releases})
    x0, y0, cell_w, row_h = 810, 970, 52, 34
    parts = [
        f'<text x="{x0}" y="{y0 - 25}" class="matrix-head">PAIRED COMPLETION PASSPORT · POSITION / CLOCK</text>',
        f'<text x="{x0 - 66}" y="{y0 - 7}" class="matrix-label">P</text>',
        f'<text x="{x0 - 50}" y="{y0 - 7}" class="matrix-label">T</text>',
    ]
    for index in range(1, 11):
        parts.append(f'<text x="{x0 + (index - 1) * cell_w + 24:.1f}" y="{y0 - 7}" class="matrix-label" text-anchor="middle">{index}</text>')
    for row, time in enumerate(times):
        y = y0 + row * row_h
        parts.append(f'<text x="{x0 - 12}" y="{y + 22}" class="matrix-label" text-anchor="end">{time[:10]}</text>')
        for column in range(1, 11):
            item = by_key[(time, column)]
            x = x0 + (column - 1) * cell_w
            for offset, key in ((0, "position"), (14, "time")):
                diagnostic = item[key]
                color = CLASS_COLORS[diagnostic["class"]]
                parts.append(
                    f'<rect x="{x}" y="{y + offset}" width="48" height="12" rx="3" fill="{color}"/>'
                    f'<text x="{x + 24}" y="{y + offset + 9}" text-anchor="middle" class="matrix-value">{diagnostic["completed"]}/{diagnostic["total"]}</text>'
                )
    return "".join(parts)


def render(primary: dict, paired: dict, geojson: dict, land_sha256: str) -> str:
    release_times = primary["release_contract"]["times"]
    tracks_by_time = {time: [] for time in release_times}
    passports = {(item["release_time"], item["release_index"]): item for item in paired["releases"]}
    for track in primary["tracks"]:
        tracks_by_time[track["release_time"]].append(track)
    panels = []
    for panel_index, (panel, release_time) in enumerate(zip(PANELS, release_times)):
        x, y = panel; width, height = PANEL_SIZE
        paths = []; endpoints = []; starts = []
        for track in tracks_by_time[release_time]:
            color = TRACK_COLORS[track["release_index"] - 1]
            paths.append(f'<path d="{track_path(track, panel)}" stroke="{color}"/>')
            endpoint = track["points"][-1]
            ex, ey = project(normalize_longitude(endpoint["longitude"]), endpoint["latitude"], panel)
            endpoints.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="3" fill="#06171c" stroke="{color}"/>')
            sx, sy = project(normalize_longitude(track["release_longitude"]), track["release_latitude"], panel)
            passport = passports[(release_time, track["release_index"])]
            starts.append(
                f'<circle cx="{sx - 3.3:.1f}" cy="{sy:.1f}" r="3" fill="{CLASS_COLORS[passport["position"]["class"]]}" stroke="#06171c" stroke-width=".7"/>'
                f'<circle cx="{sx + 3.3:.1f}" cy="{sy:.1f}" r="3" fill="{CLASS_COLORS[passport["time"]["class"]]}" stroke="#06171c" stroke-width=".7"/>'
            )
        full_both = sum(passports[(release_time, index)]["paired_pattern"] == "full/full" for index in range(1, 11))
        clip_id = f"passport-panel-{panel_index}"
        panels.append(f'''
  <g aria-label="paired pathway passports {release_time[:10]}">
    <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="14" fill="#0a242b"/>
    <g class="grid" clip-path="url(#{clip_id})">{grid(panel)}</g>
    <g class="passport-map" clip-path="url(#{clip_id})">{''.join(paths)}{''.join(endpoints)}{''.join(starts)}
      <path class="land" d="{land_path(geojson, panel)}"/>
    </g>
    <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="14" fill="none" stroke="#49666b"/>
    <rect x="{x + 9}" y="{y + 8}" width="220" height="29" rx="8" fill="#06171c" fill-opacity=".88" stroke="#49666b" stroke-opacity=".5"/>
    <text x="{x + 16}" y="{y + 29}" class="panel-title">{release_time[:10]} · {full_both}/10 FULL / FULL</text>
  </g>''')
    summary = paired["summary"]
    patterns = summary["paired_pattern_counts"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" data-motion-level="surface-pathway-passport" data-zoning="off">
  <title id="title">The corridor, not the line</title>
  <desc id="desc">Four Drake release rows with paired position and clock sensitivity marks for every central pathway. {html.escape(paired['interpretation'])}</desc>
  <metadata>Native OSCAR field SHA-256 {paired['source_receipts']['position_field_sha256']}; Natural Earth commit {LAND_COMMIT}, SHA-256 {land_sha256}. Position and time diagnostics remain separate.</metadata>
  <defs>
    {''.join(f'<clipPath id="passport-panel-{i}"><rect x="{x}" y="{y}" width="{PANEL_SIZE[0]}" height="{PANEL_SIZE[1]}" rx="14"/></clipPath>' for i, (x, y) in enumerate(PANELS))}
    <pattern id="quiet-land" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="8" height="8" fill="#f8f8f5"/><path d="M0 0V8" stroke="#506b6e" stroke-width=".5" stroke-opacity=".14"/></pattern>
    <style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.grid path{{fill:none;stroke:#8fb0b0;stroke-width:.5;stroke-opacity:.14}}.grid text{{fill:#8ba4a4;font:700 8px ui-monospace,Consolas,monospace}}.passport-map>path{{fill:none;stroke-width:1.35;stroke-linecap:round;stroke-linejoin:round;opacity:.72}}.passport-map .land{{fill:url(#quiet-land);fill-rule:evenodd;stroke:#99aaaa;stroke-width:.65;opacity:.98}}.panel-title{{fill:#e8f6f4;font-size:11px;font-weight:900;letter-spacing:1px}}.matrix-head{{fill:#62d7ce;font-size:10px;font-weight:950;letter-spacing:1.1px}}.matrix-label{{fill:#829fa0;font:800 8px ui-monospace,Consolas,monospace}}.matrix-value{{fill:#06171c;font:950 8px ui-monospace,Consolas,monospace}}</style>
  </defs>
  <rect width="{WIDTH}" height="{HEIGHT}" fill="#06171c"/>
  <text x="60" y="42" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.5">OSW / MOTION STUDY · M2 PAIRED PASSPORT</text>
  <text x="60" y="86" fill="#eef9f7" font-size="35" font-weight="950">THE CORRIDOR, NOT THE LINE</text>
  <text x="60" y="116" fill="#9db3b2" font-size="12">40 central pathways · position and clock kept separate · paired completion support at every seed</text>
  <rect x="1104" y="38" width="336" height="31" rx="15" fill="#102a30" stroke="#f0cf70" stroke-opacity=".7"/>
  <text x="1272" y="59" text-anchor="middle" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.2">TWO DIAGNOSTICS · NO COMPOSITE SCORE</text>
  {''.join(panels)}
  <g transform="translate(60 944)">
    <text fill="#62d7ce" font-size="11" font-weight="950" letter-spacing="1.1">PAIRED VERDICT</text>
    <text y="31" fill="#e5f4f2" font-size="20" font-weight="950">{summary['full_under_both']} / {summary['base_releases']}</text>
    <text x="92" y="31" fill="#9db3b2" font-size="11">full under both declared tests</text>
    <text y="60" fill="#9db3b2" font-size="10.5">{summary['lost_under_both']} lost / lost · {summary['other_or_mixed']} mixed or one-sided</text>
    <text y="92" fill="#62d7ce" font-size="10" font-weight="950" letter-spacing="1.1">PATTERNS</text>
    <text y="116" fill="#9db3b2" font-size="10.5">full/full {patterns.get('full/full', 0)} · full/mixed {patterns.get('full/mixed', 0)} · mixed/full {patterns.get('mixed/full', 0)}</text>
    <text y="139" fill="#9db3b2" font-size="10.5">mixed/mixed {patterns.get('mixed/mixed', 0)} · mixed/lost {patterns.get('mixed/lost', 0)} · lost/lost {patterns.get('lost/lost', 0)}</text>
    <text y="172" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.1">READ</text>
    <text x="48" y="172" fill="#9db3b2" font-size="10.5">stable interior · fragile margins</text>
  </g>
  {passport_matrix(paired['releases'])}
  <g transform="translate(810 1138)">
    <circle cx="4" cy="0" r="4" fill="#62d7ce"/><text x="14" y="4" class="matrix-label">FULL</text>
    <circle cx="74" cy="0" r="4" fill="#f0cf70"/><text x="84" y="4" class="matrix-label">MIXED</text>
    <circle cx="154" cy="0" r="4" fill="#f05d67"/><text x="164" y="4" class="matrix-label">LOST</text>
    <text x="236" y="4" class="matrix-label">P = ±15 km POSITION · T = ±5 DAY CLOCK</text>
  </g>
  <text x="60" y="1160" fill="#627c7e" font-size="9">PAIRED MARKS AT EACH START: LEFT = POSITION · RIGHT = CLOCK · CLASS MEANS COMPLETION UNDER THE DECLARED TEST ONLY · NOT PROBABILITY OR HEAT</text>
</svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-pathways-2018.json"))
    parser.add_argument("--paired", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-release-sensitivity-pair-2018.json"))
    parser.add_argument("--land-geojson", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-motion-drake-corridor-passport-2018.svg"))
    args = parser.parse_args()
    raw_land = args.land_geojson.read_bytes()
    land_sha256 = hashlib.sha256(raw_land).hexdigest()
    if land_sha256 != EXPECTED_LAND_SHA256:
        raise SystemExit(f"Natural Earth source checksum mismatch: {land_sha256}")
    svg = render(
        json.loads(args.primary.read_text(encoding="utf-8")),
        json.loads(args.paired.read_text(encoding="utf-8")),
        json.loads(raw_land), land_sha256,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8", newline="\n")
    print(args.output)


if __name__ == "__main__":
    main()

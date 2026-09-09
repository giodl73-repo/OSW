"""Render deterministic release-neighborhood sensitivity for Drake pathways."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import pathlib

from build_drake_pathways_view import (
    DOMAIN, EXPECTED_LAND_SHA256, LAND_COMMIT, PANELS, PANEL_SIZE,
    TRACK_COLORS, grid, land_path, normalize_longitude, project, track_path,
)


WIDTH, HEIGHT = 1500, 1180


def matrix(groups: list[dict], trials_per_group: int = 9, time_key: str = "release_time", heading: str = "RELEASE NEIGHBORHOOD") -> str:
    by_key = {(group[time_key], group["release_index"]): group for group in groups}
    times = sorted({group[time_key] for group in groups})
    x0, y0, cell_w, cell_h = 880, 965, 46, 29
    parts = [f'<text x="{x0}" y="{y0 - 22}" class="matrix-head">COMPLETED / {trials_per_group} BY {heading}</text>']
    for index in range(1, 11):
        parts.append(f'<text x="{x0 + (index - 1) * cell_w + cell_w / 2:.1f}" y="{y0 - 6}" class="matrix-label" text-anchor="middle">{index}</text>')
    for row, time in enumerate(times):
        y = y0 + row * cell_h
        parts.append(f'<text x="{x0 - 12}" y="{y + 19}" class="matrix-label" text-anchor="end">{time[:10]}</text>')
        for column in range(1, 11):
            completed = by_key[(time, column)]["completed"]
            if completed == trials_per_group:
                color = "#62d7ce"
            elif completed == 0:
                color = "#f05d67"
            else:
                color = "#f0cf70"
            x = x0 + (column - 1) * cell_w
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell_w - 3}" height="{cell_h - 3}" rx="5" fill="{color}" fill-opacity=".9"/>'
                f'<text x="{x + (cell_w - 3) / 2:.1f}" y="{y + 19}" text-anchor="middle" class="matrix-value">{completed}</text>'
            )
    return "".join(parts)


def render(primary: dict, sensitivity: dict, geojson: dict, land_sha256: str) -> str:
    is_time = sensitivity["schema"].endswith("release-time-sensitivity.v1")
    time_key = "central_release_time" if is_time else "release_time"
    trials_per_group = len(sensitivity["experiment"]["time_offset_days"]) if is_time else 9
    if is_time:
        eyebrow = "OSW / MOTION STUDY · M2 RELEASE-TIME SENSITIVITY"
        title = "HOW MUCH DOES THE CLOCK MATTER?"
        subtitle = "40 central releases · five deterministic starts from −5 to +5 days · 200 native-grid tracks · no diffusion"
        badge = "CORRIDOR ROBUSTNESS ≠ ONE PERFECT DATE"
        description = "Five deterministic release times spanning ten days around each of forty central Drake surface releases."
        verdict_label = "TIME-WINDOW VERDICT"
        completed_total = sensitivity["summary"]["completed_trials"]
        trial_total = sensitivity["summary"]["shifted_trials"]
        full = sensitivity["summary"]["fully_completed_windows"]
        mixed = sensitivity["summary"]["mixed_windows"]
        lost = sensitivity["summary"]["fully_terminated_windows"]
        typical_label = "typical window median"
        matrix_heading = "RELEASE-TIME WINDOW"
        footer_dot = "SHIFTED-TIME"
    else:
        eyebrow = "OSW / MOTION STUDY · M2 RELEASE SENSITIVITY"
        title = "HOW MUCH DOES ONE SEED MATTER?"
        subtitle = "40 central releases · 3 × 3 deterministic ±15 km neighborhoods · 360 native-grid tracks · no diffusion"
        badge = "CORRIDOR ROBUSTNESS ≠ ONE CERTAIN LINE"
        description = "Nine deterministic release positions within fifteen kilometres of each of forty central Drake surface releases."
        verdict_label = "NEIGHBORHOOD VERDICT"
        completed_total = sensitivity["summary"]["completed_trials"]
        trial_total = sensitivity["summary"]["perturbed_trials"]
        full = sensitivity["summary"]["fully_completed_neighborhoods"]
        mixed = sensitivity["summary"]["mixed_neighborhoods"]
        lost = sensitivity["summary"]["fully_terminated_neighborhoods"]
        typical_label = "typical neighborhood median"
        matrix_heading = "RELEASE NEIGHBORHOOD"
        footer_dot = "PERTURBED"
    release_times = primary["release_contract"]["times"]
    primary_by_time = {time: [] for time in release_times}
    trials_by_time = {time: [] for time in release_times}
    for track in primary["tracks"]:
        primary_by_time[track["release_time"]].append(track)
    for trial in sensitivity["trials"]:
        trials_by_time[trial[time_key]].append(trial)
    panels = []
    for panel_index, (panel, release_time) in enumerate(zip(PANELS, release_times)):
        x, y = panel; width, height = PANEL_SIZE
        central_paths = []; central_endpoints = []; trial_marks = []
        for track in primary_by_time[release_time]:
            color = TRACK_COLORS[track["release_index"] - 1]
            central_paths.append(f'<path d="{track_path(track, panel)}" stroke="{color}"/>')
            endpoint = track["points"][-1]
            ex, ey = project(normalize_longitude(endpoint["longitude"]), endpoint["latitude"], panel)
            central_endpoints.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="#06171c" stroke="{color}" stroke-width="1.4"/>')
        for trial in trials_by_time[release_time]:
            color = TRACK_COLORS[trial["release_index"] - 1]
            endpoint = trial["endpoint"]
            ex, ey = project(normalize_longitude(endpoint["longitude"]), endpoint["latitude"], panel)
            if trial["status"] == "completed":
                trial_marks.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="1.8" fill="{color}" fill-opacity=".68"/>')
            else:
                trial_marks.append(f'<path d="M{ex-2.4:.1f},{ey-2.4:.1f}l4.8,4.8m0,-4.8l-4.8,4.8" stroke="{color}"/>')
        completed = sum(trial["status"] == "completed" for trial in trials_by_time[release_time])
        clip_id = f"release-panel-{panel_index}"
        panels.append(f'''
  <g aria-label="release sensitivity {release_time[:10]}">
    <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="14" fill="#0a242b"/>
    <g class="grid" clip-path="url(#{clip_id})">{grid(panel)}</g>
    <g class="sensitivity-map" clip-path="url(#{clip_id})">{''.join(central_paths)}{''.join(trial_marks)}{''.join(central_endpoints)}
      <path class="land" d="{land_path(geojson, panel)}"/>
    </g>
    <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="14" fill="none" stroke="#49666b"/>
    <rect x="{x + 9}" y="{y + 8}" width="226" height="29" rx="8" fill="#06171c" fill-opacity=".88" stroke="#49666b" stroke-opacity=".5"/>
    <text x="{x + 16}" y="{y + 29}" class="panel-title">{release_time[:10]} · {completed}/{trials_per_group * 10} COMPLETE</text>
  </g>''')
    summary = sensitivity["summary"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" data-motion-level="surface-pathway-sensitivity" data-zoning="off">
  <title id="title">{title}</title>
  <desc id="desc">{description} Central tracks are thin lines; completed shifted endpoints are dots and terminated trials are crosses. {html.escape(sensitivity['interpretation'])}</desc>
  <metadata>Native OSCAR field SHA-256 {sensitivity['velocity_source']['field_sha256']}; Natural Earth commit {LAND_COMMIT}, SHA-256 {land_sha256}. No diffusion or random sampling.</metadata>
  <defs>
    {''.join(f'<clipPath id="release-panel-{i}"><rect x="{x}" y="{y}" width="{PANEL_SIZE[0]}" height="{PANEL_SIZE[1]}" rx="14"/></clipPath>' for i, (x, y) in enumerate(PANELS))}
    <pattern id="quiet-land" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="8" height="8" fill="#f8f8f5"/><path d="M0 0V8" stroke="#506b6e" stroke-width=".5" stroke-opacity=".14"/></pattern>
    <style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.grid path{{fill:none;stroke:#8fb0b0;stroke-width:.5;stroke-opacity:.14}}.grid text{{fill:#8ba4a4;font:700 8px ui-monospace,Consolas,monospace}}.sensitivity-map>path{{fill:none;stroke-width:1.05;stroke-linecap:round;stroke-linejoin:round;opacity:.42}}.sensitivity-map .land{{fill:url(#quiet-land);fill-rule:evenodd;stroke:#99aaaa;stroke-width:.65;opacity:.98}}.panel-title{{fill:#e8f6f4;font-size:11px;font-weight:900;letter-spacing:1px}}.matrix-head{{fill:#62d7ce;font-size:10px;font-weight:950;letter-spacing:1.1px}}.matrix-label{{fill:#829fa0;font:800 8px ui-monospace,Consolas,monospace}}.matrix-value{{fill:#06171c;font:950 10px ui-monospace,Consolas,monospace}}</style>
  </defs>
  <rect width="{WIDTH}" height="{HEIGHT}" fill="#06171c"/>
  <text x="60" y="42" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.5">{eyebrow}</text>
  <text x="60" y="86" fill="#eef9f7" font-size="35" font-weight="950">{title}</text>
  <text x="60" y="116" fill="#9db3b2" font-size="12">{subtitle}</text>
  <rect x="1110" y="38" width="330" height="31" rx="15" fill="#102a30" stroke="#f0cf70" stroke-opacity=".7"/>
  <text x="1275" y="59" text-anchor="middle" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.2">{badge}</text>
  {''.join(panels)}
  <g transform="translate(60 958)">
    <text fill="#62d7ce" font-size="11" font-weight="950" letter-spacing="1.1">{verdict_label}</text>
    <text y="29" fill="#e5f4f2" font-size="13" font-weight="900">{completed_total} / {trial_total} complete</text>
    <text y="54" fill="#9db3b2" font-size="10.5">{full} fully complete · {mixed} mixed · {lost} fully lost</text>
    <text y="82" fill="#62d7ce" font-size="10" font-weight="950" letter-spacing="1.1">ENDPOINT SPREAD</text>
    <text y="106" fill="#9db3b2" font-size="10.5">{typical_label} {summary['median_of_completed_endpoint_medians_km']:.2f} km</text>
    <text y="128" fill="#9db3b2" font-size="10.5">largest completed offset {summary['maximum_completed_endpoint_separation_from_central_km']:.2f} km</text>
    <text y="157" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.1">READ</text>
    <text x="48" y="157" fill="#9db3b2" font-size="10.5">eastward corridor + local divergence</text>
    <text y="179" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.1">DO NOT READ</text>
    <text x="92" y="179" fill="#9db3b2" font-size="10.5">probability · volume · residence · heat</text>
  </g>
  {matrix(sensitivity['groups'], trials_per_group, time_key, matrix_heading)}
  <text x="60" y="1153" fill="#627c7e" font-size="9">DOT = COMPLETED {footer_dot} ENDPOINT · × = TERMINATED TRIAL END · OPEN CIRCLE + THIN LINE = CENTRAL RELEASE · COLOR = RELEASE POSITION NORTH → SOUTH</text>
</svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-pathways-2018.json"))
    parser.add_argument("--sensitivity", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-release-sensitivity-2018.json"))
    parser.add_argument("--land-geojson", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-motion-drake-release-sensitivity-2018.svg"))
    args = parser.parse_args()
    raw_land = args.land_geojson.read_bytes()
    land_sha256 = hashlib.sha256(raw_land).hexdigest()
    if land_sha256 != EXPECTED_LAND_SHA256:
        raise SystemExit(f"Natural Earth source checksum mismatch: {land_sha256}")
    svg = render(
        json.loads(args.primary.read_text(encoding="utf-8")),
        json.loads(args.sensitivity.read_text(encoding="utf-8")),
        json.loads(raw_land), land_sha256,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8", newline="\n")
    print(args.output)


if __name__ == "__main__":
    main()

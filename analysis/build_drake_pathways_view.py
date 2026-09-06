"""Render the receipted four-season Drake surface-pathway method pilot."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import pathlib


WIDTH, HEIGHT = 1500, 1080
DOMAIN = (-82.0, -38.0, -72.0, -43.0)
PANELS = ((60, 175), (765, 175), (60, 570), (765, 570))
PANEL_SIZE = (675, 345)
EXPECTED_LAND_SHA256 = "9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9"
LAND_COMMIT = "ca96624a56bd078437bca8184e78163e5039ad19"
TRACK_COLORS = ("#73e2da", "#63cdd1", "#6fb8cf", "#8ca5c8", "#ad91bc", "#cc7fa6", "#e2788b", "#ee806f", "#f39a62", "#efb968", "#dfd374")


def normalize_longitude(longitude: float) -> float:
    return longitude - 360 if longitude > 180 else longitude


def project(longitude: float, latitude: float, panel: tuple[int, int]) -> tuple[float, float]:
    west, east, south, north = DOMAIN
    x, y = panel
    width, height = PANEL_SIZE
    return (
        x + (longitude - west) / (east - west) * width,
        y + (north - latitude) / (north - south) * height,
    )


def polygon_bounds(ring: list[list[float]]) -> tuple[float, float, float, float]:
    xs = [point[0] for point in ring]; ys = [point[1] for point in ring]
    return min(xs), max(xs), min(ys), max(ys)


def land_path(geojson: dict, panel: tuple[int, int]) -> str:
    west, east, south, north = DOMAIN
    commands = []
    for feature in geojson["features"]:
        geometry = feature["geometry"]
        polygons = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
        for polygon in polygons:
            for ring in polygon:
                minimum_x, maximum_x, minimum_y, maximum_y = polygon_bounds(ring)
                if maximum_x < west or minimum_x > east or maximum_y < south or minimum_y > north:
                    continue
                points = [project(point[0], point[1], panel) for point in ring]
                if points:
                    commands.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in points) + "Z")
    return "".join(commands)


def grid(panel: tuple[int, int]) -> str:
    west, east, south, north = DOMAIN
    parts = []
    for longitude in range(-80, -39, 10):
        x1, y1 = project(longitude, south, panel); x2, y2 = project(longitude, north, panel)
        parts.append(f'<path d="M{x1:.1f},{y1:.1f}L{x2:.1f},{y2:.1f}"/><text x="{x1 + 4:.1f}" y="{panel[1] + 17}">{abs(longitude)}°W</text>')
    for latitude in range(-70, -44, 5):
        x1, y1 = project(west, latitude, panel); x2, y2 = project(east, latitude, panel)
        parts.append(f'<path d="M{x1:.1f},{y1:.1f}L{x2:.1f},{y2:.1f}"/><text x="{panel[0] + 5}" y="{y1 - 5:.1f}">{abs(latitude)}°S</text>')
    return "".join(parts)


def track_path(track: dict, panel: tuple[int, int]) -> str:
    points = [project(normalize_longitude(point["longitude"]), point["latitude"], panel) for point in track["points"]]
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in points)


def render(data: dict, geojson: dict, land_sha256: str, sensitivity: dict, grid_sensitivity: dict) -> str:
    release_times = data["release_contract"]["times"]
    grouped = {release_time: [] for release_time in release_times}
    for track in data["tracks"]:
        grouped[track["release_time"]].append(track)
    panels = []
    for panel_index, (panel, release_time) in enumerate(zip(PANELS, release_times)):
        x, y = panel; width, height = PANEL_SIZE
        paths = []
        endpoints = []
        starts = []
        for track in grouped[release_time]:
            color = TRACK_COLORS[(track["release_index"] - 1) % len(TRACK_COLORS)]
            dash = ' stroke-dasharray="5 4"' if track["status"] != "completed" else ""
            paths.append(f'<path d="{track_path(track, panel)}" stroke="{color}"{dash}/>')
            start = project(normalize_longitude(track["release_longitude"]), track["release_latitude"], panel)
            end_point = track["points"][-1]
            end = project(normalize_longitude(end_point["longitude"]), end_point["latitude"], panel)
            starts.append(f'<circle cx="{start[0]:.1f}" cy="{start[1]:.1f}" r="2.6" fill="{color}"/>')
            if track["status"] == "completed":
                endpoints.append(f'<circle cx="{end[0]:.1f}" cy="{end[1]:.1f}" r="3" fill="none" stroke="{color}"/>')
            else:
                endpoints.append(f'<path d="M{end[0]-3:.1f},{end[1]-3:.1f}l6,6m0,-6l-6,6" stroke="{color}"/>')
        completed = sum(track["status"] == "completed" for track in grouped[release_time])
        clip_id = f"panel-{panel_index}"
        panels.append(f'''
  <g aria-label="release {release_time[:10]}">
    <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="14" fill="#0a242b"/>
    <g class="grid" clip-path="url(#{clip_id})">{grid(panel)}</g>
    <g class="tracks" clip-path="url(#{clip_id})">{''.join(paths)}{''.join(starts)}{''.join(endpoints)}
      <path class="land" d="{land_path(geojson, panel)}"/>
    </g>
    <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="14" fill="none" stroke="#49666b"/>
    <rect x="{x + 9}" y="{y + 8}" width="205" height="29" rx="8" fill="#06171c" fill-opacity=".88" stroke="#49666b" stroke-opacity=".5"/>
    <text x="{x + 16}" y="{y + 29}" class="panel-title">{release_time[:10]} · {completed}/{len(grouped[release_time])} COMPLETE</text>
  </g>''')
    summary = data["summary"]
    contract = data["solver_contract"]
    source = data["velocity_source"]
    grid_resolution = source["native_resolution_degrees"] * source["space_stride"]
    non_reference = [case for case in sensitivity["cases"] if case["timestep_hours"] != sensitivity["reference_timestep_hours"]]
    maximum_endpoint_separation = max(case["common_completed_endpoint_separation_from_reference_km"]["maximum"] for case in non_reference)
    grid_separation = grid_sensitivity["common_completed_endpoint_separation_km"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" data-motion-level="surface-pathway" data-zoning="off">
  <title id="title">Drake Passage historical surface-pathway method pilot</title>
  <desc id="desc">Four ensembles of {data['release_contract']['count_per_time']} deterministic 30-day surface trajectories released across the wet interior of a schematic Drake Passage section. {html.escape(data['boundary'])}</desc>
  <metadata>OSCAR source SHA-256 {source['source_sha256']}; packaged field SHA-256 {source['field_sha256']}; Natural Earth commit {LAND_COMMIT}, SHA-256 {land_sha256}. {html.escape(json.dumps(contract, separators=(',', ':')))}</metadata>
  <defs>
    {''.join(f'<clipPath id="panel-{i}"><rect x="{x}" y="{y}" width="{PANEL_SIZE[0]}" height="{PANEL_SIZE[1]}" rx="14"/></clipPath>' for i, (x, y) in enumerate(PANELS))}
    <pattern id="quiet-land" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="8" height="8" fill="#f8f8f5"/><path d="M0 0V8" stroke="#506b6e" stroke-width=".5" stroke-opacity=".14"/></pattern>
    <style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.grid path{{fill:none;stroke:#8fb0b0;stroke-width:.5;stroke-opacity:.14}}.grid text{{fill:#8ba4a4;font:700 8px ui-monospace,Consolas,monospace}}.tracks>path{{fill:none;stroke-width:1.65;stroke-linecap:round;stroke-linejoin:round;opacity:.9}}.tracks .land{{fill:url(#quiet-land);fill-rule:evenodd;stroke:#99aaaa;stroke-width:.65;opacity:.98}}.panel-title{{fill:#e8f6f4;font-size:11px;font-weight:900;letter-spacing:1px}}</style>
  </defs>
  <rect width="{WIDTH}" height="{HEIGHT}" fill="#06171c"/>
  <text x="60" y="42" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.5">OSW / MOTION STUDY · M2 METHOD PILOT</text>
  <text x="60" y="86" fill="#eef9f7" font-size="35" font-weight="950">FOUR RELEASES THROUGH DRAKE</text>
  <text x="60" y="116" fill="#9db3b2" font-size="12">{summary['released']} equal-count surface parcels · 30 days · historical OSCAR 2017.0 · nominal 15 m · zoning off</text>
  <rect x="1125" y="38" width="315" height="31" rx="15" fill="#102a30" stroke="#f0cf70" stroke-opacity=".7"/>
  <text x="1282.5" y="59" text-anchor="middle" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.25">TRACKS ARE PATHWAYS · NOT HEAT TRANSPORT</text>
  {''.join(panels)}
  <g transform="translate(60 936)">
    <text fill="#62d7ce" font-size="11" font-weight="950" letter-spacing="1.1">SOLVER RECEIPT</text>
    <text x="112" fill="#abc1bf" font-size="10.5">forward RK4 · 6 h step · linear time + strict four-wet-corner bilinear space · no diffusion · invalid stencil terminates</text>
    <text y="27" fill="#e5f4f2" font-size="11" font-weight="850">{summary['completed']} / {summary['released']} complete 30 days</text>
    <text x="190" y="27" fill="#9db3b2" font-size="10.5">open circle = completed · × / dashed = terminated · line color = release position north → south</text>
    <text y="50" fill="#62d7ce" font-size="10" font-weight="950" letter-spacing="1.1">STEP CHECK</text>
    <text x="84" y="50" fill="#9db3b2" font-size="10.5">3 / 6 / 12 h retain the same {summary['completed']} complete + {summary['terminated']} lost · max completed-endpoint separation {maximum_endpoint_separation:.2f} km · loss timing range ≤ {sensitivity['maximum_loss_timing_range_hours']} h</text>
    <text y="73" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.1">GRID CHECK</text>
    <text x="88" y="73" fill="#9db3b2" font-size="10.5">⅓° primary vs ⅔° coarse: {grid_sensitivity['status_disagreement_count']} status switches · completed endpoint median {grid_separation['median']:.2f} km · max {grid_separation['maximum']:.2f} km</text>
    <text y="96" fill="#f0cf70" font-size="10" font-weight="950" letter-spacing="1.1">DO NOT READ</text>
    <text x="92" y="96" fill="#9db3b2" font-size="10.5">volume · residence · coherence · temperature advection · full-depth circulation · transported heat · precise beaching time</text>
  </g>
  <text x="60" y="1052" fill="#627c7e" font-size="9">REGIONAL METHOD DOMAIN 45–70°S, 80–40°W · APPROX. {grid_resolution:.3f}° GRID · SOURCE {source['source_sha256'][:16]}… · FIELD {source['field_sha256'][:16]}…</text>
</svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-pathways-2018.json"))
    parser.add_argument("--sensitivity", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-timestep-sensitivity-2018.json"))
    parser.add_argument("--grid-sensitivity", type=pathlib.Path, default=pathlib.Path("research/osw-m2-drake-grid-sensitivity-2018.json"))
    parser.add_argument("--land-geojson", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-motion-drake-pathways-2018.svg"))
    args = parser.parse_args()
    raw_land = args.land_geojson.read_bytes()
    land_sha256 = hashlib.sha256(raw_land).hexdigest()
    if land_sha256 != EXPECTED_LAND_SHA256:
        raise SystemExit(f"Natural Earth source checksum mismatch: {land_sha256}")
    svg = render(
        json.loads(args.data.read_text(encoding="utf-8")), json.loads(raw_land), land_sha256,
        json.loads(args.sensitivity.read_text(encoding="utf-8")),
        json.loads(args.grid_sensitivity.read_text(encoding="utf-8")),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8", newline="\n")
    print(args.output)


if __name__ == "__main__":
    main()

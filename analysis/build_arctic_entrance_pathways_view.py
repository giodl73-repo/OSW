"""Render deterministic surface pathways from the paired Arctic entrance lanes."""

from __future__ import annotations

import argparse
import html
import json
import pathlib

try:
    from build_arctic_entrances_motion_view import land_paths, load_land, normalize_longitude, projection
except ModuleNotFoundError:
    from analysis.build_arctic_entrances_motion_view import land_paths, load_land, normalize_longitude, projection


WIDTH, HEIGHT = 1400, 980
PANELS = {
    "fram_west_export": {"box": (45, 155, 420, 570), "domain": (-20, 20, 72, 80), "center": (0, 76), "title": "FRAM WEST", "subtitle": "EXPORT LANE"},
    "fram_east_inflow": {"box": (490, 155, 420, 570), "domain": (-20, 20, 72, 80), "center": (0, 76), "title": "FRAM EAST", "subtitle": "INFLOW LANE"},
    "barents_inflow": {"box": (935, 155, 420, 570), "domain": (20, 60, 68, 80), "center": (40, 74), "title": "BARENTS", "subtitle": "EASTWARD ENTRANCE"},
}
SEASON_COLORS = {"2017-12-16": "#7e9dff", "2018-03-18": "#62d7ce", "2018-06-17": "#f0cf70", "2018-09-16": "#dc83ff"}


def track_path(track: dict, panel: dict) -> str:
    screen = projection(panel)
    points = [screen(normalize_longitude(point["longitude"]), point["latitude"]) for point in track["points"]]
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in points)


def panel(group: str, tracks: list[dict], summary: dict, geojson: dict) -> str:
    definition = PANELS[group]
    x, y, width, height = definition["box"]
    paths = []
    endpoints = []
    for track in tracks:
        color = SEASON_COLORS[track["release_time"][:10]]
        dash = ' stroke-dasharray="5 4"' if track["status"] != "completed" else ""
        paths.append(f'<path d="{track_path(track, definition)}" stroke="{color}"{dash}/>')
        end = projection(definition)(normalize_longitude(track["points"][-1]["longitude"]), track["points"][-1]["latitude"])
        if track["status"] == "completed":
            endpoints.append(f'<circle cx="{end[0]:.1f}" cy="{end[1]:.1f}" r="2.5" fill="none" stroke="{color}"/>')
        else:
            endpoints.append(f'<path d="M{end[0]-3:.1f},{end[1]-3:.1f}l6,6m0,-6l-6,6" stroke="{color}"/>')
    fate = next(key for key in summary["fates"] if key not in ("other", "terminated"))
    return f'''<g aria-label="{definition['title']}"><rect x="{x}" y="{y}" width="{width}" height="{height}" rx="17" class="panel"/><clipPath id="clip-{group}"><rect x="{x}" y="{y+43}" width="{width}" height="{height-104}"/></clipPath><text x="{x+18}" y="{y+29}" class="panel-title">{definition['title']}</text><text x="{x+width-18}" y="{y+28}" class="panel-sub">{definition['subtitle']}</text><g class="tracks" clip-path="url(#clip-{group})">{''.join(paths)}{''.join(endpoints)}<path d="{land_paths(geojson, definition)}" class="land"/></g><text x="{x+17}" y="{y+height-36}" class="summary">{summary['completed']} / {summary['released']} COMPLETE · {summary['fates'][fate]} {fate.upper()} · {summary['fates']['terminated']} LOST</text><text x="{x+17}" y="{y+height-17}" class="fine">MEDIAN COMPLETED DISTANCE {summary['median_completed_distance_km']:.0f} KM</text></g>'''


def build(payload: dict, geojson: dict, land_sha256: str) -> str:
    summaries = {item["group"]: item for item in payload["summaries"]}
    grouped = {group: [track for track in payload["tracks"] if track["group"] == group] for group in PANELS}
    panels = "".join(panel(group, grouped[group], summaries[group], geojson) for group in PANELS)
    west = summaries["fram_west_export"]; east = summaries["fram_east_inflow"]; barents = summaries["barents_inflow"]
    legend = "".join(f'<path d="M{x} 786h28" stroke="{color}" stroke-width="2"/><text x="{x+36}" y="790" class="legend">{date}</text>' for x, (date, color) in zip((50, 270, 490, 710), SEASON_COLORS.items()))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" data-motion-level="m2-arctic-entrance-pathways"><title id="title">Arctic entrance deterministic surface pathways</title><desc id="desc">Western Fram completed tracks consistently export south, eastern Fram tracks have mixed northward fate, and most completed Barents tracks move eastward. Tracks are pathways, not heat transport.</desc><metadata>Natural Earth SHA-256 {land_sha256}. {html.escape(payload['boundary'])}</metadata><defs><pattern id="quiet-land" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="8" height="8" fill="#f8f8f5"/><path d="M0 0V8" stroke="#506b6e" stroke-width=".5" stroke-opacity=".14"/></pattern><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.panel{{fill:#0b252c;stroke:#49666b}}.panel-title{{fill:#eef9f7;font-size:17px;font-weight:950}}.panel-sub{{fill:#819c9d;font-size:8px;font-weight:900;letter-spacing:1px;text-anchor:end}}.tracks>path{{fill:none;stroke-width:1.25;stroke-linecap:round;stroke-linejoin:round;opacity:.72}}.tracks .land{{fill:url(#quiet-land);fill-rule:evenodd;stroke:#9aabaa;stroke-width:.65;opacity:.98}}.summary{{fill:#eef9f7;font:850 9px ui-monospace,Consolas,monospace}}.fine{{fill:#617d80;font-size:7.5px}}.legend{{fill:#9bb1b0;font-size:8.5px}}.metric{{fill:#eef9f7;font:950 24px ui-monospace,Consolas,monospace}}.metric-label{{fill:#91a9a8;font-size:8px;font-weight:900;letter-spacing:.9px}}.note{{fill:#a8bfbd;font-size:9.5px}}</style></defs><rect width="1400" height="980" fill="#06171c"/><text x="45" y="43" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.4">OSW / ARCTIC HEAT ROUTES · M2 PATHWAY LAB</text><text x="45" y="87" fill="#eef9f7" font-size="34" font-weight="950">EXPORT IS CLEANER THAN INFLOW</text><text x="45" y="116" fill="#9db3b2" font-size="12">112 deterministic equal-count surface tracks · four historical releases · strict wet-stencil RK4</text><rect x="1050" y="39" width="305" height="30" rx="15" fill="#102a30" stroke="#f0cf70"/><text x="1202.5" y="59" fill="#f0cf70" text-anchor="middle" font-size="9.5" font-weight="950" letter-spacing="1">PATHWAYS · NOT HEAT TRANSPORT</text>{panels}<g>{legend}</g><g transform="translate(990 778)"><text class="metric">{west['fates']['southward']}/{west['completed']} · {east['fates']['northward']}/{east['completed']} · {barents['fates']['eastward']}/{barents['completed']}</text><text y="22" class="metric-label">DECLARED DIRECTION AMONG COMPLETED · WEST / EAST / BARENTS</text></g><rect x="45" y="833" width="1310" height="98" rx="14" fill="#0d242a"/><text x="67" y="859" fill="#eef9f7" font-size="14" font-weight="950">THE CORRIDOR, NOT A FORECAST</text><text x="67" y="883" class="note">Fram export is coherent in this experiment. Eastern Fram inflow is seasonally and spatially mixed; Barents is predominantly eastward.</text><text x="67" y="904" class="note">Termination marks a coast/domain stencil failure—not beaching, residence, or disappearance. Equal track counts are not transported volume or probability.</text><text x="67" y="921" class="fine">FRAM 20 DAYS DUE TO OSCAR 80°N LIMIT · BARENTS 30 DAYS · NOMINAL 15 M · NO DIFFUSION · NO TEMPERATURE, SALINITY, DEPTH, VOLUME, OR HEAT</text><text x="45" y="958" fill="#536f72" font-size="8">FORWARD RK4 · 6-HOUR STEP · LINEAR TIME + STRICT FOUR-WET-CORNER BILINEAR SPACE · OPEN CIRCLE COMPLETE · × / DASHED TERMINATED</text></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m2-arctic-entrance-pathways-2018.json"))
    parser.add_argument("--land-geojson", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-motion-arctic-entrance-pathways-2018.svg"))
    args = parser.parse_args()
    land, digest = load_land(args.land_geojson)
    svg = build(json.loads(args.input.read_text(encoding="utf-8")), land, digest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

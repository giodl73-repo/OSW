"""Render the source-tagged Agulhas pathway fate and gate-sensitivity audit."""

from __future__ import annotations

import argparse
import html
import json
import pathlib

try:
    from build_arctic_entrances_motion_view import land_paths, load_land, projection
except ModuleNotFoundError:
    from analysis.build_arctic_entrances_motion_view import land_paths, load_land, projection


WIDTH, HEIGHT = 1400, 1020
MAP = {"box": (45, 155, 720, 535), "domain": (5, 48, -46, -28), "center": (27, -37)}
FATE_COLORS = {
    "cape_basin": "#ffad55",
    "return_corridor": "#54d8d0",
    "both_thresholds": "#d78cff",
    "unresolved": "#667f83",
    "terminated": "#e26f86",
}


def track_path(track: dict) -> str:
    screen = projection(MAP)
    points = [screen(point["longitude"], point["latitude"]) for point in track["points"]]
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in points)


def track_layer(tracks: list[dict]) -> str:
    parts = []
    for track in sorted(tracks, key=lambda item: item["baseline_fate"] == "unresolved", reverse=True):
        fate = track["baseline_fate"]
        parts.append(f'<path d="{track_path(track)}" stroke="{FATE_COLORS[fate]}" class="track fate-{fate}"/>')
    return "".join(parts)


def gate_layer() -> str:
    screen = projection(MAP)
    wx1, wy1 = screen(15, -28); wx2, wy2 = screen(15, -42)
    ex1, ey1 = screen(35, -34); ex2, ey2 = screen(35, -46)
    return f'''<path d="M{wx1:.1f},{wy1:.1f}L{wx2:.1f},{wy2:.1f}" stroke="#ffad55" class="gate"/><text x="{wx1+8:.1f}" y="{wy1+14:.1f}" class="gate-label" fill="#ffad55">15°E · CAPE BASIN</text><path d="M{ex1:.1f},{ey1:.1f}L{ex2:.1f},{ey2:.1f}" stroke="#54d8d0" class="gate"/><text x="{ex1+8:.1f}" y="{ey1+14:.1f}" class="gate-label" fill="#54d8d0">35°E · RETURN</text>'''


def release_card(summary: dict, x: int, y: int) -> str:
    fates = summary["fates"]
    order = ("cape_basin", "return_corridor", "unresolved", "terminated", "both_thresholds")
    labels = {"cape_basin": "CAPE", "return_corridor": "RETURN", "unresolved": "OPEN", "terminated": "LOST", "both_thresholds": "BOTH"}
    total = summary["released"]
    cursor = 0
    bars = []
    for fate in order:
        width = 370 * fates[fate] / total
        if width:
            bars.append(f'<rect x="{cursor:.1f}" y="58" width="{width:.1f}" height="9" fill="{FATE_COLORS[fate]}"/>')
        cursor += width
    values = " · ".join(f"{fates[fate]} {labels[fate]}" for fate in order if fates[fate])
    return f'''<g transform="translate({x} {y})"><rect width="400" height="104" rx="13" class="card"/><text x="16" y="24" class="card-date">{summary['release_time'][:10]}</text><text x="384" y="24" class="card-total">36 PATHS</text><text x="16" y="47" class="card-values">{values}</text><g transform="translate(15 0)">{''.join(bars)}</g><text x="16" y="88" class="card-note">150-DAY FATE CENSUS · EQUAL COUNT</text></g>'''


def sensitivity_cell(item: dict, x: int, y: int, baseline: bool) -> str:
    f = item["fates"]
    border = "#f0cf70" if baseline else "#3d5a60"
    return f'''<g transform="translate({x} {y})"><rect width="260" height="70" rx="10" fill="#0d272e" stroke="{border}"/><text x="13" y="22" class="sense-gate">W {item['west_gate_east']:.0f}°E · E {item['east_gate_east']:.0f}°E</text><text x="13" y="47" class="sense-values"><tspan fill="#ffad55">{f['cape_basin']} C</tspan><tspan fill="#54d8d0"> · {f['return_corridor']} R</tspan><tspan fill="#667f83"> · {f['unresolved']} U</tspan><tspan fill="#e26f86"> · {f['terminated']} T</tspan></text><text x="247" y="61" class="both" text-anchor="end">{f['both_thresholds']} BOTH</text></g>'''


def build(payload: dict, geojson: dict, land_sha256: str) -> str:
    x, y, width, height = MAP["box"]
    cards = "".join(release_card(item, 800, 177 + index * 121) for index, item in enumerate(payload["release_summaries"]))
    sensitivity = "".join(
        sensitivity_cell(item, 495 + column * 280, 763 + row * 82, item["west_gate_east"] == 15 and item["east_gate_east"] == 35)
        for row, west in enumerate((12, 15, 18))
        for column, east in enumerate((33, 35, 37))
        for item in payload["gate_sensitivity"]
        if item["west_gate_east"] == west and item["east_gate_east"] == east
    )
    screen = projection(MAP)
    seeds = "".join(f'<circle cx="{screen(center["longitude"], center["latitude"])[0]:.1f}" cy="{screen(center["longitude"], center["latitude"])[1]:.1f}" r="4" fill="#eef9f7" stroke="#06171c" stroke-width="1.5"/>' for center in payload["release_contract"]["centers"])
    f = payload["baseline_fates"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" data-motion-level="m2-agulhas-source-pathways"><title id="title">Agulhas source-tagged pathway fate sensitivity</title><desc id="desc">One hundred eight deterministic upstream pathway trials produce fourteen Cape Basin crossings, twenty-four return-corridor crossings, sixty-two unresolved paths, and eight terminations under the baseline gates. Nearby gate definitions change the census.</desc><metadata>Natural Earth SHA-256 {land_sha256}. {html.escape(payload['boundary'])}</metadata><defs><clipPath id="map-clip"><rect x="{x}" y="{y+42}" width="{width}" height="{height-42}" rx="15"/></clipPath><pattern id="quiet-land" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="8" height="8" fill="#fbfbf8"/><path d="M0 0V8" stroke="#607678" stroke-width=".45" stroke-opacity=".13"/></pattern><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.panel{{fill:#0a242b;stroke:#46666b}}.track{{fill:none;stroke-width:.85;stroke-linecap:round;stroke-linejoin:round;opacity:.55}}.fate-unresolved{{opacity:.25}}.gate{{stroke-width:1.25;stroke-dasharray:5 4}}.gate-label{{font-size:7.5px;font-weight:950;letter-spacing:.7px}}.land{{fill:url(#quiet-land);fill-rule:evenodd;stroke:#9aabaa;stroke-width:.7}}.card{{fill:#0d272e;stroke:#405e63}}.card-date{{fill:#eef9f7;font-size:12px;font-weight:950}}.card-total{{fill:#718d8f;font-size:8px;font-weight:900;text-anchor:end;letter-spacing:1px}}.card-values{{fill:#9cb2b1;font:850 9px ui-monospace,Consolas,monospace}}.card-note{{fill:#607d80;font-size:7.5px;font-weight:900;letter-spacing:.8px}}.sense-gate{{fill:#9bb1b0;font-size:8px;font-weight:900;letter-spacing:.7px}}.sense-values{{font:900 13px ui-monospace,Consolas,monospace}}.both{{fill:#d78cff;font-size:7px;font-weight:900}}.note{{fill:#a6bcba;font-size:10px}}.fine{{fill:#587477;font-size:8px}}</style></defs><rect width="1400" height="1020" fill="#06171c"/><text x="45" y="42" fill="#54d8d0" font-size="14" font-weight="900" letter-spacing="2.4">OSW / AGULHAS · M2 SOURCE-TAGGED PATHWAYS</text><text x="45" y="86" fill="#eef9f7" font-size="35" font-weight="950">THE FATE DEPENDS ON WHERE YOU DRAW THE GATE.</text><text x="45" y="117" fill="#9db3b2" font-size="12">Four upstream centers × nine nearby seeds × three release dates · 150 days · deterministic surface pathways</text><rect x="1060" y="37" width="295" height="30" rx="15" fill="#102a30" stroke="#f0cf70"/><text x="1207.5" y="57" fill="#f0cf70" text-anchor="middle" font-size="9.5" font-weight="950" letter-spacing="1">COUNTS · NOT LEAKAGE PERCENT</text><rect x="{x}" y="{y}" width="{width}" height="{height}" rx="17" class="panel"/><text x="{x+18}" y="{y+28}" fill="#eef9f7" font-size="15" font-weight="950">108 PATHS FROM ONE UPSTREAM LADDER</text><text x="{x+width-18}" y="{y+28}" fill="#789597" text-anchor="end" font-size="8" font-weight="900">BASELINE GATES 15°E / 35°E</text><g clip-path="url(#map-clip)">{track_layer(payload['tracks'])}{gate_layer()}<path d="{land_paths(geojson, MAP)}" class="land"/>{seeds}</g>{cards}<g transform="translate(800 570)"><text fill="#eef9f7" font-size="30" font-weight="950">{f['cape_basin']} · {f['return_corridor']} · {f['unresolved']} · {f['terminated']}</text><text y="25" fill="#8ba4a4" font-size="8" font-weight="900" letter-spacing="1">CAPE · RETURN · UNRESOLVED · TERMINATED</text><text y="54" class="note">Most paths reach neither threshold within 150 days.</text><text y="73" class="note">That unresolved majority is part of the result.</text><text y="101" class="fine">NO TRACK IS A UNIT OF WATER, VOLUME, OR HEAT.</text></g><text x="45" y="735" fill="#eef9f7" font-size="16" font-weight="950">NINE REASONABLE GATE PAIRS · NINE DIFFERENT CENSUSES</text><text x="45" y="759" class="note">C = Cape Basin · R = return corridor · U = unresolved · T = terminated. Gold outline marks the baseline.</text><g transform="translate(45 782)"><text fill="#ffad55" font-size="32" font-weight="950">2–20</text><text y="24" class="card-note">CAPE CROSSINGS</text><text y="56" fill="#54d8d0" font-size="32" font-weight="950">23–54</text><text y="80" class="card-note">RETURN CROSSINGS</text><text y="114" class="note">Gate placement is a method choice,</text><text y="133" class="note">not a harmless label.</text></g>{sensitivity}<text x="45" y="995" class="fine">NOMINAL 15 M · ONE HISTORICAL OSCAR YEAR · EQUAL-COUNT METHOD ENSEMBLE · STRICT WET STENCIL · NO DIFFUSION · NOT PROBABILITY, VOLUME, HEAT, OR CLIMATOLOGY</text></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m2-agulhas-source-pathways-2018.json"))
    parser.add_argument("--land-geojson", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-motion-agulhas-source-pathways-2018.svg"))
    args = parser.parse_args()
    land, digest = load_land(args.land_geojson)
    svg = build(json.loads(args.input.read_text(encoding="utf-8")), land, digest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

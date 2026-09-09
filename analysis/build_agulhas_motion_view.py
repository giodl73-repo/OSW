"""Render the Agulhas current-turn-return-leakage junction audit."""

from __future__ import annotations

import argparse
import html
import json
import pathlib

try:
    from build_arctic_entrances_motion_view import annual_vectors, land_paths, load_land, projection
    from simulate_oscar_pathways import load_assignment
except ModuleNotFoundError:
    from analysis.build_arctic_entrances_motion_view import annual_vectors, land_paths, load_land, projection
    from analysis.simulate_oscar_pathways import load_assignment


WIDTH, HEIGHT = 1400, 1020
MAP = {
    "box": (45, 150, 890, 700),
    "domain": (5, 55, -48, -25),
    "center": (30, -36.5),
}
ROLE_COLORS = {
    "boundary-current": "#ffad55",
    "retroflection": "#d78cff",
    "return-current": "#54d8d0",
    "cape-basin": "#719cff",
}


def rectangle_path(extent: dict) -> str:
    screen = projection(MAP)
    points = [
        screen(extent["west"], extent["north"]),
        screen(extent["east"], extent["north"]),
        screen(extent["east"], extent["south"]),
        screen(extent["west"], extent["south"]),
    ]
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in points) + "Z"


def track_path(track: dict) -> str:
    screen = projection(MAP)
    points = [screen(point["longitude"], point["latitude"]) for point in track["points"]]
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in points)


def track_layer(tracks: list[dict]) -> str:
    parts = []
    for track in tracks:
        role = track["seed"]["role"]
        color = ROLE_COLORS[role]
        end_x, end_y = projection(MAP)(track["points"][-1]["longitude"], track["points"][-1]["latitude"])
        parts.append(
            f'<path d="{track_path(track)}" stroke="{color}" class="track"/>'
            f'<circle cx="{end_x:.1f}" cy="{end_y:.1f}" r="2.2" fill="#07191e" stroke="{color}" stroke-width="1"/>'
        )
    return "".join(parts)


def window_layer(windows: list[dict]) -> str:
    labels = {
        "boundary-current": (33.7, -30.0, "1 · CURRENT"),
        "retroflection": (17.0, -41.2, "2 · TURN"),
        "return-current": (43.5, -43.0, "3 · RETURN"),
        "cape-basin": (6.0, -31.0, "4 · LEAKAGE FIELD"),
    }
    screen = projection(MAP)
    parts = []
    for window in windows:
        color = ROLE_COLORS[window["id"]]
        x, y = screen(*labels[window["id"]][:2])
        parts.append(
            f'<path d="{rectangle_path(window["extent"])}" stroke="{color}" class="window"/>'
            f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" class="map-label">{labels[window["id"]][2]}</text>'
        )
    return "".join(parts)


def metric_card(window: dict, x: int, y: int) -> str:
    annual = window["annual"]
    color = ROLE_COLORS[window["id"]]
    direction = {
        "boundary-current": f"{annual['southward_fraction']:.0%} SOUTHWARD",
        "retroflection": f"{annual['vector_coherence']:.0%} NET COHERENCE",
        "return-current": f"{annual['eastward_fraction']:.0%} EASTWARD",
        "cape-basin": f"{annual['vector_coherence']:.0%} NET COHERENCE",
    }[window["id"]]
    return f'''<g transform="translate({x} {y})"><rect width="400" height="111" rx="13" class="card"/><rect width="5" height="111" rx="2.5" fill="{color}"/><text x="21" y="26" fill="{color}" class="card-kicker">{window['role'].upper()}</text><text x="21" y="54" class="card-value">{annual['mean_speed_m_s']:.2f} m/s</text><text x="207" y="54" class="card-value">{direction}</text><text x="21" y="77" class="card-label">MEAN SAMPLE SPEED</text><text x="21" y="97" class="card-note">{window['name'].upper()}</text></g>'''


def build(analysis: dict, velocity: dict, geojson: dict, land_sha256: str) -> str:
    cards = "".join(metric_card(window, 960, 180 + index * 128) for index, window in enumerate(analysis["windows"]))
    map_x, map_y, map_width, map_height = MAP["box"]
    screen = projection(MAP)
    cape_x, cape_y = screen(18.5, -34.8)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" data-motion-level="m2-agulhas-junction"><title id="title">The Agulhas junction</title><desc id="desc">Historical surface velocity and seasonal deterministic tracks distinguish the southwestward Agulhas Current, its energetic retroflection, the eastward return current, and variable westward leakage into the Cape Basin.</desc><metadata>Natural Earth SHA-256 {land_sha256}. Beal et al. 2011 doi:10.1038/nature09983. Richardson 2007 doi:10.1016/j.dsr.2007.04.010. {html.escape(analysis['boundary'])}</metadata><defs><clipPath id="map-clip"><rect x="{map_x}" y="{map_y+42}" width="{map_width}" height="{map_height-42}" rx="15"/></clipPath><pattern id="quiet-land" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="8" height="8" fill="#fbfbf8"/><path d="M0 0V8" stroke="#607678" stroke-width=".45" stroke-opacity=".13"/></pattern>{''.join(f'<marker id="arrow-{color}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#{color}"/></marker>' for color in ('ffb454','62d7ce','7e9dff'))}<style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.map-panel{{fill:#0a242b;stroke:#46666b}}.track{{fill:none;stroke-width:1.15;stroke-linecap:round;stroke-linejoin:round;opacity:.72}}.window{{fill:none;stroke-width:.75;stroke-dasharray:3 4;opacity:.5}}.land{{fill:url(#quiet-land);fill-rule:evenodd;stroke:#9aabaa;stroke-width:.75}}.map-label{{font-size:8px;font-weight:950;letter-spacing:1px}}.card{{fill:#0d272e;stroke:#405e63}}.card-kicker{{font-size:8px;font-weight:950;letter-spacing:1px}}.card-value{{fill:#eef9f7;font:900 17px ui-monospace,Consolas,monospace}}.card-label{{fill:#718d8f;font-size:7px;font-weight:900;letter-spacing:.8px}}.card-note{{fill:#9cb2b1;font-size:8px;font-weight:800}}.note{{fill:#a6bcba;font-size:10px}}.fine{{fill:#587477;font-size:8px}}</style></defs><rect width="1400" height="1020" fill="#06171c"/><text x="45" y="42" fill="#54d8d0" font-size="14" font-weight="900" letter-spacing="2.4">OSW / SOUTHERN AFRICA · M2 JUNCTION AUDIT</text><text x="45" y="86" fill="#eef9f7" font-size="35" font-weight="950">THE CURRENT TURNS. SOME WATER ESCAPES.</text><text x="45" y="117" fill="#9db3b2" font-size="12">71 historical surface-velocity fields · 28 seasonal deterministic tracks · December 2017–November 2018</text><rect x="1060" y="37" width="295" height="30" rx="15" fill="#102a30" stroke="#f0cf70"/><text x="1207.5" y="57" fill="#f0cf70" text-anchor="middle" font-size="9.5" font-weight="950" letter-spacing="1">PATHWAYS · NOT HEAT TRANSPORT</text><rect x="{map_x}" y="{map_y}" width="{map_width}" height="{map_height}" rx="17" class="map-panel"/><text x="{map_x+18}" y="{map_y+28}" fill="#eef9f7" font-size="16" font-weight="950">ONE JUNCTION · FOUR MOTION ROLES</text><text x="{map_x+map_width-18}" y="{map_y+28}" fill="#789597" text-anchor="end" font-size="8" font-weight="900" letter-spacing="1">ANNUAL VECTORS + 45-DAY TRACKS</text><g clip-path="url(#map-clip)">{annual_vectors(velocity, MAP)}{window_layer(analysis['windows'])}{track_layer(analysis['tracks'])}<path d="{land_paths(geojson, MAP)}" class="land"/><circle cx="{cape_x:.1f}" cy="{cape_y:.1f}" r="3.5" fill="#fbfbf8"/><text x="{cape_x-9:.1f}" y="{cape_y-9:.1f}" fill="#eef9f7" text-anchor="end" font-size="8" font-weight="900">CAPE OF GOOD HOPE</text></g>{cards}<g transform="translate(960 714)"><text fill="#eef9f7" font-size="14" font-weight="950">WHY THE MEAN ARROW FAILS</text><text y="25" class="note">The turning and leakage sectors remain energetic</text><text y="43" class="note">while their net vectors nearly cancel. Low coherence</text><text y="61" class="note">here means changing directions—not still water.</text><text y="89" class="note">Rings and filaments export Indian Ocean water</text><text y="107" class="note">westward episodically; this surface map cannot</text><text y="125" class="note">measure their volume or heat transport.</text></g><rect x="45" y="880" width="1310" height="91" rx="14" fill="#0d242a"/><text x="67" y="907" fill="#eef9f7" font-size="14" font-weight="950">READ THE SYSTEM AS A VERB</text><text x="67" y="931" class="note">Current → turn → return is the dominant geometry. Leakage is not a second continuous river; it is an intermittent field of rings, cyclones, and direct-flow fragments.</text><text x="67" y="951" class="fine">DIAGNOSTIC BOXES ARE WINDOWS, NOT BORDERS · NATIVE 1/3° OSCAR GRID · NOMINAL 15 M · NO TEMPERATURE, SALINITY, DEPTH, VOLUME, OR HEAT WEIGHTING</text><text x="45" y="997" class="fine">FORWARD RK4 · 6-HOUR STEP · DAILY OUTPUT · STRICT WET STENCIL · FOUR SEASONAL RELEASES · ALL 28 TRACKS COMPLETED · SOURCE CHECKSUMS IN RESEARCH RECEIPT</text></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=pathlib.Path, default=pathlib.Path("research/osw-m2-agulhas-motion-2018.json"))
    parser.add_argument("--velocity", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-agulhas-native-2018.js"))
    parser.add_argument("--land-geojson", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-motion-agulhas-junction-2018.svg"))
    args = parser.parse_args()
    land, digest = load_land(args.land_geojson)
    svg = build(json.loads(args.analysis.read_text(encoding="utf-8")), load_assignment(args.velocity), land, digest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

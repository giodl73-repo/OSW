"""Render the attributed GEOMAR/INALT20 Agulhas transport replication."""

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
MAP = {"box": (45, 155, 735, 610), "domain": (3, 35, -45, -32), "center": (19, -38.5)}
TRACK_COLORS = ("#d78cff", "#ffad55", "#54d8d0", "#719cff")


def line_path(points: list[dict]) -> str:
    screen = projection(MAP)
    return "M" + "L".join(f"{screen(point['longitude'], point['latitude'])[0]:.1f},{screen(point['longitude'], point['latitude'])[1]:.1f}" for point in points)


def section_layer(points: list[dict]) -> str:
    parts = []
    for number in range(1, 7):
        group = [point for point in points if point["section_number"] == number]
        if not group:
            continue
        name = group[0]["section"]
        color = "#ffad55" if name in ("west", "northwest") else "#eef9f7" if name == "release" else "#54d8d0" if name == "east" else "#607d80"
        width = 3.2 if name in ("west", "northwest", "release", "east") else 1.1
        parts.append(f'<path d="{line_path(group)}" stroke="{color}" stroke-width="{width}" class="section"/>')
    return "".join(parts)


def trajectory_layer(trajectories: list[dict]) -> str:
    return "".join(f'<path d="{line_path(track["points"])}" stroke="{color}" class="track"/>' for track, color in zip(trajectories, TRACK_COLORS))


def time_series(annual: list[dict], x: int, y: int, width: int, height: int) -> str:
    years = [item["release_year"] for item in annual]
    values = [item["leakage_sv"] for item in annual]
    min_year, max_year = min(years), max(years)
    min_value, max_value = 4.0, 17.0
    def point(year: int, value: float) -> tuple[float, float]:
        return x + (year - min_year) / (max_year - min_year) * width, y + height - (value - min_value) / (max_value - min_value) * height
    path = "M" + "L".join(f"{point(year, value)[0]:.1f},{point(year, value)[1]:.1f}" for year, value in zip(years, values))
    grid = "".join(f'<path d="M{x},{point(min_year, value)[1]:.1f}H{x+width}" class="grid"/><text x="{x-10}" y="{point(min_year, value)[1]+3:.1f}" class="axis" text-anchor="end">{value}</text>' for value in (5, 10, 15))
    ticks = "".join(f'<text x="{point(year, min_value)[0]:.1f}" y="{y+height+20}" class="axis" text-anchor="middle">{year}</text>' for year in (1960, 1980, 2000, 2014))
    return f'{grid}<path d="{path}" class="series"/>{ticks}'


def build(payload: dict, geojson: dict, land_sha256: str) -> str:
    x, y, width, height = MAP["box"]
    leakage = payload["leakage"]
    east = payload["return_current_east_exit"]
    screen = projection(MAP)
    release_label = screen(31.8, -32.1); west_label = screen(6.2, -37.5); east_label = screen(34.7, -38.5)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" data-motion-level="m3-geomar-agulhas-replication"><title id="title">Published Agulhas leakage transport replication</title><desc id="desc">Exact archived experiment sections and four example trajectories accompany the 1958 to 2014 transport-weighted leakage series. West plus Northwest exits average 9.894 Sverdrups.</desc><metadata>GEOMAR archive {payload['archive']['handle']}; {payload['archive']['license']}; {html.escape(payload['boundary'])} Natural Earth SHA-256 {land_sha256}.</metadata><defs><clipPath id="map-clip"><rect x="{x}" y="{y+42}" width="{width}" height="{height-42}" rx="15"/></clipPath><pattern id="quiet-land" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="8" height="8" fill="#fbfbf8"/><path d="M0 0V8" stroke="#607678" stroke-width=".45" stroke-opacity=".13"/></pattern><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.panel{{fill:#0a242b;stroke:#46666b}}.land{{fill:url(#quiet-land);fill-rule:evenodd;stroke:#9aabaa;stroke-width:.7}}.track{{fill:none;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round;opacity:.82}}.section{{fill:none;stroke-linecap:round;stroke-linejoin:round}}.map-label{{font-size:8px;font-weight:950;letter-spacing:.7px}}.grid{{stroke:#36545a;stroke-width:.7}}.axis{{fill:#718d8f;font-size:8px}}.series{{fill:none;stroke:#ffad55;stroke-width:2.4;stroke-linejoin:round}}.metric{{fill:#eef9f7;font:950 31px ui-monospace,Consolas,monospace}}.metric-label{{fill:#789597;font-size:8px;font-weight:900;letter-spacing:1px}}.note{{fill:#a6bcba;font-size:10px}}.fine{{fill:#587477;font-size:8px}}</style></defs><rect width="1400" height="1020" fill="#06171c"/><text x="45" y="42" fill="#54d8d0" font-size="14" font-weight="900" letter-spacing="2.4">OSW / AGULHAS · PUBLISHED M3 REPLICATION</text><text x="45" y="86" fill="#eef9f7" font-size="35" font-weight="950">THE LEAKAGE GATE IS A BENT LINE.</text><text x="45" y="117" fill="#9db3b2" font-size="12">Exact archived experiment sections · four example 3-D paths · 57 transport-weighted release years</text><rect x="1048" y="37" width="307" height="30" rx="15" fill="#102a30" stroke="#f0cf70"/><text x="1201.5" y="57" fill="#f0cf70" text-anchor="middle" font-size="9.5" font-weight="950" letter-spacing="1">ATTRIBUTED MODEL OUTPUT · CC BY 4.0</text><rect x="{x}" y="{y}" width="{width}" height="{height}" rx="17" class="panel"/><text x="{x+18}" y="{y+28}" fill="#eef9f7" font-size="15" font-weight="950">THE AUTHORS' ACTUAL EXIT GEOMETRY</text><text x="{x+width-18}" y="{y+28}" fill="#789597" text-anchor="end" font-size="8" font-weight="900">SCHMIDT ET AL. · EXPERIMENT P</text><g clip-path="url(#map-clip)">{trajectory_layer(payload['example_trajectories'])}{section_layer(payload['section_geometry'])}<path d="{land_paths(geojson, MAP)}" class="land"/></g><text x="{release_label[0]:.1f}" y="{release_label[1]+18:.1f}" class="map-label" text-anchor="end" fill="#eef9f7">32°S RELEASE</text><text x="{west_label[0]:.1f}" y="{west_label[1]:.1f}" class="map-label" fill="#ffad55">WEST + NORTHWEST = LEAKAGE</text><text x="{east_label[0]:.1f}" y="{east_label[1]:.1f}" class="map-label" text-anchor="end" fill="#54d8d0">EAST = RETURN EXIT</text><g transform="translate(825 168)"><text fill="#eef9f7" font-size="15" font-weight="950">PUBLISHED LEAKAGE SERIES</text><text y="22" class="metric-label">WEST + NORTHWEST · RELEASE YEAR</text>{time_series(payload['annual'], 35, 55, 485, 230)}<text x="35" y="340" class="metric">{leakage['mean_sv']:.3f} Sv</text><text x="35" y="362" class="metric-label">1958–2014 MEAN</text><text x="300" y="340" class="metric">±{leakage['population_standard_deviation_sv']:.3f}</text><text x="300" y="362" class="metric-label">POPULATION SD · SV</text><text x="35" y="420" fill="#ffad55" font-size="24" font-weight="950">+{leakage['linear_trend_sv_per_decade']:.3f} Sv / decade</text><text x="35" y="443" class="metric-label">UNWEIGHTED LINEAR FIT · ARCHIVED PERIOD</text><text x="35" y="485" class="note">This recomputes the authors' archived model result.</text><text x="35" y="505" class="note">It is not a new OSW simulation or a universal value.</text></g><rect x="45" y="800" width="1310" height="151" rx="14" fill="#0b242a" stroke="#38585e"/><text x="68" y="829" fill="#eef9f7" font-size="15" font-weight="950">THE JUNCTION NOW HAS TRANSPORT WEIGHTS</text><text x="68" y="868" fill="#ffad55" font-size="31" font-weight="950">{leakage['mean_sv']:.2f} Sv</text><text x="68" y="891" class="metric-label">WEST + NORTHWEST LEAKAGE EXITS</text><text x="400" y="868" fill="#54d8d0" font-size="31" font-weight="950">{east['mean_sv']:.2f} Sv</text><text x="400" y="891" class="metric-label">EAST RETURN-CURRENT EXIT</text><text x="790" y="852" class="note">The return current is larger than leakage in this experiment,</text><text x="790" y="873" class="note">but the leakage is not one straight gate: a diagonal western</text><text x="790" y="894" class="note">leg joins a zonal northwest leg around the Cape Basin.</text><text x="68" y="927" class="fine">SOURCE: SCHMIDT, SCHWARZKOPF, RÜHS &amp; BIASTOCH · INALT20 / PARCELS DERIVED OUTPUT · CC BY 4.0 · POPULATION SD IS DESCRIPTIVE, NOT AN UNCERTAINTY INTERVAL</text><text x="45" y="990" class="fine">CHECKSUM-PINNED NETCDF · ATTRIBUTED RECALCULATION · NOT OBSERVATION-ONLY, PRESENT-DAY MONITORING, OR AN OSW MODEL RUN · FULL RECEIPT IN RESEARCH/</text></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m3-geomar-agulhas-published-replication.json"))
    parser.add_argument("--land-geojson", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m3-geomar-agulhas-published-replication.svg"))
    args = parser.parse_args()
    land, digest = load_land(args.land_geojson)
    svg = build(json.loads(args.input.read_text(encoding="utf-8")), land, digest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

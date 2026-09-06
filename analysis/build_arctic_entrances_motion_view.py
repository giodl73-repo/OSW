"""Render the paired Fram and Barents historical surface-motion screens."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import pathlib
import urllib.request

from pyproj import Transformer

try:
    from simulate_oscar_pathways import load_assignment
except ModuleNotFoundError:
    from analysis.simulate_oscar_pathways import load_assignment


WIDTH, HEIGHT = 1400, 1020
LAND_COMMIT = "ca96624a56bd078437bca8184e78163e5039ad19"
LAND_URL = f"https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{LAND_COMMIT}/geojson/ne_110m_land.geojson"
LAND_SHA256 = "9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9"
PANELS = {
    "fram": {"box": (50, 160, 635, 565), "domain": (-20, 20, 72, 80), "center": (0, 76), "title": "FRAM STRAIT", "subtitle": "OPPOSING SURFACE LANES"},
    "barents": {"box": (715, 160, 635, 565), "domain": (20, 60, 68, 80), "center": (40, 74), "title": "BARENTS SEA OPENING", "subtitle": "EASTWARD SURFACE ENTRANCE"},
}
SEASONS = ("DJF", "MAM", "JJA", "SON")


def normalize_longitude(value: float) -> float:
    return value - 360 if value > 180 else value


def projection(panel: dict):
    lon0, lat0 = panel["center"]
    transformer = Transformer.from_crs("EPSG:4326", f"+proj=laea +lat_0={lat0} +lon_0={lon0} +R=6371008.8", always_xy=True)
    west, east, south, north = panel["domain"]
    samples = []
    for index in range(41):
        fraction = index / 40
        lon = west + (east - west) * fraction
        lat = south + (north - south) * fraction
        samples.extend((transformer.transform(lon, south), transformer.transform(lon, north), transformer.transform(west, lat), transformer.transform(east, lat)))
    min_x, max_x = min(p[0] for p in samples), max(p[0] for p in samples)
    min_y, max_y = min(p[1] for p in samples), max(p[1] for p in samples)
    x, y, width, height = panel["box"]
    pad = 18
    scale = min((width - 2 * pad) / (max_x - min_x), (height - 88) / (max_y - min_y))
    def screen(longitude: float, latitude: float) -> tuple[float, float]:
        px, py = transformer.transform(longitude, latitude)
        return x + width / 2 + (px - (min_x + max_x) / 2) * scale, y + 59 + (max_y - py) * scale
    return screen


def annual_vectors(payload: dict, panel: dict) -> str:
    rows, columns = payload["shape"][1:]
    screen = projection(panel)
    parts = []
    for row in range(1, rows - 1, 3):
        latitude = payload["latitude_values"][row]
        for column in range(1, columns - 1, 3):
            index = row * columns + column
            pairs = [(frame["u_mm_s"][index], frame["v_mm_s"][index]) for frame in payload["frames"]]
            pairs = [(u, v) for u, v in pairs if u is not None and v is not None]
            if len(pairs) < 50:
                continue
            u = sum(pair[0] for pair in pairs) / len(pairs) / 1000
            v = sum(pair[1] for pair in pairs) / len(pairs) / 1000
            speed = math.hypot(u, v)
            if speed < .015:
                continue
            longitude = normalize_longitude(payload["longitude_values"][column])
            length = 0.38 + min(speed, .45) * 2.4
            cosine = max(.2, math.cos(math.radians(latitude)))
            end_lon = longitude + u / speed * length / cosine
            end_lat = latitude + v / speed * length
            sx, sy = screen(longitude, latitude); ex, ey = screen(end_lon, end_lat)
            color = "#ffb454" if speed >= .12 else "#62d7ce" if speed >= .06 else "#7e9dff"
            opacity = min(.9, .38 + speed * 2.2)
            parts.append(f'<path d="M{sx:.1f},{sy:.1f}L{ex:.1f},{ey:.1f}" stroke="{color}" stroke-width="1.5" opacity="{opacity:.2f}" marker-end="url(#arrow-{color[1:]})"/>')
    return "".join(parts)


def land_paths(geojson: dict, panel: dict) -> str:
    screen = projection(panel)
    west, east, south, north = panel["domain"]
    commands = []
    for feature in geojson["features"]:
        geometry = feature["geometry"]
        polygons = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
        for polygon in polygons:
            for ring in polygon:
                normalized = [(normalize_longitude(point[0]), point[1]) for point in ring]
                if not any(west - 15 <= lon <= east + 15 and south - 10 <= lat <= north + 10 for lon, lat in normalized):
                    continue
                points = []
                for lon, lat in normalized:
                    try:
                        px, py = screen(lon, lat)
                    except Exception:
                        continue
                    if math.isfinite(px) and math.isfinite(py):
                        points.append((px, py))
                if points:
                    commands.append("M" + "L".join(f"{px:.1f},{py:.1f}" for px, py in points) + "Z")
    return "".join(commands)


def gate_overlay(name: str, entrance: dict, panel: dict) -> str:
    screen = projection(panel)
    if name == "fram":
        latitude = entrance["sampled_fixed_coordinate"]
        segments = ((-10, 0, "#7e9dff", "EXPORT"), (.3333333, 4.6666667, "#8ca6a8", "TURN"), (5, 15, "#ffb454", "INFLOW"))
        parts = []
        for west, east, color, label in segments:
            x1, y1 = screen(west, latitude); x2, y2 = screen(east, latitude)
            parts.append(f'<path d="M{x1:.1f},{y1:.1f}L{x2:.1f},{y2:.1f}" stroke="{color}" stroke-width="6"/><text x="{(x1+x2)/2:.1f}" y="{y1-9:.1f}" class="gate-label">{label}</text>')
        return "".join(parts)
    longitude = entrance["sampled_fixed_coordinate"]
    x1, y1 = screen(longitude, 71); x2, y2 = screen(longitude, 74.6666667)
    return f'<path d="M{x1:.1f},{y1:.1f}L{x2:.1f},{y2:.1f}" stroke="#ffb454" stroke-width="6"/><text x="{x2+10:.1f}" y="{y2+4:.1f}" class="gate-label" text-anchor="start">INFLOW SCREEN</text>'


def season_strip(name: str, entrance: dict, panel: dict) -> str:
    x, y, width, height = panel["box"]
    if name == "fram":
        series = next(lane for lane in entrance["lanes"] if lane["name"] == "eastern inflow lane")["seasons"]
        caption = "EASTERN INFLOW LANE · NORTHWARD M/S"
    else:
        series = entrance["seasons"]
        caption = "FULL SCREEN · EASTWARD M/S"
    baseline = y + height - 27
    parts = [f'<text x="{x+18}" y="{baseline-47}" class="strip-label">{caption}</text>']
    for index, item in enumerate(series):
        sx = x + 245 + index * 88
        value = item["mean_normal_velocity_m_s"]
        top = baseline - value * 1200
        parts.append(f'<line x1="{sx}" y1="{baseline}" x2="{sx}" y2="{top:.1f}" stroke="#ffb454" stroke-width="9" stroke-linecap="round"/><text x="{sx}" y="{baseline+17}" class="season">{item["season"]}</text><text x="{sx}" y="{top-8:.1f}" class="value">{value:+.3f}</text>')
    return "".join(parts)


def build(analysis: dict, payloads: dict, geojson: dict, land_sha256: str) -> str:
    entrance_by_name = {item["name"].split()[0].lower(): item for item in analysis["entrances"]}
    panels = []
    for name in ("fram", "barents"):
        panel = PANELS[name]; x, y, width, height = panel["box"]
        entrance = entrance_by_name[name]
        panels.append(f'''<g aria-label="{panel['title']}"><rect x="{x}" y="{y}" width="{width}" height="{height}" rx="18" class="panel"/><clipPath id="clip-{name}"><rect x="{x}" y="{y+45}" width="{width}" height="{height-110}"/></clipPath><text x="{x+18}" y="{y+30}" class="panel-title">{panel['title']}</text><text x="{x+width-18}" y="{y+29}" class="panel-sub">{panel['subtitle']}</text><g clip-path="url(#clip-{name})">{annual_vectors(payloads[name], panel)}<path d="{land_paths(geojson, panel)}" class="land"/>{gate_overlay(name, entrance, panel)}</g>{season_strip(name, entrance, panel)}</g>''')
    fram = entrance_by_name["fram"]
    west = next(lane for lane in fram["lanes"] if lane["name"] == "western export lane")["annual_frame_weighted_mean_normal_velocity_m_s"]
    east = next(lane for lane in fram["lanes"] if lane["name"] == "eastern inflow lane")["annual_frame_weighted_mean_normal_velocity_m_s"]
    barents = entrance_by_name["barents"]["annual_frame_weighted_mean_normal_velocity_m_s"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" data-motion-level="m2-arctic-entrances"><title id="title">Paired Atlantic-Arctic surface entrances</title><desc id="desc">One historical year of nominal-fifteen-metre OSCAR motion shows opposing surface lanes in Fram Strait and an eastward surface entrance through the Barents Sea Opening. These are motion screens, not heat transport.</desc><metadata>Natural Earth {LAND_COMMIT}, SHA-256 {land_sha256}. {html.escape(analysis['boundary'])}</metadata><defs><pattern id="quiet-land" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="8" height="8" fill="#f8f8f5"/><path d="M0 0V8" stroke="#506b6e" stroke-width=".5" stroke-opacity=".14"/></pattern>{''.join(f'<marker id="arrow-{color}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#{color}"/></marker>' for color in ('ffb454','62d7ce','7e9dff'))}<style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.panel{{fill:#0b252c;stroke:#49666b}}.panel-title{{fill:#eef9f7;font-size:18px;font-weight:950}}.panel-sub{{fill:#799597;font-size:8.5px;font-weight:900;letter-spacing:1px;text-anchor:end}}.land{{fill:url(#quiet-land);fill-rule:evenodd;stroke:#9aabaa;stroke-width:.7}}.gate-label{{fill:#eef9f7;font-size:8px;font-weight:950;text-anchor:middle;letter-spacing:.8px}}.strip-label{{fill:#8da8a8;font-size:8px;font-weight:900;letter-spacing:1px}}.season{{fill:#8da8a8;font-size:8px;font-weight:900;text-anchor:middle}}.value{{fill:#eef9f7;font:800 8px ui-monospace,Consolas,monospace;text-anchor:middle}}.metric{{fill:#eef9f7;font:950 25px ui-monospace,Consolas,monospace}}.metric-label{{fill:#8da8a8;font-size:8.5px;font-weight:900;letter-spacing:1px}}.note{{fill:#a8bfbd;font-size:10px}}.fine{{fill:#607d80;font-size:8px}}</style></defs><rect width="1400" height="1020" fill="#06171c"/><text x="50" y="44" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.4">OSW / ARCTIC HEAT ROUTES · M2 PAIRED ENTRANCES</text><text x="50" y="88" fill="#eef9f7" font-size="35" font-weight="950">ONE ARCTIC ENTRANCE IS REALLY TWO</text><text x="50" y="119" fill="#9db3b2" font-size="12">Fram Strait + Barents Sea Opening · 71 historical OSCAR fields · December 2017–November 2018 · nominal 15 m</text><rect x="1055" y="39" width="295" height="30" rx="15" fill="#102a30" stroke="#f0cf70"/><text x="1202.5" y="59" fill="#f0cf70" text-anchor="middle" font-size="9.5" font-weight="950" letter-spacing="1">SURFACE MOTION · NOT HEAT TRANSPORT</text>{''.join(panels)}<g transform="translate(50 782)"><text class="metric">{west:+.3f} m/s</text><text y="22" class="metric-label">FRAM WEST · SOUTHWARD EXPORT</text><text x="405" class="metric">{east:+.3f} m/s</text><text x="405" y="22" class="metric-label">FRAM EAST · NORTHWARD INFLOW</text><text x="840" class="metric">{barents:+.3f} m/s</text><text x="840" y="22" class="metric-label">BARENTS · EASTWARD INFLOW</text></g><rect x="50" y="852" width="1300" height="112" rx="14" fill="#0d242a"/><text x="72" y="878" fill="#eef9f7" font-size="14" font-weight="950">THE LANDMASS LESSON</text><text x="72" y="902" class="note">Fram is a two-way street at the surface: averaging the whole strait hides a northward Atlantic-side lane inside stronger western export.</text><text x="72" y="922" class="note">Barents is a second route, but it carries Atlantic water onto a shallow shelf where much more heat can be released before the water reaches the central Arctic.</text><text x="72" y="945" class="fine">UNWEIGHTED GRID-SCREEN VELOCITY · ONE HISTORICAL YEAR · OLDER OSCAR 2017.0 · NO DEPTH, TEMPERATURE, SALINITY, VOLUME, HEAT, OR WATER-MASS CLASSIFICATION · FRAM CLIPPED AT OSCAR'S 80°N LIMIT</text><text x="50" y="992" fill="#536f72" font-size="8">SOURCE FILES CHECKSUM-PINNED IN THE ANALYSIS RECEIPT · NATURAL EARTH COASTLINES {land_sha256[:16]}…</text></svg>'''


def load_land(path: pathlib.Path | None) -> tuple[dict, str]:
    raw = path.read_bytes() if path else urllib.request.urlopen(LAND_URL, timeout=60).read()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != LAND_SHA256:
        raise ValueError(f"Natural Earth checksum {digest} != {LAND_SHA256}")
    return json.loads(raw), digest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=pathlib.Path, default=pathlib.Path("research/osw-m2-arctic-entrances-motion-2018.json"))
    parser.add_argument("--fram", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-fram-native-2018.js"))
    parser.add_argument("--barents", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-barents-native-2018.js"))
    parser.add_argument("--land-geojson", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-motion-arctic-entrances-2018.svg"))
    args = parser.parse_args()
    land, digest = load_land(args.land_geojson)
    svg = build(json.loads(args.analysis.read_text(encoding="utf-8")), {"fram": load_assignment(args.fram), "barents": load_assignment(args.barents)}, land, digest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

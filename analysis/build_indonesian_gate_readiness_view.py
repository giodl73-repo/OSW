"""Render the Indonesian Throughflow gate-resolvability audit."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import pathlib
import urllib.request

from pyproj import Transformer
from shapely.geometry import box, shape

try:
    from simulate_oscar_pathways import load_assignment
except ModuleNotFoundError:
    from analysis.simulate_oscar_pathways import load_assignment


WIDTH, HEIGHT = 1400, 980
LAND_COMMIT = "ca96624a56bd078437bca8184e78163e5039ad19"
LAND_URL = f"https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{LAND_COMMIT}/geojson/ne_10m_land.geojson"
LAND_SHA256 = "1ac90796408bc6ad6911d69448485d3c4dbf2190370080368a09976e1c9f7416"
DOMAIN = (105, 140, -15, 10)
MAP_BOX = (45, 155, 850, 660)
COLORS = {"usable_surface_hint": "#62d7ce", "surface_sign_conflict": "#ff7d72", "direction_only_underresolved": "#f0cf70", "not_screenable": "#71898b"}


def load_land(path: pathlib.Path | None) -> tuple[dict, str]:
    raw = path.read_bytes() if path else urllib.request.urlopen(LAND_URL, timeout=60).read()
    digest = hashlib.sha256(raw).hexdigest()
    expected = None if path else LAND_SHA256
    if expected and digest != expected:
        raise ValueError(f"Natural Earth checksum mismatch: {digest}")
    return json.loads(raw), digest


def projector():
    transformer = Transformer.from_crs("EPSG:4326", "+proj=laea +lat_0=-3 +lon_0=122.5 +R=6371008.8", always_xy=True)
    west, east, south, north = DOMAIN
    samples = [transformer.transform(lon, lat) for lon in (west, east) for lat in (south, north)]
    samples += [transformer.transform(west + (east-west)*i/40, lat) for i in range(41) for lat in (south, north)]
    min_x, max_x = min(x for x, _ in samples), max(x for x, _ in samples)
    min_y, max_y = min(y for _, y in samples), max(y for _, y in samples)
    x0, y0, width, height = MAP_BOX
    scale = min((width - 25) / (max_x-min_x), (height - 25) / (max_y-min_y))
    def screen(lon: float, lat: float) -> tuple[float, float]:
        x, y = transformer.transform(lon, lat)
        return x0 + width/2 + (x-(min_x+max_x)/2)*scale, y0 + height/2 + ((min_y+max_y)/2-y)*scale
    return screen


def ring_path(coords, screen) -> str:
    points = [screen(lon, lat) for lon, lat, *_ in coords]
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in points) + "Z"


def land_path(geojson: dict) -> str:
    screen = projector()
    clip = box(103, -17, 142, 12)
    paths = []
    for feature in geojson["features"]:
        geometry = shape(feature["geometry"])
        if not geometry.intersects(clip):
            continue
        clipped = geometry.intersection(clip)
        polygons = [clipped] if clipped.geom_type == "Polygon" else list(clipped.geoms) if clipped.geom_type == "MultiPolygon" else []
        for polygon in polygons:
            paths.append(ring_path(polygon.exterior.coords, screen))
            paths.extend(ring_path(interior.coords, screen) for interior in polygon.interiors)
    return "".join(paths)


def vectors(payload: dict) -> str:
    screen = projector(); rows, columns = payload["shape"][1:]
    parts = []
    for row in range(2, rows-2, 4):
        lat = payload["latitude_values"][row]
        for column in range(2, columns-2, 4):
            index = row*columns+column
            pairs = [(frame["u_mm_s"][index], frame["v_mm_s"][index]) for frame in payload["frames"]]
            pairs = [(u, v) for u, v in pairs if u is not None and v is not None]
            if len(pairs) < 60:
                continue
            u = sum(pair[0] for pair in pairs)/len(pairs)/1000; v = sum(pair[1] for pair in pairs)/len(pairs)/1000
            speed = math.hypot(u, v)
            if speed < .025:
                continue
            lon = payload["longitude_values"][column]
            length = .25 + min(speed, .5)*1.5
            sx, sy = screen(lon, lat); ex, ey = screen(lon + u/speed*length/max(.4, math.cos(math.radians(lat))), lat + v/speed*length)
            parts.append(f'<path d="M{sx:.1f},{sy:.1f}L{ex:.1f},{ey:.1f}" marker-end="url(#arrow)"/>')
    return "".join(parts)


def gate_marks(gates: list[dict]) -> str:
    screen = projector(); parts = []
    label_offsets = {"MAK": (-35, -20), "LIF": (12, -17), "LOM": (-44, 30), "OMB": (12, -16), "TIM": (14, 30)}
    for gate in gates:
        color = COLORS[gate["verdict"]]
        points = gate["point_support"]
        x1, y1 = screen(points[0]["longitude"], points[0]["latitude"]); x2, y2 = screen(points[-1]["longitude"], points[-1]["latitude"])
        parts.append(f'<path d="M{x1:.1f},{y1:.1f}L{x2:.1f},{y2:.1f}" stroke="{color}" class="gate"/>')
        for point in points:
            x, y = screen(point["longitude"], point["latitude"])
            if point["finite_frames"] == 71:
                parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}" stroke="#06171c" stroke-width="1.5"/>')
            else:
                parts.append(f'<path d="M{x-4:.1f},{y-4:.1f}l8,8m0,-8l-8,8" stroke="{color}" stroke-width="2"/>')
        mx, my = (x1+x2)/2, (y1+y2)/2; dx, dy = label_offsets[gate["code"]]
        parts.append(f'<text x="{mx+dx:.1f}" y="{my+dy:.1f}" fill="{color}" class="gate-code">{gate["code"]}</text>')
    return "".join(parts)


def card(gate: dict, index: int) -> str:
    x, y = 930, 155 + index*128
    color = COLORS[gate["verdict"]]; support = gate["finite_points_per_frame"]
    mean = gate["annual_frame_weighted_mean_declared_positive_velocity_m_s"]
    verdict = {"usable_surface_hint": "USABLE SURFACE HINT", "surface_sign_conflict": "SURFACE SIGN CONFLICT", "direction_only_underresolved": "UNDERRESOLVED", "not_screenable": "NOT SCREENABLE"}[gate["verdict"]]
    sign = "+" if mean >= 0 else ""
    return f'''<g transform="translate({x} {y})"><rect width="425" height="108" rx="13" class="card"/><rect width="5" height="108" rx="2.5" fill="{color}"/><text x="22" y="27" class="card-code" fill="{color}">{gate['code']}</text><text x="77" y="27" class="card-title">{html.escape(gate['name'].upper())}</text><text x="22" y="51" class="role">{html.escape(gate['role'].upper())}</text><text x="22" y="79" class="number">{support['minimum']}/{gate['candidate_grid_points']} WET</text><text x="151" y="79" class="number">{sign}{mean:.3f} M/S</text><text x="403" y="79" text-anchor="end" fill="{color}" class="verdict">{verdict}</text><text x="22" y="98" class="fine">DECLARED POSITIVE: {html.escape(gate['positive'].upper())}</text></g>'''


def build(audit: dict, payload: dict, geojson: dict, digest: str) -> str:
    cards = "".join(card(gate, index) for index, gate in enumerate(audit["gates"]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" data-motion-level="m2-indonesian-readiness"><title id="title">Indonesian Throughflow gate resolvability</title><desc id="desc">A local equal-area map audits five candidate Indonesian Throughflow screens. Timor is a usable surface hint; Makassar and Lifamatola show surface sign conflicts; Lombok and Ombai are underresolved.</desc><metadata>Natural Earth 1:10m SHA-256 {digest}. {html.escape(audit['boundary'])}</metadata><defs><marker id="arrow" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#76999a"/></marker><pattern id="land" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="8" height="8" fill="#f7f7f3"/><path d="M0 0V8" stroke="#789092" stroke-width=".5" stroke-opacity=".17"/></pattern><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.map{{fill:#0a242b;stroke:#46666a}}.vectors path{{fill:none;stroke:#76999a;stroke-width:1.15;opacity:.5}}.land{{fill:url(#land);fill-rule:evenodd;stroke:#9dacab;stroke-width:.55}}.gate{{stroke-width:5;stroke-linecap:round}}.gate-code{{font-size:12px;font-weight:950;paint-order:stroke;stroke:#06171c;stroke-width:4px}}.card{{fill:#0d252b;stroke:#405e62}}.card-code{{font:950 18px ui-monospace,Consolas,monospace}}.card-title{{fill:#eef9f7;font-size:15px;font-weight:950}}.role{{fill:#879fa0;font-size:8px;font-weight:850;letter-spacing:.8px}}.number{{fill:#eef9f7;font:850 13px ui-monospace,Consolas,monospace}}.verdict{{font-size:8px;font-weight:950;letter-spacing:.7px}}.fine{{fill:#668185;font-size:7px}}.note{{fill:#a8bfbd;font-size:10px}}</style></defs><rect width="1400" height="980" fill="#06171c"/><text x="45" y="43" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.4">OSW / INDONESIAN HEAT ROUTES · M2 RESOLUTION AUDIT</text><text x="45" y="87" fill="#eef9f7" font-size="34" font-weight="950">ONE THROUGHFLOW. FIVE GATES.</text><text x="45" y="116" fill="#9db3b2" font-size="12">Before arrows become a story, ask whether the grid can hold the strait.</text><rect x="1050" y="39" width="305" height="30" rx="15" fill="#102a30" stroke="#f0cf70"/><text x="1202.5" y="59" fill="#f0cf70" text-anchor="middle" font-size="9.5" font-weight="950" letter-spacing="1">GRID SUPPORT · NOT HEAT TRANSPORT</text><rect x="45" y="155" width="850" height="660" rx="16" class="map"/><clipPath id="map-clip"><rect x="45" y="155" width="850" height="660" rx="16"/></clipPath><g clip-path="url(#map-clip)"><g class="vectors">{vectors(payload)}</g><path d="{land_path(geojson)}" class="land"/>{gate_marks(audit['gates'])}</g>{cards}<g transform="translate(45 846)"><circle cx="5" cy="5" r="4" fill="#62d7ce"/><text x="17" y="9" class="note">finite in all 71 fields</text><path d="M180 1l8 8m0-8l-8 8" stroke="#f0cf70" stroke-width="2"/><text x="200" y="9" class="note">masked in one or more fields</text><path d="M420 5h30" stroke="#ff7d72" stroke-width="5"/><text x="461" y="9" class="note">screen with contrary annual surface sign</text></g><rect x="45" y="883" width="1310" height="61" rx="13" fill="#0d242a"/><text x="66" y="908" fill="#eef9f7" font-size="13" font-weight="950">THE FAILURE IS THE FINDING</text><text x="66" y="928" class="note">Lombok and Ombai do not have enough native wet samples for a serious M2 section. Makassar and Lifamatola warn that surface velocity is not the full-depth throughflow. Timor alone clears this screen.</text><text x="45" y="965" fill="#536f72" font-size="8">OSCAR 2017.0 · 71 FIVE-DAY FIELDS · DEC 2017–NOV 2018 · NOMINAL 15 M · 1/3° GRID · LOCAL LAMBERT AZIMUTHAL EQUAL AREA · NATURAL EARTH 1:10M LAND</text></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=pathlib.Path, default=pathlib.Path("research/osw-m2-indonesian-gate-readiness-2018.json"))
    parser.add_argument("--velocity", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-indonesian-native-2018.js"))
    parser.add_argument("--land-geojson", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-motion-indonesian-gate-readiness-2018.svg"))
    args = parser.parse_args()
    audit = json.loads(args.audit.read_text(encoding="utf-8")); payload = load_assignment(args.velocity); land, digest = load_land(args.land_geojson)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(audit, payload, land, digest), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

"""Render the two valid but noninterchangeable Barents native-face paths."""

from __future__ import annotations

import argparse
import html
import json
import pathlib

import netCDF4
import numpy as np


WIDTH = 1400
HEIGHT = 930
BOUNDS = (10.0, 31.0, 69.0, 78.0)


def normalize_longitude(values):
    return ((np.asarray(values, dtype=float) + 180.0) % 360.0) - 180.0


def projector(box):
    west, east, south, north = BOUNDS
    x, y, width, height = box
    return lambda lon, lat: (x + (float(lon) - west) / (east - west) * width, y + (north - float(lat)) / (north - south) * height)


def svg_path(points, project):
    return " ".join(("M" if index == 0 else "L") + f"{project(point['longitude_deg'], point['latitude_deg'])[0]:.1f},{project(point['longitude_deg'], point['latitude_deg'])[1]:.1f}" for index, point in enumerate(points))


def land_points(lon, lat, wet, project):
    west, east, south, north = BOUNDS
    marks = []
    for y in range(0, lon.shape[0], 2):
        for x in range(0, lon.shape[1], 2):
            if not wet[y, x] and west <= lon[y, x] <= east and south <= lat[y, x] <= north:
                px, py = project(lon[y, x], lat[y, x])
                marks.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.0"/>')
    return "".join(marks)


def face_marks(faces, project, color):
    marks = []
    for face in faces:
        x, y = project(face["longitude_deg"], face["latitude_deg"])
        shape = f'<rect x="{x - 2.4:.1f}" y="{y - 2.4:.1f}" width="4.8" height="4.8" rx="1"' if face["face"] == "U" else f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.8"'
        marks.append(f'{shape} fill="{color}"/>')
    return "".join(marks)


def build(payload, mesh_path):
    with netCDF4.Dataset(mesh_path) as dataset:
        lon = normalize_longitude(dataset.variables["glamt"][:])
        lat = np.asarray(dataset.variables["gphit"][:], dtype=float)
        wet = np.asarray(dataset.variables["tmask"][0]) > 0
    left = (52, 183, 620, 435); right = (728, 183, 620, 435)
    lp = projector(left); rp = projector(right)
    proxy = payload["observational_proxy"]; closure = payload["model_closure"]
    bear_distance = payload["comparison"]["closure_stop_distance_from_bear_target_km"]
    land_left = land_points(lon, lat, wet, lp); land_right = land_points(lon, lat, wet, rp)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" data-motion-level="m3-barents-section-bakeoff">
<title id="title">Two valid Barents lines answer two different questions</title><desc id="desc">A 43-face wet-ended Fugloya-Bear observational proxy is compared with a 73-face coast-to-coast Norway-Svalbard model closure. Both pass native C-grid topology checks but their endpoints and meanings differ.</desc><metadata>{html.escape(payload['boundary'])}</metadata>
<defs><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.panel{{fill:#092229;stroke:#36575d}}.land{{fill:#eef5f1;opacity:.93}}.proxy{{fill:none;stroke:#55ded3;stroke-width:4;stroke-linejoin:round}}.closure{{fill:none;stroke:#ff9a52;stroke-width:4;stroke-linejoin:round}}.body{{fill:#aac0bf;font-size:13px}}.fine{{fill:#78979a;font-size:10px}}.metric{{fill:#eef8f5;font-size:24px;font-weight:950}}.label{{fill:#eef8f5;font-size:13px;font-weight:900;letter-spacing:1px}}.check{{fill:#55ded3;font-size:11px;font-weight:900}}</style></defs>
<rect width="1400" height="930" fill="#06171c"/><text x="52" y="42" fill="#55ded3" font-size="12" font-weight="950" letter-spacing="2">OSW / BARENTS · NATIVE SECTION BAKEOFF</text><text x="52" y="88" fill="#eef8f5" font-size="36" font-weight="950">TWO VALID LINES. TWO DIFFERENT QUESTIONS.</text><text x="52" y="120" class="body">Topology can certify a face path. It cannot make unlike endpoints measure the same domain.</text>
<g><rect x="52" y="153" width="620" height="495" rx="14" class="panel"/><text x="72" y="177" class="label">OBSERVATIONAL PROXY · FUGLØYA–BEAR</text><g class="land">{land_left}</g><path d="{svg_path(proxy['faces'], lp)}" class="proxy"/>{face_marks(proxy['faces'], lp, '#55ded3')}</g>
<g><rect x="728" y="153" width="620" height="495" rx="14" class="panel"/><text x="748" y="177" class="label">MODEL CLOSURE · NORWAY–SVALBARD</text><g class="land">{land_right}</g><path d="{svg_path(closure['faces'], rp)}" class="closure"/>{face_marks(closure['faces'], rp, '#ff9a52')}</g>
<g transform="translate(52 682)"><text class="metric">{proxy['face_count']} FACES · {proxy['u_face_count']} U + {proxy['v_face_count']} V</text><text y="29" class="body">virtual wet endpoints preserve comparison with the named section</text><text y="54" class="fine">OPEN PROXY · MODEL WATER CAN BYPASS THE ENDS</text></g>
<g transform="translate(728 682)"><text class="metric">{closure['face_count']} FACES · {closure['u_face_count']} U + {closure['v_face_count']} V</text><text y="29" class="body">modeled coast at both ends; northern endpoint is {bear_distance:.0f} km from Bear target</text><text y="54" class="fine">BUDGET CLOSURE · NOT THE OBSERVATIONAL BSO</text></g>
<rect x="52" y="775" width="1296" height="88" rx="12" fill="#102a30" stroke="#36575d"/><text x="72" y="804" fill="#eef8f5" font-size="14" font-weight="950">BOTH PATHS PASS THE SAME TOPOLOGY CONTRACT</text><text x="72" y="832" class="check">✓ CONNECTED CORNERS</text><text x="300" y="832" class="check">✓ UNIQUE FACES</text><text x="500" y="832" class="check">✓ DEGREE-2 INTERIOR</text><text x="752" y="832" class="check">✓ ZERO CORNER DUPLICATION</text><text x="1055" y="832" fill="#ffbd71" font-size="11" font-weight="950">≠ SAME MEASUREMENT</text>
<text x="52" y="901" class="fine">SQUARE = U FACE · CIRCLE = V FACE · SURFACE GEOMETRY ONLY · NO VELOCITY, VOLUME, HEAT, OR OBSERVATIONAL AGREEMENT · PUBLIC ORAS5 ORCA025 MESH</text></svg>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-barents-section-bakeoff.json"))
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-arctic-entrances-mesh.nc"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m3-oras5-barents-section-bakeoff.svg"))
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(payload, args.mesh), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

"""Render the native-grid readiness contrast between Fram and Barents gates."""

from __future__ import annotations

import argparse
import html
import json
import pathlib

import netCDF4
import numpy as np


WIDTH = 1400
HEIGHT = 920


def normalize_longitude(values):
    return ((np.asarray(values, dtype=float) + 180.0) % 360.0) - 180.0


def projector(bounds, box):
    west, east, south, north = bounds
    x, y, width, height = box

    def project(lon, lat):
        px = x + (float(lon) - west) / (east - west) * width
        py = y + (north - float(lat)) / (north - south) * height
        return px, py

    return project


def path(points, project) -> str:
    return " ".join(("M" if index == 0 else "L") + f"{project(lon, lat)[0]:.1f},{project(lon, lat)[1]:.1f}" for index, (lon, lat) in enumerate(points))


def grid_paths(lon, lat, bounds, project, step=8) -> str:
    west, east, south, north = bounds
    lines = []
    for y in range(0, lon.shape[0], step):
        points = [(lon[y, x], lat[y, x]) for x in range(lon.shape[1]) if west <= lon[y, x] <= east and south <= lat[y, x] <= north]
        if len(points) > 1:
            lines.append(f'<path d="{path(points, project)}"/>')
    for x in range(0, lon.shape[1], step):
        points = [(lon[y, x], lat[y, x]) for y in range(lon.shape[0]) if west <= lon[y, x] <= east and south <= lat[y, x] <= north]
        if len(points) > 1:
            lines.append(f'<path d="{path(points, project)}"/>')
    return "".join(lines)


def land_points(lon, lat, wet, bounds, project) -> str:
    west, east, south, north = bounds
    marks = []
    for y in range(0, lon.shape[0], 2):
        for x in range(0, lon.shape[1], 2):
            if not wet[y, x] and west <= lon[y, x] <= east and south <= lat[y, x] <= north:
                px, py = project(lon[y, x], lat[y, x])
                marks.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.1"/>')
    return "".join(marks)


def build(payload: dict, mesh_path: pathlib.Path) -> str:
    with netCDF4.Dataset(mesh_path) as dataset:
        t_lon = normalize_longitude(dataset.variables["glamt"][:])
        t_lat = np.asarray(dataset.variables["gphit"][:], dtype=float)
        wet = (np.asarray(dataset.variables["umask"][0]) > 0) | (np.asarray(dataset.variables["vmask"][0]) > 0)
        v_lon = normalize_longitude(dataset.variables["glamv"][:]); v_lat = np.asarray(dataset.variables["gphiv"][:], dtype=float)
        u_lon = normalize_longitude(dataset.variables["glamu"][:]); u_lat = np.asarray(dataset.variables["gphiu"][:], dtype=float)

    fram_bounds = (-25, 20, 76.5, 81)
    barents_bounds = (10, 31, 69, 77)
    fram_box = (52, 184, 620, 440)
    barents_box = (728, 184, 620, 440)
    fram_project = projector(fram_bounds, fram_box)
    barents_project = projector(barents_bounds, barents_box)
    fram = payload["fram"]
    barents = payload["barents_single_column_test"]
    fram_line = list(zip(fram["longitude_deg"], fram["latitude_deg"]))
    barents_line = list(zip(barents["longitude_deg"], barents["latitude_deg"]))
    fx1, fy1 = fram_project(payload["targets"]["fram"]["west_deg"], payload["targets"]["fram"]["latitude_deg_north"])
    fx2, fy2 = fram_project(payload["targets"]["fram"]["east_deg"], payload["targets"]["fram"]["latitude_deg_north"])
    bx1, by1 = barents_project(payload["targets"]["barents"]["longitude_deg_east"], payload["targets"]["barents"]["south_deg"])
    bx2, by2 = barents_project(payload["targets"]["barents"]["longitude_deg_east"], payload["targets"]["barents"]["north_deg"])
    bear = payload["bear_island_representation"]
    bear_x, bear_y = barents_project(bear["target"]["longitude_deg_east"], bear["target"]["latitude_deg_north"])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" data-motion-level="m3-arctic-gate-readiness">
<title id="title">One Arctic gate fits the grid; one does not</title>
<desc id="desc">Native ORCA025 surface geometry shows a 60-face land-bounded Fram V-row, while a single Barents U-column drifts more than ten degrees and the nominal Bear Island target is wet in the model.</desc>
<metadata>{html.escape(payload['boundary'])}</metadata>
<defs><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.panel{{fill:#092229;stroke:#36575d;stroke-width:1}}.grid{{fill:none;stroke:#7ea0a2;stroke-width:.7;opacity:.18}}.land{{fill:#eef5f1;opacity:.92}}.target{{fill:none;stroke:#d6e4df;stroke-width:2;stroke-dasharray:7 7;opacity:.8}}.fram{{fill:none;stroke:#55ded3;stroke-width:5;stroke-linecap:round;stroke-linejoin:round}}.barents{{fill:none;stroke:#ff9a52;stroke-width:5;stroke-linecap:round;stroke-linejoin:round}}.fine{{fill:#78979a;font-size:10px}}.body{{fill:#aac0bf;font-size:13px}}.metric{{fill:#eef8f5;font-size:24px;font-weight:950}}.label{{fill:#eef8f5;font-size:13px;font-weight:900;letter-spacing:1px}}.eyebrow{{fill:#55ded3;font-size:12px;font-weight:950;letter-spacing:2px}}</style></defs>
<rect width="1400" height="920" fill="#06171c"/>
<text x="52" y="42" class="eyebrow">OSW / ARCTIC ENTRANCES · NATIVE GEOMETRY AUDIT</text>
<text x="52" y="88" fill="#eef8f5" font-size="36" font-weight="950">ONE GATE FITS THE GRID. ONE DOES NOT.</text>
<text x="52" y="120" class="body">Before velocity or heat, ask whether the declared geographic gate can be represented by one native face line.</text>
<g><rect x="52" y="154" width="620" height="500" rx="14" class="panel"/><text x="72" y="178" class="label">FRAM STRAIT · V FACES</text><g class="grid">{grid_paths(v_lon, v_lat, fram_bounds, fram_project)}</g><g class="land">{land_points(t_lon, t_lat, wet, fram_bounds, fram_project)}</g><path d="M{fx1:.1f},{fy1:.1f}L{fx2:.1f},{fy2:.1f}" class="target"/><path d="{path(fram_line, fram_project)}" class="fram"/><circle cx="{fram_project(*fram_line[0])[0]:.1f}" cy="{fram_project(*fram_line[0])[1]:.1f}" r="6" fill="#55ded3"/><circle cx="{fram_project(*fram_line[-1])[0]:.1f}" cy="{fram_project(*fram_line[-1])[1]:.1f}" r="6" fill="#55ded3"/></g>
<g><rect x="728" y="154" width="620" height="500" rx="14" class="panel"/><text x="748" y="178" class="label">BARENTS OPENING · SINGLE U-COLUMN TEST</text><g class="grid">{grid_paths(u_lon, u_lat, barents_bounds, barents_project)}</g><g class="land">{land_points(t_lon, t_lat, wet, barents_bounds, barents_project)}</g><path d="M{bx1:.1f},{by1:.1f}L{bx2:.1f},{by2:.1f}" class="target"/><path d="{path(barents_line, barents_project)}" class="barents"/><circle cx="{barents_project(*barents_line[0])[0]:.1f}" cy="{barents_project(*barents_line[0])[1]:.1f}" r="6" fill="#ff9a52"/><circle cx="{barents_project(*barents_line[-1])[0]:.1f}" cy="{barents_project(*barents_line[-1])[1]:.1f}" r="6" fill="#ff9a52"/></g>
<g transform="translate({bear_x:.1f} {bear_y:.1f})"><path d="M-8-8L8 8M-8 8L8-8" stroke="#d78cff" stroke-width="4"/><text x="14" y="-9" fill="#dba8ff" font-size="10" font-weight="950">BEAR ISLAND TARGET</text><text x="14" y="5" class="fine">WET T CELL IN ORCA025</text></g>
<g transform="translate(52 690)"><text class="metric">{fram['face_count']} NATIVE FACES</text><text y="28" class="body">one continuous V-row, land-bounded at the surface</text><text y="52" class="fine">TEAL = SELECTED NATIVE RUN · DASH = DECLARED 78.83°N TARGET</text></g>
<g transform="translate(728 690)"><text class="metric">{barents['longitude_drift_deg']:.2f}° DRIFT · ISLAND WET</text><text y="28" class="body">one U column misses 20°E; the nominal Bear endpoint is not dry</text><text y="52" class="fine">ORANGE = REJECTED COLUMN · PURPLE × = APPROXIMATE BEAR TARGET</text></g>
<rect x="52" y="782" width="1296" height="83" rx="12" fill="#102a30" stroke="#36575d"/><text x="72" y="811" fill="#ffbd71" font-size="16" font-weight="950">NEXT DECISION: OBSERVATIONAL PROXY OR MODEL CLOSURE?</text><text x="72" y="838" class="body">Use a virtual-endpoint mixed U/V staircase for Fugløya–Bear comparison—or a separate Norway–Svalbard land-bounded gate for budgets. Never merge the meanings.</text>
<text x="52" y="896" class="fine">NATIVE CURVILINEAR COORDINATE VIEW · SURFACE GEOMETRY ONLY · NO STATE FIELDS · NO VOLUME OR HEAT TRANSPORT · SOURCE: PUBLIC ORAS5 ORCA025 MESH</text>
</svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-arctic-gate-readiness.json"))
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-arctic-entrances-mesh.nc"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m3-oras5-arctic-gate-readiness.svg"))
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(payload, args.mesh), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

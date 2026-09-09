"""Build a latitude-depth portrait of the four-sample mean native Drake gate."""

from __future__ import annotations

import argparse
import html
import json
import math
import pathlib


STOPS = ((-1.5, "#667fe0"), (0, "#8ca8ff"), (1, "#71c5e8"), (2, "#62d7ce"), (3, "#b8db75"), (5, "#ffb454"), (7.5, "#ff806d"))


def interpolate_color(value: float) -> str:
    if value <= STOPS[0][0]:
        return STOPS[0][1]
    if value >= STOPS[-1][0]:
        return STOPS[-1][1]
    for (low, low_hex), (high, high_hex) in zip(STOPS, STOPS[1:]):
        if low <= value <= high:
            fraction = (value - low) / (high - low)
            a = tuple(int(low_hex[i:i + 2], 16) for i in (1, 3, 5))
            b = tuple(int(high_hex[i:i + 2], 16) for i in (1, 3, 5))
            rgb = tuple(round(x + (y - x) * fraction) for x, y in zip(a, b))
            return "#" + "".join(f"{channel:02x}" for channel in rgb)
    raise AssertionError("unreachable color interval")


def build(payload: dict) -> str:
    levels, segments = payload["shape"]
    plot_x0, plot_x1, plot_y0, plot_y1 = 92, 1312, 220, 740
    cell_width = (plot_x1 - plot_x0) / segments
    maximum_depth = payload["maximum_nominal_model_depth_m"]
    depth_y = lambda depth: plot_y0 + (max(0, depth) / maximum_depth) ** .55 * (plot_y1 - plot_y0)
    temperature = payload["mean_potential_temperature_degC"]
    velocity = payload["mean_normal_velocity_m_s"]
    wet = payload["wet_fraction"]
    explicit_thickness = payload["cell_thickness_m"]
    cells = []
    marks = []
    bottom_by_segment = [0.0] * segments
    for level, depth in enumerate(payload["layer_depths"]):
        top = depth["top_m"]
        for segment in range(segments):
            index = level * segments + segment
            if not wet[index]:
                continue
            bottom = top + float(explicit_thickness[index])
            bottom_by_segment[segment] = max(bottom_by_segment[segment], bottom)
            x = plot_x0 + segment * cell_width
            y0, y1 = depth_y(top), depth_y(bottom)
            cells.append(f'<rect data-cell="{level}-{segment}" x="{x:.2f}" y="{y0:.2f}" width="{cell_width + .18:.2f}" height="{max(.38, y1 - y0 + .18):.2f}" fill="{interpolate_color(temperature[index])}"/>')
            if level % 4 == 0 and segment % 3 == 1 and abs(velocity[index]) >= .025:
                cx, cy = x + cell_width / 2, (y0 + y1) / 2
                radius = min(6.2, 2.1 + abs(velocity[index]) * 7)
                if velocity[index] > 0:
                    marks.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{radius:.2f}" class="motion"/><circle cx="{cx:.2f}" cy="{cy:.2f}" r="1.25" fill="#06171c"/>')
                else:
                    arm = radius * .58
                    marks.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{radius:.2f}" class="motion"/><path d="M{cx-arm:.2f},{cy-arm:.2f}L{cx+arm:.2f},{cy+arm:.2f}M{cx+arm:.2f},{cy-arm:.2f}L{cx-arm:.2f},{cy+arm:.2f}" class="cross"/>')
    seabed_points = [f"{plot_x0:.2f},{plot_y1:.2f}"]
    for segment, bottom in enumerate(bottom_by_segment):
        seabed_points.append(f"{plot_x0 + (segment + .5) * cell_width:.2f},{depth_y(bottom):.2f}")
    seabed_points.append(f"{plot_x1:.2f},{plot_y1:.2f}")
    depth_grid = []
    for value in (0, 200, 700, 1500, 3000, 6000):
        y = depth_y(value)
        depth_grid.append(f'<line x1="{plot_x0}" y1="{y:.2f}" x2="{plot_x1}" y2="{y:.2f}" class="grid"/><text x="{plot_x0 - 12}" y="{y + 4:.2f}" class="axis" text-anchor="end">{value if value else 0} m</text>')
    latitudes = payload["latitude_deg"]
    lat_grid = []
    for latitude in (-66, -64, -62, -60, -58, -56):
        nearest = min(range(segments), key=lambda i: abs(latitudes[i] - latitude))
        x = plot_x0 + (nearest + .5) * cell_width
        lat_grid.append(f'<line x1="{x:.2f}" y1="{plot_y0}" x2="{x:.2f}" y2="{plot_y1}" class="vgrid"/><text x="{x:.2f}" y="{plot_y1 + 24}" class="lat">{abs(latitude)}°S</text>')
    legend = []
    for index, (value, color) in enumerate(STOPS):
        x = 750 + index * 72
        legend.append(f'<rect x="{x}" y="805" width="72" height="13" fill="{color}"/><text x="{x}" y="836" class="legend">{value:g}°C</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="920" viewBox="0 0 1400 920" role="img" aria-labelledby="title desc" data-motion-level="m3-drake-section-field">
<title id="title">Latitude-depth portrait of the native Drake Passage gate</title><desc id="desc">A nonlinear-depth cross-section from the Antarctic Peninsula toward South America shows four-sample mean potential temperature, with sampled dot symbols for eastward velocity out of the page and cross symbols for westward velocity into the page.</desc>
<defs><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.kicker{{fill:#62d7ce;font-size:14px;font-weight:900;letter-spacing:2.4px}}.title{{fill:#eef9f7;font-size:34px;font-weight:950}}.sub{{fill:#9db3b2;font-size:12px}}.grid{{stroke:#d7e7e5;stroke-width:.6;stroke-opacity:.18}}.vgrid{{stroke:#d7e7e5;stroke-width:.6;stroke-opacity:.11}}.axis{{fill:#789596;font:800 9px ui-monospace,Consolas,monospace}}.lat{{fill:#9db3b2;font:850 10px ui-monospace,Consolas,monospace;text-anchor:middle}}.motion{{fill:#eef9f7;fill-opacity:.75;stroke:#06171c;stroke-width:1}}.cross{{fill:none;stroke:#06171c;stroke-width:1.2;stroke-linecap:round}}.label{{fill:#9db3b2;font-size:9px;font-weight:900;letter-spacing:1.1px}}.legend{{fill:#9db3b2;font:800 8px ui-monospace,Consolas,monospace}}.note{{fill:#a9bfbe;font-size:10px}}.fine{{fill:#617d80;font-size:8.5px}}</style></defs>
<rect width="1400" height="920" fill="#06171c"/><text x="48" y="44" class="kicker">OSW / HEAT MOTION · M3 NATIVE SECTION PORTRAIT</text><text x="48" y="88" class="title">A SLICE THROUGH THE GATE</text><text x="48" y="118" class="sub">67.125°W · four sampled 2018 months · temperature field + cross-section-normal velocity</text>
<rect x="40" y="170" width="1320" height="600" rx="16" fill="#0b2127" stroke="#29464c"/><text x="{plot_x0}" y="199" class="label">ANTARCTIC PENINSULA / SOUTH</text><text x="{plot_x1}" y="199" class="label" text-anchor="end">SOUTH AMERICA / NORTH</text>
<g aria-label="Potential-temperature field">{''.join(cells)}</g><path d="M{' L'.join(seabed_points)} Z" fill="#19262a" stroke="#789596" stroke-width="1"/>{''.join(depth_grid)}{''.join(lat_grid)}<g aria-label="Sampled normal velocity symbols">{''.join(marks)}</g>
<g transform="translate(92 804)"><circle cx="8" cy="8" r="6" class="motion"/><circle cx="8" cy="8" r="1.25" fill="#06171c"/><text x="22" y="12" class="note">EASTWARD · OUT OF SECTION</text><circle cx="245" cy="8" r="6" class="motion"/><path d="M241,4L249,12M249,4L241,12" class="cross"/><text x="260" y="12" class="note">WESTWARD · INTO SECTION</text><text x="480" y="12" class="label">MEAN POTENTIAL TEMPERATURE</text></g>{''.join(legend)}
<rect x="48" y="856" width="1304" height="38" rx="12" fill="#0d242a"/><text x="68" y="874" class="note">The warmer eastward core spans much of the passage; colder counterflow is embedded within and beneath it rather than forming one simple surface ribbon.</text><text x="68" y="888" class="fine">NONLINEAR DEPTH DISPLAY · VELOCITY SYMBOLS SAMPLED FOR LEGIBILITY · FOUR MONTHS, NOT AN ANNUAL MEAN OR CLIMATOLOGY · NOT WATER-MASS BOUNDARIES OR HEAT CONVERGENCE</text><metadata>{html.escape(payload['boundary'])}</metadata></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-section-field-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m3-oras5-drake-section-field-2018.svg"))
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(payload), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

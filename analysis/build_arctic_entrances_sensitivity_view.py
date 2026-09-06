"""Render the Arctic entrance surface-screen sensitivity bakeoff."""

from __future__ import annotations

import argparse
import html
import json
import pathlib


def color(value: float) -> str:
    maximum = .03
    strength = min(1.0, abs(value) / maximum)
    if value >= 0:
        start, end = (32, 54, 60), (255, 180, 84)
    else:
        start, end = (32, 54, 60), (126, 157, 255)
    rgb = tuple(round(a + (b - a) * strength) for a, b in zip(start, end))
    return f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"


def matrix(cases: list[dict], row_values: list[float], column_values: list[float], x: float, y: float, cell_w: float, cell_h: float, column_key: str) -> str:
    lookup = {(round(item["sampled_fixed_coordinate"], 3), round(item[column_key], 3)): item for item in cases}
    parts = []
    for row, row_value in enumerate(row_values):
        sampled_row = min({round(item["sampled_fixed_coordinate"], 3) for item in cases}, key=lambda value: abs(value - row_value))
        parts.append(f'<text x="{x-12}" y="{y+row*cell_h+cell_h*.62:.1f}" class="axis-label">{sampled_row:.2f}°N</text>')
        for column, column_value in enumerate(column_values):
            item = lookup[(sampled_row, round(column_value, 3))]
            value = item["annual_mean_normal_velocity_m_s"]
            cx, cy = x + column * cell_w, y + row * cell_h
            parts.append(f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cell_w-5:.1f}" height="{cell_h-5:.1f}" rx="7" fill="{color(value)}"/><text x="{cx+(cell_w-5)/2:.1f}" y="{cy+cell_h*.58:.1f}" class="cell-value">{value:+.3f}</text>')
    for column, value in enumerate(column_values):
        parts.append(f'<text x="{x+column*cell_w+(cell_w-5)/2:.1f}" y="{y-12}" class="column-label">{value:g}°E</text>')
    return "".join(parts)


def build(payload: dict) -> str:
    east = payload["fram_eastern_inflow"]
    west = payload["fram_western_export"]
    barents = payload["barents_eastward_inflow"]
    east_rows = sorted({round(item["sampled_fixed_coordinate"], 3) for item in east["cases"]})
    east_columns = sorted({item["along_min"] for item in east["cases"]})
    west_rows = sorted({round(item["sampled_fixed_coordinate"], 3) for item in west["cases"]})
    west_columns = sorted({item["along_max"] for item in west["cases"]})
    line_x0, line_step, baseline, scale = 1035, 27, 485, 5200
    line_points = []
    line_marks = []
    for index, item in enumerate(barents["cases"]):
        x = line_x0 + index * line_step
        value = item["annual_mean_normal_velocity_m_s"]
        y = baseline - value * scale
        line_points.append((x, y))
        line_marks.append(f'<circle cx="{x}" cy="{y:.1f}" r="5" fill="#ffb454"/><text x="{x}" y="{baseline+22}" class="tiny">{item["sampled_fixed_coordinate"]:.0f}</text>')
    line_path = "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in line_points)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900" role="img" aria-labelledby="title desc" data-motion-level="m2-arctic-entrances-sensitivity"><title id="title">Arctic entrance surface-screen sensitivity</title><desc id="desc">Thirty eastern Fram variants change sign when the screen moves north, while all eighteen western Fram variants remain southward and all eleven Barents variants remain eastward.</desc><metadata>{html.escape(payload['boundary'])}</metadata><defs><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.panel{{fill:#0b252c;stroke:#49666b}}.head{{fill:#eef9f7;font-size:16px;font-weight:950}}.sub{{fill:#8ca7a7;font-size:8.5px;font-weight:900;letter-spacing:.9px}}.axis-label{{fill:#8ca7a7;font:800 8px ui-monospace,Consolas,monospace;text-anchor:end}}.column-label{{fill:#8ca7a7;font:800 8px ui-monospace,Consolas,monospace;text-anchor:middle}}.cell-value{{fill:#f5fbfa;font:850 9px ui-monospace,Consolas,monospace;text-anchor:middle}}.tiny{{fill:#8ca7a7;font:800 7px ui-monospace,Consolas,monospace;text-anchor:middle}}.metric{{fill:#eef9f7;font:950 27px ui-monospace,Consolas,monospace}}.metric-label{{fill:#8ca7a7;font-size:8.5px;font-weight:900;letter-spacing:1px}}.note{{fill:#a8bfbd;font-size:10px}}.fine{{fill:#607d80;font-size:8px}}</style></defs><rect width="1400" height="900" fill="#06171c"/><text x="48" y="43" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.4">OSW / ARCTIC HEAT ROUTES · M2 SCREEN CHALLENGE</text><text x="48" y="87" fill="#eef9f7" font-size="34" font-weight="950">FRAM INFLOW MOVES WITH THE SCREEN</text><text x="48" y="116" fill="#9db3b2" font-size="12">Nearby latitude and lane-boundary bakeoff · annual mean normal surface velocity · m/s</text>
<rect x="40" y="150" width="620" height="430" rx="17" class="panel"/><text x="65" y="183" class="head">FRAM EASTERN LANE</text><text x="65" y="203" class="sub">ROWS = SCREEN LATITUDE · COLUMNS = EASTERN-LANE START · ORANGE NORTH / BLUE SOUTH</text>{matrix(east['cases'], east_rows, east_columns, 140, 245, 96, 49, 'along_min')}
<rect x="680" y="150" width="325" height="430" rx="17" class="panel"/><text x="705" y="183" class="head">FRAM WESTERN LANE</text><text x="705" y="203" class="sub">LANE EAST EDGE · EVERY CASE EXPORTS SOUTH</text>{matrix(west['cases'], west_rows, west_columns, 758, 245, 70, 49, 'along_max')}
<rect x="1025" y="150" width="335" height="430" rx="17" class="panel"/><text x="1050" y="183" class="head">BARENTS SCREEN</text><text x="1050" y="203" class="sub">SCREEN LONGITUDE · EVERY CASE FLOWS EAST</text><line x1="1045" y1="{baseline}" x2="1330" y2="{baseline}" stroke="#49666b"/><path d="{line_path}" fill="none" stroke="#ffb454" stroke-width="3" opacity=".55"/>{''.join(line_marks)}<text x="1180" y="530" class="sub" text-anchor="middle">20°E → 30°E</text>
<g transform="translate(48 640)"><text class="metric">{east['summary']['direction_support_count']} / {east['summary']['case_count']}</text><text y="23" class="metric-label">FRAM EAST CASES NORTHWARD</text><text x="430" class="metric">{west['summary']['direction_support_count']} / {west['summary']['case_count']}</text><text x="430" y="23" class="metric-label">FRAM WEST CASES SOUTHWARD</text><text x="860" class="metric">{barents['summary']['direction_support_count']} / {barents['summary']['case_count']}</text><text x="860" y="23" class="metric-label">BARENTS CASES EASTWARD</text></g>
<rect x="48" y="720" width="1304" height="120" rx="14" fill="#0d242a"/><text x="70" y="746" fill="#eef9f7" font-size="14" font-weight="950">WHAT SURVIVES THE CHALLENGE</text><text x="70" y="772" class="note">Western Fram export and eastward Barents motion are directionally stable across these nearby screens.</text><text x="70" y="793" class="note">The eastern Fram lane is northward at 77.67–78.67°N, but reverses at 79.0–79.33°N. One latitude cannot stand for the whole gateway.</text><text x="70" y="817" class="fine">DIRECTION SUPPORT IS DESCRIPTIVE, NOT PROBABILITY OR UNCERTAINTY · UNWEIGHTED OSCAR 2017.0 NOMINAL-15-M GRID SAMPLES · NO DEPTH, SECTION AREA, TEMPERATURE, SALINITY, VOLUME, OR HEAT</text><text x="48" y="872" fill="#536f72" font-size="8">THE M3 NATIVE SECTION MUST RETAIN SIGNED BRANCHES AND PASS ITS OWN GEOMETRY SENSITIVITY; THIS M2 BAKEOFF DOES NOT SELECT THE FINAL GATE.</text></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m2-arctic-entrances-sensitivity-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-motion-arctic-entrances-sensitivity-2018.svg"))
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(payload), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

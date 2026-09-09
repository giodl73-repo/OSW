"""Build the M3 four-month Drake gate passport SVG."""

from __future__ import annotations

import argparse
import html
import json
import pathlib


COLORS = {"-1.9": "#ffb454", "0.0": "#62d7ce", "5.0": "#dc83ff"}


def build(payload: dict) -> str:
    rows = payload["rows"]
    volume_rows = []; heat_paths = {key: [] for key in COLORS}; heat_dots = []
    y_values = [255, 375, 495, 615]
    volume_scale = 1.72
    heat_x0, heat_width = 820, 500
    heat_min, heat_max = -1.5, 2.5
    heat_x = lambda value: heat_x0 + (value - heat_min) / (heat_max - heat_min) * heat_width
    for row, y in zip(rows, y_values):
        positive = row["positive_Sv"]; negative = abs(row["negative_Sv"]); net = row["net_Sv"]
        volume_rows.append(f'''
          <text x="72" y="{y - 19}" class="month">{html.escape(row['label'].upper())}</text>
          <line x1="344" y1="{y}" x2="{344 + positive * volume_scale:.2f}" y2="{y}" class="east"/>
          <line x1="344" y1="{y + 25}" x2="{344 - negative * volume_scale:.2f}" y2="{y + 25}" class="west"/>
          <text x="{356 + positive * volume_scale:.2f}" y="{y + 4}" class="value">+{positive:.1f}</text>
          <text x="{332 - negative * volume_scale:.2f}" y="{y + 29}" class="value end">−{negative:.1f}</text>
          <rect x="578" y="{y - 26}" width="145" height="62" rx="12" class="netbox"/>
          <text x="650.5" y="{y - 2}" class="net">{net:.2f}</text><text x="650.5" y="{y + 19}" class="unit">SV NET EAST</text>
          <text x="72" y="{y + 52}" class="temp">T<tspan baseline-shift="sub">net</tspan> {row['net_temperature_degC']:.2f}°C</text>''')
        for reference in COLORS:
            value = row["net_heat_PW_by_reference_degC"][reference]
            x = heat_x(value)
            heat_paths[reference].append((x, y))
            heat_dots.append(f'<circle cx="{x:.2f}" cy="{y}" r="7" fill="{COLORS[reference]}"/><text x="{x:.2f}" y="{y - 13}" class="heatvalue" fill="{COLORS[reference]}">{value:+.2f}</text>')
    paths = []
    for reference, points in heat_paths.items():
        paths.append(f'<path d="M' + 'L'.join(f'{x:.2f},{y}' for x, y in points) + f'" fill="none" stroke="{COLORS[reference]}" stroke-width="2" opacity=".65"/>')
    ticks = []
    for value in (-1, 0, 1, 2):
        x = heat_x(value)
        ticks.append(f'<line x1="{x:.2f}" y1="205" x2="{x:.2f}" y2="675" class="grid"/><text x="{x:.2f}" y="700" class="axis">{value:+d} PW</text>')
    summary = payload["summary"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1000" viewBox="0 0 1400 1000" role="img" aria-labelledby="title desc" data-motion-level="m3-drake-seasonal-gate">
<title id="title">One Drake gate, four monthly means, three heat-reference answers</title>
<desc id="desc">Four 2018 ORAS5 monthly calculations compare eastward and westward volume branches, net eastward volume, transport-weighted temperature, and heat transport relative to minus 1.9, zero, and five degrees Celsius.</desc>
<defs><style>
text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.kicker{{fill:#62d7ce;font-size:14px;font-weight:900;letter-spacing:2.4px}}.title{{fill:#eef9f7;font-size:34px;font-weight:950}}.sub{{fill:#9db3b2;font-size:12px}}.month{{fill:#eef9f7;font-size:13px;font-weight:950;letter-spacing:1.5px}}.east{{stroke:#ffb454;stroke-width:14;stroke-linecap:round}}.west{{stroke:#7e9dff;stroke-width:14;stroke-linecap:round}}.value{{fill:#d7e7e5;font:900 10px ui-monospace,Consolas,monospace}}.end{{text-anchor:end}}.netbox{{fill:#102a30;stroke:#62d7ce;stroke-opacity:.55}}.net{{fill:#eef9f7;font:950 24px ui-monospace,Consolas,monospace;text-anchor:middle}}.unit{{fill:#62d7ce;font-size:8px;font-weight:950;letter-spacing:1.3px;text-anchor:middle}}.temp{{fill:#789596;font:850 10px ui-monospace,Consolas,monospace}}.grid{{stroke:#29464c;stroke-width:1}}.axis{{fill:#789596;font:850 9px ui-monospace,Consolas,monospace;text-anchor:middle}}.heatvalue{{font:950 9px ui-monospace,Consolas,monospace;text-anchor:middle}}.small{{fill:#789596;font-size:9px;font-weight:850}}.metric{{fill:#eef9f7;font:950 27px ui-monospace,Consolas,monospace}}.label{{fill:#9db3b2;font-size:9px;font-weight:900;letter-spacing:1px}}.note{{fill:#a9bfbe;font-size:10px}}.fine{{fill:#617d80;font-size:8.5px}}
</style></defs>
<rect width="1400" height="1000" fill="#06171c"/><text x="48" y="44" class="kicker">OSW / HEAT MOTION  ·  M3 NATIVE DRAKE GATE</text><text x="48" y="88" class="title">ONE GATE / FOUR MONTHS / THREE HEAT ANSWERS</text><text x="48" y="118" class="sub">ORAS5 ORCA025 · 75 levels · 87 native U faces at 67.125°W · positive eastward</text>
<g aria-label="Volume branches"><text x="72" y="178" class="label">MONTHLY VOLUME BRANCHES · SV</text><line x1="344" y1="195" x2="344" y2="660" stroke="#48646a"/><text x="355" y="197" class="small">EASTWARD →</text><text x="332" y="197" class="small" text-anchor="end">← WESTWARD</text>{''.join(volume_rows)}</g>
<g aria-label="Reference-relative heat"><text x="820" y="178" class="label">NET ADVECTIVE HEAT · PW · REFERENCE TEMPERATURE CHANGES THE NUMBER</text>{''.join(ticks)}{''.join(paths)}{''.join(heat_dots)}<g transform="translate(835 735)"><circle r="6" fill="#ffb454"/><text x="14" y="4" class="note">Tref −1.9°C</text><circle cx="130" r="6" fill="#62d7ce"/><text x="144" y="4" class="note">Tref 0°C</text><circle cx="240" r="6" fill="#dc83ff"/><text x="254" y="4" class="note">Tref 5°C</text></g></g>
<path d="M48 790H1352" stroke="#345157"/><g transform="translate(48 825)"><text class="metric">{summary['net_volume_Sv']['mean']:.2f} SV</text><text y="22" class="label">FOUR-SAMPLE NET MEAN</text><text x="245" class="metric">{summary['net_volume_Sv']['range']:.2f} SV</text><text x="245" y="22" class="label">NET RANGE</text><text x="485" class="metric">{summary['positive_volume_Sv']['range']:.2f} / {summary['negative_volume_Sv']['range']:.2f}</text><text x="485" y="22" class="label">EAST / WEST BRANCH RANGES · SV</text><text x="935" class="metric">{summary['net_temperature_degC']['range']:.2f}°C</text><text x="935" y="22" class="label">TNET RANGE</text></g>
<rect x="48" y="895" width="1304" height="48" rx="12" fill="#0d242a"/><text x="68" y="916" class="note">THE NET LOOKS STEADIER THAN ITS BRANCHES: east and west each vary ~12–13 Sv while cancellation leaves a 5.64 Sv net range.</text><text x="68" y="934" class="fine">FOUR SAMPLED MONTHLY MEANS · ONE REANALYSIS MEMBER · ARITHMETIC T-TO-U COLLOCATION · NOT AN ANNUAL MEAN, CLIMATOLOGY, MASS CLOSURE, EDDY FLUX, CONVERGENCE, OR ANTARCTIC HEAT DELIVERY</text>
<metadata>{html.escape(payload['boundary'])}</metadata></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-seasons-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m3-oras5-drake-seasons-2018.svg"))
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(payload), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

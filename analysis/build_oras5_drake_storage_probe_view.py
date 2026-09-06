"""Build the M4 sparse storage-tendency probe SVG."""

from __future__ import annotations

import argparse
import html
import json
import pathlib


MONTH_LABELS = {"201802": "FEB", "201805": "MAY", "201808": "AUG", "201811": "NOV"}


def build(payload: dict) -> str:
    states = payload["heat_content"]
    temps = [item["volume_weighted_temperature_degC"] for item in states]
    temp_min, temp_max = 1.20, 1.39
    temp_y = lambda value: 600 - (value - temp_min) / (temp_max - temp_min) * 310
    temp_points = [(160 + index * 155, temp_y(value)) for index, value in enumerate(temps)]
    temp_path = "M" + "L".join(f"{x:.2f},{y:.2f}" for x, y in temp_points)
    temp_marks = []
    for point, item in zip(temp_points, states):
        x, y = point
        temp_marks.append(f'<circle cx="{x}" cy="{y:.2f}" r="8" fill="#62d7ce"/><text x="{x}" y="{y - 17:.2f}" class="temp">{item["volume_weighted_temperature_degC"]:.3f}°C</text><text x="{x}" y="635" class="month">{MONTH_LABELS[item["month"]]}</text>')
    interval_rows = []
    zero, scale = 1000, 2500
    for index, item in enumerate(payload["intervals"]):
        y = 285 + index * 135
        storage = item["storage_tendency_PW"]
        advection = item["endpoint_mean_net_outward_advective_heat_PW_at_0C"]
        remainder = item["unclosed_tendency_plus_advective_divergence_PW"]
        interval_rows.append(f'''
          <text x="785" y="{y - 35}" class="interval">{MONTH_LABELS[item['start_month']]} → {MONTH_LABELS[item['end_month']]} · {item['days_between_representative_dates']:.0f} DAYS</text>
          <line x1="{zero}" y1="{y}" x2="{zero + storage * scale:.2f}" y2="{y}" class="storage"/><text x="{zero + storage * scale - 10:.2f}" y="{y + 4}" class="value end">{storage:+.4f}</text>
          <line x1="{zero}" y1="{y + 28}" x2="{zero + advection * scale:.2f}" y2="{y + 28}" class="advective"/><text x="{zero + advection * scale + 10:.2f}" y="{y + 32}" class="value">{advection:+.4f}</text>
          <line x1="{zero}" y1="{y + 56}" x2="{zero + remainder * scale:.2f}" y2="{y + 56}" class="remainder"/><text x="{zero + remainder * scale + 10:.2f}" y="{y + 60}" class="value">{remainder:+.4f}</text>''')
    geometry = payload["geometry"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="920" viewBox="0 0 1400 920" role="img" aria-labelledby="title desc" data-motion-level="m4-drake-storage-probe">
<title id="title">Sparse Drake control-box heat-storage probe</title><desc id="desc">Four volume-weighted monthly temperatures and three sparse interval comparisons place heat-content storage tendency beside endpoint-average outward advective heat divergence and the remaining unclosed term.</desc>
<defs><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.kicker{{fill:#62d7ce;font-size:14px;font-weight:900;letter-spacing:2.4px}}.title{{fill:#eef9f7;font-size:34px;font-weight:950}}.sub{{fill:#9db3b2;font-size:12px}}.panel{{fill:#0b2127;stroke:#29464c}}.head{{fill:#eef9f7;font-size:15px;font-weight:950}}.label{{fill:#9db3b2;font-size:9px;font-weight:900;letter-spacing:1.1px}}.temp{{fill:#eef9f7;font:900 11px ui-monospace,Consolas,monospace;text-anchor:middle}}.month{{fill:#9db3b2;font-size:10px;font-weight:950;text-anchor:middle}}.interval{{fill:#eef9f7;font-size:10px;font-weight:950}}.storage{{stroke:#7e9dff;stroke-width:12;stroke-linecap:round}}.advective{{stroke:#ffb454;stroke-width:12;stroke-linecap:round}}.remainder{{stroke:#dc83ff;stroke-width:12;stroke-linecap:round}}.value{{fill:#eef9f7;font:900 9px ui-monospace,Consolas,monospace}}.end{{text-anchor:end}}.axis{{stroke:#48646a;stroke-width:1}}.metric{{fill:#eef9f7;font:950 26px ui-monospace,Consolas,monospace}}.metric-label{{fill:#9db3b2;font-size:8.5px;font-weight:900;letter-spacing:1px}}.note{{fill:#a9bfbe;font-size:9.5px}}.fine{{fill:#617d80;font-size:8px}}</style></defs>
<rect width="1400" height="920" fill="#06171c"/><text x="48" y="44" class="kicker">OSW / HEAT MOTION · M4 STORAGE PROBE</text><text x="48" y="88" class="title">STORAGE ENTERS THE BUDGET / IT DOES NOT CLOSE IT</text><text x="48" y="118" class="sub">Native T-cell area + partial thickness · sparse monthly-mean endpoints · primary control box</text>
<rect x="40" y="155" width="690" height="555" rx="16" class="panel"/><text x="70" y="190" class="head">THE BOX COOLS, THEN TURNS SLIGHTLY WARMER</text><text x="70" y="211" class="label">VOLUME-WEIGHTED POTENTIAL TEMPERATURE · NOT HEAT TRANSPORT</text><path d="{temp_path}" fill="none" stroke="#62d7ce" stroke-width="3" opacity=".55"/>{''.join(temp_marks)}
<rect x="750" y="155" width="610" height="555" rx="16" class="panel"/><text x="785" y="190" class="head">THREE TERMS / ONLY TWO ARE MEASURED HERE</text><text x="785" y="211" class="label">PW · STORAGE + ENDPOINT-MEAN OUTWARD ADVECTION = UNCLOSED REMAINDER</text><line x1="{zero}" y1="235" x2="{zero}" y2="675" class="axis"/>{''.join(interval_rows)}
<g transform="translate(48 755)"><text class="metric">{geometry['wet_t_cell_count']:,}</text><text y="22" class="metric-label">WET NATIVE T CELLS</text><text x="330" class="metric">{geometry['box_volume_m3'] / 1e14:.3f} ×10¹⁴ M³</text><text x="330" y="22" class="metric-label">FIXED BOX VOLUME</text><text x="810" class="metric">REFERENCE-INVARIANT</text><text x="810" y="22" class="metric-label">STORAGE TENDENCY AT FIXED VOLUME</text></g>
<g transform="translate(785 681)"><line x1="0" y1="0" x2="35" y2="0" class="storage"/><text x="48" y="4" class="note">STORAGE</text><line x1="145" y1="0" x2="180" y2="0" class="advective"/><text x="193" y="4" class="note">OUTWARD ADVECTION</text><line x1="365" y1="0" x2="400" y2="0" class="remainder"/><text x="413" y="4" class="note">UNCLOSED</text></g>
<rect x="48" y="839" width="1304" height="62" rx="12" fill="#0d242a"/><text x="68" y="859" class="note">THE REMAINDER IS NOT A DISCOVERED HEAT SOURCE. Sparse endpoint sampling and omitted surface, mixing, diffusion, ice, and native tracer terms are inseparable here.</text><text x="68" y="878" class="note">A complete budget requires time-integrated, model-consistent tendencies and fluxes over identical intervals.</text><text x="68" y="894" class="fine">CONSTANT ρ/CP · FOUR MONTHLY MEANS · THREE 89–92 DAY DIFFERENCES · NOT BUDGET CLOSURE, CAUSAL ATTRIBUTION, OR ANTARCTIC DELIVERY</text><metadata>{html.escape(payload['boundary'])}</metadata></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-storage-probe-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m4-oras5-drake-storage-probe-2018.svg"))
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(payload), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

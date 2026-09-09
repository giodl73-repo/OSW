"""Build the M3 Drake gate and temperature-collocation sensitivity SVG."""

from __future__ import annotations

import argparse
import html
import json
import pathlib


MONTH_COLORS = ("#62d7ce", "#ffb454", "#7e9dff", "#dc83ff")


def build(payload: dict) -> str:
    gates = payload["gate_summary"]
    schemes = payload["collocation_summary"]
    gate_min, gate_max = 121.5, 128.5
    gate_x0, gate_width = 150, 500
    gate_x = lambda value: gate_x0 + (value - gate_min) / (gate_max - gate_min) * gate_width
    gate_rows = []
    for index, gate in enumerate(gates):
        y = 260 + index * 92
        values = [r["net_volume_Sv"] for r in payload["gate_records"] if r["x"] == gate["x"]]
        dots = "".join(
            f'<circle cx="{gate_x(value):.2f}" cy="{y}" r="6" fill="{MONTH_COLORS[i]}"/>'
            for i, value in enumerate(values)
        )
        mean_x = gate_x(gate["net_volume_Sv"]["mean"])
        gate_rows.append(f'''
          <text x="72" y="{y - 10}" class="row">{abs(gate['mean_longitude_deg']):.3f}°W</text>
          <text x="72" y="{y + 10}" class="fine">{gate['south_deg']:.1f}°S → {gate['north_deg']:.1f}°S</text>
          <line x1="{gate_x(gate['net_volume_Sv']['minimum']):.2f}" y1="{y}" x2="{gate_x(gate['net_volume_Sv']['maximum']):.2f}" y2="{y}" class="range"/>
          {dots}<path d="M{mean_x:.2f},{y - 14}V{y + 14}" class="mean"/>
          <text x="680" y="{y + 5}" class="number">{gate['net_volume_Sv']['mean']:.3f} Sv</text>''')

    heat_x0, heat_width = 900, 390
    heat_min, heat_max = 1.20, 1.42
    heat_x = lambda value: heat_x0 + (value - heat_min) / (heat_max - heat_min) * heat_width
    scheme_rows = []
    for index, scheme in enumerate(schemes):
        y = 275 + index * 112
        heat = scheme["net_heat_0C_PW"]
        delta = scheme["heat_difference_from_mean_collocation_PW"]["mean"]
        scheme_rows.append(f'''
          <text x="790" y="{y - 17}" class="row">{html.escape(scheme['collocation'].upper())}</text>
          <line x1="{heat_x(heat['minimum']):.2f}" y1="{y}" x2="{heat_x(heat['maximum']):.2f}" y2="{y}" class="heat-range"/>
          <circle cx="{heat_x(heat['mean']):.2f}" cy="{y}" r="8" class="heat-mean"/>
          <text x="{heat_x(heat['mean']):.2f}" y="{y - 15}" class="heat-label">{heat['mean']:.3f}</text>
          <text x="790" y="{y + 22}" class="fine">Δ from mean {delta:+.3f} PW</text>''')

    gate_ticks = "".join(
        f'<line x1="{gate_x(value):.2f}" y1="205" x2="{gate_x(value):.2f}" y2="650" class="grid"/><text x="{gate_x(value):.2f}" y="680" class="axis">{value:.0f}</text>'
        for value in (122, 124, 126, 128)
    )
    heat_ticks = "".join(
        f'<line x1="{heat_x(value):.2f}" y1="205" x2="{heat_x(value):.2f}" y2="650" class="grid"/><text x="{heat_x(value):.2f}" y="680" class="axis">{value:.2f}</text>'
        for value in (1.20, 1.25, 1.30, 1.35, 1.40)
    )
    spread = payload["across_gate_four_sample_mean_volume_Sv"]["range"]
    baseline = next(item for item in schemes if item["collocation"] == "mean")["net_heat_0C_PW"]["mean"]
    max_delta = max(abs(item["heat_difference_from_mean_collocation_PW"]["mean"]) for item in schemes)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="920" viewBox="0 0 1400 920" role="img" aria-labelledby="title desc" data-motion-level="m3-drake-method-sensitivity">
<title id="title">Drake transport sensitivity to gate position and temperature collocation</title>
<desc id="desc">Five nearby ORAS5 native gates produce almost identical four-month mean volume transport, while four temperature-to-velocity-face collocations produce a visible range of reference-relative heat transport.</desc>
<defs><style>
text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.kicker{{fill:#62d7ce;font-size:14px;font-weight:900;letter-spacing:2.4px}}.title{{fill:#eef9f7;font-size:34px;font-weight:950}}.sub{{fill:#9db3b2;font-size:12px}}.panel{{fill:#0b2127;stroke:#29464c}}.head{{fill:#eef9f7;font-size:16px;font-weight:950}}.label{{fill:#9db3b2;font-size:9px;font-weight:900;letter-spacing:1.2px}}.row{{fill:#e8f4f2;font-size:12px;font-weight:900}}.fine{{fill:#789596;font-size:9px;font-weight:800}}.number{{fill:#eef9f7;font:900 12px ui-monospace,Consolas,monospace}}.grid{{stroke:#29464c;stroke-width:1}}.axis{{fill:#789596;font:800 9px ui-monospace,Consolas,monospace;text-anchor:middle}}.range{{stroke:#617d80;stroke-width:5;stroke-linecap:round}}.mean{{stroke:#eef9f7;stroke-width:2}}.heat-range{{stroke:#7e9dff;stroke-width:5;stroke-linecap:round}}.heat-mean{{fill:#62d7ce;stroke:#06171c;stroke-width:2}}.heat-label{{fill:#eef9f7;font:900 10px ui-monospace,Consolas,monospace;text-anchor:middle}}.metric{{fill:#eef9f7;font:950 30px ui-monospace,Consolas,monospace}}.metric-label{{fill:#9db3b2;font-size:9px;font-weight:900;letter-spacing:1px}}.note{{fill:#a9bfbe;font-size:10px}}
</style></defs>
<rect width="1400" height="920" fill="#06171c"/><text x="48" y="44" class="kicker">OSW / HEAT MOTION · M3 METHOD SENSITIVITY</text><text x="48" y="88" class="title">DOES THE GATE MOVE THE ANSWER?</text><text x="48" y="118" class="sub">Four sampled 2018 monthly means · native ORCA025 faces · dimensions kept separate</text>
<rect x="48" y="155" width="690" height="570" rx="16" class="panel"/><text x="72" y="190" class="head">VOLUME / MOVE THE GATE</text><text x="72" y="212" class="label">FIVE LAND-BOUNDED U-FACE SECTIONS · MONTHLY DOTS · FOUR-SAMPLE MEAN TICK · SV</text>{gate_ticks}{''.join(gate_rows)}
<rect x="762" y="155" width="590" height="570" rx="16" class="panel"/><text x="790" y="190" class="head">HEAT / MOVE TEMPERATURE TO THE FACE</text><text x="790" y="212" class="label">FIXED PRIMARY GATE · MONTHLY RANGE + FOUR-SAMPLE MEAN · PW AT TREF 0°C</text>{heat_ticks}{''.join(scheme_rows)}
<g transform="translate(48 770)"><text class="metric">{spread:.3f} SV</text><text y="25" class="metric-label">ACROSS-GATE SPREAD OF FOUR-SAMPLE MEANS</text><text x="430" class="metric">{baseline:.3f} PW</text><text x="430" y="25" class="metric-label">ARITHMETIC-MEAN COLLOCATION BASELINE</text><text x="855" class="metric">±{max_delta:.3f} PW</text><text x="855" y="25" class="metric-label">LARGEST MEAN COLLOCATION SHIFT</text></g>
<rect x="48" y="842" width="1304" height="44" rx="12" fill="#0d242a"/><text x="68" y="862" class="note">VERDICT: nearby gate placement barely moves net volume; offline temperature collocation visibly moves reference-relative heat.</text><text x="68" y="878" class="fine">METHOD SENSITIVITY, NOT OBSERVATIONAL UNCERTAINTY · FOUR MONTHS, ONE REANALYSIS MEMBER · NOT MASS CLOSURE, MODEL-NATIVE TRACER FLUX, CONVERGENCE, OR ANTARCTIC HEAT DELIVERY</text>
<metadata>{html.escape(payload['boundary'])}</metadata></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-method-sensitivity-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m3-oras5-drake-method-sensitivity-2018.svg"))
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(payload), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

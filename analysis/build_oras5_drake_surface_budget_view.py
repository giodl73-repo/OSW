"""Build the M4 native surface-forcing budget SVG."""

from __future__ import annotations

import argparse
import html
import json
import pathlib


LABELS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")


def build(payload: dict) -> str:
    monthly = payload["monthly_surface_heat"]
    intervals = payload["intervals"]
    span = payload["sampled_span"]
    x0, step = 112, 106
    zero_y, flux_scale = 370, 0.82
    monthly_marks = []
    line_points = []
    for index, (label, item) in enumerate(zip(LABELS, monthly)):
        x = x0 + index * step
        watts = item["area_mean_net_downward_surface_heat_W_m2"]
        y = zero_y - watts * flux_scale
        line_points.append((x, y))
        color = "#62d7ce" if watts >= 0 else "#7e9dff"
        monthly_marks.append(
            f'<line x1="{x}" y1="{zero_y}" x2="{x}" y2="{y:.2f}" stroke="{color}" stroke-width="9" stroke-linecap="round"/>'
            f'<circle cx="{x}" cy="{y:.2f}" r="5" fill="{color}"/>'
            f'<text x="{x}" y="{y - 12 if watts >= 0 else y + 22:.2f}" class="smallvalue">{watts:+.1f}</text>'
            f'<text x="{x}" y="405" class="month">{label}</text>'
        )
    flux_path = "M" + "L".join(f"{x:.2f},{y:.2f}" for x, y in line_points)

    budget_zero, budget_scale = 700, 1550
    interval_marks = []
    for index, item in enumerate(intervals):
        x = x0 + (index + .5) * step
        components = (
            (-22, item["storage_tendency_PW"], "#7e9dff", "storage"),
            (-7, item["endpoint_mean_net_outward_advective_heat_PW_at_0C"], "#ffb454", "outward advection"),
            (8, -item["endpoint_mean_net_downward_surface_heat_PW"], "#62d7ce", "minus surface input"),
        )
        for dx, value, color, role in components:
            y = budget_zero - value * budget_scale
            interval_marks.append(f'<line x1="{x + dx:.2f}" y1="{budget_zero}" x2="{x + dx:.2f}" y2="{y:.2f}" stroke="{color}" stroke-width="8" stroke-linecap="round"><title>{role}: {value:+.4f} PW</title></line>')
        remaining_y = budget_zero - item["remaining_after_surface_heat_PW"] * budget_scale
        interval_marks.append(f'<path d="M{x + 25:.2f},{remaining_y - 6:.2f}L{x + 31:.2f},{remaining_y:.2f}L{x + 25:.2f},{remaining_y + 6:.2f}L{x + 19:.2f},{remaining_y:.2f}Z" fill="#dc83ff"><title>remaining: {item["remaining_after_surface_heat_PW"]:+.4f} PW</title></path><text x="{x:.2f}" y="735" class="interval">{LABELS[index]}–{LABELS[index + 1]}</text>')

    before = span["mean_unclosed_PW"]
    surface = span["time_weighted_mean_net_downward_surface_heat_PW"]
    after = span["mean_remaining_after_surface_heat_PW"]
    fraction = 100 * span["surface_fraction_of_pre_surface_remainder"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="980" viewBox="0 0 1400 980" role="img" aria-labelledby="title desc" data-motion-level="m4-drake-surface-budget">
<title id="title">Native ORAS5 surface heat explains part of the Drake control-box remainder</title><desc id="desc">Monthly native net downward surface heat flux is added to the twelve-month storage and outward-advection probe. Surface forcing accounts for 31 percent of the prior mean remainder, leaving 0.0427 petawatts unresolved.</desc>
<defs><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.kicker{{fill:#62d7ce;font-size:14px;font-weight:900;letter-spacing:2.4px}}.title{{fill:#eef9f7;font-size:34px;font-weight:950}}.sub{{fill:#9db3b2;font-size:12px}}.panel{{fill:#0b2127;stroke:#29464c}}.head{{fill:#eef9f7;font-size:15px;font-weight:950}}.label{{fill:#9db3b2;font-size:9px;font-weight:900;letter-spacing:1.1px}}.month{{fill:#9db3b2;font-size:9px;font-weight:950;text-anchor:middle}}.smallvalue{{fill:#eef9f7;font:850 8px ui-monospace,Consolas,monospace;text-anchor:middle}}.axis{{stroke:#48646a;stroke-width:1}}.interval{{fill:#789596;font:850 7.5px ui-monospace,Consolas,monospace;text-anchor:middle}}.metric{{fill:#eef9f7;font:950 26px ui-monospace,Consolas,monospace}}.metric-label{{fill:#9db3b2;font-size:8.5px;font-weight:900;letter-spacing:1px}}.equation{{fill:#d9e8e6;font:800 13px ui-monospace,Consolas,monospace}}.note{{fill:#a9bfbe;font-size:9.5px}}.fine{{fill:#617d80;font-size:8px}}</style></defs>
<rect width="1400" height="980" fill="#06171c"/><text x="48" y="44" class="kicker">OSW / HEAT MOTION · M4 NATIVE SURFACE FORCING</text><text x="48" y="88" class="title">THE SURFACE EXPLAINS PART — NOT ALL</text><text x="48" y="118" class="sub">Same ORCA025 grid · same Drake control box · twelve monthly means · positive surface flux enters the ocean</text>
<rect x="40" y="150" width="1320" height="620" rx="16" class="panel"/><text x="72" y="184" class="head">WHAT THE SURFACE ADDS</text><text x="72" y="205" class="label">AREA-MEAN NET DOWNWARD HEAT FLUX · W/M² · CYAN INTO OCEAN · BLUE OUT OF OCEAN</text><line x1="72" y1="{zero_y}" x2="1328" y2="{zero_y}" class="axis"/><path d="{flux_path}" fill="none" stroke="#62d7ce" stroke-width="2" opacity=".32"/>{''.join(monthly_marks)}
<line x1="72" y1="445" x2="1328" y2="445" stroke="#29464c"/><text x="72" y="478" class="head">WHERE THE REMAINDER GOES AFTER SURFACE FORCING</text><text x="72" y="499" class="label">SIGNED PW · BLUE STORAGE + ORANGE OUTWARD ADVECTION − CYAN DOWNWARD SURFACE = MAGENTA REMAINING</text><line x1="72" y1="{budget_zero}" x2="1328" y2="{budget_zero}" class="axis"/>{''.join(interval_marks)}
<g transform="translate(48 820)"><text class="metric">{before:+.4f} PW</text><text y="22" class="metric-label">BEFORE SURFACE TERM</text><text x="330" class="metric">− {surface:.4f} PW</text><text x="330" y="22" class="metric-label">NET DOWNWARD SURFACE INPUT</text><text x="690" class="metric">= {after:+.4f} PW</text><text x="690" y="22" class="metric-label">STILL REMAINING</text><text x="1030" class="metric">{fraction:.0f}%</text><text x="1030" y="22" class="metric-label">OF PRIOR GAP EXPLAINED</text></g>
<rect x="48" y="884" width="1304" height="58" rx="12" fill="#0d242a"/><text x="68" y="904" class="equation">dH/dt + outward advection − downward surface input = remaining</text><text x="68" y="922" class="note">Every interval remains positive after the surface term. The unresolved mean falls from {before:.4f} to {after:.4f} PW.</text><text x="68" y="937" class="fine">ORAS5 MODEL/REANALYSIS FLUX, INCLUDING SURFACE-RESTORING CONTEXT · NOT DIRECT OBSERVATION OR MODEL-NATIVE TRACER-BUDGET CLOSURE · ICE/MIXING/DIFFUSION/INCREMENTS UNRESOLVED</text><metadata>{html.escape(payload['boundary'])}</metadata></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-surface-budget-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m4-oras5-drake-surface-budget-2018.svg"))
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(payload), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

"""Build the M4 nested-control-box sensitivity SVG."""

from __future__ import annotations

import argparse
import html
import json
import math
import pathlib


def heat0(item: dict) -> float:
    return next(case["net_outward_PW"]["mean"] for case in item["net_outward_heat_PW"] if case["reference_temperature_degC"] == 0)


def build(payload: dict) -> str:
    east = [item for item in payload["variants"] if item["family"] == "eastward_extent"]
    north = [item for item in payload["variants"] if item["family"] == "northward_extent"]
    family = {item["family"]: item for item in payload["family_summary"]}
    worst_volume = max(item["maximum_absolute_monthly_volume_imbalance_Sv"] for item in family.values())
    conservative_volume_bound = math.ceil(worst_volume * 1000) / 1000
    heat_x0, heat_width = 250, 420
    heat_x = lambda value: heat_x0 + value / .06 * heat_width
    east_rows = []
    for index, item in enumerate(east):
        y = 285 + index * 92
        value = heat0(item)
        east_rows.append(f'<text x="72" y="{y + 5}" class="row">TO {abs(item["extent"]["east_mean_longitude_deg"]):.3f}°W</text><line x1="{heat_x0}" y1="{y}" x2="{heat_x(value):.2f}" y2="{y}" class="heat"/><circle cx="{heat_x(value):.2f}" cy="{y}" r="7" fill="#62d7ce"/><text x="{heat_x(value) + 13:.2f}" y="{y + 5}" class="value">{value:.3f} PW</text><text x="72" y="{y + 23}" class="fine">Q imbalance {item["net_outward_volume_Sv"]["mean"]:.4f} Sv</text>')
    north_rows = []
    for index, item in enumerate(north):
        y = 285 + index * 92
        value = heat0(item)
        x0 = 965
        x = x0 + value / .06 * 330
        north_rows.append(f'<text x="800" y="{y + 5}" class="row">TO {abs(item["extent"]["north_mean_latitude_deg"]):.3f}°S</text><line x1="{x0}" y1="{y}" x2="{x:.2f}" y2="{y}" class="heat"/><circle cx="{x:.2f}" cy="{y}" r="7" fill="#62d7ce"/><text x="{x + 13:.2f}" y="{y + 5}" class="value">{value:.3f} PW</text><text x="800" y="{y + 23}" class="fine">Q imbalance {item["net_outward_volume_Sv"]["mean"]:.4f} Sv</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="920" viewBox="0 0 1400 920" role="img" aria-labelledby="title desc" data-motion-level="m4-drake-control-box-sensitivity">
<title id="title">Nested Drake control-box geometry sensitivity</title><desc id="desc">Two matched panels expand the native control box eastward and northward, showing that every box remains tightly volume-balanced while mean zero-degree-reference advective heat divergence changes with box geometry.</desc>
<defs><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.kicker{{fill:#62d7ce;font-size:14px;font-weight:900;letter-spacing:2.4px}}.title{{fill:#eef9f7;font-size:34px;font-weight:950}}.sub{{fill:#9db3b2;font-size:12px}}.panel{{fill:#0b2127;stroke:#29464c}}.head{{fill:#eef9f7;font-size:15px;font-weight:950}}.label{{fill:#9db3b2;font-size:9px;font-weight:900;letter-spacing:1.1px}}.row{{fill:#eef9f7;font-size:11px;font-weight:950}}.heat{{stroke:#29464c;stroke-width:8;stroke-linecap:round}}.value{{fill:#eef9f7;font:900 10px ui-monospace,Consolas,monospace}}.fine{{fill:#789596;font:800 8.5px ui-monospace,Consolas,monospace}}.metric{{fill:#eef9f7;font:950 28px ui-monospace,Consolas,monospace}}.metric-label{{fill:#9db3b2;font-size:8.5px;font-weight:900;letter-spacing:1px}}.note{{fill:#a9bfbe;font-size:9.5px}}</style></defs>
<rect width="1400" height="920" fill="#06171c"/><text x="48" y="44" class="kicker">OSW / HEAT MOTION · M4 GEOMETRY CHALLENGE</text><text x="48" y="88" class="title">THE BOX CLOSES / THE HEAT RESIDUAL MOVES</text><text x="48" y="118" class="sub">Nested native boxes · four-sample means · signed outward advective flux</text>
<rect x="40" y="155" width="690" height="545" rx="16" class="panel"/><text x="72" y="190" class="head">EXPAND EASTWARD</text><text x="72" y="211" class="label">WEST FIXED AT 69.125°W · NORTH/SOUTH FIXED · NET HEAT AT TREF 0°C</text><path d="M85 235H690" stroke="#29464c"/>{''.join(east_rows)}
<rect x="750" y="155" width="610" height="545" rx="16" class="panel"/><text x="800" y="190" class="head">EXPAND NORTHWARD</text><text x="800" y="211" class="label">SOUTH FIXED AT 66.162°S · EAST/WEST FIXED · NET HEAT AT TREF 0°C</text><path d="M800 235H1328" stroke="#29464c"/>{''.join(north_rows)}
<g transform="translate(48 750)"><text class="metric">{family['eastward_extent']['heat_0C_mean_PW_across_boxes']['range']:.4f} PW</text><text y="23" class="metric-label">HEAT RANGE · EASTWARD EXTENT</text><text x="420" class="metric">{family['northward_extent']['heat_0C_mean_PW_across_boxes']['range']:.4f} PW</text><text x="420" y="23" class="metric-label">HEAT RANGE · NORTHWARD EXTENT</text><text x="860" class="metric">&lt; {conservative_volume_bound:.3f} SV</text><text x="860" y="23" class="metric-label">WORST MONTHLY VOLUME IMBALANCE · ALL BOXES</text></g>
<rect x="48" y="837" width="1304" height="58" rx="12" fill="#0d242a"/><text x="68" y="857" class="note">VERDICT: near-zero volume imbalance is robust across these boxes; the advective heat residual is geometry-dependent.</text><text x="68" y="875" class="note">Therefore 0.055 PW belongs to one declared box—not to “Drake Passage” as a universal heat-convergence number.</text><text x="68" y="890" class="fine">METHOD SENSITIVITY, NOT OBSERVATIONAL UNCERTAINTY · NO STORAGE, SURFACE FLUX, DIFFUSION, NATIVE TRACER-BUDGET CLOSURE, OR ANTARCTIC DELIVERY</text><metadata>{html.escape(payload['boundary'])}</metadata></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-control-box-sensitivity-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m4-oras5-drake-control-box-sensitivity-2018.svg"))
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(payload), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

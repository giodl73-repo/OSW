"""Build the twelve-month M4 compact budget probe SVG."""

from __future__ import annotations

import argparse
import html
import json
import pathlib


LABELS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")


def build(payload: dict) -> str:
    monthly = payload["monthly"]
    x0, step = 105, 108
    temp_min, temp_max = 1.20, 1.39
    temp_y = lambda value: 405 - (value - temp_min) / (temp_max - temp_min) * 180
    temp_points = [(x0 + index * step, temp_y(item["volume_weighted_temperature_degC"])) for index, item in enumerate(monthly)]
    temp_path = "M" + "L".join(f"{x:.2f},{y:.2f}" for x, y in temp_points)
    temp_marks = []
    for label, point, item in zip(LABELS, temp_points, monthly):
        x, y = point
        temp_marks.append(f'<circle cx="{x}" cy="{y:.2f}" r="6" fill="#62d7ce"/><text x="{x}" y="{y - 13:.2f}" class="smallvalue">{item["volume_weighted_temperature_degC"]:.3f}</text><text x="{x}" y="438" class="month">{label}</text>')
    baseline, scale = 650, 1700
    interval_marks = []
    for index, item in enumerate(payload["intervals"]):
        x = x0 + (index + .5) * step
        storage = item["storage_tendency_PW"]
        advection = item["endpoint_mean_net_outward_advective_heat_PW_at_0C"]
        unclosed = item["unclosed_PW"]
        storage_y = baseline - storage * scale
        adv_y = baseline - advection * scale
        remainder_y = baseline - unclosed * scale
        interval_marks.append(f'''
          <line x1="{x - 13:.2f}" y1="{baseline}" x2="{x - 13:.2f}" y2="{storage_y:.2f}" class="storage"/>
          <line x1="{x + 7:.2f}" y1="{baseline}" x2="{x + 7:.2f}" y2="{adv_y:.2f}" class="advective"/>
          <path d="M{x + 20:.2f},{remainder_y - 6:.2f}L{x + 26:.2f},{remainder_y:.2f}L{x + 20:.2f},{remainder_y + 6:.2f}L{x + 14:.2f},{remainder_y:.2f}Z" fill="#dc83ff"/>
          <text x="{x:.2f}" y="680" class="interval">{LABELS[index]}–{LABELS[index + 1]}</text>''')
    span = payload["sampled_span"]
    max_q = max(abs(item["net_outward_volume_Sv"]) for item in monthly)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="940" viewBox="0 0 1400 940" role="img" aria-labelledby="title desc" data-motion-level="m4-drake-monthly-budget">
<title id="title">Twelve-month compact native Drake storage and advection probe</title><desc id="desc">Monthly volume-weighted box temperature and eleven adjacent-month comparisons show storage tendency, endpoint-average outward advective heat divergence, and the still-unclosed remainder from January through December 2018.</desc>
<defs><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.kicker{{fill:#62d7ce;font-size:14px;font-weight:900;letter-spacing:2.4px}}.title{{fill:#eef9f7;font-size:34px;font-weight:950}}.sub{{fill:#9db3b2;font-size:12px}}.panel{{fill:#0b2127;stroke:#29464c}}.head{{fill:#eef9f7;font-size:15px;font-weight:950}}.label{{fill:#9db3b2;font-size:9px;font-weight:900;letter-spacing:1.1px}}.month{{fill:#9db3b2;font-size:9px;font-weight:950;text-anchor:middle}}.smallvalue{{fill:#eef9f7;font:850 8px ui-monospace,Consolas,monospace;text-anchor:middle}}.axis{{stroke:#48646a;stroke-width:1}}.storage{{stroke:#7e9dff;stroke-width:10;stroke-linecap:round}}.advective{{stroke:#ffb454;stroke-width:10;stroke-linecap:round}}.interval{{fill:#789596;font:850 7.5px ui-monospace,Consolas,monospace;text-anchor:middle}}.metric{{fill:#eef9f7;font:950 27px ui-monospace,Consolas,monospace}}.metric-label{{fill:#9db3b2;font-size:8.5px;font-weight:900;letter-spacing:1px}}.note{{fill:#a9bfbe;font-size:9.5px}}.fine{{fill:#617d80;font-size:8px}}</style></defs>
<rect width="1400" height="940" fill="#06171c"/><text x="48" y="44" class="kicker">OSW / HEAT MOTION · M4 MONTHLY BUDGET PROBE</text><text x="48" y="88" class="title">TWELVE MONTHS / THE GAP PERSISTS</text><text x="48" y="118" class="sub">Compact native control-box states · 15 January–15 December 2018 · exact four-month anchor reproduction</text>
<rect x="40" y="155" width="1320" height="570" rx="16" class="panel"/><text x="72" y="190" class="head">MONTHLY BOX TEMPERATURE</text><text x="72" y="211" class="label">VOLUME-WEIGHTED POTENTIAL TEMPERATURE · °C</text><path d="{temp_path}" fill="none" stroke="#62d7ce" stroke-width="3" opacity=".55"/>{''.join(temp_marks)}
<line x1="72" y1="475" x2="1328" y2="475" stroke="#29464c"/><text x="72" y="505" class="head">ELEVEN ADJACENT-MONTH INTERVALS</text><text x="72" y="525" class="label">SIGNED PW · BLUE STORAGE · ORANGE OUTWARD ADVECTION · MAGENTA DIAMOND UNCLOSED</text><line x1="72" y1="{baseline}" x2="1328" y2="{baseline}" class="axis"/>{''.join(interval_marks)}
<g transform="translate(48 770)"><text class="metric">{span['mean_storage_tendency_PW']:+.4f} PW</text><text y="22" class="metric-label">334-DAY MEAN STORAGE TENDENCY</text><text x="380" class="metric">{span['time_weighted_mean_outward_advective_heat_PW_at_0C']:+.4f} PW</text><text x="380" y="22" class="metric-label">TIME-WEIGHTED OUTWARD ADVECTION · TREF 0°C</text><text x="865" class="metric">{span['mean_unclosed_PW']:+.4f} PW</text><text x="865" y="22" class="metric-label">MEAN UNCLOSED REMAINDER</text></g>
<rect x="48" y="842" width="1304" height="58" rx="12" fill="#0d242a"/><text x="68" y="862" class="note">DENSER SAMPLING CHANGES THE CURVE, NOT THE VERDICT: every interval retains a positive unclosed remainder.</text><text x="68" y="880" class="note">The twelve compact states reproduce all four prior anchor calculations exactly; maximum monthly volume imbalance is {max_q:.5f} Sv.</text><text x="68" y="895" class="fine">MONTHLY-MEAN ENDPOINTS + TRAPEZOIDAL ADVECTION · NOT TIME-INTEGRATED NATIVE BUDGET CLOSURE, SURFACE/ICE/MIXING/DIFFUSIVE ATTRIBUTION, OR ANTARCTIC DELIVERY</text><metadata>{html.escape(payload['boundary'])}</metadata></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-monthly-budget-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m4-oras5-drake-monthly-budget-2018.svg"))
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(payload), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

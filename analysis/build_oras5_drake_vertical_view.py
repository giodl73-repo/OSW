"""Build the M3 Drake vertical-anatomy SVG."""

from __future__ import annotations

import argparse
import html
import json
import pathlib


def build(payload: dict) -> str:
    rows = payload["summary"]
    y_values = (255, 355, 455, 555, 655)
    volume_scale, heat_scale = 4.2, 410
    volume_zero, heat_zero = 375, 1045
    content = []
    for row, y in zip(rows, y_values):
        vp = row["positive_volume_Sv"]["mean"]
        vn = abs(row["negative_volume_Sv"]["mean"])
        hp = row["positive_heat_0C_PW"]["mean"]
        hn = abs(row["negative_heat_0C_PW"]["mean"])
        content.append(f'''
          <text x="62" y="{y + 5}" class="band">{html.escape(row['band'])}</text>
          <line x1="{volume_zero}" y1="{y}" x2="{volume_zero + vp * volume_scale:.2f}" y2="{y}" class="east"/>
          <line x1="{volume_zero}" y1="{y + 22}" x2="{volume_zero - vn * volume_scale:.2f}" y2="{y + 22}" class="west"/>
          <text x="{volume_zero + vp * volume_scale + 10:.2f}" y="{y + 4}" class="value">+{vp:.1f}</text>
          <text x="{volume_zero - vn * volume_scale - 10:.2f}" y="{y + 26}" class="value end">−{vn:.1f}</text>
          <text x="655" y="{y + 15}" class="net">{row['net_volume_Sv']['mean']:+.1f}</text>
          <line x1="{heat_zero}" y1="{y}" x2="{heat_zero + hp * heat_scale:.2f}" y2="{y}" class="heat-east"/>
          <line x1="{heat_zero}" y1="{y + 22}" x2="{heat_zero - hn * heat_scale:.2f}" y2="{y + 22}" class="heat-west"/>
          <text x="{heat_zero + hp * heat_scale + 10:.2f}" y="{y + 4}" class="value">+{hp:.3f}</text>
          <text x="{heat_zero - hn * heat_scale - 10:.2f}" y="{y + 26}" class="value end">−{hn:.3f}</text>
          <text x="1320" y="{y + 15}" class="net end">{row['net_heat_0C_PW']['mean']:+.3f}</text>''')
    net_volume = sum(row["net_volume_Sv"]["mean"] for row in rows)
    net_heat = sum(row["net_heat_0C_PW"]["mean"] for row in rows)
    shallow_heat = sum(row["net_heat_0C_PW"]["mean"] for row in rows[:2]) / net_heat * 100
    deep_volume = sum(row["net_volume_Sv"]["mean"] for row in rows[2:]) / net_volume * 100
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="920" viewBox="0 0 1400 920" role="img" aria-labelledby="title desc" data-motion-level="m3-drake-vertical-anatomy">
<title id="title">Vertical anatomy of Drake Passage volume and heat transport</title><desc id="desc">Five declared depth strata compare opposing and net volume transport with opposing and net reference-relative heat transport across four sampled 2018 ORAS5 months.</desc>
<defs><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.kicker{{fill:#62d7ce;font-size:14px;font-weight:900;letter-spacing:2.4px}}.title{{fill:#eef9f7;font-size:34px;font-weight:950}}.sub{{fill:#9db3b2;font-size:12px}}.head{{fill:#eef9f7;font-size:15px;font-weight:950}}.label{{fill:#9db3b2;font-size:9px;font-weight:900;letter-spacing:1.2px}}.band{{fill:#eef9f7;font-size:13px;font-weight:950}}.axis{{stroke:#48646a;stroke-width:1}}.east{{stroke:#ffb454;stroke-width:13;stroke-linecap:round}}.west{{stroke:#7e9dff;stroke-width:13;stroke-linecap:round}}.heat-east{{stroke:#62d7ce;stroke-width:13;stroke-linecap:round}}.heat-west{{stroke:#dc83ff;stroke-width:13;stroke-linecap:round}}.value{{fill:#c8d8d6;font:900 9px ui-monospace,Consolas,monospace}}.end{{text-anchor:end}}.net{{fill:#eef9f7;font:950 14px ui-monospace,Consolas,monospace}}.metric{{fill:#eef9f7;font:950 30px ui-monospace,Consolas,monospace}}.metric-label{{fill:#9db3b2;font-size:9px;font-weight:900;letter-spacing:1px}}.note{{fill:#a9bfbe;font-size:10px}}.fine{{fill:#617d80;font-size:8.5px}}</style></defs>
<rect width="1400" height="920" fill="#06171c"/><text x="48" y="44" class="kicker">OSW / HEAT MOTION · M3 VERTICAL ANATOMY</text><text x="48" y="88" class="title">THE WATER IS DEEP / THE HEAT SIGNAL IS SHALLOWER</text><text x="48" y="118" class="sub">Four-sample means · 67.125°W native gate · opposing branches remain visible</text>
<rect x="40" y="155" width="690" height="565" rx="16" fill="#0b2127" stroke="#29464c"/><text x="62" y="190" class="head">VOLUME TRANSPORT</text><text x="62" y="211" class="label">EASTWARD / WESTWARD BRANCHES · SV</text><line x1="{volume_zero}" y1="225" x2="{volume_zero}" y2="690" class="axis"/><text x="655" y="211" class="label">NET</text>
<rect x="748" y="155" width="612" height="565" rx="16" fill="#0b2127" stroke="#29464c"/><text x="772" y="190" class="head">REFERENCE-RELATIVE HEAT</text><text x="772" y="211" class="label">EASTWARD / WESTWARD BRANCHES · PW AT TREF 0°C</text><line x1="{heat_zero}" y1="225" x2="{heat_zero}" y2="690" class="axis"/><text x="1320" y="211" class="label" text-anchor="end">NET</text>{''.join(content)}
<g transform="translate(48 772)"><text class="metric">{deep_volume:.1f}%</text><text y="25" class="metric-label">OF NET VOLUME BELOW 700 M</text><text x="400" class="metric">{shallow_heat:.1f}%</text><text x="400" y="25" class="metric-label">OF 0°C-REFERENCE NET HEAT ABOVE 700 M</text><text x="895" class="metric">{net_volume:.2f} SV / {net_heat:.3f} PW</text><text x="895" y="25" class="metric-label">STRATA SUM BACK TO SECTION</text></g>
<rect x="48" y="842" width="1304" height="44" rx="12" fill="#0d242a"/><text x="68" y="862" class="note">Depth changes the story: substantial net water transport persists below 700 m, while temperature weighting concentrates the 0°C-reference heat signal upward.</text><text x="68" y="878" class="fine">DECLARED MIDPOINT DEPTH BINS · NOT WATER MASSES, OVERTURNING CLASSES, CONVERGENCE, MODEL-NATIVE TRACER FLUX, OR ANTARCTIC HEAT DELIVERY</text><metadata>{html.escape(payload['boundary'])}</metadata></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-vertical-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m3-oras5-drake-vertical-2018.svg"))
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(payload), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

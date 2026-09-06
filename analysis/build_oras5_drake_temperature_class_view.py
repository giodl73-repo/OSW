"""Build the M3 Drake temperature-class transport SVG."""

from __future__ import annotations

import argparse
import html
import json
import pathlib


COLORS = ("#8ca8ff", "#71c5e8", "#62d7ce", "#b8db75", "#ffb454", "#ff806d")


def build(payload: dict) -> str:
    rows = payload["summary"]
    y_values = (245, 330, 415, 500, 585, 670)
    zero, volume_scale = 390, 3.45
    heat_x0, heat_width = 865, 420
    heat_x = lambda value: heat_x0 + (value + .02) / .55 * heat_width
    content = []
    for index, (row, y) in enumerate(zip(rows, y_values)):
        positive = row["positive_volume_Sv"]["mean"]
        negative = abs(row["negative_volume_Sv"]["mean"])
        net_heat = row["net_heat_0C_PW"]["mean"]
        content.append(f'''
          <rect x="58" y="{y - 18}" width="9" height="36" rx="4" fill="{COLORS[index]}"/><text x="80" y="{y + 5}" class="class">{html.escape(row['class'])}</text>
          <line x1="{zero}" y1="{y - 8}" x2="{zero + positive * volume_scale:.2f}" y2="{y - 8}" class="east"/>
          <line x1="{zero}" y1="{y + 12}" x2="{zero - negative * volume_scale:.2f}" y2="{y + 12}" class="west"/>
          <text x="{zero + positive * volume_scale + 9:.2f}" y="{y - 4}" class="value">+{positive:.1f}</text>
          <text x="{zero - negative * volume_scale - 9:.2f}" y="{y + 16}" class="value end">−{negative:.1f}</text>
          <text x="710" y="{y + 5}" class="net">{row['net_volume_Sv']['mean']:+.1f}</text>
          <line x1="{heat_x(0):.2f}" y1="{y}" x2="{heat_x(net_heat):.2f}" y2="{y}" stroke="{COLORS[index]}" stroke-width="15" stroke-linecap="round"/>
          <text x="{heat_x(net_heat) + (10 if net_heat >= 0 else -10):.2f}" y="{y + 4}" class="value {'end' if net_heat < 0 else ''}">{net_heat:+.3f}</text>''')
    west_total = abs(sum(row["negative_volume_Sv"]["mean"] for row in rows))
    cold_west = abs(sum(row["negative_volume_Sv"]["mean"] for row in rows[:3]))
    net_total = sum(row["net_volume_Sv"]["mean"] for row in rows)
    mid_net = sum(row["net_volume_Sv"]["mean"] for row in rows[2:4])
    heat_total = sum(row["net_heat_0C_PW"]["mean"] for row in rows)
    ticks = "".join(f'<line x1="{heat_x(v):.2f}" y1="205" x2="{heat_x(v):.2f}" y2="700" class="grid"/><text x="{heat_x(v):.2f}" y="725" class="axis">{v:.1f}</text>' for v in (0, .1, .2, .3, .4, .5))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="920" viewBox="0 0 1400 920" role="img" aria-labelledby="title desc" data-motion-level="m3-drake-temperature-classes">
<title id="title">Drake Passage transport partitioned by potential-temperature class</title><desc id="desc">Six declared potential-temperature classes compare eastward and westward volume branches and net heat transport relative to zero degrees Celsius across four sampled 2018 ORAS5 months.</desc>
<defs><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.kicker{{fill:#62d7ce;font-size:14px;font-weight:900;letter-spacing:2.4px}}.title{{fill:#eef9f7;font-size:34px;font-weight:950}}.sub{{fill:#9db3b2;font-size:12px}}.panel{{fill:#0b2127;stroke:#29464c}}.head{{fill:#eef9f7;font-size:15px;font-weight:950}}.label{{fill:#9db3b2;font-size:9px;font-weight:900;letter-spacing:1.2px}}.class{{fill:#eef9f7;font-size:13px;font-weight:950}}.east{{stroke:#ffb454;stroke-width:12;stroke-linecap:round}}.west{{stroke:#7e9dff;stroke-width:12;stroke-linecap:round}}.value{{fill:#c8d8d6;font:900 9px ui-monospace,Consolas,monospace}}.end{{text-anchor:end}}.net{{fill:#eef9f7;font:950 14px ui-monospace,Consolas,monospace}}.grid{{stroke:#29464c;stroke-width:1}}.axis{{fill:#789596;font:800 9px ui-monospace,Consolas,monospace;text-anchor:middle}}.metric{{fill:#eef9f7;font:950 30px ui-monospace,Consolas,monospace}}.metric-label{{fill:#9db3b2;font-size:9px;font-weight:900;letter-spacing:1px}}.note{{fill:#a9bfbe;font-size:10px}}.fine{{fill:#617d80;font-size:8.5px}}</style></defs>
<rect width="1400" height="920" fill="#06171c"/><text x="48" y="44" class="kicker">OSW / HEAT MOTION · M3 TEMPERATURE POPULATIONS</text><text x="48" y="88" class="title">THE RETURN FLOW IS COLDER</text><text x="48" y="118" class="sub">Potential-temperature classes · four-sample means · 67.125°W native gate</text>
<rect x="40" y="155" width="715" height="595" rx="16" class="panel"/><text x="58" y="190" class="head">WHO CARRIES THE WATER?</text><text x="58" y="211" class="label">EASTWARD / WESTWARD VOLUME BRANCHES · SV</text><line x1="{zero}" y1="215" x2="{zero}" y2="705" stroke="#48646a"/><text x="710" y="211" class="label">NET</text>
<rect x="775" y="155" width="585" height="595" rx="16" class="panel"/><text x="800" y="190" class="head">WHO CARRIES THE 0°C-REFERENCE HEAT SIGNAL?</text><text x="800" y="211" class="label">NET ADVECTIVE HEAT · PW</text>{ticks}{''.join(content)}
<g transform="translate(48 790)"><text class="metric">{cold_west / west_total * 100:.1f}%</text><text y="25" class="metric-label">OF WESTWARD FLOW AT OR BELOW 2°C</text><text x="430" class="metric">{mid_net / net_total * 100:.1f}%</text><text x="430" y="25" class="metric-label">OF NET VOLUME IN THE 1–3°C CLASSES</text><text x="885" class="metric">{heat_total:.3f} PW</text><text x="885" y="25" class="metric-label">ALL CLASSES SUM TO SECTION AT TREF 0°C</text></g>
<rect x="48" y="856" width="1304" height="38" rx="12" fill="#0d242a"/><text x="68" y="874" class="note">TEMPERATURE CLASSES ARE NOT WATER MASSES: salinity, density, neutral surfaces, source history, and mixing are absent.</text><text x="68" y="888" class="fine">ARITHMETIC T-TO-U COLLOCATION · FOUR MONTHS, ONE REANALYSIS MEMBER · NOT MODEL-NATIVE TRACER FLUX, CONVERGENCE, OR ANTARCTIC HEAT DELIVERY</text><metadata>{html.escape(payload['boundary'])}</metadata></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-temperature-classes-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m3-oras5-drake-temperature-classes-2018.svg"))
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(payload), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

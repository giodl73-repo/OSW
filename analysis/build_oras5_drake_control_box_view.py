"""Build the first M4 native Drake control-box SVG."""

from __future__ import annotations

import argparse
import html
import json
import pathlib


MONTH_LABELS = {"201802": "FEB", "201805": "MAY", "201808": "AUG", "201811": "NOV"}


def heat_at(boundary: dict, reference: float) -> float:
    return next(item["net_PW"]["mean"] for item in boundary["heat_transport_PW"] if item["reference_temperature_degC"] == reference)


def build(payload: dict) -> str:
    summary = payload["summary"]
    boundaries = {item["name"]: item for item in summary["boundaries"]}
    west, east, south, north = (boundaries[name] for name in ("west", "east", "south", "north"))
    monthly = []
    heat_scale = 3100
    for index, month in enumerate(payload["months"]):
        y = 272 + index * 94
        heat0 = next(item["net_boundary_PW"] for item in month["net_outward_heat_PW"] if item["reference_temperature_degC"] == 0)
        monthly.append(f'<text x="890" y="{y + 5}" class="row">{MONTH_LABELS[month["month"]]}</text><rect x="950" y="{y - 10}" width="{heat0 * heat_scale:.2f}" height="20" rx="10" fill="#62d7ce"/><text x="{965 + heat0 * heat_scale:.2f}" y="{y + 5}" class="value">{heat0:.3f} PW</text>')
    reference_summary = summary["net_outward_heat_PW"]
    ref_min, ref_max = .05445, .05482
    ref_x = lambda value: 920 + (value - ref_min) / (ref_max - ref_min) * 350
    reference_marks = []
    for item in reference_summary:
        value = item["net_outward_PW"]["mean"]
        label = f"{item['reference_temperature_degC']:g}°C"
        reference_marks.append(f'<circle cx="{ref_x(value):.2f}" cy="676" r="7" fill="#ffb454"/><text x="{ref_x(value):.2f}" y="660" class="ref">{label}</text>')
    geometry = payload["geometry"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="920" viewBox="0 0 1400 920" role="img" aria-labelledby="title desc" data-motion-level="m4-drake-control-box">
<title id="title">Four-boundary native Drake control-box flux pilot</title><desc id="desc">A schematic control box shows four-sample mean outward volume and zero-degree-reference heat flux at western, eastern, southern, and northern native boundaries, beside monthly net advective heat divergence and its small reference-temperature sensitivity.</desc>
<defs><marker id="arrow-in" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#7e9dff"/></marker><marker id="arrow-out" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#ffb454"/></marker><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.kicker{{fill:#62d7ce;font-size:14px;font-weight:900;letter-spacing:2.4px}}.title{{fill:#eef9f7;font-size:34px;font-weight:950}}.sub{{fill:#9db3b2;font-size:12px}}.panel{{fill:#0b2127;stroke:#29464c}}.head{{fill:#eef9f7;font-size:15px;font-weight:950}}.label{{fill:#9db3b2;font-size:9px;font-weight:900;letter-spacing:1.1px}}.place{{fill:#789596;font-size:9px;font-weight:900;letter-spacing:.8px}}.boundary{{fill:#eef9f7;font:950 15px ui-monospace,Consolas,monospace;text-anchor:middle}}.detail{{fill:#9db3b2;font:850 9px ui-monospace,Consolas,monospace;text-anchor:middle}}.in{{stroke:#7e9dff;stroke-linecap:round}}.out{{stroke:#ffb454;stroke-linecap:round}}.row{{fill:#eef9f7;font-size:11px;font-weight:950}}.value{{fill:#eef9f7;font:900 10px ui-monospace,Consolas,monospace}}.grid{{stroke:#29464c;stroke-width:1}}.ref{{fill:#9db3b2;font:850 9px ui-monospace,Consolas,monospace;text-anchor:middle}}.metric{{fill:#eef9f7;font:950 27px ui-monospace,Consolas,monospace}}.metric-label{{fill:#9db3b2;font-size:8.5px;font-weight:900;letter-spacing:1px}}.note{{fill:#a9bfbe;font-size:9.5px}}.fine{{fill:#617d80;font-size:8px}}</style></defs>
<rect width="1400" height="920" fill="#06171c"/><text x="48" y="44" class="kicker">OSW / HEAT MOTION · M4 CONTROL VOLUME</text><text x="48" y="88" class="title">ONE GATE BECOMES FOUR</text><text x="48" y="118" class="sub">Native ORCA025 boundaries · signed outward flux · four sampled 2018 months</text>
<rect x="40" y="155" width="750" height="590" rx="16" class="panel"/><text x="68" y="190" class="head">WHERE DOES THE WESTERN INFLOW LEAVE?</text><text x="68" y="211" class="label">FOUR-SAMPLE MEAN · VOLUME SV / HEAT PW AT TREF 0°C</text>
<path d="M250 280L250 650L610 650L610 280Z" fill="#102a30" stroke="#62d7ce" stroke-width="2"/><text x="430" y="455" class="place">GRID-ALIGNED</text><text x="430" y="474" class="place">DRAKE CONTROL BOX</text><path d="M68 650Q145 580 250 590L250 650Z" fill="#263238"/><text x="100" y="683" class="place">ANTARCTIC PENINSULA</text><path d="M520 280Q575 325 610 390L610 280Z" fill="#263238"/><text x="555" y="260" class="place">SOUTH AMERICA</text>
<line x1="90" y1="465" x2="235" y2="465" class="in" stroke-width="18" marker-end="url(#arrow-in)"/><text x="160" y="430" class="boundary">IN {abs(west['volume_Sv']['mean']):.2f} SV</text><text x="160" y="447" class="detail">{abs(heat_at(west, 0)):.3f} PW · WEST</text>
<line x1="625" y1="465" x2="760" y2="465" class="out" stroke-width="11" marker-end="url(#arrow-out)"/><text x="690" y="430" class="boundary">OUT {east['volume_Sv']['mean']:.2f} SV</text><text x="690" y="447" class="detail">{heat_at(east, 0):.3f} PW · EAST</text>
<line x1="430" y1="265" x2="430" y2="225" class="out" stroke-width="13" marker-end="url(#arrow-out)"/><text x="530" y="229" class="boundary">OUT {north['volume_Sv']['mean']:.2f} SV</text><text x="530" y="246" class="detail">{heat_at(north, 0):.3f} PW · NORTH</text>
<line x1="430" y1="665" x2="430" y2="710" class="out" stroke-width="3" marker-end="url(#arrow-out)"/><text x="535" y="687" class="boundary">OUT {south['volume_Sv']['mean']:.2f} SV</text><text x="535" y="704" class="detail">{heat_at(south, 0):+.3f} PW · SOUTH</text>
<text x="250" y="725" class="detail">{abs(geometry['west_mean_longitude_deg']):.3f}°W</text><text x="610" y="725" class="detail">{abs(geometry['east_mean_longitude_deg']):.3f}°W</text>
<rect x="810" y="155" width="550" height="590" rx="16" class="panel"/><text x="842" y="190" class="head">WHAT REMAINS AFTER ALL FOUR SIDES?</text><text x="842" y="211" class="label">NET OUTWARD ADVECTIVE HEAT · TREF 0°C</text>{''.join(monthly)}
<line x1="842" y1="602" x2="1328" y2="602" class="grid"/><text x="842" y="630" class="head">REFERENCE AMBIGUITY NEARLY COLLAPSES</text><text x="842" y="648" class="label">FOUR-SAMPLE MEAN NET OUTWARD HEAT · ZOOMED PW AXIS</text><line x1="920" y1="676" x2="1270" y2="676" stroke="#48646a" stroke-width="4" stroke-linecap="round"/>{''.join(reference_marks)}<text x="920" y="704" class="ref">{ref_min:.5f}</text><text x="1270" y="704" class="ref">{ref_max:.5f}</text>
<g transform="translate(48 785)"><text class="metric">{summary['net_outward_volume_Sv']['mean']:.3f} SV</text><text y="22" class="metric-label">MEAN OUTWARD VOLUME IMBALANCE</text><text x="420" class="metric">{next(item['net_outward_PW']['mean'] for item in reference_summary if item['reference_temperature_degC'] == 0):.3f} PW</text><text x="420" y="22" class="metric-label">MEAN NET OUTWARD ADVECTIVE HEAT · TREF 0°C</text><text x="900" class="metric">{summary['across_reference_mean_heat_range_PW']:.6f} PW</text><text x="900" y="22" class="metric-label">MEAN HEAT RANGE ACROSS THREE REFERENCES</text></g>
<rect x="48" y="853" width="1304" height="50" rx="12" fill="#0d242a"/><text x="68" y="873" class="note">VOLUME NEARLY CLOSES; THE HEAT RESIDUAL DOES NOT YET MEAN ACCUMULATION. Matched storage tendency and non-advective boundary/surface terms are still absent.</text><text x="68" y="890" class="fine">ONE SMALL BOX · ONE REANALYSIS MEMBER · FOUR MONTHS · OFFLINE T-TO-FACE COLLOCATION · NOT A CLIMATOLOGY, COMPLETE MODEL BUDGET, CAUSAL ATTRIBUTION, OR ANTARCTIC HEAT DELIVERY</text><metadata>{html.escape(payload['boundary'])}</metadata></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-control-box-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m4-oras5-drake-control-box-2018.svg"))
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(payload), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

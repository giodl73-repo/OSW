"""Render the OSCAR-to-HYCOM Indonesian gate-support comparison."""

from __future__ import annotations

import argparse
import html
import json
import math
import pathlib


WIDTH, HEIGHT = 1400, 980
COLORS = {"MAK": "#62d7ce", "LIF": "#7e9dff", "LOM": "#f0cf70", "OMB": "#dc83ff", "TIM": "#ff9a68"}


def support_bar(x: float, y: float, width: float, wet: int, total: int, color: str) -> str:
    wet_width = width * wet / total
    return f'<rect x="{x}" y="{y}" width="{width}" height="13" rx="6.5" fill="#18343a"/><rect x="{x}" y="{y}" width="{wet_width:.1f}" height="13" rx="6.5" fill="{color}"/><text x="{x+width+14}" y="{y+11}" class="count">{wet}/{total}</text>'


def profile_path(profiles: list[dict], x: float, y: float, width: float, height: float) -> str:
    finite = [item for item in profiles if item["wet_points"] and item["mean_declared_positive_velocity_m_s"] is not None]
    if not finite:
        return ""
    max_depth = 2500
    max_speed = max(.15, max(abs(item["mean_declared_positive_velocity_m_s"]) for item in finite))
    points = []
    for item in finite:
        px = x + width * math.sqrt(min(item["depth_m"], max_depth) / max_depth)
        py = y + height/2 - item["mean_declared_positive_velocity_m_s"] / max_speed * height*.42
        points.append((px, py))
    return "M" + "L".join(f"{px:.1f},{py:.1f}" for px, py in points)


def row(gate: dict, index: int) -> str:
    y = 170 + index*132; color = COLORS[gate["code"]]
    oscar = gate["oscar"]; hycom = gate["hycom"]
    surface = hycom["surface_mean_declared_positive_velocity_m_s"]
    sign = "+" if surface >= 0 else ""
    path = profile_path(gate["profiles"], 1010, y+26, 315, 68)
    return f'''<g><rect x="45" y="{y}" width="1310" height="112" rx="13" class="row"/><rect x="45" y="{y}" width="5" height="112" rx="2.5" fill="{color}"/><text x="67" y="{y+31}" fill="{color}" class="code">{gate['code']}</text><text x="125" y="{y+29}" class="name">{html.escape(gate['name'].upper())}</text><text x="67" y="{y+53}" class="role">{html.escape(gate['role'].upper())}</text><text x="318" y="{y+23}" class="label">OSCAR 1/3° · SURFACE</text>{support_bar(318,y+38,210,oscar['surface_wet_points'],oscar['candidate_points'],color)}<text x="318" y="{y+77}" class="fine">71-FIELD MINIMUM WET SUPPORT</text><path d="M580 {y+51}h45" stroke="#698486" stroke-width="1.5" marker-end="url(#arrow)"/><text x="664" y="{y+23}" class="label">HYCOM 1/12° · SURFACE</text>{support_bar(664,y+38,210,hycom['surface_wet_points'],hycom['candidate_points'],color)}<text x="664" y="{y+77}" class="fine">{sign}{surface:.3f} M/S DECLARED-POSITIVE</text><text x="1010" y="{y+16}" class="label">ONE-DAY VERTICAL MOTION PROFILE</text><path d="M1010 {y+60}h315" class="zero"/><path d="{path}" fill="none" stroke="{color}" stroke-width="2.2"/><text x="1010" y="{y+99}" class="fine">0 M</text><text x="1325" y="{y+99}" text-anchor="end" class="fine">DEEPEST WET {hycom['deepest_wet_standard_level_m']:.0f} M</text></g>'''


def build(payload: dict) -> str:
    rows = "".join(row(gate, index) for index, gate in enumerate(payload["gates"]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" data-motion-level="m3-indonesian-grid-bakeoff"><title id="title">Indonesian gate grid bakeoff</title><desc id="desc">Five rows compare surface wet-point support on one-third-degree OSCAR and one-twelfth-degree HYCOM, followed by a one-day full-depth normal-velocity profile.</desc><metadata>{html.escape(payload['boundary'])}</metadata><defs><marker id="arrow" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#698486"/></marker><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.row{{fill:#0c252b;stroke:#3f5e62}}.code{{font:950 18px ui-monospace,Consolas,monospace}}.name{{fill:#eef9f7;font-size:16px;font-weight:950}}.role,.label{{fill:#89a2a2;font-size:8px;font-weight:900;letter-spacing:.9px}}.count{{fill:#eef9f7;font:850 11px ui-monospace,Consolas,monospace}}.fine{{fill:#698588;font-size:7.5px}}.zero{{stroke:#587276;stroke-width:.8;stroke-dasharray:3 3}}</style></defs><rect width="1400" height="980" fill="#06171c"/><text x="45" y="43" fill="#62d7ce" font-size="14" font-weight="900" letter-spacing="2.4">OSW / INDONESIAN HEAT ROUTES · M3 GRID BAKEOFF</text><text x="45" y="87" fill="#eef9f7" font-size="34" font-weight="950">THE FINER GRID OPENS ALL FIVE.</text><text x="45" y="116" fill="#9db3b2" font-size="12">More wet cells restore candidate sections. They do not validate the section or calculate transport.</text><rect x="1050" y="39" width="305" height="30" rx="15" fill="#102a30" stroke="#f0cf70"/><text x="1202.5" y="59" fill="#f0cf70" text-anchor="middle" font-size="9.5" font-weight="950" letter-spacing="1">ONE DAILY FIELD · NOT A MEAN</text>{rows}<rect x="45" y="846" width="1310" height="82" rx="13" fill="#0d242a"/><text x="67" y="873" fill="#eef9f7" font-size="13" font-weight="950">RESOLUTION PASSES. TRANSPORT HAS NOT STARTED.</text><text x="67" y="896" fill="#a8bfbd" font-size="9.5">HYCOM restores 7–38 surface wet cells at every candidate and exposes 900–2500 m of standard-level structure. Lifamatola's surface still runs opposite its declared deep route.</text><text x="67" y="916" fill="#a8bfbd" font-size="9.5">Next: section-angle sensitivity, connected wet-column checks, face geometry, thickness, and T/S-defined branch accounting before volume or heat.</text><text x="45" y="960" fill="#536f72" font-size="8">OSCAR: 71 FIVE-DAY FIELDS, DEC 2017–NOV 2018, NOMINAL 15 M · HYCOM GLBA0.08 EXPT 91.2: 2018-11-16, 33 STANDARD Z LEVELS · VELOCITY CURVES ARE NOT CROSS-PRODUCT SKILL SCORES</text></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m3-indonesian-grid-bakeoff-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m3-indonesian-grid-bakeoff-2018.svg"))
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(payload), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

"""Render the OSW-D7 multi-branch heatwave lineage family."""

from __future__ import annotations

import argparse
from datetime import date
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "research" / "osw-d7-noaa-crw-mhw-lineage-family-2026.json"
DEFAULT_OUTPUT = ROOT / "figures" / "osw-d7-noaa-crw-mhw-lineage-family-2026.svg"


def build(input_path=DEFAULT_INPUT, output_path=DEFAULT_OUTPUT):
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    nodes = payload["nodes"]
    edges = payload["edges"]
    summary = payload["summary"]
    if (summary["node_count"], summary["edge_count"]) != (28, 29):
        raise ValueError("view expects the governed D7 family topology")
    node_by_id = {node["node_id"]: node for node in nodes}
    start, end = date.fromisoformat("2026-07-21"), date.fromisoformat("2026-08-10")

    def x_for(date_value):
        return 86 + (date.fromisoformat(date_value) - start).days / (end - start).days * 1028

    off_y = {
        "2026-07-29-C02": 226,
        "2026-07-30-C02": 176,
        "2026-07-30-C03": 226,
        "2026-07-30-C04": 434,
        "2026-08-03-C02": 434,
        "2026-08-05-C02": 434,
        "2026-08-08-C02": 434,
    }
    positions = {}
    for node in nodes:
        positions[node["node_id"]] = (x_for(node["date"]), 330 if node["on_d3_primary_branch"] else off_y[node["node_id"]])

    edge_svg = []
    for edge in edges:
        x1, y1 = positions[edge["from"]]
        x2, y2 = positions[edge["to"]]
        primary = node_by_id[edge["from"]]["on_d3_primary_branch"] and node_by_id[edge["to"]]["on_d3_primary_branch"]
        color = "#267b87" if primary else "#c17a43"
        width = min(7, 1.2 + math.log10(edge["intersection_pixels"] + 1) * 1.5)
        control = (x2 - x1) * 0.48
        edge_svg.append(
            f'<path d="M{x1:.1f} {y1:.1f}C{x1+control:.1f} {y1:.1f} {x2-control:.1f} {y2:.1f} {x2:.1f} {y2:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{width:.2f}" opacity=".78"/>'
        )

    node_svg = []
    label_svg = []
    for node in nodes:
        x, y = positions[node["node_id"]]
        pixels = node["summary"]["pixel_count"]
        if node["on_d3_primary_branch"]:
            radius, fill, stroke = 7, "#173f51", "#f8fbfa"
        else:
            radius, fill, stroke = min(11, 4.5 + math.log10(pixels + 1) * 2.4), "#f3b65d", "#8b512e"
        node_svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        if not node["on_d3_primary_branch"]:
            anchor = "middle"
            label_y = y - radius - 8 if y < 330 else y + radius + 16
            label_svg.append(f'<text x="{x:.1f}" y="{label_y:.1f}" text-anchor="{anchor}" class="branchlabel">{pixels} px</text>')

    date_labels = [
        ("2026-07-21", "21 JUL"), ("2026-07-23", "23"), ("2026-07-28", "28"),
        ("2026-07-31", "31"), ("2026-08-03", "3 AUG"), ("2026-08-05", "5"),
        ("2026-08-08", "8"), ("2026-08-10", "10 AUG"),
    ]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800" role="img">
<title>OSW-D7 multi-branch marine heatwave lineage family</title>
<desc>The exact-overlap family contains 28 daily components and 29 edges from July 21 through August 10. A 21-node primary trunk has seven side components, five split nodes, and one merge node. Five side components terminate and two merge back.</desc>
<style>.eyebrow{{font:700 14px Inter,"Segoe UI",sans-serif;letter-spacing:2.2px;fill:#327487}}.title{{font:700 40px Georgia,serif;fill:#112f3b}}.lead{{font:400 18px Inter,"Segoe UI",sans-serif;fill:#49636c}}.section{{font:700 12px Inter,"Segoe UI",sans-serif;letter-spacing:1.4px;fill:#2e7182}}.legend{{font:600 12px Inter,"Segoe UI",sans-serif;fill:#425f69}}.date{{font:600 11px Inter,"Segoe UI",sans-serif;fill:#60777f}}.branchlabel{{font:700 11px Inter,"Segoe UI",sans-serif;fill:#84502f}}.metric{{font:700 31px Georgia,serif;fill:#153946}}.metriclabel{{font:700 11px Inter,"Segoe UI",sans-serif;letter-spacing:.8px;fill:#60767e}}.body{{font:400 13px Inter,"Segoe UI",sans-serif;fill:#506a73}}.small{{font:500 11px Inter,"Segoe UI",sans-serif;fill:#657b82}}</style>
<rect width="1200" height="800" fill="#f8fbfa"/><path d="M0 0H1200V12H0Z" fill="#1f7185"/>
<text x="72" y="61" class="eyebrow">OSW · DETECTED OBJECT 07 · LINEAGE FAMILY</text>
<text x="72" y="113" class="title">One lineage is a family, not a chain</text>
<text x="72" y="149" class="lead">Keep every exact-overlap branch: the primary path becomes one trunk through a split-and-merge genealogy.</text>
<g transform="translate(72 177)"><circle cx="8" cy="8" r="7" fill="#173f51"/><text x="24" y="12" class="legend">D3 primary trunk · 21 components</text><circle cx="254" cy="8" r="7" fill="#f3b65d" stroke="#8b512e"/><text x="270" y="12" class="legend">side component · label = pixels</text><path d="M505 8h34" stroke="#c17a43" stroke-width="3"/><text x="550" y="12" class="legend">exact-overlap branch · width = log(shared pixels)</text></g>
<rect x="72" y="207" width="1056" height="288" rx="8" fill="#edf4f3"/>
<path d="M86 330H1114" stroke="#cbdcdd" stroke-width="1"/>
{''.join(edge_svg)}
{''.join(node_svg)}
{''.join(label_svg)}
<text x="86" y="300" class="section">PRIMARY TRUNK</text>
<text x="1088" y="226" text-anchor="end" class="section">TIME →</text>
{''.join(f'<path d="M{x_for(value):.1f} 468v8" stroke="#809399"/><text x="{x_for(value):.1f}" y="490" text-anchor="middle" class="date">{label}</text>' for value, label in date_labels)}
<path d="M72 521H1128" stroke="#c6d6d9"/>
<g transform="translate(72 556)"><text class="metric">{summary['node_count']}</text><text x="54" y="-3" class="metriclabel">COMPONENTS</text><text x="224" class="metric">{summary['edge_count']}</text><text x="278" y="-3" class="metriclabel">OVERLAP EDGES</text><text x="484" class="metric">{summary['split_node_count']}</text><text x="514" y="-3" class="metriclabel">SPLIT NODES</text><text x="682" class="metric">{summary['merge_node_count']}</text><text x="712" y="-3" class="metriclabel">MERGE NODE</text><text x="878" class="metric">{summary['off_primary_node_count']}</text><text x="908" y="-3" class="metriclabel">SIDE COMPONENTS</text></g>
<g transform="translate(72 629)"><rect width="326" height="91" rx="7" fill="#e5f2f2"/><text x="18" y="28" class="section">THE TRUNK IS STILL USEFUL</text><text x="18" y="53" class="body">D3 remains one reproducible primary path.</text><text x="18" y="74" class="body">The graph records what that path omitted.</text></g>
<g transform="translate(437 629)"><rect width="326" height="91" rx="7" fill="#f7eadc"/><text x="18" y="28" class="section">SIDE-BRANCH FATES</text><text x="18" y="53" class="body">{summary['off_primary_terminal_node_count']} terminate · {summary['off_primary_merge_back_node_count']} merge back into the trunk.</text><text x="18" y="74" class="body">Largest side component: {summary['largest_off_primary_component_pixels']} pixels.</text></g>
<g transform="translate(802 629)"><rect width="326" height="91" rx="7" fill="#edf2f2"/><text x="18" y="28" class="section">IDENTITY CHANGES FORM</text><text x="18" y="53" class="body">A family graph need not crown one heir.</text><text x="18" y="74" class="body">It preserves branching as evidence.</text></g>
<text x="72" y="755" class="small">Source: NOAA CRW Marine Heatwave Watch v1.0.1 daily category · native 0.05° grid · 21 Jul–10 Aug 2026.</text>
<text x="72" y="777" class="small">Four-neighbor · adjacent-day exact overlap · no size pruning · threshold-state genealogy, not material water or mechanism continuity.</text>
</svg>'''
    Path(output_path).write_text(svg, encoding="utf-8", newline="\n")
    return svg


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build(args.input, args.output)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

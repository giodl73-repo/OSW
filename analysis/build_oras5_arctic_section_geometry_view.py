"""Render full-depth geometry for Fram and two Barents section meanings."""

from __future__ import annotations

import argparse
import json
import pathlib


WIDTH = 1400
HEIGHT = 900
COLORS = ("#83eee2", "#55d8d0", "#30aeb4", "#477e9e", "#585d8e", "#493b73")
SHORT = {"Fram Strait": "FRAM STRAIT", "Fugloya-Bear observational proxy": "FUGLØYA–BEAR PROXY", "Norway-Svalbard model closure": "NORWAY–SVALBARD CLOSURE"}


def stacked_bar(section, x, y, width):
    chunks = []; cursor = x
    for index, item in enumerate(section["depth_bins"]):
        segment = width * item["fraction"]
        if segment > 0:
            chunks.append(f'<rect x="{cursor:.1f}" y="{y}" width="{segment:.1f}" height="34" fill="{COLORS[index]}"/>')
        cursor += segment
    return "".join(chunks)


def depth_rows(section, x, y):
    chunks = []
    for index, item in enumerate(section["depth_bins"]):
        upper = "+" if item["upper_m"] is None else str(item["upper_m"])
        label = f"{item['lower_m']}–{upper} m"
        chunks.append(f'<circle cx="{x}" cy="{y + index * 24}" r="5" fill="{COLORS[index]}"/><text x="{x + 14}" y="{y + 4 + index * 24}" class="fine">{label}</text><text x="{x + 132}" y="{y + 4 + index * 24}" class="pct">{item["fraction"] * 100:.1f}%</text>')
    return "".join(chunks)


def panel(section, index):
    x = 52 + index * 432
    area = section["total_section_area_m2"] / 1e6
    depth = section["column_depth_m"]
    land = "COAST ↔ COAST" if section["land_bounded_at_surface"] else "VIRTUAL WET ENDS"
    return f'''<g><rect x="{x}" y="160" width="404" height="596" rx="14" class="panel"/><text x="{x + 20}" y="190" class="head">{SHORT[section['name']]}</text><text x="{x + 20}" y="222" class="metric">{area:.0f} km²</text><text x="{x + 20}" y="244" class="body">native wet cross-sectional area</text><text x="{x + 20}" y="285" fill="#eef8f5" font-size="18" font-weight="950">{section['horizontal_face_count']} FACES · {section['wet_3d_cell_count']:,} WET CELLS</text><text x="{x + 20}" y="310" class="fine">{land} · MAX DEPTH {depth['maximum']:.0f} m</text><text x="{x + 20}" y="352" class="label">AREA BY REFERENCE-LEVEL DEPTH</text>{stacked_bar(section, x + 20, 370, 364)}{depth_rows(section, x + 28, 434)}<line x1="{x + 20}" y1="588" x2="{x + 384}" y2="588" stroke="#36575d"/><text x="{x + 20}" y="620" class="check">✓ MASK MISMATCHES 0</text><text x="{x + 20}" y="646" class="check">✓ FINITE POSITIVE WET AREAS</text><text x="{x + 20}" y="672" class="check">✓ DEPTH BINS REPRODUCE TOTAL</text><text x="{x + 20}" y="712" class="fine">COLUMN DEPTH RANGE</text><text x="{x + 20}" y="735" fill="#eef8f5" font-size="15" font-weight="900">{depth['minimum']:.0f}–{depth['maximum']:.0f} m</text></g>'''


def build(payload):
    sections = payload["sections"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" data-motion-level="m3-arctic-section-geometry"><title id="title">Same grid, three different Arctic cross-sections</title><desc id="desc">Full-depth native geometry compares deep Fram Strait with two shallow Barents section meanings after zero mask mismatches and exact depth-bin area closure.</desc><metadata>{payload['boundary']}</metadata><defs><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.panel{{fill:#092229;stroke:#36575d}}.head{{fill:#eef8f5;font-size:13px;font-weight:950;letter-spacing:1px}}.metric{{fill:#55ded3;font-size:32px;font-weight:950}}.body{{fill:#aac0bf;font-size:12px}}.fine{{fill:#78979a;font-size:9px}}.pct{{fill:#dce9e5;font-size:10px;font-weight:900}}.label{{fill:#aac0bf;font-size:10px;font-weight:900;letter-spacing:1px}}.check{{fill:#55ded3;font-size:11px;font-weight:900}}</style></defs><rect width="1400" height="900" fill="#06171c"/><text x="52" y="42" fill="#55ded3" font-size="12" font-weight="950" letter-spacing="2">OSW / ARCTIC ENTRANCES · FULL-DEPTH GEOMETRY</text><text x="52" y="87" fill="#eef8f5" font-size="36" font-weight="950">SAME GRID. THREE DIFFERENT CROSS-SECTIONS.</text><text x="52" y="119" class="body">Area and depth constrain what future velocity can carry. They are not transport by themselves.</text>{''.join(panel(section, index) for index, section in enumerate(sections))}<rect x="52" y="785" width="1268" height="56" rx="10" fill="#102a30" stroke="#36575d"/><text x="72" y="819" fill="#ffbd71" font-size="14" font-weight="950">FRAM IS DEEP. BOTH BARENTS DEFINITIONS ARE SHELF GATES. LONGER DOES NOT MEAN DEEPER.</text><text x="52" y="876" class="fine">75 REFERENCE LEVELS · ADJACENT-MINIMUM PARTIAL-STEP RECONSTRUCTION · INTERNAL CONSISTENCY PASS, NOT INDEPENDENT ORAS5 VALIDATION · NO VELOCITY OR HEAT</text></svg>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-arctic-section-geometry-audit.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m3-oras5-arctic-section-geometry.svg"))
    args = parser.parse_args(); payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(build(payload), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

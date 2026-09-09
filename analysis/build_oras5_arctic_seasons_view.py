"""Build the four-snapshot Arctic gateway transport comparison plate."""

from __future__ import annotations

import argparse
import html
import json
import pathlib


COLORS = {"fram": "#26bad8", "barents-proxy": "#f2aa4c", "barents-closure": "#df7058"}
LABELS = {"201802": "FEB", "201805": "MAY", "201808": "AUG", "201811": "NOV"}
TITLES = {"fram": "FRAM STRAIT", "barents-proxy": "FUGLØYA–BEAR PROXY", "barents-closure": "NORWAY–SVALBARD CLOSURE"}


def text(x, y, value, size=18, fill="#dcecf2", weight=400, anchor="start", opacity=1):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}" opacity="{opacity}">{html.escape(str(value))}</text>'


def line(x1, y1, x2, y2, stroke="#33505a", width=1, opacity=1):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{width}" opacity="{opacity}"/>'


def build(payload):
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="940" viewBox="0 0 1500 940" role="img" aria-labelledby="title desc">',
        '<title id="title">Four 2018 ORAS5 Arctic gateway transport snapshots</title>',
        '<desc id="desc">Fram exports net water while carrying positive reference-relative heat in all four snapshots. Both Barents sections import water and heat.</desc>',
        '<rect width="1500" height="940" fill="#07171d"/>',
        '<style>text{font-family:Inter,"Segoe UI",Arial,sans-serif}</style>',
        text(70, 70, "WATER LEAVES THROUGH FRAM. HEAT STILL ENTERS.", 32, "#f4fafb", 750),
        text(70, 108, "ORAS5 · FOUR 2018 SNAPSHOTS · SAME NATIVE MESH · SAME THREE SECTION CONTRACTS", 15, "#8fb0bb", 600),
        text(1430, 70, "M3", 20, "#678690", 700, "end"),
    ]
    panel_x = {"fram": 70, "barents-proxy": 550, "barents-closure": 1030}
    for slug, section in payload["sections"].items():
        x = panel_x[slug]; color = COLORS[slug]; summary = section["sample_summary"]
        parts += [
            f'<rect x="{x}" y="145" width="400" height="660" rx="12" fill="#0b222a" stroke="#274650"/>',
            f'<rect x="{x}" y="145" width="400" height="7" rx="3" fill="{color}"/>',
            text(x + 26, 198, TITLES[slug], 21, "#f4fafb", 700),
            text(x + 26, 232, f'4-snapshot net mean {summary["net_volume_Sv"]["sample_mean"]:+.2f} Sv', 14, color, 650),
            text(x + 374, 232, f'AW class {summary["atlantic_water_net_Sv"]["sample_mean"]:+.2f} Sv', 13, "#9cb6bf", 500, "end"),
            text(x + 26, 276, "SIGNED VOLUME BRANCHES", 13, "#789aa5", 700),
            text(x + 374, 276, "◆ NET", 12, "#9cb6bf", 600, "end"),
        ]
        axis = x + 205; volume_scale = 17
        for row_index, row in enumerate(section["months"]):
            y = 320 + row_index * 62
            neg = row["negative_volume_Sv"]; pos = row["positive_volume_Sv"]; net = row["net_volume_Sv"]
            parts += [
                text(x + 26, y + 5, LABELS[row["month"]], 13, "#9cb6bf", 650),
                line(x + 74, y, x + 374, y, "#284751"),
                line(axis, y - 17, axis, y + 17, "#5f7d87", 1),
                line(axis + neg * volume_scale, y - 5, axis, y - 5, color, 10, .34),
                line(axis, y + 6, axis + pos * volume_scale, y + 6, color, 10, .92),
                f'<path d="M {axis+net*volume_scale:.2f} {y-7} l 7 7 l -7 7 l -7 -7 z" fill="#f4fafb"/>',
                text(x + 374, y + 5, f'{net:+.2f}', 14, "#dcecf2", 650, "end"),
            ]
        parts += [
            line(x + 26, 563, x + 374, 563, "#274650"),
            text(x + 26, 602, "ADVECTIVE HEAT · θREF 0°C", 13, "#789aa5", 700),
        ]
        for row_index, row in enumerate(section["months"]):
            y = 640 + row_index * 36
            tw = row["heat_transport_PW"]["0.0"] * 1000
            parts += [
                text(x + 26, y + 5, LABELS[row["month"]], 12, "#9cb6bf", 600),
                f'<circle cx="{x+100}" cy="{y}" r="4" fill="{color}"/>',
                line(x + 100, y, x + 100 + tw * 1.8, y, color, 7, .82),
                text(x + 374, y + 5, f'{tw:+.1f} TW', 14, "#dcecf2", 650, "end"),
            ]
        parts += [
            text(x + 26, 789, "light/dark bars = opposing volume branches", 11, "#668690", 400),
        ]
    parts += [
        text(70, 850, "THE FRAM SIGN SPLIT IS THE RESULT", 14, "#26bad8", 700),
        text(70, 882, "Net volume is southward in every snapshot; warm northward flow still makes the 0°C-reference heat signal positive.", 21, "#e6f1f4", 650),
        text(70, 913, "Four snapshots are not an annual mean. Open-gate heat transport is reference-relative—not convergence, storage, or heat delivered inside the Arctic.", 14, "#8fb0bb", 400),
        text(1430, 913, "OSW · OCEAN STATES OF THE WORLD", 12, "#55747e", 700, "end"),
        '</svg>',
    ]
    return "\n".join(parts) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-arctic-seasons-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m3-oras5-arctic-seasons-2018.svg"))
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(payload), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

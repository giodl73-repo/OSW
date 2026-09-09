"""Build the one-month three-gateway Arctic transport pilot plate."""

from __future__ import annotations

import argparse
import html
import json
import pathlib


COLORS = {"fram": "#25b9d7", "barents-proxy": "#f0a54b", "barents-closure": "#db6e56"}


def text(x, y, value, size=20, fill="#dcecf2", weight=400, anchor="start", opacity=1):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}" opacity="{opacity}">{html.escape(str(value))}</text>'


def line(x1, y1, x2, y2, stroke="#33505a", width=1, opacity=1):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{width}" opacity="{opacity}"/>'


def build(payload):
    width, height = 1500, 930
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">February 2018 ORAS5 Arctic gateway transport pilot</title>',
        '<desc id="desc">Three panels compare signed volume branches, Atlantic Water comparison classes, and reference-relative heat transport for Fram Strait and two noninterchangeable Barents sections.</desc>',
        '<rect width="1500" height="930" fill="#07171d"/>',
        '<style>text{font-family:Inter,"Segoe UI",Arial,sans-serif}</style>',
        text(70, 72, "THE ARCTIC HAS TWO ATLANTIC DOORS—AND EACH DOOR HAS COUNTERFLOW.", 30, "#f4fafb", 700),
        text(70, 110, "ORAS5 · FEBRUARY 2018 · NATIVE 75-LEVEL T/S/U/V · ONE-MONTH PILOT", 16, "#8fb0bb", 600),
        text(1430, 72, "M3", 20, "#678690", 700, "end"),
    ]
    panel_x = {"fram": 70, "barents-proxy": 550, "barents-closure": 1030}
    short_name = {"fram": "FRAM STRAIT", "barents-proxy": "FUGLØYA–BEAR PROXY", "barents-closure": "NORWAY–SVALBARD CLOSURE"}
    for slug, section in payload["sections"].items():
        x = panel_x[slug]; color = COLORS[slug]
        vol = section["volume_transport_Sv"]
        aw = section["atlantic_water_comparison_class"]
        parts += [
            f'<rect x="{x}" y="150" width="400" height="620" rx="12" fill="#0b222a" stroke="#274650"/>',
            f'<rect x="{x}" y="150" width="400" height="7" rx="3" fill="{color}"/>',
            text(x + 26, 204, short_name[slug], 21, "#f4fafb", 700),
            text(x + 374, 178, f'{section["face_count"]} FACES', 12, "#789aa5", 600, "end"),
            text(x + 26, 245, "FULL SIGNED SECTION", 13, "#789aa5", 700),
        ]
        axis = x + 200; scale = 24
        parts += [line(x + 28, 304, x + 372, 304, "#31515b"), line(axis, 275, axis, 335, "#698994", 1)]
        pos_w = vol["positive_Sv"] * scale; neg_w = abs(vol["negative_Sv"]) * scale
        parts += [
            f'<rect x="{axis}" y="283" width="{pos_w:.2f}" height="20" fill="{color}" opacity=".95"/>',
            f'<rect x="{axis-neg_w:.2f}" y="306" width="{neg_w:.2f}" height="20" fill="{color}" opacity=".35"/>',
            text(axis + pos_w + 7, 299, f'+{vol["positive_Sv"]:.2f}', 15, "#dcecf2", 600),
            text(axis - neg_w - 7, 322, f'{vol["negative_Sv"]:.2f}', 15, "#9cb6bf", 600, "end"),
            text(x + 26, 365, "NET", 13, "#789aa5", 700),
            text(x + 374, 365, f'{vol["net_Sv"]:+.2f} Sv', 26, color, 700, "end"),
            text(x + 26, 411, "ATLANTIC-WATER COMPARISON CLASS", 13, "#789aa5", 700),
            text(x + 26, 441, f'T > {aw["threshold"]["temperature_gt_degC"]:.0f}°C  ·  S > {aw["threshold"]["salinity_gt_PSU"]:.1f}', 15, "#bfd1d7", 500),
            text(x + 26, 483, f'{aw["net_Sv"]:+.2f} Sv net', 25, color, 700),
            text(x + 374, 483, f'{aw["positive_fraction_of_full_positive"]*100:.0f}% of + branch', 14, "#9cb6bf", 500, "end"),
            line(x + 26, 511, x + 374, 511, "#274650"),
            text(x + 26, 548, "REFERENCE-RELATIVE HEAT", 13, "#789aa5", 700),
        ]
        heat_cases = [section["heat_transport_PW"][key] for key in ("-1.9", "0.0", "2.0")]
        for row, case in enumerate(heat_cases):
            y = 586 + row * 45
            tw = case["net_PW"] * 1000
            parts += [
                text(x + 26, y, f'θref {case["reference_temperature_degC"]:+.1f}°C', 14, "#9cb6bf", 500),
                f'<circle cx="{x+220}" cy="{y-5}" r="5" fill="{color}"/>',
                line(x + 220, y - 5, x + 220 + tw * .75, y - 5, color, 6, .8),
                text(x + 374, y, f'{tw:+.1f} TW', 16, "#dcecf2", 600, "end"),
            ]
        parts += [
            text(x + 26, 737, "positive = into Arctic / Barents", 12, "#698994", 400),
            text(x + 374, 737, "negative = return/export", 12, "#698994", 400, "end"),
        ]
    diff = payload["barents_definition_difference"]
    parts += [
        text(70, 822, "SECTION MEANING MATTERS", 14, "#f0a54b", 700),
        text(70, 854, f'The broader Barents closure carries {diff["closure_minus_proxy_net_Sv"]:+.2f} Sv ({diff["percent_of_proxy_net"]:.1f}%) more net flow than the observational proxy.', 21, "#e6f1f4", 600),
        text(70, 884, "That is an endpoint/domain difference—not an uncertainty interval. Heat is advective and reference-relative; it is not gateway convergence or an Arctic heat budget.", 14, "#8fb0bb", 400),
        text(1430, 914, "OSW · OCEAN STATES OF THE WORLD", 12, "#55747e", 700, "end"),
        "</svg>",
    ]
    return "\n".join(parts) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-arctic-transport-pilot-201802.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m3-oras5-arctic-transport-pilot-201802.svg"))
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(payload), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

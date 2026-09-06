"""Build matched latitude-depth maps of native-cell Drake volume and heat contributions."""

from __future__ import annotations

import argparse
import html
import json
import math
import pathlib


BACKGROUND = (15, 35, 40)
POSITIVE = (255, 180, 84)
NEGATIVE = (126, 157, 255)


def color(value: float, maximum: float, softening: float) -> str:
    strength = math.asinh(abs(value) / softening) / math.asinh(maximum / softening)
    target = POSITIVE if value >= 0 else NEGATIVE
    rgb = tuple(round(a + (b - a) * strength) for a, b in zip(BACKGROUND, target))
    return "#" + "".join(f"{channel:02x}" for channel in rgb)


def build(payload: dict) -> str:
    levels, segments = payload["shape"]
    plot_x0, plot_x1 = 100, 1320
    cell_width = (plot_x1 - plot_x0) / segments
    maximum_depth = payload["maximum_nominal_model_depth_m"]
    panels = (
        ("mean_cell_volume_transport_Sv", "VOLUME CONTRIBUTION", "SV PER NATIVE FACE CELL", 220, 465, .03),
        ("mean_cell_heat_transport_PW_at_0C", "0°C-REFERENCE HEAT CONTRIBUTION", "PW PER NATIVE FACE CELL", 545, 790, .0003),
    )
    panel_output = []
    bottom_by_segment = [0.0] * segments
    for level, depth in enumerate(payload["layer_depths"]):
        for segment in range(segments):
            index = level * segments + segment
            if payload["wet_fraction"][index]:
                bottom_by_segment[segment] = max(bottom_by_segment[segment], depth["top_m"] + float(payload["cell_thickness_m"][index]))
    for key, title, unit, y0, y1, softening in panels:
        values = payload[key]
        maximum = max(abs(value) for value in values if value is not None)
        depth_y = lambda depth: y0 + (max(0, depth) / maximum_depth) ** .55 * (y1 - y0)
        cells = []
        for level, depth in enumerate(payload["layer_depths"]):
            top = depth["top_m"]
            for segment in range(segments):
                index = level * segments + segment
                if values[index] is None:
                    continue
                bottom = top + float(payload["cell_thickness_m"][index])
                x = plot_x0 + segment * cell_width
                top_y, bottom_y = depth_y(top), depth_y(bottom)
                cells.append(f'<rect data-transport-cell="{key}-{level}-{segment}" x="{x:.2f}" y="{top_y:.2f}" width="{cell_width + .18:.2f}" height="{max(.3, bottom_y - top_y + .14):.2f}" fill="{color(values[index], maximum, softening)}"/>')
        seabed = [f"{plot_x0:.2f},{y1:.2f}"] + [
            f"{plot_x0 + (segment + .5) * cell_width:.2f},{depth_y(bottom):.2f}" for segment, bottom in enumerate(bottom_by_segment)
        ] + [f"{plot_x1:.2f},{y1:.2f}"]
        grids = []
        for depth in (0, 700, 1500, 3000, 6000):
            y = depth_y(depth)
            grids.append(f'<line x1="{plot_x0}" y1="{y:.2f}" x2="{plot_x1}" y2="{y:.2f}" class="grid"/><text x="{plot_x0 - 12}" y="{y + 4:.2f}" class="axis" text-anchor="end">{depth} m</text>')
        panel_output.append(f'<text x="{plot_x0}" y="{y0 - 38}" class="head">{title}</text><text x="{plot_x0}" y="{y0 - 20}" class="label">{unit} · SIGNED · ASINH COLOR SCALE</text>{"".join(cells)}<path d="M{" L".join(seabed)} Z" fill="#19262a" stroke="#789596" stroke-width=".8"/>{"".join(grids)}')
    latitudes = payload["latitude_deg"]
    lat_labels = []
    for latitude in (-66, -64, -62, -60, -58, -56):
        nearest = min(range(segments), key=lambda i: abs(latitudes[i] - latitude))
        x = plot_x0 + (nearest + .5) * cell_width
        lat_labels.append(f'<text x="{x:.2f}" y="818" class="lat">{abs(latitude)}°S</text>')
    volume = [abs(value) for value in payload["mean_cell_volume_transport_Sv"] if value is not None]
    heat = [abs(value) for value in payload["mean_cell_heat_transport_PW_at_0C"] if value is not None]
    count = len(volume)
    top_count = round(.1 * count)
    volume_share = sum(sorted(volume, reverse=True)[:top_count]) / sum(volume) * 100
    heat_share = sum(sorted(heat, reverse=True)[:top_count]) / sum(heat) * 100
    audit = payload["transport_sum_audit"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="950" viewBox="0 0 1400 950" role="img" aria-labelledby="title desc" data-motion-level="m3-drake-transport-field">
<title id="title">Native-cell Drake volume and heat contribution maps</title><desc id="desc">Matched latitude-depth sections show signed four-sample mean volume and zero-degree-reference heat contributions for every wet native face cell, using nonlinear depth and asinh color scales.</desc>
<defs><style>text{{font-family:Inter,ui-sans-serif,system-ui,sans-serif}}.kicker{{fill:#62d7ce;font-size:14px;font-weight:900;letter-spacing:2.4px}}.title{{fill:#eef9f7;font-size:34px;font-weight:950}}.sub{{fill:#9db3b2;font-size:12px}}.head{{fill:#eef9f7;font-size:15px;font-weight:950}}.label{{fill:#9db3b2;font-size:9px;font-weight:900;letter-spacing:1.1px}}.grid{{stroke:#d7e7e5;stroke-width:.55;stroke-opacity:.16}}.axis{{fill:#789596;font:800 8px ui-monospace,Consolas,monospace}}.lat{{fill:#9db3b2;font:850 9px ui-monospace,Consolas,monospace;text-anchor:middle}}.metric{{fill:#eef9f7;font:950 23px ui-monospace,Consolas,monospace}}.metric-label{{fill:#9db3b2;font-size:8px;font-weight:900;letter-spacing:1px}}.note{{fill:#a9bfbe;font-size:9.5px}}.fine{{fill:#617d80;font-size:8px}}</style></defs>
<rect width="1400" height="950" fill="#06171c"/><text x="48" y="44" class="kicker">OSW / HEAT MOTION · M3 NATIVE-CELL ACCOUNTING</text><text x="48" y="88" class="title">WHERE DOES THE TRANSPORT CROSS?</text><text x="48" y="118" class="sub">67.125°W · four-sample means · cell contributions sum exactly to the gate result</text>
<rect x="40" y="150" width="1320" height="680" rx="16" fill="#0b2127" stroke="#29464c"/><text x="{plot_x0}" y="210" class="label">ANTARCTIC PENINSULA / SOUTH</text><text x="{plot_x1}" y="210" class="label" text-anchor="end">SOUTH AMERICA / NORTH</text>{''.join(panel_output)}{''.join(lat_labels)}
<g transform="translate(48 850)"><text class="metric">{audit['volume_Sv']:.3f} SV</text><text y="19" class="metric-label">CELL SUM · VOLUME</text><text x="285" class="metric">{audit['heat_transport_PW_at_0C']:.3f} PW</text><text x="285" y="19" class="metric-label">CELL SUM · HEAT AT TREF 0°C</text><text x="600" class="metric">{volume_share:.1f}% / {heat_share:.1f}%</text><text x="600" y="19" class="metric-label">TOP 10% OF CELLS · SHARE OF ABSOLUTE VOLUME / HEAT</text><rect x="1080" y="-12" width="95" height="13" fill="#7e9dff"/><rect x="1175" y="-12" width="95" height="13" fill="#ffb454"/><text x="1080" y="19" class="metric-label">NEGATIVE</text><text x="1270" y="19" class="metric-label" text-anchor="end">POSITIVE</text></g>
<rect x="48" y="902" width="1304" height="34" rx="12" fill="#0d242a"/><text x="68" y="919" class="note">Per-cell intensity is resolution-dependent; the accounting meaning comes from signed sums, not from treating bright cells as permanent geographic objects.</text><text x="68" y="932" class="fine">NONLINEAR DEPTH + ASINH COLOR SCALES · FOUR MONTHS, NOT CLIMATOLOGY · HEAT SIGN DEPENDS ON TREF 0°C · NOT CONVERGENCE OR ANTARCTIC DELIVERY</text><metadata>{html.escape(payload['boundary'])}</metadata></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-section-field-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m3-oras5-drake-transport-field-2018.svg"))
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(payload), encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

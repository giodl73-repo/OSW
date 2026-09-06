"""Render the D11 RTOFS surface horizontal-advection screen."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "atlas" / "data" / "rtofs-mhw-bridge-north-atlantic-20260807-20260812.json"
ANALYSIS = ROOT / "research" / "osw-d11-rtofs-mhw-horizontal-advection-2026.json"
OUTPUT = ROOT / "figures" / "osw-d11-rtofs-mhw-horizontal-advection-2026.svg"


def decoded_map(payload: dict, key: str) -> np.ndarray:
    return np.asarray([[np.nan if value is None else value / 1000 for value in row] for row in payload["bridge_interval_maps"][key]], dtype=float)


def build(source_path: Path = SOURCE, analysis_path: Path = ANALYSIS, output: Path = OUTPUT) -> None:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    result = json.loads(analysis_path.read_text(encoding="utf-8"))
    latitude = np.asarray(source["grid"]["latitude_degrees_north_e6"], dtype=float) / 1_000_000
    longitude = np.asarray(source["grid"]["longitude_degrees_east_e6"], dtype=float) / 1_000_000
    keys = ["surface_temperature_tendency_c_per_day_milli", "endpoint_mean_horizontal_advection_c_per_day_milli", "unresolved_remainder_c_per_day_milli"]
    titles = ["A  MODELED SST TENDENCY", "B  HORIZONTAL ADVECTION", "C  UNRESOLVED REMAINDER"]
    maps = [decoded_map(result, key) for key in keys]
    intervals = result["intervals"]
    bridge = result["bridge_evaluation"]
    mld = bridge["mixed_layer_thickness"]

    mpl.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none", "svg.hashsalt": "osw-d11-rtofs-advection-v1", "figure.facecolor": "#06171c", "axes.facecolor": "#0c252b", "text.color": "#eef9f7", "axes.labelcolor": "#9db3b2", "xtick.color": "#78979a", "ytick.color": "#78979a"})
    fig = plt.figure(figsize=(14, 9.8), dpi=100)
    grid = fig.add_gridspec(2, 6, left=.055, right=.97, top=.72, bottom=.12, height_ratios=[1.05, .8], hspace=.38, wspace=.32)
    cmap = mpl.colors.LinearSegmentedColormap.from_list("osw_balance", ["#28759a", "#8fd0ca", "#102a30", "#f1cf70", "#e6654a"])
    norm = mpl.colors.TwoSlopeNorm(vmin=-2, vcenter=0, vmax=2)
    image = None
    for index, (field, title) in enumerate(zip(maps, titles)):
        axis = fig.add_subplot(grid[0, index * 2 : index * 2 + 2])
        image = axis.pcolormesh(longitude, latitude, field, shading="nearest", cmap=cmap, norm=norm)
        axis.contour(longitude, latitude, field, levels=[0], colors="#eef9f7", linewidths=.75, alpha=.8)
        axis.scatter([-49.875], [42.125], marker="+", s=90, linewidths=1.8, color="#ffffff", zorder=5)
        axis.set_title(title, loc="left", fontsize=10, fontweight="bold", pad=7)
        axis.set_xlim(-52, -47); axis.set_ylim(39.5, 43.5)
        axis.set_xticks([-51, -49, -47]); axis.set_yticks([40, 41.5, 43]); axis.tick_params(labelsize=7)
        for spine in axis.spines.values(): spine.set_edgecolor("#45676b")
    color_axis = fig.add_axes([.69, .775, .28, .018])
    fig.colorbar(image, cax=color_axis, orientation="horizontal")
    color_axis.set_title("°C per day · blue cooling / orange warming", fontsize=8, color="#9db3b2", pad=5)
    color_axis.tick_params(labelsize=7)

    bar = fig.add_subplot(grid[1, :4])
    x = np.arange(len(intervals)); width = .25
    observed = [item["surface_temperature_tendency"]["latitude_weighted_mean_c_per_day"] for item in intervals]
    advective = [item["endpoint_mean_horizontal_advection"]["latitude_weighted_mean_c_per_day"] for item in intervals]
    remainder = [item["unresolved_remainder"]["latitude_weighted_mean_c_per_day"] for item in intervals]
    bar.axhline(0, color="#78979a", linewidth=.8)
    bar.bar(x - width, observed, width, color="#f1cf70", label="modeled SST tendency")
    bar.bar(x, advective, width, color="#62d7ce", label="horizontal advection")
    bar.bar(x + width, remainder, width, color="#d7a5ef", label="unresolved remainder")
    bar.set_xticks(x, [item["start"][5:] + "→" + item["end"][8:] for item in intervals], fontsize=8)
    bar.set_ylabel("fixed-box mean · °C/day", fontsize=8)
    bar.grid(axis="y", color="#24444b", linewidth=.7)
    bar.legend(frameon=False, fontsize=8, ncol=3, loc="lower left", labelcolor="#dcecea")
    for spine in bar.spines.values(): spine.set_edgecolor("#45676b")

    callout = fig.add_subplot(grid[1, 4:]); callout.axis("off")
    callout.add_patch(mpl.patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=.02,rounding_size=.04", facecolor="#102a30", edgecolor="#f1cf70", linewidth=1.2))
    callout.text(.07, .84, "AUG 11 → 12 · BOX MEAN", color="#f1cf70", fontsize=9, fontweight="bold")
    callout.text(.07, .65, f"warming       +{bridge['box_mean_temperature_tendency_c_per_day']:.3f}°C/day", fontsize=11, fontweight="bold")
    callout.text(.07, .49, f"advection     +{bridge['box_mean_horizontal_advection_c_per_day']:.3f}°C/day", color="#62d7ce", fontsize=11, fontweight="bold")
    callout.text(.07, .33, f"unresolved    +{bridge['box_mean_unresolved_remainder_c_per_day']:.3f}°C/day", color="#d7a5ef", fontsize=11, fontweight="bold")
    callout.text(.07, .17, f"mixed layer   {mld['box_mean_start_m']:.1f} → {mld['box_mean_end_m']:.1f} m", color="#aac1c0", fontsize=9.5, fontweight="bold")
    callout.text(.07, .06, "Shoaling is context—not a diagnosed term.", color="#78979a", fontsize=8)

    fig.text(.055, .945, "OSW / MARINE HEATWAVE OBJECT · D11 OCEAN-MOTION SCREEN", color="#62d7ce", fontsize=12, fontweight="bold")
    fig.text(.055, .895, "THE MODEL WARMS. HORIZONTAL ADVECTION IS NOT THE MAIN TERM.", fontsize=24, fontweight="bold")
    fig.text(.055, .852, "Across the bridge day, the signed horizontal-advection term is 13% of box-mean warming and opposes warming at the anchor.", color="#aac1c0", fontsize=11)
    fig.text(.055, .795, "AUGUST 11 → 12 · + anchor · white contour = zero tendency · identical ±2°C/day scale", color="#78979a", fontsize=8)
    fig.text(.055, .058, "NOAA GLOBAL RTOFS / HYCOM 93.1 · 1/12° CURVILINEAR GRID · PLATE CARRÉE DISPLAY · 00 UTC N024 NOWCASTS · SURFACE T, U, V + DIAGNOSTIC MLD", color="#68878a", fontsize=7.4, fontweight="bold")
    fig.text(.055, .032, "OFFLINE EULERIAN SCREEN · NOT MODEL-NATIVE TRACER BUDGET OR CAUSAL ATTRIBUTION · REMAINDER INCLUDES SURFACE FLUX, VERTICAL PROCESSES, MIXING, ASSIMILATION + ERROR", color="#68878a", fontsize=7.4, fontweight="bold")
    fig.text(.97, .032, "OSW-D11", ha="right", color="#62d7ce", fontsize=8, fontweight="bold")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, format="svg", facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--analysis", type=Path, default=ANALYSIS)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(); build(args.source, args.analysis, args.output); print(f"wrote {args.output}")


if __name__ == "__main__": main()

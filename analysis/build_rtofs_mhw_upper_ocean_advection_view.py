"""Render D14 depth-integrated horizontal advection and partial budget."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "atlas" / "data" / "rtofs-mhw-upper-ocean-north-atlantic-20260807-20260812.json"
D13 = ROOT / "research" / "osw-d13-rtofs-mhw-upper-ocean-storage-2026.json"
ANALYSIS = ROOT / "research" / "osw-d14-rtofs-mhw-upper-ocean-advection-2026.json"
OUTPUT = ROOT / "figures" / "osw-d14-rtofs-mhw-upper-ocean-advection-2026.svg"


def decoded_map(payload: dict, key: str) -> np.ndarray:
    return np.asarray([[np.nan if value is None else value / 100 for value in row]
                       for row in payload["bridge_interval_maps"][key]], dtype=float)


def build(source_path: Path = SOURCE, d13_path: Path = D13, analysis_path: Path = ANALYSIS, output: Path = OUTPUT) -> None:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    d13 = json.loads(d13_path.read_text(encoding="utf-8"))
    result = json.loads(analysis_path.read_text(encoding="utf-8"))
    latitude = np.asarray(source["grid"]["latitude_degrees_north_e6"], dtype=float) / 1_000_000
    longitude = np.asarray(source["grid"]["longitude_degrees_east_e6"], dtype=float) / 1_000_000
    fields = [decoded_map(result, key) for key in (
        "fixed_0_50_m_storage_tendency_w_m2_centi",
        "offline_0_50_m_horizontal_advection_w_m2_centi",
        "cross_system_partial_residual_w_m2_centi",
    )]
    titles = ["A  FIXED-COLUMN STORAGE", "B  HORIZONTAL ADVECTION", "C  PARTIAL RESIDUAL"]
    intervals = result["intervals"]
    bridge = result["bridge_evaluation"]

    mpl.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none", "svg.hashsalt": "osw-d14-column-advection-v1", "figure.facecolor": "#06171c", "axes.facecolor": "#0c252b", "text.color": "#eef9f7", "axes.labelcolor": "#9db3b2", "xtick.color": "#78979a", "ytick.color": "#78979a"})
    fig = plt.figure(figsize=(14, 9.8), dpi=100)
    grid = fig.add_gridspec(2, 6, left=.055, right=.97, top=.72, bottom=.12, height_ratios=[1.02, .86], hspace=.4, wspace=.4)
    balance = mpl.colors.LinearSegmentedColormap.from_list("budget_balance", ["#28759a", "#8fd0ca", "#102a30", "#f1cf70", "#e6654a"])
    norm = mpl.colors.TwoSlopeNorm(vmin=-3000, vcenter=0, vmax=3000)
    for index, (field, title) in enumerate(zip(fields, titles)):
        axis = fig.add_subplot(grid[0, index * 2:index * 2 + 2])
        image = axis.pcolormesh(longitude, latitude, field, shading="nearest", cmap=balance, norm=norm)
        axis.contour(longitude, latitude, field, levels=[0], colors="#eef9f7", linewidths=.7, alpha=.8)
        axis.scatter([-49.875], [42.125], marker="+", s=90, linewidths=1.8, color="#ffffff", zorder=5)
        axis.set_title(title, loc="left", fontsize=10, fontweight="bold", pad=7)
        axis.set_xlim(-52, -47); axis.set_ylim(39.5, 43.5)
        axis.set_xticks([-51, -49, -47]); axis.set_yticks([40, 41.5, 43]); axis.tick_params(labelsize=7)
        for spine in axis.spines.values(): spine.set_edgecolor("#45676b")
    color_axis = fig.add_axes([.70, .765, .27, .014])
    fig.colorbar(image, cax=color_axis, orientation="horizontal", extend="both")
    color_axis.set_title("W/m² · blue cooling/divergence · orange warming/convergence · clipped ±3000", fontsize=7.2, color="#9db3b2", pad=4)
    color_axis.tick_params(labelsize=6.5)

    time_axis = fig.add_subplot(grid[1, :2])
    x = np.arange(len(intervals)); width = .19
    budgets = [item["cross_system_partial_budget_scale"] for item in intervals]
    series = [
        ("storage", [b["rtofs_fixed_0_50_m_storage_tendency_w_m2"] for b in budgets], "#e6654a"),
        ("horiz. advection", [b["rtofs_offline_0_50_m_horizontal_advection_w_m2"] for b in budgets], "#62d7ce"),
        ("surface flux", [b["gfs_net_downward_surface_flux_w_m2"] for b in budgets], "#f1cf70"),
        ("partial residual", [b["storage_minus_horizontal_advection_minus_surface_flux_w_m2"] for b in budgets], "#d7a5ef"),
    ]
    for offset, (label, values, color) in zip((-.285, -.095, .095, .285), series):
        time_axis.bar(x + offset, values, width, color=color, label=label)
    time_axis.axhline(0, color="#eef9f7", linewidth=.7)
    time_axis.set_xticks(x, [item["start"][5:] + "→" + item["end"][8:] for item in intervals], rotation=25, fontsize=7)
    time_axis.set_ylabel("box scale · W/m²", fontsize=8)
    time_axis.set_title("D  FIVE PARTIAL BUDGETS", loc="left", fontsize=10, fontweight="bold")
    time_axis.grid(axis="y", color="#24444b", linewidth=.6); time_axis.legend(frameon=False, fontsize=6.6, ncol=2, labelcolor="#dcecea")
    for spine in time_axis.spines.values(): spine.set_edgecolor("#45676b")

    depth_axis = fig.add_subplot(grid[1, 2:4])
    limits = [10, 20, 30, 50]
    storage = [d13["intervals"][-1]["fixed_columns"][f"zero_to_{limit}_m"]["storage_tendency_w_m2"]["latitude_weighted_mean"] for limit in limits]
    advection = [intervals[-1]["depth_integrated_horizontal_advection"][f"zero_to_{limit}_m"]["endpoint_mean_horizontal_advection_w_m2"]["latitude_weighted_mean"] for limit in limits]
    depth_axis.plot(limits, storage, color="#e6654a", marker="o", linewidth=2, label="storage")
    depth_axis.plot(limits, advection, color="#62d7ce", marker="o", linewidth=2, label="horizontal advection")
    depth_axis.axhline(bridge["gfs_net_downward_surface_flux_w_m2"], color="#f1cf70", linestyle="--", linewidth=1.4, label="GFS surface gain")
    depth_axis.set_xticks(limits, [f"0–{limit}" for limit in limits]); depth_axis.set_xlabel("fixed column · m", fontsize=8); depth_axis.set_ylabel("bridge-day scale · W/m²", fontsize=8)
    depth_axis.set_title("E  MOTION EMERGES WITH DEPTH", loc="left", fontsize=10, fontweight="bold")
    depth_axis.grid(color="#24444b", linewidth=.6); depth_axis.tick_params(labelsize=7); depth_axis.legend(frameon=False, fontsize=7, labelcolor="#dcecea")
    for spine in depth_axis.spines.values(): spine.set_edgecolor("#45676b")

    callout = fig.add_subplot(grid[1, 4:]); callout.axis("off")
    callout.add_patch(mpl.patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=.02,rounding_size=.04", facecolor="#102a30", edgecolor="#f1cf70", linewidth=1.2))
    callout.text(.07, .86, "AUG 11 → 12 · 0–50 M BOX", color="#f1cf70", fontsize=9, fontweight="bold")
    callout.text(.07, .69, f"storage             +{bridge['rtofs_fixed_0_50_m_storage_tendency_w_m2']:.0f} W/m²", fontsize=10.5, fontweight="bold")
    callout.text(.07, .54, f"horizontal motion   +{bridge['rtofs_offline_0_50_m_horizontal_advection_w_m2']:.0f} W/m² · 73%", color="#62d7ce", fontsize=9.7, fontweight="bold")
    callout.text(.07, .39, f"surface gain        +{bridge['gfs_net_downward_surface_flux_w_m2']:.0f} W/m² · 48%", color="#f1cf70", fontsize=9.7, fontweight="bold")
    callout.text(.07, .24, f"partial residual      {bridge['cross_system_partial_residual_w_m2']:+.0f} W/m²", color="#d7a5ef", fontsize=10, fontweight="bold")
    callout.text(.07, .10, "Resolved scales sum to 120%; this is close in", color="#aac1c0", fontsize=8.2)
    callout.text(.07, .03, "magnitude—not a native cross-model closure.", color="#aac1c0", fontsize=8.2)

    fig.text(.055, .945, "OSW / MARINE HEATWAVE OBJECT · D14 DEPTH-INTEGRATED MOTION SCREEN", color="#62d7ce", fontsize=12, fontweight="bold")
    fig.text(.055, .895, "MOTION WAS HIDING BELOW THE SURFACE.", fontsize=24, fontweight="bold")
    fig.text(.055, .852, "The surface diagnostic is 13% of surface warming; the separate 0–50 m diagnostic is 72.5% of fixed-column storage. Depth changes the mechanism story.", color="#aac1c0", fontsize=10.1)
    fig.text(.055, .795, "AUGUST 11 → 12 · + anchor · white contour = zero · maps share one robust clipped scale", color="#78979a", fontsize=8)
    fig.text(.055, .058, "NOAA GLOBAL RTOFS / HYCOM 93.1 · 15 STANDARD DEPTHS, 0–50 M · ENDPOINT-MEAN OFFLINE −u·∇T · FOUR/EIGHT-NEIGHBOR SENSITIVITY · PLATE CARRÉE", color="#68878a", fontsize=7.0, fontweight="bold")
    fig.text(.055, .032, "GFS SURFACE TERM CROSSES MODEL SYSTEMS · NOT NATIVE TRACER FLUX OR BUDGET CLOSURE · VERTICAL EXCHANGE, MIXING, ASSIMILATION, INTERPOLATION + ERROR REMAIN", color="#68878a", fontsize=7.0, fontweight="bold")
    fig.text(.97, .032, "OSW-D14", ha="right", color="#62d7ce", fontsize=8, fontweight="bold")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, format=output.suffix.lstrip("."), facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--d13", type=Path, default=D13)
    parser.add_argument("--analysis", type=Path, default=ANALYSIS)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(); build(args.source, args.d13, args.analysis, args.output); print(f"wrote {args.output}")


if __name__ == "__main__": main()

"""Render the D12 GFS-to-RTOFS surface-energy plausibility screen."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RTOFS = ROOT / "atlas" / "data" / "rtofs-mhw-bridge-north-atlantic-20260807-20260812.json"
ANALYSIS = ROOT / "research" / "osw-d12-gfs-surface-flux-screen-2026.json"
OUTPUT = ROOT / "figures" / "osw-d12-gfs-surface-flux-screen-2026.svg"


def decoded_map(payload: dict, key: str, scale: int) -> np.ndarray:
    return np.asarray([[np.nan if value is None else value / scale for value in row] for row in payload["bridge_interval_maps"][key]], dtype=float)


def build(rtofs_path: Path = RTOFS, analysis_path: Path = ANALYSIS, output: Path = OUTPUT) -> None:
    source = json.loads(rtofs_path.read_text(encoding="utf-8"))
    result = json.loads(analysis_path.read_text(encoding="utf-8"))
    latitude = np.asarray(source["grid"]["latitude_degrees_north_e6"], dtype=float) / 1_000_000
    longitude = np.asarray(source["grid"]["longitude_degrees_east_e6"], dtype=float) / 1_000_000
    net_flux = decoded_map(result, "net_downward_surface_flux_w_m2_centi", 100)
    mixed_layer = decoded_map(result, "start_mixed_layer_depth_m_centi", 100)
    warming = decoded_map(result, "mixed_layer_equivalent_tendency_minimum_5_m_start_depth_c_per_day_e4", 10_000)
    intervals = result["intervals"]
    bridge = result["bridge_evaluation"]
    sensitivity = bridge["depth_floor_sensitivity"]

    mpl.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none", "svg.hashsalt": "osw-d12-surface-energy-v1", "figure.facecolor": "#06171c", "axes.facecolor": "#0c252b", "text.color": "#eef9f7", "axes.labelcolor": "#9db3b2", "xtick.color": "#78979a", "ytick.color": "#78979a"})
    fig = plt.figure(figsize=(14, 9.8), dpi=100)
    grid = fig.add_gridspec(2, 6, left=.055, right=.97, top=.72, bottom=.12, height_ratios=[1.05, .82], hspace=.39, wspace=.34)
    fields = [net_flux, mixed_layer, warming]
    titles = ["A  NET SURFACE HEAT FLUX", "B  STARTING MIXED LAYER", "C  FLUX-EQUIVALENT TEMPERATURE"]
    balance = mpl.colors.LinearSegmentedColormap.from_list("flux", ["#28759a", "#8fd0ca", "#102a30", "#f1cf70", "#e6654a"])
    cmaps = [balance, "viridis_r", balance]
    norms = [mpl.colors.TwoSlopeNorm(vmin=-120, vcenter=0, vmax=220), mpl.colors.Normalize(0, 60), mpl.colors.TwoSlopeNorm(vmin=-.3, vcenter=0, vmax=.85)]
    labels = ["W/m² · + downward into surface", "m · diagnostic MLD", "°C/day · blue cooling / orange warming · 5 m floor"]
    for index, (field, title, cmap, norm, label) in enumerate(zip(fields, titles, cmaps, norms, labels)):
        axis = fig.add_subplot(grid[0, index * 2:index * 2 + 2])
        image = axis.pcolormesh(longitude, latitude, field, shading="nearest", cmap=cmap, norm=norm)
        if index != 1:
            axis.contour(longitude, latitude, field, levels=[0], colors="#eef9f7", linewidths=.7, alpha=.8)
        axis.scatter([-49.875], [42.125], marker="+", s=90, linewidths=1.8, color="#ffffff", zorder=5)
        axis.set_title(title, loc="left", fontsize=10, fontweight="bold", pad=7)
        axis.set_xlim(-52, -47); axis.set_ylim(39.5, 43.5)
        axis.set_xticks([-51, -49, -47]); axis.set_yticks([40, 41.5, 43]); axis.tick_params(labelsize=7)
        for spine in axis.spines.values(): spine.set_edgecolor("#45676b")
        color_axis = fig.add_axes([.055 + index * .305, .755, .255, .014])
        fig.colorbar(image, cax=color_axis, orientation="horizontal")
        color_axis.set_title(label, fontsize=7.5, color="#9db3b2", pad=4)
        color_axis.tick_params(labelsize=6.5)

    time_axis = fig.add_subplot(grid[1, :4])
    x = np.arange(len(intervals))
    remainder = [item["cross_system_scale_comparison"]["rtofs_pre_flux_unresolved_remainder_c_per_day"] for item in intervals]
    slab = [item["rtofs_grid_collocation"]["start_depth_sensitivity"]["box_mean_flux_over_box_mean_depth_c_per_day"] for item in intervals]
    floor_5 = [item["rtofs_grid_collocation"]["start_depth_sensitivity"]["minimum_5_m_depth_c_per_day"] for item in intervals]
    native = [item["rtofs_grid_collocation"]["start_depth_sensitivity"]["native_diagnostic_depth_c_per_day"] for item in intervals]
    time_axis.axhline(0, color="#78979a", linewidth=.8)
    time_axis.bar(x, remainder, .66, color="#d7a5ef", alpha=.35, label="RTOFS remainder before flux")
    time_axis.plot(x, slab, color="#8fd0ca", marker="o", linewidth=1.6, label="box-mean slab")
    time_axis.plot(x, floor_5, color="#f1cf70", marker="o", linewidth=1.8, label="5 m floor")
    time_axis.plot(x, native, color="#e6654a", marker="o", linewidth=1.4, label="native cell depth")
    time_axis.set_xticks(x, [item["start"][5:] + "→" + item["end"][8:] for item in intervals], fontsize=8)
    time_axis.set_ylabel("temperature-change scale · °C/day", fontsize=8)
    time_axis.grid(axis="y", color="#24444b", linewidth=.7)
    time_axis.legend(frameon=False, fontsize=7.5, ncol=2, loc="upper left", labelcolor="#dcecea")
    for spine in time_axis.spines.values(): spine.set_edgecolor("#45676b")

    callout = fig.add_subplot(grid[1, 4:]); callout.axis("off")
    callout.add_patch(mpl.patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=.02,rounding_size=.04", facecolor="#102a30", edgecolor="#f1cf70", linewidth=1.2))
    low = sensitivity["start_depth"]["box_mean_flux_over_box_mean_depth_c_per_day"]
    high = sensitivity["endpoint_mean_depth"]["native_diagnostic_depth_c_per_day"]
    callout.text(.07, .84, "AUG 11 → 12 · ENERGY SCALE", color="#f1cf70", fontsize=9, fontweight="bold")
    callout.text(.07, .67, f"surface gain      +{bridge['gfs_box_net_downward_surface_flux_w_m2']:.0f} W/m²", fontsize=11, fontweight="bold")
    callout.text(.07, .50, f"warming scale    +{low:.2f} to +{high:.2f}°C/day", color="#f1cf70", fontsize=10.5, fontweight="bold")
    callout.text(.07, .34, "RTOFS remainder  +0.47°C/day", color="#d7a5ef", fontsize=10.5, fontweight="bold")
    callout.text(.07, .19, "Surface gain is material; depth choice dominates", color="#aac1c0", fontsize=8.4)
    callout.text(.07, .08, "the conversion and no variant closes the day.", color="#aac1c0", fontsize=8.4)

    fig.text(.055, .945, "OSW / MARINE HEATWAVE OBJECT · D12 SURFACE-ENERGY SCREEN", color="#62d7ce", fontsize=12, fontweight="bold")
    fig.text(.055, .895, "SURFACE FLUX TURNS POSITIVE. THE MIXED LAYER TURNS SHALLOW.", fontsize=22, fontweight="bold")
    fig.text(.055, .852, "On August 11, GFS supplies +113 W/m² into the surface while RTOFS shows a rapidly shoaling mixed layer—but the systems do not form a closed budget.", color="#aac1c0", fontsize=10.5)
    fig.text(.055, .795, "AUGUST 11 → 12 · + anchor · GFS flux bilinearly sampled on the RTOFS grid", color="#78979a", fontsize=8)
    fig.text(.055, .058, "NOAA GFS NATIVE GAUSSIAN-GRID SURFACE-FLUX FORECAST · FOUR 6-HOUR MEANS / DAY · NOAA GLOBAL RTOFS DIAGNOSTIC MLD · PLATE CARRÉE DISPLAY", color="#68878a", fontsize=7.2, fontweight="bold")
    fig.text(.055, .032, "CROSS-SYSTEM ENERGY-SCALE TEST · NOT REANALYSIS, NATIVE MODEL CLOSURE, INDEPENDENT VALIDATION, OR CAUSAL ATTRIBUTION · SHORTWAVE PENETRATION + VERTICAL TERMS UNRESOLVED", color="#68878a", fontsize=7.1, fontweight="bold")
    fig.text(.97, .032, "OSW-D12", ha="right", color="#62d7ce", fontsize=8, fontweight="bold")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, format=output.suffix.lstrip("."), facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rtofs", type=Path, default=RTOFS)
    parser.add_argument("--analysis", type=Path, default=ANALYSIS)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(); build(args.rtofs, args.analysis, args.output); print(f"wrote {args.output}")


if __name__ == "__main__": main()

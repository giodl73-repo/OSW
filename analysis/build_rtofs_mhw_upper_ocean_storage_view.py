"""Render D13 fixed-depth upper-ocean storage across the MHW bridge."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "atlas" / "data" / "rtofs-mhw-upper-ocean-north-atlantic-20260807-20260812.json"
ANALYSIS = ROOT / "research" / "osw-d13-rtofs-mhw-upper-ocean-storage-2026.json"
OUTPUT = ROOT / "figures" / "osw-d13-rtofs-mhw-upper-ocean-storage-2026.svg"


def decoded_map(payload: dict, key: str) -> np.ndarray:
    return np.asarray([[np.nan if value is None else value / 1000 for value in row]
                       for row in payload["bridge_interval_maps"][key]], dtype=float)


def build(source_path: Path = SOURCE, analysis_path: Path = ANALYSIS, output: Path = OUTPUT) -> None:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    result = json.loads(analysis_path.read_text(encoding="utf-8"))
    latitude = np.asarray(source["grid"]["latitude_degrees_north_e6"], dtype=float) / 1_000_000
    longitude = np.asarray(source["grid"]["longitude_degrees_east_e6"], dtype=float) / 1_000_000
    depths = np.asarray(source["vertical_support"]["standard_depths_m"], dtype=float)
    fields = [
        decoded_map(result, "surface_temperature_change_c_milli"),
        decoded_map(result, "zero_to_50_m_column_mean_temperature_change_c_milli"),
        decoded_map(result, "surface_minus_column_mean_change_c_milli"),
    ]
    titles = ["A  SURFACE CHANGE", "B  FIXED 0–50 M COLUMN MEAN", "C  SURFACE INTENSIFICATION"]
    intervals = result["intervals"]
    bridge = result["bridge_evaluation"]

    mpl.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none", "svg.hashsalt": "osw-d13-upper-storage-v1", "figure.facecolor": "#06171c", "axes.facecolor": "#0c252b", "text.color": "#eef9f7", "axes.labelcolor": "#9db3b2", "xtick.color": "#78979a", "ytick.color": "#78979a"})
    fig = plt.figure(figsize=(14, 9.8), dpi=100)
    grid = fig.add_gridspec(2, 6, left=.055, right=.97, top=.72, bottom=.12, height_ratios=[1.02, .86], hspace=.4, wspace=.42)
    balance = mpl.colors.LinearSegmentedColormap.from_list("storage_balance", ["#28759a", "#8fd0ca", "#102a30", "#f1cf70", "#e6654a"])
    limits = [2.0, 1.5, 1.5]
    for index, (field, title, limit) in enumerate(zip(fields, titles, limits)):
        axis = fig.add_subplot(grid[0, index * 2:index * 2 + 2])
        image = axis.pcolormesh(longitude, latitude, field, shading="nearest", cmap=balance, norm=mpl.colors.TwoSlopeNorm(vmin=-limit, vcenter=0, vmax=limit))
        axis.contour(longitude, latitude, field, levels=[0], colors="#eef9f7", linewidths=.7, alpha=.8)
        axis.scatter([-49.875], [42.125], marker="+", s=90, linewidths=1.8, color="#ffffff", zorder=5)
        axis.set_title(title, loc="left", fontsize=10, fontweight="bold", pad=7)
        axis.set_xlim(-52, -47); axis.set_ylim(39.5, 43.5)
        axis.set_xticks([-51, -49, -47]); axis.set_yticks([40, 41.5, 43]); axis.tick_params(labelsize=7)
        for spine in axis.spines.values(): spine.set_edgecolor("#45676b")
        color_axis = fig.add_axes([.055 + index * .305, .755, .255, .014])
        fig.colorbar(image, cax=color_axis, orientation="horizontal", extend="both")
        color_axis.set_title(f"°C/day · blue cooling / orange warming · clipped at ±{limit:g}", fontsize=7.2, color="#9db3b2", pad=4)
        color_axis.tick_params(labelsize=6.5)

    profile_axis = fig.add_subplot(grid[1, :2])
    colors = ["#4e879f", "#6eb1bc", "#a8cdbf", "#f1cf70", "#e6654a"]
    for interval, color in zip(intervals, colors):
        profile = [interval["box_mean_temperature_change_by_standard_depth_c"][str(int(z))] for z in depths]
        label = interval["start"][5:] + "→" + interval["end"][8:]
        profile_axis.plot(profile, depths, color=color, linewidth=2 if interval is intervals[-1] else 1.1, marker="o" if interval is intervals[-1] else None, markersize=3, label=label)
    profile_axis.axvline(0, color="#78979a", linewidth=.8)
    profile_axis.invert_yaxis(); profile_axis.set_ylim(50, 0)
    profile_axis.set_xlabel("box-mean ΔT · °C/day", fontsize=8); profile_axis.set_ylabel("standard depth · m", fontsize=8)
    profile_axis.set_title("D  WHERE EACH DAY WARMS OR COOLS", loc="left", fontsize=10, fontweight="bold")
    profile_axis.grid(color="#24444b", linewidth=.6); profile_axis.tick_params(labelsize=7)
    profile_axis.legend(frameon=False, fontsize=6.8, ncol=2, labelcolor="#dcecea")
    for spine in profile_axis.spines.values(): spine.set_edgecolor("#45676b")

    storage_axis = fig.add_subplot(grid[1, 2:4])
    limits_m = [10, 20, 30, 50]
    storage = [intervals[-1]["fixed_columns"][f"zero_to_{limit}_m"]["storage_tendency_w_m2"]["latitude_weighted_mean"] for limit in limits_m]
    storage_axis.bar(np.arange(4), storage, color=["#8fd0ca", "#62d7ce", "#f1cf70", "#e6654a"], width=.7)
    storage_axis.axhline(bridge["gfs_net_downward_surface_flux_w_m2"], color="#ffffff", linestyle="--", linewidth=1.3, label="GFS surface gain +113 W/m²")
    storage_axis.set_xticks(np.arange(4), [f"0–{limit} m" for limit in limits_m], fontsize=8)
    storage_axis.set_ylabel("fixed-column storage tendency · W/m²", fontsize=8)
    storage_axis.set_title("E  HEAT GAIN ACCUMULATES WITH DEPTH", loc="left", fontsize=10, fontweight="bold")
    storage_axis.grid(axis="y", color="#24444b", linewidth=.7); storage_axis.tick_params(labelsize=7)
    storage_axis.legend(frameon=False, fontsize=7.2, labelcolor="#dcecea", loc="upper left")
    for spine in storage_axis.spines.values(): spine.set_edgecolor("#45676b")

    callout = fig.add_subplot(grid[1, 4:]); callout.axis("off")
    callout.add_patch(mpl.patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=.02,rounding_size=.04", facecolor="#102a30", edgecolor="#f1cf70", linewidth=1.2))
    callout.text(.07, .86, "AUG 11 → 12 · BOX SCALE", color="#f1cf70", fontsize=9, fontweight="bold")
    callout.text(.07, .69, f"surface ΔT       +{bridge['box_surface_temperature_change_c']:.2f}°C", fontsize=11, fontweight="bold")
    callout.text(.07, .53, f"0–50 m mean ΔT  +{bridge['box_zero_to_50_m_column_mean_temperature_change_c']:.2f}°C", color="#62d7ce", fontsize=10.5, fontweight="bold")
    callout.text(.07, .37, f"column storage   +{bridge['box_zero_to_50_m_storage_tendency_w_m2']:.0f} W/m²", color="#e6654a", fontsize=10.5, fontweight="bold")
    callout.text(.07, .21, f"GFS surface gain +{bridge['gfs_net_downward_surface_flux_w_m2']:.0f} W/m² · scale 48%", color="#f1cf70", fontsize=9.7, fontweight="bold")
    callout.text(.07, .08, "Surface intensifies 5.4× faster, but the fixed", color="#aac1c0", fontsize=8.2)
    callout.text(.07, .01, "column also gains heat. The budget stays open.", color="#aac1c0", fontsize=8.2)

    fig.text(.055, .945, "OSW / MARINE HEATWAVE OBJECT · D13 FIXED-COLUMN STORAGE SCREEN", color="#62d7ce", fontsize=12, fontweight="bold")
    fig.text(.055, .895, "THE SURFACE INTENSIFIES. THE UPPER OCEAN ALSO GAINS HEAT.", fontsize=22, fontweight="bold")
    fig.text(.055, .852, "The box-average surface warms 5.4× faster than the 0–50 m mean; forecast-derived surface gain is 48% of the cross-system modeled storage magnitude.", color="#aac1c0", fontsize=10.5)
    fig.text(.055, .795, "AUGUST 11 → 12 · + anchor · white contour = zero change · fixed-depth integration avoids division by a changing MLD", color="#78979a", fontsize=8)
    fig.text(.055, .058, "NOAA GLOBAL RTOFS / HYCOM 93.1 · 15 STANDARD DEPTHS, 0–50 M · POTENTIAL TEMPERATURE · 00 UTC N024 NOWCASTS · PLATE CARRÉE DISPLAY", color="#68878a", fontsize=7.2, fontweight="bold")
    fig.text(.055, .032, "STANDARD-DEPTH STORAGE PROXY WITH CONSTANT ρCp · GFS COMPARISON CROSSES MODEL SYSTEMS · NOT NATIVE-LAYER HEAT CONTENT, CLOSED BUDGET, OBSERVATION, OR CAUSAL ATTRIBUTION", color="#68878a", fontsize=7.0, fontweight="bold")
    fig.text(.97, .032, "OSW-D13", ha="right", color="#62d7ce", fontsize=8, fontweight="bold")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, format=output.suffix.lstrip("."), facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--analysis", type=Path, default=ANALYSIS)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(); build(args.source, args.analysis, args.output); print(f"wrote {args.output}")


if __name__ == "__main__": main()

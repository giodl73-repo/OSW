"""Render the separate-product OISST cross-check of the D4 threshold bridge."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "atlas" / "data" / "oisst-mhw-bridge-north-atlantic-20260807-20260812.json"
ANALYSIS = ROOT / "research" / "osw-d10-oisst-mhw-bridge-crosscheck-2026.json"
OUTPUT = ROOT / "figures" / "osw-d10-oisst-mhw-bridge-crosscheck-2026.svg"


def build(source_path: Path = SOURCE, analysis_path: Path = ANALYSIS, output: Path = OUTPUT) -> None:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    result = json.loads(analysis_path.read_text(encoding="utf-8"))
    latitudes = np.asarray(source["latitude_degrees_north"])
    longitudes = np.asarray(source["longitude_degrees_east"])
    dates = [row[0] for row in source["rows"]]
    fields = [np.asarray(row[1], dtype=float) / 100 for row in source["rows"]]
    days = result["days"]

    mpl.rcParams.update({
        "font.family": "DejaVu Sans",
        "svg.fonttype": "none",
        "svg.hashsalt": "osw-d10-oisst-bridge-v1",
        "axes.facecolor": "#0c252b",
        "figure.facecolor": "#06171c",
        "text.color": "#eef9f7",
        "axes.labelcolor": "#9db3b2",
        "xtick.color": "#718e90",
        "ytick.color": "#718e90",
    })
    fig = plt.figure(figsize=(14, 9.8), dpi=100)
    grid = fig.add_gridspec(3, 6, left=.055, right=.97, top=.77, bottom=.11, height_ratios=[1, 1, .8], hspace=.38, wspace=.28)
    cmap = mpl.colors.LinearSegmentedColormap.from_list("osw_sst", ["#163f54", "#277d91", "#65c5b8", "#f0cf70", "#e96d4b"])
    image = None
    for index, (date, field) in enumerate(zip(dates, fields)):
        axis = fig.add_subplot(grid[index // 3, (index % 3) * 2 : (index % 3) * 2 + 2])
        image = axis.pcolormesh(longitudes, latitudes, field, shading="nearest", cmap=cmap, vmin=15, vmax=27)
        axis.contour(longitudes, latitudes, field, levels=[24, 25], colors=["#e9f5f2", "#f4d476"], linewidths=[.7, 1.1], alpha=.9)
        axis.scatter([-49.875], [42.125], marker="+", s=80, linewidths=1.8, color="#ffffff", zorder=5)
        day = days[index]
        axis.set_title(f"{date[5:].replace('-', ' / ')}   CRW {day['crw_anchor_category']}", fontsize=10.5, fontweight="bold", loc="left", color="#eef9f7", pad=6)
        axis.text(.99, .04, f"anchor {day['oisst_anchor_sst_c']:.2f}°C", transform=axis.transAxes, ha="right", fontsize=8, color="#dcecea", fontweight="bold")
        axis.set_xlim(longitudes.min() - .125, longitudes.max() + .125)
        axis.set_ylim(latitudes.min() - .125, latitudes.max() + .125)
        axis.set_xticks([-51, -49, -47.5]); axis.set_yticks([40.5, 41.5, 42.5])
        axis.tick_params(labelsize=7, length=2)
        for spine in axis.spines.values(): spine.set_edgecolor("#45676b")
    color_axis = fig.add_axes([.79, .805, .18, .018])
    fig.colorbar(image, cax=color_axis, orientation="horizontal", label="OISST °C")
    color_axis.tick_params(labelsize=7)

    line = fig.add_subplot(grid[2, :4])
    x = np.arange(len(days))
    anchor = np.asarray([day["oisst_anchor_sst_c"] for day in days])
    box = np.asarray([day["oisst_fixed_box_area_weighted_mean_sst_c"] for day in days])
    line.plot(x, anchor, color="#f4d476", marker="o", linewidth=2.2, label="nearest OISST cell")
    line.plot(x, box, color="#65c5b8", marker="o", linewidth=2.2, label="fixed-box mean")
    line.axvspan(3.5, 5.0, color="#d7a5ef", alpha=.08)
    line.set_xticks(x, [date[5:].replace("-", "/") for date in dates], fontsize=8)
    line.set_ylabel("surface temperature · °C", fontsize=8)
    line.grid(axis="y", color="#24444b", linewidth=.7)
    line.legend(frameon=False, fontsize=8, ncol=2, loc="lower left", labelcolor="#dcecea")
    for spine in line.spines.values(): spine.set_edgecolor("#45676b")

    callout = fig.add_subplot(grid[2, 4:]); callout.axis("off")
    callout.add_patch(mpl.patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=.02,rounding_size=.04", facecolor="#102a30", edgecolor="#d7a5ef", linewidth=1.2))
    callout.text(.07, .82, "AUG 11 → 12", color="#d7a5ef", fontsize=9, fontweight="bold")
    callout.text(.07, .61, "CRW category   0 → 1", fontsize=13, fontweight="bold")
    callout.text(.07, .40, "anchor OISST   −0.13°C", color="#f4d476", fontsize=11, fontweight="bold")
    callout.text(.07, .23, "box mean       +0.16°C", color="#65c5b8", fontsize=11, fontweight="bold")
    callout.text(.07, .08, "Threshold return ≠ local rebound", color="#9db3b2", fontsize=8.5)

    fig.text(.055, .945, "OSW / MARINE HEATWAVE OBJECT · D10 SEPARATE-PRODUCT SST CROSS-CHECK", color="#62d7ce", fontsize=12, fontweight="bold")
    fig.text(.055, .895, "THE CATEGORY RETURNS. THE NEAREST CELL KEEPS COOLING.", fontsize=25, fontweight="bold")
    fig.text(.055, .855, "The neighborhood warms on August 12 while the anchor cools—evidence for spatial/product distinction, not a diagnosed cause.", color="#aac1c0", fontsize=11)
    fig.text(.055, .81, "+  anchor · contours 24/25°C · identical 15–27°C scale", color="#708f91", fontsize=8)
    fig.text(.055, .052, "NOAA OISST V2.1 · DAILY 0.25° OBJECTIVELY ANALYZED SST · EQUIRECTANGULAR (PLATE CARRÉE) · FIXED 40.125–42.875°N, 51.375–47.375°W BOX", color="#68878a", fontsize=7.5, fontweight="bold")
    fig.text(.055, .027, "SEPARATE FROM 0.05° CORALTEMP-DERIVED CATEGORIES; INPUTS MAY OVERLAP · NOT HEAT CONTENT, ADVECTION, SURFACE-FLUX ATTRIBUTION, OR CAUSATION", color="#68878a", fontsize=7.5, fontweight="bold")
    fig.text(.97, .027, "OSW-D10", ha="right", color="#62d7ce", fontsize=8, fontweight="bold")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, format="svg", facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--analysis", type=Path, default=ANALYSIS)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    build(args.source, args.analysis, args.output)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

"""Render the scale sensitivity of connected Nordic heat-jet runs."""

from __future__ import annotations

import argparse
import json
import pathlib

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np


def build(input_path: pathlib.Path, output_path: pathlib.Path) -> None:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    cases = payload["cases"]
    windows = np.asarray([case["window_faces"] for case in cases])
    run_counts = np.asarray([case["run_count"] for case in cases])
    singles = np.asarray([case["single_face_run_count"] for case in cases])
    distance_runs = np.asarray(payload["summary"]["distance_run_counts"])
    distance_singles = np.asarray(payload["summary"]["distance_single_face_run_counts"])
    strongest_in = np.asarray([case["strongest_inward_run"]["net_heat_convergence_TW_at_0C"] for case in cases])
    leader_component = np.asarray([case["annual_leader_component"]["net_heat_convergence_TW_at_0C"] for case in cases])
    strongest_out = np.asarray([case["strongest_outward_run"]["net_heat_convergence_TW_at_0C"] for case in cases])
    ridge_signs = np.asarray([next(section["signs"] for section in case["sections"] if section["id"] == "iceland_scotland_ridge") for case in cases])

    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.hashsalt": "osw-nordic-jet-run-sensitivity-v1"})
    figure = plt.figure(figsize=(12.6, 7.4), facecolor="#f4f1e9")
    grid = figure.add_gridspec(2, 2, left=0.075, right=0.955, top=0.75, bottom=0.13, width_ratios=(0.85, 1.5), hspace=0.5, wspace=0.3)

    count_axis = figure.add_subplot(grid[:, 0])
    count_axis.plot(windows, run_counts, color="#183944", marker="o", linewidth=2.2, label="all runs")
    count_axis.plot(windows, singles, color="#8a989a", marker="o", linewidth=2.2, label="single-face runs")
    count_axis.plot(windows, distance_runs, color="#183944", marker="s", linewidth=1.4, linestyle="--", label="km-radius runs")
    count_axis.plot(windows, distance_singles, color="#8a989a", marker="s", linewidth=1.4, linestyle="--", label="km-radius singletons")
    for x, total, one in zip(windows, run_counts, singles):
        count_axis.text(x, total + 3, str(total), ha="center", color="#183944", fontweight="bold")
        count_axis.text(x, one - 5, str(one), ha="center", color="#68777b", fontweight="bold")
    count_axis.set_xticks(windows)
    count_axis.set_ylim(-3, 106)
    count_axis.set_xlabel("centered smoothing window (faces)")
    count_axis.set_ylabel("connected components")
    count_axis.set_title("A  FRAGMENTATION FALLS RAPIDLY", loc="left", fontsize=10, fontweight="bold")
    count_axis.legend(frameon=False, loc="upper right", fontsize=7.5)
    count_axis.spines[["top", "right"]].set_visible(False)

    ribbon_axis = figure.add_subplot(grid[0, 1])
    ribbon_axis.imshow(ridge_signs, cmap=ListedColormap(("#23677a", "#d17829")), vmin=-1, vmax=1, aspect="auto", interpolation="nearest")
    ribbon_axis.set_yticks(range(4), [f"{window}-face" for window in windows])
    ribbon_axis.set_xlabel("ordered Iceland–Scotland boundary face")
    ribbon_axis.set_title("B  CORES MERGE INTO BROADER INFLOW BANDS", loc="left", fontsize=10, fontweight="bold")
    ribbon_axis.axvline(8, color="#f4f1e9", linewidth=1.2, linestyle="--")
    ribbon_axis.text(8.6, 0.1, "annual leader", rotation=90, va="top", fontsize=7, color="#f4f1e9")

    heat_axis = figure.add_subplot(grid[1, 1])
    heat_axis.plot(windows, strongest_in, color="#d17829", marker="o", linewidth=2.2, label="strongest import component")
    heat_axis.plot(windows, leader_component, color="#c89a48", marker="s", linewidth=1.8, linestyle="--", label="component containing annual leader")
    heat_axis.plot(windows, strongest_out, color="#23677a", marker="o", linewidth=2.2, label="strongest export component")
    heat_axis.axhline(0, color="#8a989a", linewidth=0.7)
    heat_axis.set_xticks(windows)
    heat_axis.set_xlabel("centered smoothing window (faces)")
    heat_axis.set_ylabel("original unsmoothed heat sum (TW)")
    heat_axis.set_title("C  THE DOMINANT IMPORT CHANGES SCALE", loc="left", fontsize=10, fontweight="bold")
    heat_axis.legend(frameon=False, fontsize=7.5, loc="center left")
    heat_axis.spines[["top", "right"]].set_visible(False)

    figure.text(0.045, 0.95, "NORDIC HEAT JETS FORM A HIERARCHY, NOT ONE FIXED SET", fontsize=18.5, fontweight="bold", color="#183944")
    figure.text(0.045, 0.902, "Face-count windows calibrated against cumulative face-center distance radii of 0, 20, 30, and 50 km", fontsize=9.5, color="#4c5d63")
    figure.text(0.045, 0.825, "Face/km agreement: 3/20 = 97.5% · 5/30 = 97.9% · 7/50 = 93.7%. The compact-to-broad hierarchy survives physical calibration.", fontsize=10.2, color="#183944", fontweight="bold")
    figure.text(0.045, 0.04, "Solid circles use face windows; dashed squares use matched km radii · distance follows face centers, not physical edges · no scale is uniquely correct", fontsize=7.2, color="#68777b")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, format="svg", metadata={"Date": None})
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-jet-run-sensitivity-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m4-oras5-nordic-jet-run-sensitivity-2018.svg"))
    args = parser.parse_args()
    build(args.input, args.output)
    print(args.output.resolve())


if __name__ == "__main__":
    main()

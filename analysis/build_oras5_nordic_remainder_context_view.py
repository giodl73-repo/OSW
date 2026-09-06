"""Render the Nordic remainder beside same-room ice and mixed-layer seasonality."""

from __future__ import annotations

import argparse
import json
import pathlib

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def build(input_path: pathlib.Path, output_path: pathlib.Path) -> None:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    records = payload["months"]
    correlations = payload["zero_lag_pearson_correlation_with_remainder"]
    x = np.arange(12)
    remainder = np.asarray([record["unresolved_remainder_TW"] for record in records])
    ice = 100 * np.asarray([record["area_mean_ice_concentration"] for record in records])
    mixed_layer = np.asarray([record["area_mean_mixed_layer_depth_m"] for record in records])

    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.hashsalt": "osw-nordic-remainder-context-v1"})
    figure = plt.figure(figsize=(12.6, 6.7), facecolor="#f4f1e9")
    grid = figure.add_gridspec(1, 3, left=0.055, right=0.96, top=0.76, bottom=0.21, width_ratios=(1.35, 1, 1), wspace=0.28)

    remainder_axis = figure.add_subplot(grid[0, 0])
    remainder_axis.bar(x, remainder, color=np.where(remainder >= 0, "#d17829", "#2a7e91"), width=0.7)
    remainder_axis.axhline(0, color="#5f6d72", linewidth=0.7)
    remainder_axis.set_xticks(x, list("JFMAMJJASOND"))
    remainder_axis.set_ylabel("unresolved remainder (TW)")
    remainder_axis.set_title("A  REMAINDER ALTERNATES", loc="left", fontweight="bold")
    remainder_axis.spines[["top", "right"]].set_visible(False)

    ice_axis = figure.add_subplot(grid[0, 1])
    ice_axis.fill_between(x, ice, color="#9bc9d2", alpha=0.75)
    ice_axis.plot(x, ice, color="#23677a", marker="o", linewidth=1.6, markersize=4)
    ice_axis.set_xticks(x, list("JFMAMJJASOND"))
    ice_axis.set_ylabel("area-mean ice concentration (%)")
    ice_axis.set_ylim(bottom=0)
    ice_axis.set_title("B  ICE HAS A SMOOTH SEASON", loc="left", fontweight="bold")
    ice_axis.text(0.03, 0.94, f"r with remainder = {correlations['area_mean_ice_concentration']:+.2f}", transform=ice_axis.transAxes, va="top", color="#334d56")
    ice_axis.spines[["top", "right"]].set_visible(False)

    mixed_axis = figure.add_subplot(grid[0, 2])
    mixed_axis.fill_between(x, mixed_layer, color="#d9c7a6", alpha=0.8)
    mixed_axis.plot(x, mixed_layer, color="#8b5e34", marker="o", linewidth=1.6, markersize=4)
    mixed_axis.set_xticks(x, list("JFMAMJJASOND"))
    mixed_axis.set_ylabel("area-mean mixed-layer depth (m)")
    mixed_axis.set_ylim(bottom=0)
    mixed_axis.set_title("C  MIXING DEPTH HAS ONE TOO", loc="left", fontweight="bold")
    mixed_axis.text(0.03, 0.94, f"r with remainder = {correlations['area_mean_mixed_layer_depth_m']:+.2f}", transform=mixed_axis.transAxes, va="top", color="#334d56")
    mixed_axis.spines[["top", "right"]].set_visible(False)

    figure.text(0.045, 0.935, "THE REMAINDER DOES NOT FOLLOW THE OBVIOUS SEASONAL CLOCK", fontsize=18, fontweight="bold", color="#183944")
    figure.text(0.045, 0.89, "Same 12,550-cell Nordic room · 2018 monthly ORAS5 means · contemporaneous comparison only", fontsize=9.5, color="#4c5d63")
    figure.text(0.045, 0.825, "Ice concentration is nearly unrelated to the monthly remainder; mixed-layer depth is only modestly aligned.", fontsize=10.5, color="#183944", fontweight="bold")
    figure.text(0.045, 0.055, "Twelve months from one reanalysis year · seasonal confounding · correlation is not attribution · the remainder still mixes unavailable native terms and offline-method error", fontsize=7.2, color="#68777b")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, format="svg", metadata={"Date": None})
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-remainder-context-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m4-oras5-nordic-remainder-context-2018.svg"))
    args = parser.parse_args()
    build(args.input, args.output)
    print(args.output.resolve())


if __name__ == "__main__":
    main()

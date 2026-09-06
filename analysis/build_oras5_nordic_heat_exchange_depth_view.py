"""Render gate-by-depth Nordic heat convergence from paired donor branches."""

from __future__ import annotations

import argparse
import json
import pathlib

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


GATE_LABELS = ("DENMARK", "ICELAND–SCOTLAND", "NORTH SEA", "FRAM", "NORWAY–SVALBARD")
DEPTH_LABELS = ("0–100", "100–300", "300–700", "700–1500", "1500–3000", ">3000")


def build(input_path: pathlib.Path, output_path: pathlib.Path) -> None:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    matrix = np.asarray([[item["net_heat_convergence_TW_at_0C"] for item in section["depth_bins"]] for section in payload["time_weighted_2018"]])
    totals = matrix.sum(axis=0)
    upper = float(totals[:3].sum()); deep = float(totals[3:].sum())

    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.hashsalt": "osw-nordic-heat-exchange-depth-v1"})
    figure = plt.figure(figsize=(12.6, 6.7), facecolor="#f4f1e9")
    grid = figure.add_gridspec(1, 2, left=0.115, right=0.95, top=0.76, bottom=0.2, width_ratios=(1.7, 0.75), wspace=0.28)

    matrix_axis = figure.add_subplot(grid[0, 0])
    limit = max(abs(matrix.min()), abs(matrix.max()))
    image = matrix_axis.imshow(matrix, cmap="RdBu_r", vmin=-limit, vmax=limit, aspect="auto")
    matrix_axis.set_xticks(np.arange(6), DEPTH_LABELS)
    matrix_axis.set_yticks(np.arange(5), GATE_LABELS)
    matrix_axis.set_xlabel("reference-depth layer (m)")
    matrix_axis.set_title("A  WHERE EACH GATE ADDS OR REMOVES HEAT", loc="left", fontweight="bold")
    matrix_axis.tick_params(length=0)
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            value = matrix[row, column]
            matrix_axis.text(column, row, f"{value:+.0f}", ha="center", va="center", color="white" if abs(value) > 0.48 * limit else "#263d45", fontsize=8)
    colorbar = figure.colorbar(image, ax=matrix_axis, fraction=0.035, pad=0.025)
    colorbar.set_label("net heat convergence (TW)")

    total_axis = figure.add_subplot(grid[0, 1])
    y = np.arange(6)
    total_axis.barh(y, totals, color=np.where(totals >= 0, "#d17829", "#2a7e91"), height=0.62)
    total_axis.axvline(0, color="#53656b", linewidth=0.8)
    total_axis.set_yticks(y, DEPTH_LABELS)
    total_axis.invert_yaxis()
    total_axis.set_xlabel("all-gate convergence (TW)")
    total_axis.set_title("B  THE ROOM'S VERTICAL SUM", loc="left", fontweight="bold")
    total_axis.spines[["top", "right"]].set_visible(False)
    for row, value in enumerate(totals):
        total_axis.text(value + (2 if value >= 0 else -2), row, f"{value:+.1f}", ha="left" if value >= 0 else "right", va="center", fontsize=8, color="#334d56")
    total_axis.set_xlim(min(-18, totals.min() - 8), totals.max() + 20)

    figure.text(0.045, 0.935, "THE HEAT EXCHANGE LIVES ABOVE 700 METRES", fontsize=19, fontweight="bold", color="#183944")
    figure.text(0.045, 0.89, "Time-weighted 2018 upwind-donor sensitivity · five gates × six reference-depth layers · 0°C reference", fontsize=9.5, color="#4c5d63")
    figure.text(0.045, 0.825, f"The room gains {upper:+.1f} TW above 700 m and loses {abs(deep):.1f} TW below it; depth changes which gates dominate.", fontsize=10.5, color="#183944", fontweight="bold")
    figure.text(0.045, 0.05, "Reference-layer midpoint binning · reconstructed partial steps · donor sampling is not native FCT/TVD · positive means heat converges into the Nordic room", fontsize=7.2, color="#68777b")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, format="svg", metadata={"Date": None})
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-heat-exchange-anatomy-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m4-oras5-nordic-heat-exchange-depth-2018.svg"))
    args = parser.parse_args()
    build(args.input, args.output)
    print(args.output.resolve())


if __name__ == "__main__":
    main()

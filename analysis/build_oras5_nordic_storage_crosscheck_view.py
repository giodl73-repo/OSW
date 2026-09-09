"""Render the Nordic Seas independent storage cross-check."""

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
    summary = payload["summary"]
    x = np.arange(12)
    native = np.asarray([record["archived_column_storage_tendency_TW"] for record in records])
    reconstructed = np.asarray([record["reconstructed_temperature_storage_tendency_TW"] for record in records])
    difference = np.asarray([record["storage_difference_TW"] for record in records])

    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.hashsalt": "osw-nordic-storage-crosscheck-v1"})
    figure = plt.figure(figsize=(12.6, 6.7), facecolor="#f4f1e9")
    grid = figure.add_gridspec(1, 2, left=0.055, right=0.94, top=0.79, bottom=0.22, width_ratios=(1.55, 1), wspace=0.26)
    axis = figure.add_subplot(grid[0, 0])
    axis.plot(x, reconstructed, color="#d17829", linewidth=3.5, alpha=0.7, label="reconstructed from 75-level temperature")
    axis.plot(x, native, color="#183944", marker="o", markersize=4.5, linewidth=1.7, label="archived ORAS5 column heat")
    axis.axhline(0, color="#647177", linewidth=0.7)
    axis.set_xticks(x, list("JFMAMJJASOND"))
    axis.set_ylabel("storage tendency (TW)")
    axis.set_title("A  TWO INDEPENDENT STORAGE ESTIMATES OVERLAP", loc="left", fontweight="bold")
    axis.spines[["top", "right"]].set_visible(False)
    axis.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22), ncol=1, frameon=False)

    check = figure.add_subplot(grid[0, 1])
    check.bar(x, difference, color=np.where(difference >= 0, "#2a7e91", "#8a5b8e"), width=0.68)
    check.axhline(0, color="#647177", linewidth=0.7)
    check.set_xticks(x, list("JFMAMJJASOND"))
    check.set_ylabel("archived minus reconstructed (TW)")
    check.set_title("B  THE DIFFERENCE IS SMALL", loc="left", fontweight="bold")
    check.spines[["top", "right"]].set_visible(False)

    figure.text(0.045, 0.935, "STORAGE IS NOT THE MISSING 38 TW", fontsize=19, fontweight="bold", color="#183944")
    figure.text(0.045, 0.895, f"Independent ORAS5 column heat vs reconstructed native volume · r = {summary['storage_tendency_correlation']:.5f} · RMSE {summary['storage_tendency_rmse_TW']:.2f} TW", fontsize=9.5, color="#4c5d63")
    figure.text(0.045, 0.842, f"Replacing storage moves the time-weighted remainder only from {summary['time_weighted_original_remainder_TW']:+.1f} to {summary['time_weighted_archived_storage_remainder_TW']:+.1f} TW.", fontsize=10.5, color="#183944", fontweight="bold")
    figure.text(0.045, 0.055, "One ORAS5 member and year · monthly-mean midpoint differences · this validates storage agreement, not native tracer-budget closure", fontsize=7.4, color="#68777b")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, format="svg", metadata={"Date": None})
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-storage-crosscheck-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m4-oras5-nordic-storage-crosscheck-2018.svg"))
    args = parser.parse_args()
    build(args.input, args.output)
    print(args.output.resolve())


if __name__ == "__main__":
    main()

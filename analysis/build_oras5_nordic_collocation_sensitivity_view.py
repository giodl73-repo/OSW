"""Render Nordic boundary tracer-collocation sensitivity."""

from __future__ import annotations

import argparse
import json
import pathlib

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


METHODS = ("adjacent_mean", "inside_cell", "outside_cell", "upwind")
METHOD_LABELS = ("ADJACENT\nMEAN", "INSIDE\nCELL", "OUTSIDE\nCELL", "UPWIND\nDONOR")
SECTION_LABELS = ("DENMARK", "ICELAND–\nSCOTLAND", "NORTH\nSEA", "FRAM", "NORWAY–\nSVALBARD")


def build(input_path: pathlib.Path, output_path: pathlib.Path) -> None:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    summary = payload["summary"]
    x = np.arange(4)
    convergence = np.asarray([summary[method]["time_weighted_advective_convergence_TW_at_0C"] for method in METHODS])
    mean_remainder = np.asarray([summary[method]["time_weighted_unresolved_remainder_TW_at_0C"] for method in METHODS])
    section_summary = payload["time_weighted_section_convergence_TW_at_0C"]
    section_shifts = np.asarray([values["upwind"] - values["adjacent_mean"] for values in section_summary.values()])
    months = np.arange(12)
    adjacent_months = np.asarray([record["methods"]["adjacent_mean"]["unresolved_remainder_TW_at_0C"] for record in payload["months"]])
    upwind_months = np.asarray([record["methods"]["upwind"]["unresolved_remainder_TW_at_0C"] for record in payload["months"]])

    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.7, "svg.hashsalt": "osw-nordic-collocation-sensitivity-v1"})
    figure = plt.figure(figsize=(12.6, 6.7), facecolor="#f4f1e9")
    grid = figure.add_gridspec(1, 3, left=0.055, right=0.96, top=0.76, bottom=0.22, width_ratios=(1, 1.1, 1.5), wspace=0.3)

    total_axis = figure.add_subplot(grid[0, 0])
    colors = ["#d17829", "#d9a167", "#d9a167", "#2a7e91"]
    total_axis.bar(x, convergence, color=colors, width=0.66)
    total_axis.set_xticks(x, METHOD_LABELS)
    total_axis.set_ylabel("advective heat convergence (TW)")
    total_axis.set_title("A  ONE RULE MOVES 43 TW", loc="left", fontweight="bold")
    total_axis.spines[["top", "right"]].set_visible(False)
    for index, (heat, remainder) in enumerate(zip(convergence, mean_remainder)):
        total_axis.text(index, heat + 3, f"{heat:.1f}\nrem {remainder:+.1f}", ha="center", va="bottom", fontsize=7.5, color="#334d56")
    total_axis.set_ylim(0, max(convergence) + 32)

    section_axis = figure.add_subplot(grid[0, 1])
    colors = np.where(section_shifts >= 0, "#d17829", "#2a7e91")
    section_axis.bar(np.arange(5), section_shifts, color=colors, width=0.65)
    section_axis.axhline(0, color="#5f6d72", linewidth=0.7)
    section_axis.set_xticks(np.arange(5), SECTION_LABELS)
    section_axis.set_ylabel("upwind minus adjacent-mean convergence (TW)")
    section_axis.set_title("B  SOUTHERN INFLOW DRIVES IT", loc="left", fontweight="bold")
    section_axis.spines[["top", "right"]].set_visible(False)
    for index, value in enumerate(section_shifts):
        section_axis.text(index, value + (1 if value >= 0 else -1), f"{value:+.1f}", ha="center", va="bottom" if value >= 0 else "top", fontsize=7.5)

    month_axis = figure.add_subplot(grid[0, 2])
    month_axis.plot(months, adjacent_months, color="#d17829", marker="o", linewidth=1.6, label="adjacent mean")
    month_axis.plot(months, upwind_months, color="#2a7e91", marker="o", linewidth=1.6, label="upwind donor")
    month_axis.axhline(0, color="#5f6d72", linewidth=0.7)
    month_axis.set_xticks(months, list("JFMAMJJASOND"))
    month_axis.set_ylabel("unresolved remainder (TW)")
    month_axis.set_title("C  MEAN CLOSURE IS NOT MONTHLY CLOSURE", loc="left", fontweight="bold")
    month_axis.spines[["top", "right"]].set_visible(False)
    month_axis.legend(loc="lower center", bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False)

    figure.text(0.045, 0.935, "THE BUDGET GAP IS SENSITIVE TO THE FACE-FLUX RULE", fontsize=18, fontweight="bold", color="#183944")
    figure.text(0.045, 0.89, "2018 Nordic room · identical velocity, geometry, storage, and surface forcing · 0°C reference", fontsize=9.5, color="#4c5d63")
    figure.text(0.045, 0.825, "Upwind donor sampling nearly closes the annual mean—but does not reproduce ORAS5's nonlinear native tracer scheme.", fontsize=10.5, color="#183944", fontweight="bold")
    figure.text(0.045, 0.055, "All rules multiply separate monthly-mean velocity and temperature · upwind is a sensitivity endpoint, not native FCT/TVD · submonthly covariance and model tendencies remain unavailable", fontsize=7.2, color="#68777b")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, format="svg", metadata={"Date": None})
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-collocation-sensitivity-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m4-oras5-nordic-collocation-sensitivity-2018.svg"))
    args = parser.parse_args()
    build(args.input, args.output)
    print(args.output.resolve())


if __name__ == "__main__":
    main()

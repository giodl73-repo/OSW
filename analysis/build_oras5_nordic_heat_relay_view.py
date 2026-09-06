"""Render the monthly Nordic heat-relay timing screen."""

from __future__ import annotations

import argparse
import json
import pathlib

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")


def build(input_path: pathlib.Path, output_path: pathlib.Path) -> None:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    months = payload["months"]
    south = np.asarray([month["southern_gate_input_TW"] for month in months])
    north = np.asarray([month["northern_gate_export_TW"] for month in months])
    surface = np.asarray([month["surface_downward_TW"] for month in months])
    storage = np.asarray([month["storage_tendency_TW"] for month in months])
    shifts = np.asarray(list(payload["summary"]["southern_to_northern_circular_shift_correlations"].values()))
    corr = payload["summary"]["same_month_correlations"]
    means = payload["summary"]["mean_powers_TW"]

    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "svg.hashsalt": "osw-nordic-heat-relay-v1"})
    figure = plt.figure(figsize=(12.6, 8.0), facecolor="#f4f1e9")
    grid = figure.add_gridspec(2, 2, left=0.075, right=0.955, top=0.75, bottom=0.12, hspace=0.42, wspace=0.28)

    relay_axis = figure.add_subplot(grid[0, 0])
    relay_axis.plot(range(12), south, color="#d17829", marker="o", linewidth=2.2, label="southern-gate input")
    relay_axis.plot(range(12), north, color="#23677a", marker="o", linewidth=2.2, label="northern-gate export")
    relay_axis.set_xticks(range(12), MONTHS, rotation=45)
    relay_axis.set_ylabel("heat power (TW)")
    relay_axis.set_title("A  SOUTH AND NORTH STRENGTHEN TOGETHER", loc="left", fontsize=10, fontweight="bold")
    relay_axis.legend(frameon=False, fontsize=8)
    relay_axis.spines[["top", "right"]].set_visible(False)
    relay_axis.text(0.04, 0.08, f"same-month r = {corr['southern_input_vs_northern_export']:.2f}", transform=relay_axis.transAxes, color="#183944", fontweight="bold")

    shift_axis = figure.add_subplot(grid[0, 1])
    shift_axis.bar(range(12), shifts, color=["#d17829"] + ["#78939a"] * 11)
    shift_axis.axhline(0, color="#8a989a", linewidth=0.7)
    shift_axis.set_xticks(range(12))
    shift_axis.set_xlabel("circular shift of northern series (months)")
    shift_axis.set_ylabel("correlation with southern input")
    shift_axis.set_ylim(-0.9, 0.9)
    shift_axis.set_title("B  SAME MONTH IS THE STRONGEST ALIGNMENT", loc="left", fontsize=10, fontweight="bold")
    shift_axis.spines[["top", "right"]].set_visible(False)

    storage_axis = figure.add_subplot(grid[1, 0])
    storage_axis.plot(range(12), surface, color="#6d8f9a", marker="o", linewidth=2, label="surface downward")
    storage_axis.plot(range(12), storage, color="#c28b3c", marker="o", linewidth=2, label="storage tendency")
    storage_axis.axhline(0, color="#8a989a", linewidth=0.7)
    storage_axis.set_xticks(range(12), MONTHS, rotation=45)
    storage_axis.set_ylabel("heat power (TW)")
    storage_axis.set_title("C  SURFACE FORCING TRACKS STORAGE", loc="left", fontsize=10, fontweight="bold")
    storage_axis.legend(frameon=False, fontsize=8)
    storage_axis.spines[["top", "right"]].set_visible(False)
    storage_axis.text(0.04, 0.08, f"same-month r = {corr['surface_downward_vs_storage_tendency']:.2f}", transform=storage_axis.transAxes, color="#183944", fontweight="bold")

    balance_axis = figure.add_subplot(grid[1, 1])
    labels = ("south\ninput", "north\nexport", "surface", "storage", "unresolved")
    values = (means["southern_gate_input_TW"], -means["northern_gate_export_TW"], means["surface_downward_TW"], means["storage_tendency_TW"], means["upwind_consistent_unresolved_remainder_TW"])
    balance_axis.bar(range(5), values, color=("#d17829", "#23677a", "#6d8f9a", "#c28b3c", "#9b9184"))
    balance_axis.axhline(0, color="#8a989a", linewidth=0.7)
    balance_axis.set_xticks(range(5), labels)
    balance_axis.set_ylabel("2018 time-mean power (TW)")
    balance_axis.set_title("D  THE RELAY'S ANNUAL ACCOUNTING", loc="left", fontsize=10, fontweight="bold")
    balance_axis.spines[["top", "right"]].set_visible(False)
    for index, value in enumerate(values):
        balance_axis.text(index, value + (8 if value >= 0 else -13), f"{value:+.1f}", ha="center", va="bottom" if value >= 0 else "top", fontsize=7.5, fontweight="bold")

    figure.text(0.045, 0.95, "THE NORDIC SEAS ACT LIKE A SEASONAL HEAT RELAY", fontsize=18.5, fontweight="bold", color="#183944")
    figure.text(0.045, 0.902, "Southern Atlantic-side convergence, northern export, surface exchange, and storage · 2018 monthly means", fontsize=9.5, color="#4c5d63")
    figure.text(0.045, 0.825, "Gateway input and export co-vary in the same month (r = 0.81), while surface forcing tracks storage even more closely (r = 0.98).", fontsize=10.2, color="#183944", fontweight="bold")
    figure.text(0.045, 0.038, "Twelve seasonally confounded months · circular shifts are timing contrasts, not a null test · association does not measure parcel transit or causality", fontsize=7.2, color="#68777b")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, format="svg", metadata={"Date": None})
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-heat-relay-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m4-oras5-nordic-heat-relay-2018.svg"))
    args = parser.parse_args()
    build(args.input, args.output)
    print(args.output.resolve())


if __name__ == "__main__":
    main()

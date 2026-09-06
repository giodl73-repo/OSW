"""Render paired inward/outward water and heat branches at Nordic gates."""

from __future__ import annotations

import argparse
import json
import pathlib

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


LABELS = ("DENMARK STRAIT", "ICELAND–SCOTLAND RIDGE", "NORTHERN NORTH SEA", "FRAM STRAIT", "NORWAY–SVALBARD")


def build(input_path: pathlib.Path, output_path: pathlib.Path) -> None:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    records = payload["time_weighted_2018"]
    y = np.arange(len(records))
    inward_heat = np.asarray([record["inward_heat_TW_at_0C"] for record in records])
    outward_heat = np.asarray([record["outward_heat_TW_at_0C"] for record in records])
    inward_temp = np.asarray([record["inward_effective_temperature_degC"] for record in records])
    outward_temp = np.asarray([record["outward_effective_temperature_degC"] for record in records])
    inward_volume = np.asarray([record["inward_volume_Sv"] for record in records])
    outward_volume = np.asarray([record["outward_volume_Sv"] for record in records])
    net_heat = inward_heat - outward_heat

    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.hashsalt": "osw-nordic-heat-exchange-anatomy-v1"})
    figure = plt.figure(figsize=(12.6, 6.7), facecolor="#f4f1e9")
    grid = figure.add_gridspec(1, 2, left=0.15, right=0.95, top=0.77, bottom=0.25, width_ratios=(1.45, 1), wspace=0.28)

    heat_axis = figure.add_subplot(grid[0, 0])
    heat_axis.barh(y, inward_heat, color="#d17829", height=0.34, label="heat entering")
    heat_axis.barh(y, -outward_heat, color="#2a7e91", height=0.34, label="heat leaving")
    heat_axis.axvline(0, color="#53656b", linewidth=0.8)
    heat_axis.set_yticks(y, LABELS)
    heat_axis.invert_yaxis()
    heat_axis.set_xlabel("gross branch heat transport at 0°C reference (TW)")
    heat_axis.set_title("A  LARGE OPPOSING HEAT STREAMS", loc="left", fontweight="bold")
    heat_axis.spines[["top", "right", "left"]].set_visible(False)
    heat_axis.legend(loc="lower center", bbox_to_anchor=(0.5, -0.28), ncol=2, frameon=False)
    for row, (incoming, outgoing, net) in enumerate(zip(inward_heat, outward_heat, net_heat)):
        heat_axis.text(incoming + 8, row, f"net {net:+.0f}", va="center", fontsize=7.5, color="#334d56")

    temp_axis = figure.add_subplot(grid[0, 1])
    for row, (incoming, outgoing) in enumerate(zip(inward_temp, outward_temp)):
        temp_axis.plot([incoming, outgoing], [row, row], color="#aeb8b8", linewidth=2, zorder=1)
    temp_axis.scatter(inward_temp, y, color="#d17829", s=55, label="entering donor water", zorder=2)
    temp_axis.scatter(outward_temp, y, color="#2a7e91", s=55, label="leaving donor water", zorder=2)
    temp_axis.set_yticks(y, [f"{iv:.1f} in / {ov:.1f} out Sv" for iv, ov in zip(inward_volume, outward_volume)])
    temp_axis.invert_yaxis()
    temp_axis.set_xlabel("transport-weighted donor temperature (°C)")
    temp_axis.set_title("B  DIRECTION SELECTS TEMPERATURE", loc="left", fontweight="bold")
    temp_axis.spines[["top", "right", "left"]].set_visible(False)
    temp_axis.legend(loc="lower center", bbox_to_anchor=(0.5, -0.32), ncol=1, frameon=False)
    temp_axis.grid(axis="x", color="#d8d5cc", linewidth=0.6)

    figure.text(0.045, 0.935, "EACH GATE IS TWO RIVERS, NOT ONE ARROW", fontsize=19, fontweight="bold", color="#183944")
    figure.text(0.045, 0.89, "Time-weighted 2018 monthly means · upstream donor temperature · branch magnitudes shown separately", fontsize=9.5, color="#4c5d63")
    figure.text(0.045, 0.825, "Heat direction depends on which temperature travels with each opposing current—not simply on net water flow.", fontsize=10.5, color="#183944", fontweight="bold")
    figure.text(0.045, 0.05, "One ORAS5 member and year · monthly donor sampling is not native FCT/TVD or submonthly covariance · 0°C reference heat is meaningful here because whole-room volume nearly closes", fontsize=7.2, color="#68777b")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, format="svg", metadata={"Date": None})
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-heat-exchange-anatomy-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m4-oras5-nordic-heat-exchange-anatomy-2018.svg"))
    args = parser.parse_args()
    build(args.input, args.output)
    print(args.output.resolve())


if __name__ == "__main__":
    main()

"""Render the five-section full-depth anatomy of the Nordic Seas control volume."""

from __future__ import annotations

import json
import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


ROOT = pathlib.Path(__file__).resolve().parents[1]
INPUT = ROOT / "research/osw-m4-oras5-nordic-section-geometry-audit.json"
OUTPUT = ROOT / "figures/osw-m4-oras5-nordic-section-geometry.svg"
COLORS = ("#b6e0e5", "#7fc4ce", "#3e9eac", "#217381", "#164c5a", "#0b303b")
LABELS = ("0–100", "100–300", "300–700", "700–1500", "1500–3000", ">3000 m")


def main():
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    sections = payload["sections"]
    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.hashsalt": "osw-nordic-section-geometry-v1"})
    figure, (area_axis, depth_axis) = plt.subplots(1, 2, figsize=(12.8, 7.2), gridspec_kw={"width_ratios": (1.45, 1)}, facecolor="#f6f3ec")
    figure.subplots_adjust(left=0.08, right=0.96, top=0.79, bottom=0.19, wspace=0.28)
    names = [section["name"].replace(" model closure", "").replace(" continuous", "") for section in sections]
    y = np.arange(len(sections))
    left = np.zeros(len(sections))
    for index, (color, label) in enumerate(zip(COLORS, LABELS)):
        values = np.array([section["depth_bins"][index]["area_m2"] / 1e6 for section in sections])
        area_axis.barh(y, values, left=left, color=color, edgecolor="#f6f3ec", linewidth=0.8, label=label)
        left += values
    area_axis.set_yticks(y, names)
    area_axis.invert_yaxis()
    area_axis.set_xlabel("wet cross-sectional area (km²)")
    area_axis.set_title("A  THE FIVE OPENINGS ARE NOT FIVE EQUAL DOORS", loc="left", fontweight="bold")
    area_axis.spines[["top", "right"]].set_visible(False)
    for row, total in zip(y, left):
        area_axis.text(total + 10, row, f"{total:,.0f}", va="center", fontsize=8, color="#334d56")
    area_axis.legend(ncol=3, loc="lower left", bbox_to_anchor=(0, -0.28), frameon=False, fontsize=8, title="reference-level depth bin (m)")

    maxima = np.array([section["column_depth_m"]["maximum"] for section in sections])
    depth_axis.barh(y, maxima, color="#087f8c", height=0.58)
    depth_axis.set_yticks(y, [section["id"].replace("_", " ").upper() for section in sections])
    depth_axis.invert_yaxis()
    depth_axis.set_xlabel("maximum wet column depth (m)")
    depth_axis.set_title("B  ONLY FRAM IS A DEEP GATE", loc="left", fontweight="bold")
    depth_axis.spines[["top", "right"]].set_visible(False)
    for row, value in zip(y, maxima):
        depth_axis.text(value + 45, row, f"{value:,.0f} m", va="center", fontsize=8, color="#334d56")
    depth_axis.set_xlim(0, max(maxima) * 1.18)

    figure.suptitle("THE CLOSED ROOM NOW HAS DEPTH", x=0.06, y=0.96, ha="left", fontsize=19, fontweight="bold", color="#18343d")
    figure.text(0.06, 0.905, "1,816 km² of total wet boundary area · Fram supplies 814 km² and 60% of its area lies below 700 m.", fontsize=10, color="#4c5d63")
    figure.text(0.06, 0.855, "Denmark Strait reaches 662 m · Iceland–Scotland 971 m · North Sea 285 m · Norway–Svalbard 432 m.", fontsize=9, color="#4c5d63")
    figure.text(0.06, 0.025, "Adjacent-minimum ORCA025 partial-step reconstruction · internal mask/area consistency pass, not independent production-thickness validation or transport", fontsize=7.5, color="#5e6c71")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, format="svg", facecolor=figure.get_facecolor(), metadata={"Date": None}, bbox_inches="tight")
    plt.close(figure)
    text = OUTPUT.read_text(encoding="utf-8")
    OUTPUT.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8", newline="\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()

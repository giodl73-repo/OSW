"""Render the monthly Nordic Seas partial heat budget and gate contributions."""

from __future__ import annotations

import calendar
import json
import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


ROOT = pathlib.Path(__file__).resolve().parents[1]
INPUT = ROOT / "research/osw-m4-oras5-nordic-partial-budget-2018.json"
OUTPUT = ROOT / "figures/osw-m4-oras5-nordic-partial-budget-2018.svg"


def main():
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    records = payload["months"]
    weights = np.array([calendar.monthrange(int(record["month"][:4]), int(record["month"][4:]))[1] for record in records], dtype=float)
    storage = np.array([record["storage_tendency_TW"]["0.0"] for record in records])
    convergence = np.array([-record["boundary_totals"]["outward_heat_TW"]["0.0"] for record in records])
    surface = np.array([record["surface_downward_TW"] for record in records])
    remainder = np.array([record["unresolved_remainder_TW"]["0.0"] for record in records])
    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.hashsalt": "osw-nordic-partial-budget-v1"})
    figure = plt.figure(figsize=(12.8, 7.2), facecolor="#f6f3ec")
    grid = figure.add_gridspec(1, 2, width_ratios=(1.55, 1), left=0.07, right=0.96, top=0.79, bottom=0.22, wspace=0.27)
    month_axis = figure.add_subplot(grid[0, 0]); gate_axis = figure.add_subplot(grid[0, 1])
    x = np.arange(12)
    month_axis.axhline(0, color="#526269", linewidth=0.7)
    month_axis.plot(x, storage, color="#18343d", marker="o", linewidth=2.3, label="storage tendency")
    month_axis.plot(x, convergence, color="#d0762d", marker="o", linewidth=1.8, label="advective convergence")
    month_axis.plot(x, surface, color="#27778a", marker="o", linewidth=1.8, label="downward surface heat")
    month_axis.plot(x, remainder, color="#8a5b8e", marker="o", linewidth=1.5, linestyle="--", label="unresolved remainder")
    month_axis.set_xticks(x, ("J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"))
    month_axis.set_ylabel("heat-budget term (TW)")
    month_axis.set_title("A  STORAGE FOLLOWS A LARGE SEASONAL BREATH", loc="left", fontweight="bold")
    month_axis.spines[["top", "right"]].set_visible(False)
    month_axis.legend(frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(0.5, -0.22))

    section_names = [section["id"].replace("_", " ").upper() for section in records[0]["sections"]]
    section_convergence = []
    section_volume = []
    for index in range(len(section_names)):
        section_convergence.append(float(np.average([-record["sections"][index]["outward_heat_TW"]["0.0"] for record in records], weights=weights)))
        section_volume.append(float(np.average([-record["sections"][index]["outward_volume_Sv"] for record in records], weights=weights)))
    y = np.arange(len(section_names))
    colors = ["#d0762d" if value >= 0 else "#27778a" for value in section_convergence]
    gate_axis.barh(y, section_convergence, color=colors, height=0.6)
    gate_axis.axvline(0, color="#526269", linewidth=0.7)
    gate_axis.set_yticks(y, section_names)
    gate_axis.invert_yaxis()
    gate_axis.set_xlabel("time-weighted advective heat convergence (TW)")
    gate_axis.set_title("B  RIDGE IMPORT DOMINATES; NORTH AND EAST EXPORT", loc="left", fontweight="bold")
    gate_axis.spines[["top", "right"]].set_visible(False)
    for row, (heat, volume) in enumerate(zip(section_convergence, section_volume)):
        gate_axis.text(heat + (5 if heat >= 0 else -5), row, f"{heat:+.0f} TW\n{volume:+.2f} Sv in", ha="left" if heat >= 0 else "right", va="center", fontsize=7.5, color="#334d56")
    gate_axis.set_xlim(min(section_convergence) - 85, max(section_convergence) + 55)

    mean_convergence = float(np.average(convergence, weights=weights))
    mean_surface = float(np.average(surface, weights=weights))
    mean_remainder = float(np.average(remainder, weights=weights))
    figure.suptitle("HEAT ENTERS—BUT THE OFFLINE ROOM BUDGET DOES NOT CLOSE", x=0.06, y=0.96, ha="left", fontsize=17, fontweight="bold", color="#18343d")
    figure.text(0.06, 0.905, f"2018 monthly means at 0°C reference · +{mean_convergence:.1f} TW advective convergence · {mean_surface:+.1f} TW surface input · {mean_remainder:+.1f} TW mean unresolved remainder", fontsize=9.5, color="#4c5d63")
    figure.text(0.06, 0.855, "Whole-room mass imbalance stays within −0.064 to +0.074 Sv. Small is not zero; all reference-temperature cases remain in the receipt.", fontsize=9, color="#4c5d63")
    figure.text(0.06, 0.02, "One ORAS5 member and year · monthly-mean offline velocity × adjacent-mean temperature · finite-difference storage · remainder retains ice, mixing, diffusion, assimilation, and numerical error", fontsize=7.3, color="#5e6c71")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, format="svg", facecolor=figure.get_facecolor(), metadata={"Date": None}, bbox_inches="tight")
    plt.close(figure)
    text = OUTPUT.read_text(encoding="utf-8")
    OUTPUT.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8", newline="\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()

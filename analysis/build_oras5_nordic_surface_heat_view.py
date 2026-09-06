"""Render the spatial and monthly ORAS5 surface heat exchange over the Nordic room."""

from __future__ import annotations

import calendar
import json
import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt
import netCDF4
import numpy as np


ROOT = pathlib.Path(__file__).resolve().parents[1]
MESH = ROOT / "atlas/data/oras5-nordic-seas-mesh.nc"
HEAT = ROOT / "atlas/data/oras5-nordic-surface-heat-2018.nc"
CONTROL = ROOT / "research/osw-m4-oras5-nordic-control-volume.json"
ANALYSIS = ROOT / "research/osw-m4-oras5-nordic-surface-heat-2018.json"
OUTPUT = ROOT / "figures/osw-m4-oras5-nordic-surface-heat-2018.svg"


def main():
    control = json.loads(CONTROL.read_text(encoding="utf-8"))
    analysis = json.loads(ANALYSIS.read_text(encoding="utf-8"))
    with netCDF4.Dataset(MESH) as dataset:
        lon = ((np.asarray(dataset.variables["glamt"][:], dtype=float) + 180) % 360) - 180
        lat = np.asarray(dataset.variables["gphit"][:], dtype=float)
        water = np.asarray(dataset.variables["tmask"][0], dtype=bool)
    with netCDF4.Dataset(HEAT) as dataset:
        months = np.asarray(dataset.variables["month"][:], dtype=int)
        flux = np.ma.filled(dataset.variables["sohefldo"][:], np.nan).astype(float)
    days = np.array([calendar.monthrange(month // 100, month % 100)[1] for month in months], dtype=float)
    annual = np.average(flux, axis=0, weights=days)
    inside = np.zeros(water.shape, dtype=bool)
    indices = np.asarray(control["inside_t_cells"], dtype=int)
    inside[indices[:, 0], indices[:, 1]] = True
    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.hashsalt": "osw-nordic-surface-heat-v1"})
    figure = plt.figure(figsize=(12.8, 7.2), facecolor="#f6f3ec")
    grid = figure.add_gridspec(1, 2, width_ratios=(1.4, 1), left=0.07, right=0.96, top=0.80, bottom=0.15, wspace=0.25)
    map_axis = figure.add_subplot(grid[0, 0]); month_axis = figure.add_subplot(grid[0, 1])
    map_axis.scatter(lon[water][::4], lat[water][::4], s=1.2, color="#dfeaed", linewidths=0, zorder=1)
    limit = 180.0
    points = map_axis.scatter(lon[inside], lat[inside], c=annual[inside], s=4.8, cmap="RdBu_r", vmin=-limit, vmax=limit, linewidths=0, zorder=2)
    map_axis.scatter(lon[~water][::3], lat[~water][::3], s=2, color="#faf9f5", linewidths=0, zorder=3)
    for section in control["sections"]:
        faces = section["faces"]
        map_axis.plot([face["longitude_deg"] for face in faces], [face["latitude_deg"] for face in faces], color="#173f4a", linewidth=1.25, zorder=4)
    map_axis.set_xlim(-40, 31); map_axis.set_ylim(56, 84); map_axis.set_aspect(1.55)
    map_axis.set_xlabel("longitude"); map_axis.set_ylabel("latitude")
    map_axis.set_title("A  WHERE THE OCEAN LOSES AND GAINS HEAT", loc="left", fontweight="bold")
    map_axis.spines[["top", "right"]].set_visible(False)
    colorbar = figure.colorbar(points, ax=map_axis, orientation="horizontal", pad=0.12, fraction=0.045)
    colorbar.set_label("2018 time-weighted mean net downward surface heat flux (W/m²)")

    powers = np.array([record["integrated_downward_power_TW"] for record in analysis["months"]])
    x = np.arange(12)
    colors = np.where(powers >= 0, "#d9782d", "#27778a")
    month_axis.bar(x, powers, color=colors, width=0.72)
    month_axis.axhline(0, color="#18343d", linewidth=0.8)
    month_axis.set_xticks(x, ("J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"))
    month_axis.set_ylabel("integrated downward surface power (TW)")
    month_axis.set_title("B  SUMMER UPTAKE, LONGER COOLING SEASON", loc="left", fontweight="bold")
    month_axis.spines[["top", "right"]].set_visible(False)
    month_axis.text(0.03, 0.04, "orange = into ocean\nblue = out of ocean", transform=month_axis.transAxes, color="#526269", fontsize=8)
    for index in (2, 6):
        month_axis.text(index, powers[index] + (18 if powers[index] >= 0 else -18), f"{powers[index]:+.0f}", ha="center", va="bottom" if powers[index] >= 0 else "top", fontsize=8, fontweight="bold")

    annual_power = analysis["time_weighted_2018"]["integrated_downward_power_TW"]
    annual_flux = analysis["time_weighted_2018"]["area_mean_flux_W_m2"]
    annual_energy = analysis["time_weighted_2018"]["net_downward_energy_ZJ"]
    figure.suptitle("THE ROOM BREATHES HEAT THROUGH ITS SURFACE", x=0.06, y=0.965, ha="left", fontsize=19, fontweight="bold", color="#18343d")
    figure.text(0.06, 0.91, f"2018 ORAS5 forcing · {annual_flux:+.1f} W/m² · {annual_power:+.1f} TW · {annual_energy:+.2f} ZJ net downward (negative = ocean heat loss)", fontsize=10, color="#4c5d63")
    figure.text(0.06, 0.855, "Four warming months and eight cooling months. This is surface exchange—not advective convergence, storage, or a complete heat budget.", fontsize=9, color="#4c5d63")
    figure.text(0.06, 0.02, "One ORAS5 member · twelve 2018 monthly means · exact 12,550-cell native mask and e1t×e2t area · not a climatology or observation-only estimate", fontsize=7.5, color="#5e6c71")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, format="svg", facecolor=figure.get_facecolor(), metadata={"Date": None}, bbox_inches="tight")
    plt.close(figure)
    text = OUTPUT.read_text(encoding="utf-8")
    OUTPUT.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8", newline="\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()

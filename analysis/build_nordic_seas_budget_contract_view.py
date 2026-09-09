"""Render the native-grid Nordic Seas heat-room contract."""

from __future__ import annotations

import json
import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt
import netCDF4
import numpy as np


ROOT = pathlib.Path(__file__).resolve().parents[1]
MESH = ROOT / "atlas/data/oras5-nordic-seas-mesh.nc"
CONTRACT = ROOT / "research/osw-m4-nordic-seas-budget-contract.json"
CONTROL = ROOT / "research/osw-m4-oras5-nordic-control-volume.json"
OUTPUT = ROOT / "figures/osw-m4-nordic-seas-budget-contract.svg"


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    control = json.loads(CONTROL.read_text(encoding="utf-8"))
    with netCDF4.Dataset(MESH) as dataset:
        lon = np.asarray(dataset.variables["glamt"][:], dtype=float)
        lat = np.asarray(dataset.variables["gphit"][:], dtype=float)
        water = np.asarray(dataset.variables["tmask"][0, :, :], dtype=bool)
    lon = ((lon + 180.0) % 360.0) - 180.0
    inside = np.zeros_like(water, dtype=bool)
    indices = np.asarray(control["inside_t_cells"], dtype=int)
    inside[indices[:, 0], indices[:, 1]] = True

    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.hashsalt": "osw-nordic-seas-budget-contract-v1"})
    figure = plt.figure(figsize=(12.8, 7.6), facecolor="#f6f3ec")
    grid = figure.add_gridspec(1, 2, width_ratios=(1.55, 1.0), wspace=0.15)
    map_axis = figure.add_subplot(grid[0, 0])
    gate_axis = figure.add_subplot(grid[0, 1])

    map_axis.scatter(lon[water][::3], lat[water][::3], s=2.2, color="#dbeaf0", linewidths=0, zorder=1)
    map_axis.scatter(lon[inside][::2], lat[inside][::2], s=4.0, color="#abd8df", linewidths=0, zorder=2)
    map_axis.scatter(lon[~water][::3], lat[~water][::3], s=2.4, color="#faf9f5", linewidths=0, zorder=2)
    for section in control["sections"]:
        faces = section["faces"]
        map_axis.plot([face["longitude_deg"] for face in faces], [face["latitude_deg"] for face in faces], color="#087f8c", linewidth=2.5, zorder=5)
    for section in contract["control_volume"]["gateway_intents"]:
        start, stop = section["from"], section["to"]
        map_axis.plot([start["longitude_deg"], stop["longitude_deg"]], [start["latitude_deg"], stop["latitude_deg"]], color="#d0762d", linewidth=1.0, linestyle=(0, (2, 3)), alpha=0.55, zorder=4)
    map_axis.text(-2, 79.8, "FRAM", color="#075f69", fontweight="bold", fontsize=9)
    map_axis.text(21, 73.8, "BARENTS\nCLOSURE", color="#075f69", fontweight="bold", fontsize=9, ha="left")
    map_axis.text(-27, 65.2, "DENMARK", color="#075f69", fontweight="bold", fontsize=8, ha="center")
    map_axis.text(-9, 60.7, "ICELAND–SCOTLAND RIDGE", color="#075f69", fontweight="bold", fontsize=7, ha="center")
    map_axis.text(1.2, 58.0, "NORTH SEA", color="#075f69", fontweight="bold", fontsize=7, ha="center")
    map_axis.text(-5, 69.0, "NORDIC SEAS\nHEAT ROOM", ha="center", va="center", fontsize=15, fontweight="bold", color="#234a59")
    map_axis.set_xlim(-42, 35)
    map_axis.set_ylim(56, 84)
    map_axis.set_aspect(1.65)
    map_axis.set_xlabel("longitude")
    map_axis.set_ylabel("latitude")
    map_axis.set_title("A  THE BOUNDARY MUST CLOSE BEFORE THE HEAT CAN", loc="left", fontweight="bold")
    map_axis.spines[["top", "right"]].set_visible(False)

    gate_axis.set_xlim(0, 1)
    gate_axis.set_ylim(-1.1, len(contract["readiness"]) + 1.5)
    gate_axis.axis("off")
    summary = contract["readiness_summary"]
    gate_axis.set_title(f"B  READINESS · {summary['pass']} PASS / {summary['open']} OPEN", loc="left", fontweight="bold")
    palette = {"pass": ("#087f8c", "PASS"), "open": ("#d0762d", "OPEN"), "blocked": ("#a33d3d", "BLOCKED")}
    for index, item in enumerate(contract["readiness"]):
        y = len(contract["readiness"]) - index
        color, word = palette[item["status"]]
        gate_axis.text(0.0, y, word, color=color, fontweight="bold", fontsize=8, va="center")
        gate_axis.text(0.18, y + 0.13, item["label"], color="#18343d", fontweight="bold", fontsize=9, va="center")
        gate_axis.text(0.18, y - 0.18, item["reason"], color="#526269", fontsize=7.2, va="top", wrap=True)
    gate_axis.text(0, -0.95, "storage + outward advection − downward surface heat\n= unresolved ice + mixing + diffusion + assimilation + error", fontsize=9, color="#18343d", fontweight="bold", va="bottom")

    figure.suptitle("THE NORDIC SEAS NOW CLOSES AS ONE OCEAN ROOM", x=0.06, y=0.975, ha="left", fontsize=18, fontweight="bold", color="#18343d")
    figure.text(0.06, 0.93, "12,550 wet surface cells · 284 unique boundary faces · every wet opening is explicit, including the northern North Sea.", fontsize=9.5, color="#4c5d63")
    figure.text(0.06, 0.018, "Native ORCA025 geometry, twelve-month state, and surface forcing · faint orange shows the rejected Faroe split · native tracer-budget terms remain open", fontsize=7.5, color="#5e6c71")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, format="svg", facecolor=figure.get_facecolor(), metadata={"Date": None}, bbox_inches="tight")
    plt.close(figure)
    text = OUTPUT.read_text(encoding="utf-8")
    OUTPUT.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8", newline="\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()

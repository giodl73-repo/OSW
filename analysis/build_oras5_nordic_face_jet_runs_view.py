"""Map contiguous same-sign Nordic boundary heat-jet runs."""

from __future__ import annotations

import argparse
import json
import pathlib

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np

from build_oras5_nordic_face_intensity_bakeoff_view import background


MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
SHORT = {"denmark_strait": "DEN", "iceland_scotland_ridge": "ISR", "northern_north_sea": "NNS", "fram_strait": "FRA", "norway_svalbard": "NSV"}
INWARD, OUTWARD = "#d17829", "#23677a"


def build(input_path: pathlib.Path, control_path: pathlib.Path, mesh_path: pathlib.Path, output_path: pathlib.Path) -> None:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    ranked = sorted(payload["runs"], key=lambda run: abs(run["net_heat_convergence_TW_at_0C"]), reverse=True)
    top = ranked[:10]
    inward = payload["summary"]["strongest_inward_run"]
    outward = payload["summary"]["strongest_outward_run"]
    lon, lat, field = background(control_path, mesh_path)

    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "svg.hashsalt": "osw-nordic-face-jet-runs-v1"})
    figure = plt.figure(figsize=(12.6, 8.0), facecolor="#f4f1e9")
    grid = figure.add_gridspec(2, 2, left=0.065, right=0.955, top=0.77, bottom=0.115, width_ratios=(1.45, 1), hspace=0.42, wspace=0.3)
    map_axis = figure.add_subplot(grid[:, 0])
    map_axis.pcolormesh(lon, lat, field, shading="auto", cmap=ListedColormap(("#faf9f5", "#edf3f4", "#d5e8eb")), vmin=0, vmax=2, rasterized=True, zorder=1)
    for run in payload["runs"]:
        coords = run["faces"]
        map_axis.plot([face["longitude_deg"] for face in coords], [face["latitude_deg"] for face in coords], color="#aab7b9", linewidth=0.8, marker="o", markersize=1.5, zorder=2)
    peak = max(abs(run["net_heat_convergence_TW_at_0C"]) for run in top)
    for rank, run in reversed(list(enumerate(top, 1))):
        coords = run["faces"]
        color = INWARD if run["sign"] == "inward_heat" else OUTWARD
        width = 2 + 6 * abs(run["net_heat_convergence_TW_at_0C"]) / peak
        map_axis.plot([face["longitude_deg"] for face in coords], [face["latitude_deg"] for face in coords], color=color, linewidth=width, solid_capstyle="round", marker="o", markersize=width * 0.65, markeredgecolor="#f4f1e9", markeredgewidth=0.4, zorder=4)
    map_axis.set_xlim(-42, 35); map_axis.set_ylim(56, 84); map_axis.set_aspect(1.65)
    map_axis.set_xlabel("longitude"); map_axis.set_ylabel("latitude")
    map_axis.set_title("A  THE TEN STRONGEST CONNECTED RUNS", loc="left", fontsize=10, fontweight="bold")
    map_axis.spines[["top", "right"]].set_visible(False)

    bar_axis = figure.add_subplot(grid[0, 1])
    values = np.asarray([run["net_heat_convergence_TW_at_0C"] for run in top])[::-1]
    labels = [f"{rank:02d} {SHORT[run['section_id']]} · {run['face_count']} faces" for rank, run in enumerate(top, 1)][::-1]
    bar_axis.barh(range(10), values, color=[INWARD if value > 0 else OUTWARD for value in values])
    bar_axis.axvline(0, color="#7d898b", linewidth=0.7)
    bar_axis.set_yticks(range(10), labels)
    bar_axis.set_xlabel("net heat convergence (TW)")
    bar_axis.set_title("B  TEN RUNS CARRY HALF OF GROSS EXCHANGE", loc="left", fontsize=10, fontweight="bold")
    bar_axis.spines[["top", "right"]].set_visible(False)

    month_axis = figure.add_subplot(grid[1, 1])
    month_axis.plot(range(12), inward["monthly_net_heat_convergence_TW_at_0C"], color=INWARD, marker="o", linewidth=2, label=f"compact ISR import · {inward['face_count']} faces")
    month_axis.plot(range(12), outward["monthly_net_heat_convergence_TW_at_0C"], color=OUTWARD, marker="o", linewidth=2, label=f"broad NSV export · {outward['face_count']} faces")
    month_axis.axhline(0, color="#7d898b", linewidth=0.7)
    month_axis.set_xticks(range(12), MONTHS, rotation=45)
    month_axis.set_ylabel("net heat convergence (TW)")
    month_axis.set_title("C  OPPOSITE STRUCTURES, PERSISTENT SIGNS", loc="left", fontsize=10, fontweight="bold")
    month_axis.legend(frameon=False, fontsize=7.5, loc="lower left")
    month_axis.spines[["top", "right"]].set_visible(False)

    figure.text(0.045, 0.955, "THE STRONGEST FACES ASSEMBLE INTO PERSISTENT JETS", fontsize=18.5, fontweight="bold", color="#183944")
    figure.text(0.045, 0.91, "Maximal same-sign runs along each ordered native boundary · orange enters the Nordic room · blue leaves", fontsize=9.5, color="#4c5d63")
    figure.text(0.045, 0.84, "A compact 4-face Atlantic core carries +106.5 TW; a broad 33-face Norway–Svalbard band carries −72.0 TW. Both keep their sign all year.", fontsize=10.2, color="#183944", fontweight="bold")
    figure.text(0.045, 0.035, "Annual-sign segmentation yields 95 runs, including 51 single-face runs · descriptive connected components, not objectively identified currents", fontsize=7.2, color="#68777b")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, format="svg", metadata={"Date": None})
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-face-jet-runs-2018.json"))
    parser.add_argument("--control", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-control-volume.json"))
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-nordic-seas-mesh.nc"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m4-oras5-nordic-face-jet-runs-2018.svg"))
    args = parser.parse_args()
    build(args.input, args.control, args.mesh, args.output)
    print(args.output.resolve())


if __name__ == "__main__":
    main()

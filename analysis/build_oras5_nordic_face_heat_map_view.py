"""Map annual heat convergence on all 284 Nordic boundary faces."""

from __future__ import annotations

import argparse
import json
import pathlib

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, TwoSlopeNorm
import netCDF4
import numpy as np


def build(input_path: pathlib.Path, control_path: pathlib.Path, mesh_path: pathlib.Path, output_path: pathlib.Path) -> None:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    control = json.loads(control_path.read_text(encoding="utf-8"))
    with netCDF4.Dataset(mesh_path) as dataset:
        lon = np.asarray(dataset.variables["glamt"][:], dtype=float)
        lat = np.asarray(dataset.variables["gphit"][:], dtype=float)
        water = np.asarray(dataset.variables["tmask"][0], dtype=bool)
    lon = ((lon + 180) % 360) - 180
    inside = np.zeros_like(water); cells = np.asarray(control["inside_t_cells"], dtype=int); inside[cells[:, 0], cells[:, 1]] = True
    faces = [face | {"section_id": section["id"]} for section in payload["sections"] for face in section["faces"]]
    values = np.asarray([face["net_heat_convergence_TW_at_0C"] for face in faces])
    face_lon = np.asarray([face["longitude_deg"] for face in faces]); face_lat = np.asarray([face["latitude_deg"] for face in faces])
    ranked = np.sort(np.abs(values))[::-1]; cumulative = np.cumsum(ranked) / np.sum(ranked)
    summary = payload["summary"]

    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.hashsalt": "osw-nordic-face-heat-map-v1"})
    figure = plt.figure(figsize=(12.6, 7.0), facecolor="#f4f1e9")
    grid = figure.add_gridspec(1, 2, left=0.065, right=0.95, top=0.78, bottom=0.16, width_ratios=(1.55, 0.9), wspace=0.32)
    map_axis = figure.add_subplot(grid[0, 0])
    background = np.where(inside, 2, np.where(water, 1, 0))
    map_axis.pcolormesh(lon, lat, background, shading="auto", cmap=ListedColormap(("#faf9f5", "#edf3f4", "#d5e8eb")), vmin=0, vmax=2, rasterized=True, zorder=1)
    limit = float(max(abs(values.min()), abs(values.max())))
    cmap = LinearSegmentedColormap.from_list("osw_heat", ("#23677a", "#f5f2ea", "#d17829"))
    sizes = 14 + 115 * np.sqrt(np.abs(values) / limit)
    points = map_axis.scatter(face_lon, face_lat, c=values, s=sizes, cmap=cmap, norm=TwoSlopeNorm(vmin=-limit, vcenter=0, vmax=limit), edgecolor="#f4f1e9", linewidth=0.45, zorder=5)
    label_box = {"facecolor": "#f4f1e9", "edgecolor": "none", "alpha": 0.86, "pad": 1.2}
    map_axis.text(-28, 65.0, "DENMARK", fontsize=7.5, fontweight="bold", ha="center", bbox=label_box, zorder=7)
    map_axis.text(-10, 58.5, "ICELAND–SCOTLAND", fontsize=7.5, fontweight="bold", ha="center", bbox=label_box, zorder=7)
    map_axis.text(1, 57.2, "NORTH SEA", fontsize=7, fontweight="bold", ha="center", bbox=label_box, zorder=7)
    map_axis.text(-2, 80.6, "FRAM", fontsize=7.5, fontweight="bold", ha="center", bbox=label_box, zorder=7)
    map_axis.text(23, 74.2, "NORWAY–SVALBARD", fontsize=7, fontweight="bold", ha="center", bbox=label_box, zorder=7)
    map_axis.set_xlim(-42, 35); map_axis.set_ylim(56, 84); map_axis.set_aspect(1.65)
    map_axis.set_xlabel("longitude"); map_axis.set_ylabel("latitude")
    map_axis.set_title("A  HEAT ENTERS AND LEAVES SIDE BY SIDE", loc="left", fontweight="bold")
    map_axis.spines[["top", "right"]].set_visible(False)
    colorbar = figure.colorbar(points, ax=map_axis, fraction=0.035, pad=0.025)
    colorbar.ax.set_title("TW", fontsize=8, pad=4)

    rank_axis = figure.add_subplot(grid[0, 1])
    rank_axis.plot(np.arange(1, len(ranked) + 1), 100 * cumulative, color="#183944", linewidth=2)
    for count in (10, 20, 50, 100):
        share = 100 * cumulative[count - 1]
        rank_axis.scatter([count], [share], color="#d17829", s=35, zorder=3)
        rank_axis.text(count + 4, share, f"{count} faces · {share:.0f}%", va="center", fontsize=8, color="#334d56")
    rank_axis.axhline(50, color="#b8b2a6", linewidth=0.7, linestyle="--")
    rank_axis.set_xlim(0, 284); rank_axis.set_ylim(0, 103)
    rank_axis.set_xlabel("faces ranked by absolute heat contribution")
    rank_axis.set_ylabel("cumulative share of gross exchange (%)")
    rank_axis.set_title("B  TWENTY FACES CARRY HALF", loc="left", fontweight="bold")
    rank_axis.spines[["top", "right"]].set_visible(False)
    rank_axis.text(0.04, 0.18, f"gross |face heat|  {summary['gross_absolute_face_heat_TW']:.0f} TW\nnet convergence  {summary['net_face_heat_convergence_TW']:.0f} TW\nopposing cancellation  {100 * summary['opposing_face_cancellation_fraction']:.0f}%", transform=rank_axis.transAxes, fontsize=9, color="#183944", linespacing=1.5)

    figure.text(0.045, 0.945, "THE GATES ARE INTERLEAVED HEAT JETS", fontsize=19, fontweight="bold", color="#183944")
    figure.text(0.045, 0.9, "All 284 native boundary faces · time-weighted 2018 monthly upwind-donor sensitivity · symbol area scales with |TW|", fontsize=9.5, color="#4c5d63")
    figure.text(0.045, 0.84, "Many more faces export than import heat, but a compact set of powerful Atlantic inflow faces dominates the net.", fontsize=10.5, color="#183944", fontweight="bold")
    figure.text(0.045, 0.035, "Face totals reflect width, depth, velocity, and donor temperature · not flux density · monthly donor sampling is not native FCT/TVD or submonthly covariance", fontsize=7.2, color="#68777b")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, format="svg", metadata={"Date": None})
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-face-heat-map-2018.json"))
    parser.add_argument("--control", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-control-volume.json"))
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-nordic-seas-mesh.nc"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m4-oras5-nordic-face-heat-map-2018.svg"))
    args = parser.parse_args(); build(args.input, args.control, args.mesh, args.output); print(args.output.resolve())


if __name__ == "__main__":
    main()

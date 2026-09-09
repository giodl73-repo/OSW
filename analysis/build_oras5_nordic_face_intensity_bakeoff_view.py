"""Compare total face heat transport with area-normalized jet intensity."""

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


def background(control_path: pathlib.Path, mesh_path: pathlib.Path):
    control = json.loads(control_path.read_text(encoding="utf-8"))
    with netCDF4.Dataset(mesh_path) as dataset:
        lon = np.asarray(dataset.variables["glamt"][:], dtype=float)
        lat = np.asarray(dataset.variables["gphit"][:], dtype=float)
        water = np.asarray(dataset.variables["tmask"][0], dtype=bool)
    lon = ((lon + 180) % 360) - 180
    inside = np.zeros_like(water); cells = np.asarray(control["inside_t_cells"], dtype=int); inside[cells[:, 0], cells[:, 1]] = True
    return lon, lat, np.where(inside, 2, np.where(water, 1, 0))


def draw_map(axis, lon, lat, field, face_lon, face_lat, values, sizes, title, unit):
    axis.pcolormesh(lon, lat, field, shading="auto", cmap=ListedColormap(("#faf9f5", "#edf3f4", "#d5e8eb")), vmin=0, vmax=2, rasterized=True, zorder=1)
    limit = float(max(abs(values.min()), abs(values.max())))
    cmap = LinearSegmentedColormap.from_list("osw_heat", ("#23677a", "#f5f2ea", "#d17829"))
    points = axis.scatter(face_lon, face_lat, c=values, s=sizes, cmap=cmap, norm=TwoSlopeNorm(vmin=-limit, vcenter=0, vmax=limit), edgecolor="#f4f1e9", linewidth=0.4, zorder=4)
    axis.set_xlim(-42, 35); axis.set_ylim(56, 84); axis.set_aspect(1.65)
    axis.set_xlabel("longitude"); axis.set_ylabel("latitude"); axis.set_title(title, loc="left", fontweight="bold")
    axis.spines[["top", "right"]].set_visible(False)
    colorbar = axis.figure.colorbar(points, ax=axis, fraction=0.035, pad=0.025); colorbar.ax.set_title(unit, fontsize=8, pad=4)


def build(input_path: pathlib.Path, control_path: pathlib.Path, mesh_path: pathlib.Path, output_path: pathlib.Path) -> None:
    payload = json.loads(input_path.read_text(encoding="utf-8")); summary = payload["summary"]
    faces = [face for section in payload["sections"] for face in section["faces"]]
    face_lon = np.asarray([face["longitude_deg"] for face in faces]); face_lat = np.asarray([face["latitude_deg"] for face in faces])
    total = np.asarray([face["net_heat_convergence_TW_at_0C"] for face in faces])
    density = np.asarray([face["net_heat_flux_density_MW_m2_at_0C"] for face in faces])
    lon, lat, field = background(control_path, mesh_path)
    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.hashsalt": "osw-nordic-face-intensity-bakeoff-v1"})
    figure, axes = plt.subplots(1, 2, figsize=(12.6, 6.7), facecolor="#f4f1e9")
    figure.subplots_adjust(left=0.06, right=0.96, top=0.76, bottom=0.16, wspace=0.25)
    draw_map(axes[0], lon, lat, field, face_lon, face_lat, total, 13 + 110 * np.sqrt(np.abs(total) / np.max(np.abs(total))), "A  TOTAL HEAT CARRIED", "TW")
    draw_map(axes[1], lon, lat, field, face_lon, face_lat, density, 13 + 110 * np.sqrt(np.abs(density) / np.max(np.abs(density))), "B  HEAT PER WET FACE AREA", "MW/m²")
    figure.text(0.045, 0.94, "THE STRONGEST ATLANTIC JET SURVIVES AREA NORMALIZATION", fontsize=18, fontweight="bold", color="#183944")
    figure.text(0.045, 0.895, "Total contribution includes gate geometry; intensity divides by reconstructed wet cross-sectional area", fontsize=9.5, color="#4c5d63")
    figure.text(0.045, 0.83, f"Twelve of the top 20 faces overlap · strongest import remains 13.0°W, 64.0°N · +66.4 TW · +7.66 MW/m²", fontsize=10.5, color="#183944", fontweight="bold")
    figure.text(0.045, 0.035, "Cross-sectional MW/m² is not air–sea surface flux · both panels use monthly upwind-donor sensitivity, not native FCT/TVD or submonthly covariance", fontsize=7.2, color="#68777b")
    output_path.parent.mkdir(parents=True, exist_ok=True); figure.savefig(output_path, format="svg", metadata={"Date": None}); plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-face-heat-map-2018.json"))
    parser.add_argument("--control", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-control-volume.json"))
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-nordic-seas-mesh.nc"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m4-oras5-nordic-face-intensity-bakeoff-2018.svg"))
    args = parser.parse_args(); build(args.input, args.control, args.mesh, args.output); print(args.output.resolve())


if __name__ == "__main__":
    main()

"""Show the three exact multipliers behind Nordic face heat transport."""

from __future__ import annotations

import argparse
import json
import pathlib

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, LogNorm, TwoSlopeNorm
import numpy as np

from build_oras5_nordic_face_intensity_bakeoff_view import background


HEAT_CMAP = LinearSegmentedColormap.from_list("osw_heat", ("#23677a", "#f5f2ea", "#d17829"))
SEQUENTIAL_CMAP = LinearSegmentedColormap.from_list("osw_scale", ("#e5eeee", "#6e9dab", "#173f4c"))


def draw(axis, lon, lat, field, face_lon, face_lat, values, title, unit, diverging=False) -> None:
    axis.pcolormesh(lon, lat, field, shading="auto", cmap=ListedColormap(("#faf9f5", "#edf3f4", "#d5e8eb")), vmin=0, vmax=2, rasterized=True, zorder=1)
    if diverging:
        limit = float(np.max(np.abs(values)))
        norm, cmap = TwoSlopeNorm(vmin=-limit, vcenter=0, vmax=limit), HEAT_CMAP
    else:
        positive = values[values > 0]
        norm, cmap = LogNorm(vmin=float(np.min(positive)), vmax=float(np.max(positive))), SEQUENTIAL_CMAP
    points = axis.scatter(face_lon, face_lat, c=values, s=23, cmap=cmap, norm=norm, edgecolor="#f4f1e9", linewidth=0.25, zorder=4)
    axis.set_xlim(-42, 35); axis.set_ylim(56, 84); axis.set_aspect(1.65)
    axis.set_xlabel("longitude"); axis.set_ylabel("latitude")
    axis.set_title(title, loc="left", fontsize=10, fontweight="bold")
    axis.spines[["top", "right"]].set_visible(False)
    colorbar = axis.figure.colorbar(points, ax=axis, fraction=0.032, pad=0.018)
    colorbar.ax.set_title(unit, fontsize=7.5, pad=3)


def build(input_path: pathlib.Path, control_path: pathlib.Path, mesh_path: pathlib.Path, output_path: pathlib.Path) -> None:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    faces = [face for section in payload["sections"] for face in section["faces"]]
    face_lon = np.asarray([face["longitude_deg"] for face in faces])
    face_lat = np.asarray([face["latitude_deg"] for face in faces])
    area = np.asarray([face["wet_cross_sectional_area_m2"] / 1e6 for face in faces])
    speed = np.asarray([face["gross_exchange_speed_m_s"] for face in faces])
    thermal = np.asarray([face["net_thermal_transport_factor_C_at_0C"] for face in faces])
    heat = np.asarray([face["net_heat_convergence_TW_at_0C"] for face in faces])
    lon, lat, field = background(control_path, mesh_path)
    spread = payload["summary"]["driver_p90_to_p10_spread"]

    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "svg.hashsalt": "osw-nordic-face-drivers-v1"})
    figure, axes = plt.subplots(2, 2, figsize=(12.6, 9.1), facecolor="#f4f1e9")
    figure.subplots_adjust(left=0.065, right=0.955, top=0.78, bottom=0.105, hspace=0.35, wspace=0.22)
    draw(axes[0, 0], lon, lat, field, face_lon, face_lat, area, "A  WET GATE GEOMETRY", "km²")
    draw(axes[0, 1], lon, lat, field, face_lon, face_lat, speed, "B  GROSS EXCHANGE SPEED", "m/s")
    draw(axes[1, 0], lon, lat, field, face_lon, face_lat, thermal, "C  SIGNED THERMAL TRANSPORT FACTOR", "°C", True)
    draw(axes[1, 1], lon, lat, field, face_lon, face_lat, heat, "D  RESULTING NET HEAT", "TW", True)

    figure.text(0.045, 0.955, "EVERY HEAT JET HAS THREE MULTIPLIERS", fontsize=19, fontweight="bold", color="#183944")
    figure.text(0.045, 0.91, "wet area  ×  gross exchange speed  ×  signed thermal factor  ×  ρCp  =  net face heat", fontsize=10, color="#4c5d63")
    figure.text(0.045, 0.845, f"P90/P10 spread · geometry {spread['wet_cross_sectional_area']:.1f}× · speed {spread['gross_exchange_speed']:.1f}× · |thermal factor| {spread['absolute_net_thermal_transport_factor']:.1f}×", fontsize=10.5, color="#183944", fontweight="bold")
    figure.text(0.045, 0.035, "The signed thermal factor is net heat divided by gross volume exchange—not a water-mass temperature · monthly upwind-donor sensitivity, not native FCT/TVD", fontsize=7.2, color="#68777b")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, format="svg", metadata={"Date": None})
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-face-heat-map-2018.json"))
    parser.add_argument("--control", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-control-volume.json"))
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-nordic-seas-mesh.nc"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m4-oras5-nordic-face-drivers-2018.svg"))
    args = parser.parse_args()
    build(args.input, args.control, args.mesh, args.output)
    print(args.output.resolve())


if __name__ == "__main__":
    main()

"""Show whether annual Nordic face-heat hotspots persist month by month."""

from __future__ import annotations

import argparse
import json
import pathlib

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
import numpy as np


MONTH_LABELS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
SHORT = {"denmark_strait": "DEN", "iceland_scotland_ridge": "ISR", "northern_north_sea": "NNS", "fram_strait": "FRA", "norway_svalbard": "NSV"}


def build(input_path: pathlib.Path, output_path: pathlib.Path) -> None:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    faces = [face | {"section_id": section["id"]} for section in payload["sections"] for face in section["faces"]]
    ranked = sorted(faces, key=lambda face: abs(face["net_heat_convergence_TW_at_0C"]), reverse=True)
    top = ranked[:20]
    matrix = np.asarray([[entry["net_heat_convergence_TW_at_0C"] for entry in face["monthly"]] for face in top])
    leader = matrix[0]
    persistence = payload["summary"]["monthly_persistence"]
    overlap = np.asarray(list(persistence["annual_top_20_monthly_top_20_overlap"].values()))
    labels = [f"{rank:02d}  {SHORT[face['section_id']]}  {face['longitude_deg']:.1f}°, {face['latitude_deg']:.1f}°" for rank, face in enumerate(top, 1)]

    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "svg.hashsalt": "osw-nordic-face-persistence-v1"})
    cmap = LinearSegmentedColormap.from_list("osw_heat", ("#23677a", "#f5f2ea", "#d17829"))
    limit = float(np.max(np.abs(matrix)))
    figure = plt.figure(figsize=(12.6, 8.4), facecolor="#f4f1e9")
    grid = figure.add_gridspec(2, 2, left=0.12, right=0.955, top=0.77, bottom=0.11, width_ratios=(1.65, 0.9), hspace=0.42, wspace=0.28)

    heat_axis = figure.add_subplot(grid[:, 0])
    image = heat_axis.imshow(matrix, cmap=cmap, norm=TwoSlopeNorm(vmin=-limit, vcenter=0, vmax=limit), aspect="auto")
    heat_axis.set_xticks(range(12), MONTH_LABELS)
    heat_axis.set_yticks(range(20), labels)
    heat_axis.tick_params(axis="y", labelsize=7.5)
    heat_axis.set_title("A  ANNUAL TOP 20 THROUGH ALL TWELVE MONTHS", loc="left", fontsize=10, fontweight="bold")
    heat_axis.set_xlabel("2018 monthly-mean face heat")
    colorbar = figure.colorbar(image, ax=heat_axis, fraction=0.03, pad=0.025)
    colorbar.ax.set_title("TW", fontsize=8, pad=3)

    leader_axis = figure.add_subplot(grid[0, 1])
    leader_axis.plot(range(12), leader, color="#d17829", marker="o", linewidth=2)
    leader_axis.fill_between(range(12), 0, leader, color="#d17829", alpha=0.12)
    leader_axis.set_xticks(range(12), MONTH_LABELS, rotation=45)
    leader_axis.set_ylabel("net heat convergence (TW)")
    leader_axis.set_title("B  THE LEADER NEVER SURRENDERS #1", loc="left", fontsize=10, fontweight="bold")
    leader_axis.spines[["top", "right"]].set_visible(False)
    leader_axis.text(0.04, 0.08, f"positive 12/12 months\nabsolute rank #1 12/12", transform=leader_axis.transAxes, color="#183944", fontweight="bold")

    overlap_axis = figure.add_subplot(grid[1, 1])
    overlap_axis.bar(range(12), overlap, color="#547f8c", width=0.72)
    overlap_axis.axhline(float(np.mean(overlap)), color="#d17829", linewidth=1.5, linestyle="--")
    overlap_axis.set_xticks(range(12), MONTH_LABELS, rotation=45)
    overlap_axis.set_ylim(0, 20.8); overlap_axis.set_yticks((0, 5, 10, 15, 20))
    overlap_axis.set_ylabel("annual-top-20 faces retained")
    overlap_axis.set_title("C  MOST OF THE TOP 20 PERSIST", loc="left", fontsize=10, fontweight="bold")
    overlap_axis.spines[["top", "right"]].set_visible(False)
    overlap_axis.text(0.04, 0.9, f"monthly range {int(overlap.min())}–{int(overlap.max())} · mean {np.mean(overlap):.1f}/20", transform=overlap_axis.transAxes, color="#183944", fontweight="bold")

    figure.text(0.045, 0.955, "THE ATLANTIC HEAT JET IS NOT AN ANNUAL-MEAN MIRAGE", fontsize=18.5, fontweight="bold", color="#183944")
    figure.text(0.045, 0.91, "All 284 native boundary faces reranked independently in each 2018 monthly mean", fontsize=9.5, color="#4c5d63")
    figure.text(0.045, 0.84, "The same Iceland-side face is the strongest absolute transporter in every month; the broader hotspot set also remains recognizable.", fontsize=10.2, color="#183944", fontweight="bold")
    figure.text(0.045, 0.035, "Monthly persistence within one ORAS5 member/year is not interannual persistence or climatology · upwind monthly-donor sensitivity, not native FCT/TVD", fontsize=7.2, color="#68777b")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, format="svg", metadata={"Date": None})
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-face-heat-map-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("figures/osw-m4-oras5-nordic-face-persistence-2018.svg"))
    args = parser.parse_args()
    build(args.input, args.output)
    print(args.output.resolve())


if __name__ == "__main__":
    main()

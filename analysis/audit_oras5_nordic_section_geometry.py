"""Audit full-depth mask, thickness, width, and area for the five Nordic boundaries."""

from __future__ import annotations

import argparse
import json
import pathlib

import netCDF4
import numpy as np

import audit_oras5_arctic_section_geometry as geometry


def run(mesh_path: pathlib.Path, control_path: pathlib.Path) -> dict:
    control = json.loads(control_path.read_text(encoding="utf-8"))
    with netCDF4.Dataset(mesh_path) as dataset:
        arrays = {
            name: np.asarray(np.ma.filled(dataset.variables[name][:], 0))
            for name in ("e3t_0", "mbathy", "e3t_ps", "umask", "vmask", "e2u", "e1v")
        }
    _, u_thickness, v_thickness, fallback = geometry.reconstruct_faces(
        arrays["e3t_0"], arrays["mbathy"], arrays["e3t_ps"]
    )
    sections = []
    for source in control["sections"]:
        summary = geometry.section_summary(
            source["name"],
            source["semantics"],
            source["faces"],
            u_thickness,
            v_thickness,
            arrays["umask"].astype(bool),
            arrays["vmask"].astype(bool),
            arrays["e2u"],
            arrays["e1v"],
            arrays["e3t_0"],
            True,
        )
        summary["id"] = source["id"]
        sections.append(summary)
    all_pass = all(
        section["checks"]["mask_mismatch_count"] == 0
        and section["checks"]["wet_area_finite_positive"]
        and section["checks"]["depth_bins_reproduce_total"]
        and section["checks"]["all_widths_finite_positive"]
        for section in sections
    )
    return {
        "schema": "osw.oras5.nordic-section-geometry-audit.v1",
        "status": "five_sections_pass_internal_full_depth_geometry" if all_pass else "full_depth_geometry_failed",
        "sources": {
            "mesh": {"path": f"atlas/data/{mesh_path.name}", "sha256": geometry.sha256_file(mesh_path)},
            "surface_control_volume": {"path": f"research/{control_path.name}", "sha256": geometry.sha256_file(control_path)},
        },
        "reconstruction": {
            "operator": "minimum reconstructed thickness of the two adjacent T cells at each interior U/V face",
            "fallback_bottom_cell_count": fallback,
            "reference_level_count": len(arrays["e3t_0"]),
            "depth_bins_m": [list(bounds) for bounds in geometry.DEPTH_BINS_M],
        },
        "sections": sections,
        "boundary_total_area_m2": float(sum(section["total_section_area_m2"] for section in sections)),
        "all_sections_pass": all_pass,
        "boundary": "Internal native mask/thickness/area consistency only. This does not independently validate production face thickness or calculate volume, heat, storage, surface exchange, uncertainty, or Arctic delivery.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-nordic-seas-mesh.nc"))
    parser.add_argument("--control", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-control-volume.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-section-geometry-audit.json"))
    args = parser.parse_args()
    payload = run(args.mesh, args.control)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {payload['status']}")


if __name__ == "__main__":
    main()

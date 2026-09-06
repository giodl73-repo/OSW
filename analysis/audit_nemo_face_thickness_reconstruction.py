"""Audit the adjacent-minimum face-thickness candidate on a native mesh subset."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

import netCDF4
import numpy as np


def as_filled(values, fill=0):
    return np.asarray(np.ma.filled(values, fill))


def reconstruct_t(reference, mbathy, partial):
    reference = np.asarray(reference, dtype=float)
    mbathy = np.asarray(mbathy, dtype=int)
    partial = np.asarray(partial, dtype=float)
    if reference.ndim != 1 or mbathy.ndim != 2 or partial.shape != mbathy.shape:
        raise ValueError("expected 1D reference thickness and matching 2D bottom arrays")
    nz = len(reference)
    if np.any(reference <= 0) or np.any(~np.isfinite(reference)):
        raise ValueError("reference thickness must be finite and positive")
    if np.any(mbathy < 0) or np.any(mbathy > nz):
        raise ValueError("mbathy is outside the vertical grid")
    if np.any(partial < 0) or np.any(~np.isfinite(partial)):
        raise ValueError("partial thickness must be finite and nonnegative")
    effective_partial = partial.copy()
    fallback = (mbathy > 0) & (effective_partial == 0)
    effective_partial[fallback] = reference[mbathy[fallback] - 1]
    level = np.arange(1, nz + 1)[:, None, None]
    full = level < mbathy[None, :, :]
    bottom = level == mbathy[None, :, :]
    thickness = np.where(full, reference[:, None, None], 0.0)
    thickness = np.where(bottom, effective_partial[None, :, :], thickness)
    return thickness, int(fallback.sum())


def audit_arrays(reference, mbathy, partial, umask, vmask, e2u, e1v) -> dict:
    t, fallback_count = reconstruct_t(reference, mbathy, partial)
    umask = np.asarray(umask) > 0; vmask = np.asarray(vmask) > 0
    if umask.shape != t.shape or vmask.shape != t.shape:
        raise ValueError("U/V masks must match reconstructed T-cell shape")
    if np.asarray(e2u).shape != t.shape[1:] or np.asarray(e1v).shape != t.shape[1:]:
        raise ValueError("horizontal metrics must match the T-cell horizontal shape")

    u = np.minimum(t[:, :, :-1], t[:, :, 1:])
    v = np.minimum(t[:, :-1, :], t[:, 1:, :])
    predicted_u = u > 0; predicted_v = v > 0
    actual_u = umask[:, :, :-1]; actual_v = vmask[:, :-1, :]
    u_mismatch = int(np.count_nonzero(predicted_u != actual_u))
    v_mismatch = int(np.count_nonzero(predicted_v != actual_v))

    t_depth = t.sum(axis=0)
    u_depth_residual = u.sum(axis=0) - np.minimum(t_depth[:, :-1], t_depth[:, 1:])
    v_depth_residual = v.sum(axis=0) - np.minimum(t_depth[:-1, :], t_depth[1:, :])
    u_area = u * np.asarray(e2u, dtype=float)[None, :, :-1]
    v_area = v * np.asarray(e1v, dtype=float)[None, :-1, :]
    wet_u_area = u_area[predicted_u]; wet_v_area = v_area[predicted_v]
    finite_positive_area = (
        wet_u_area.size > 0 and wet_v_area.size > 0
        and np.all(np.isfinite(wet_u_area)) and np.all(np.isfinite(wet_v_area))
        and np.all(wet_u_area > 0) and np.all(wet_v_area > 0)
    )
    max_depth_residual = max(
        float(np.max(np.abs(u_depth_residual), initial=0)),
        float(np.max(np.abs(v_depth_residual), initial=0)),
    )
    passes = u_mismatch == 0 and v_mismatch == 0 and max_depth_residual < 1e-9 and finite_positive_area
    return {
        "status": "candidate_passes_native_geometry_consistency" if passes else "candidate_fails_native_geometry_consistency",
        "fallback_bottom_cell_count": fallback_count,
        "wet_face_count": {"u": int(predicted_u.sum()), "v": int(predicted_v.sum())},
        "mask_mismatch_count": {"u": u_mismatch, "v": v_mismatch},
        "maximum_face_column_depth_residual_m": max_depth_residual,
        "wet_face_area_m2": {
            "u_minimum": None if not wet_u_area.size else float(wet_u_area.min()),
            "u_maximum": None if not wet_u_area.size else float(wet_u_area.max()),
            "v_minimum": None if not wet_v_area.size else float(wet_v_area.min()),
            "v_maximum": None if not wet_v_area.size else float(wet_v_area.max()),
            "all_finite_positive": bool(finite_positive_area),
        },
        "terminal_face_copying": False,
    }


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit_file(path: pathlib.Path) -> dict:
    with netCDF4.Dataset(path) as dataset:
        arrays = {name: as_filled(dataset.variables[name][:]) for name in (
            "e3t_0", "mbathy", "e3t_ps", "umask", "vmask", "e2u", "e1v"
        )}
    result = audit_arrays(
        arrays["e3t_0"], arrays["mbathy"], arrays["e3t_ps"], arrays["umask"],
        arrays["vmask"], arrays["e2u"], arrays["e1v"],
    )
    return {
        "schema": "oceanlines.osw.m3-nemo-face-thickness-audit.v1",
        **result,
        "source": {"path": str(path), "sha256": sha256_file(path)},
        "method": (
            "Reconstruct T thickness from e3t_0, mbathy, and e3t_ps; set each interior U/V "
            "thickness to the minimum of its two adjacent T-cell thicknesses."
        ),
        "next_test": "compare reconstructed face thickness or transport against an independently generated ORCA025 reference",
        "boundary": (
            "A mask/depth/area consistency pass supports internal geometry but does not prove exact "
            "ORAS5 configuration equivalence, state-field alignment, section topology, or transport."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    result = audit_file(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {result['status']}")


if __name__ == "__main__":
    main()

"""Reconstruct interior NEMO U/V face thicknesses from partial-step T cells.

This implements the CDFTOOLS 3.0 adjacent-minimum candidate while deliberately
omitting terminal faces.  It is a geometry experiment, not yet an accepted
ORAS5 section-extraction method.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib


def finite_positive(value, label: str, allow_zero: bool = False) -> float:
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} must be finite")
    value = float(value)
    if value < 0 or (value == 0 and not allow_zero):
        raise ValueError(f"{label} must be {'nonnegative' if allow_zero else 'positive'}")
    return value


def reconstruct(payload: dict) -> dict:
    levels, rows, columns = payload["shape"]
    if any(not isinstance(value, int) or value < 1 for value in (levels, rows, columns)):
        raise ValueError("shape must contain positive integer levels, rows, and columns")
    if rows < 2 or columns < 2:
        raise ValueError("at least two rows and columns are required for interior faces")
    reference = payload["e3t_0_m"]
    bottom_level = payload["mbathy_1_based"]
    partial = payload["e3t_ps_m"]
    cells = rows * columns
    if len(reference) != levels or len(bottom_level) != cells or len(partial) != cells:
        raise ValueError("geometry arrays do not match shape")
    reference = [finite_positive(value, f"e3t_0 {level}") for level, value in enumerate(reference)]

    t = [[[0.0 for _ in range(columns)] for _ in range(rows)] for _ in range(levels)]
    fallback_count = 0
    for row in range(rows):
        for column in range(columns):
            cell = row * columns + column
            bottom = bottom_level[cell]
            if not isinstance(bottom, int) or not 0 <= bottom <= levels:
                raise ValueError("mbathy must be an integer from zero through the number of levels")
            bottom_thickness = finite_positive(partial[cell], f"e3t_ps {cell}", allow_zero=True)
            if bottom and bottom_thickness == 0:
                bottom_thickness = reference[bottom - 1]
                fallback_count += 1
            for level in range(bottom):
                t[level][row][column] = bottom_thickness if level == bottom - 1 else reference[level]

    u = [[[0.0 for _ in range(columns - 1)] for _ in range(rows)] for _ in range(levels)]
    v = [[[0.0 for _ in range(columns)] for _ in range(rows - 1)] for _ in range(levels)]
    for level in range(levels):
        for row in range(rows):
            for column in range(columns - 1):
                u[level][row][column] = min(t[level][row][column], t[level][row][column + 1])
        for row in range(rows - 1):
            for column in range(columns):
                v[level][row][column] = min(t[level][row][column], t[level][row + 1][column])

    def flatten(values):
        return [number for level in values for row in level for number in row]

    u_flat, v_flat = flatten(u), flatten(v)
    input_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "schema": "oceanlines.osw.m3-nemo-face-thickness-candidate.v1",
        "status": "synthetic_candidate_not_accepted_for_ORAS5_transport",
        "input_sha256": hashlib.sha256(input_bytes).hexdigest(),
        "input_schema": payload["schema"],
        "shape": payload["shape"],
        "u_shape": [levels, rows, columns - 1],
        "v_shape": [levels, rows - 1, columns],
        "u_face_thickness_m": u_flat,
        "v_face_thickness_m": v_flat,
        "fallback_bottom_cell_count": fallback_count,
        "checks": {
            "u_nonnegative": all(value >= 0 for value in u_flat),
            "v_nonnegative": all(value >= 0 for value in v_flat),
            "terminal_face_copying": False,
            "operator": "minimum of the two adjacent reconstructed T-cell thicknesses",
        },
        "boundary": (
            "Synthetic verification of an interior-face partial-step reconstruction candidate. "
            "It excludes terminal faces and does not establish equivalence to the precise ORAS5 "
            "configuration, validate a remote mesh, extract a section, or calculate transport."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    result = reconstruct(json.loads(args.input.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {len(result['u_face_thickness_m'])} U and {len(result['v_face_thickness_m'])} V faces")


if __name__ == "__main__":
    main()

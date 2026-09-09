"""Audit NetCDF inputs for conservative native-face section transport.

The audit is deliberately strict.  It inventories evidence but does not infer
face areas from nominal resolution or treat cell-centred rotated velocity as a
native face flux.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

import netCDF4


ALIASES = {
    "temperature": ("votemper", "thetao", "potential_temperature"),
    "u_velocity": ("vozocrtx", "uo", "zonal_velocity"),
    "v_velocity": ("vomecrty", "vo", "meridional_velocity"),
    "u_face_width": ("e2u", "u_face_width", "u_face_width_m"),
    "v_face_width": ("e1v", "v_face_width", "v_face_width_m"),
    "u_layer_thickness": ("e3u", "e3u_0", "u_layer_thickness", "u_layer_thickness_m"),
    "v_layer_thickness": ("e3v", "e3v_0", "v_layer_thickness", "v_layer_thickness_m"),
    "u_wet_mask": ("umask", "u_wet_fraction"),
    "v_wet_mask": ("vmask", "v_wet_fraction"),
    "u_longitude": ("glamu", "nav_lon_u", "longitude_u"),
    "u_latitude": ("gphiu", "nav_lat_u", "latitude_u"),
    "v_longitude": ("glamv", "nav_lon_v", "longitude_v"),
    "v_latitude": ("gphiv", "nav_lat_v", "latitude_v"),
    "time": ("time_counter", "time", "time_centered"),
}
REQUIRED = tuple(ALIASES)
DIAGNOSTIC_ONLY = {
    "rotated_zonal_velocity", "rotated_meridional_velocity",
    "eastward_sea_water_velocity", "northward_sea_water_velocity",
}


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def assess_names(names: set[str]) -> dict:
    evidence = {}
    missing = []
    for requirement, aliases in ALIASES.items():
        matches = sorted(names.intersection(aliases))
        evidence[requirement] = matches
        if not matches:
            missing.append(requirement)
    diagnostic = sorted(names.intersection(DIAGNOSTIC_ONLY))
    return {
        "status": "ready_for_section_extraction" if not missing else "blocked_missing_native_face_evidence",
        "requirements": evidence,
        "missing": missing,
        "diagnostic_velocity_fields_not_accepted_as_face_flux": diagnostic,
        "inference_policy": "No nominal-resolution area inference; every native U/V face metric must be explicit.",
    }


def inventory(paths: list[pathlib.Path]) -> tuple[list[dict], set[str]]:
    files = []
    names: set[str] = set()
    for path in paths:
        raw_hash = sha256_file(path)
        with netCDF4.Dataset(path) as dataset:
            variables = {}
            for name, variable in dataset.variables.items():
                names.add(name)
                variables[name] = {
                    "dimensions": list(variable.dimensions),
                    "shape": list(variable.shape),
                    "dtype": str(variable.dtype),
                    "units": getattr(variable, "units", None),
                    "standard_name": getattr(variable, "standard_name", None),
                    "grid": getattr(variable, "grid", None),
                }
            files.append({"path": str(path), "sha256": raw_hash, "variables": variables})
    return files, names


def audit(paths: list[pathlib.Path]) -> dict:
    if not paths:
        raise ValueError("at least one NetCDF path is required")
    files, names = inventory(paths)
    readiness = assess_names(names)
    return {
        "schema": "oceanlines.osw.m3-section-readiness.v1",
        "status": readiness["status"],
        "files": files,
        "readiness": readiness,
        "next_step": (
            "Declare a gate and extract signed native U/V faces into the section-kernel contract."
            if not readiness["missing"] else
            "Acquire the missing native mesh-mask/metric evidence; do not calculate transport yet."
        ),
        "boundary": (
            "Readiness means only that named input categories are present. It does not validate units, "
            "coordinate alignment, section topology, conservation, mass closure, or heat transport."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", type=pathlib.Path, nargs="+")
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    result = audit(args.paths)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {result['status']}")


if __name__ == "__main__":
    main()

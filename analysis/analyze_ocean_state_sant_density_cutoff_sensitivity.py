"""Challenge annual SANT density-bin occupancy and flux with shifted cutoffs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import gsw
import netCDF4
import numpy as np

from analyze_ocean_state_sant_closed_box import faces
from analyze_ocean_state_sant_closed_box_density_boundary import face_position
from analyze_ocean_state_sant_density_boundary_collocation import upstream_pair
from analyze_ocean_state_sant_density_boundary_year import MESH, SOURCE, local_box, read_mesh
from analyze_ocean_state_sant_density_inventory_year import METRICS
from analyze_ocean_state_sant_partial_perimeter import face_values
from fetch_ocean_state_sant_closed_box_monthly_fields import MONTHS, ROOT, SELECTION, crop, sha256


BOUNDARY = ROOT / "research" / "ocean-state-sant-density-boundary-monthly-series-2018.json"
INVENTORY = ROOT / "research" / "ocean-state-sant-density-inventory-monthly-series-2018.json"
OUTPUT = ROOT / "research" / "ocean-state-sant-density-cutoff-sensitivity-2018.json"
SCHEMES = (("lower_0_1", -0.1), ("baseline", 0.0), ("higher_0_1", 0.1))
BASE_EDGES = (26.5, 27.0, 27.5)


def sigma0(temperature: np.ndarray, salinity: np.ndarray, depth: np.ndarray, longitude: np.ndarray | float, latitude: np.ndarray | float) -> np.ndarray:
    pressure = gsw.p_from_z(-depth, latitude)
    absolute_salinity = gsw.SA_from_SP(salinity, pressure, longitude, latitude)
    return gsw.sigma0(absolute_salinity, gsw.CT_from_pt(absolute_salinity, temperature))


def measure(box: dict, fields: dict, mesh: dict, area: np.ndarray) -> dict:
    selection = np.s_[:, box["y_start"]:box["y_stop_exclusive"], box["x_start"]:box["x_stop_exclusive"]]
    local_area = area[selection[1:]]
    volume = mesh["thickness"][selection] * local_area[None, :, :]
    cell_sigma = sigma0(fields["votemper"][selection], fields["vosaline"][selection], mesh["midpoint"][selection],
                        mesh["longitude"][selection[1:]][None, :, :], mesh["latitude"][selection[1:]][None, :, :])
    valid_cells = np.isfinite(volume) & (volume > 0) & np.isfinite(cell_sigma)
    cell_volume = volume[valid_cells]
    cell_density = cell_sigma[valid_cells]
    q_parts, centered_parts, upstream_parts = [], [], []
    for face in faces(box):
        axis, y, x = face["face"], face["y"], face["x"]
        velocity = fields["vozocrtx" if axis == "U" else "vomecrty"][:, y, x]
        part = face_values(face, fields["votemper"], fields["vosaline"], velocity, mesh["thickness"], mesh["midpoint"],
                           mesh["metrics"][axis]["width"][y, x], mesh["metrics"][axis]["wet"][:, y, x])
        lon, lat = face_position(face, mesh["longitude"], mesh["latitude"])
        centered_sigma = sigma0(part["temp"], part["salt"], part["depth"], lon, lat)
        upstream_t, upstream_s = upstream_pair(face, fields["votemper"], fields["vosaline"], velocity)
        upstream_sigma = sigma0(upstream_t, upstream_s, part["depth"], lon, lat)
        valid = part["valid"] & np.isfinite(centered_sigma) & np.isfinite(upstream_sigma)
        q_parts.append(part["q"][valid])
        centered_parts.append(centered_sigma[valid])
        upstream_parts.append(upstream_sigma[valid])
    q = np.concatenate(q_parts)
    centered_density = np.concatenate(centered_parts)
    upstream_density = np.concatenate(upstream_parts)
    total_volume = float(cell_volume.sum())
    schemes = []
    for identifier, shift in SCHEMES:
        edges = [round(edge + shift, 1) for edge in BASE_EDGES]
        cells = np.searchsorted(edges, cell_density, side="right")
        centered = np.searchsorted(edges, centered_density, side="right")
        upstream = np.searchsorted(edges, upstream_density, side="right")
        bins = []
        for index in range(4):
            bin_volume = float(cell_volume[cells == index].sum())
            bins.append({"index": index, "volume_fraction": round(bin_volume / total_volume, 9),
                         "centered_net_outward_Sv": round(float(q[centered == index].sum() / 1e6), 9),
                         "upstream_net_outward_Sv": round(float(q[upstream == index].sum() / 1e6), 9)})
        schemes.append({"id": identifier, "cutoffs_sigma0_kg_m3": edges, "bins": bins})
    return {"valid_volume_m3": round(total_volume, 3), "valid_wet_cell_count": int(valid_cells.sum()),
            "valid_wet_face_level_count": int(q.size), "net_outward_all_density_Sv": round(float(q.sum() / 1e6), 9),
            "schemes": schemes}


def build(source_path: Path = SOURCE, selection_path: Path = SELECTION, boundary_path: Path = BOUNDARY, inventory_path: Path = INVENTORY) -> dict:
    source_path, selection_path, boundary_path, inventory_path = map(Path, (source_path, selection_path, boundary_path, inventory_path))
    source = json.loads(source_path.read_text(encoding="utf-8"))
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    boundary = json.loads(boundary_path.read_text(encoding="utf-8"))
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    if source["selection"]["sha256"] != sha256(selection_path) or boundary["source"]["sha256"] != sha256(source_path) or inventory["source"]["sha256"] != sha256(source_path):
        raise ValueError("cutoff challenge requires the same fixed box and compact source family")
    rectangle = crop(selection)
    mesh = read_mesh(rectangle)
    y = slice(rectangle["y_start"], rectangle["y_stop_exclusive"])
    x = slice(rectangle["x_start"], rectangle["x_stop_exclusive"])
    with netCDF4.Dataset(METRICS) as metrics:
        area = np.asarray(metrics["e1t"][y, x], dtype=float) * np.asarray(metrics["e2t"][y, x], dtype=float)
    boxes = [local_box(box, rectangle) for box in [selection["primary"], *selection["one_cell_displaced_controls"]]]
    archive = ROOT / source["output"]["path"]
    if sha256(archive) != source["output"]["sha256"]:
        raise ValueError("compact source archive changed")
    months = []
    with netCDF4.Dataset(archive) as dataset:
        for index, month in enumerate(MONTHS):
            fields = {name: np.asarray(np.ma.filled(dataset[name][index], np.nan), dtype=float) for name in ("votemper", "vosaline", "vozocrtx", "vomecrty")}
            outcomes = []
            for box_index, box in enumerate(boxes):
                result = measure(box, fields, mesh, area)
                baseline = result["schemes"][1]["bins"]
                reference_flux = boundary["months"][index]["outcomes"][box_index]
                reference_stock = inventory["boxes"][box_index]["months"][index]
                if result["valid_wet_face_level_count"] != reference_flux["horizontal_density_boundary"]["all_valid_wet_face_level_count"] or result["valid_wet_cell_count"] != reference_stock["valid_wet_cell_count"]:
                    raise ValueError(f"{month} {box['id']} support differs from annual baselines")
                for bin_index, item in enumerate(baseline):
                    old_flux = reference_flux["horizontal_density_boundary"]["strata"][bin_index]["net_outward_volume_Sv"]
                    old_upstream = reference_flux["collocation_sensitivity"]["strata"][bin_index]["upstream_net_outward_Sv"]
                    old_fraction = reference_stock["strata"][bin_index]["volume_fraction"]
                    if abs(item["centered_net_outward_Sv"] - old_flux) > 2e-9 or abs(item["upstream_net_outward_Sv"] - old_upstream) > 2e-9 or abs(item["volume_fraction"] - old_fraction) > 2e-9:
                        raise ValueError(f"{month} {box['id']} zero-shift scheme does not reproduce the annual baselines")
                outcomes.append({"box": box["id"], **result})
            months.append({"valid_time": f"2018-{month[-2:]}-01/P1M", "outcomes": outcomes})
    return {"schema": "osw-ocean-state-sant-density-cutoff-sensitivity-v1",
            "status": "posthoc_numeric_cutoff_sensitivity_not_water_mass_or_transformation",
            "source": {"path": source_path.relative_to(ROOT).as_posix(), "sha256": sha256(source_path)},
            "selection": {"path": selection_path.relative_to(ROOT).as_posix(), "sha256": sha256(selection_path)},
            "annual_boundary": {"path": boundary_path.relative_to(ROOT).as_posix(), "sha256": sha256(boundary_path)},
            "annual_inventory": {"path": inventory_path.relative_to(ROOT).as_posix(), "sha256": sha256(inventory_path)},
            "method": {"cutoff_shifts_sigma0_kg_m3": [shift for _, shift in SCHEMES], "baseline_cutoffs_sigma0_kg_m3": list(BASE_EDGES),
                       "scope": "All three numeric cutoffs shift together by -0.1, 0, or +0.1 kg/m3; bin index 2 is the middle-high numeric bin in each scheme.",
                       "selection_timing": "This sensitivity was designed after inspection of the baseline annual series, so it is a challenge, not preregistered confirmation.",
                       "collocation": "centered adjacent-cell mean and upstream T-cell density with the same native velocity and wet-face support"},
            "months": months,
            "boundary": "Changing arbitrary numeric density cutoffs may change bin occupancy and signed horizontal flux without changing any native volume or velocity. This post hoc sensitivity is not a water-mass classification, transformation rate, matched inventory tendency, or budget; vertical/mixing/assimilation and submonthly covariance remain absent."}


def validate(payload: dict) -> None:
    if len(payload["months"]) != 12 or payload["status"] != "posthoc_numeric_cutoff_sensitivity_not_water_mass_or_transformation":
        raise ValueError("twelve-month cutoff challenge required")
    for month in payload["months"]:
        if len(month["outcomes"]) != 4:
            raise ValueError("fixed box and three controls required")
        for outcome in month["outcomes"]:
            if len(outcome["schemes"]) != 3:
                raise ValueError("three declared cutoff schemes required")
            for scheme in outcome["schemes"]:
                if len(scheme["bins"]) != 4 or abs(sum(item["volume_fraction"] for item in scheme["bins"]) - 1) > 1e-7:
                    raise ValueError("density bins must partition valid volume")
                if abs(sum(item["centered_net_outward_Sv"] for item in scheme["bins"]) - outcome["net_outward_all_density_Sv"]) > 4e-9:
                    raise ValueError("cutoff shift changed total native volume flux")
                if abs(sum(item["upstream_net_outward_Sv"] for item in scheme["bins"]) - outcome["net_outward_all_density_Sv"]) > 4e-9:
                    raise ValueError("upstream cutoff shift changed total native volume flux")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    payload = build()
    validate(payload)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

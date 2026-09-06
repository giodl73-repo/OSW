"""Replicate published Agulhas leakage summaries from archived GEOMAR outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

import numpy as np
import xarray as xr


SECTION_NAMES = {1: "release", 2: "north", 3: "east", 4: "south", 5: "west", 6: "northwest"}


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stats(values: np.ndarray, years: np.ndarray | None = None) -> dict:
    coordinates = np.asarray(years if years is not None else np.arange(len(values)), dtype=int)
    return {
        "mean_sv": float(np.mean(values)),
        "population_standard_deviation_sv": float(np.std(values)),
        "minimum_sv": float(np.min(values)),
        "minimum_release_year": int(coordinates[np.argmin(values)]),
        "maximum_sv": float(np.max(values)),
        "maximum_release_year": int(coordinates[np.argmax(values)]),
    }


def run(section_path: pathlib.Path, transport_path: pathlib.Path, examples_path: pathlib.Path) -> dict:
    with xr.open_dataset(section_path) as sections:
        section_geometry = [
            {"section_number": int(number), "section": SECTION_NAMES[int(number)], "longitude": float(lon), "latitude": float(lat)}
            for number, lon, lat in zip(sections.section_number.values, sections.lon.values, sections.lat.values)
        ]
        section_license = sections.attrs.get("license")
    with xr.open_dataset(transport_path) as transport:
        years = transport.release_year.values.astype(int)
        west = transport.transport_per_section.sel(section="West").values
        northwest = transport.transport_per_section.sel(section="Northwest").values
        leakage = west + northwest
        east = transport.transport_per_section.sel(section="East").values
        all_sections = {
            str(name): stats(transport.transport_per_section.sel(section=name).values, years)
            for name in transport.section.values
        }
    with xr.open_dataset(examples_path) as examples:
        trajectories = []
        for index in range(examples.sizes["traj"]):
            finite = np.isfinite(examples.lon.values[index]) & np.isfinite(examples.lat.values[index])
            trajectories.append({
                "id": index + 1,
                "points": [
                    {"longitude": float(lon), "latitude": float(lat), "depth_m": float(depth), "temperature_c": float(temp), "salinity": float(salt)}
                    for lon, lat, depth, temp, salt in zip(
                        examples.lon.values[index][finite], examples.lat.values[index][finite], examples.z.values[index][finite],
                        examples.T.values[index][finite], examples.S.values[index][finite],
                    )
                ],
            })
    slope_sv_per_year = float(np.polyfit(years, leakage, 1)[0])
    return {
        "schema": "oceanlines.osw.m3-geomar-agulhas-published-replication.v1",
        "status": "attributed_recalculation_from_published_derived_model_output",
        "release_years": {"start": int(years[0]), "stop": int(years[-1]), "count": len(years)},
        "leakage_definition": "sum of transport exiting the archived Parcels domain through section 5 West and section 6 Northwest",
        "leakage": {**stats(leakage, years), "linear_trend_sv_per_decade": slope_sv_per_year * 10},
        "return_current_east_exit": stats(east, years),
        "all_section_summaries": all_sections,
        "annual": [
            {"release_year": int(year), "west_sv": float(w), "northwest_sv": float(n), "leakage_sv": float(l), "east_sv": float(e)}
            for year, w, n, l, e in zip(years, west, northwest, leakage, east)
        ],
        "section_geometry": section_geometry,
        "example_trajectories": trajectories,
        "sources": [
            {"path": str(path), "sha256": sha256_file(path)}
            for path in (section_path, transport_path, examples_path)
        ],
        "archive": {
            "handle": "https://hdl.handle.net/20.500.12085/b704e917-09dd-4a73-b6a1-ea24a549920c",
            "paper": "https://doi.org/10.5194/os-17-1067-2021",
            "license": section_license,
            "authors": "Christina Schmidt, Franziska U. Schwarzkopf, Siren Rühs, and Arne Biastoch",
        },
        "method": "OSW opens the authors' compact derived section and transport NetCDFs, sums West + Northwest for every release year, and recomputes descriptive statistics and an unweighted ordinary least-squares linear trend.",
        "boundary": "This is an attributed replication of archived INALT20/Parcels model output, not a new OSW simulation, observation-only estimate, present-day monitoring product, or universal leakage value. Population standard deviation describes the 57 archived annual values; no uncertainty interval is inferred. The linear trend is sensitive to the archived 1958–2014 period and forcing.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=pathlib.Path, default=pathlib.Path("atlas/data/geomar-agulhas"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m3-geomar-agulhas-published-replication.json"))
    args = parser.parse_args()
    result = run(
        args.data_dir / "Parcels_sections_32S.nc",
        args.data_dir / "Parcels_trajectories_32S_postprocessing_transport_per_section.nc",
        args.data_dir / "Parcels_trajectories_32S_examples.nc",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

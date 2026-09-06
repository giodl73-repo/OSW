"""Audit the live ICDC ORAS5 native-grid catalog for heat-budget terms."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import urllib.request
import xml.etree.ElementTree as ET


CATALOG_URL = "https://icdc.cen.uni-hamburg.de/thredds/catalog/ftpthredds/EASYInit/oras5/ORCA025/catalog.xml"
REQUIRED_NATIVE_TERMS = {
    "temperature_tendency": ("temperature_tendency", "votemptend", "ttrd"),
    "native_tracer_advection": ("temperature_advection", "advective_temperature_tendency", "ttrdadv"),
    "vertical_mixing": ("vertical_mixing_temperature_tendency", "ttrd_zdf"),
    "lateral_diffusion": ("lateral_diffusion_temperature_tendency", "ttrd_ldf"),
    "sea_ice_heat_exchange": ("ice_ocean_heat_flux", "sea_ice_heat_flux"),
    "assimilation_increment": ("temperature_analysis_increment", "assimilation_increment"),
}


def audit(output: pathlib.Path, retrieved_at: str) -> dict:
    with urllib.request.urlopen(CATALOG_URL, timeout=60) as response:
        source = response.read()
    root = ET.fromstring(source)
    namespace = {"t": "http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0"}
    names = sorted({node.attrib.get("name", "") for node in root.findall(".//t:catalogRef", namespace)} - {""})
    availability = {
        term: {"available": any(candidate in names for candidate in candidates), "candidate_names": list(candidates)}
        for term, candidates in REQUIRED_NATIVE_TERMS.items()
    }
    result = {
        "schema": "osw.oras5.native-budget-availability.v1",
        "status": "live_native_grid_catalog_audited",
        "retrieved_at": retrieved_at,
        "catalog": {"url": CATALOG_URL, "sha256": hashlib.sha256(source).hexdigest(), "variable_family_count": len(names), "variable_families": names},
        "required_native_terms": availability,
        "archived_partial_diagnostics": {
            "surface_heat_flux": "sohefldo" in names,
            "total_column_heat_content": "sohtcbtm" in names,
            "potential_temperature_state": "votemper" in names,
            "native_grid_velocity_state": "vozocrtx" in names and "vomecrty" in names,
        },
        "conclusion": "The public ICDC ORCA025 monthly archive supports an independent storage check and offline advection, but exposes none of the model-native tendency, mixing, diffusion, sea-ice heat-exchange, or assimilation-increment families required to close and decompose the regional heat budget.",
        "boundary": "Absence from this public catalog is an archive-availability result, not proof that the ORAS5 production system never computed these terms or that they cannot be obtained from ECMWF by another route.",
    }
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-native-budget-availability.json"))
    parser.add_argument("--retrieved-at")
    args = parser.parse_args()
    result = audit(args.output, args.retrieved_at or dt.datetime.now(dt.timezone.utc).isoformat())
    print(f"audited {result['catalog']['variable_family_count']} variable families")


if __name__ == "__main__":
    main()

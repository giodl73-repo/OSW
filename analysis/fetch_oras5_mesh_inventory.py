"""Receipt the public ORAS5 ORCA025 mesh metadata without downloading 650 MB."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import urllib.request

try:
    from inspect_oras5_section_readiness import assess_names
except ModuleNotFoundError:
    from analysis.inspect_oras5_section_readiness import assess_names


DDS_URL = "https://icdc.cen.uni-hamburg.de/thredds/dodsC/ftpthredds/EASYInit/oras5/ORCA025/mesh/mesh_mask.nc.dds"
CATALOGUE_URL = "https://icdc.cen.uni-hamburg.de/thredds/catalog/ftpthredds/EASYInit/oras5/ORCA025/mesh/catalog.html"
CDFTOOLS_SOURCE_URL = "https://sources.debian.org/src/cdftools/3.0-1/cdfio.f90/"
DECLARATION = re.compile(r"^\s*(Byte|Int\d+|UInt\d+|Float\d+)\s+(\w+)((?:\[[^]]+\])+);\s*$")
DIMENSION = re.compile(r"\[\s*(\w+)\s*=\s*(\d+)\s*]")


def fetch(url: str = DDS_URL) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "OSW/0.1 (public research atlas)"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def parse(raw: bytes) -> list[dict]:
    variables = []
    for line in raw.decode("utf-8").splitlines():
        match = DECLARATION.match(line)
        if not match:
            continue
        variables.append({
            "name": match.group(2),
            "type": match.group(1),
            "dimensions": {name: int(size) for name, size in DIMENSION.findall(match.group(3))},
        })
    if not variables:
        raise ValueError("DDS contains no recognized array declarations")
    return variables


def package(raw: bytes, retrieved_at: str) -> dict:
    variables = parse(raw)
    names = {variable["name"] for variable in variables}
    readiness = assess_names(names)
    reconstruction_inputs = ("mbathy", "e3t_ps", "e3t_0")
    return {
        "schema": "oceanlines.oras5.mesh-inventory.v1",
        "status": "remote_metadata_only",
        "source": "University of Hamburg ICDC THREDDS ORAS5 ORCA025 mesh_mask.nc",
        "catalogue_url": CATALOGUE_URL,
        "dds_url": DDS_URL,
        "retrieved_at": retrieved_at,
        "dds_sha256": hashlib.sha256(raw).hexdigest(),
        "reported_full_file_bytes": 650753384,
        "variables": variables,
        "section_readiness_from_mesh_alone": readiness,
        "finding": (
            "The public mesh supplies U/V horizontal metrics, U/V masks, and U/V coordinates, "
            "but its DDS does not expose explicit e3u/e3v native-face layer thickness arrays."
        ),
        "face_thickness_reconstruction_candidate": {
            "required_inputs": list(reconstruction_inputs),
            "available": all(name in names for name in reconstruction_inputs),
            "method_observed_in_cdftools_3_0": (
                "rebuild T-cell thickness by level from e3t_0, replace the mbathy bottom level "
                "with e3t_ps, then use the minimum of adjacent T thicknesses at U and V faces"
            ),
            "source_url": CDFTOOLS_SOURCE_URL,
            "status": "not_accepted_pending_ORAS5_configuration_validation_and_edge_tests",
            "caution": (
                "This is an inference from third-party CDFTOOLS source, not an explicit face metric "
                "in the mesh payload; the source also cautions about its terminal-edge handling."
            ),
        },
        "boundary": (
            "A remote variable inventory is not the mesh payload and does not validate values, "
            "units, partial-cell reconstruction, alignment with CDS files, or section transport."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retrieved-at")
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-mesh-inventory.json"))
    args = parser.parse_args()
    retrieved_at = args.retrieved_at or dt.datetime.now(dt.timezone.utc).isoformat()
    result = package(fetch(), retrieved_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {len(result['variables'])} variables")


if __name__ == "__main__":
    main()

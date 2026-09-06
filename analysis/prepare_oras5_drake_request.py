"""Prepare or execute the receipted ORAS5 M3 Drake pilot request.

Dry-run is the default.  Downloading is opt-in because the all-level global
files may be large and CDS authentication and licence acceptance are external
preconditions.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib


DATASET = "reanalysis-oras5"
DEFAULT_MONTHS = ("02", "05", "08", "11")
VARIABLES = ("potential_temperature", "zonal_velocity", "meridional_velocity")
CATALOGUE_URL = "https://cds.climate.copernicus.eu/datasets/reanalysis-oras5"
DATASET_DOI = "10.24381/cds.67e8eeb7"
MESH_CATALOGUE_URL = "https://icdc.cen.uni-hamburg.de/thredds/catalog/ftpthredds/EASYInit/oras5/ORCA025/mesh/catalog.html"


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_manifest(year: int = 2018, months: tuple[str, ...] = DEFAULT_MONTHS) -> dict:
    if year < 2015:
        raise ValueError("operational ORAS5 request requires year >= 2015")
    normalized = tuple(f"{int(month):02d}" for month in months)
    if not normalized or any(not 1 <= int(month) <= 12 for month in normalized):
        raise ValueError("months must contain values from 01 through 12")
    if len(set(normalized)) != len(normalized):
        raise ValueError("months must be unique")
    request = {
        "product_type": ["operational"],
        "vertical_resolution": ["all_levels"],
        "variable": list(VARIABLES),
        "year": [str(year)],
        "month": list(normalized),
    }
    canonical = json.dumps(request, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "schema": "oceanlines.oras5.request-manifest.v1",
        "status": "download_not_executed",
        "dataset": DATASET,
        "dataset_doi": DATASET_DOI,
        "catalogue_url": CATALOGUE_URL,
        "request": request,
        "request_sha256": hashlib.sha256(canonical).hexdigest(),
        "pilot": {
            "name": "M3 Drake Passage seasonal all-level intake",
            "section_geometry": "not supplied by this request",
            "seasonal_sampling": "February, May, August, and November monthly means",
        },
        "required_companion_geometry": [
            "native U/V face coordinates and staggering declaration",
            "U/V horizontal face widths",
            "U/V layer thicknesses or exact cell bounds",
            "U/V wet fractions or masks",
        ],
        "companion_geometry_candidate": {
            "source": "University of Hamburg ICDC THREDDS ORAS5 ORCA025 mesh catalogue",
            "url": MESH_CATALOGUE_URL,
            "status": "candidate_requires_native_U_V_vertical_metric_audit",
        },
        "boundary": (
            "This is a retrieval manifest, not a transport result. ORAS5 temperature and velocity "
            "files must not be converted to section transport until native face geometry, wet masks, "
            "vertical metrics, section orientation, and grid staggering pass the M3 readiness audit."
        ),
    }


def write_json(payload: dict, path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, default=2018)
    parser.add_argument("--month", action="append", dest="months")
    parser.add_argument("--manifest", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-drake-request-2018.json"))
    parser.add_argument("--download", type=pathlib.Path, help="Opt in to authenticated CDS retrieval to this path")
    args = parser.parse_args()
    manifest = build_manifest(args.year, tuple(args.months or DEFAULT_MONTHS))
    if args.download:
        try:
            import cdsapi
        except ImportError as error:
            raise SystemExit("cdsapi is required only for --download") from error
        args.download.parent.mkdir(parents=True, exist_ok=True)
        cdsapi.Client().retrieve(DATASET, manifest["request"], str(args.download))
        manifest["status"] = "download_complete"
        manifest["download"] = {
            "path": str(args.download),
            "bytes": args.download.stat().st_size,
            "sha256": sha256_file(args.download),
            "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
    write_json(manifest, args.manifest)
    print(f"wrote {args.manifest}: {manifest['status']}")


if __name__ == "__main__":
    main()

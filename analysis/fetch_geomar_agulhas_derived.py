"""Fetch the compact CC BY 4.0 GEOMAR Agulhas replication artifacts."""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import urllib.request


BASE_URL = "https://data.geomar.de/downloads/20.500.12085/b704e917-09dd-4a73-b6a1-ea24a549920c/FINAL_VERSION/DATA"
FILES = {
    "Parcels_sections_32S.nc": "ae192601885aae71b096841f21f59da073b7f7be56dc7796370f873c014ab6a4",
    "Parcels_trajectories_32S_postprocessing_transport_per_section.nc": "725413d78c1aa1afd777eeb6e6890be8a7215568d7ed5c0a19d880927ae3ba21",
    "Parcels_trajectories_32S_examples.nc": "ea2eb8c5d8164ead7e5c1c4c4be7316d775fcec005d7e4b5ea4ba7ea10790e60",
}


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fetch(output_dir: pathlib.Path) -> list[pathlib.Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, expected in FILES.items():
        raw = urllib.request.urlopen(f"{BASE_URL}/{name}", timeout=120).read()
        actual = sha256_bytes(raw)
        if actual != expected:
            raise ValueError(f"{name} SHA-256 {actual} != {expected}")
        path = output_dir / name
        path.write_bytes(raw)
        paths.append(path)
        print(f"wrote {path} ({len(raw)} bytes)")
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=pathlib.Path, default=pathlib.Path("atlas/data/geomar-agulhas"))
    args = parser.parse_args()
    fetch(args.output_dir)


if __name__ == "__main__":
    main()

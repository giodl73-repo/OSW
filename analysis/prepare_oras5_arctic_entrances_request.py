"""Prepare the native ORAS5 M3 intake contract for Fram and Barents entrances."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib


MONTHS = ("201802", "201805", "201808", "201811")
MEMBER = "opa0"
BASE = "https://icdc.cen.uni-hamburg.de/thredds/dodsC/ftpthredds/EASYInit/oras5/ORCA025"
FIELDS = {
    "votemper": "potential temperature on T cells",
    "vosaline": "practical salinity on T cells",
    "vozocrtx": "native i-direction velocity on U faces",
    "vomecrty": "native j-direction velocity on V faces",
}
DOMAINS = {
    "fram": {"west": -20.0, "east": 20.0, "south": 72.0, "north": 82.0},
    "barents": {"west": 15.0, "east": 45.0, "south": 68.0, "north": 80.0},
}


def source_url(field: str, month: str) -> str:
    suffix = "grid_T" if field in ("votemper", "vosaline") else "grid_U" if field == "vozocrtx" else "grid_V"
    return f"{BASE}/{field}/{MEMBER}/{field}_ORAS5_1m_{month}_{suffix}_02.nc"


def build_manifest() -> dict:
    sources = [{"month": month, "field": field, "role": role, "url": source_url(field, month)} for month in MONTHS for field, role in FIELDS.items()]
    canonical_request = {
        "member": MEMBER,
        "months": list(MONTHS),
        "fields": list(FIELDS),
        "domains": DOMAINS,
    }
    digest = hashlib.sha256(json.dumps(canonical_request, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return {
        "schema": "oceanlines.oras5.arctic-entrances-request.v1",
        "status": "native_mesh_acquired_four_snapshot_transport_synthesis_executed",
        "request_sha256": digest,
        "request": canonical_request,
        "sources": sources,
        "mesh_source": f"{BASE}/mesh/mesh_mask.nc",
        "gate_contracts": [
            {
                "name": "Fram Strait",
                "candidate_geographic_line": {"latitude_deg_north": 78.8333333, "west_deg": -20.0, "east_deg": 15.0},
                "positive_normal": "northward into Arctic Ocean",
                "required_decomposition": ["western export", "central recirculation/transition", "eastern Atlantic inflow"],
                "selection_rule": "derive a land-bounded native V-face section; report whole section and all signed branches before any Atlantic Water subset",
            },
            {
                "name": "Barents Sea Opening",
                "candidate_geographic_line": {"longitude_deg_east": 20.0, "south_deg": 70.5, "north_deg": 75.0},
                "positive_normal": "eastward into Barents Sea",
                "required_decomposition": ["Norwegian Coastal Current", "central Atlantic inflow", "northern return flow"],
                "selection_rule": "choose semantics first: either a virtual-endpoint mixed U/V Fugloya-Bear observational proxy or a distinct land-bounded Norway-Svalbard model gateway; preserve branches and prevent corner duplication",
                "grid_representation_warning": "the approximate Bear Island target is a wet T cell in this ORCA025 mesh, so the observational section cannot also be a native land-bounded closure",
            },
        ],
        "calculation_contract": {
            "first_outputs": ["signed volume transport", "reference-relative advective heat transport", "temperature-salinity populations", "latitude/depth or distance/depth native-cell portrait"],
            "reference_temperature_cases_degC": [-1.9, 0.0, 2.0],
            "atlantic_water_classification": "must be declared from temperature and salinity together and reported beside, never instead of, the full signed section",
            "paired_interpretation": "compare route and heat fate only after each gateway passes its own geometry, collocation, and branch-conservation audits",
        },
        "required_audits": [
            "discover native index windows from T/U/V coordinates rather than assuming regular longitude/latitude indices",
            "re-run partial-cell face-thickness and mask consistency on both new domains",
            "verify native face orientation and section normal at every selected face",
            "challenge nearby gate placement and T-to-face collocation separately",
            "retain opposing branches and demonstrate that class/bin sums reproduce whole-section totals",
        ],
        "geometry_receipt": "research/osw-m3-oras5-arctic-gate-readiness.json",
        "section_bakeoff_receipt": "research/osw-m3-oras5-barents-section-bakeoff.json",
        "section_sensitivity_receipt": "research/osw-m3-oras5-barents-section-sensitivity.json",
        "full_depth_geometry_receipt": "research/osw-m3-oras5-arctic-section-geometry-audit.json",
        "pilot_state_receipt": "research/osw-m3-oras5-arctic-entrances-state-201802.json",
        "pilot_transport_receipt": "research/osw-m3-oras5-arctic-transport-pilot-201802.json",
        "seasonal_transport_receipt": "research/osw-m3-oras5-arctic-seasons-2018.json",
        "boundary": "February, May, August, and November 2018 state/transport snapshots now exist. The M2 surface lanes guide interpretation but do not select full-depth Atlantic Water cells. Four snapshots are not a time-weighted annual mean, climatology, convergence, or Arctic heat-delivery result.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m3-oras5-arctic-entrances-request-2018.json"))
    args = parser.parse_args()
    payload = build_manifest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {payload['status']}")


if __name__ == "__main__":
    main()

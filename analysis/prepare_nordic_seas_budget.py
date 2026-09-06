"""Freeze the Nordic Seas control-volume experiment before deriving new sections."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib


MONTHS = ("201801", "201802", "201803", "201804", "201805", "201806", "201807", "201808", "201809", "201810", "201811", "201812")
SOUTHERN_SECTION_INTENTS = (
    {
        "id": "denmark_strait",
        "name": "Denmark Strait",
        "from": {"land": "Greenland", "longitude_deg": -34.5, "latitude_deg": 66.3},
        "to": {"land": "Iceland", "longitude_deg": -24.0, "latitude_deg": 66.5},
    },
    {
        "id": "iceland_faroe",
        "name": "Iceland–Faroe",
        "from": {"land": "Iceland", "longitude_deg": -13.5, "latitude_deg": 64.3},
        "to": {"land": "Faroe", "longitude_deg": -6.8, "latitude_deg": 62.1},
    },
    {
        "id": "faroe_scotland",
        "name": "Faroe–Scotland",
        "from": {"land": "Faroe", "longitude_deg": -6.8, "latitude_deg": 61.8},
        "to": {"land": "Scotland", "longitude_deg": -4.5, "latitude_deg": 58.8},
    },
)


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def artifact(path: pathlib.Path, root: pathlib.Path) -> dict[str, object]:
    return {
        "path": path.relative_to(root).as_posix(),
        "present": path.exists(),
        "sha256": sha256_file(path) if path.exists() else None,
    }


def build(root: pathlib.Path) -> dict[str, object]:
    mesh = root / "atlas/data/oras5-nordic-seas-mesh.nc"
    barents = root / "research/osw-m3-oras5-barents-section-bakeoff.json"
    readiness = root / "research/osw-m3-oras5-arctic-section-geometry-audit.json"
    seasons = root / "research/osw-m3-oras5-arctic-seasons-2018.json"
    southern = root / "research/osw-m4-oras5-nordic-southern-sections.json"
    control = root / "research/osw-m4-oras5-nordic-control-volume.json"
    control_payload = json.loads(control.read_text(encoding="utf-8")) if control.exists() else None
    full_depth = root / "research/osw-m4-oras5-nordic-section-geometry-audit.json"
    full_depth_payload = json.loads(full_depth.read_text(encoding="utf-8")) if full_depth.exists() else None
    metrics = root / "atlas/data/oras5-nordic-t-metrics.nc"
    surface_heat = root / "atlas/data/oras5-nordic-surface-heat-2018.nc"
    surface_analysis = root / "research/osw-m4-oras5-nordic-surface-heat-2018.json"
    available_state_months = [
        month
        for month in MONTHS
        if (root / f"atlas/data/oras5-nordic-budget-state-{month}.nc").exists()
    ]
    partial_budget = root / "research/osw-m4-oras5-nordic-partial-budget-2018.json"
    column_heat = root / "atlas/data/oras5-nordic-column-heat-2018.nc"
    storage_crosscheck = root / "research/osw-m4-oras5-nordic-storage-crosscheck-2018.json"
    native_budget_audit = root / "research/osw-m4-oras5-native-budget-availability.json"
    gates = [
        {
            "id": "native_mesh",
            "label": "Combined native T/U/V mesh",
            "status": "pass" if mesh.exists() else "blocked",
            "reason": "expanded mesh spans every accepted ridge, Fram, Barents, and North Sea boundary",
        },
        {
            "id": "northern_and_eastern_sections",
            "label": "Fram + Norway–Svalbard closure",
            "status": "pass" if readiness.exists() and barents.exists() else "blocked",
            "reason": "accepted land-bounded native-face paths and full-depth internal geometry audit already exist",
        },
        {
            "id": "southern_sections",
            "label": "Southern ridge + North Sea sections",
            "status": "pass" if southern.exists() else "open",
            "reason": "native land-bounded Denmark, continuous Iceland–Scotland, and northern North Sea paths are derived; the two-part Faroe split failed closure",
        },
        {
            "id": "closed_t_cell_mask",
            "label": "Unique enclosed Nordic Seas T-cell mask",
            "status": "pass" if control_payload and control_payload["status"] == "closed_surface_control_volume" else "open",
            "reason": "12,550 wet surface T cells are enclosed by 284 unique faces without reaching a mesh edge" if control_payload and control_payload["status"] == "closed_surface_control_volume" else "the five section paths must form one gap-free, nonoverlapping boundary with represented land",
        },
        {
            "id": "full_depth_geometry",
            "label": "Five-section full-depth geometry",
            "status": "pass" if full_depth_payload and full_depth_payload["all_sections_pass"] else "open",
            "reason": "all 284 faces pass mask, width, partial-step, positive-area, and depth-bin closure checks" if full_depth_payload and full_depth_payload["all_sections_pass"] else "surface topology passes; southern and North Sea widths, partial steps, wet areas, and depth closure remain unaudited",
        },
        {
            "id": "monthly_state",
            "label": "T/S/U/V for all 12 months",
            "status": "pass" if len(available_state_months) == 12 else "open",
            "reason": f"{len(available_state_months)}/12 compact native monthly states are present; all storage cells and five boundary sections are covered" if len(available_state_months) == 12 else f"{len(available_state_months)}/12 compact native monthly states are present; monthly storage remains incomplete",
        },
        {
            "id": "cell_metrics_and_surface_flux",
            "label": "Native T-cell area + downward surface heat flux",
            "status": "pass" if metrics.exists() and surface_heat.exists() and surface_analysis.exists() else "open",
            "reason": "e1t/e2t and all twelve monthly sohefldo fields are aligned to the exact 12,550-cell mask" if metrics.exists() and surface_heat.exists() and surface_analysis.exists() else "the current subset lacks e1t/e2t and sohefldo required for storage and surface input",
        },
        {
            "id": "native_budget_terms",
            "label": "Ice, mixing, diffusion, and assimilation terms",
            "status": "open",
            "reason": "the live public ORCA025 catalog has been audited and exposes none of the required native tendency families; the offline budget must retain an unresolved remainder",
        },
    ]
    return {
        "schema": "osw.oras5.nordic-seas-budget-contract.v1",
        "status": "offline_partial_budget_ready_public_native_terms_unavailable" if native_budget_audit.exists() and storage_crosscheck.exists() else ("offline_partial_budget_ready_native_terms_open" if partial_budget.exists() and len(available_state_months) == 12 else "contract_frozen_geometry_not_ready"),
        "question": "How much Atlantic heat enters the Nordic Seas, how much crosses Fram and Barents into the Arctic, and what is transformed, stored, or omitted between those gates?",
        "control_volume": {
            "name": "Nordic Seas heat room",
            "inside": "ocean T cells north of the Greenland–Scotland Ridge, south of Fram Strait, and west of the Norway–Svalbard model closure, connected through represented wet cells",
            "boundaries": {
                "south": [
                    {"id": "denmark_strait", "name": "Denmark Strait", "source": "research/osw-m4-oras5-nordic-control-volume.json"},
                    {"id": "iceland_scotland_ridge", "name": "Iceland–Scotland Ridge continuous model closure", "source": "research/osw-m4-oras5-nordic-control-volume.json"},
                    {"id": "northern_north_sea", "name": "Northern North Sea model closure", "source": "research/osw-m4-oras5-nordic-control-volume.json"},
                ],
                "north": {
                    "id": "fram_strait",
                    "name": "Fram Strait",
                    "source": "research/osw-m3-oras5-arctic-gate-readiness.json",
                    "positive_normal": "outward from Nordic Seas, northward into Arctic Ocean",
                },
                "east": {
                    "id": "norway_svalbard",
                    "name": "Norway–Svalbard model closure",
                    "source": "research/osw-m3-oras5-barents-section-bakeoff.json",
                    "positive_normal": "outward from Nordic Seas, eastward into the Barents domain",
                },
                "land": "represented Greenland, Iceland, Faroe, Scotland/Norway, and Svalbard coast cells",
            },
            "gateway_intents": list(SOUTHERN_SECTION_INTENTS),
            "warning": "The Fugløya–Bear observational proxy is excluded because its wet virtual endpoints permit bypass flow. The original Iceland–Faroe plus Faroe–Scotland split also fails surface closure at ORCA025; one continuous Iceland–Scotland cut is used instead. Britain requires an explicit northern North Sea closure.",
        },
        "frozen_accounting": {
            "positive_flux": "outward from the Nordic Seas control volume",
            "volume_closure": "sum of signed native-face volume flux across all five ocean sections",
            "advective_heat": "rho0 * cp0 * sum((potential_temperature - reference_temperature) * signed_volume_flux)",
            "partial_budget_equation": "storage_tendency + outward_advective_heat - downward_surface_heat = unresolved_remainder",
            "reference_temperature_cases_degC": [-1.9, 0.0, 2.0, 5.0],
            "reference_invariance_gate": "heat-divergence differences between reference temperatures must equal -rho0*cp0*delta_reference*volume_imbalance",
            "required_reporting": [
                "each named section before their sum",
                "positive and negative volume branches",
                "all reference-temperature cases",
                "monthly storage and surface terms",
                "unresolved remainder without causal relabeling",
            ],
        },
        "promotion_gates": [
            "all five section paths use unique native wet faces and terminate on represented land",
            "section union plus land encloses exactly one intended connected wet T-cell component",
            "boundary has zero duplicate faces, zero gaps, and consistent outward signs",
            "full-depth masks, partial steps, widths, and areas pass the existing reconstruction audit",
            "all 12 monthly T/S/U/V states and T-cell storage metrics are checksum pinned",
            "monthly volume imbalance is reported before any reference-relative heat convergence",
            "surface heat flux is integrated over the identical T-cell mask",
            "ice, mixing, diffusion, and assimilation remain explicit missing terms unless retrieved",
        ],
        "readiness": gates,
        "readiness_summary": {
            "pass": sum(gate["status"] == "pass" for gate in gates),
            "open": sum(gate["status"] == "open" for gate in gates),
            "blocked": sum(gate["status"] == "blocked" for gate in gates),
        },
        "available_state_months": available_state_months,
        "sources": {
            "mesh": artifact(mesh, root),
            "barents_paths": artifact(barents, root),
            "arctic_geometry": artifact(readiness, root),
            "four_snapshot_synthesis": artifact(seasons, root),
            "southern_sections": artifact(southern, root),
            "closed_control_volume": artifact(control, root),
            "full_depth_geometry": artifact(full_depth, root),
            "t_cell_metrics": artifact(metrics, root),
            "surface_heat": artifact(surface_heat, root),
            "surface_heat_analysis": artifact(surface_analysis, root),
            "partial_budget": artifact(partial_budget, root),
            "column_heat": artifact(column_heat, root),
            "storage_crosscheck": artifact(storage_crosscheck, root),
            "native_budget_availability": artifact(native_budget_audit, root),
        },
        "interpretation_boundary": "The offline partial budget now includes transport, storage, surface exchange, and an independent storage cross-check. It is not model-native closure, attribution of the unresolved remainder, a climatology, or an Arctic-delivery result.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-nordic-seas-budget-contract.json"))
    args = parser.parse_args()
    payload = build(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {payload['readiness_summary']}")


if __name__ == "__main__":
    main()

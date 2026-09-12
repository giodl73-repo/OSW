"""Build a non-joining evidence synthesis for the SANT intra-state dynamics research slice."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVED_LEDGER = ROOT / "research" / "ocean-state-interior-ledger-sant-201808.json"
ASSIGNMENT = ROOT / "research" / "ocean-state-interior-sant-current-geometry-assignment-2026-09-12.json"
PATHWAYS = ROOT / "research" / "ocean-state-interior-sant-pathways-current-geometry-2018.json"
VERTICAL = ROOT / "research" / "ocean-state-interior-sant-vertical-structure-current-geometry-2018.json"
DENSITY = ROOT / "research" / "ocean-state-interior-sant-density-structure-current-geometry-2018.json"
SURFACE_STORAGE = ROOT / "research" / "ocean-state-sant-current-geometry-surface-storage-2018.json"
PARTIAL_PERIMETER = ROOT / "research" / "ocean-state-sant-current-geometry-partial-perimeter-2018.json"
CLOSED_BOX = ROOT / "research" / "ocean-state-sant-closed-box-horizontal-account-2018.json"
CLOSED_BOX_INVENTORY = ROOT / "research" / "ocean-state-sant-closed-box-inventory-change-screen-2018.json"
VERTICAL_SOURCE_AUDIT = ROOT / "research" / "ocean-state-sant-vertical-process-source-audit-2026-09-12.json"
CUSTODY_AUDIT = ROOT / "research" / "ocean-state-interior-source-custody-audit-2026-09-12.json"
OUTPUT = ROOT / "research" / "ocean-state-intra-state-dynamics-synthesis-sant-2018.json"
BROWSER = ROOT / "exchange" / "interior-dynamics.js"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def receipt(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def build(archived_ledger: Path = ARCHIVED_LEDGER, assignment: Path = ASSIGNMENT, pathways: Path = PATHWAYS, vertical: Path = VERTICAL, density: Path = DENSITY, surface_storage: Path = SURFACE_STORAGE, partial_perimeter: Path = PARTIAL_PERIMETER, closed_box: Path = CLOSED_BOX, closed_box_inventory: Path = CLOSED_BOX_INVENTORY, vertical_source_audit: Path = VERTICAL_SOURCE_AUDIT, custody_audit: Path = CUSTODY_AUDIT) -> dict:
    archived_ledger, assignment, pathways, vertical, density, surface_storage, partial_perimeter, closed_box, closed_box_inventory, vertical_source_audit, custody_audit = map(Path, (archived_ledger, assignment, pathways, vertical, density, surface_storage, partial_perimeter, closed_box, closed_box_inventory, vertical_source_audit, custody_audit))
    ledger, membership, pathway, profile, density_screen, surface_account, perimeter, box, inventory, vertical_audit, audit = map(load, (archived_ledger, assignment, pathways, vertical, density, surface_storage, partial_perimeter, closed_box, closed_box_inventory, vertical_source_audit, custody_audit))
    if membership["status"] != "separate_unjoined_source_family" or not pathway["join_status"].startswith("not_joined") or not profile["join_status"].startswith("not_joined"):
        raise ValueError("dynamics source family must remain separate from archived contents")
    if pathway["membership_source"]["sha256"] != sha256(assignment) or profile["membership_source"]["sha256"] != sha256(assignment) or density_screen["source_family_manifest"]["sha256"] != sha256(ROOT / density_screen["source_family_manifest"]["path"]) or surface_account["assignment"]["sha256"] != sha256(assignment):
        raise ValueError("dynamic screens must bind to the same pinned membership assignment")
    seasonal_relative = [{"valid_time": month["valid_time"], "seed_results": [{key: result[key] for key in ("seed", "mean_control_separation_change_km", "mean_final_temperature_contrast_c")} for result in month["relative_motion"]]} for month in pathway["months"]]
    central_vertical = [{"valid_time": month["valid_time"], "interfaces": next(profile_item for profile_item in month["profiles"] if profile_item["seed"] == "central")["interfaces"]} for month in profile["months"]]
    return {
        "schema": "osw-ocean-state-intra-state-dynamics-synthesis-v1",
        "status": "coverage_complete_for_current_custodied_evidence_not_complete_physical_dynamics",
        "state": {"geometry_edition": "longhurst-v4-54", "province": "SANT"},
        "source_families": {
            "archived_contents": {"receipt": receipt(archived_ledger), "status": "archived_geometry_2018_contents_only", "permitted_use": "temperature contents and static geometry overlay"},
            "current_geometry_dynamics": {"assignment": receipt(assignment), "pathway_screen": receipt(pathways), "vertical_structure_screen": receipt(vertical), "density_structure_screen": receipt(density), "surface_storage_account": receipt(surface_storage), "partial_perimeter_screen": receipt(partial_perimeter), "closed_box_horizontal_account": receipt(closed_box), "closed_box_inventory_screen": receipt(closed_box_inventory), "status": "separate_unjoined_source_family", "permitted_use": "bounded local kinematics, T/S density structure, partial perimeter flux, open surface/storage evidence, and closed-horizontal-box terms only"},
            "custody_audit": receipt(custody_audit),
            "vertical_process_source_audit": receipt(vertical_source_audit),
        },
        "relation_coverage": [
            {"relation": "occupancy", "status": "supported_reference_assignment", "evidence": "Pinned native SANT membership has 6,147 T-cell centres and 5,614 guarded interior-core cells.", "non_claim": "A geographic assignment is not a material boundary or water-mass identity."},
            {"relation": "co_occurrence", "status": "supported_bounded_model_screen", "evidence": "Each kinematic support point has co-located temperature; T/S profiles retain fixed numerical-density-stratum occupancy.", "non_claim": "Eulerian samples and numerical strata are not parcel thermodynamics, causal coupling, or water-mass names."},
            {"relation": "vertical_structure", "status": "supported_bounded_model_screen", "evidence": "Three fixed seeds have temperature, salinity-derived TEOS-10 density, and horizontal-velocity proxies at nearest 0, 100, 200, and 1,000 m T-level midpoints in four months.", "non_claim": "Temperature/density gradients and horizontal shear do not diagnose vertical exchange."},
            {"relation": "lateral_interior_pathway", "status": "supported_bounded_kinematic_screen", "evidence": "Three geometry-predeclared seeds and eleven available cardinal controls were advanced for five days in four monthly-mean fields; all remained in guarded support.", "non_claim": "This is not an observed Lagrangian or material trajectory, retention result, or transport."},
            {"relation": "local_relative_motion", "status": "supported_bounded_kinematic_screen", "evidence": "Seed/control separations can contract or expand under the declared screen (e.g. western May -0.375 km; central May +10.728 km).", "non_claim": "Relative separation is not horizontal convergence, accumulation, or flux divergence."},
            {"relation": "vertical_transfer", "status": "not_supported", "required_evidence": "Vertical velocity or diapycnal flux, plus compatible density/mixing information or a closed budget.", "reason": f"The direct-source audit result is {vertical_audit['result']}; the custodied Drake state files expose no native vertical velocity."},
            {"relation": "surface_forcing_and_storage", "status": "supported_open_account", "evidence": "All 12 monthly surface heat, freshwater, and column-heat-content fields are area-integrated over current SANT membership.", "non_claim": "Surface/storage evidence without matched lateral/vertical terms is not a closed budget or attribution."},
            {"relation": "partial_lateral_perimeter", "status": "supported_partial_perimeter_screen", "evidence": "All 474 in-domain membership faces are screened with adjacent T/S collocation; 176 subset-edge sides remain unmeasured.", "non_claim": "Partial gross and net fluxes are not a closed lateral boundary or convergence."},
            {"relation": "interior_convergence", "status": "horizontal_advective_term_and_inventory_endpoints_supported_total_convergence_not_supported", "evidence": "A 16×16 geometry-selected box and three one-cell controls have complete 64-face horizontal perimeters, horizontal advective terms, and fixed column-heat-content endpoints in four months.", "required_evidence": "Matched native vertical, mixing/diffusion, tendency/assimilation terms and compatible time support for total convergence or budget closure.", "reason": "The endpoint differences are not native tendencies or residuals, and the closed box measures one horizontal advective term only; vertical and other terms remain absent."},
            {"relation": "transformation", "status": "density_strata_supported_transformation_not_supported", "required_evidence": "Compatible class-volume fluxes through a closed control volume, with a declared density-class convention.", "reason": "TEOS-10 density strata now exist, but no class-volume flux or vertical transfer term is available."},
            {"relation": "event_perturbation", "status": "not_supported", "required_evidence": "A temporally and spatially matched before/during/after event account on this source family.", "reason": "No compatible SANT 2018 event account is custodied."},
        ],
        "bounded_results": {"seasonal_relative_motion": seasonal_relative, "central_seed_vertical_interfaces": central_vertical, "central_seed_density_interfaces": [{"valid_time": month["valid_time"], "interfaces": next(item for item in month["profiles"] if item["seed"] == "central")["interfaces"]} for month in density_screen["months"]], "partial_perimeter_geometry": perimeter["geometry"], "surface_storage_month_count": len(surface_account["monthly_account"]), "closed_box_horizontal_advective_terms": [{"valid_time": month["valid_time"], "primary": month["outcomes"][0]["horizontal_boundary"]} for month in box["months"]], "closed_box_primary_inventory_endpoints": next(item for item in inventory["boxes"] if item["box"] == "primary")},
        "research_conclusion": "The intra-state dynamics research slice is complete as an evidence-bounded map: occupancy, local kinematics, relative motion, T/S density structure, a partial perimeter, an open surface/storage account, and closed-horizontal-box advective and inventory-endpoint terms are separately receipted. Vertical transfer, total convergence, transformation flux, and event perturbation remain explicit unsupported mechanisms with named acquisition gates. No numerical value is joined across the archived and current-geometry source families.",
        "boundary": "This synthesis is a relation-by-relation evidence map, not a state-wide dynamical model, water-mass classification, transport account, closure calculation, causal graph, or geometry bridge.",
    }


def validate(payload: dict) -> None:
    required = {"occupancy", "co_occurrence", "vertical_structure", "lateral_interior_pathway", "local_relative_motion", "surface_forcing_and_storage", "partial_lateral_perimeter", "vertical_transfer", "interior_convergence", "transformation", "event_perturbation"}
    coverage = {item["relation"]: item for item in payload["relation_coverage"]}
    if payload["status"] != "coverage_complete_for_current_custodied_evidence_not_complete_physical_dynamics" or set(coverage) != required:
        raise ValueError("synthesis must cover every registered relation without claiming full physical dynamics")
    if any("not_supported" in item["status"] and not item.get("required_evidence") for item in coverage.values()):
        raise ValueError("unsupported relations require an acquisition gate")
    if payload["source_families"]["current_geometry_dynamics"]["status"] != "separate_unjoined_source_family":
        raise ValueError("source-family separation is required")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--browser", type=Path, default=BROWSER)
    args = parser.parse_args()
    payload = build()
    validate(payload)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    args.browser.write_text("window.OSW_INTRA_STATE_DYNAMICS = " + json.dumps(payload, separators=(",", ":")) + ";\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

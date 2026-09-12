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
CUSTODY_AUDIT = ROOT / "research" / "ocean-state-interior-source-custody-audit-2026-09-12.json"
OUTPUT = ROOT / "research" / "ocean-state-intra-state-dynamics-synthesis-sant-2018.json"
BROWSER = ROOT / "exchange" / "interior-dynamics.js"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def receipt(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def build(archived_ledger: Path = ARCHIVED_LEDGER, assignment: Path = ASSIGNMENT, pathways: Path = PATHWAYS, vertical: Path = VERTICAL, custody_audit: Path = CUSTODY_AUDIT) -> dict:
    archived_ledger, assignment, pathways, vertical, custody_audit = map(Path, (archived_ledger, assignment, pathways, vertical, custody_audit))
    ledger, membership, pathway, profile, audit = map(load, (archived_ledger, assignment, pathways, vertical, custody_audit))
    if membership["status"] != "separate_unjoined_source_family" or not pathway["join_status"].startswith("not_joined") or not profile["join_status"].startswith("not_joined"):
        raise ValueError("dynamics source family must remain separate from archived contents")
    if pathway["membership_source"]["sha256"] != sha256(assignment) or profile["membership_source"]["sha256"] != sha256(assignment):
        raise ValueError("dynamic screens must bind to the same pinned membership assignment")
    seasonal_relative = [{"valid_time": month["valid_time"], "seed_results": [{key: result[key] for key in ("seed", "mean_control_separation_change_km", "mean_final_temperature_contrast_c")} for result in month["relative_motion"]]} for month in pathway["months"]]
    central_vertical = [{"valid_time": month["valid_time"], "interfaces": next(profile_item for profile_item in month["profiles"] if profile_item["seed"] == "central")["interfaces"]} for month in profile["months"]]
    return {
        "schema": "osw-ocean-state-intra-state-dynamics-synthesis-v1",
        "status": "coverage_complete_for_current_custodied_evidence_not_complete_physical_dynamics",
        "state": {"geometry_edition": "longhurst-v4-54", "province": "SANT"},
        "source_families": {
            "archived_contents": {"receipt": receipt(archived_ledger), "status": "archived_geometry_2018_contents_only", "permitted_use": "temperature contents and static geometry overlay"},
            "current_geometry_dynamics": {"assignment": receipt(assignment), "pathway_screen": receipt(pathways), "vertical_structure_screen": receipt(vertical), "status": "separate_unjoined_source_family", "permitted_use": "bounded local kinematics, co-located temperature, and vertical structure only"},
            "custody_audit": receipt(custody_audit),
        },
        "relation_coverage": [
            {"relation": "occupancy", "status": "supported_reference_assignment", "evidence": "Pinned native SANT membership has 6,147 T-cell centres and 5,614 guarded interior-core cells.", "non_claim": "A geographic assignment is not a material boundary or water-mass identity."},
            {"relation": "co_occurrence", "status": "supported_bounded_model_screen", "evidence": "Each kinematic support point has a co-located monthly surface temperature sample; local seed/control temperature contrasts are retained.", "non_claim": "Eulerian samples along a screen are not parcel thermodynamics or causal coupling."},
            {"relation": "vertical_structure", "status": "supported_bounded_model_screen", "evidence": "Three fixed seeds have temperature and horizontal-velocity proxies at nearest 0, 100, 200, and 1,000 m T-level midpoints in four months.", "non_claim": "Temperature gradients and horizontal shear do not diagnose vertical exchange."},
            {"relation": "lateral_interior_pathway", "status": "supported_bounded_kinematic_screen", "evidence": "Three geometry-predeclared seeds and eleven available cardinal controls were advanced for five days in four monthly-mean fields; all remained in guarded support.", "non_claim": "This is not an observed Lagrangian or material trajectory, retention result, or transport."},
            {"relation": "local_relative_motion", "status": "supported_bounded_kinematic_screen", "evidence": "Seed/control separations can contract or expand under the declared screen (e.g. western May -0.375 km; central May +10.728 km).", "non_claim": "Relative separation is not horizontal convergence, accumulation, or flux divergence."},
            {"relation": "vertical_transfer", "status": "not_supported", "required_evidence": "Vertical velocity or diapycnal flux, plus compatible density/mixing information or a closed budget.", "reason": "The custodied Drake state files expose temperature, zonal velocity, and meridional velocity only."},
            {"relation": "interior_convergence", "status": "not_supported", "required_evidence": "A closed control-volume geometry with matched native boundary, surface, storage, and residual terms.", "reason": "The trajectory screen has no closed volume or flux accounting."},
            {"relation": "transformation", "status": "not_supported", "required_evidence": "Salinity/density class definition and compatible class-volume fluxes.", "reason": "Temperature alone cannot define or quantify water-mass transformation."},
            {"relation": "event_perturbation", "status": "not_supported", "required_evidence": "A temporally and spatially matched before/during/after event account on this source family.", "reason": "No compatible SANT 2018 event account is custodied."},
        ],
        "bounded_results": {"seasonal_relative_motion": seasonal_relative, "central_seed_vertical_interfaces": central_vertical},
        "research_conclusion": "The intra-state dynamics research slice is complete as an evidence-bounded map: supported geographic occupancy, lateral kinematics, local relative motion, temperature co-occurrence, and vertical structure are individually receipted; transfer, convergence, transformation, and event perturbation remain explicit unsupported relations with named acquisition gates. No numerical value is joined across the archived and current-geometry source families.",
        "boundary": "This synthesis is a relation-by-relation evidence map, not a state-wide dynamical model, water-mass classification, transport account, closure calculation, causal graph, or geometry bridge.",
    }


def validate(payload: dict) -> None:
    required = {"occupancy", "co_occurrence", "vertical_structure", "lateral_interior_pathway", "local_relative_motion", "vertical_transfer", "interior_convergence", "transformation", "event_perturbation"}
    coverage = {item["relation"]: item for item in payload["relation_coverage"]}
    if payload["status"] != "coverage_complete_for_current_custodied_evidence_not_complete_physical_dynamics" or set(coverage) != required:
        raise ValueError("synthesis must cover every registered relation without claiming full physical dynamics")
    if any(item["status"] == "not_supported" and not item.get("required_evidence") for item in coverage.values()):
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

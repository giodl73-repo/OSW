"""Build the complete per-border evidence matrix and bounded dispositions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

try:
    from acquire_ocean_state_hydrography_pilot import sha256_text_file
except ImportError:  # pragma: no cover
    from analysis.acquire_ocean_state_hydrography_pilot import sha256_text_file


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def hydro_summary(records: list[dict]) -> dict:
    if not records:
        return {"status": "unknown", "reason": "no admitted matched province-property-depth-time records"}
    differences = np.asarray([item["first_minus_second_median_degC"] for item in records], dtype=float)
    overlaps = np.asarray([item["interquartile_overlap_degC"] for item in records], dtype=float)
    return {
        "status": "model_screen_temperature_only",
        "comparison_count": len(records),
        "median_absolute_median_difference_degC": round(float(np.median(np.abs(differences))), 6),
        "minimum_iqr_overlap_degC": round(float(overlaps.min()), 6),
        "maximum_iqr_overlap_degC": round(float(overlaps.max()), 6),
        "sign_consistency_fraction": round(float(max(np.mean(differences > 0), np.mean(differences < 0))), 6),
        "limits": "descriptive ORAS5 temperature contrasts; spatial autocorrelation and multiple comparisons unresolved",
    }


def build(root: Path = ROOT) -> dict:
    root = Path(root)
    paths = {
        "policy": root / "research/ocean-state-zoning-disposition-policy-v1.json",
        "adjacency": root / "research/longhurst-2007-province-adjacency.json",
        "hypsometry": root / "research/longhurst-2007-province-hypsometric-fingerprints.json",
        "contents": root / "research/ocean-state-hydrography-pilot-2018.json",
        "exchange": root / "research/ocean-state-boundary-exchange-pilot-2018.json",
        "stability": root / "research/ocean-state-boundary-stability-pilot-2018.json",
        "events": root / "research/ocean-event-state-route-2026.json",
    }
    data = {name: load(path) for name, path in paths.items()}
    if data["policy"]["status"] != "frozen_before_matrix_generation":
        raise ValueError("disposition policy must be frozen before synthesis")
    contents_by_edge = {}
    for record in data["contents"]["adjacent_contrasts"]:
        contents_by_edge.setdefault(record["edge_id"], []).append(record)
    event_edges = {item["source_graph_edge"]: item for item in data["events"]["lineage_family_route"]["crossing_candidates"]}
    tested_edge = data["exchange"]["selection"]["edge_id"]
    matrix = []
    for edge in data["adjacency"]["edges"]:
        edge_id = edge["edge_id"]
        first, second = edge["provinces"]
        exchange = {"status": "unknown", "reason": "not measured in Stage 4"}
        stability = {"status": "unknown", "reason": "not tested in Stage 5"}
        controls = {"status": "unknown", "reason": "no matched physical test"}
        disposition = "unknown"
        rationale = "Only source geometry and sampled depth character are global; physical-boundary disposition criteria are incomplete."
        if edge_id == tested_edge:
            exchange = {
                "status": "bounded_ORAS5_native_face_pilot",
                "measured_faces": data["exchange"]["geometry"]["measured_matched_face_count"],
                "source_faces": data["exchange"]["geometry"]["source_boundary_face_count"],
                "seasonal_volume_sign_reversal": data["exchange"]["summary"]["seasonal_volume_sign_reversal"],
                "net_volume_Sv_by_month": data["exchange"]["summary"]["net_volume_Sv_by_month"],
                "limits": data["exchange"]["boundary"],
            }
            stability = {
                "status": data["stability"]["summary"]["temperature_front_disposition"],
                "static_edge_match_fraction": data["stability"]["summary"]["static_edge_match_fraction"],
                "matched_season_fraction": data["stability"]["summary"]["matched_season_fraction"],
                "surface_to_depth_direction_agreement": data["stability"]["summary"]["surface_to_depth_temperature_contrast_direction_agreement"],
                "interannual": data["stability"]["summary"]["interannual_stability"],
            }
            controls = {
                "status": "tested_no_static_advantage",
                "exchange_control_net_Sv_by_month": data["exchange"]["summary"]["net_control_volume_Sv_by_month"],
                "temperature_front_static_advantage_fraction": data["stability"]["summary"]["static_advantage_over_control_fraction"],
            }
            negative_tests = int(controls["temperature_front_static_advantage_fraction"] <= 0) + int(stability["static_edge_match_fraction"] == 0)
            if negative_tests >= 2:
                disposition = "demote"
                rationale = "The tested segment has no persistent temperature-front match and no advantage over its displaced control; demote only its physical-boundary candidacy while retaining the source reference edge."
        event = {"status": "unknown", "reason": "no admitted event transition on this graph edge"}
        if edge_id in event_edges:
            candidate = event_edges[edge_id]
            event = {"status": "geometric_lineage_transition_only", "from": candidate["from"], "to": candidate["to"], "intersection_pixels": candidate["intersection_pixels"], "source_retained_fraction": candidate["source_retained_fraction"], "volume_exchange": "unsupported", "heat_transport": "unsupported"}
        missing = []
        if hydro_summary(contents_by_edge.get(edge_id, []))["status"] == "unknown": missing.append("matched hydrographic contents")
        if exchange["status"] == "unknown": missing.append("native-grid exchange")
        if stability["status"] == "unknown": missing.append("seasonal/multiyear boundary stability")
        missing.extend(["two independent observed physical fields", "interannual support", "second-product sensitivity", "retention or closed-volume evidence"])
        matrix.append({
            "edge_id": edge_id,
            "provinces": [first, second],
            "geometry": {"status": "source_backed_reference_edge", "shared_boundary_length_km": edge["shared_boundary_length_km"], "sampled_grid_support": edge["sampled_grid_support"], "physical_boundary_class": edge["physical_boundary_class"]},
            "hypsometry": {"status": "sampled_global_depth_character_available", "first": data["hypsometry"]["provinces"][first], "second": data["hypsometry"]["provinces"][second], "meaning": "adjacent depth character; not boundary identity"},
            "hydrographic_content": hydro_summary(contents_by_edge.get(edge_id, [])),
            "exchange": exchange,
            "stability": stability,
            "controls": controls,
            "event_route": event,
            "gate_dependence": {"status": "unknown", "reason": "no source-edge-specific gateway/topographic sensitivity admitted"},
            "uncertainty": {"status": "incomplete", "known_sensitivities": [item for item in ("tracer collocation and thermal reference" if edge_id == tested_edge else "", "event identity policy" if edge_id in event_edges else "") if item], "missing": missing},
            "disposition": disposition,
            "rationale": rationale,
            "decision_rule": data["policy"]["rules"][disposition],
            "falsification_or_upgrade": (
                "Demotion would be overturned by multiyear alignment in at least two independent physical fields plus exchange or retention behavior distinguishable from matched controls."
                if disposition == "demote"
                else "Unknown changes only when the complete frozen rule for retain, merge, split, move, or demote is satisfied; one new positive or negative signal is insufficient."
            ),
            "scope": "entire source edge remains reference geography; physical interpretation is unknown except the bounded 16-face SANT--SSTC segment",
        })

    counts = {name: sum(item["disposition"] == name for item in matrix) for name in data["policy"]["allowed_dispositions"]}
    return {
        "schema": "osw-ocean-state-zoning-evidence-matrix-v1",
        "status": "stage_7_bounded_synthesis_complete_no_source_geography_revision",
        "policy": {"path": paths["policy"].relative_to(root).as_posix(), "sha256": sha256_text_file(paths["policy"]), "frozen_before_matrix": True},
        "summary": {"edge_count": len(matrix), "disposition_counts": counts, "tested_physical_segment_count": 1, "source_reference_edge_changes": 0, "candidate_physical_overlay_changes": 1},
        "matrix": matrix,
        "candidate_revised_geography": {
            "source_edition": "longhurst-v4-54",
            "source_geometry_changes": [],
            "physical_overlay_annotations": [{"edge_id": tested_edge, "scope": "16 of 18 native faces in the 2018 Drake regional subset", "action": "demote_from_persistent_physical_boundary_candidate", "source_reference_edge": "retained"}],
            "display_rule": "show beside the unchanged source edition; never substitute it for the source geometry",
        },
        "public_finding": "The program establishes a reproducible border-testing method, not a new global zoning. Of 128 source edges, 127 remain physically unknown. One bounded SANT--SSTC segment is demoted as a persistent physical-boundary candidate because its exchange resembles a displaced control and no tested temperature front stays on the line. The source reference edge remains.",
        "approval": {"repository_roles": "implementation and claim-discipline review only", "owner": "not_requested_for_scientific_adoption", "external_scientific_review": "not_conducted", "publication": "not_authorized"},
        "sources": {name: {"path": path.relative_to(root).as_posix(), "canonical_lf_sha256": sha256_text_file(path)} for name, path in paths.items()},
        "boundary": "No automated zoning revision is adopted. Unknown is the dominant evidence result. The sole demotion is segment- and claim-specific and cannot delete or redraw the Longhurst source edge.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=Path("research/ocean-state-zoning-evidence-matrix.json"))
    parser.add_argument("--browser-output", type=Path, default=Path("exchange/decisions.js"))
    args = parser.parse_args()
    result = build(args.root)
    output = args.output if args.output.is_absolute() else args.root / args.output
    browser = args.browser_output if args.browser_output.is_absolute() else args.root / args.browser_output
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    browser.write_text("window.OSW_DECISIONS = " + json.dumps(result, separators=(",", ":")) + ";\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()

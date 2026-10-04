"""Materialize every named-current × OSW-state atlas relation explicitly.

The source arrows and OSW lines are map geometry; none is an observed
current-core footprint. A locator point indexes a state without proving flow.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
OUTPUT = RESEARCH / "ocean-current-state-relation-matrix.json"

EVIDENCE = (
    ("stable_cartographic_current_crossings", "cartographic_arrow_crossing", "cartographic"),
    ("schematic_current_centerline_crossings", "osw_schematic_line_crossing", "motion"),
    ("editorial_nasa_current_line_crossings", "osw_editorial_nasa_line_crossing", "motion"),
    ("editorial_named_current_line_crossings", "osw_editorial_named_line_crossing", "motion"),
    ("width_sensitive_cartographic_contacts", "width_sensitive_map_contact", "cartographic"),
    ("current_locator_candidates", "editorial_locator_candidate", "motion"),
)


def read(name: str) -> dict:
    return json.loads((RESEARCH / name).read_text(encoding="utf-8"))


def build() -> dict:
    currents = read("ocean-current-almanac.json")
    motion = read("ocean-motion-state-join.json")
    cartographic = read("cartographic-ocean-current-state-join.json")
    ids = [item["id"] for item in currents["entries"]]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate current IDs")
    codes = sorted(motion["states"])
    if set(codes) != set(cartographic["states"]):
        raise ValueError("Motion and cartographic joins differ in OSW states")
    for code in codes:
        for field, _, source in EVIDENCE:
            entries = (cartographic if source == "cartographic" else motion)["states"][code][field]
            unknown = set(entries) - set(ids)
            if unknown:
                raise ValueError(f"Unknown currents in {code}/{field}: {sorted(unknown)}")
    arrow_refs = {}
    for arrow in cartographic["arrows"]:
        current_id = arrow["osw_current_id"]
        if current_id is None:
            continue
        for field, status in (("stable_state_codes", "stable"), ("width_sensitive_state_codes", "width_sensitive")):
            for code in arrow[field]:
                arrow_refs.setdefault((current_id, code), {"stable": [], "width_sensitive": []})[status].append(arrow["source_arrow_id"])
    state_rows = {}
    current_rows = {item["id"]: {"name": item["name"], "states_by_relation": {status: [] for _, status, _ in EVIDENCE}, "unresolved_states": []}
                    for item in currents["entries"]}
    linked = 0
    for code in codes:
        relations = {}
        for current_id in ids:
            evidence = [field for field, _, source in EVIDENCE
                        if current_id in (cartographic if source == "cartographic" else motion)["states"][code][field]]
            refs = arrow_refs.get((current_id, code), {"stable": [], "width_sensitive": []})
            if bool(refs["stable"]) != ("stable_cartographic_current_crossings" in evidence):
                raise ValueError(f"Stable arrow references differ for {current_id}/{code}")
            if bool(refs["width_sensitive"] and not refs["stable"]) != ("width_sensitive_cartographic_contacts" in evidence):
                raise ValueError(f"Width-sensitive arrow references differ for {current_id}/{code}")
            relation = next((status for field, status, _ in EVIDENCE if field in evidence), "unresolved")
            linked += bool(evidence)
            relations[current_id] = {
                "atlas_relation": relation,
                "evidence_kinds": evidence,
                "cartographic_source_arrow_ids": refs,
                "physical_relation": "unknown_no_observed_current_core_footprint",
            }
            if relation == "unresolved":
                current_rows[current_id]["unresolved_states"].append(code)
            else:
                current_rows[current_id]["states_by_relation"][relation].append(code)
        state_rows[code] = {
            "name": motion["states"][code]["name"],
            "currents": relations,
            "atlas_linked_current_count": sum(bool(row["evidence_kinds"]) for row in relations.values()),
        }
    return {
        "schema": "osw.almanac.ocean-current-state-relation-matrix.v1",
        "current_ledger": "research/ocean-current-almanac.json",
        "motion_state_join": "research/ocean-motion-state-join.json",
        "cartographic_state_join": "research/cartographic-ocean-current-state-join.json",
        "cartographic_source_layer": cartographic["source_layer"],
        "cartographic_source_geojson_sha256": cartographic["source_geojson_sha256"],
        "state_geometry": motion["state_geometry"],
        "status_precedence": [field for field, _, _ in EVIDENCE],
        "status_by_evidence_kind": {field: status for field, status, _ in EVIDENCE},
        "method": "For each current and coast-masked OSW state, preserve every existing cartographic-arrow, schematic-line, editorial-line, and locator-point relation. Cartographic decisions retain the contributing source arrow IDs. The first listed evidence kind labels the atlas relation. Reverse current-first indexes are derived from the same decisions.",
        "claim_limit": "An unresolved pair is not an absence claim. Cartographic arrows and OSW lines are map geometry, not observed current-core paths; locator points are weaker still. Physical passage, intersection, and containment remain unknown without a source-delineated current footprint and a compatible state definition.",
        "current_count": len(ids),
        "state_count": len(codes),
        "pair_count": len(ids) * len(codes),
        "atlas_linked_pair_count": linked,
        "states": state_rows,
        "currents": current_rows,
    }


def main() -> None:
    result = build()
    OUTPUT.write_text(json.dumps(result, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {result['pair_count']} current/state pairs; {result['atlas_linked_pair_count']} have atlas evidence")


if __name__ == "__main__":
    main()

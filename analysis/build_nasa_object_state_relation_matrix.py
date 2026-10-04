"""Materialize every NASA identified object × OSW state relation explicitly."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
OUTPUT = RESEARCH / "nasa-object-state-relation-matrix.json"

EVIDENCE_ORDER = (
    "cartographic_current_crossings",
    "schematic_current_crossings",
    "schematic_object_crossings",
    "editorial_current_line_crossings",
    "width_sensitive_cartographic_contacts",
    "object_locator_candidates",
)
STATUS_BY_KIND = {
    "cartographic_current_crossings": "cartographic_arrow_crossing",
    "schematic_current_crossings": "osw_schematic_current_crossing",
    "schematic_object_crossings": "osw_schematic_object_gate_crossing",
    "editorial_current_line_crossings": "osw_editorial_current_crossing",
    "width_sensitive_cartographic_contacts": "width_sensitive_map_contact",
    "object_locator_candidates": "editorial_locator_candidate",
}


def read(name: str) -> dict:
    return json.loads((RESEARCH / name).read_text(encoding="utf-8"))


def main() -> None:
    catalog = read("nasa-perpetual-ocean-objects.json")
    forms = read("nasa-perpetual-ocean-motion-forms.json")
    crosswalk = read("nasa-ocean-object-state-crosswalk.json")
    current_matrix = read("ocean-current-state-relation-matrix.json")
    state_ledger = read("ocean-motion-state-join.json")
    object_ids = [item["id"] for item in catalog["objects"]]
    state_codes = sorted(crosswalk["states"])
    if set(object_ids) != set(crosswalk["objects"]):
        raise ValueError("NASA crosswalk and object ledger differ")
    if set(state_codes) != set(state_ledger["states"]):
        raise ValueError("NASA crosswalk and OSW state ledger differ")
    if set(state_codes) != set(current_matrix["states"]):
        raise ValueError("NASA and named-current state matrices differ")
    context_edges = {object_id: [] for object_id in object_ids}
    for item in catalog["objects"]:
        for member_id in item.get("example_object_ids", []):
            context_edges[item["id"]].append((member_id, "nasa_named_example"))
        for relation in item.get("system_context", []):
            if relation["relation"] != "narrated_part_of":
                raise ValueError(f"Unreviewed NASA system-context relation on {item['id']}")
            context_edges[relation["system_id"]].append((item["id"], "nasa_narrated_part_of_system"))
    for relation in forms["class_relations"]:
        context_edges[relation["parent_id"]].append((relation["child_id"], "osw_taxonomic_child"))
    if any(member_id not in object_ids for edges in context_edges.values() for member_id, _ in edges):
        raise ValueError("NASA contextual member points outside the object ledger")
    rows = {}
    linked_pairs = 0
    contextual_pairs = 0
    for code in state_codes:
        relations = {}
        for object_id in object_ids:
            object_join = crosswalk["objects"][object_id]
            evidence = object_join["state_evidence"]
            kinds = [kind for kind in EVIDENCE_ORDER if code in evidence[kind]]
            current_id = object_join["almanac_current_id"]
            if current_id:
                current_relation = current_matrix["states"][code]["currents"][current_id]
                arrow_ids = current_relation["cartographic_source_arrow_ids"]
                if ("cartographic_current_crossings" in kinds) != bool(arrow_ids["stable"]):
                    raise ValueError(f"Stable arrow evidence differs for {object_id}/{code}")
                if ("width_sensitive_cartographic_contacts" in kinds) != (
                    bool(arrow_ids["width_sensitive"]) and not arrow_ids["stable"]
                ):
                    raise ValueError(f"Width-sensitive arrow evidence differs for {object_id}/{code}")
            else:
                arrow_ids = {"stable": [], "width_sensitive": []}
            linked_pairs += bool(kinds)
            contextual_members = []
            for member_id, relation in context_edges[object_id]:
                member_evidence = crosswalk["objects"][member_id]["state_evidence"]
                member_kinds = [kind for kind in EVIDENCE_ORDER if code in member_evidence[kind]]
                if member_kinds:
                    contextual_members.append({"object_id": member_id, "relation": relation, "evidence_kinds": member_kinds})
            contextual_pairs += bool(contextual_members)
            relations[object_id] = {
                "atlas_relation": STATUS_BY_KIND[kinds[0]] if kinds else "unresolved",
                "evidence_kinds": kinds,
                "cartographic_source_arrow_ids": arrow_ids,
                "contextual_members": contextual_members,
                "physical_relation": "unknown_no_nasa_feature_footprint",
            }
        rows[code] = {"name": state_ledger["states"][code]["name"], "objects": relations,
                      "atlas_linked_object_count": sum(bool(row["evidence_kinds"]) for row in relations.values())}
    result = {
        "schema": "osw.almanac.nasa-object-state-relation-matrix.v1",
        "object_ledger": "research/nasa-perpetual-ocean-objects.json",
        "crosswalk": "research/nasa-ocean-object-state-crosswalk.json",
        "current_state_matrix": "research/ocean-current-state-relation-matrix.json",
        "cartographic_source_layer": current_matrix["cartographic_source_layer"],
        "cartographic_source_geojson_sha256": current_matrix["cartographic_source_geojson_sha256"],
        "motion_forms": "research/nasa-perpetual-ocean-motion-forms.json",
        "status_precedence": list(EVIDENCE_ORDER),
        "status_by_evidence_kind": STATUS_BY_KIND,
        "method": "For every audited NASA object and every OSW coast-masked state, carry all existing cartographic, schematic, editorial, and point-locator evidence from the crosswalk. Cartographic decisions carry the independent source arrow IDs through the named-current matrix. The first evidence kind in precedence order labels the atlas relation; the complete evidence list is retained. Separately report direct named-example, narrated system-member, and OSW taxonomic-child objects with their own atlas evidence in that state.",
        "claim_limit": "An unlinked pair is unresolved, not evidence that an object is absent. Contextual members show where a separately indexed example has atlas evidence; they do not transfer a class or system footprint to that state. Even linked pairs have no NASA-published individual feature footprint, so physical crossing, containment, and intersection remain unknown. Map lines and locators are separate atlas evidence types.",
        "object_count": len(object_ids),
        "state_count": len(state_codes),
        "pair_count": len(object_ids) * len(state_codes),
        "atlas_linked_pair_count": linked_pairs,
        "contextual_pair_count": contextual_pairs,
        "states": rows,
    }
    OUTPUT.write_text(json.dumps(result, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {result['pair_count']} NASA object/state pairs; {linked_pairs} have direct atlas evidence and {contextual_pairs} have contextual members")
if __name__ == "__main__":
    main()

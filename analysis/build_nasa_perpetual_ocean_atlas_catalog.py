"""Materialize one source-scoped atlas record for each NASA motion object."""

import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
OUTPUT = RESEARCH / "nasa-perpetual-ocean-atlas-catalog.json"


def read(name):
    return json.loads((RESEARCH / name).read_text(encoding="utf-8"))


def build():
    nasa = read("nasa-perpetual-ocean-objects.json")
    source_audit = read("nasa-perpetual-ocean-source-audit.json")
    crosswalk = read("nasa-ocean-object-state-crosswalk.json")
    matrix = read("nasa-object-state-relation-matrix.json")
    forms = read("nasa-perpetual-ocean-motion-forms.json")
    coverage = read("nasa-perpetual-ocean-object-coverage-audit.json")
    movies = read("nasa-object-movie-variant-join.json")
    crops = read("nasa-current-cartographic-crop-join.json")
    currents = read("ocean-current-almanac.json")
    lengths = read("ocean-current-length-evidence.json")
    current_nasa = read("ocean-current-nasa-crosswalk.json")
    eddies = read("ocean-eddy-name-inventory.json")
    releases = {item["id"]: item for item in nasa["releases"]}
    audited_releases = {item["id"]: item for item in source_audit["releases"]}
    if set(releases) != set(audited_releases):
        raise ValueError("NASA release ledger and source audit differ")
    release_index = []
    for release_id, release in releases.items():
        object_ids = [item["id"] for item in nasa["objects"] if release_id in item["nasa_sources"]]
        if len(object_ids) != len(set(object_ids)) or len(audited_releases[release_id]["object_ids"]) != len(set(audited_releases[release_id]["object_ids"])):
            raise ValueError(f"Duplicate NASA object in release {release_id}")
        if set(object_ids) != set(audited_releases[release_id]["object_ids"]):
            raise ValueError(f"NASA source audit and object ledger differ for {release_id}")
        release_index.append({
            "id": release_id,
            "title": release["title"],
            "url": release["url"],
            "reviewed_parts": audited_releases[release_id]["reviewed_parts"],
            "object_ids": object_ids,
            "object_count": len(object_ids),
            "boundary_note": audited_releases[release_id]["boundary_note"],
        })
    current_by_id = {item["id"]: item for item in currents["entries"]}
    length_by_id = {item["current_id"]: item for item in lengths["entries"]}
    current_relation_by_id = {item["current_id"]: item for item in current_nasa["entries"]}
    crop_by_id = {item["nasa_object_id"]: item for item in crops["records"]}
    coverage_by_id = {item["object_id"]: item for item in coverage["objects"]}
    variants_by_id = defaultdict(list)
    for movie in movies["entries"]:
        for relation in movie["direct_object_relations"]:
            variants_by_id[relation["object_id"]].append({
                "media_id": movie["media_id"],
                "release_id": movie["release_id"],
                "group_id": movie["group_id"],
                "filename": movie["filename"],
                "url": relation["movie_url"],
                "relation": relation["relation"],
                "support_url": relation["support_url"],
            })
    named_by_id = defaultdict(dict)
    for eddy in eddies["entries"]:
        for field, relation in (("generic_nasa_class_id", "generic_class_context"),
                                ("specific_nasa_class_id", "specific_class_context"),
                                ("nasa_related_flow_id", "related_flow_context")):
            if eddy.get(field):
                context = named_by_id[eddy[field]].setdefault(eddy["id"], {
                    "named_eddy_id": eddy["id"],
                    "name": eddy["name"],
                    "source_collection": eddy["source_collection"],
                    "identity_level": eddy["identity_level"],
                    "relations": [],
                    "source_url": eddy["source_url"],
                    "source_event_date": eddy.get("source_event_date"),
                    "event_year": eddy.get("event_year"),
                    "date_evidence": eddy.get("date_evidence"),
                    "temporal_relation": eddy.get("temporal_relation"),
                    "state_locator_candidates": eddy.get("state_locator_candidates", []),
                    "additional_observed_position_joins": eddy.get("additional_observed_position_joins", []),
                    "published_observed_position": eddy.get("published_observed_position"),
                    "published_dated_map_presence": eddy.get("published_dated_map_presence"),
                    "independent_source_census": eddy.get("independent_source_census"),
                    "locator_evidence_type": eddy.get("locator_evidence_type"),
                    "related_current_id": eddy.get("related_current_id"),
                    "vertical_evidence": eddy.get("vertical_evidence"),
                    "movie_depth_relation": eddy.get("movie_depth_relation"),
                    "movie_relation": eddy.get("movie_relation"),
                    "atlas_anchor": eddy["atlas_anchor"],
                    "individual_nasa_identity_claim": False,
                })
                context["relations"].append(relation)
    object_ids = {item["id"] for item in nasa["objects"]}
    if object_ids != set(crosswalk["objects"]) or object_ids != set(forms["objects"]) or object_ids != set(coverage_by_id):
        raise ValueError("NASA source, crosswalk, form, and coverage ledgers differ")
    if set(named_by_id) - object_ids or set(variants_by_id) - object_ids:
        raise ValueError("Named eddy or movie relation points to an unknown NASA object")
    state_codes = sorted(matrix["states"])
    records = []
    for item in nasa["objects"]:
        object_id = item["id"]
        joined = crosswalk["objects"][object_id]
        current_id = joined["almanac_current_id"]
        if current_id and (current_id not in current_by_id or current_relation_by_id[current_id]["status"] != "nasa_named_or_described"):
            raise ValueError(f"Invalid direct current join for {object_id}")
        state_relations = {code: matrix["states"][code]["objects"][object_id] for code in state_codes}
        linked_states = [code for code, relation in state_relations.items() if relation["evidence_kinds"]]
        if any(relation["physical_relation"] != "unknown_no_nasa_feature_footprint" for relation in state_relations.values()):
            raise ValueError(f"Unexpected NASA footprint claim for {object_id}")
        if set(joined["release_evidence"]) != set(item["nasa_sources"]):
            raise ValueError(f"Release evidence missing for {object_id}")
        records.append({
            "id": object_id,
            "name": item["name"],
            "support": item["support"],
            "motion_form": forms["objects"][object_id],
            "description": item["description"],
            "osw_object_id": item["osw_object_id"],
            "parent_id": joined["parent_id"],
            "class_parent": joined["class_parent"],
            "class_children": joined["class_children"],
            "example_object_ids": joined["example_object_ids"],
            "system_context": joined["system_context"],
            "releases": [{
                "id": release_id,
                "url": releases[release_id]["url"],
                "model_period_as_described": releases[release_id]["period_as_described"],
                "vertical_scope": releases[release_id]["vertical_scope"],
                "evidence": joined["release_evidence"][release_id],
            } for release_id in item["nasa_sources"]],
            "reported_properties": joined["reported_properties"],
            "current_join": ({
                "current_id": current_id,
                "kind": current_by_id[current_id]["kind"],
                "length_evidence": length_by_id[current_id],
                "relation": current_relation_by_id[current_id]["status"],
            } if current_id else None),
            "external_current_context": joined["external_current_context"],
            "state_relations": state_relations,
            "atlas_evidence_state_codes": linked_states,
            "unresolved_state_count": len(state_codes) - len(linked_states),
            "primary_media_route": coverage_by_id[object_id]["primary_media_route"],
            "primary_media_url": coverage_by_id[object_id]["primary_media_url"],
            "source_linked_movie_variants": variants_by_id[object_id],
            "regional_movie": joined["regional_movie"],
            "cartographic_crop_contacts": crop_by_id[object_id]["cartographic_crop_contacts"] if object_id in crop_by_id else [],
            "named_eddy_context": list(named_by_id[object_id].values()),
        })
    return {
        "schema": "osw.almanac.nasa-perpetual-ocean-atlas-catalog.v1",
        "scope": "One integrated export for every NASA-identified motion object in the seven audited Perpetual Ocean releases. Named eddy links and cartographic crossings are independent atlas context, not NASA model identity or feature footprints.",
        "source_ledgers": [
            "research/nasa-perpetual-ocean-objects.json", "research/nasa-ocean-object-state-crosswalk.json",
            "research/nasa-perpetual-ocean-source-audit.json",
            "research/nasa-object-state-relation-matrix.json", "research/nasa-perpetual-ocean-motion-forms.json",
            "research/nasa-perpetual-ocean-object-coverage-audit.json", "research/nasa-object-movie-variant-join.json",
            "research/nasa-current-cartographic-crop-join.json", "research/ocean-current-almanac.json",
            "research/ocean-current-length-evidence.json", "research/ocean-current-nasa-crosswalk.json",
            "research/ocean-eddy-name-inventory.json",
        ],
        "object_count": len(records),
        "release_count": len(release_index),
        "releases": release_index,
        "state_count": len(state_codes),
        "state_pair_count": len(records) * len(state_codes),
        "records": records,
    }


if __name__ == "__main__":
    result = build()
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {result['object_count']} integrated NASA atlas records with {result['state_pair_count']} state decisions")

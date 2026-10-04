"""Create one traceable JSON review packet per rights-screened atlas entity."""

from __future__ import annotations

import json
import hashlib
import re
from pathlib import Path


COLLECTIONS = (
    "names", "length_assessments", "measurements", "relations", "media",
    "geometries", "tile_state_relations", "named_eddy_state_assessments",
    "named_eddy_source_observations", "named_current_source_observations",
    "operational_eddy_state_observations", "diagnosed_current_path_observations", "classification_vocabularies", "named_eddy_footprint_candidates", "footprint_movie_context",
    "observation_sets",
)


def filename(entity_id: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", entity_id.replace(":", "__")).strip("_")
    if not slug:
        raise ValueError(f"Unsafe entity packet filename: {entity_id}")
    return slug + "-" + hashlib.sha256(entity_id.encode("utf-8")).hexdigest()[:10] + ".json"


def source_ids(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key.endswith("source_id") and isinstance(child, str):
                yield child
            else:
                yield from source_ids(child)
    elif isinstance(value, list):
        for child in value:
            yield from source_ids(child)


def applies(collection: str, row: dict, entity_id: str) -> bool:
    if collection == "named_eddy_footprint_candidates":
        return row["entity_id"] == entity_id or any(item["state_id"] == entity_id for item in row["state_assessments"])
    if collection == "relations":
        return entity_id in (row["subject_id"], row["object_id"])
    if collection == "named_eddy_state_assessments":
        return entity_id in (row["eddy_id"], row["state_id"])
    if collection == "named_current_source_observations":
        return entity_id in (row["entity_id"], row["state_id"])
    if collection == "operational_eddy_state_observations":
        return entity_id in (row["operational_eddy_id"], row["state_id"])
    if collection == "tile_state_relations":
        return entity_id == row["state_id"]
    if collection == "observation_sets":
        return entity_id == "state:" + row.get("state_code", "")
    return row.get("entity_id") == entity_id


def build_packets(rows: dict[str, list[dict]], output: Path) -> dict:
    """Write packets and return the path index; all references use screened rows."""
    output.mkdir(parents=True, exist_ok=True)
    entities = {row["id"]: row for row in rows["entities"]}
    sources = {row["id"]: row for row in rows["sources"]}
    claims = {row["id"]: row for row in rows["claims"]}
    targets = {name: {row["id"]: row for row in rows[name]} for name in COLLECTIONS}
    tiles = {row["id"]: row for row in rows["tiles"]}
    index = {}
    for entity_id, entity in entities.items():
        selected = {name: [row for row in rows[name] if applies(name, row, entity_id)]
                    for name in COLLECTIONS}
        footprint_geometry_ids = {row["geometry_id"] for row in selected["named_eddy_footprint_candidates"]}
        footprint_ids = {row["id"] for row in selected["named_eddy_footprint_candidates"]}
        selected["footprint_movie_context"] = [row for row in rows["footprint_movie_context"] if row["footprint_candidate_id"] in footprint_ids]
        selected["geometries"] = [row for row in rows["geometries"] if row["entity_id"] == entity_id or row["id"] in footprint_geometry_ids]
        tile_ids = {row["tile_id"] for row in selected["tile_state_relations"]}
        tile_ids |= {row["tile_id"] for row in selected["media"] if row.get("tile_id")}
        selected["tile_state_relations"] = [row for row in rows["tile_state_relations"]
                                            if row["state_id"] == entity_id or row["tile_id"] in tile_ids]
        tile_ids |= {row["tile_id"] for row in selected["footprint_movie_context"]}
        selected["tiles"] = [tiles["tile:" + tile_id] for tile_id in sorted(tile_ids)]
        target_ids = {name: {row["id"] for row in records} for name, records in selected.items()}
        selected_claims = {row["id"]: row for row in rows["claims"]
                           if row["target_id"] in target_ids.get(row["target_collection"], set())}
        supporting_targets = {}
        pending = list(selected_claims.values())
        while pending:
            parent = pending.pop()
            support_id = parent.get("support_claim_id")
            if not support_id or support_id in selected_claims:
                continue
            support = claims[support_id]
            selected_claims[support_id] = support
            pending.append(support)
            target = targets[support["target_collection"]][support["target_id"]]
            if target["id"] not in target_ids.get(support["target_collection"], set()):
                supporting_targets[target["id"]] = target
        related_ids = {row["object_id"] if row["subject_id"] == entity_id else row["subject_id"]
                       for row in selected["relations"]}
        related_ids |= {row["state_id"] for row in selected["named_eddy_state_assessments"]
                        if row["eddy_id"] == entity_id}
        related_ids |= {row["eddy_id"] for row in selected["named_eddy_state_assessments"]
                        if row["state_id"] == entity_id}
        related_ids |= {row["state_id"] for row in selected["named_current_source_observations"]
                        if row["entity_id"] == entity_id}
        related_ids |= {row["state_id"] for row in selected["tile_state_relations"]}
        for candidate in selected["named_eddy_footprint_candidates"]:
            related_ids.add(candidate["entity_id"])
            related_ids.update(row["state_id"] for row in candidate["state_assessments"])
        related_ids.discard(entity_id)
        related_entities = [entities[item] for item in sorted(related_ids) if item in entities]
        source_set = set(source_ids(entity))
        for value in list(selected.values()) + [list(selected_claims.values()),
                                                list(supporting_targets.values()), related_entities]:
            source_set.update(source_ids(value))
        if source_set - set(sources):
            raise ValueError(f"Missing source for {entity_id}: {source_set - set(sources)}")
        packet = {
            "schema": "osw.ocean-motion-entity-packet.v1",
            "status": "rights_screened_review_copy_not_published",
            "source_set": "OSW ocean motion v0.1.0 rights-screened preview",
            "entity": entity,
            "records": {name: records for name, records in selected.items() if records},
            "claims": [selected_claims[item] for item in sorted(selected_claims)],
            "supporting_targets": [supporting_targets[item] for item in sorted(supporting_targets)],
            "related_entities": related_entities,
            "sources": [sources[item] for item in sorted(source_set)],
            "source_ledger_base": "../source-ledgers/",
            "limitations": ["This packet is a screened source-set excerpt, not a complete global inventory.",
                            "Point and editorial state locators do not establish whole-feature physical containment.",
                            "Scientific claims and public release remain under review."],
        }
        path = output / filename(entity_id)
        path.write_text(json.dumps(packet, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        index[entity_id] = "entity-packets/" + path.name
    expected = {Path(value).name for value in index.values()}
    for old in output.glob("*.json"):
        if old.name not in expected:
            if old.parent.resolve() != output.resolve():
                raise ValueError("Packet cleanup escaped output directory")
            old.unlink()
    return dict(sorted(index.items()))

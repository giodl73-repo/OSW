"""Project the full ocean-motion candidate into a rights-screened preview.

This is a review artifact, not a publication authorization. The full candidate
and its source ledgers remain the authoritative research record.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from build_ocean_motion_entity_packets import build_packets


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "almanac" / "release" / "v0.1.0"
OUTPUT = ROOT / "almanac" / "release" / "v0.1.0-rights-screened-preview"
COLLECTIONS = (
    "entities", "names", "measurements", "length_assessments", "relations",
    "claims", "media", "geometries", "tiles", "tile_state_relations",
    "named_eddy_state_assessments", "named_eddy_source_observations",
    "named_current_source_observations", "operational_eddy_state_observations",
    "diagnosed_current_path_observations", "classification_vocabularies", "named_eddy_footprint_candidates", "footprint_movie_context", "observation_sets", "sources",
)
CLAIM_TARGETS = (
    "relations", "measurements", "tile_state_relations",
    "named_eddy_state_assessments", "named_eddy_source_observations",
    "named_current_source_observations", "operational_eddy_state_observations",
    "diagnosed_current_path_observations", "classification_vocabularies", "named_eddy_footprint_candidates", "footprint_movie_context",
)


def read(name: str):
    return json.loads((SOURCE / name).read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def id_digest(values) -> str:
    return hashlib.sha256(("\n".join(sorted(values)) + "\n").encode("utf-8")).hexdigest()


def source_ids(value):
    """Find source references in nested records without confusing ordinary IDs."""
    if isinstance(value, dict):
        for key, child in value.items():
            if key.endswith("source_id") and isinstance(child, str):
                yield child
            else:
                yield from source_ids(child)
    elif isinstance(value, list):
        for child in value:
            yield from source_ids(child)


def pointer_parts(pointer: str) -> list[str]:
    assert pointer.startswith("/")
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]


def pointer_get(value, parts: list[str]):
    for part in parts:
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def pointer_insert(node, parts: list[str], value):
    if not parts:
        return value
    part, rest = parts[0], parts[1:]
    if part.isdecimal():
        assert node is None or isinstance(node, list)
        node = [] if node is None else node
        index = int(part)
        node.extend([None] * (index + 1 - len(node)))
        node[index] = pointer_insert(node[index], rest, value)
    else:
        assert node is None or isinstance(node, dict)
        node = {} if node is None else node
        node[part] = pointer_insert(node.get(part), rest, value)
    return node


def main() -> None:
    full = {name: read(name + ".json") for name in COLLECTIONS}
    pending = {row["id"]: row for row in full["sources"]
               if row.get("kind") == "external" and
               row.get("rights_status", "").startswith("pending")}
    pending_urls = {row["url"] for row in pending.values() if row.get("url")}
    assert pending and any(row.get("provider_asset_redistributed") for row in pending.values())
    direct_pending_counts = {
        name: sum(bool(set(source_ids(row)) & pending.keys()) or
                  any(url in pending_urls for url in row.get("source_urls", []))
                  for row in records)
        for name, records in full.items() if name != "sources"
    }
    indirect_arrow_count = sum(
        bool(row.get("cartographic_source_arrow_ids", {}).get("stable") or
             row.get("cartographic_source_arrow_ids", {}).get("width_sensitive"))
        for row in full["relations"])

    def source_clear(row):
        if any(sid in pending for sid in source_ids(row)):
            return False
        # Some relation rows carry several direct URLs in addition to source_id.
        if any(url in pending_urls for url in row.get("source_urls", [])):
            return False
        # The state matrix cites its OSW ledger as source_id, but these arrow
        # identifiers encode the ArcGIS FeatureServer geometry under review.
        arrows = row.get("cartographic_source_arrow_ids", {})
        if arrows.get("stable") or arrows.get("width_sensitive"):
            return False
        return True

    rows = {name: [dict(row) for row in records if source_clear(row)]
            for name, records in full.items() if name != "sources"}
    rows["sources"] = [dict(row) for row in full["sources"] if row["id"] not in pending]

    # The ArcGIS arrow source only supports the illustrated-span columns. Keep
    # the independent length assessment while removing that measurement.
    redacted_spans = 0
    for original in full["length_assessments"]:
        if original["entity_id"] not in {row["entity_id"] for row in rows["length_assessments"]}:
            if original.get("illustration_source_id") in pending and source_clear({
                key: value for key, value in original.items()
                if key not in {"illustration_source_id", "illustrated_span_km",
                               "illustrated_span_rank", "illustration_limit"}
            }):
                edited = dict(original)
                edited["illustration_source_id"] = None
                edited["illustration_ledger_source_id"] = None
                edited["illustrated_span_km"] = None
                edited["illustrated_span_rank"] = None
                edited["illustration_limit"] = "Excluded from rights-screened preview pending cartographic source review."
                rows["length_assessments"].append(edited)
                redacted_spans += 1

    # Keep the reference graph closed after source-derived entities disappear.
    while True:
        before = sum(map(len, rows.values()))
        ids = {name: {row["id"] for row in records} for name, records in rows.items()}
        entities, tiles, geometries = ids["entities"], ids["tiles"], ids["geometries"]

        def valid(name, row):
            for key in ("entity_id", "eddy_id", "operational_eddy_id", "state_id"):
                if row.get(key) is not None and row[key] not in entities:
                    return False
            if name == "relations" and (row["subject_id"] not in entities or row["object_id"] not in entities):
                return False
            if name == "claims":
                if row["subject_id"].startswith("tile:"):
                    if row["subject_id"] not in tiles:
                        return False
                elif row["subject_id"] not in entities:
                    return False
                if row["object_id"] is not None and row["object_id"] not in entities:
                    return False
                if row["target_id"] not in ids[row["target_collection"]]:
                    return False
                if row["support_claim_id"] is not None and row["support_claim_id"] not in ids["claims"]:
                    return False
            if row.get("tile_id") is not None and "tile:" + row["tile_id"] not in tiles:
                return False
            if name == "diagnosed_current_path_observations" and row["geometry_id"] not in geometries:
                return False
            if name in CLAIM_TARGETS and row["claim_id"] not in ids["claims"]:
                return False
            return True

        for name in rows:
            if name != "sources":
                rows[name] = [row for row in rows[name] if valid(name, row)]
        if sum(map(len, rows.values())) == before:
            break

    ids = {name: {row["id"] for row in records} for name, records in rows.items()}
    referenced_sources = {sid for name, records in rows.items() if name != "sources"
                          for row in records for sid in source_ids(row)}
    assert referenced_sources <= ids["sources"]
    assert not (referenced_sources & pending.keys())
    assert all(row["claim_id"] in ids["claims"] for name in CLAIM_TARGETS for row in rows[name])
    assert all(row["target_id"] in ids[row["target_collection"]] for row in rows["claims"])
    assert all(row.get("support_claim_id") is None or row["support_claim_id"] in ids["claims"]
               for row in rows["claims"])
    assert all(row.get("illustration_source_id") not in pending for row in rows["length_assessments"])
    redacted_spans = sum(str(row.get("illustration_limit", "")).startswith(
        "Excluded from rights-screened") for row in rows["length_assessments"])

    # Source summary fields in the full package describe the full candidate.
    # Recalculate them after screening so a zero-use source is not presented as
    # evidence for rows that were removed from this export.
    for source in rows["sources"]:
        use = {name: sum(row.get("source_id") == source["id"] for row in records)
               for name, records in rows.items() if name not in {"sources", "claims"}}
        source["record_count"] = sum(use.values())
        source["derived_detection_count"] = sum(
            row["detection_count"] for row in rows["observation_sets"]
            if row["source_id"] == source["id"])
        source["total_packaged_row_count"] = source["record_count"] + source["derived_detection_count"]
        source["used_in_collections"] = [name for name, count in use.items() if count]

    # Preserve the exact JSON pointers in retained internal claims, copying
    # only their target records. Array positions remain stable; excluded
    # records appear as null placeholders rather than copied provider values.
    excerpts = {}
    original_ledgers = {}
    for claim in rows["claims"]:
        locator = claim.get("source_locator") or ""
        if not locator.startswith("source-ledgers/"):
            continue
        ledger_path, pointer = locator.split("#", 1)
        filename = Path(ledger_path).name
        assert ledger_path == "source-ledgers/" + filename
        if filename not in original_ledgers:
            original_ledgers[filename] = read("source-ledgers/" + filename)
        original_ledger = original_ledgers[filename]
        parts = pointer_parts(pointer)
        value = pointer_get(original_ledger, parts)
        excerpts[filename] = pointer_insert(excerpts.get(filename), parts, value)
    assert len(excerpts) == 5
    assert not any(url in json.dumps(excerpts, ensure_ascii=False) for url in pending_urls)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    excerpt_dir = OUTPUT / "source-ledgers"
    excerpt_dir.mkdir(parents=True, exist_ok=True)
    for filename, excerpt in excerpts.items():
        write_json(excerpt_dir / filename, excerpt)
    for name, records in rows.items():
        write_json(OUTPUT / (name + ".json"), records)
        fields = sorted({key for record in records for key in record})
        with (OUTPUT / (name + ".csv")).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for record in records:
                writer.writerow({key: json.dumps(value, ensure_ascii=False, sort_keys=True)
                                 if isinstance(value, (list, dict)) else value
                                 for key, value in record.items()})
    (OUTPUT / "schema.json").write_bytes((SOURCE / "schema.json").read_bytes())
    (OUTPUT / "ranked-length-editorial-reviews.json").write_bytes(
        (SOURCE / "ranked-length-editorial-reviews.json").read_bytes())
    for document in ("RIGHTS-SCREENED-PREVIEW.md", "RANKED-LENGTH-EVIDENCE-AUDIT.md"):
        (OUTPUT / ("README.md" if document == "RIGHTS-SCREENED-PREVIEW.md" else document)).write_bytes(
            (SOURCE.parent / document).read_bytes())
    packet_index = build_packets(rows, OUTPUT / "entity-packets")
    write_json(OUTPUT / "entity-packets-index.json", packet_index)
    report = {
        "status": "rights_screened_preview_not_published",
        "basis": "v0.1.0 full research candidate",
        "rule": "Exclude all external sources with pending rights status and records that depend on them, including internal-ledger state relations carrying ArcGIS arrow IDs; redact ArcGIS illustrated spans while retaining independent current-length assessments. Copy only screened source-ledger records reached by retained claim locators, with null placeholders for excluded array positions.",
        "limitations": ["Scientific claims remain individually unreviewed.",
                        "Screened ledger excerpts resolve retained internal claim pointers but are not the full source ledgers or acquisition workflow.",
                        "This projection does not resolve website/repository reuse terms or authorize deposition."],
        "counts": {name: len(records) for name, records in rows.items()},
        "removed_counts": {name: len(full[name]) - len(rows[name]) for name in COLLECTIONS},
        "excluded_pending_source_count": len(pending),
        "excluded_used_pending_source_count": sum(row.get("record_count", 0) > 0
                                                   for row in pending.values()),
        "excluded_pending_source_id_sha256": id_digest(pending),
        "excluded_used_pending_source_id_sha256": id_digest(
            sid for sid, row in pending.items() if row.get("record_count", 0) > 0),
        "direct_pending_reference_counts": direct_pending_counts,
        "indirect_arcgis_arrow_relation_count": indirect_arrow_count,
        "screened_ledger_excerpt_count": len(excerpts),
        "ranked_length_editorial_assessment_count": len(read("ranked-length-editorial-reviews.json")["entries"]),
        "redacted_illustrated_span_count": redacted_spans,
        "retained_claim_reviews": dict(Counter(row["review_status"] for row in rows["claims"])),
        "entity_packet_count": len(packet_index),
    }
    write_json(OUTPUT / "screening-report.json", report)
    files = sorted(path for path in OUTPUT.rglob("*") if path.is_file() and path.name != "manifest.json")
    manifest = {"status": report["status"],
                "source_manifest_sha256": hashlib.sha256((SOURCE / "manifest.json").read_bytes()).hexdigest(),
                "build_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "entity_packet_builder_sha256": hashlib.sha256((ROOT / "analysis" / "build_ocean_motion_entity_packets.py").read_bytes()).hexdigest(),
                "files": [{"path": path.relative_to(OUTPUT).as_posix(),
                           "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                          for path in files]}
    write_json(OUTPUT / "manifest.json", manifest)
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()

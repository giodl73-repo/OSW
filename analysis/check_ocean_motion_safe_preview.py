"""Independently check the rights-screened ocean-motion preview export."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from build_ocean_motion_safe_preview import (COLLECTIONS, CLAIM_TARGETS, SOURCE, OUTPUT,
                                             id_digest, pointer_get, pointer_parts, source_ids)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def check() -> None:
    manifest = load(OUTPUT / "manifest.json")
    assert manifest["status"] == "rights_screened_preview_not_published"
    assert manifest["source_manifest_sha256"] == hashlib.sha256((SOURCE / "manifest.json").read_bytes()).hexdigest()
    assert manifest["entity_packet_builder_sha256"] == hashlib.sha256(
        (SOURCE.parents[2] / "analysis" / "build_ocean_motion_entity_packets.py").read_bytes()).hexdigest()
    for entry in manifest["files"]:
        path = OUTPUT / entry["path"]
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
    assert {entry["path"] for entry in manifest["files"]} == {
        path.relative_to(OUTPUT).as_posix() for path in OUTPUT.rglob("*")
        if path.is_file() and path.name != "manifest.json"
    }
    assert (OUTPUT / "README.md").read_bytes() == (SOURCE.parent / "RIGHTS-SCREENED-PREVIEW.md").read_bytes()
    assert (OUTPUT / "RANKED-LENGTH-EVIDENCE-AUDIT.md").read_bytes() == (
        SOURCE.parent / "RANKED-LENGTH-EVIDENCE-AUDIT.md").read_bytes()
    assert (OUTPUT / "ranked-length-editorial-reviews.json").read_bytes() == (
        SOURCE / "ranked-length-editorial-reviews.json").read_bytes()

    rows = {name: load(OUTPUT / (name + ".json")) for name in COLLECTIONS}
    original = {name: load(SOURCE / (name + ".json")) for name in COLLECTIONS}
    report = load(OUTPUT / "screening-report.json")
    schema = load(OUTPUT / "schema.json")["definitions"]
    ids = {name: {row["id"] for row in records} for name, records in rows.items()}
    pending = {row["id"]: row for row in original["sources"]
               if row.get("kind") == "external" and row.get("rights_status", "").startswith("pending")}
    pending_urls = {row["url"] for row in pending.values() if row.get("url")}
    packet_index = load(OUTPUT / "entity-packets-index.json")
    assert set(packet_index) == ids["entities"]
    assert len(set(packet_index.values())) == len(packet_index) == report["entity_packet_count"]
    assert {"entity-packets/" + path.name for path in (OUTPUT / "entity-packets").glob("*.json")} == set(packet_index.values())
    source_by_id = {row["id"]: row for row in rows["sources"]}
    claim_by_id_full = {row["id"]: row for row in rows["claims"]}
    for entity_id, relative in packet_index.items():
        packet = load(OUTPUT / relative)
        assert packet["schema"] == "osw.ocean-motion-entity-packet.v1"
        assert packet["status"] == "rights_screened_review_copy_not_published"
        assert packet["entity"] == next(row for row in rows["entities"] if row["id"] == entity_id)
        assert not any(url in json.dumps(packet, ensure_ascii=False) for url in pending_urls)
        record_ids = set()
        for name, records in packet["records"].items():
            assert name in rows
            original_rows = {row["id"]: row for row in rows[name]}
            for record in records:
                assert record == original_rows[record["id"]]
                record_ids.add((name, record["id"]))
        support_ids = {(row["target_collection"], row["target_id"])
                       for row in packet["claims"] if (row["target_collection"], row["target_id"]) not in record_ids}
        assert support_ids == {(row["target_collection"], row["target_id"])
                               for row in packet["claims"] if row["target_id"] in
                               {target["id"] for target in packet["supporting_targets"]}}
        packet_claims = {row["id"]: row for row in packet["claims"]}
        assert all(row == claim_by_id_full[row["id"]] and
                   (row["target_collection"], row["target_id"]) in record_ids | support_ids and
                   (not row.get("support_claim_id") or row["support_claim_id"] in packet_claims)
                   for row in packet["claims"])
        assert packet["sources"] == [source_by_id[row["id"]] for row in packet["sources"]]
        packet_evidence = [packet["entity"], packet["records"], packet["claims"],
                           packet["supporting_targets"], packet["related_entities"]]
        assert set().union(*(set(source_ids(value)) for value in packet_evidence)) == {
            row["id"] for row in packet["sources"]}
    assert len(pending) == report["excluded_pending_source_count"]
    assert sum(row.get("record_count", 0) > 0 for row in pending.values()) == report[
        "excluded_used_pending_source_count"]
    assert id_digest(pending) == report["excluded_pending_source_id_sha256"]
    assert id_digest(sid for sid, row in pending.items() if row.get("record_count", 0) > 0) == report[
        "excluded_used_pending_source_id_sha256"]
    assert not (ids["sources"] & pending.keys())
    assert not any(row["type"] == "operational_eddy_detection" for row in rows["entities"])
    assert not any(row["role"] == "dated_operational_eddy_polygon" for row in rows["geometries"])
    assert not rows["operational_eddy_state_observations"]
    paper_ring_ids = {"eddy:published:kraken-2013", "eddy:published:thor-2020",
                      "eddy:published:ursa-2021", "eddy:published:cameron-2009-observed",
                      "eddy:published:darwin-2009-observed"}
    assert paper_ring_ids <= ids["entities"]
    assert {row["entity_id"] for row in rows["named_eddy_source_observations"]} == paper_ring_ids
    assert not ({"eddy:horizon:loop-52-primary", "eddy:horizon:loop-53-primary",
                 "eddy:horizon:loop-60-primary", "eddy:horizon:loop-69-primary",
                 "eddy:horizon:loop-70-primary"} & ids["entities"])
    assert all("horizonmarine.com" not in json.dumps(row, ensure_ascii=False).lower()
               and "horizon:loop-" not in json.dumps(row, ensure_ascii=False).lower()
               for name, records in rows.items() for row in records)
    assert len(list((OUTPUT / "source-ledgers").glob("*.json"))) == report[
        "screened_ledger_excerpt_count"]
    for name in COLLECTIONS:
        if name == "sources":
            continue
        direct = sum(bool(set(source_ids(row)) & pending.keys()) or
                     any(url in pending_urls for url in row.get("source_urls", []))
                     for row in original[name])
        assert direct == report["direct_pending_reference_counts"][name]
    assert report["indirect_arcgis_arrow_relation_count"] == sum(
        bool(row.get("cartographic_source_arrow_ids", {}).get("stable") or
             row.get("cartographic_source_arrow_ids", {}).get("width_sensitive"))
        for row in original["relations"])

    for name, records in rows.items():
        assert len(records) == len(ids[name]) == report["counts"][name]
        assert len(original[name]) - len(records) == report["removed_counts"][name]
        validator = Draft202012Validator(schema[name], format_checker=FormatChecker())
        with (OUTPUT / (name + ".csv")).open(encoding="utf-8", newline="") as stream:
            flat = list(csv.DictReader(stream))
        assert len(flat) == len(records)
        for row, csv_row in zip(records, flat):
            validator.validate(row)
            assert not (set(source_ids(row)) & pending.keys()), (name, row["id"])
            assert not any(url in json.dumps(row, ensure_ascii=False) for url in pending_urls), (name, row["id"])
            for field, cell in csv_row.items():
                value = row.get(field)
                expected = (json.dumps(value, ensure_ascii=False, sort_keys=True)
                            if isinstance(value, (dict, list)) else "" if value is None else str(value))
                assert cell == expected, (name, row["id"], field)
            for key in ("entity_id", "eddy_id", "operational_eddy_id", "state_id"):
                if row.get(key) is not None:
                    assert row[key] in ids["entities"], (name, row["id"], key)
            if row.get("tile_id") is not None:
                assert "tile:" + row["tile_id"] in ids["tiles"]
            if name in CLAIM_TARGETS:
                assert row["claim_id"] in ids["claims"]
            if name == "relations":
                assert row["subject_id"] in ids["entities"] and row["object_id"] in ids["entities"]
                arrows = row.get("cartographic_source_arrow_ids", {})
                assert not (arrows.get("stable") or arrows.get("width_sensitive"))
            if name == "claims":
                assert row["target_id"] in ids[row["target_collection"]]
                assert row["support_claim_id"] is None or row["support_claim_id"] in ids["claims"]
                assert row["review_status"] == "not_individually_reviewed"

    for source in rows["sources"]:
        use = {name: sum(row.get("source_id") == source["id"] for row in records)
               for name, records in rows.items() if name not in {"sources", "claims"}}
        assert source["record_count"] == sum(use.values())
        assert source["used_in_collections"] == [name for name, count in use.items() if count]
        assert source["derived_detection_count"] == sum(
            row["detection_count"] for row in rows["observation_sets"]
            if row["source_id"] == source["id"])
        assert source["total_packaged_row_count"] == (
            source["record_count"] + source["derived_detection_count"])

    claim_by_id = {row["id"]: row for row in rows["claims"]}
    assert len(claim_by_id) == sum(len(rows[name]) for name in CLAIM_TARGETS)
    for name in CLAIM_TARGETS:
        for row in rows[name]:
            claim = claim_by_id[row["claim_id"]]
            assert (claim["target_collection"], claim["target_id"]) == (name, row["id"])
    assert len([row for row in rows["length_assessments"] if row["rank_eligible"]]) == 11
    editorial = load(OUTPUT / "ranked-length-editorial-reviews.json")
    assert editorial["status"] == "source_passage_audit_only_not_scientific_claim_approval"
    assert len(editorial["entries"]) == report["ranked_length_editorial_assessment_count"] == 11
    ranked_claims = {row["claim_id"]: row for row in rows["measurements"] if row["rank_eligible"]}
    assert {row["claim_id"] for row in editorial["entries"]} == set(ranked_claims)
    for row in editorial["entries"]:
        claim = claim_by_id[row["claim_id"]]
        assert row["review_fingerprint"] == claim["review_fingerprint"]
        assert row["subject_id"] == claim["subject_id"]
        assert row["reported_length_km"] == claim["value"]
        assert row["scientific_review_status"] == claim["review_status"] == "not_individually_reviewed"
    assert len([row for row in rows["length_assessments"]
                if row.get("illustration_limit", "").startswith("Excluded from rights-screened")]) == report["redacted_illustrated_span_count"]
    assert all(row.get("illustration_source_id") is None or row["illustration_source_id"] in ids["sources"]
               for row in rows["length_assessments"])
    excerpt_cache = {}
    original_cache = {}
    internal_count = 0
    for claim in rows["claims"]:
        locator = claim.get("source_locator") or ""
        if not locator.startswith("source-ledgers/"):
            continue
        path, pointer = locator.split("#", 1)
        filename = Path(path).name
        if filename not in excerpt_cache:
            excerpt_cache[filename] = load(OUTPUT / "source-ledgers" / filename)
            original_cache[filename] = load(SOURCE / "source-ledgers" / filename)
        parts = pointer_parts(pointer)
        assert pointer_get(excerpt_cache[filename], parts) == pointer_get(original_cache[filename], parts)
        internal_count += 1
    assert internal_count > 8000
    assert len(excerpt_cache) == report["screened_ledger_excerpt_count"]
    assert not any(url in json.dumps(excerpt_cache, ensure_ascii=False) for url in pending_urls)
    assert not list(OUTPUT.rglob("*.nc")) and not list(OUTPUT.rglob("*.zip"))
    print(f"Rights-screened preview valid: {len(rows['entities'])} entities, {len(rows['claims'])} claims")


if __name__ == "__main__":
    check()

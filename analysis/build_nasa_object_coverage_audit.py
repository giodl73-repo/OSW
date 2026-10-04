"""Summarize source, media, and atlas coverage for every NASA motion object.

This audits the identified-object ledger, not every particle or unnamed eddy in
NASA's model visualization. The live series release check is a separate gate.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
OUTPUT = RESEARCH / "nasa-perpetual-ocean-object-coverage-audit.json"


def read(name: str) -> dict:
    return json.loads((RESEARCH / name).read_text(encoding="utf-8"))


def main() -> None:
    catalog = read("nasa-perpetual-ocean-objects.json")
    forms = read("nasa-perpetual-ocean-motion-forms.json")
    source_audit = read("nasa-perpetual-ocean-source-audit.json")
    crosswalk = read("nasa-ocean-object-state-crosswalk.json")
    tiles = read("nasa-perpetual-ocean-tile-join.json")
    media = read("nasa-perpetual-ocean-object-media.json")
    media_by_id = {item["id"]: item for item in media["assets"]}
    rows = []
    if set(forms["objects"]) != {item["id"] for item in catalog["objects"]}:
        raise ValueError("NASA motion-form classification does not cover the object ledger")
    for item in catalog["objects"]:
        object_id = item["id"]
        join = crosswalk["objects"][object_id]
        evidence = join["release_evidence"]
        checked_phrases = sum(bool(source.get("support_pattern")) for source in evidence.values())
        checked_media_groups = sum(len(source.get("media_group_ids", [])) for source in evidence.values())
        checked_narration_passages = sum(source["evidence_kind"] == "narration_cues" for source in evidence.values())
        state_codes = join["state_evidence"]["object_locator_candidates"]
        if join["feature_media_ids"]:
            media_route = "feature_specific_movie"
            media_url = media_by_id[join["feature_media_ids"][0]]["movie_url"]
        elif join["narrated_start_s"] is not None:
            media_route = "narrated_clip"
            media_url = next(release["timed_movie"] for release in catalog["releases"] if release["id"] == "po2-narrated")
            media_url += f"#t={join['narrated_start_s']},{join['narrated_end_s']}"
        elif join["regional_movie"]:
            media_route = "regional_model_crop"
            media_url = join["regional_movie"]["url"]
        elif join["source_overview_movie"]:
            media_route = "source_release_overview"
            media_url = join["source_overview_movie"]["url"]
        else:
            media_route = "missing"
            media_url = None
        rows.append({
            "object_id": object_id,
            "name": item["name"],
            "support": item["support"],
            "motion_form": forms["objects"][object_id],
            "source_release_ids": item["nasa_sources"],
            "source_evidence_count": len(evidence),
            "source_phrase_check_count": checked_phrases,
            "media_group_phrase_check_count": checked_media_groups,
            "narration_passage_check_count": checked_narration_passages,
            "has_direct_current_record": bool(item.get("almanac_current_id")),
            "has_editorial_locator": item["locator"] is not None,
            "state_locator_candidates": state_codes,
            "regional_crop_url": join["regional_movie"]["url"] if join["regional_movie"] else None,
            "primary_media_route": media_route,
            "primary_media_url": media_url,
            "coverage_issue": "missing source evidence, phrase check, or media navigation" if not evidence or checked_phrases != len(evidence) or media_url is None else
                              "located object lacks state or crop navigation" if item["locator"] is not None and (not state_codes or not join["regional_movie"]) else
                              "unlocated object has a state or crop claim" if item["locator"] is None and (state_codes or join["regional_movie"]) else None,
        })
    issues = [row for row in rows if row["coverage_issue"]]
    payload = {
        "schema": "osw.almanac.nasa-object-coverage-audit.v1",
        "scope": "NASA-identified names, structures, and processes in the seven audited Perpetual Ocean source releases. Unnamed particles and individually unlabelled eddies are outside this identified-object inventory.",
        "source_audit": "research/nasa-perpetual-ocean-source-audit.json",
        "object_ledger": "research/nasa-perpetual-ocean-objects.json",
        "motion_form_ledger": "research/nasa-perpetual-ocean-motion-forms.json",
        "crosswalk": "research/nasa-ocean-object-state-crosswalk.json",
        "media_relation_limit": "A crop or narrated clip is navigation to NASA's model presentation, not an observed feature footprint, individual eddy identity, or NASA-endorsed OSW state boundary.",
        "summary": {
            "audited_releases": len(catalog["releases"]),
            "live_series_release_ids_recorded": source_audit["series_discovery"]["tagged_release_ids"],
            "identified_objects": len(rows),
            "motion_forms_classified": sum(row["motion_form"] in forms["forms"] for row in rows),
            "source_evidence_edges": sum(row["source_evidence_count"] for row in rows),
            "source_phrase_checks": sum(row["source_phrase_check_count"] for row in rows),
            "individual_media_group_phrase_checks": sum(row["media_group_phrase_check_count"] for row in rows),
            "narration_passage_checks": sum(row["narration_passage_check_count"] for row in rows),
            "objects_with_editorial_locators": sum(row["has_editorial_locator"] for row in rows),
            "unlocated_classes_or_processes": sum(not row["has_editorial_locator"] for row in rows),
            "objects_with_media_navigation": sum(row["primary_media_url"] is not None for row in rows),
            "objects_with_direct_current_records": sum(row["has_direct_current_record"] for row in rows),
            "nasa_regional_crop_movies": len(tiles["tiles"]),
            "coverage_issue_count": len(issues),
        },
        "objects": rows,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote NASA object coverage audit: {len(rows)} objects, {len(issues)} issues")
    if issues:
        raise ValueError("NASA object coverage audit found gaps: " + ", ".join(row["object_id"] for row in issues))


if __name__ == "__main__":
    main()

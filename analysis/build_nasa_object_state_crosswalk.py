"""Join NASA-identified motion objects to release, movie, and OSW state evidence."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
OUTPUT = RESEARCH / "nasa-ocean-object-state-crosswalk.json"


def read(name: str) -> dict:
    return json.loads((RESEARCH / name).read_text(encoding="utf-8"))


def main() -> None:
    nasa = read("nasa-perpetual-ocean-objects.json")
    motion = read("ocean-motion-state-join.json")
    arrows = read("cartographic-ocean-current-state-join.json")
    tiles = read("nasa-perpetual-ocean-tile-join.json")
    media = read("nasa-perpetual-ocean-object-media.json")
    release_media = read("nasa-perpetual-ocean-release-media.json")
    source_evidence = read("nasa-perpetual-ocean-object-evidence.json")
    properties = read("nasa-perpetual-ocean-object-properties.json")
    forms = read("nasa-perpetual-ocean-motion-forms.json")
    releases = {item["id"]: item for item in nasa["releases"]}
    nasa_objects_by_id = {item["id"]: item for item in nasa["objects"]}
    if set(forms["objects"]) != set(nasa_objects_by_id):
        raise ValueError("NASA motion forms do not cover the object ledger")
    class_parents = {}
    class_children = {object_id: [] for object_id in nasa_objects_by_id}
    for edge in forms["class_relations"]:
        child_id, parent_id = edge["child_id"], edge["parent_id"]
        if child_id not in nasa_objects_by_id or parent_id not in nasa_objects_by_id or child_id in class_parents:
            raise ValueError(f"Invalid NASA class relation: {edge}")
        class_parents[child_id] = edge
        class_children[parent_id].append(edge)
    movies_by_release = {item["release_id"]: item["movies"] for item in release_media["releases"]}
    states = {}
    for code in motion["states"]:
        states[code] = {
            "cartographic_current_crossings": [],
            "width_sensitive_cartographic_contacts": [],
            "schematic_current_crossings": [],
            "schematic_object_crossings": [],
            "editorial_current_line_crossings": [],
            "object_locator_candidates": [],
        }
    objects = {}
    for item in nasa["objects"]:
        object_id = item["id"]
        current_id = item.get("almanac_current_id")
        parent_id = item.get("parent_id")
        parent_current_id = nasa_objects_by_id[parent_id].get("almanac_current_id") if parent_id else None
        evidence = {key: [] for key in next(iter(states.values()))}
        for code, relation in motion["states"].items():
            mapped = arrows["states"][code]
            if current_id:
                if current_id in mapped["stable_cartographic_current_crossings"]:
                    evidence["cartographic_current_crossings"].append(code)
                if current_id in mapped["width_sensitive_cartographic_contacts"]:
                    evidence["width_sensitive_cartographic_contacts"].append(code)
                if current_id in relation["schematic_current_centerline_crossings"]:
                    evidence["schematic_current_crossings"].append(code)
                if current_id in relation["editorial_nasa_current_line_crossings"]:
                    evidence["editorial_current_line_crossings"].append(code)
            if object_id in relation["nasa_object_locator_candidates"]:
                evidence["object_locator_candidates"].append(code)
            if object_id in relation["schematic_nasa_object_crossings"]:
                evidence["schematic_object_crossings"].append(code)
        for codes in evidence.values():
            codes.sort()
        for key, codes in evidence.items():
            for code in codes:
                states[code][key].append(object_id)
        tile = tiles["nasa_object_joins"].get(object_id)
        feature_media_ids = [asset["id"] for asset in media["assets"] if object_id in asset["object_ids"]]
        overview_movie = None
        if item.get("narrated_start_s") is None and tile is None and not feature_media_ids:
            for release_id in item["nasa_sources"]:
                movies = movies_by_release[release_id]
                overview_movie = next(({"release_id": release_id, "url": movie["url"], "media_id": movie["media_id"], "relation": "release_overview_only"}
                                       for movie in movies if movie["filename"].endswith(".mp4") and "clean_noDate_1080p30" in movie["filename"]), None)
                if not overview_movie:
                    overview_movie = next(({"release_id": release_id, "url": movie["url"], "media_id": movie["media_id"], "relation": "release_overview_only"}
                                           for movie in movies if movie["filename"].endswith(".mp4")), None)
                if overview_movie:
                    break
        objects[object_id] = {
            "nasa_support": item["support"],
            "release_ids": item["nasa_sources"],
            "release_urls": [releases[release_id]["url"] for release_id in item["nasa_sources"]],
            "release_evidence": source_evidence["objects"][object_id],
            "reported_properties": [property for property in properties["properties"] if property["object_id"] == object_id],
            "almanac_current_id": current_id,
            "osw_object_id": item["osw_object_id"],
            "parent_id": parent_id,
            "parent_current_id": parent_current_id,
            "external_current_context": item.get("external_current_context", []),
            "example_object_ids": item.get("example_object_ids", []),
            "example_relation": item.get("example_relation"),
            "system_context": item.get("system_context", []),
            "class_parent": class_parents.get(object_id),
            "class_children": sorted(class_children[object_id], key=lambda edge: edge["child_id"]),
            "narrated_start_s": item.get("narrated_start_s"),
            "narrated_end_s": item.get("narrated_end_s"),
            "regional_movie": tile,
            "feature_media_ids": feature_media_ids,
            "source_overview_movie": overview_movie,
            "state_evidence": evidence,
        }
    for relation in states.values():
        for ids in relation.values():
            ids.sort()
    result = {
        "schema": "osw.almanac.nasa-object-state-crosswalk.v1",
        "object_ledger": "research/nasa-perpetual-ocean-objects.json",
        "state_ledger": "research/ocean-motion-state-join.json",
        "cartographic_ledger": "research/cartographic-ocean-current-state-join.json",
        "tile_ledger": "research/nasa-perpetual-ocean-tile-join.json",
        "media_ledger": "research/nasa-perpetual-ocean-object-media.json",
        "source_evidence_ledger": "research/nasa-perpetual-ocean-object-evidence.json",
        "property_ledger": "research/nasa-perpetual-ocean-object-properties.json",
        "motion_form_ledger": "research/nasa-perpetual-ocean-motion-forms.json",
        "evidence_limit": "NASA identifies the objects in linked releases. Current crossings come from independent cartographic arrows or OSW schematic/editorial lines. The Indonesian Throughflow gate is an OSW conceptual feature line. Object locators are approximate points and regional movies are geographic context. None proves a NASA-segmented footprint, an observed current core, or an individual eddy track.",
        "objects": objects,
        "states": states,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    count = sum(len(item["state_evidence"]["cartographic_current_crossings"]) for item in objects.values())
    print(f"Wrote {len(objects)} NASA objects, {len(states)} states, {count} cartographic object/state crossings")


if __name__ == "__main__":
    main()

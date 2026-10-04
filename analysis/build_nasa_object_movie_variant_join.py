"""Join all audited NASA movie listings to source-supported motion objects."""

import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
OUTPUT = RESEARCH / "nasa-object-movie-variant-join.json"
COMPOSITING_GROUPS = {376528, 376532, 376578, 376593, 376594}
DIRECT_GROUPS = {376521, 376522, 376527, 376877, 379442, 378115}
CONTEXT_GROUPS = {351520, 351524, 350679, 376525, 377711, 377719,
                  378119, 378120, 377900, 377901, 377904}


def read(name):
    return json.loads((RESEARCH / name).read_text(encoding="utf-8"))


def build():
    catalog = read("nasa-perpetual-ocean-objects.json")
    evidence = read("nasa-perpetual-ocean-object-evidence.json")["objects"]
    releases = read("nasa-perpetual-ocean-release-media.json")
    source_groups = {movie["group_id"] for release in releases["releases"] for movie in release["movies"]}
    reviewed_groups = COMPOSITING_GROUPS | DIRECT_GROUPS | CONTEXT_GROUPS
    if source_groups != reviewed_groups:
        raise ValueError(f"NASA movie groups need review: new={sorted(source_groups - reviewed_groups)}, missing={sorted(reviewed_groups - source_groups)}")
    by_id = {item["id"]: item for item in catalog["objects"]}
    claimed_by_release = defaultdict(list)
    for object_id, edges in evidence.items():
        for release_id in edges:
            claimed_by_release[release_id].append(object_id)
    entries = []
    for release in releases["releases"]:
        release_id = release["release_id"]
        release_objects = sorted(claimed_by_release[release_id])
        for movie in release["movies"]:
            direct = []
            for object_id in release_objects:
                edge = evidence[object_id][release_id]
                if movie["group_id"] in edge.get("media_group_ids", []):
                    direct.append({
                        "object_id": object_id,
                        "relation": "same_cited_media_group",
                        "support_url": f"{release['source_page']}#media_group_{movie['group_id']}",
                        "movie_url": movie["url"],
                    })
                elif edge["evidence_kind"] == "narration_cues" and release_id == "po2-narrated":
                    object_record = by_id[object_id]
                    start, end = object_record.get("narrated_start_s"), object_record.get("narrated_end_s")
                    if start is None or end is None:
                        raise ValueError(f"Missing narrated interval for {object_id}")
                    direct.append({
                        "object_id": object_id,
                        "relation": "narrated_bounded_clip",
                        "support_url": edge["source_url"],
                        "movie_url": f"{movie['url']}#t={start},{end}",
                        "cue_numbers": edge["cue_numbers"],
                    })
            status = ("source_group_or_cue_join" if direct else
                      "compositing_layer" if movie["group_id"] in COMPOSITING_GROUPS else
                      "release_context_only" if release_objects else "no_identified_object_on_release")
            if bool(direct) != (movie["group_id"] in DIRECT_GROUPS):
                raise ValueError(f"Movie group disposition changed for {movie['group_id']}")
            entries.append({
                "release_id": release_id,
                "media_id": movie["media_id"],
                "filename": movie["filename"],
                "url": movie["url"],
                "width": movie["width"],
                "height": movie["height"],
                "group_id": movie["group_id"],
                "status": status,
                "direct_object_relations": direct,
                "release_identified_object_ids": release_objects,
            })
    counts = Counter(item["status"] for item in entries)
    return {
        "schema": "osw.almanac.nasa-object-movie-variant-join.v1",
        "release_media_ledger": "research/nasa-perpetual-ocean-release-media.json",
        "object_evidence_ledger": "research/nasa-perpetual-ocean-object-evidence.json",
        "object_ledger": "research/nasa-perpetual-ocean-objects.json",
        "rule": "A movie is directly joined to an object only if its NASA media group contains the checked object phrase, or the NASA narrated release has exact cue evidence and an editorial clip window for that object. Other movies are release context, compositing layers, or releases without identified objects; release co-membership is not a scene identity.",
        "status_counts": {key: counts[key] for key in ("source_group_or_cue_join", "compositing_layer", "release_context_only", "no_identified_object_on_release")},
        "movie_listing_count": len(entries),
        "entries": entries,
    }


if __name__ == "__main__":
    result = build()
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {result['movie_listing_count']} movie/object variant records: {result['status_counts']}")

"""Resolve each NASA object/release claim to a source group or narration cue."""

from __future__ import annotations

import json
import re
import urllib.request
from html import unescape
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "nasa-perpetual-ocean-objects.json"
OUTPUT = ROOT / "research" / "nasa-perpetual-ocean-object-evidence.json"

GROUPS = {
    "po-2011-viz": {"gulf-stream": [351521], "kuroshio": [351523], "ocean-eddies": [351519]},
    "po-2011-story": {"gulf-stream": [350680, 350677], "kuroshio": [350682, 350677], "agulhas": [350681], "agulhas-retroflection": [350681], "ocean-eddies": [350677]},
    "po2-western-boundary": {
        "gulf-stream": [376523, 376521, 376522], "kuroshio": [376523, 376521, 376522], "agulhas": [376523, 376521, 376522],
        "indonesian-throughflow": [376523], "western-boundary-currents": [376523],
        "red-sea-saline-overflow": [376523], "persian-gulf-saline-overflow": [376523],
        "kuroshio-meanders": [376523], "agulhas-retroflection": [376523],
        "agulhas-rings": [376523], "western-boundary-rings": [376523],
        "gulf-stream-cold-cores": [376523], "gulf-stream-deep-return": [376523, 376527],
        "gulf-of-mexico-loop-eddies": [376523],
    },
    "po2-crops": {"agulhas": [379442], "agulhas-rings": [379442]},
    "po2-sphere": {"gulf-stream": [378115]},
}
NARRATION_CUES = {
    "gulf-stream": [49, 50, 51, 52, 53, 54],
    "kuroshio": [21, 22, 23, 24, 25, 26],
    "agulhas": [35, 36, 37, 38, 39, 40],
    "east-australian": [12],
    "western-boundary-currents": [14, 15],
    "kuroshio-eastward-turn": [23],
    "kuroshio-eddies": [24],
    "agulhas-retroflection": [37],
    "agulhas-rings": [38, 39, 40, 41],
    "gulf-stream-deep-return": [65, 66, 67, 68, 69, 70],
    "global-overturning": [41, 42, 43, 44],
    "north-atlantic-sinking": [55, 56],
    "upwelling": [29, 30, 31],
    "downwelling": [29],
}
SUPPORT_PATTERNS = {
    "po-2011-viz": {"gulf-stream": r"Gulf Stream", "kuroshio": r"Kuroshio", "ocean-eddies": r"ocean eddies"},
    "po-2011-story": {"gulf-stream": r"Gulf Stream", "kuroshio": r"Kuroshio", "agulhas": r"Agulhas Current", "agulhas-retroflection": r"loops eastward", "ocean-eddies": r"circular pools"},
    "po2-western-boundary": {
        "gulf-stream": r"Gulf Stream", "kuroshio": r"Kuroshio", "agulhas": r"Agulhas Current",
        "indonesian-throughflow": r"Indonesian Throughflow", "red-sea-saline-overflow": r"Red Sea",
        "persian-gulf-saline-overflow": r"Persian Gulf", "western-boundary-currents": r"western boundary currents",
        "kuroshio-meanders": r"meanders", "agulhas-retroflection": r"retroflects",
        "agulhas-rings": r"Agulhas Rings", "western-boundary-rings": r"turbulent rings",
        "gulf-stream-cold-cores": r"cold cores", "gulf-stream-deep-return": r"return current underneath|counter.?current",
        "gulf-of-mexico-loop-eddies": r"loop currents in the Gulf of Mexico",
    },
    "po2-crops": {"agulhas": r"Agulhas Current", "agulhas-rings": r"Agulhas Rings"},
    "po2-sphere": {"gulf-stream": r"Gulf Stream"},
    "po2-narrated": {
        "gulf-stream": r"Gulf Stream", "kuroshio": r"Kuroshio", "agulhas": r"Agulhas Current",
        "east-australian": r"East Australian Current", "western-boundary-currents": r"western boundary currents",
        "kuroshio-eastward-turn": r"turns east", "kuroshio-eddies": r"huge eddies",
        "agulhas-retroflection": r"sharp turn", "agulhas-rings": r"Agulhas rings",
        "gulf-stream-deep-return": r"cold, deep water headed south beneath",
        "global-overturning": r"overturning circulation", "north-atlantic-sinking": r"sinks deep",
        "upwelling": r"upwelling", "downwelling": r"downwelling",
    },
}


def get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "OSW-Ocean-Motion-Almanac/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def seconds(value: str) -> float:
    hour, minute, rest = value.split(":")
    return round(int(hour) * 3600 + int(minute) * 60 + float(rest.replace(",", ".")), 3)


def main() -> None:
    ledger = json.loads(SOURCE.read_text(encoding="utf-8"))
    releases = {item["id"]: item for item in ledger["releases"]}
    transcript_url = releases["po2-narrated"]["transcript"]
    transcript = BeautifulSoup(get(transcript_url), "html.parser").get_text()
    cue_pattern = re.compile(r"(?m)^\s*(\d+)\s*\n\s*(\d\d:\d\d:\d\d,\d+)\s*-->\s*(\d\d:\d\d:\d\d,\d+)")
    cue_matches = list(cue_pattern.finditer(transcript))
    cues = {int(match.group(1)): {"start_seconds": seconds(match.group(2)), "end_seconds": seconds(match.group(3))}
            for match in cue_matches}
    cue_text = {int(match.group(1)): " ".join(transcript[match.end():cue_matches[index + 1].start() if index + 1 < len(cue_matches) else len(transcript)].split())
                for index, match in enumerate(cue_matches)}
    if set(cues) != set(range(1, 74)):
        raise ValueError("NASA narrated transcript cue count changed")
    valid_groups = {}
    for release_id in GROUPS:
        page_id = releases[release_id]["url"].rstrip("/").rsplit("/", 1)[-1]
        page = json.loads(get(f"https://svs.gsfc.nasa.gov/api/{page_id}"))
        valid_groups[release_id] = {group["id"]: group for group in page["media_groups"]}
    expected_patterns = {(item["id"], release_id) for item in ledger["objects"] for release_id in item["nasa_sources"]}
    actual_patterns = {(object_id, release_id) for release_id, entries in SUPPORT_PATTERNS.items() for object_id in entries}
    if expected_patterns != actual_patterns:
        raise ValueError(f"NASA support patterns differ: missing={expected_patterns - actual_patterns}, extra={actual_patterns - expected_patterns}")
    evidence = {}
    for item in ledger["objects"]:
        object_id = item["id"]
        sources = {}
        for release_id in item["nasa_sources"]:
            if release_id == "po2-narrated":
                numbers = NARRATION_CUES[object_id]
                pattern = SUPPORT_PATTERNS[release_id][object_id]
                passage = " ".join(cue_text[number] for number in numbers)
                if not re.search(pattern, passage, re.IGNORECASE):
                    raise ValueError(f"NASA narration cues no longer support {object_id}: {pattern}")
                sources[release_id] = {
                    "source_url": transcript_url,
                    "evidence_kind": "narration_cues",
                    "cue_numbers": numbers,
                    "cue_times": [dict(number=number, **cues[number]) for number in numbers],
                    "support_pattern": pattern,
                }
            else:
                group_ids = GROUPS[release_id][object_id]
                if not set(group_ids) <= set(valid_groups[release_id]):
                    raise ValueError(f"NASA media group changed for {object_id}/{release_id}")
                pattern = SUPPORT_PATTERNS[release_id][object_id]
                for group_id in group_ids:
                    passage = " ".join(unescape(BeautifulSoup(str(valid_groups[release_id][group_id].get(field, "")), "html.parser").get_text(" "))
                                       for field in ("title", "caption", "description"))
                    if not re.search(pattern, passage, re.IGNORECASE):
                        raise ValueError(f"NASA media group {group_id} no longer supports {object_id}: {pattern}")
                sources[release_id] = {
                    "source_url": f"{releases[release_id]['url']}#media_group_{group_ids[0]}",
                    "evidence_kind": "nasa_media_group",
                    "media_group_ids": group_ids,
                    "media_group_urls": [f"{releases[release_id]['url']}#media_group_{group_id}" for group_id in group_ids],
                    "support_pattern": pattern,
                }
        evidence[object_id] = sources
    expected = {(item["id"], release_id) for item in ledger["objects"] for release_id in item["nasa_sources"]}
    actual = {(object_id, release_id) for object_id, sources in evidence.items() for release_id in sources}
    if actual != expected:
        raise ValueError(f"Evidence edges differ: missing={expected - actual}, extra={actual - expected}")
    output = {
        "schema": "osw.almanac.nasa-object-evidence.v1",
        "source_ledger": "research/nasa-perpetual-ocean-objects.json",
        "method": "Each object/release relationship points to the relevant NASA SVS media groups or exact cue numbers in the published narrated transcript. On regeneration, every cited group is individually checked for its curated object-support phrase in NASA's live text; narration cue selections are checked together as a cited passage. The pattern is retained on each edge for review. Cue selections identify supporting passages; the separate movie clip bounds are editorial navigation intervals.",
        "relationship_count": len(actual),
        "objects": evidence,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(actual)} source-evidence relationships for {len(evidence)} NASA objects")


if __name__ == "__main__":
    main()

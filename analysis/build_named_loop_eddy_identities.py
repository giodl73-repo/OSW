"""Expand Horizon's numbered ring rows into primary and secondary name records."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "named-loop-current-eddies.json"
OUTPUT = ROOT / "research" / "named-loop-current-eddy-identities.json"
EXTERNAL_EVIDENCE = {
    55: {
        "source_url": "https://repository.library.noaa.gov/view/noaa/28993",
        "relation": "independent_named_2010_ring_account",
        "note": "NOAA-hosted primary research identifies Eddy Franklin as the 2010 Loop Current anticyclonic ring. It does not supply a NASA identity match or a closed OSW state footprint in this ledger.",
    },
}


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    names = []
    for event in source["entries"]:
        number = event["source_number"]
        primary = {
            "id": f"loop-{number:02d}-primary",
            "name": event["name"],
            "role": "primary",
            "source_number": number,
            "initial_separation": event["initial_separation"],
            "related_primary_id": None,
        }
        if number in EXTERNAL_EVIDENCE:
            if event["name"] != "Franklin" or event["initial_separation"][:4] != "2010":
                raise ValueError("External ring evidence no longer matches Horizon's Franklin event")
            primary["external_evidence"] = EXTERNAL_EVIDENCE[number]
        names.append(primary)
        if event["secondary_name"]:
            names.append({
                "id": f"loop-{number:02d}-secondary",
                "name": event["secondary_name"],
                "role": "secondary",
                "source_number": number,
                "initial_separation": None,
                "related_primary_id": f"loop-{number:02d}-primary",
            })
    if len({item["name"].casefold() for item in names}) != len(names):
        raise ValueError("Duplicate named eddy labels require manual identity review")
    result = {
        "schema": "osw.almanac.named-loop-eddy-identities.v1",
        "source_ledger": "research/named-loop-current-eddies.json",
        "source": source["source"],
        "retrieved_date": source["retrieved_date"],
        "identity_rule": "One primary name per numbered Horizon event; a nonempty 'Name of Secondary Eddy' cell becomes a linked secondary name record. Secondary names have no independently reported separation date, numbered event, dated footprint, or track in this source.",
        "numbered_event_count": len(source["entries"]),
        "secondary_name_count": sum(item["role"] == "secondary" for item in names),
        "entries": names,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(names)} eddy names from {len(source['entries'])} numbered events")


if __name__ == "__main__":
    main()

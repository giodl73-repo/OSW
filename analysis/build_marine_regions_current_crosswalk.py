"""Reconcile Marine Regions' Current gazetteer type with OSW's named ledger."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research" / "marine-regions-current-crosswalk.json"
TYPE_URL = "https://www.marineregions.org/rest/getGazetteerTypes.json/"
RECORD_URL = "https://www.marineregions.org/rest/getGazetteerRecordsByType.json/Current/"
ALIASES = {
    18978: "peru-humboldt",  # Source uses Peru Current; OSW lists Peru (Humboldt).
    30100: "guiana",        # Guyana/Guiana spelling variant; geographic extent still needs source review.
    30103: "falkland",      # Malvinas is the alternative name recorded in OSW.
}
EXCLUSIONS = {
    18527: ("different_object_type", "Source calls the North Atlantic Subtropical Gyre a Current, but it is a gyre system, not one named current."),
    30234: ("generic_class", "Western Boundary Current is a current class, not an individual named flow."),
    31753: ("sea_ice_drift", "Transpolar Drift Stream is sea-ice drift, outside this ocean-current ledger."),
    33645: ("circulation_system", "South China Sea Water Circulation is a regional circulation system, not one named current."),
}
REVIEWED_CANDIDATES = {
    5398: {
        "review_note": "NOAA's repeated 28°35′N sections found a southward band near the proposed Antilles–Guiana Countercurrent, but its water properties matched the adjacent northward band. The authors favored eddies over two continuous currents. This is a historical current hypothesis, not a verified path or state crossing.",
        "review_source_url": "https://spo.nmfs.noaa.gov/sites/default/files/pdf-content/1975/733/ingham.pdf",
        "review_status": "historical_continuity_disputed",
    },
    30232: {
        "review_note": "The gazetteer assigns this alternative-classification name to the North Sea, but its cited Sivkov et al. study describes intermittent bottom currents in the Baltic Sea driven by inflow from the North Sea. The cited abstract does not establish a separately bounded North Sea current, so a route, length, and OSW state crossing remain unresolved.",
        "review_source_url": "https://doi.org/10.1144/GSL.MEM.2002.022.01.10",
        "review_status": "gazetteer_geography_conflicts_with_cited_study",
    },
}


def fetch(url: str) -> tuple[object, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": "OSW-Ocean-Motion-Almanac/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
    return json.loads(raw), raw


def main() -> None:
    types, _ = fetch(TYPE_URL)
    if not any(item["typeID"] == 26 and item["type"] == "Current" for item in types):
        raise ValueError("Marine Regions Current type changed")
    current_ledger = json.loads((ROOT / "research" / "ocean-current-almanac.json").read_text(encoding="utf-8"))
    by_name = {item["name"].casefold(): item["id"] for item in current_ledger["entries"]}
    for entry in current_ledger["entries"]:
        for name in entry.get("aliases", []):
            key = name.casefold()
            if key in by_name and by_name[key] != entry["id"]:
                raise ValueError(f"Ambiguous current alias: {name}")
            by_name[key] = entry["id"]
    by_id = {item["id"] for item in current_ledger["entries"]}
    if not set(ALIASES.values()) <= by_id:
        raise ValueError("Alias mapping refers to a missing OSW current")
    records = []
    hashes = []
    offset = 0
    while True:
        url = f"{RECORD_URL}?offset={offset}"
        batch, raw = fetch(url)
        hashes.append({"url": url, "sha256": hashlib.sha256(raw).hexdigest(), "count": len(batch)})
        if not isinstance(batch, list):
            raise ValueError("Marine Regions Current endpoint did not return a list")
        records.extend(batch)
        if len(batch) < 100:
            break
        offset += 100
    if len({item["MRGID"] for item in records}) != len(records):
        raise ValueError("Duplicate Marine Regions identifier")
    result = []
    for item in records:
        mrgid = int(item["MRGID"])
        name = item["preferredGazetteerName"]
        primary = next((entry["id"] for entry in current_ledger["entries"] if entry["name"].casefold() == name.casefold()), None)
        ledger_alias = by_name.get(name.casefold()) if primary is None else None
        alias = ALIASES.get(mrgid)
        if mrgid in EXCLUSIONS:
            status, note = EXCLUSIONS[mrgid]
            matched = None
        elif primary or ledger_alias or alias:
            status = "matched_exact_name" if primary else "matched_alias_review"
            note = "Exact preferred-name match." if primary else "Name alias matched; geographic and historical identity requires source review."
            matched = primary or ledger_alias or alias
        else:
            status = "candidate_needs_review"
            note = "Source lists this as a Current; OSW has not resolved identity, location, or relationship to an existing name."
            matched = None
        record = {
            "mrgid": mrgid,
            "name": name,
            "source": item.get("gazetteerSource"),
            "source_status": item.get("status"),
            "source_accepted_mrgid": item.get("accepted"),
            "source_place_type": item.get("placeType"),
            "source_point": [item["longitude"], item["latitude"]] if item.get("longitude") is not None and item.get("latitude") is not None else None,
            "source_bbox": [item["minLongitude"], item["minLatitude"], item["maxLongitude"], item["maxLatitude"]] if all(item.get(key) is not None for key in ("minLongitude", "minLatitude", "maxLongitude", "maxLatitude")) else None,
            "record_url": f"https://www.marineregions.org/gazetteer.php?p=details&id={mrgid}",
            "join_status": status,
            "osw_current_id": matched,
            "join_note": note,
        }
        if mrgid in REVIEWED_CANDIDATES:
            record.update(REVIEWED_CANDIDATES[mrgid])
        result.append(record)
    output = {
        "schema": "osw.almanac.marine-regions-current-crosswalk.v1",
        "retrieved_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "type_url": TYPE_URL,
        "record_endpoint": RECORD_URL,
        "source_batches": hashes,
        "source_record_count": len(result),
        "method": "Inventory every Marine Regions gazetteer record returned by place type Current. Match exact OSW names, explicit ledger aliases, and three reviewed lexical aliases; retain all other names as candidates or explicit type exclusions. Candidate review evidence does not promote a name to a verified current. Most records have no source coordinates. This is a source-specific name reconciliation, not a global current census, spatial footprint, or NASA identification.",
        "records": result,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(result)} source names: {sum(item['join_status'].startswith('matched') for item in result)} matched, {sum(item['join_status'] == 'candidate_needs_review' for item in result)} candidates, {len(EXCLUSIONS)} exclusions")


if __name__ == "__main__":
    main()

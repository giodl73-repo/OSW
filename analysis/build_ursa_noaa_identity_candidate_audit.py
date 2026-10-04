"""Record NOAA daily detections near source-dated Ursa events without naming one.

Requires two existing NOAA MUNSTER daily state snapshots. The source paper's
maps and event dates guide a broad candidate window, not an identity match.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research" / "ursa-2021-noaa-identity-candidate-audit.json"
DATES = ("20210308", "20210426")
PAPER = "https://repository.library.noaa.gov/view/noaa/71031"
PAPER_PDF_SHA256 = "051dc76cf47b625c040576a2d75f27c1979e188ca1c35904af5a6d24bd018ad5"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    dates = []
    for date in DATES:
        path = ROOT / "research" / f"noaa-munster-eddy-state-{date}.json"
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        if snapshot["date"] != f"{date[:4]}-{date[4:6]}-{date[6:]}":
            raise ValueError(f"Wrong NOAA snapshot date: {date}")
        candidates = []
        for item in snapshot["entries"]:
            longitude, latitude = item["center"]
            radius = item["radius_km"]
            if (item["polarity"] == "anticyclonic" and
                    longitude is not None and latitude is not None and radius is not None and
                    -90.5 <= longitude <= -83.5 and 24 <= latitude <= 29 and radius >= 25):
                candidates.append({
                    "noaa_daily_detection_id": item["id"],
                    "center_lon_lat": item["center"],
                    "radius_km": radius,
                    "contained_osw_states": item["contained_states"],
                    "intersected_osw_states": item["intersected_states"],
                    "name_match_status": "unverified",
                })
        dates.append({
            "observation_date": snapshot["date"],
            "event_stage": ("temporary_detachment" if date == "20210308" else
                            "final_detachment_reported"),
            "source_snapshot_path": path.relative_to(ROOT).as_posix(),
            "source_snapshot_sha256": digest(path),
            "source_netcdf_url": snapshot["source"],
            "source_netcdf_sha256": snapshot["source_sha256"],
            "candidate_count": len(candidates),
            "candidates": sorted(candidates, key=lambda row: (-row["radius_km"], row["noaa_daily_detection_id"])),
        })
    if [item["candidate_count"] for item in dates] != [5, 4]:
        raise ValueError(f"The broad NOAA candidate counts changed: {[item['candidate_count'] for item in dates]}")
    result = {
        "schema": "osw.almanac.ursa-noaa-identity-candidate-audit.v1",
        "named_eddy_id": "published:ursa-2021",
        "paper_url": PAPER,
        "paper_doi": "10.1016/j.pocean.2025.103529",
        "paper_pdf_sha256": PAPER_PDF_SHA256,
        "paper_locator": "Section 3.6; Figures 19–20",
        "candidate_window_lon_lat": [-90.5, 24, -83.5, 29],
        "candidate_minimum_radius_km": 25,
        "method": "Select every anticyclonic MUNSTER daily detection centered in a deliberately broad eastern-Gulf window around the source paper's Ursa event maps, with radius at least 25 km. Retain NOAA local IDs and already calculated OSW contour-state joins without promoting a detection to a named identity.",
        "identity_decision": "unresolved_multiple_candidates",
        "claim_limit": "The source paper's maps and event dates do not identify a NOAA MUNSTER daily ID. Nearby anticyclones can have different state joins; no listed state is attributed to named Ursa. NOAA MUNSTER and the paper's analyzed/model fields have different eddy definitions, and the NOAA product's reuse terms remain under review.",
        "dates": dates,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print([(item["observation_date"], item["candidate_count"]) for item in dates])


if __name__ == "__main__":
    main()

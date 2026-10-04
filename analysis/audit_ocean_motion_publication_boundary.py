"""Audit the local almanac bundle against the screened dataset boundary.

Default mode writes a factual audit. --gate exits unsuccessfully while the
site still serves the full candidate with unresolved provider-value uses.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "almanac"
PACKAGE = SITE / "release" / "v0.1.0"
OUTPUT = SITE / "release" / "publication-boundary-audit.json"
SITE_FILES = ("index.html", "app.js", "object.html", "object.js", "movies.html", "movies.js")
REFERENCE = re.compile(r"[\"'`]((?:\.\./research/|release/v0\.1\.0/)[^\"'`]+)[\"'`]")
FAMILY_MARKERS = {
    "Horizon named Loop eddies": ("named-loop-current-eddies", "ocean-eddy-name-inventory",
                                   "named-loop-eddy"),
    "NOAA MUNSTER detections and tracks": ("noaa-munster-", "noaa-nasa-eddy-crop-join"),
    "NAVO front and FREDDIES observations": ("gulf-stream-navo-", "navo-freddies-"),
    "NOAA LSA velocity-derived path": ("gulf-stream-geostrophic-", "noaa-lsa-"),
    "ArcGIS arrow-derived joins and spans": ("cartographic-ocean-current-state-join",
                                            "ocean-current-illustrated-spans"),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", action="store_true", help="fail if full-candidate source uses remain")
    args = parser.parse_args()
    sources = json.loads((PACKAGE / "sources.json").read_text(encoding="utf-8"))
    pending_used = [row for row in sources if row.get("kind") == "external" and
                    row.get("rights_status", "").startswith("pending") and
                    row.get("record_count", 0) > 0]
    references = {}
    for name in SITE_FILES:
        path = SITE / name
        references[name] = sorted(set(REFERENCE.findall(path.read_text(encoding="utf-8"))))
    all_references = {ref for group in references.values() for ref in group}
    research_references = sorted(ref for ref in all_references if ref.startswith("../research/"))
    candidate_references = sorted(ref for ref in all_references if ref.startswith("release/v0.1.0/"))
    families = {family: sorted(ref for ref in research_references + candidate_references
                               if any(marker in ref for marker in markers))
                for family, markers in FAMILY_MARKERS.items()}
    screened = json.loads((SITE / "release" / "v0.1.0-rights-screened-preview" /
                           "screening-report.json").read_text(encoding="utf-8"))
    pending_digest = hashlib.sha256(("\n".join(sorted(row["id"] for row in pending_used)) + "\n").encode(
        "utf-8")).hexdigest()
    preview_matches_current_source_review = (
        screened["excluded_used_pending_source_count"] == len(pending_used) and
        screened["excluded_used_pending_source_id_sha256"] == pending_digest)
    blocked = bool(pending_used and PACKAGE.is_dir()) or not preview_matches_current_source_review
    report = {
        "status": "full_research_bundle_not_cleared_for_public_dataset_promotion",
        "scope": "Local almanac HTML and JavaScript static references; dynamic manifest paths are represented by their loaded manifest, not enumerated here.",
        "site_files_checked": list(SITE_FILES),
        "static_reference_counts": {name: len(refs) for name, refs in references.items()},
        "research_reference_count": len(research_references),
        "full_candidate_reference_count": len(candidate_references),
        "pending_used_external_source_count": len(pending_used),
        "pending_provider_value_source_count": sum(bool(row.get("provider_asset_redistributed"))
                                                   for row in pending_used),
        "full_candidate_directory_in_site_tree": PACKAGE.is_dir(),
        "source_family_references": families,
        "screened_preview_status": screened["status"],
        "screened_preview_entity_count": screened["counts"]["entities"],
        "screened_preview_matches_current_source_review": preview_matches_current_source_review,
        "publication_gate": "blocked_until_source_use_and_site_bundle_reconciled" if blocked else "source_use_boundary_clear",
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                      encoding="utf-8")
    print(f"Almanac boundary: {len(research_references)} research references, "
          f"{len(candidate_references)} full-candidate references, "
          f"{len(pending_used)} pending used external sources")
    if args.gate and blocked:
        raise SystemExit("Publication gate remains closed: the local site loads full-candidate source uses")


if __name__ == "__main__":
    main()

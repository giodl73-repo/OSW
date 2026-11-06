"""Frozen source-statement report/diagram; no current geometry or annual statistics."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "research/reported-current-width-evidence-preflight-v1.json"
FACTS = "research/eicc-wijesekera-2015-width-source-facts-v1.json"
REPORT = ROOT / "research/eicc-wijesekera-2015-width-evidence-v1.json"
FIGURE = ROOT / "figures/eicc-wijesekera-2015-width-evidence-v1.svg"
SUPPORT = {
    "source_reported_shipboard_survey_summary",
    "source_reported_observational_synthesis_context",
    "source_reported_combined_observation_model_context",
}
NULL_FIELDS = (
    "whole_current_width_km", "annual_width_min_km", "annual_width_max_km",
    "seasonal_width_range_km", "geometry", "area_km2", "state_intersections",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate(facts: dict) -> None:
    if facts.get("schema") != "osw.reported-current-width-evidence-facts.v1":
        raise ValueError("Unexpected source facts schema")
    if facts.get("identity_status") != "prepared_identity_pending_canonical_admission":
        raise ValueError("This source-stage method cannot promote identity")
    eligibility = facts["eligibility"]
    expected = {
        "canonical_identity_admitted": False,
        "canonical_width_admissions": 0,
        "new_independent_width_observations": 0,
        "width_ranking_eligible": False,
        "physical_seasonal_playback_eligible": False,
        **{key: None for key in NULL_FIELDS},
    }
    if eligibility != expected or any(type(eligibility[k]) is not type(v) for k, v in expected.items()):
        raise ValueError("Physical/annual/canonical admission is outside this method")
    rows = facts["reported_widths"]
    if len(rows) != 3 or {r["support_kind"] for r in rows} != SUPPORT:
        raise ValueError("Retain three distinct support contexts without duplicate sampling")
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate statement identity")
    for row in rows:
        value = row["reported_width_km"]
        if type(value) not in (int, float) or not math.isfinite(value) or not 0 < value <= 300:
            raise ValueError("Invalid value or outside the prospective diagram scale")
        if row.get("canonical_width_admitted") is not False:
            raise ValueError("Source summary is not canonical admission")
        for key in ("width_boundary_criterion", "width_edge_coordinates", "uncertainty_km", "width_depth_interval_m"):
            if row.get(key) is not None:
                raise ValueError("Do not invent a threshold, edges, error or width layer")
        level = row.get("width_depth_level_m")
        if level is not None and (type(level) not in (int, float) or not math.isfinite(level) or level < 0):
            raise ValueError("Invalid source-associated depth level")
        if row["support_kind"] != "source_reported_shipboard_survey_summary" and level is not None:
            raise ValueError("Contextual summaries have no admitted numerical width level")
        if not row.get("locator") or not row.get("date_assignment") or not row.get("geographic_scope"):
            raise ValueError("Missing source scope")
    source = facts["source"]
    if source.get("access_scope") != "retained_full_primary_article_selected_passages_reviewed":
        raise ValueError("Full primary source required; not abstract-only support")
    if source.get("original_asset_redistributed") is not False or source.get("source_figures_digitized") is not False:
        raise ValueError("No original redistribution or figure digitization authorized")


def inspect_inputs() -> tuple[dict, dict]:
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    for relative, expected in preflight["input_sha256"].items():
        path = (ROOT / relative).resolve()
        if not path.is_relative_to(ROOT) or digest(path.read_bytes()) != expected:
            raise ValueError(f"Pinned input differs: {relative}")
    facts = json.loads((ROOT / FACTS).read_text(encoding="utf-8"))
    validate(facts)
    source = facts["source"]
    original = ROOT / source["original_file"]
    if original.stat().st_size != source["original_bytes"] or digest(original.read_bytes()) != source["original_sha256"]:
        raise ValueError("Retained original differs")
    import pymupdf
    import unicodedata
    with pymupdf.open(original) as pdf:
        if len(pdf) != source["original_pdf_pages"]:
            raise ValueError("Original page count differs")
        for item in preflight["source_page_anchors"]:
            text = " ".join(unicodedata.normalize("NFKC", pdf[item["pdf_page"] - 1].get_text()).split())
            if any(anchor not in text for anchor in item["anchors"]):
                raise ValueError(f"Source passage anchor missing on PDF page{item['pdf_page']}")
    return facts, preflight


def report_bytes(facts: dict, preflight: dict) -> bytes:
    validate(facts)
    report = {
        "schema": "osw.reported-current-width-evidence-report.v1",
        "method": "plans/reported-current-width-evidence-protocol-v1.md",
        "input_sha256": preflight["input_sha256"],
        "original_sha256": facts["source"]["original_sha256"],
        "source_statement_count": len(facts["reported_widths"]),
        "independent_observations_created": 0,
        "canonical_admission_verified": False,
        "source_facts": facts,
    }
    return (json.dumps(report, indent=2, ensure_ascii=True, allow_nan=False) + "\n").encode()


def svg_bytes(facts: dict) -> bytes:
    validate(facts)
    esc = html.escape
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="660" viewBox="0 0 1000 660" role="img" aria-labelledby="title desc">',
        '<title id="title">East India Coastal Current: three source-reported width statements</title>',
        '<desc id="desc">Separate reports of about100km on the inbound23-24December2013 ship transect, approximately200km at the westward turn south of Sri Lanka, and250km in broader south-and-west observation/model discussion. Different scopes, not an annual range. Errors and current edges unknown. Canonical admission pending.</desc>',
        '<rect width="1000" height="660" fill="#f5f8fc"/>',
        '<g font-family="Arial, sans-serif" fill="#152b40">',
        '<text x="36" y="44" font-size="25" font-weight="bold">East India Coastal Current</text>',
        '<text x="36" y="73" font-size="17">Source-reported widths | November-December2013 study</text>',
        '<text x="36" y="101" font-size="15">Different locations and support. Three statements; no new independent samples.</text>',
    ]
    details = [
        ("23-24Dec2013; near5.25N; 21m source context", "Shipboard survey summary | section3.2, PDF6-7"),
        ("Nov-Dec2013 narrative; exact width-sample days unknown", "Observational synthesis | section3.2, PDF7"),
        ("December2013 study context; precise support window unknown", "Combined observation/model discussion | section4, PDF14"),
    ]
    for index, (row, (time_text, support_text)) in enumerate(zip(facts["reported_widths"], details)):
        y = 150 + index * 120
        value = row["reported_width_km"]
        x = 590 + value * 1.1
        hollow = row["support_kind"] == "source_reported_combined_observation_model_context"
        parts.extend([
            f'<text x="36" y="{y}" font-size="18" font-weight="bold">{esc(row["label"])}</text>',
            f'<text x="36" y="{y+26}" font-size="14">{esc(time_text)}</text>',
            f'<text x="36" y="{y+49}" font-size="14">{esc(support_text)}</text>',
            f'<line x1="590" y1="{y+22}" x2="920" y2="{y+22}" stroke="#b8c7d5"/>',
            f'<circle cx="{x:g}" cy="{y+22}" r="8" stroke="#006b83" stroke-width="3" fill="{"#f5f8fc" if hollow else "#006b83"}"/>',
            f'<text x="{x:g}" y="{y-1}" text-anchor="middle" font-size="18" font-weight="bold">{"~" if row["precision"] in ("about", "approximately") else ""}{value:g} km</text>',
        ])
    for value in (0, 100, 200, 300):
        x = 590 + value * 1.1
        parts.append(f'<text x="{x:g}" y="477" text-anchor="middle" font-size="13">{value}</text>')
    parts.extend([
        '<text x="755" y="499" text-anchor="middle" font-size="13">Reported width (km); marker position only</text>',
        '<text x="36" y="533" font-size="15">250km covers a broader south-and-west scope; it is not an error bound on200km.</text>',
        '<text x="36" y="558" font-size="15">Unknown edges, cutoff and errors. No annual range, geographic footprint or seasonal animation.</text>',
        '<text x="36" y="583" font-size="15">Full primary article retained; selected passages reviewed. Canonical identity/width delivery pending.</text>',
        f'<a href="{esc(facts["source"]["publisher_url"], quote=True)}"><text x="36" y="615" font-size="14" fill="#006b83">Wijesekera et al.2015 | doi:10.1002/2015JC010744 | original linked; source figures not copied</text></a>',
        '</g></svg>\n',
    ])
    return "\n".join(parts).encode()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "check"))
    action = parser.parse_args().action
    facts, preflight = inspect_inputs()
    outputs = ((REPORT, report_bytes(facts, preflight)), (FIGURE, svg_bytes(facts)))
    if action == "build":
        if any(path.exists() for path, _ in outputs):
            raise ValueError("Existing products are immutable; use check or a new version")
        for path, data in outputs:
            path.write_bytes(data)
    else:
        for path, data in outputs:
            if path.read_bytes() != data:
                raise ValueError(f"Product differs: {path.name}")
    print(json.dumps({"action": action, "products": {p.relative_to(ROOT).as_posix(): digest(b) for p, b in outputs}, "canonical_admission_verified": False}))


if __name__ == "__main__":
    main()

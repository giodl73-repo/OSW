"""Audit conflicting Cameron/Darwin chronology before cross-source identity joins."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "named-loop-current-eddy-identities.json"
TARGET = ROOT / "research" / "loop-eddy-cameron-darwin-name-date-conflict.json"
PAPER_URL = "https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2019JC015172"
OBSERVATION_URL = "https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2012JC007890"

# These are *paper statements*, not a harmonized event chronology. Section
# 2.1 reverses the assignment used by Section 3.4. Horizon reports an
# initial December 2008 Darwin separation, so a later February 2009 paper
# event cannot be equated to that initial date without a stage mapping.
PAPER_ASSIGNMENTS = {
    "section_2_1": {"Darwin": "2008-07", "Cameron": "2009-02"},
    "section_3_4": {"Cameron": "2008-07", "Darwin": "2009-02"},
}


def build() -> dict:
    horizon = json.loads(SOURCE.read_text(encoding="utf-8"))
    relevant = {row["name"]: row for row in horizon["entries"]
                if row["name"] in {"Cameron", "Darwin"}}
    assert set(relevant) == {"Cameron", "Darwin"}
    horizon_months = {name: row["initial_separation"][:7]
                      for name, row in relevant.items()}
    assert PAPER_ASSIGNMENTS["section_2_1"] != PAPER_ASSIGNMENTS["section_3_4"]
    assert horizon_months == {"Cameron": "2008-07", "Darwin": "2008-12"}
    return {
        "schema": "osw.almanac.loop-eddy-name-date-conflict-audit.v1",
        "as_of": "2026-09-30",
        "paper": {
            "url": PAPER_URL,
            "doi": "10.1029/2019JC015172",
            "title": "Medium-Term Forecasting of Loop Current Eddy Cameron and Eddy Darwin Formation in the Gulf of Mexico With a Divide-and-Conquer Machine Learning Approach",
            "reference_field": "GoM-HYCOM simulated sea surface height, January 1992 to December 2009; LSTM forecasts are evaluated against that model field",
            "reference_field_locator": "Section 2.1, Data Set; Sections 3.4 and 3.5",
            "publisher_erratum": {
                "source_locator": "Erratum at end of full text, dated 2019-09-06 on publisher page",
                "scope": "Corrects transposed references to Figures 4 and 5 in Section 3.1 only; it does not address the Cameron/Darwin chronology in Sections 2.1 or 3.4.",
            },
            "claims": [
                {
                    "source_locator": "Section 2.1, Data Set, final paragraph",
                    "name_to_separation_month": PAPER_ASSIGNMENTS["section_2_1"],
                    "claim_role": "internally_conflicting_model_event_assignment",
                },
                {
                    "source_locator": "Section 3.4, opening paragraph and Figure 9 caption",
                    "name_to_separation_month": PAPER_ASSIGNMENTS["section_3_4"],
                    "claim_role": "model_event_assignment_matching_Horizon_Cameron_month_only",
                },
            ],
        },
        "horizon": {
            "source_url": horizon["source"],
            "source_ledger": "research/named-loop-current-eddy-identities.json",
            "records": [
                {"id": "horizon:" + relevant[name]["id"], "name": name,
                 "initial_separation": relevant[name]["initial_separation"]}
                for name in ("Cameron", "Darwin")
            ],
        },
        "independent_observation": {
            "url": OBSERVATION_URL,
            "doi": "10.1029/2012JC007890",
            "title": "Observations of intermittent deep currents and eddies in the Gulf of Mexico",
            "publication_date": "2012-09-14",
            "methods": "Moored current measurements interpreted with AVISO altimetry; the Cameron and Darwin names are expressly credited to Horizon Marine in Table 2 and Figure 3.",
            "name_origin": "horizon_attributed_not_independently_named",
            "observations": [
                {
                    "name": "Cameron",
                    "date": "2009-01-20",
                    "source_locator": "Section 4.1.1, paragraph 32; Figure 6a",
                    "reported_position_lon_lat": [-95.0, 22.5],
                    "position_semantics": "Approximate eddy center at mooring A on this date, not a whole-eddy footprint",
                    "reported_diameter_km_approx": 300,
                },
                {
                    "name": "Darwin",
                    "date": "2009-07-25",
                    "source_locator": "Section 4.1.2, paragraph 36; Figure 7a",
                    "reported_position_lon_lat": None,
                    "position_semantics": "Northeast of the L/A/K moorings, with southwestern edge across the moorings; no center coordinate transcribed",
                    "reported_diameter_km_approx": 200,
                },
                {
                    "name": "Darwin",
                    "date": "2009-08-05",
                    "source_locator": "Section 4.1.2, paragraph 37; Figure 7b",
                    "reported_position_lon_lat": None,
                    "position_semantics": "Mooring A is near the center; mooring coordinates are not asserted as an exact eddy-center coordinate",
                    "reported_diameter_km_approx": None,
                },
            ],
            "date_semantics": "These are dated western Gulf observations, not initial separation dates or complete lifetimes.",
            "identity_evidence": "Independent observations of named features, but the labels originate with Horizon; the paper does not independently resolve the 2019 article's internal formation-date conflict.",
        },
        "assessment": {
            "type": "within_paper_name_date_inconsistency",
            "section_2_1_matches_horizon": PAPER_ASSIGNMENTS["section_2_1"] == horizon_months,
            "section_3_4_matches_horizon_by_name": {
                name: PAPER_ASSIGNMENTS["section_3_4"][name] == horizon_months[name]
                for name in ("Cameron", "Darwin")
            },
            "darwin_stage_difference": "Horizon gives initial separation on 2008-12-08; the paper's Section 3.4 describes a February 2009 simulated-model separation. These may be different detachment stages, but the article does not establish that correspondence.",
            "paper_event_basis": "simulated_reference_field_not_independent_observation",
            "identity_join_status": "unresolved_do_not_merge_or_count_as_independent_observed_rings",
            "resolution_need": "A corrected 2019 article statement or a dated observed-ring source that independently maps each label to its initial detachment stage. The 2012 mooring paper establishes later western Gulf observations but credits its names to Horizon.",
        },
    }


if __name__ == "__main__":
    payload = build()
    TARGET.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {TARGET.relative_to(ROOT)}: {payload['assessment']['type']}")

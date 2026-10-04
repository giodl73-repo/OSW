---
skill: roles-check
topic: ocean-motion-independent-current-names
date: 2026-10-02
source_commit: 5298e8b33a918752496ab334fc7e597fed32dc24
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

This reviews the uncommitted replacement of three ArcGIS-derived naming
citations, and the dependent candidate, screened export, and review site.
It is a narrow provenance review, not external scientific approval of the
atlas release. ORBIT is excluded because no planetary analogy changes.
Each selected role owns a changed data, presentation, validation, or release
boundary. The authoritative inputs are the three current entries, source-use
reviews, metadata overrides, generated manifests, and validation output.

| Role | Finding | Severity | Evidence and disposition |
|---|---|---|---|
| CURRENT | Caribbean naming evidence describes regional presence, not a measured whole-current path. | P3 | Report section 3.1.2 supports the name; length remains null. Preserve that scope. |
| CURRENT | The South Atlantic paper distinguishes surface and intermediate expressions. | P2 | Section 3.5 is used for identity only. No float track or surface-axis measurement is admitted. Review depth before adding path geometry. |
| CURRENT | South Indian naming evidence identifies eastward flow near 40 degrees S. | P3 | Grand et al. section 3.2 supports the existing subtropical identity. Preserve its distinction from the countercurrent and Agulhas Return Current. |
| SOUNDER | All three identities now have independent URLs and exact section locators. | P3 | Current ledger records name_source and name_source_locator. Retain them in source-ledger claim excerpts. |
| SOUNDER | Bibliographic identity is available for all three sources. | P3 | Metadata overrides record title, year/date, citation, and evidence URL; the new DOI has a matched Crossref receipt. Preserve pinned receipts. |
| SOUNDER | Linked factual use does not establish permission to redistribute source figures or data. | P2 | Source-use notes explicitly limit current use. Re-review if geometry or source assets are added. |
| CHART | A naming citation alone cannot support a state crossing. | P2 | Screened export still removes ArcGIS arrow-derived state relations. Keep unresolved pairs explicit. |
| CHART | The illustrated spans depend on a secondary source reference. | P2 | Fixed source usage accounting to count illustration_source_id; added a check requiring 27 ArcGIS-supported length-assessment rows in the pending queue. |
| CHART | Approximate editorial locator points remain distinct from measured paths. | P3 | Three retained objects use existing editorial locator geometry, with uncertainty text. Preserve its map and packet label. |
| BEACON | All three names can appear in the inventory without adding unsupported length ranks. | P3 | Screened counts are 98 currents and eight ranked estimates. Keep ranking evidence visible. |
| BEACON | Unknown whole-current lengths must remain visible in the list. | P3 | Inventory now contains 81 records without a whole-current number, including these three. Preserve the unknown category. |
| BEACON | Source replacement must not imply that the ArcGIS terms were cleared. | P2 | Notices and scope text retain a separate pending arrow review. Keep that condition in release notes. |
| HARBOR | The three additions use the existing semantic object and length tables. | P3 | No new pointer-only control is introduced. Browser checks cover their presence in the length inventory. |
| HARBOR | Source links and packet downloads provide a textual evidence route. | P3 | All 216 objects have screened evidence packets; the packet checker verifies closure. Preserve link labels. |
| HARBOR | This narrow automated pass cannot close human accessibility review. | P2 | Existing publication gate remains open. Record an actual human review before publication. |
| KEEL | Current-ledger consistency and full candidate validation pass. | P3 | check_motion_almanac.py and check_ocean_motion_release.py completed successfully after regeneration. |
| KEEL | The screened export is closed over retained records and sources. | P3 | check_ocean_motion_safe_preview.py passes with 216 entities and 8,576 claims; 27 illustrated spans are redacted. |
| KEEL | Changed object counts require a regenerated site and browser expectations. | P2 | Builder and checker counts, length categories, and marker totals were updated; browser verification is a required finish condition for this change. |
| LOGBOOK | Publication documentation contained stale inventory totals. | P2 | Fixed publication boundary and plan from 213/95 to 216/98; unknown-length count becomes 81. |
| LOGBOOK | Attribution must identify the actual paper/report rather than its hosting domain. | P3 | Added titles, authors/agency, sections, and notices. NOAA hosting is not recorded as an Elsevier reuse license. |
| LOGBOOK | Release remains a candidate with scientific, terms, accessibility, and owner gates. | P2 | Candidate and screened status fields are unchanged. Do not label the review bundle an approved or registered dataset. |

Roles reviewed: 7. P1 blockers: 0. P2 conditions: 9. P3 findings: 12.
Verdict: APPROVED-WITH-CONDITIONS for the narrow provenance change.
The main shared condition is that naming evidence does not establish a
physical path, state passage, or measured current length.

Amendments completed: replace the three naming citations with independent
sources and precise locators; count secondary illustration references in the
terms queue and validate the 27-row dependency; refresh preview totals and
source attribution. The regenerated site boundary check passes with 266 files,
216 objects, and 70 NASA crops; the browser test passes search, map, length
inventory, state passports, movies, and deep links. Scientific and human
accessibility review remain release conditions.

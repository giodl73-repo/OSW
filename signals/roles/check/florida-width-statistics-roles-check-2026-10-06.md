---
skill: roles-check
topic: florida-width-statistics
date: 2026-10-06
source_commit: e65b2c1c51024a1ca779ec545d4c039bcc31b2b9
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Florida surface jet width statistics review

Artifact: source audit, width inventory/protocol v1.21, query bundle and atlas
presentation. This reviews the local follow-up to the source commit above.
Seven functional lenses apply; ORBIT is excluded because there is no planetary
comparison. This is an internal review, not independent scientific peer review.

| # | Role | Finding | Severity/status | Evidence and action |
|---|---|---|---|---|
| 1 | CURRENT | Relative threshold identifies a local surface jet. | P3 verified | Both edges at half instantaneous core speed; section 25.42 N retained. |
| 2 | CURRENT | Two-year observed extrema must not become annual limits. | P2 resolved | Dedicated range class and rejection tests; annual eligibility false. |
| 3 | CURRENT | Seasonal phase is supported, numerical monthly widths are missing. | P3 open | August/September peak and late-winter minimum stored separately; recover numeric series next. |
| 4 | SOUNDER | Mean confidence, standard deviation and extrema are different statistics. | P2 resolved | 59, +/-2, 6 and 41-76 km have separate fields and visible explanation. |
| 5 | SOUNDER | Confidence percentage is unresolved in inspected text. | P3 verified | Null retained; no assumed 95 percent. |
| 6 | SOUNDER | Acquisition and sampling support are explicit. | P3 verified | Full publisher HTML inspected; PDF size failure disclosed; 2005-2006 years, 0.75 m nominal sensing depth, 1.2 km grid, 20 minute acquisition and 40 h metric filter retained. |
| 7 | CHART | Summary statistics cannot supply a geographic footprint. | P3 verified | Null section geometry, hidden locator, no route buffer. |
| 8 | CHART | A single bar could imply whole-current dimensions. | P3 verified | Bar omitted for this statistical class. |
| 9 | CHART | Existing route is contextual geography. | P3 verified | Static editorial route note remains beside the map; no seasonal boundary animation. |
| 10 | BEACON | Card headline should show both mean and observed range. | P2 resolved | Atlas summary and inspector show 59 km mean and 41-76 km observed range. |
| 11 | BEACON | Measurement definition and source remain reachable. | P3 verified | Threshold/filter, local support, article link and precise locator retained. |
| 12 | BEACON | Whole-current length/width ranking remains unsupported. | P3 verified | Ranking false; annual and whole-current limitations beside the statistics. |
| 13 | HARBOR | Meaning is available as text without color or motion. | P3 verified | Statistics and limitations in semantic details and text inspector. |
| 14 | HARBOR | Card and inspector navigation must survive small viewports. | P3 verified | Shared URL, atlas-to-inspector link and 320 px reflow browser checks. |
| 15 | HARBOR | Manual assistive-technology review remains outstanding. | P3 open | Semantic controls and keyboard details checked; do not claim full screen-reader review. |
| 16 | KEEL | Unsupported transformations should fail offline. | P3 verified | Tests reject confidence-as-range, new monthly values, physical edges/layers and false annual support. |
| 17 | KEEL | Generated dependencies must share current receipts. | P3 verified | Protocol, source audit, width inventory, dashboard and bundle receipts refreshed. |
| 18 | KEEL | Native and WASM must agree on the new record. | P3 verified | Dedicated browser test compares the returned width record to native output. |
| 19 | LOGBOOK | Coverage must reconcile. | P3 verified | 39 source records, 26 current owners, 67 unassessed; canonical release unchanged. |
| 20 | LOGBOOK | Follow-up publication status must be truthful. | P3 open | Local uncommitted follow-up; PR21 merged the earlier work only. |
| 21 | LOGBOOK | Scientific admission remains a distinct gate. | P3 open | Editorial status and raw-array/geometry recovery gates retained. |

## Synthesis

Seven roles, 21 findings: zero open P1/P2, three resolved P2 issues, 18 P3
notes. APPROVED-WITH-CONDITIONS for local editorial presentation. CURRENT,
SOUNDER and BEACON agree that observed variation, uncertainty on the mean and
seasonal phase cannot substitute for numeric monthly boundary evidence.

Three amendments: give the filtered time-series range its own validation class;
preserve confidence/variation/extrema independently; show mean and range together
on the atlas card. All implemented. Monthly graph extraction, geographic
boundaries, manual assistive-technology review and scientific admission remain.

Verification: 56 Python tests and 417 subtests; 23 Rust tests; JavaScript syntax
and whitespace checks; browser share/reload, semantic details, narrow layout and
native/WASM equality. Agulhas browser regression passes. All 38 earlier source
measurement records are unchanged; Gulf/Loop numerical documents change only
their general protocol hash. Canonical release diff empty.

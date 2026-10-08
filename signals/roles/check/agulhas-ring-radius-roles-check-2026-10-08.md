---
skill: roles-check
topic: agulhas-ring-radius
date: 2026-10-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Internal functional review

CURRENT checks radius definitions and temporal support; SOUNDER provenance and conflicts; CHART visual scope; BEACON readable source claims; HARBOR equivalent access; KEEL reproducibility; LOGBOOK publication and licensing. ORBIT is excluded because no analogy is used. This is internal review, not independent scientific approval.

| Role | Finding | Severity | Location | Resolution |
|---|---|---|---|---|
| CURRENT | Altimetric area-equivalent radius is not an occupied perimeter or transverse current width. | P2 | Methods / audit | Dedicated radius metric, null geometry and all inference flags false. |
| CURRENT | Thermocline fit errors and XBT depth cannot become radius uncertainty or a depth layer. | P2 | Table 1 / protocol | Explicit exclusions; radius uncertainty remains null. |
| CURRENT | The source's velocity terminology and conflicting radii still need independent scientific interpretation. | P3 | Methods / Eliza | Author wording preserved; two canonical radii remain null. |
| SOUNDER | Caption/table disagreements must survive extraction and query. | P2 | Figure 10 / Table 1 | All eleven source claims retained; no preferred value, midpoint or conflict-as-range. |
| SOUNDER | January 2019 versus 2010 must not become a silently corrected date. | P2 | Eliza January slot | Normalized month null; panel label, body/table and caption claims explicit. |
| SOUNDER | Reproducibility needs original bytes and complete evidence binding. | P2 | Generator / geography / bundles | PDF, acquisition, protocol, generator and full audit receipts validated. |
| CHART | Sparse sections must not imply a continuous seasonal trajectory. | P2 | Radius renderer | Separate rows and points; no connecting curve or animation. |
| CHART | Hollow conflicting points need a legend that rules out uncertainty endpoints. | P2 | SVG / caption | Filled/hollow explanation and textual raw claims accompany each chart. |
| CHART | Equivalent-radius circles must not create mapped disks or state intersections. | P2 | Atlas / joins | Existing locators and joins retained; no new geographic primitive. |
| BEACON | A count of records can obscure the unresolved slots and differing Astrid definitions. | P2 | Dashboard / batch | Named scoped radius evidence; batch distinguishes eight records from resolved comparable observations. |
| BEACON | Readers need the radius unit and month beside each value. | P2 | Chart | Section labels, km radius scale and plain text source values supplied. |
| BEACON | Source conflicts need a short route to their exact data. | P2 | Chart anchor | Direct per-owner source query preserves table/caption locators and nulls. |
| HARBOR | Color alone cannot distinguish resolved values from conflicting claims. | P2 | Chart | Filled/hollow shapes, explicit unresolved headings and text alternatives. |
| HARBOR | SVG text must remain readable and unclipped at 320 px. | P2 | Registered browser | All three atlas charts checked for label bounds, effective size and page reflow. |
| HARBOR | The source query link must be available without a pointer. | P2 | Figure anchor | Semantic anchor; keyboard navigation shares the existing query path. |
| KEEL | Updating hashes alone must not admit fabricated radii, ranges or footprints. | P2 | Compiled guard / tests | Full audit comparison rejects coherent rewrites; default Python mutations reject admission changes. |
| KEEL | Both source and canonical query paths must give identical native/WASM results. | P2 | Registered browser | Exact source-query and four-owner evidence-filter parity assertions. |
| KEEL | Complete default and protected remote gates must finish before main landing. | P3 | Publication | Default suite and affected browsers required locally; no remote-gate bypass. |
| LOGBOOK | Original redistribution needs attribution and the actual license link. | P2 | Publisher / acquisition | Publisher Copyright link verified as CC BY 4.0; unchanged original and attribution tracked. |
| LOGBOOK | Added sizes must not be counted as new eddy footprints or repaired annual gaps. | P2 | Batch / coverage | One footprint candidate remains; annual and current-dimension gaps remain explicit. |
| LOGBOOK | Draft publication must not be described as mainline completion. | P3 | Git / PR | Publication state recorded separately; no main landing claim. |

Roles reviewed: 7. P1 blockers: 0. P2 issues: 18 addressed in the scoped implementation and executable gates. P3 notes: 3 scientific/publication follow-ups.

Verdict: APPROVED-WITH-CONDITIONS for editorial source evidence, subject to the documented validation gates. Independent scientific admission and protected main publication remain open.

Amendments: preserve complete conflict claims and unknown dates; use separate filled/hollow section points with textual alternatives; bind the original and full audit in Python/Rust, then verify source queries and coverage lights.

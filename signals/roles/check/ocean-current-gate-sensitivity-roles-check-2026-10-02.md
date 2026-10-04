---
skill: roles-check
topic: ocean-current-gate-sensitivity
date: 2026-10-02
source_commit: 5298e8b33a918752496ab334fc7e597fed32dc24
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

Scope: the uncommitted seven-span sensitivity method, generated gate ledger,
candidate/screened length assessments, and screened atlas length inventory.
The selected roles cover physical interpretation, source identity, geographic
comparison, reader meaning, textual access, reproducibility, and release
status. ORBIT is excluded because no planetary comparison changes.
This functional review does not replace scientific or human accessibility
approval of the release.

| Role | Finding | Severity | Evidence and action |
|---|---|---|---|
| CURRENT | Gate separation is not along-current length. | P2 | The ledger, METHODS, and visible scenario text explicitly restrict the quantity. Keep whole-current ranking separate. |
| CURRENT | Upper-ocean fronts and deeper gyre return flows have different boundaries. | P3 | The definition audit records direct primary-source evidence and defers unsupported whole-current numbers. Follow its layer/branch admission requirements. |
| CURRENT | Geographic scenarios do not describe meanders or changing separation. | P3 | The interpretation says no measured path or physical confidence interval. Preserve this limit on any chart. |
| SOUNDER | The perturbation size is an editorial assumption. | P2 | perturbation_basis identifies ±0.5 degrees as a scenario choice, not source uncertainty. Obtain empirical error before interpreting statistical reliability. |
| SOUNDER | Source gates and existing citations are preserved. | P3 | Seven entries retain start/end, gate type, source URL, and conditional rounded floor. No new provider geometry is imported. |
| SOUNDER | Rank metadata is linked to its method ledger. | P3 | length_assessments carries gate_distance_method_source_id; release checks require exact equality with the gate receipt. Keep the reference in evidence packets. |
| CHART | Comparisons cover seven geographic spans with differing extents. | P2 | rank_interpretation and visible text state the comparison set and exclude current-length rank. Do not mix these positions into the published table. |
| CHART | Tied spans have possible positions rather than an artificial strict order. | P3 | Benguela and Brazil both receive positions 6–7. The other five finite envelopes are disjoint for this chosen perturbation. Preserve ties. |
| CHART | Latitude-only gates remain on an abstract common meridian. | P3 | No longitude or geographic core is invented by the computation. Do not draw this computation as an observed line. |
| BEACON | Every displayed range states its scenario and limitation. | P3 | Seven inventory rows contain ranges, ±0.5-degree gate scenarios, comparison-set size, and confidence-interval caveat. Keep the language beside the number. |
| BEACON | Whole-current unknowns remain visible. | P3 | 81 inventory records still have no admitted whole-current number, and eight published ranks remain unchanged. Do not count scenarios as new known current lengths. |
| BEACON | Scenario information initially appeared in the wrong rendering loop. | P3 | Browser verification caught the missing seven rows; the block was moved into the full length inventory and the rerun passes. Keep this browser assertion. |
| HARBOR | Scenario meaning is exposed in semantic table text. | P3 | No palette, pointer action, or animation is required to read values and limits. Retain the textual comparison. |
| HARBOR | Search and existing keyboard controls still work. | P3 | The browser test exercises inventory search, skip link, map links, and state controls after regeneration. Preserve these checks. |
| HARBOR | Human accessibility review is still required for publication. | P2 | Automated presence and keyboard checks do not prove screen-reader usability or complete accessibility. The publication condition remains open. |
| KEEL | All declared scenarios are enumerated deterministically. | P3 | Cartesian products produce 9 meridional or 81 point-gate scenarios using WGS84. The checker verifies scenario counts and baseline containment. |
| KEEL | Envelope and possible-position output is verified independently of the UI. | P3 | check_motion_almanac.py asserts the seven rank pairs; release checking validates ranges, source equality, schema, CSV parity, and hashes. Preserve these gates. |
| KEEL | Generated package and rendered behavior both pass. | P3 | Full candidate, screened preview/site, JS syntax, and screened browser checks passed. The browser verifies seven sensitivity rows and the two shared positions. |
| LOGBOOK | Methods and change log describe the new quantity. | P3 | METHODS names finite scenarios, assumptions, exclusions, and regeneration; CHANGELOG records the addition. Keep the method tied to the candidate version. |
| LOGBOOK | This does not complete the user's broader length inventory. | P2 | No additional whole-current estimate is admitted in this pass. The definition audit specifies the next source and identity work. Continue route admissions. |
| LOGBOOK | Candidate and preview status remain truthful. | P3 | Manifests retain candidate/review status, 216 screened entities, and 70 crops. Do not claim an official or published dataset from these checks. |

Roles reviewed: 7. P1 blockers: 0. P2 conditions: 5. P3 findings: 16.
Verdict: APPROVED-WITH-CONDITIONS for the method and presentation change.
CURRENT, CHART, and BEACON agree that geographic gate separation and
whole-current path length must remain distinct quantities.

Three amendments completed: declare the perturbation assumption and finite
envelope limits; retain possible positions and ties in a separate comparison
set; expose the method beside each inventory value and verify the rendered
rows. Broader whole-current measurement, scientific review, and human
accessibility review remain work for the active atlas goal.

---
skill: roles-check
topic: cameron-darwin-observed-positions
date: 2026-09-30
roles_used: 5
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Cameron and Darwin dated observations: role review

Artifact: `research/loop-eddy-cameron-darwin-name-date-conflict.json`, its
builder, and the accompanying release methods. CURRENT reviews event physics;
SOUNDER reviews source provenance; CHART reviews position and footprint meaning;
KEEL reviews regeneration; LOGBOOK reviews the release boundary.

| Role | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| CURRENT | The 2012 study observes western Gulf occurrences, whereas the 2019 article discusses formation or separation in a simulated field. | P2 | Both paper claims | Keep observation and formation dates in different fields. Done. |
| CURRENT | Cameron's January 20 center is an instantaneous location. | P2 | 2012 Section 4.1.1 | Do not infer a complete track or lifetime. Done. |
| CURRENT | Darwin's July 25 diameter and August 5 near-center description are different dates and evidence types. | P2 | 2012 Section 4.1.2 | Preserve separate observations. Done. |
| SOUNDER | The 2012 mooring and altimetry evidence is independent of the 2019 model reference field. | P3 | 2012 methods | Preserve the observation source and method in the audit. Done. |
| SOUNDER | The 2012 authors explicitly credit the Cameron and Darwin labels to Horizon Marine. | P2 | 2012 Table 2 footnote | Label the name origin as Horizon-attributed, not independently coined. Done. |
| SOUNDER | The paper's narrative contains additional broad month references that are not an initial detachment chronology. | P2 | 2012 Sections 3–4 | Cite the exact dated figure paragraphs for each transcribed observation. Done. |
| CHART | A center point cannot establish an eddy footprint or state containment. | P2 | Cameron 2009-01-20 | Keep the coordinate in the audit without a polygon or containment edge. Done. |
| CHART | Darwin is northeast of an array on July 25; no center coordinate is stated in that paragraph. | P2 | Darwin 2009-07-25 | Leave the coordinate null. Done. |
| CHART | A mooring near Darwin's center on August 5 is not the exact center. | P2 | Darwin 2009-08-05 | Leave the coordinate null and state the relation in words. Done. |
| KEEL | The audit is generated from a deterministic builder. | P3 | Builder and JSON | Keep equality and semantic assertions in `check_motion_almanac.py`. Done. |
| KEEL | Release and preview hashes change when the audit or methods change. | P3 | Package manifests | Regenerate and run release, preview, and site checks. Done. |
| KEEL | No map geometry is generated from an approximate point. | P2 | Spatial outputs | Require a separate reviewed point-to-state method before adding a state locator. Open. |
| LOGBOOK | Source-scoped observations must not silently merge with Horizon register entities. | P2 | Inventory | Keep the main 310-entity inventory unchanged pending an explicit attribution model. Done. |
| LOGBOOK | The 2019 name/date conflict remains unresolved. | P2 | Audit assessment | Keep its identity join status unresolved. Done. |
| LOGBOOK | The full candidate and screened site remain unpublished review artifacts. | P2 | Release boundary | Retain the existing rights, scientific, accessibility, and owner gates. Open. |

Roles reviewed: 5. P1 blockers: 0; P2 issues: 12; P3 notes: 3.
Verdict: **APPROVED-WITH-CONDITIONS** for the dated evidence audit. The audit
does not approve a new eddy identity, state containment claim, or publication.
Top finding: independent measurements do not make the Horizon-derived names
independent identities. CURRENT, SOUNDER, and LOGBOOK agree that event stage and
name provenance must remain explicit.

Amendments: (1) Store the 2012 dated positions and source attribution in the
audit; done. (2) Preserve null geometry for Darwin and no state containment
edge for either observation; done. (3) Design a source-attributed observation
record and reviewed point-to-state relation before promoting these observations
into the public inventory; open.

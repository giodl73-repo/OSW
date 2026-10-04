---
skill: roles-check
topic: red-sea-redsox-branch-reach
date: 2026-10-04
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 3
verdict: APPROVED-WITH-CONDITIONS
---
# Red Sea REDSOX source reach and branch review

Artifacts: source-scope audit, validator, width decision, dashboard fingerprint,
atlas card, tests and documentation. Seven installed role lenses apply to the
science, provenance, cartography, explanation, accessibility, reproducibility
and repository record. ORBIT is inapplicable. This is internal editorial review,
not independent scientific measurement or identity admission.

| Role | Finding | Severity | Artifact | Resolution / condition |
| --- | --- | --- | --- | --- |
| CURRENT | Plume thickness must not become fixed depth bounds | P2 | Reach extraction | Addressed: 100–250 m is layer thickness; fixed depth bounds stay null and mutation is rejected. |
| CURRENT | Channel width does not establish paired current edges | P2 | Width decision | Addressed: 5 km stays geographic context; no numeric current width admitted. |
| CURRENT | Descending plume branches differ from downstream equilibrated water | P3 | Component hierarchy | Northern and southern main plume roles separated from winter gully product; no continuous undercurrent inferred. |
| SOUNDER | Different channel length conventions are not uncertainty bounds | P2 | Channel context | Addressed: 115/120/130 km preserve distinct source locators; no interval formed. |
| SOUNDER | Cruise context does not identify exact reach occupations | P3 | Dates | Peters campaign context retained with exact-period flag false; Bower start-date difference explicit. |
| SOUNDER | A source inspection is not raw-data acquisition | P3 | Provenance | URLs, DOI, inspected sections and access date documented; no raw-array or source-geometry checksum claimed. |
| CHART | A numeric reach without vertices cannot justify a map line | P3 | Atlas preview | Geometry remains null; browser checks no route-map is borrowed. Compatible axes remain a gate. |
| CHART | Existing regional name locator has limited geographic meaning | P3 | Main atlas | Locator retained as name geography; reach text explicitly excludes reconstructed axis. |
| CHART | Branch taxonomy should not visually imply simultaneous footprints | P3 | Branch list | Components shown as text with local identity status; no branch polygons or seasonal interpolation. |
| BEACON | Readers need the source metric next to 130 km | P3 | Reach heading | Winter, speed threshold, thickness and sampled-reach scope appear together. |
| BEACON | Branch names can appear official without identity status | P3 | Branch list | Each names its source role and pending canonical identity. |
| BEACON | Channel facts remain useful if scope is clear | P3 | Context disclosure | Collapsible channel section preserves individual source descriptions and current-width limitation. |
| HARBOR | Scope cannot depend on marker colors | P3 | Card | Reach, branch status and channel distinctions expressed in text and semantic list. |
| HARBOR | Source context needs keyboard access | P3 | Disclosure | Native details/summary and source links retained; no hover-only evidence. |
| HARBOR | Narrow cards must retain dimensions and conditions | P3 | Reflow | 320 px browser check passes without document overflow; screenshot inspected. |
| KEEL | Unsupported dimension promotion needs executable guards | P3 | Validator/tests | Tests reject whole-current dimensions, annual range, fixed depth, rank, geometry and playback promotion. |
| KEEL | Branch hierarchy must reject cycles and premature admission | P3 | Validator/tests | Cycle and canonical-identity mutations rejected; source components remain local. |
| KEEL | Evidence edits must reach the dashboard fingerprint | P3 | Builder/tests | Scope audit is included; Red Sea tests retain zero route/width/ranked-length capability. |
| LOGBOOK | Counts must reflect reviewed but nonnumeric width | P3 | Coverage docs | Current counts 25 records/16 names/78 unassessed/5 reviewed nonnumeric/1 derived pending documented. |
| LOGBOOK | Internal review must not be labeled science approval | P3 | Audit/review | Editorial status preserved; independent branch and measurement admission remain open. |
| LOGBOOK | Focused validation cannot establish release readiness | P3 | Operational status | Tests named explicitly; no clean-checkout full-suite, commit, publication or release-completion claim. |

## Synthesis

Roles reviewed: 7. P1 blockers: 0. P2 issues: 3, all addressed. P3 notes: 18.
Verdict: APPROVED-WITH-CONDITIONS for the local editorial scope product.
Top finding: source-reported reach, plume thickness and channel geography need
separate metrics. CURRENT, SOUNDER and CHART agree that these facts cannot be
promoted into a full-current axis, velocity width or annual envelope.

## Three amendments

1. Preserve thickness separately from depth bounds and retain scalar plume-speed
   semantics in the audit, card and validator; mutation tests enforce both.
2. Keep each channel convention in its own source context and exclude the 5 km
   channel description from numeric current-width admission; record the reviewed
   nonnumeric width decision in the inventory and coverage documents.
3. Keep three branch/product components local and geometrically unresolved;
   validate their hierarchy, expose identity status in the card and require
   compatible axes, paired current edges and independent admission before promotion.

## Verification and remaining gates

Passed: 3 Red Sea source-scope tests, 18 width-inventory tests, 16 dashboard tests,
and browser checks for all 35 source-scope identities including Red Sea reload,
three components, channel disclosure, absent route geometry and narrow reflow.
Card screenshot inspected. Canonical ledger SHA256 remains
`6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e`.

Open: source convention reconciliation, exact occupation support, compatible
current axes and paired velocity edges, independent component/measurement
admission, and any annual dimension evidence. No full repository suite or
clean-checkout publication gate was run for this change.

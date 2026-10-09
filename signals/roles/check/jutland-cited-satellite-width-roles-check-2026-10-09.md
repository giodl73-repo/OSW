---
skill: roles-check
topic: jutland-cited-satellite-width
date: 2026-10-09
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Internal seven-role review

Artifact: Nielsen source inspection, three cited site descriptions, later-source
reconciliation, protocols, source/query data, Python and Rust/WASM guards,
atlas/inspector display and verified navigation-test correction. Seven installed
role lenses apply; ORBIT has no new analogy to review. One agent performs these
lenses; this is not an independent scientific panel.

## CURRENT — mechanism and support

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Satellite-image width cannot be claimed as velocity-core width. | P2 | Protocol 1–3 | Image-estimate operator explicit; threshold and paired velocity boundaries unknown. |
| 2 | Mostly mixed water and 30 m bathymetry do not define image depth. | P2 | Protocol 4 | Fixed layer bounds remain null; depth promotions rejected. |
| 3 | Midsummer German Bight fractions do not date numeric image widths. | P2 | Protocol 5 | Qualitative context preserved; no calendar, numeric series or playback. |

## SOUNDER — source stewardship

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Thesis/reprint years can be treated as observation dates. | P2 | Preface / record | 1999/2000 publication lineage retained separately from unknown occupations. |
| 2 | Aarup's two report series can be silently conflated. | P2 | PDF p140 | Danish series 42 citation distinct from English series 52; both originals unreviewed. |
| 3 | The later 10–20 km citation chain was previously uninspected. | P2 | Existing DHI card | Original now inspected; bibliography linked but exact numeric corroboration not claimed; source comparison pinned. |

## CHART — visual evidence

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Three locations can look like an annual 20–40 km range. | P2 | Four cards | Each site displayed separately; no pooled bounds or midpoint. |
| 2 | Named towns are not geographic current edges. | P2 | Geometry | No transects, edge polygons or route-width buffer inferred. |
| 3 | 20/25 km labels can collide on compact cards. | P2 | Shared renderer | Existing outward close-label alignment retained; narrow-screen label separation checked. |

## BEACON — public explanation

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Inspected thesis can sound like inspected satellite imagery. | P2 | Source quality | Explicit Aarup imagery/methods unknown note beside each chart. |
| 2 | Danish translation can be mistaken for independent observation. | P2 | Audit context | Editorial translation label and original-language citation; no new observation claim. |
| 3 | Conflicting source scope can be concealed by selecting a preferred width. | P2 | DHI reconciliation | Both source operators visible; no preferred value or numerical corroboration asserted. |

## HARBOR — equivalent access

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Site identity and limitations need textual access. | P2 | SVG / caption | Scoped aria description and visible caption retain site, quantity, unknown dates and methods. |
| 2 | Source inspection must work without map pointer interaction. | P2 | Source links | Semantic links target each exact audit array pointer; native/WASM source results compared. |
| 3 | Four records must remain readable at mobile width. | P2 | Browser | 320 px reflow, rendered font size and card content checked; screenshot reviewed. |

## KEEL — reproducibility

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Owner-first source lookup fails when one owner has two audits. | P2 | Rust registry | Source selected by known record ID; wrong owner/context/audit rejected. |
| 2 | Self-consistent receipt changes can promote or replace source support. | P2 | Mutation tests | Coherent phase/range/depth edits, same-owner source substitution and deleted-context alias tested in native/WASM. |
| 3 | Remote seasonal navigation assertion predates West Australian breadth data. | P2 | Verified CI failure | Exact owned phase/current/option assertions replace obsolete no-phase expectation; no playback or integrity gates weakened. |

## LOGBOOK — repository record

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | More descriptions do not close the 34 unassessed owners. | P2 | Batch | Coverage reported as 109/58/34; full objective remains incomplete. |
| 2 | Whole report review or original-image license could be implied. | P2 | Receipt / batch | Selected page list explicit; original remains ignored; no redistribution license established. |
| 3 | Source outage and browser assertion failure are different states. | P2 | Parent CI audit | Exact run IDs and failure gates distinguished; independent science and mainline publication remain pending. |

## Synthesis and amendments

Roles reviewed: 7. P1 blockers: 0. P2 issues: 21 addressed in source bounds,
reconciliation, identity binding, display and executable checks. Verdict:
APPROVED-WITH-CONDITIONS for editorial publication after validation. Scientific
admission still requires original Aarup methods and comparable dated sections.

Top finding: preserve site and measurement operator through the complete record.
CURRENT, SOUNDER, CHART and BEACON agree on that restriction.

Three amendments:

1. Keep three satellite estimates and the water-mass band separate and reconcile
   the inspected citation chain without assigning a preferred value.
2. Bind multiple source audits through record identity rather than owner alone.
3. Correct the obsolete browser expectation to verify the current's own phase
   while retaining disabled playback and unrelated-phase rejection.

## Executed validation

Full suite: 1,076 tests and 918 subtests passed (463.51 seconds). Rust: 41 tests
passed; native/WASM builds succeeded. New satellite and existing DHI browsers
passed source/query parity, mobile cards and coherent integrity rejection.
Seasonal navigation passed 100 current links, 64 route-card links, 117 phase
links and six round trips, including the owned-phase correction. Original
download checksum, dependency invariants, 48 module syntax checks and 14 page
assignments passed. Four-card mobile screenshot visually inspected.

The editorial validation condition is satisfied. Original Aarup methods,
scientific admission and mainline publication remain pending; these seven
internal role lenses are not independent scientific reviewers.

---
skill: roles-check
topic: brazil-initial-reach
date: 2026-10-23
roles_used: 7
p1_count: 0
p2_count: 2
verdict: APPROVED-WITH-CONDITIONS
---

# Brazil initial reach: internal source-stage review

Artifact: frozen v2 report/SVG, original-reviewed source facts, prospective
method/tests/preflight and independent actual-product checks. This review uses
installed functional lenses; it is not external scientific peer review.
The verdict permits source-stage draft delivery on PR83. Canonical atlas
delivery is unfinished and must satisfy the two P2 conditions below.

Select CURRENT for physical quantity/support, SOUNDER for original custody,
CHART for diagram meaning, BEACON for public wording, HARBOR for equivalent
access, KEEL for frozen replay and LOGBOOK for release/gap status. ORBIT is
irrelevant: no planetary comparison is introduced.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| C1 | The1500 km value describes the initial strengthening reach, not the whole Brazil Current. | P3 | Original p244 and report constraint | Keep the separate regional quantity, null whole-current length and false ranking flag. |
| C2 | Near10 degrees south is approximate context; no longitude or downstream coordinates define this reach. | P3 | Source facts and constraint | Preserve nulls; do not derive endpoints from distance or the next page's separation latitudes. |
| C3 | Transport/depth descriptions and adjacent dated front illustrations do not establish a common layer or observation window for the reach. | P3 | Original pp244–245 | Keep layer and epoch explicitly unspecified; add no seasonal envelope or physical bound. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| S1 | Exact original size, SHA256 and401-page count agree with the existing acquisition receipt; selected source assertions are checked independently. | P3 | Custody and admission checks | Preserve that original pin; do not replace it with a different book rendition. |
| S2 | This chapter's September2002 revision differs from1994 print publication and the2005 directory label. | P3 | Source version fields | Keep all three roles explicit and never use any as observation dates. |
| S3 | Source uncertainty and a page-by-page completeness audit are absent. No redistribution grant for the full book is asserted. | P3 | Report source and schematic | Retain unknowns, selected-review scope and the ignored-original boundary. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| T1 | The line is explicitly a schematic segment without coordinates, scale axis, coastline or geographic projection. | P3 | Saved SVG | Preserve its non-geographic explanation when embedding it in the atlas. |
| T2 | The source's round number is retained without an added approximation sign, equality claim or uncertainty band. | P3 | Value and caption | Keep the semantic relation beside the value in query rows too. |
| T3 | The actual saved SVG was rasterized and inspected; native-size text and labels fit without observed collisions. | P3 | Visual QA | Keep this evidence distinct from the unrun responsive browser gate. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| B1 | The heading says initial reach and the visible text distinguishes source dates from observation support. | P3 | Diagram and report | Retain both qualifications in shortened public labels. |
| B2 | Unknown physical dimensions refer to the scope of this source statement; independent section-width evidence may exist elsewhere. | P3 | Future host UI | Say explicitly that this source supplies no full-current dimensions and retain the separate section-width links. |
| B3 | The source is a textbook synthesis, not a new OSW measurement or observation campaign. | P3 | Source class and derivation | Preserve that evidence class and the statement that no distance calculation was performed. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| H1 | SVG title, description and visible text carry the number and essential limitations without color dependence. | P3 | Saved SVG | Preserve these alternatives and the report's equivalent structured values. |
| H2 | No rebuilt query/card host or narrow-screen keyboard access has been verified for this new product. Shrinking a1000px SVG alone is insufficient. | P2 | Pending canonical delivery | Supply readable host text and keyboard access; run the single batched mobile/browser gate before claiming atlas delivery. |
| H3 | This is static evidence with no observation time series or animation. | P3 | Product scope | Do not attach seasonal playback or motion implying unobserved evolution. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| K1 | Commit fee4925 froze source, method, tests, protocol and preflight before actual execution; first build and read-only replay matched exactly. | P3 | Freeze and execution | Preserve all executed inputs/products; use a new version for corrections. |
| K2 | All35 focused checks passed, including independent original/value and saved-product verification. Checks ran at one CPU with BelowNormal priority. | P3 | Focused suite | Keep the documented commands; avoid repeating full regression for each source. |
| K3 | The existing40-target Linux replay result does not cover this new original-dependent report. Only its synthetic suite is added to conformance now. | P2 | Pending reproduction coverage | Add explicit actual-original/report reproduction coverage for the compatible batch; record unavailable sources as failures or missing evidence, never silent passes. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| L1 | Source-stage products exist, while canonical query/card/native/WASM admission is still pending. | P3 | Batch plan | Keep the internal draft verdict and pending gates visible; do not call this a shipped atlas update. |
| L2 | No new full-current length, width, route, season, state join or ranked value is admitted by these files. | P3 | Report flags and unchanged canonical data | Keep the measurement gap open and batch integration on PR83. |
| L3 | Full regression and broader program gaps remain unresolved; local disk headroom constrains builds. | P3 | Resource policy and batch status | Keep one heavy job and the disk preflight; no main merge or overall completion claim. |

## Synthesis and amendments

Roles reviewed:7. P1 blockers:0; P2 pending delivery issues:2; P3 notes:19.
Verdict: **APPROVED-WITH-CONDITIONS for source-stage draft delivery**.
Canonical atlas delivery remains unfinished. CURRENT, SOUNDER and BEACON agree
that1500 km must never become an exact whole-current measurement or a dated
seasonal sample. HARBOR and KEEL require evidence from the actual delivery
surface and source-original reproduction path before that scope is claimed.

1. Add the separate regional record/provenance and readable host explanation
   during batched query/card integration; preserve independent width evidence.
2. Extend actual-source reproduction coverage without representing a missing
   ignored original or an unrun Linux replay as a passing check.
3. Run one serialized native/WASM/browser validation cycle for the compatible
   batch after the disk preflight; retain full regression as the final gate.

---
skill: roles-check
topic: south-australian-2d-source
date: 2026-10-20
source_commit: 2a3717bf91b4aca30f5d77b9f561ccf7cd64604e
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Internal source and model-context review

Scope: source intake, exact overlap, declared monthly context operator,
machine-readable outcomes and two static scientific figures. These are
repository functional lenses, not external scientific peer review. ORBIT is
excluded because no planetary comparison is made. Approval covers source
artifact delivery into the existing draft PR, not current identity, physical
width admission, complete atlas/UI integration, or merge/release readiness.

## CURRENT — physical interpretation

| # | Finding | Severity | Evidence and disposition |
|---|---|---|---|
| 1 | Positive u and connected cells do not identify a named current. | P2 | Both protocols, report and figures retain identity/width admission false. Implemented. |
| 2 | Seed obliquity varies; a one-point direction cannot correct a section width. | P2 | All twelve angles retained; no cosine correction, rotation or replacement peaks. Implemented. |
| 3 | Monthly means and box contacts do not prove material continuity or annual extrema. | P2 | All 36 cases, sides, failures and explicit scope flags retained. Implemented. |

## SOUNDER — custody and exact source

| # | Finding | Severity | Evidence and disposition |
|---|---|---|---|
| 1 | The original deferred write lost a rejected response. | P2 | Complete responses now staged before validation; failure-custody test passes. Second response retained and reused. Fixed. |
| 2 | Assumed coordinate spacing rejected valid native coordinates. | P2 | Original values retained; separate coordinate request matches exactly; amendments and batch correction record actual spacing and earlier inference. Fixed without shifting indices. |
| 3 | A changed corpus must not pass by resealing its receipt. | P2 | Context generator freezes acquisition SHA, which binds all four raw responses, NPZ and quality; rejection test passes. All 55,632 original scalar values agree exactly. Fixed. |

## CHART — source maps

| # | Finding | Severity | Evidence and disposition |
|---|---|---|---|
| 1 | Missing source cells can look like an inferred coastline. | P2 | Gray/unsupported legend, captions and SVG descriptions deny coastline inference; no shoreline drawn. Implemented. |
| 2 | Arrow direction and aspect must preserve east/north meaning. | P2 | Local longitude correction, aspect at 35°S, normalized direction-only glyphs every fourth cell, explicit projection/scale wording. Implemented. |
| 3 | Monthly figure legend overlapped explanatory text. | P2 | Reserved footer area, separated legend/text, regenerated and visually inspected final PNG. Fixed. Source panel also inspected. |

## BEACON — public claims

| # | Finding | Severity | Evidence and disposition |
|---|---|---|---|
| 1 | Source acquisition can be mistaken for another completed width. | P2 | Batch status and all admission flags state otherwise. Existing twelve section estimates unchanged. Implemented. |
| 2 | Readers need dates, depth and model identity near the figures. | P2 | Exact source-day dates, 2012 monthly panels, 100 m, GOFS 3.0 HYCOM+NCODA titles/captions. Implemented. |
| 3 | Native spacing diagnosis must not assert undocumented provider internals. | P2 | Batch correction reports observed values and supersedes earlier endpoint inference; no implementation attribution. Implemented. |

## HARBOR — equivalent meaning

| # | Finding | Severity | Evidence and disposition |
|---|---|---|---|
| 1 | SVG figures need semantic names and descriptions. | P2 | Both have role=img and linked title/description IDs; focused tests verify them. Implemented. |
| 2 | Color must not be the only source for numerical interpretation. | P2 | Exact grid membership, support, angles, thresholds and sides are machine-readable; textual claims and explicit legends accompany maps. Implemented for source artifacts. |
| 3 | Large scientific sheets do not replace responsive current-card interaction. | P2 | Source sheets remain zoomable standalone artifacts. Batch explicitly leaves accessible card/WASM integration required; no UI-completion claim. Condition retained. |

## KEEL — reproducibility

| # | Finding | Severity | Evidence and disposition |
|---|---|---|---|
| 1 | Default tests must remain offline. | P2 | Acquisition explicit; tests use retained originals and mocked failure transport. 26 tests/5 subtests pass. Implemented. |
| 2 | Adjacency and pairing must reject convenient gap bridging. | P2 | Tests cover diagonal separation, unsupported barriers, threshold ties, empty seed and marginal complete-pair support. Implemented. |
| 3 | A predecessor full pass cannot certify new source/UI work. | P2 | Clean 778c791 full pass is scoped to 1805 tests/1164 subtests. Successor full gate remains required; no native/WASM integration claimed here. Condition retained. |

## LOGBOOK — delivery status

| # | Finding | Severity | Evidence and disposition |
|---|---|---|---|
| 1 | Per-gap PRs impose an unwanted workflow. | P3 | Continue existing branch and draft PR83. No merge or new PR. Implemented. |
| 2 | Published originals need redistribution support. | P3 | Retained provider DAS explicitly says public release/distribution unlimited. Duran PDF remains ignored. Implemented. |
| 3 | Navigation and physical interpretation remain unfinished. | P3 | Batch names current-card/query integration and independent geographic/dynamical review as next work. Goal remains active. |

## Synthesis and amendments

Seven roles; 21 findings: 0 P1, 18 P2, 3 P3. Source artifacts may enter the
existing draft PR. Broader UI/full-suite and scientific-admission conditions
remain explicit. CURRENT and CHART agree that highlighted cells must not be
described as a physical footprint.

Three amendments completed: retain failed originals before validation; verify
native coordinates using a separate response and preserve correction history;
repair footer overlap and add described, pinned SVG output. Next required work
is actual current-card/Rust/WASM integration and its verification, followed by
further named-flow interpretation. No external scientific endorsement claimed.

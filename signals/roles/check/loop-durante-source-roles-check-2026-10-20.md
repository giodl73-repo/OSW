---
skill: roles-check
topic: loop-durante-source
date: 2026-10-20
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Loop Current processed-source integration review

Baseline: 5633d093585901fb83d9b5498b2b628f0043a7aa; reviewed working batch
described in `plans/loop-durante-2026-source-gap-batch-2026-10-20.md`.
Internal repository lenses; this is not independent scientific peer review.
Artifact: source acquisition, derived source visualization, checked index and
Rust/WASM diagnostic integration. These seven roles intersect the work. ORBIT
is excluded because there is no planetary comparison or atlas release here.

## Findings

P2 findings below are corrected in this batch. P3 entries record retained
limitations or verified safeguards. No unresolved P1/P2 authorizes a main merge.

| Role | Finding | Severity | Evidence and disposition |
|---|---|---|---|
| CURRENT | Coordinate means do not span the Loop's complete path. | P2 | Both 248-point arrays end south of 23.15N. Full-route admission remains false; points are unjoined and no route length is inferred. |
| CURRENT | Phase composites cannot be assigned daily dates or seasons. | P2 | Source view and scene explicitly label conditional surface composites; all three clocks are retained separately without dating the composites. |
| CURRENT | Enclosed-area scalars cannot establish width or route length. | P3 | Original area_loop/AMR_loop values remain unscaled with unit evidence and unknown enclosure definition; no dimension is admitted. |
| SOUNDER | Record/CITATION versions and README license notes disagree. | P2 | API version0 and CC BY4.0 are retained with README TODO, CITATION1.0.0 and placeholder manuscript DOI; no verified publication claim. |
| SOUNDER | Concurrent clocks differ at one source entry. | P2 | Missing tisp time stays missing at zero-based position3462/MATLAB3463; source selection indices remain one-based. Clock blocks preserve gaps. |
| SOUNDER | Source support and storage association must survive export. | P3 | Raw MAT, original dictionary/metadata/code archives and pinned inventories retained; 25 numeric fields retain masks, semantic shape and numeric-bit checks. |
| CHART | Missing grid cells could be mistaken for coastline. | P2 | Gray is explicitly labeled missing source speed, not coastline; full source grid is rendered. |
| CHART | Vector glyphs could imply another speed estimate. | P3 | Fixed-stride arrows are normalized direction only; common color scale represents original C fields, separately from mean U/V. |
| CHART | Dense points visually resemble a continuous path. | P3 | Each array uses point markers, no connecting segment; title and caption state incomplete coordinate means and no inferred length. |
| BEACON | Source recovery could be reported as a closed measurement gap. | P2 | Batch notes and scene identify source coverage and retain the missing full Loop route/physical-width status. |
| BEACON | An index number is ambiguous without its basis. | P2 | UI notes, figure description and JSON now distinguish zero-based3462 from MATLAB3463. |
| BEACON | Existing captions suffered a refresh-helper encoding regression. | P2 | Helper now reads UTF-8 explicitly; corrupted source literals repaired. Preservation assertion remains exact and must pass before commit. |
| HARBOR | Figure meaning must be available outside its palette. | P3 | SVG title/description plus shared facts, notes, clocks table and coordinate-support table provide textual meaning and limits. |
| HARBOR | Scientific plate is too dense to read at phone thumbnail size. | P3 | Existing explicit full-size figure link is retained; actual 320px keyboard/browser check is required. No hover-only access. |
| HARBOR | Conditional configurations could imply playback through time. | P3 | This static source sheet has no fabricated seasonal playback; shared pages preserve the source evidence class. |
| KEEL | Derived data must reject silent source replacement. | P3 | Offline operator verifies exact source bytes, inventories, protocol/generator pins, dimensions, clock gaps and array hashes. Resume does not overwrite changed originals. |
| KEEL | Native/WASM acceptance must include source ownership and mutations. | P3 | Browser checks exercise all three shipped views, complete native/WASM source rows, six packet corruptions and one index corruption. |
| KEEL | Prior clean full pass predates this integration. | P3 | ce3cb2c passed1826tests/1164subtests; combined successor gate is required. Draft publication does not imply latest full-suite success. |
| LOGBOOK | Scope must stay on the existing user-authorized PR. | P3 | Same branch codex/current-measurement-gaps and draftPR83; no new PR and no main merge. |
| LOGBOOK | Remote CI acquisition failures are not passing tests. | P3 | Earlier provider403/timeout runs are reported separately from local offline passes; no authentication or source-integrity bypass. |
| LOGBOOK | Azores preflight is not an executed extraction. | P3 | Separate method preflight records unexecuted calibration; no width or failed-attempt rows fabricated. |

## Synthesis

Roles reviewed: 7. Open P1: 0. Open P2: 0. P3 notes: 13.
Eight P2 findings corrected as described above.

Verdict: **APPROVED-WITH-CONDITIONS** for the same draft PR.
Top finding: the supplied coordinate means must not become a full Loop length.
CURRENT, SOUNDER and BEACON agree that source identity and physical scope govern
what may be measured; CHART and HARBOR require those limits beside the picture.

## Amendments and publication conditions

1. Retain the full-path/width rejection and distinguish composite fields,
   coordinate means, source clocks and area scalars in every consumer.
2. Require repaired-caption preservation, final shipped-browser checks and
   staged source-pin verification before committing this batch.
3. Start a clean combined full gate at the committed batch; keep PR83 draft and
   report its actual terminal or running state without borrowing an older pass.

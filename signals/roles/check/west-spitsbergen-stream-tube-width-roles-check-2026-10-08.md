---
skill: roles-check
topic: west-spitsbergen-stream-tube-width
date: 2026-10-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# West Spitsbergen stream-tube width review

Internal data/code/presentation review against working base 817683a. Seven
roles cover oceanographic meaning, evidence, cartography, explanation,
accessibility, reproducibility and release records. No planetary comparison
is present, so ORBIT is excluded. This is not independent scientific review.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Tube 1 and tube 2 represent different boundary definitions. | P2 | Values/metric | Addressed: distinct records, no average or sum; retain property-defined layer. |
| 2 | Observed AW depths and reference pressure do not define width at fixed depth. | P2 | Context | Addressed: null layer bounds and explicit exclusions bound by Python/Rust. |
| 3 | Cruise timing does not give exact individual section occupations. | P2 | Time | Addressed: separate cruise context and false seasonal/annual eligibility. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Table brackets associate two widths with two thresholds. | P2 | Sensitivity cases | Addressed: preserve 0.02/0.08 m/s mapping; no probability or annual range. |
| 2 | A1 and A2 share a single source tube. | P2 | Observation independence | Addressed: shared observation group and visible legend; six cells are not six surveys. |
| 3 | Original evidence needs an offline rights and byte receipt. | P2 | Acquisition | Addressed: original PDF and CC BY 4.0 attribution, checksum and byte count retained. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Sensitivity whiskers could be mistaken for error bars. | P2 | Legend/SVG | Addressed: dashed threshold segments, nominal marks, explicit non-confidence caption. |
| 2 | Along-section widths do not establish a flow-normal map buffer. | P2 | Atlas | Addressed: no derived geographic edges, route buffer or state intersection. |
| 3 | A measured section map would aid geographic orientation. | P3 | Next work | Recover source-supported station/edge coordinates before adding such a map. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | AW and transport constraint need visible explanations. | P2 | Chart prose | Addressed: Atlantic Water definition and 1.3 Sv constraint; 10% is not width error. |
| 2 | The 21/61 km B comparison could look like temporal change. | P2 | Labels/caption | Addressed: section/tube labels and August snapshot context, no temporal line. |
| 3 | Naming similarities could lead to duplicate coverage claims. | P2 | Identity/status | Addressed: assign west-spitsbergen only; leave spitsbergen-atlantic unresolved. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Color alone cannot encode the two methods. | P2 | Chart | Addressed: circles/squares, labels, SVG description and full textual table. |
| 2 | Values must remain usable at 320 px. | P2 | Reflow | Addressed: responsive SVG, larger text and wrapping table; final browser passes at 320 px. |
| 3 | Readers need a direct path to complete records. | P3 | Query/navigation | Preserve semantic query link and per-record evidence links. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Rewritten hashes could preserve a scientifically false row. | P2 | Loaders | Addressed: exact compiled audit binding and coherent-rewrite rejection tests. |
| 2 | Changing width inventory invalidates seasonal-frame receipt. | P2 | Generation | Addressed: refresh receipt while preserving frame contents and old rows. |
| 3 | New metric must have automated negative scope checks. | P2 | Tests | Addressed: 84 Python mutation subtests and Rust semantic tests; full suite passes 829 tests and 913 subtests. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Scoped width counts are not full annual coverage. | P2 | Batch status | Addressed: 85 records/41 owners/52 unassessed with remaining scientific gaps explicit. |
| 2 | Draft/local completion cannot establish mainline publication. | P2 | Git/status | Addressed: record actual parent draft and PR30's running main gate separately. |
| 3 | Source limitations must travel with retained originals. | P3 | Plan/protocol | Preserve exact dates/edges unknowns, licenses and extraction scope with the batch. |

## Synthesis and amendments

Roles reviewed: 7. P1 blockers: 0. P2 findings: 18, corrected in working
artifacts and verified by final checks. P3 notes: 3. Verdict:
APPROVED-WITH-CONDITIONS. Full suite (829 tests, 913 subtests), 40 Rust
tests, mobile reflow, native/WASM query parity and atlas/source-index browser
checks pass. Scientific admission and protected-main publication remain
separate pending gates.

Top finding: source bracket cases are boundary-choice sensitivity, not annual
variation or confidence bounds. CURRENT, SOUNDER, CHART and BEACON agree.

1. Store each threshold and transport definition separately, including A's
   shared source tube and section-specific C/B exceptions.
2. Bind full records to the inspected original and source-specific protocol;
   reject dates, layers, dimensions and identity promotions.
3. Render responsive charts with textual threshold values and a direct Rust
   query link; verify the atlas and evidence paths before publication.

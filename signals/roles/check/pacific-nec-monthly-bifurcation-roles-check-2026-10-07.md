---
skill: roles-check
topic: pacific-nec-monthly-bifurcation
date: 2026-10-07
roles_used: [CURRENT, SOUNDER, CHART, KEEL, LOGBOOK]
p1_count: 0
p2_count: 4
p2_remaining: 1
implementation_p2_remaining: 0
p3_count: 11
verdict: APPROVED-WITH-CONDITIONS
---

# Pacific NEC monthly branching extraction review

Artifact: source PDF acquisition/configuration, extraction protocol, generator, derived data, source registration and validation. Five relevant installed roles are applied. No new visual controls are added, so BEACON/HARBOR do not require another UI design review; ORBIT is outside this terrestrial source scope. CHART checks the source figure calibration and encoding. This internal review is not independent scientific peer review.

## CURRENT

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | A source-labelled deviation band must not become annual extrema or confidence bounds. | P2 resolved | Band kind is explicit; annual-extrema/confidence eligibility is false. | Retain the source label and missing statistical conventions. |
| 2 | The source caption does not identify the denominator, multiplier or averaging weights. | P3 | These fields remain null or unextracted. | Do not infer a confidence probability or statistical convention from symmetry. |
| 3 | The observations describe a regional surface geostrophic branching latitude. | P3 | Degree units, historical period and null current dimensions/geometry. | Apply E01-E05 and M01-M13 before any route admission. |

## SOUNDER

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | The author PDF and acquisition route are identified by exact checksum. | P3 | Fresh CI-header retrieval matched 3,012,493 bytes and the pinned SHA-256. | Keep explicit acquisition outside offline tests. |
| 2 | Independently rounded band endpoints need their own reading allowances. | P2 resolved | Raw mean/boundary values and PDF coordinates are retained; all three displayed values have separate intervals. | Do not reconstruct rounded bands from a rounded mean/deviation. |
| 3 | The series preserves October 1992-December 2009 and leaves individual observation years/counts unextracted. | P3 | Source-period metadata and false extraction flags. | Do not infer two observed years from repeated plotting. |

## CHART

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | The mean and filled band have uniquely verified vector topology. | P3 | One 23-segment mean and one 47-segment filled polygon; crosses/outlines/upper panel excluded. | Keep exact shape, color, width and rectangle constraints. |
| 2 | Month assignment is tied to half-bin centers rather than incidental drawing order. | P3 | All 24 centers checked; two cycles agree in both means and boundaries. | Retain the month-shift and repetition gates. |
| 3 | The latitude scale is taken from the lower panel and preserves its north-positive orientation. | P3 | Rendered page 2528; y=251.992 at 18 N and y=413.188 at 8 N. | Reject reversed calibration and band/mean mismatches. |

## KEEL

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Extraction regenerates the complete pinned output and rejects seven invalid-source/configuration cases. | P3 | Two unittest cases, six mutation subtests plus stale-source rejection. | Keep the exact output equality and independent expected means/bounds. |
| 2 | The full offline suite and current engine validation passed. | P3 | 773 tests, 598 subtests, 37 Rust unit tests, three browser checks, 37 JS modules and 14 page assignments. | Required remote CI remains separate. |
| 3 | The new checked document remains queryable with original source pointers and exact values. | P3 | 68-source/native/WASM comparison and rendered twelve-month source query. | Keep original-byte/source-oracle assertions when adding sources. |

## LOGBOOK

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | The source PDF must stay outside the shipped assets. | P2 resolved | git check-ignore confirms the original is excluded; only acquisition/configuration and derived facts are staged. | Preserve the ignored-fixture boundary. |
| 2 | The Pacific identity remains an inventory proposal; admitted inventory/length/width counts are unchanged. | P3 | Null geometry and dimensions, false ranking, existing parent/source audit. | Do not describe this as canonical admission or a whole-current measurement. |
| 3 | This candidate is local and depends on PRs #26-29. | P2 publication condition | Feature branch on 3d30ee1; no source publication claim. | Publish the reviewed candidate and pass the complete protected-main gate. |

## Synthesis and amendments

Five roles; zero P1 blockers; three addressed P2 implementation findings, one open P2 publication condition and eleven P3 notes. CURRENT and SOUNDER agree that the source band and graph-reading allowances must remain separate. KEEL and LOGBOOK agree that local validation does not establish publication.

1. Keep the source-labelled standard-deviation band distinct from reading allowances, confidence intervals and annual extrema.
2. Preserve exact vertices, checksum-pinned acquisition, month calibration and missing statistical conventions.
3. Publish the reviewed candidate through required CI, retaining its dependency chain and scientific-review-pending status.

## Verification

The source page and figure caption were visually inspected. The current author URL with the CI acquisition header returned bytes matching the pinned PDF. The extraction unit checks passed, including all seven rejection cases. The full offline suite passed 773 tests and 598 subtests. All 37 Rust tests and native/WASM builds passed. Browser checks passed exact original bytes for 68 sources, native/WASM equality, the twelve Pacific rows and original source pointers, the existing index across all twelve dated NOAA inventories and 100 currents, and source workspace sharing/mobile/error isolation. All 37 JavaScript modules, all 14 page assignments and whitespace checks passed; every engine manifest hash matches. No original PDF or frozen release data is included. Protected-main CI and scientific admission remain pending.

---
skill: roles-check
topic: indian-secc-hycom-results
date: 2026-10-22
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Internal review: retained HYCOM source, candidate results and query maps

Seven installed project lenses, applied by the implementing agent. This is
not external scientific approval. Artifact: original-response package, paired
monthly fields, 144 candidate attempts, twelve maps, Rust source-index access
and current-card evidence navigation. ORBIT is unrelated to this data batch.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | A monthly daily-00Z sample mean differs from full three-hourly means, climatology and observations. | P2 | Source/figure | Resolved: estimator, provider 15m depth, model year and limitations remain visible. |
| 2 | Two five-station passes are the same May seed at two steps, not two independent currents. | P2 | Candidate counts | Resolved: report distinguishes two attempts, one both-step seed and zero stronger candidates. |
| 3 | Unresolved northern edges at the equatorial source limit cannot become a width or prove no crossing in the last unsampled interval. | P2 | May result | Resolved: retain failures, document discrete support, keep current identity/width/annual/state admissions closed. |

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Missing source timestamps invalidate a blind eight-index stride. | P2 | Acquisition | Resolved: exact calendar lookup, 363 daily00Z dates, August14/December25 explicitly absent; all82 checked requests retained. |
| 2 | Packed type and paired masks affect both vector direction and thresholds. | P2 | Means | Resolved: exact Float32 scale promoted to Float64, Int64 sums, common component mask, ceil80%-calendar-day eligibility; all6,851,625 valid paired positions accounted for. |
| 3 | Public fields must be retrievable and reproduce without the mutable provider. | P2 | Custody | Resolved locally: 22,715,226-byte original-response ZIP; exact NPZ, lossless JSON and quality reconstruction; full-precision JSON/NPZ agreement; fresh Linux gate added and pending. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | A source mask or threshold segment could look like a coast or named-current boundary. | P2 | Twelve maps | Resolved: no inferred coastline, explicit missing/inadequate mask, dashed candidates and dotted diagnostics. No admitted outline. |
| 2 | Clipped color values and vector units need explicit scale context. | P2 | Legend | Resolved: fixed +/-0.6m/s eastward component, negative=westward, vector key0.5m/s and monthly clipping counts. |
| 3 | Initial arrow key overlapped the title; phone figure margins reduced useful size. | P2 | Render QA | Fixed and visually checked: separate figure-coordinate key, wider phone image and selected-map full-size link. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | A finer product is not an experiment isolating source resolution. | P2 | Interpretation | Resolved: forcing, product, depth interpretation and temporal-support differences remain explicit. |
| 2 | Readers may infer a gap closed from new data volume. | P2 | Notice/status | Resolved: no new catalog width/length, annual extrema, state passage or named axis is claimed; existing170widths and13ranked lengths unchanged. |
| 3 | Failed attempts must be as accessible as a promising May case. | P2 | Results | Resolved: all144 cases,72 step comparisons, twelve monthly rows and complete native grids are queryable; zero stronger candidates stated. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Palette cannot be the only access to outcomes or model values. | P2 | Alternatives | Resolved: line styles, arrows, updated text, all-month table, full-grid source queries and downloads. |
| 2 | Month selection needs complete keyboard operation and context. | P2 | Controls | Resolved in actual Chrome: native labeled select, live summary, image alternative, full-size selected link. |
| 3 | Source navigation needs narrow reflow and keyboard entry from a current card. | P2 | Main UI | Actual Chrome passes320px/card-to-map checks, all144 exact native/WASM cases and selected full-grid months. Final provenance-only refresh is rerun before publication. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Live data availability must not become a hidden default-test dependency. | P2 | Acquisition | Resolved: explicit bounded/resumable network action;16 focused tests pass with retained-source reconstruction network-forbidden. |
| 2 | Unsafe archives, map/source divergence and loss of numeric precision need executable guards. | P2 | Verification | Resolved: flat bounded checksummed members; typed maps/frame identity; exact JSON/NPZ bits, dates, masks, report rebuilds and map pins. |
| 3 | Narrow gates cannot establish the entire broad test matrix. | P2 | Release gates | Open broader scope: fresh Linux33-report/original-source gate pending;137-check browser matrix/full local suite unrun under existing4GiB guard. No overall green claim. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Another gap must not create another PR or a main merge. | P2 | Delivery | Resolved: continuing branch/draft PR83. |
| 2 | New evidence must preserve prior records and original source bytes. | P2 | Preservation | Verified: all450 prior source descriptors,32 prior report/producer pairs,170 widths,78 routes and every object geometry exact. Only IndianSECC evidence navigation changes. |
| 3 | Archive-member and velocity-response counts were conflated in CLI telemetry. | P2 | Package receipt | Fixed/tested:173 verified archive members versus82 velocity responses. ZIP, selection, quality, NPZ and full-grid JSON bytes remain unchanged. Provenance hashes refreshed afterward. |

## Synthesis

Seven roles,21 findings; no unresolved P1 for this scoped source/query/view
batch. Twenty findings resolved locally. One broader execution-gate finding
remains open, alongside the existing source-index memory/packaging risk.
Prior offline CI failure at the Rotschi primary PDF HTTP403 is independent.
Keep the PR draft and collect fresh Linux evidence. This review does not
authorize a physical current dimension, nor claim that the full gap-filling
goal is complete.

Priority amendments completed: exact calendar/paired typed decoding; separate
axis/edge/resolution/identity gates with all failures retained; accessible maps
and lossless native/WASM query access. The previous foundation review's three
local execution gates (source reconstruction, rendered QA and browser access)
have been exercised; broader gates retain their explicit scope and status.

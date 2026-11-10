---
skill: roles-check
topic: eacc-hycom-source-compilation-v1
date: 2026-10-24
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 10
p3_count: 11
verdict: APPROVED-WITH-CONDITIONS
---

# EACC receipt-bound source compilation review

Scope: prospective scientific compiler, synthetic tests, source-compilation
protocol and interface to the v2 diagnostic. Base source commit:`eb44ba6`;
reviewed worktree hashes are in
`research/eacc-hycom-source-compilation-preparation-review-v1.json`.
These are repository functional lenses, not independent scientific reviewers.
No original velocity acquisition, model-core case or public presentation is
claimed. ORBIT is excluded because no planetary comparison is involved.

## CURRENT — physical scope and support

| # | Finding | Severity | Evidence | Action |
|---|---|---|---|---|
| C1 | Paired daily model sample means are not observations, all-time monthly means or measured current dimensions. | P3 | Compiler interpretation and false/null admission fields. | Retain those qualifiers in future cards and tables. |
| C2 | Calendar-day support stays fixed when provider timestamps are absent; insufficient paired cells remain null. | P3 | Synthetic January27-day case retains25/24 paired-cell outcomes against a25-day threshold. | Preserve both counts and failure reasons through later queries. |
| C3 | Real EACC regional association and supported physical edges remain unverified. | P2 | No original model velocities or source-neighborhood maps inspected. | Review actual geography/normal profiles before named-current admission. |

## SOUNDER — response custody and transformations

| # | Finding | Severity | Evidence | Action |
|---|---|---|---|---|
| S1 | Selection is reproduced from exact metadata, and payload maps must match exact selected coordinates. | P3 | Changed selection/coordinates and complete synthetic-year tests. | Preserve input metadata and request candidates without toleranced substitution. |
| S2 | Receipt validation is implemented, but real HTTP custody has not been acquired or checked. | P2 | Synthetic receipts only; cloud runner/preflight still outstanding. | Bind actual start/end, source URL, status, bytes and selection in a guarded sequential cloud job. |
| S3 | Original-payload hashes and canonical receipt hashes have different, explicit meanings. | P3 | `response` versus `canonical_receipt`; canonical encoding documented. | Keep original payload bytes and do not imply arbitrary receipt-file whitespace was hashed. |

## CHART — geographic evidence

| # | Finding | Severity | Evidence | Action |
|---|---|---|---|---|
| T1 | A remapped source mask is not a land or current boundary. | P2 | Null vector support is retained; no sourced coastline is introduced. | Distinguish missing support from separately sourced land in the future maps. |
| T2 | Twelve actual regional maps and normal-profile views remain undelivered. | P2 | Compilation produces fields, not a geographic renderer. | Retain all months, source support, units/depth/date, projection and censoring in cloud figures. |
| T3 | Output coordinates and15m standard-depth identity remain explicit. | P3 | Selection/map equality and depth mutation checks. | Do not relabel this remapped output grid as the unmodified computational mesh. |

## BEACON — claim wording

| # | Finding | Severity | Evidence | Action |
|---|---|---|---|---|
| B1 | Width/length/range and rank/join claims remain unadmitted after successful compilation. | P3 | False/null output fields and evidence-class string. | Keep source preparation distinct from an admitted current measurement. |
| B2 | Source/diagnostic machine statuses still need short reader-facing explanations. | P2 | No new public status guide/page exists. | Explain source gaps, incomplete downloads and censored spans beside the eventual data views. |
| B3 | An absent provider time and a missing downloaded file are treated differently. | P3 | Complete inventory gate versus retained metadata time gaps. | Preserve that distinction in progress and coverage reporting. |

## HARBOR — equivalent access

| # | Finding | Severity | Evidence | Action |
|---|---|---|---|---|
| H1 | Scientific JSON alone is not equivalent accessible evidence for future maps. | P2 | No semantic EACC monthly/station/threshold tables delivered yet. | Add source/count/edge/reason tables and links without color or hover dependence. |
| H2 | Keyboard, mobile reflow and reduced-motion behavior of that future presentation remain unverified. | P2 | No browser run claimed in this preparation. | Verify them in the later saved-cloud presentation stage. |
| H3 | Nullable outputs retain unsupported information rather than displaying zero flow. | P3 | Compiler-to-diagnostic integration retains missing corners across all72 attempts. | Give nulls a textual explanation in the interface. |

## KEEL — reproducibility and bounded processing

| # | Finding | Severity | Evidence | Action |
|---|---|---|---|---|
| K1 |124 focused checks pass with synthetic velocities, oneCPU and no network/build/browser workload. | P3 | Source selection, compiler, v2 seed/diagnostic and integration checks. | Keep this focused proof separate from actual-source and full-regression claims. |
| K2 | The original-case source/dependency/environment preflight is not frozen. | P2 | Cloud acquisition remains disabled in phase and candidate selection. | Pin the complete imported helper graph, scientific producers/tests/protocols and environment before velocity acquisition. |
| K3 | Actual provider payload parsing and source reconstruction are still untested against an acquired original. | P2 | All parsed payloads in this review are synthetic. | Retain/reconstruct actual responses and record failures in the later cloud case without tuning executed methods. |

## LOGBOOK — execution state

| # | Finding | Severity | Evidence | Action |
|---|---|---|---|---|
| L1 | Source-review phase keeps heavy work disabled; source/data/WASM are not refreshed locally. | P3 | Phase JSON and no original velocity request. | Preserve sequential cloud stages and the older local preview qualification. |
| L2 | This preparation does not itself establish a remote source backup or installed packet delivery. | P2 | Review is bound to a local worktree; no packet admission is attempted. | Verify any source-only branch backup separately and preserve installed generated assets. |
| L3 | Earlier scientific inputs and reviews remain immutable; Rotschi1972 still blocks a full offline/release claim. | P3 | Hash checks recorded in the preparation review; separate gate stated in protocol. | Retain the historical artifacts and do not infer merge/release readiness from these tests. |

## Synthesis and amendments

Seven roles; zeroP1, tenP2 prerequisites and elevenP3 findings. Verdict:
**APPROVED-WITH-CONDITIONS for prospective compilation preparation only**.
The original case, geographic association and presentation remain gated.

CURRENT, SOUNDER and KEEL agree: consistent synthetic bytes do not prove actual
source support or physical current identity. The next original run requires a
guarded cloud acquirer and exact scientific preflight, followed by actual-source
and geographic review.

Three amendments made:

1. Added strict original-response/selection/receipt validation, exact inventory
   checks and sequential receipt chronology before monthly aggregation.
2. Added streaming Int64 paired sums, calendar-day thresholds, nullable monthly
   vectors, and integration retaining all72 unsupported diagnostic outcomes.
3. Specified canonical receipt hash meaning and remaining source/figure/table/
   query delivery gates without claiming that those stages have run.

Continued preparation requires no user permission checkpoint. Heavy work remains
disabled until the actual scientific/execution prerequisites are satisfied.

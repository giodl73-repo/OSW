---
skill: roles-check
topic: rust-width-sample-queries
date: 2026-10-04
source_commit: 913a8457dde0338f2807606d7a220fff85ae783d
working_branch: codex/seasonal-query-map
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Scoped width sample query review

Artifact: `build_query_width_samples.py`, bundle generation, Rust sample bindings,
query controls/card links, generated data/WASM and verification scripts. The
source commit identifies the working-tree base, not a committed feature release.
This is an internal functional-lens review. ORBIT is excluded: no planetary
comparison is introduced. Scientific admission remains pending in source records.

## CURRENT — physical quantity and support

| # | Finding | Severity/status | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Three methods do not form a common current-width ranking. | P3, verified | Separate method families/metrics: fitted a101 widths, seasonal axis-normal threshold profiles and monthly positive-zonal components. Query page states that numerical ordering is not a global rank. | Preserve metric-specific comparisons. |
| 2 | Source-reading margins are not measurement errors or confidence intervals. | P3, verified | Plot intervals stay in their own field; measurement uncertainty is null; confidence flags remain false. NECC threshold sensitivity remains in original sample. | Add physical error support through a separate reviewed field, never relabel the plotting allowance. |
| 3 | Whole-current dimensions and annual extrema are unsupported. | P3, verified | Helper and Rust reject representation/rank promotion; annual ranges remain null; no source-width buffer is drawn. | Require comparable axis/edge evidence before annual geography. |

## SOUNDER — exact source identity

| # | Finding | Severity/status | Evidence | Recommendation |
|---|---|---|---|---|
| 4 | Binding to a stored diagnostic alone does not reproduce its source. | P2, resolved | Bundle generator now rebuilds all three diagnostics from pinned PDF/configuration or provider archives; validates dependency hashes and records reconstruction code. | Keep source reconstruction before sample projection. |
| 5 | Five Kuroshio samples are unresolved. | P3, verified | All 64 original readings are imported; five values/plot intervals remain null and queryable. | Retain missing records instead of omitting or filling them. |
| 6 | Source calendar/period ambiguity must remain explicit. | P3, verified | Kuroshio seasonal months remain null; study years retained. Leeuwin conflicting period labels and unresolved combined window remain. NECC carries 2013 and original times. | Resolve conventions from sources before adding dates/month membership. |

## CHART — scalar samples and map interpretation

| # | Finding | Severity/status | Evidence | Recommendation |
|---|---|---|---|---|
| 7 | Width samples provide no new geographic footprints. | P3, verified | `width_samples` scenes are null; coordinates/brackets remain original nested data, with no new map feature injection. | Require independent geographic-edge support for map rendering. |
| 8 | Rounded display should preserve original readings. | P3, verified | Table displays approximate km, while `source_sample` retains original raw plot values/pixels or diagnostic spans/brackets. | Keep display rounding separate from stored scientific payload. |
| 9 | Graphical intervals can overlap without a unique minimum. | P3, verified | Leeuwin scope text explicitly retains July/September overlap and rejects a uniquely narrowest month from these readings. | Do not rank overlapping extracted intervals as certain differences. |

## BEACON — usable scientific labels

| # | Finding | Severity/status | Evidence | Recommendation |
|---|---|---|---|---|
| 10 | Raw method enums/readout prose obscured the main distinction. | P2, resolved | Inspector now uses readable method-family labels, humanized status, explicit velocity threshold and study years; duplicated scope prose removed. | Keep machine keys in structured records and meaningful labels in controls. |
| 11 | A resolved number does not imply scientific admission. | P3, verified | Parent diagnostic status is shown separately from sample resolution; three source documents remain review-pending. | Retain this distinction for future source families. |
| 12 | Users need a short path to original evidence. | P3, verified | Current cards link to filtered sample queries; sample cards link to parent diagnostics, publication or source inventory/receipts. | Preserve direct navigation as inventory grows. |

## HARBOR — access to selections and uncertainty

| # | Finding | Severity/status | Evidence | Recommendation |
|---|---|---|---|---|
| 13 | Sample dimensions needed visible query controls. | P2, resolved | Current, method, month and numeric-availability selectors expose the supported predicates; controls are shown only for samples. | Keep numeric availability distinct from confidence/admission. |
| 14 | Uncertainty and missing values need textual equivalents. | P3, verified | Unresolved values print as unresolved, margins carry units/type, and measurement uncertainty is explicitly unresolved; no color-only encoding. | Keep these labels alongside any future chart. |
| 15 | Cards and controls must reflow without pointer dependence. | P3, verified | Semantic selects/buttons and source links; standalone browser check exercises card links and 320 px viewport. | Preserve existing keyboard focus styles and narrow-layout checks. |

## KEEL — bindings and executable gates

| # | Finding | Severity/status | Evidence | Recommendation |
|---|---|---|---|---|
| 16 | A sample could be relabeled with a different season's parent. | P2, resolved | Rust binds sample path to phase path and original parent phase, along with payload/context, current, values, month/year, metric, intervals and status. | Test any future normalization against exact source pointers. |
| 17 | New queries must be identical across native and WASM engines. | P3, verified | Standalone check compares full/subset/unresolved queries, null-last numeric sorting, three object joins and direct card links. | Keep both runtimes in feature verification. |
| 18 | Source and scope mutation must fail before queries run. | P3, verified | Native load checks reject changed values, months, metrics, intervals, family, owner, confidence and phase support; Python tests reject scope promotion. | Preserve source integrity checks independently of presentation. |

## LOGBOOK — truthful scope and stable queries

| # | Finding | Severity/status | Evidence | Recommendation |
|---|---|---|---|---|
| 19 | Form sorting initially discarded preset current filters. | P2, resolved | Visible sample controls restore/preserve preset filters. Extra, duplicate or unsupported structured constraints remain active and are disclosed. | Never broaden a query silently during form use. |
| 20 | 88 samples are additional granularity for three existing currents. | P3, verified | Counts are 12 Leeuwin, 64 Kuroshio, 12 NECC. Canonical records, original documents and published length ranks are unchanged. | Expand through explicit source evidence, not extrapolated widths. |
| 21 | This is a local snapshot update, with journal/release implications. | P3, verified | Feature branch remains local; bundle hash changes; source/journal rebase contract and verification commands are documented. Original PDFs stay ignored. | Use protected PR/check workflow for main; retain old journals/source snapshots. |

## Synthesis and amendments

Roles reviewed: 7. Open P1: 0. Open P2: 0. Five P2 findings were corrected; 16 P3
findings record verified strengths/limits. Verdict: **APPROVED-WITH-CONDITIONS**
for local editorial sample querying, not scientific admission or publication.

CURRENT/SOUNDER/BEACON agree: plot reading, local diagnostic and physical
measurement uncertainty remain distinct; annual full-current dimensions cannot
be inferred from this import.

Completed amendments:

1. Reconstruct and pin parent diagnostic dependencies before source-bound projection.
2. Retain exact missing/calendar/uncertainty support and readable method/status labels.
3. Expose sample filters and preserve unsupported/duplicate structured constraints.

Verification: four Python projection tests (four mutation subtests), 19 Rust tests,
source reconstruction, JS syntax, standalone native/WASM sample browser checks,
and generated artifact/source checksum verification. Commands are documented in
`plans/rust-query-store-v1.md`, section "Scoped width samples".

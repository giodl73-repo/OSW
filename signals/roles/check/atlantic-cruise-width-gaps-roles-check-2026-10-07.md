---
skill: roles-check
topic: atlantic-cruise-width-gaps
date: 2026-10-07
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 3
p2_remaining: 1
p3_count: 18
verdict: APPROVED-WITH-CONDITIONS
---

# Atlantic cruise width gap review

Artifact: pinned publisher Tables 1–2, reproducible 30-record extraction,
inventory import, shared Rust/WASM query stores and per-current cruise chart.
All seven installed role definitions were read. This is an internal role review,
not independent scientific peer review or canonical measurement admission.

## CURRENT — physical meaning

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Distances come from transport-selected station pairs, not fixed speed contours. | P3 | Article Section 2.3 / row boundary rule | Preserve the distinct metric; do not rank whole-current widths. |
| 2 | Decade labels could be mistaken for decade averages. Resolved with explicit cruise joins, sampling-window roles and false mean flags. | P2 resolved | Table 1 mapping / time convention | Retain snapshot scope and leave exact boundary occupation dates unknown. |
| 3 | Density layers and reported depth extents differ across sections. | P3 | Table 2 E–F / depth context | Never treat the depth extent as a uniform fixed layer or interpolate snapshots. |

## SOUNDER — source custody

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Two original publisher workbooks are archived with URLs, hashes, byte counts and CC BY 4.0 attribution. | P3 | acquisition.json | Keep acquisition explicit and default extraction offline. |
| 2 | Original cells, row addresses and exclusions remain separate from measurement projections. | P3 | original_tables / excluded_rows | Preserve source station labels without reindexing against cruise station totals. |
| 3 | Table 1 and Table 2 disagree on the 2018 A095 latitude. | P3 | Held-out rows 14 and 32 | Resolve with original cruise metadata; neither row is admitted here. |

## CHART — visual meaning

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Nominal latitude plus source longitude limits cannot establish map endpoints. | P3 | Section 2.1 / geometry null | Recover actual station positions before a locator, footprint or state join. |
| 2 | Scalar bars represent Table 2 distances with a zero-based kilometre axis. | P3 | cruise-span-chart | Retain a separate bar per snapshot and avoid connecting time-series lines. |
| 3 | Section and layer changes prevent interpreting bar differences as an annual range. | P3 | Chart scope / metadata table | Keep scope text adjacent to the chart and all annual/playback flags false. |

## BEACON — explanation and navigation

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | “Transport-selected cruise-section span” names the stored quantity. | P3 | Metric label / evidence title | Keep this distinction on atlas cards and in query output. |
| 2 | Cruise IDs alone are insufficient to read temporal support. | P3 | Sampling-window column | Preserve dates and nominal section beside each reported value. |
| 3 | Each current has a short path from chart to published source, exact query records and selected evidence. | P3 | Chart links / atlas inspector links | Preserve query and direct-record addresses. |

## HARBOR — equivalent access

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Bars have value labels, SVG descriptions and a semantic source table. | P3 | SVG desc / table caption and headers | Preserve equivalent textual meaning without reliance on color. |
| 2 | Mobile chart/table scrolling needs keyboard focus and adequately sized record links. Resolved with a labelled focusable region, visible outline and 44 px minimum links. | P2 resolved | Scroll-region CSS / browser check | Verify ArrowRight scrolling and page reflow at 320 px. |
| 3 | Snapshots need no animation. | P3 | Disabled seasonal play / independent bars | Preserve reduced-motion behavior and avoid implying annual continuity. |

## KEEL — reproducibility

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Standard-library workbook extraction was independently compared with bundled read-only openpyxl for both complete first sheets. | P3 | Independent cell parity check | No new spreadsheet library is needed in CI. |
| 2 | Mutation tests reject changed widths, identity, dates, layers, geometry and statistical interpretations. | P3 | test_atlantic_cruise_widths.py | Keep the exact pinned extraction comparison. |
| 3 | The new browser test is registered in the complete publication runner. | P3 | Runner declares 49 checks | Exercise all 30 spans, nine owners and native/WASM equality on the candidate. |

## LOGBOOK — publication honesty

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Prior canonical numerical records and source release remain unchanged. | P3 | Batch importer / canonical source parity | Preserve editorial admission until independent review. |
| 2 | The batch depends on pending PR #31 and must not be presented as mainline. | P2 open | Dependency chain / current remote checks | Rebase and retarget after dependencies land; pass required contexts before merge. |
| 3 | Remaining core gaps are recorded separately from UI coverage. | P3 | Batch plan / width decisions | Continue 58 unassessed widths, 89 source lengths and dated named-eddy footprints. |

## Synthesis and amendments

Seven roles, 21 findings: 0 P1, 3 P2 (two resolved, one publication condition),
18 P3. Verdict: APPROVED-WITH-CONDITIONS. CURRENT and CHART agree that the
metric and actual geography must remain separate. SOUNDER and KEEL require
exact original-table custody and mutation checks.

1. Preserve the transport-derived metric and explicit cruise windows instead
   of using decade labels as temporal means.
2. Retain null map geometry and hold out the conflicting 2018 joins.
3. Keep the reviewable batch separate from its pending dependencies and update
   publication status only after required CI and actual mainline landing.

---
skill: roles-check
topic: loop-inflow-section-spans
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Loop inflow section spans review

Internal functional review of section protocol/generator, two diagnostic files,
Rust sample/map/chart support, query UI and tests. This is not independent
scientific review. CURRENT covers physical meaning, SOUNDER source identity,
CHART geometry, BEACON interpretation, HARBOR access, KEEL reproducibility and
LOGBOOK repository evidence. ORBIT is excluded: no planetary comparison.

| # | Role | Finding | Severity / disposition | Evidence or action |
|---|---|---|---|---|
| 1 | CURRENT | A zonal component span is not a flow-normal current width. | P3, verified | Fixed 21.875 N section, northward component and gate limits explicitly declared. |
| 2 | CURRENT | A local inflow span cannot widen the whole Loop route. | P3, verified | No buffers, width-based state joins, occupied polygon or whole-current dimensions. |
| 3 | CURRENT | A coarse span needs effective-resolution review. | P3, open | September 2026 NOAA span below four native spacings is flagged; all boundaries remain scientifically unadmitted. |
| 4 | SOUNDER | Products and dates must remain separately bound. | P3, verified | Five pinned source receipts per product; date, response SHA, algorithm and source URL retained. |
| 5 | SOUNDER | Processing versions can confound temporal differences. | P3, verified | NOAA RADS 4.7.0/4.7.1/4.8.1 shown; DUACS version preserved; no isolated physical-change claim. |
| 6 | SOUNDER | Shared altimetry prevents an independence claim. | P3, verified | Source scope and query cards disclose shared observations possible; no pooled uncertainty. |
| 7 | CHART | Paired geographic endpoints need their own orientation. | P3, verified | Loop maps west/east longitudes at fixed latitude; Gulf meridional geometry remains unchanged. |
| 8 | CHART | Product charts inherited a Gulf Stream title. | P2, resolved | Loop inflow NOAA/DUACS titles and two source panels added; rendered charts inspected. |
| 9 | CHART | Sparse sample dates must preserve gaps. | P3, verified | Gregorian elapsed-day axes, unconnected points and recorded-date playback; no interpolation. |
| 10 | BEACON | Threshold sensitivity is not measurement uncertainty. | P3, verified | 40/50/60% scenarios retained; outward-rounded finite interval, null confidence/annual values. |
| 11 | BEACON | One-sided failure must not become a width. | P3, verified | Each boundary/stop reason retained; missing side gives null paired span; synthetic missing-cell case. |
| 12 | BEACON | Approximate values require consistent rounding. | P3, verified | Nominal nearest 10 km, halves upward; raw values and geometric brackets retained. |
| 13 | HARBOR | Parent cards and map marks need keyboard access. | P3, verified | Existing semantic sample buttons, chart/map selection and parent-diagnostic inspection used. |
| 14 | HARBOR | Reduced-motion setting did not disable query playback. | P2, resolved | Preference listener stops animation and disables play controls; browser regression verifies it. |
| 15 | HARBOR | Small screens must retain section meaning. | P3, verified | 320 px reflow; latitude, metric, source processing and uncertainty text remain accessible. |
| 16 | KEEL | Source/latitude/value mutation must fail before maps. | P3, verified | Raw-parent SHA plus projection/latitude/owner binding; malformed-bundle cases cover values, edges, annual promotion and source strings. |
| 17 | KEEL | Skipped native samples could bridge a gap. | P2, resolved | Adjacent native longitude spacing required; missing sample stops boundary walk. |
| 18 | KEEL | Existing source series must retain original results. | P3, verified | Original 105 sample values, metrics, dates and source records compared with main; Gulf dated regression passes. |
| 19 | LOGBOOK | New counts must be explicit and scoped. | P3, verified | 115 sample records, 17 diagnostic documents; canonical 37 width records and length ranking unchanged. |
| 20 | LOGBOOK | Rules must travel with the stored data. | P3, verified | Dedicated pinned section protocol, generator/sampler hashes, contract and tests included. |
| 21 | LOGBOOK | Local evidence cannot imply completed annual atlas. | P3, open | Sparse sample spans only; canonical/source-use/scientific admission and annual evolution remain open. |

## Synthesis and amendments

Seven roles, 21 findings: three P2 issues resolved, 18 P3 notes, no open P1/P2.
APPROVED-WITH-CONDITIONS for local component-span diagnostics. CURRENT, SOUNDER
and BEACON agree to separate local section spans, product differences, finite
threshold sensitivity and actual annual variation.

1. Retain adjacency, missing-boundary failures and conservative geometric brackets.
2. Separate product panels, processing versions, dates and source-bound map support.
3. Stop/disable playback under reduced motion; preserve manual date filters.

Verification: focused section/sample/dashboard Python checks; 22 Rust tests;
native/WASM parity; source-mutation rejection checks; product charts and exact local
map endpoints; original 105-sample comparison; existing width and Gulf dated
browser regressions; parent cards, recorded playback, reduced motion and 320 px
reflow. Source use and independent scientific admission remain unresolved; this
follow-up is local and has not been published.

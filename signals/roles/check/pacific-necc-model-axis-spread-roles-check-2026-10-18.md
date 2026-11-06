---
skill: roles-check
topic: pacific-necc-model-axis-spread
date: 2026-10-18
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---
# Pacific NECC model axis-distance scale review

Direct application of the installed role lenses to the batch on parent ab0a5a8d05fdf078a830ae6f4fa089a0ed0f81ab. Internal review, not independent scientific peer review. CURRENT covers physical meaning; SOUNDER source custody; CHART scalar/geographic encoding; BEACON claims; HARBOR accessible use; KEEL reproducibility; LOGBOOK actual delivery state. ORBIT is omitted because there is no planetary comparison.

| Role | Finding and evidence | Severity | Resolution or condition |
|---|---|---|---|
| CURRENT | Equations 1–3 define a positive-transport weighted mean absolute axis distance. | P2 | Exact operator retained; no RMS, sigma, FWHM or full-width conversion. |
| CURRENT | The 0–150 m layer and spatial averaging define a model diagnostic. | P2 | Layer, 0–10 N, 135–155 E and OFES context visible; no observational admission. |
| CURRENT | Two approximate change states cannot bound annual variability. | P2 | Null annual range/error, no exact dates or playback; mutation checks reject false claims. |
| SOUNDER | Figure 8 is in degrees, whereas the conclusion gives kilometre summaries. | P2 | Original pages inspected; 100/130 transcribed from conclusion; no OSW degree conversion. |
| SOUNDER | Local paper custody does not imply permission to redistribute it. | P2 | Pinned original and receipt retained locally; only receipt/extraction committed. |
| SOUNDER | Raw fields, exact series and independent observed trend are unavailable. | P2 | Explicit false acquisition/reproduction flags; 13-month filter and forcing caveat retained. |
| CHART | A model spread scale must not become a geographic ribbon. | P2 | Scalar bars only; no invented edges, footprints or state intersections. |
| CHART | Plotting the two states at 1960 and 2014 would invent endpoint dates. | P2 | From/to labels with no year axis or connected temporal curve. |
| CHART | Inherited seasonal table minimum width initially overflowed at 320 px. | P2 | Local fixed-layout table removes inherited minimum; actual viewport and SVG checks now pass. |
| BEACON | Increased scoped evidence is not complete physical-width coverage. | P2 | Model scale meaning and unknown full/annual widths accompany the values. |
| BEACON | New western-Pacific evidence could hide the older eastern-Pacific candidate. | P2 | Existing 12-profile OSCAR candidate preserved, explicitly pending, and linked; browser roundtrip passes. |
| BEACON | Readers need original citation and inspectable numeric records. | P3 | Shared component includes author copy, DOI, source query and per-row inspectors. |
| HARBOR | Scalar meaning must be accessible without color. | P2 | Numeric two-row table, bar labels and model/operator text are always available. |
| HARBOR | Card disclosure and source controls need keyboard operation. | P2 | Actual keyboard browser check passes; native disclosure used. |
| HARBOR | Motion and narrow layouts must not obscure limitations or values. | P2 | 320 px/reduced-motion checks and screenshot inspection pass; no seasonal playback enabled. |
| KEEL | Metric/source corruption must fail even if values look plausible. | P2 | Eleven native and actual WASM rejection cases pass, including missing/duplicate rows and source rebindings. |
| KEEL | Single-row query filtering could misrepresent the two-state comparison. | P2 | Rust scene carries both source states with explicit matching IDs; filtered query test passes. |
| KEEL | Rebuilding shared bundles can alter older evidence. | P2 | 153 earlier rows, candidate/review arrays, 42 query diagnostics and prior seasonal values preserved; 88 pins verified. |
| LOGBOOK | The old Antilles full-suite result had one stale assertion failure. | P2 | Failure retained in history; parent fixes expectation and targeted test passes. New clean combined gate required. |
| LOGBOOK | More gap filling must not create another PR. | P2 | Same continuing branch and draft PR #83; no main merge. |
| LOGBOOK | Focused passes do not establish complete current or seasonal coverage. | P2 | Counts label scoped records; full gate remains a condition and remaining gaps remain explicit. |

21 findings; zero unresolved P1 findings. APPROVED-WITH-CONDITIONS: execute and record a clean combined full-suite gate on the committed batch before calling its complete gate green. Existing remote acquisition failure for the older Reading-hosted Van Aken PDF is a separate CI concern, not evidence that this scientific source is missing locally.

## Amendments implemented

1. Bind metric, original source, author-reported units and model support; reject false conversions, extrema and geographic claims.
2. Share an accessible scalar comparison and repair mobile table overflow; keep the old candidate visibly pending and navigable.
3. Preserve earlier records, distinguish source states from query matches, and report historical failure, repair and new gate separately.

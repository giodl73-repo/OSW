---
skill: roles-check
topic: west-spitsbergen-selected-core-source
date: 2026-10-17
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---
# Published WSC core statistic: source package review

Direct use of seven installed role lenses; not independent external review. Artifact: final publisher original, acquisition and dataset metadata, protocol, extraction, validator, tests and OSW figure. ORBIT excluded: no astronomical mechanism. This review covers the source package; shared inventory/Rust/UI admission is still required.

| Role | Finding | Severity | Resolution |
|---|---|---|---|
| CURRENT | A 28 km core statistic is not a whole-current width. | P2 | Local zonal core scope and all whole-current eligibility flags remain explicit. |
| CURRENT | Q and QAW use different vertical supports. | P2 | Preserve full sampled-column Q; no temperature/salinity mask substituted. |
| CURRENT | A 60th-percentile section selection is not a 60 percent peak contour. | P2 | Separate percentile, search region and fixed transport-region boundary fields. |
| SOUNDER | Reported standard deviation can be mistaken for error or extrema. | P2 | Separate 7 km SD field; width range, confidence and annual fields remain null/false. |
| SOUNDER | Glider depth-average current alone cannot reproduce the paper. | P2 | Satellite surface reference and affected sections 7-10 retained. |
| SOUNDER | Dataset citation does not prove raw data acquisition. | P2 | Pin metadata snapshots; native profile bodies explicitly not acquired. HEAD probes are labelled metadata only. |
| CHART | Whiskers can imply a measured min/max range. | P2 | Axis and caption identify reported SD; no geographic edge band. |
| CHART | A 2 km grid can imply 2 km independent resolution. | P2 | Figure and record retain 40 km mapping scale and 3.5 km mean native spacing. |
| CHART | Sampling windows should expose gaps. | P3 | Three disconnected bars use exact Table 1 target-section dates. |
| BEACON | Missions have more dates than the science target-section windows. | P2 | Table 1 start/stop used, not deployment or recovery. |
| BEACON | Repeated autumn/winter sections do not establish full-year seasonality. | P2 | No seasonal playback or annual extrema. |
| BEACON | A source extraction must not claim exact reproduction. | P2 | Selected membership/count, numerical threshold and per-section widths remain unknown. |
| HARBOR | The figure needs a textual/numeric equivalent. | P2 | JSON contains width, SD, periods and method; shared UI table/inspector remains an integration condition. |
| HARBOR | Color cannot carry the only meaning. | P3 | Axis, marker, whisker label, mission names and dates provide redundant meaning. |
| HARBOR | SVG requires an accessible description. | P3 | SVG role/label and descriptive metadata added; rendered PNG inspected. |
| KEEL | Unchanged old source columns must not be pooled with this estimator. | P2 | Protocol prohibits pooling 2015 stream-tube widths with selected core statistic. |
| KEEL | Mutated source semantics must reject. | P2 | Frozen extraction and original SHA; tests reject SD/range, percentile, DAC and date changes. |
| KEEL | Plot regeneration must be deterministic. | P2 | Two consecutive SVG/PNG generation receipts match by hash. |
| LOGBOOK | Source readiness must not imply inventory admission. | P2 | Source package is explicitly pending shared inventory/Rust/UI integration. |
| LOGBOOK | Licensed original needs attribution. | P2 | Final CC BY 4.0 paper retained unmodified; rights visually checked on first page and acquisition includes attribution. |
| LOGBOOK | User rejected per-gap PRs. | P2 | Same codex/current-measurement-gaps workstream and draft PR 83; no new PR or main merge. |

21 findings: 0 P1, 18 P2, 3 P3. Source-package amendments above are implemented. Integration conditions remain: add the scoped width record with exact compiled Rust binding, surface the point and separately labelled SD in current-card/seasons/query views, verify numeric source inspection and mobile/keyboard behavior, preserve earlier widths, and run the combined gate. These are required work, not a passing claim.

## Amendments
1. Keep the reported standard deviation separate from ranges, error bounds and annual extrema.
2. Preserve the exact source method and discontinuous target-section periods instead of reconstructing missing selections.
3. Present the measurement with its metadata and visible sampling gaps, then complete shared inventory and UI integration on the same PR.

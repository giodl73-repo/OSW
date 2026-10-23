---
skill: roles-check
topic: ke-qiu-plot-pathlength-v1
date: 2026-10-23
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Prospective Kuroshio Extension regional length extraction

Source commit:2abc1cb8e245bc03a3aef585d9b73a8c9dec1a1a. Reviewed proposed
producer, synthetic tests, protocol and original-source facts before numerical
red-trace extraction. Seven internal functional lenses; not independent
scientific peer review. ORBIT is excluded: no planetary comparison is proposed.
Roles are selected for physical support, source custody, charts, editing,
accessibility, reproducibility and repository maintenance respectively.

| Role | Finding and evidence | Severity | Recommendation / disposition |
|---|---|---|---|
| CURRENT | Figure2a gates141E–153E cover the upstream KE, not the complete current. | P3 | Report regional support explicitly; whole-current length and rank remain null/false. |
| CURRENT | A pathlength trace does not recover the geographic axis or transverse width. | P3 | Producer keeps geographic_centerline and physical_width_km null. |
| CURRENT | Daily source SSH does not establish daily plot sampling or seasonal extrema. | P3 | Precise dates, seasonal eligibility and annual extrema remain absent/false. |
| SOUNDER | Complete original bytes and selected pages have separate custody and review support. | P3 | Exact hash/size/page count pinned; selected pages1,3,4 only; complete article stays private. |
| SOUNDER | Equal x positions can arise from finite plot precision. | P3 | Preserve distinct vertices; no duplicate-time averaging or invented timestamps. |
| SOUNDER | Reading allowances require a stroke/calibration limit. | P3 | Added maximum0.5-point source stroke; justify50km/0.1year allowances and test rejection above limit. |
| CHART | The red time-series trace could be confused with a mapped current route. | P3 | Separate scalar year/km chart with regional gates in title and visible scope. |
| CHART | Joining separate runs would manufacture graph continuity. | P3 | Separate SVG polylines for every retained run; preserve breaks and all vertices. |
| CHART | A time axis without a label may imply exact dates. | P3 | Added visible Approximate year axis label and reading allowances. |
| BEACON | Plotted minima/maxima do not establish all-source or physical extrema. | P3 | Name plotted_vertex_reading_range_km and attach range_scope. |
| BEACON | Fractional-year six-decimal storage can imply excessive precision. | P3 | Every row has explicit0.1year reading allowance; chart omits artificial exact dates. |
| BEACON | A standardized KE index mixes several quantities. | P3 | Select only red panel2a pathlength; exclude index, transport, position and recirculation. |
| HARBOR | A colored line alone cannot supply equivalent numerical access. | P2 | Complete samples must reach query/table UI alongside described SVG before delivery. |
| HARBOR | Current-card links must be usable with keyboard and a phone. | P2 | Focused browser proof required after integration; prospective freeze is not UI completion. |
| HARBOR | Vector SVG should retain semantic description and visible units. | P3 | SVG title/desc, year/km axes and visible scope/allowances provided; inspect actual rendering after build. |
| KEEL | A live original download cannot be the default arithmetic replay dependency. | P3 | Retained factual trace supports offline replay; exact original replay is a separate command. |
| KEEL | Parser and selection changes after seeing a result would compromise prospective custody. | P3 | Pin PyMuPDF1.28.2 and method/tests/protocol/facts in preflight and Git before extraction; never overwrite products. |
| KEEL | Synthetic calibration does not verify actual selectors or source support. | P2 | Require original trace replay, independent actual readback and all-vertex accounting after extraction. |
| LOGBOOK | Method freeze is distinct from admitted/publicly indexed evidence. | P3 | Record phase accurately; query/source catalog and admission are pending. |
| LOGBOOK | One PR per increment conflicts with the accepted batch workflow. | P3 | Continue existing branch and draftPR83; freeze commit precedes final delivery. |
| LOGBOOK | Existing remote scientific proof cannot cover a new extraction. | P3 | Retain pending focused and fresh remote gates; do not claim full regression green. |

Roles reviewed:7. P1:0; P2:3; P3:18.
Verdict: APPROVED-WITH-CONDITIONS for prospective freeze and actual extraction;
not approval to claim a delivered, seasonal or whole-current measurement.
CURRENT, SOUNDER and CHART agree on regional plotted support and approximate time.

## Required amendments and remaining gates

1. Keep all vertices, equal-x readings and explicit breaks, and validate source
   custody and actual calibration independently after extraction.
2. Expose complete numeric rows with chart/source links and verify keyboard,
   phone and native/WASM equality before publishing the completed increment.
3. Freeze all scientific inputs first, retain failures and use a new version
   for corrections. Local jobs remain sequential, below-normal priority, one
   logical CPU; full regression is an exclusive eventual batch gate.

## Prospective v2 operator-support amendment

V1 failed closed on a cubic command, before calibrated target readings. Keep
the frozen v1 method/protocol/tests/preflight and first extraction failure.
The raw operator diagnostic (1532 lines,4 cubics) justifies the explicit v2
correction; it contains no calibrated km/year series. V2 source commit before
freeze:f323484. The same seven lenses and21 findings apply, with these
specific dispositions:

- CURRENT: derived cubic graphic readings are never called observed samples;
  all regional, width, seasonal and physical-extrema exclusions are retained.
- SOUNDER: retain all original commands and control points as source evidence;
  exact-original replay and public offline command-mirror replay are separate.
- CHART: preserve cubic shape with a declared0.01-point interpolation bound,
  all y-stationary points and explicit run breaks.
- BEACON: count original graph knots and derived readings separately; say
  graphic range rather than implying original samples or physical extrema.
- HARBOR: visible scope, numeric table and phone/keyboard proof remain required.
- KEEL:47 combined prospective synthetic tests pass. Three initial synthetic
  count assertions incorrectly expected16 intervals where the declared error
  bound requires32; expectations corrected before v2 freeze, not the algorithm.
- LOGBOOK: this is an explicit new version, not an edit to the failed frozen
  method. No target calibrated range has been inspected. Delivery conditions
  and the continuing PR workflow remain unchanged.

Verdict remains APPROVED-WITH-CONDITIONS for prospective freeze/extraction;
P1:0, P2:3, P3:18. Actual calibration, UI integration and fresh39-report
scientific replay remain pending. The previous38-report Labrador replay passes
on Linux but cannot establish the new extraction's correctness.

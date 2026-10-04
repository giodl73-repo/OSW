---
skill: roles-check
topic: kuroshio-seasonal-width-profiles
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 3
p2_remaining: 0
p3_count: 18
verdict: APPROVED-WITH-CONDITIONS
---

# Kuroshio seasonal width profile review

Artifacts: source Figure 5 feasibility check, Figure 6a color-pixel extraction, local protocol, four-profile JSON, atlas card and dashboard. Selected roles: CURRENT for physical scope; SOUNDER custody; CHART encoding; BEACON wording; HARBOR access; KEEL reproducibility; LOGBOOK status. ORBIT is inapplicable. Role definitions were inspected in this conversation. These are internal role lenses, not independent scientific admission.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Seasonal regional profiles do not provide occupied geographic boundaries. | P3 | Scope | Keep null edges/geometry/layer/occupation and false geographic playback. |
| 2 | Source diagnostics precede averaging. | P3 | Method | Retain 0.1 m/s along-axis cutoff, normal sections and historical study interval. |
| 3 | Sparse sampling cannot establish regional spring/autumn means or annual extremes. | P3 | Statistics | Keep regional mean and annual width range null; prose records stay separate. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Overlapping or ambiguous source pixels could silently become zero or interpolated widths. | P2 | Extractor | Mark five missing samples null; multiple eligible color bands are unresolved. Mutation checks reject filling them. Addressed. |
| 2 | Calibration and RGB decisions are editorial transformations. | P3 | Custody | Pin PDF/image/config/protocol/generator and record raw pixels/values. |
| 3 | Raster decoder version may affect JPEG readings. | P3 | Runtime | Record PyMuPDF 1.28.2 and NumPy 2.4.1 with decoded raster checksum; regeneration must match. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Missing crosses inside width axes would imply a numeric width. | P2 | Encoding | Move crosses to a labelled missing row below the plot; table says missing. Addressed. |
| 2 | Figure 5 overlapping raster axes cannot supply four complete geographic routes. | P3 | Geography | Document extraction limit and retain separate coordinate-data review requirement. |
| 3 | Error bars could imply confidence in annual physical width. | P3 | Legend | Label +/-10 km editorial reading allowance, not uncertainty or confidence. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Four plotted profiles could be called four regional scalar means. | P3 | Copy | Profile readings and source winter/summer/study means remain distinct. |
| 2 | Season names do not establish calendar month membership. | P3 | Time | Explicit unresolved month convention and study period; no invented DJF/JJA. |
| 3 | 59 readings across four profiles may sound like full geographic coverage. | P3 | Coverage | State 59/64 declared samples, regional interval and omitted endpoints. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Color alone cannot identify season or missing data. | P3 | Access | Labelled select/status and sixteen-row table provide equivalent values. |
| 2 | Autoplay should stop and clean up when leaving. | P3 | Controls | Explicit Play/Pause, stop autumn, hidden-document stop and disposed-card cleanup pass. |
| 3 | Evidence tables need to be opened before visible-text assertions. | P3 | Browser checks | Open disclosure explicitly and test 320 px reflow; human assistive-technology review pending. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Dashboard could accept scope-promoted or edited profile contents. | P2 | Pipeline | Require equality to pinned local extraction; mutation tests reject annual range, confidence, geographic eligibility and missing-to-zero. Addressed. |
| 2 | Same-URL navigation is weak proof of share restoration. | P3 | Shared state | Load shared season URL from about:blank; source card restores selected season. |
| 3 | Profile records must not duplicate the two seasonal prose anchors. | P3 | Counts | Count four views; retain three scoped source measurements without adding raw reading count to inventory. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Prior scope audit records prose-only extraction. | P3 | History | Keep immutable receipt; new profile document has its own local protocol and status. |
| 2 | Local diagnostics do not change canonical admission. | P3 | Release | Canonical unchanged; source data and graph extraction remain editorial. |
| 3 | Focused green checks do not complete public release. | P3 | Gates | Independent science, human accessibility and clean-checkout/publication checks remain open. |

## Synthesis

Seven roles, 21 findings: zero P1, three addressed P2, eighteen P3. APPROVED-WITH-CONDITIONS for local historical profile display. Top finding: unreadable or ambiguous pixels must remain missing, and their marker must not occupy a numeric width position. SOUNDER, CURRENT and CHART agree that graph profile samples do not establish full seasonal geographical routes or annual physical extrema.

## Three amendments

1. Pin color sampling/calibration and source image, preserve ambiguous readings as null, record decoder/runtime versions and reading allowances.
2. Display missing samples outside the numeric chart, provide a table, retain regional/source-mean distinctions, and keep geographic geometry unmodified.
3. Pin actual profile contents in dashboard updates, count four seasonal views without prose duplication, and verify new-navigation restoration, cleanup and fail-soft scope rejection.

## Evidence and limits

Passed: two graph regeneration/mutation tests; twenty dashboard tests; width validator (37 source records across 24 names); Kuroshio prose inspector roundtrip; four-profile browser test covering missing values, selected season restoration, autumn stop, stable map view, disposed-card timer, 320 px reflow and invalid geographic-promotion fallback. Native Figure 5 and 6 images visually inspected; atlas screenshot inspected after moving missing markers below the width plot. Source geometry limitations and calibration are in the protocol. No geographic seasonal map edges are claimed. Canonical remains 6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e. Independent science, human assistive-technology and full clean-checkout/publication gates remain pending.

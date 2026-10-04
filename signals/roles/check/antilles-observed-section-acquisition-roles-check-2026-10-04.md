---
skill: roles-check
topic: antilles-observed-section-acquisition
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Antilles observed sections: internal editorial review

Artifacts: explicit NOAA final-profile acquisition, offline inventory and diagnostic builders, draft local measurement protocol, plotted sections, station map, dashboard/atlas series link and tests. Roles selected for physical meaning, data provenance, cartography, public explanation, accessibility, reproducibility and repository accuracy. ORBIT excluded: no planetary comparison. This is not independent scientific admission.

## CURRENT

| # | Finding | Severity | Section | Recommendation / evidence |
|---|---|---|---|---|
| 1 | A one-sided half-peak span could be doubled or promoted to full width. | P2 resolved | acquisition / diagnostic / page / tests | Both full-width fields remain null; nearshore edge undiagnosed and admission flags false. |
| 2 | Two May occupations cannot establish an annual cycle. | P3 condition | acquisition / diagnostic / page / tests | No seasonal playback, annual extrema or along-current route inferred. |
| 3 | Tides and method-dependent velocities may influence the section. | P3 condition | acquisition / diagnostic / page / tests | Unremoved tide flag and error velocity preserved; scientific review required. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation / evidence |
|---|---|---|---|---|
| 1 | Source units and cast-time header syntax must parse exactly. | P2 resolved | acquisition / diagnostic / page / tests | Slash/colon metadata keys supported; cm/s to m/s tested; 400 m kept distinct from dbar. |
| 2 | Quality warnings and no-data casts cannot silently become usable ocean values. | P3 verified | acquisition / diagnostic / page / tests | 17 cautions retained; casts 24-36 absent; unknown sentinel-like values stop parsing. |
| 3 | Provider bytes and transformations need reproducible provenance. | P3 verified | acquisition / diagnostic / page / tests | 57 files plus assessment/directory pinned; SHA checks and offline byte-identical regeneration pass. |

## CHART

| # | Finding | Severity | Section | Recommendation / evidence |
|---|---|---|---|---|
| 1 | Initial display extent would clip observed station coordinates. | P2 resolved | acquisition / diagnostic / page / tests | View corrected; browser asserts every station inside map bounds. |
| 2 | Sampling transect must not imply a current axis. | P3 verified | acquisition / diagnostic / page / tests | Station points only, explicit transverse-sampling description and no route count increment. |
| 3 | Interpolated offshore crossing is not an observed edge. | P3 condition | acquisition / diagnostic / page / tests | Exploratory threshold and source brackets disclosed; no footprint, buffer or uncertainty interval. |

## BEACON

| # | Finding | Severity | Section | Recommendation / evidence |
|---|---|---|---|---|
| 1 | About 37 km needs its exact meaning near the number. | P3 verified | acquisition / diagnostic / page / tests | Repeatedly labeled sampled-peak-to-offshore-half-peak span, requiring review. |
| 2 | A newly acquired old record must not look like live current activity. | P3 verified | acquisition / diagnostic / page / tests | May 2005 labels in page, chart, URL-selectable occupations and station timestamps. |
| 3 | Source data and derived interpretation need separate access. | P3 condition | acquisition / diagnostic / page / tests | Raw inventory, calculation, method, NOAA access and regional paper linked separately. |

## HARBOR

| # | Finding | Severity | Section | Recommendation / evidence |
|---|---|---|---|---|
| 1 | Selected occupation must have an equivalent textual view. | P3 verified | acquisition / diagnostic / page / tests | 23/27-row tables with UTC dates, velocity, error velocity and quality comments. |
| 2 | Stations and occupation controls must work without a pointer. | P3 verified | acquisition / diagnostic / page / tests | Keyboard focus exposes cast name; accessible station descriptions retain quality/time. |
| 3 | Narrow presentation must keep table and chart usable. | P3 verified | acquisition / diagnostic / page / tests | 320 px document reflow passes; wide table scrolls locally, map/plot stay responsive. |

## KEEL

| # | Finding | Severity | Section | Recommendation / evidence |
|---|---|---|---|---|
| 1 | Gap walking must not skip cautioned or missing casts. | P3 verified | acquisition / diagnostic / page / tests | Adversarial fixtures stop the span at an intervening invalid sample. |
| 2 | Dashboard integration must preserve provenance and pending status. | P3 verified | acquisition / diagnostic / page / tests | 13 dashboard tests include checksum mismatch, full-width, axis and annual-playback relabel rejection. |
| 3 | Focused verification is not a full clean-checkout release gate. | P3 condition | acquisition / diagnostic / page / tests | Five data tests and focused browser pass; full repository default suite not rerun. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation / evidence |
|---|---|---|---|---|
| 1 | New dataset must not increase published current dimensions. | P3 verified | acquisition / diagnostic / page / tests | 19 scoped width records / 15 names and 62 routes / 59 names remain unchanged; new diagnostic separate. |
| 2 | Repository status and attribution need the new local acquisition. | P3 verified | acquisition / diagnostic / page / tests | Source register, notices, coverage plan and protocol record provider/citation/access. |
| 3 | Internal editorial review cannot substitute for independent science admission. | P3 condition | acquisition / diagnostic / page / tests | Frozen release and canonical inventory unchanged; independent review and longitudinal axes remain open. |

## Synthesis

21 findings: zero P1, three P2 addressed, 18 P3 verified notes or remaining conditions. APPROVED-WITH-CONDITIONS for local evidence presentation. CURRENT, SOUNDER and CHART agree that observed instrument positions and the computed half-peak crossing do not establish a full-width current footprint or along-current axis.

Three amendments implemented:

1. Preserve source metadata syntax, units, timestamps, version-label discrepancy, quality warnings and absent casts in pinned local products.
2. Keep first occupation unresolved when a caution gap blocks the boundary walk; repeat one-sided candidate remains unadmitted with full width and annual ranges null.
3. Correct map extent and label size; verify station coverage, keyboard focus, restored section URL, atlas return and narrow reflow.

Evidence: 57 profiles / 22,619 samples, 40 provider-usable / 17 caution; 50 Abaco casts in two occupations plus seven other-section casts excluded. Five profile/measurement tests and 13 dashboard tests pass. Focused browser passes atlas -> section view -> restored repeat -> atlas. Page screenshot inspected. Offline inventory, diagnostic JSON and Matplotlib SVG are byte-identical on regeneration. Canonical almanac SHA unchanged. Full repository suite not rerun.

Remaining: scientific review of parsing/membership, tides/error velocities, threshold sensitivity, station support and sampled-peak representativeness; both layer-compatible boundaries; along-current axes and annual observations; independent admission and release review. No new published length, width ranking, footprint or seasonal cycle claimed.

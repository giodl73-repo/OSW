# Kuroshio model-axis-normal measurement batch

Base: 9b335cb80429dff47d18984db62e3dda48934869. Continue the existing
codex/current-measurement-gaps branch and draft PR83. This is scientific
source extraction and a standalone figure; main query/atlas integration
remains required work. The full core-data/info/visualization goal is active.

## New measurements

The earlier data supplied fixed-latitude boundary separations. This batch
intersects the two independent model boundaries with reconstructed geodesic
axis normals. No boundary arrays are paired by index. It reuses every day of
2024, nominal levels0.49/109.73/380.21m, five latitude gates, and three declared
tangent half-windows7/14/28km. The primary half-window is14km.

| Result | Attempts | Resolved | Unresolved and retained |
|---|---:|---:|---:|
| All tangent conventions |16,470 |14,034 |2,436 |
| Primary14km half-window |5,490 |4,680 |810 |

The report retains585 calendar-month/annual summaries, plus15 matched-date
tangent-sensitivity summaries. IDs identify date, source depth, gate, tangent
window and operator edition. Ambiguous crossings retain their candidate
geometry and source indices. Three resolved spans exceed the nominal140km
source transect length; they are flagged, never clipped. The smallest finite
span is about10km. No finite value is below the source's7km velocity sampling.

Examples at24.5N, primary convention, rounded for interpretation:

| Nominal depth | Resolved dates | 2024 sample min / median / max |
|---|---:|---|
|0.49m |321/366 |about60 /110 /140km |
|109.73m |365/366 |about80 /110 /130km |
|380.21m |359/366 |about70 /90 /110km |

These are model geometry sample ranges, not physical annual extrema,
measurement uncertainty intervals or a multi-year climatology. An axis normal
is not independently verified as the velocity normal. Ocean connectivity is
not established. The source's unflagged boundary fallback and110km smoothing
remain limitations. Fallback occurrence, threshold attainment and physical
uncertainty stay null. No physical width inventory/rank/state passage is admitted.

## Reproducibility and visual checks

Protocol: plans/kuroshio-axis-normal-width-protocol-v1.md. The declaration
predates the new intersections, following prior exposure to the source curves
and latitude results. It is exploratory. Initial-azimuth/subdivision wording
was clarified during implementation review without changing calculations or
thresholds. All first-pass span values, statuses and IDs survive exactly.

The complete report rebuilds byte-for-byte from the pinned original:
22,088,514 bytes, SHA256
9e0c4cbbd62426c68aa29c45149106fbdbf52ed2ca159b852c912f5572a13346.
The provider original, compressed archive, license and metadata are unchanged.
Independent source-coordinate readbacks, forward-geodesic checks and a
spherical-distance comparison cover every14,034 resolved result. Original-source
normal reconstruction retains the strict0.001m numerical check. Printed-geometry
checks account separately for coordinate/bearing rounding; neither is physical accuracy.

The standalone SVG shows monthly available-sample ranges and dated July1
maps at all three depths. Actual geodesic normals and old latitude cuts have
different styles. Missing curves remain broken; unresolved normals are marked.
The figure uses an equirectangular24N display and separate cartographic land
context. It does not draw an occupied-width ribbon or a physical footprint.
The original source figure imagery is not redistributed.

41 focused tests and12 subtests pass (19 new checks,22 previous Kuroshio checks).
Figure bytes reproduce, and its input/figure hashes are in a separate receipt.
Actual browser rendering was inspected; serif fallback and footer overlap were
corrected, and gate colours have >=4.5 contrast against white and ocean fill.
Scientific reconstruction is registered as target23. Linux execution for this
new head is a separate gate. The first Linux run at c4978a2 reproduced every
span and status but found27 last-digit bearing/coordinate differences around
1e-9 degrees. Canonical exports now use7 coordinate decimals and6 bearing
decimals; source fractions retain9. Unrounded intersections/acceptance and all
span values/statuses/IDs remain unchanged. The exact-byte gate is retained.
At9b335cb, the prior22-report scientific job and
NetCDF job passed; offline acquisition failed on the existing Rotschi1972 PDF
HTTP403 before tests. A fresh complete default-suite pass is not claimed.

At93a854b12b4bf959ff12578bf07bb706e6274902, scientific job119438106105
(run39662272663) passed all23 report reconstructions byte-for-byte, including
the canonical normal-span report. NetCDF job119438106584 passed. The following
documentation checkpoint changes no scientific input or artifact bytes.

## Reproduction commands

```
python analysis/kuroshio_axis_normal.py
python analysis/build_kuroshio_axis_normal_figure.py
python -m pytest analysis/test_kuroshio_axis_normal.py analysis/test_kuroshio_wang_dimensions.py analysis/test_kuroshio_wang_query.py -q
python analysis/inspect_scientific_reproduction.py
```

## Required next integration

Add all16,470 attempts as an explicitly typed native/WASM collection, with
source/report pointers and stable IDs. Bind the complete scientific report
and figure receipt. Keep the existing6,588 regional-length/latitude-span rows
unchanged. Extend the shared Kuroshio map/card/seasons component to select the
normal metric and tangent convention using its existing date/depth controls.
Expose coverage, monthly ranges, unknowns, normal geometry and source queries.
Validate native/WASM parity, source corruption rejection, shared selections,
keyboard/reduced-motion/narrow layout and one-owner dashboard fingerprints.

Do not claim this source report is already in the main atlas or count it as
new physical width inventory coverage. The six entries still lacking scoped
width records need additional source/identity work. Existing main bundle
bytes, inventories, historical release and previously admitted measurements
remain intact; the new source is additive and scientifically qualified.

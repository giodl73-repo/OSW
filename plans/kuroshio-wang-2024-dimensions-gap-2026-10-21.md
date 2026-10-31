# Kuroshio daily regional dimensions: source extraction batch

Base commit:abd5eb61378bed8e1e49ba49c6460012f2256bbc. Continue branch
`codex/current-measurement-gaps` and draft PR83. No new PR or main merge.
This advances the active full core-data/info/visualization goal; it does not
complete the goal or replace the remaining work with this report.

## Evidence and acquisition

New primary source: Wang, Chen, Mao and Zhang (2026),
[Scientific Data](https://doi.org/10.1038/s41597-026-07275-3),
[dataset edition1](https://doi.org/10.6084/m9.figshare.30267070.v1), CC BY4.0.
The provider publishes1993–2024 daily axes and left/right boundaries from
GLORYS12V1, with30 nominal depth levels. This source was absent from OSW.

Selected2024 before extraction as the latest complete year. Retain the entire
130603298-byte original, provider MD5/SHA256, all366 day groups and30 depth
groups, metadata, and the provider plotting example. The versioned gzip copy
is84838372 bytes and reproduces the exact original bytes. No source plotting
program is executed; the producer reads the original in memory and needs no
network or second uncompressed disk copy. Existing originals are retained.

The protocol predates extraction. Extract0.49,109.73 and380.21m nominal levels;
check the complete source inventory but do not claim measurements at all30
levels. The other31 years and27 levels remain work. The30% boundary criterion
can fall back to a valid search-window edge; no fallback flag is encoded.
Smoothing and potential censoring are limitations, not numerical uncertainty.

## New numerical data

Every one of1098 declared daily/depth cases and5490 section cases is retained.

| Result | Resolved | Unresolved and retained |
|---|---:|---|
|18–30N regional model-axis length |908 |61 long source segments;129 missing/multiple gates |
| Fixed-latitude boundary span |4976 |76 long segments;438 missing/multiple intersections |

Lengths use unique source-coordinate gate intersections and WGS84 segment
lengths. Sections18.5,21.5,24.5,27.5 and29.5N use unique intersections with each
independent curve, not source array-index pairing. These spans can be oblique
to flow and exceed the source140km normal-transect length; no value is clipped
or relabeled as a perpendicular width. Missing vertices never reconnect.

For example, the0.49m regional axis has314 valid dates of366, with an empirical
2024 length span of about1580–1890km. At24.5N the same level has304 valid dates,
with section spans about70–150km. These are different quantities/supports,
not whole-current dimensions, physical annual extrema, confidence intervals or
measurement error. Other levels and sections remain separate in the report.

All daily outcomes and39 level/month-or-year summaries are retained. Thirty-six
display frames use the predeclared first day of each month at three levels;
they are not monthly means. The source30% boundaries remain potentially
search-censored, including in otherwise geometrically resolved cases.

## Visual artifact and verification

`figures/kuroshio-wang-2024-monthly-snapshots.svg` presents twelve dated0.49m
maps, with the separate source axis/left/right curves, fixed gates, unresolved
readbacks, source attribution and limits. Missing geometry breaks lines. Line
patterns supplement color. Equirectangular display and public-domain Natural
Earth1:10 million v5.1.1 context are explicit. No buffered occupied polygon.
The numerical JSON is the textual data alternative. No new interactive page
or phone-layout behavior is claimed for this standalone scientific figure.

Sixteen focused tests pass, including byte-exact original/full numerical
reconstruction, leap-year/depth coverage, fixed gates, oblique geodesic span,
independent arrays, ambiguous crossings, missing geometry, connectivity guards,
denominators, nonpromotion flags and exact SVG reconstruction. The reconstruction
inspector gains a22nd report. Report independent new-head CI separately.

Atabd5eb6, the independent21-report reconstruction and NetCDF fixture passed.
Offline CI failed before tests on the existing Rotschi1972 IRD PDF HTTP403.
The last full local Python baseline remains774e466:1910 tests/1222 subtests;
the current disk guard prevents another complete local suite. Focused tests
and a source report do not replace those complete integration gates.

## Required continuation

Working catalogue101, pending proposals28, source-reported ranked lengths12,
scoped widths157/83 owners, reference candidates77/71 owners and dashboard241
objects remain unchanged. This report is not yet in native/WASM query data,
current cards, atlas selection or seasonal playback. Those are required next
integration work, with typed model/regional/section scope and missing-case
coverage visible. Preserve historical release and every existing owner.

Then extend acquisition/extraction to the remaining years/levels, establish
appropriate uncertainty and validation support, and continue other currents'
missing dimensions, routes and source-supported state relations. This is one
source/extraction milestone within the full objective, not program completion.


Publication evidence:16 focused tests pass on the final producer/report,
including byte-exact numerical reconstruction. The final twelve-panel SVG was
rendered at1200x1390 and visually inspected; date/depth/gates, redundant line
patterns, unresolved values, source/limits and coordinate labels are legible.
All17 staged input/output/source/review blobs match workspace bytes, including
the compressed original. Staged whitespace passes. Shipped almanac/query/Rust
files and all existing inventories remain byte-unchanged fromabd5eb6. At that
head, scientific21-report job119271231298 and NetCDF119271231685 passed;
offline119271230625 failed before tests on the existing Rotschi1972 HTTP403.

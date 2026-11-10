# EAC calendar-distribution data and visualization

Continues `codex/current-measurement-gaps`, draft PR #83. No new PR or main
merge. This fills missing calendar summaries of the existing local section
diagnostic; it does not claim to close the physical current-width gap.

## Added data

The unchanged CSIRO v2.3 100 m dated section-span report contains 3,770 source
dates from 2012-04-01 through 2022-07-27. All dates and all nine original
scenario/threshold cases are retained. New outputs describe twelve pooled
calendar-month groups and eleven separate calendar-year groups: 207
conditional distributions, with minimum, 10th percentile, median, 90th
percentile and maximum. Empty resolved sets retain null statistics.

The existing primary central/50% case resolves 2,883 dates and leaves 887
unresolved. No new independent observations or velocity-derived spans were
created by grouping them. Each distribution retains outcome counts,
contributing year-month support and source-profile indices. Month support
includes full-calendar denominators and partial-month flags. Annual support
distinguishes the partial 2012/2022 endpoints and preserves the all-unresolved
2014 diagnostic instead of drawing a zero-width observation.

The protocol fixes type-7 linear quantiles using decimal arithmetic and
0.001 km calculation readbacks. It does not change any original daily span,
projection, threshold, velocity cutoff, missingness or boundary. Pooled months
weight resolved mapped dates equally, with unequal year support. They are
not equal-year climatologies or physical seasonal widths. Filtering, SOM
filling, dependence and possible selection by failed bracketing remain explicit.

## Visualization and access

An independent SVG/PNG compares the primary month and year distributions.
Thin min/max segments, thick 10th–90th percentile segments and median points
have explicit resolved/attempted labels. These segments are not confidence
intervals, measurement errors or physical annual ranges.

The EAC map card, seasons view and diagnostic view gain a disclosure with the
comparison, full-size figure and exact source-query links. The dashboard EAC
entry links to the same figure and monthly data. Both new JSON documents are
in the checked native/WASM source corpus. No footprint or width band is drawn.

## Verification

- Nine focused data tests pass, including independent NumPy quantiles for every
  nonempty distribution and support checks for all207, complete date partitions, leap-year/partial-month support,
  null-only groups and seven corrupt date/case/value rejection cases.
- With the browser runner environment checks: eleven tests / two subtests pass.
- The figure was visually inspected. JavaScript syntax and whitespace checks
  pass (CR-at-EOL is accepted for existing Windows-generated text files).
- All 79 Rust tests, locked native/WASM builds and actual native atlas loading
  pass. Main packet: 90,252,981 bytes; WASM: 16,853,788 bytes.
- The index has 380 documents, 275,504,213 original bytes and 43,383,633
  compressed bytes. All 378 pre-existing source descriptors remain exact.
- Preservation against9409140 proves all44 other query collections and239
  other object rows unchanged. The dated input report retains its original
  SHA256. Widths155, samples463, routes76 and series28 remain unchanged.
- All648 unique staged source/build blobs match their dependency pins,
  including126 engine inputs and380 indexed documents.

The EAC calendar browser gate PASSED: both complete month/year source results
match native Rust and actual browser WASM exactly, retaining all nine cases per
group. The comparison renders on map-card, seasons and diagnostic views, with
full-size/source navigation, export and320px mobile reflow. No source originals
were requested and no page errors occurred.
The isolated full suite at8399af0 remains live; it predates this addition and
cannot certify it. Do not restart or overwrite that running checkout/CLI.

The preceding scientific-readback browser wrapper is terminal PASS: all six
shared views and56 corruption rejections, plus all three dedicated Loop views,
all54 contour cases,11 packet and2 index corruption rejections. Its original
receipts are preserved separately from this addition's gates.

## Reproduction

```powershell
python analysis/build_eac_calendar_distributions.py
python analysis/build_eac_calendar_distribution_figure.py
python -m pytest analysis/test_eac_calendar_distributions.py -q
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python analysis/test_eac_calendar_browser.py
```

The active core-data objective remains open. This is local source-diagnostic
evidence; independent scientific and canonical physical-width admission,
whole-current dimensions and geographic seasonal margins remain unresolved.

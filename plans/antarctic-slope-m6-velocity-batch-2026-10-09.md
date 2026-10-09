# Antarctic Slope Current: local observed velocity batch

This batch fills a local seasonal velocity gap using Darelius, Janout, Fer and
Sallée (2024), [PANGAEA.964717](https://doi.pangaea.de/10.1594/PANGAEA.964717),
CC BY 4.0. It retains the complete licensed source unchanged inside gzip.

The released nominal 228 m ADCP bin supplies 16,393 paired readings at M6,
east of Filchner Trough, between February 2017 and February 2021. OSW derives
49 calendar-month means and 12 equal-year seasonal composites. Each record
retains contributing years, paired counts, expected hourly slots, coverage,
partial-month status, units and unresolved measurement uncertainty.

The shared Rust store serves `current_velocity_samples`; native and WASM use
the same source-bound records, chart axes and fixed station map. Query results
retain the full matching chart across pagination. The atlas current card links
to the charts; query owner records expose the collection join. Playback highlights
discrete readings and honors reduced motion. It does not animate geographic flow.

## Measurement limits

Geographic U/V means are OSW aggregations, not a reproduction of the article's
rotation, interpolation or filtering. Released depth bins differ from
[Darelius et al. (2024), Table 1](https://doi.org/10.1029/2023JC020666);
no correction is imposed. Source timestamp timezone is unspecified. Missing
hours remain missing, and uneven sampling can bias monthly means. Seasonal
whiskers show between-year spans of monthly means, not confidence intervals.

The batch does not establish current width, length or occupied area. Numeric
width coverage remains 114 scoped descriptions across 62 owners; the Antarctic
Slope width decision still awaits a separate inventory source review. Whole-current
length gaps and most named-eddy footprints also remain open.

## Reproduction

Run from repository root:

```powershell
python analysis/build_antarctic_slope_m6_velocity.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python -m pytest -q
python analysis/test_antarctic_slope_m6_velocity_browser.py
python analysis/test_rust_collection_coverage_browser.py
```

Browser checks use the existing checkout server on port 8788 and the established
`OSW_TEST_BROWSER` override where necessary. Builds are serialized. The broader
stack also requires its existing local paper fixtures; this new dataset requires
no provider access after checkout.

Publication is a draft above PR #70, subject to validation. At this receipt's
initial writing, PR #70's push CI failed acquiring Qiu/Chen's existing paper
after three timeouts; its companion CI was exercising shipped browser checks.
Neither that failure nor the companion's eventual result is evidence of a
completed mainline merge.

## Final local validation receipt

- Full Python suite: 1,177 tests and 918 subtests passed in 502.77 seconds.
- Focused source/aggregation/native mutation tests: all three passed; the native
  guard test was added after full-suite collection and verified separately.
- Native Rust: 41 tests passed; serialized native and WASM builds passed.
- M6 browser: native/WASM parity, 320 px layout, signed fixed axes, reduced
  motion/playback, six source mutation rejections and atlas navigation passed.
- Generic browser coverage: all 40 collections, both end pages, record inspection
  and 240 object map marks passed.
- All 49 JavaScript files, all 14 page assignments and staged whitespace checks passed.
- Source index: 138 documents; engine 2,157,856 bytes; query bundle 46,509,003 bytes.

These are local results. Remote CI and mainline publication remain unverified.

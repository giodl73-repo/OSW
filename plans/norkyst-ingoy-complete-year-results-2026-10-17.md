# Complete 2024 temporal support for the Ingoy model region

Continues the existing current-gap branch and draft PR 83. This completes the declared calendar-year source acquisition and research analysis. Shared current/query UI integration and physical current-dimension assessment remain separate outstanding work.

## Source and temporal coverage

| Evidence | Retained result |
| --- | ---: |
| Daily archive requests, including endpoints | 370 |
| Original hourly fields, including 36-hour global halos | 8,856 |
| Complete 2024 calendar hours | 8,784 |
| Fixed source locations | 2,400 |
| Source space-time grid samples | 21,254,400 |
| Missing or nonwet selected source samples | 0 |
| Original year ZIP archives / original members | 14 / 740 |
| Complete monthly numeric assets | 12 |
| Fixed section positions per hour | 191 |

The source timestamps run from 30 December 2023 at 12:00 UTC through 2 January 2025 at 11:00 UTC. The extra dates are filter support, not additional months in the 2024 result. February retains all 696 calendar hours, including leap day. Other months retain their actual 720 or 744 hours. All 191 section positions have complete raw and low-pass support in every month.

The year original archives contain 96,052,360 bytes. The twelve monthly NPZ assets contain 73,394,952 bytes in total; the largest is 6,260,142 bytes. The numeric assets use the same deterministic NPY/ZIP writer as the two-month capsule. Original bytes are pinned exactly; reproducibility checks allow only tight floating-point differences in derived values. No refresh occurs during default analysis or tests.

## Continuity and independent checks

All twelve earlier fifteenth-day noon readings match every one of their 2,400 original packed cells and sea masks. All 70 dates in the two-month capsule are checked against the year acquisition. Where hourly cuts differ, the actual overlapping timestamps and all original field/mask values must agree; a daily metadata match alone is insufficient.

The new year reader reproduces the January/July capsule without overwriting it. The complete-year test reconstructs every monthly asset, mean, population standard deviation and sample quantile from all originals, and compares the native regional means and their support counts. Additional checks cover missing/duplicate requests, changed overlaps, chronological presentation, missing filter support, and projected vector directions/magnitudes.

**27 focused tests and 20 subtests passed in 76.85 seconds.** The earlier clean combined UI gate at 8130086 passed 1,619 tests and 1,061 subtests; it predates this research and is not represented as its combined gate.

## New data and views

- `section-diagnostic-year.json`: all twelve monthly section summaries, methods, units, support, dates, source pins and asset references.
- `section-hourly-year-2024-MM.npz`: one selectable month at a time, with actual UTC timestamps, raw/low-pass velocity and salinity, coordinates and preserved missing values.
- `regional-monthly-means-year.json`: complete-calendar raw/low-pass native source-cell means, support counts, geographic coordinates, plotting coordinates and rotated mean-velocity glyphs.
- `figure-year.json`: reproducible figure links/checksums and their analysis/projection dependencies.
- Three scientific figures: year section means, within-month temporal variability, and twelve monthly regional maps. Numeric data and SVG title/description accompany each view.

The regional low-pass mean uses the exact linear composition of the temporal filter and monthly averaging window. It requires every positive-weight source hour and does not renormalize around gaps. Independent tests compare it with explicit filtering/averaging and bilinear projection of the complete-month section means. This shortcut is not used to estimate filtered variances or quantiles.

Maps retain the source polar stereographic grid and 3.2 km sampled spacing. True east/north mean velocities are rotated with the established 1 km geodesic-probe convention. A common salinity scale and arrow scale apply across all months. The orange line is the fixed 24 E section, not a current axis. The selected patch has no coastline; its boundaries are sampling limits.

## Scientific limits

These are Norkyst v3 model fields at the source 10 m depth coordinate, not observations or a depth average. A single calendar year is not a seasonal climatology. Low-pass filtering attenuates tides and other high-frequency variation; it does not identify a complete harmonic tide solution. Serial dependence remains. Temporal standard deviations and sample quantiles are not confidence intervals, measurement error or physical width uncertainty.

The results establish complete temporal support for this selected model patch and section. They do not establish physical current identity, coastal coverage, paired current boundaries, whole-current length/width, state containment or annual physical width extrema. The 149 scoped width records across 79 owners are unchanged. No existing route, model snapshot, two-month artifact or scientific measurement is overwritten.

## Reproduction

```text
python analysis/fetch_norkyst_ingoy_continuous.py --all-months
python analysis/build_norkyst_continuous_year.py
python analysis/build_norkyst_continuous_year_figures.py
python -m pytest analysis/test_norkyst_continuous_source.py analysis/test_norkyst_continuous_sections.py analysis/test_norkyst_continuous_acquisition.py analysis/test_norkyst_continuous_year.py -q
```

Acquisition is explicit network work. Analysis uses the committed originals. Use the new complete-year builder above for the monthly assets, native means and chronological report; the earlier two-month builder remains preserved as its producer version. Reference environment: Python 3.14.2, NumPy 2.4.1, pyproj 3.7.2, Matplotlib 3.10.8. Source data are CC BY 4.0 Norkyst v3 hindcast subsets from MET Norway and the Institute of Marine Research. Independent OSW transformations and plots retain attribution; no publisher figure is redistributed.

## Next integration

Register the research and source documents, expose the year in the shared Rust/current/query views, and add month/field/raw-versus-low-pass controls with numeric alternatives and explicit model scope. Keep the 296-source/45-collection/40-diagnostic baseline distinct until that integration is actually built and verified. Then run the combined integration/release gate. No additional PR or main merge is authorized by this checkpoint.

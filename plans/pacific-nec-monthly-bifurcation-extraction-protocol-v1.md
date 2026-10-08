# Pacific NEC monthly branching extraction — protocol v1

Status: editorial extraction protocol, 2026-10-07. Metric: regional branching latitude in signed degrees north. Apply E01–E05 and M01–M13 before any later route or dimension admission.

## Source and selection

Use the checksum-pinned author copy of Qiu and Chen (2010), DOI 10.1175/2010JPO4462.1, figure 2b on printed page 2528 (page index 3). Preserve the original as an ignored local fixture and acquire it explicitly; do not download during offline tests. Use the pinned PyMuPDF environment.

The visually inspected lower panel plots calendar-month means as a dark thick polyline and a light gray filled polygon as a standard-deviation range. Select exactly one 23-segment, 24-vertex mean polyline and one 47-segment, 48-vertex band polygon using the declared rectangle, stroke thickness and color bounds. Exclude individual plus symbols, axes, the duplicate band outline and the upper panel's dated/filtered curves.

The x axis covers 24 month bins from January through December twice. Vertices sit near the middle of their bins. Validate every mean vertex against its expected bin center rather than assigning months from arbitrary path order. Require each band boundary to match the mean's x coordinate. Require exactly two boundary vertices per month, band containment of the mean, and near symmetry within 0.005 degree. Require repeated means and both band boundaries to agree within 0.002 degree. Keep one 12-month cycle; repetitions are not distinct observed years.

## Calibration and reading allowances

Visually verified panel bounds: x=159.882 to 438.933 PDF points; y=251.992 is 18 degrees north, y=413.188 is 8 degrees north. Convert each mean and boundary vertex with the same linear latitude calibration. Retain original mean and boundary coordinates and raw transformed values. Display each independently to 0.1 degree, with exact half ties away from zero. Do not reconstruct rounded bounds by adding a rounded deviation to a rounded mean.

Attach a separate +/-0.1-degree editorial graph-reading allowance to each displayed mean and each displayed band boundary. This allowance covers graph interpretation and rounding. It is not physical variability, instrument error, grid resolution or a confidence interval. Do not add it to the source variability band to claim a statistical coverage probability.

## Interpretation and missing support

Figure 2's caption identifies the band as a standard-deviation range. Preserve that source label. The caption does not specify a statistical denominator, multiplier, averaging weights or a confidence probability; leave these unknown rather than infer them from symmetry. Do not treat the band as annual extrema, the limits of all observations, or a future prediction interval.

The surface geostrophic diagnosis uses monthly averaged altimeter SSH over October 1992–December 2009. Preserve that historical source period and layer. Individual plus-symbol observations, monthly sample counts and observation-year assignments are not extracted by this protocol. No longitude or current boundary is supplied by this scalar plot.

## Admission and reproduction

Keep geometry, whole-current length, current width and annual dimension range null. Ranking, annual-extrema and geographic-playback eligibility remain false. Chart playback may display the monthly scalar evidence with its distinct band/allowance labels. The Pacific North Equatorial identity remains a basin-member inventory proposal.

```powershell
python analysis/acquire_local_paper_fixtures.py
python analysis/build_pacific_nec_monthly_bifurcation.py
python -m unittest discover -s analysis -p test_pacific_nec_monthly_bifurcation.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python analysis/test_rust_index_store_browser.py
python analysis/test_rust_index_page_browser.py
python analysis/test_rust_source_query_browser.py
```

The checked source workspace can query `research/pacific-nec-monthly-bifurcation-extraction.json` at `/series/0/months`. The existing Indian chart's typed API is not extended by this data-only candidate. Required CI and scientific review remain separate gates.

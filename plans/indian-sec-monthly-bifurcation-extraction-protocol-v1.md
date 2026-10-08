# Indian SEC monthly bifurcation extraction — protocol v1

Status: editorial extraction protocol, 2026-10-07. Metric: regional branching latitude in signed degrees north. This is not a current dimension or a route measurement.

## Source and selection

Use the checksum-pinned university copy of Chen et al. (2014), DOI 10.1175/JPO-D-13-0147.1, figure 3 on printed page 621. Read page index 3 with the pinned PyMuPDF runtime. Preserve the original PDF in the ignored local fixture directory and record its retrieval URL and checksum. Acquire explicitly with `analysis/acquire_local_paper_fixtures.py`; do not fetch during offline tests.

Select four-Bezier filled circular markers with width/height between 5 and 6.5 PDF points inside the declared plot rectangle. Use gray for the surface SSH diagnosis and red for WOD09 upper-400-m geostrophic flow. Exclude the blue model series because its 400/415-m layer correspondence remains unresolved. The rectangle excludes legend markers.

Deduplicate coincident paint operations by marker-center coordinates rounded to five PDF-point decimals. Sort markers by increasing x. Require exactly 24 markers per selected series: two plotted repetitions of a 12-month January–December cycle. Compare corresponding latitudes within 0.002 degree and retain one cycle; never call the repetitions two observed years.

## Calibration and display

Use visually verified latitude ticks: y=68.711 PDF points is -15.2 degrees north; y=218.825 is -18.8. Convert marker-center y by linear interpolation. Retain raw transformed values and marker centers for reproduction. Display to the nearest 0.1 degree, with exact half ties away from zero.

Attach a +/-0.1-degree graph-reading allowance to displayed values. This editorial allowance covers graph interpretation and rounding; it is not source sampling error, physical variability or a confidence interval. It does not imply that the underlying hydrographic grid resolves locations to 0.1 degree. The source variability envelope and monthly averaging weights are not extracted.

Preserve the surface SSH support interval October 1992–December 2011. Keep WOD09 contributing observation dates missing rather than borrowing the satellite interval. These are historical monthly cycles, not dated current snapshots.

## Admission restrictions

Retain null geometry, whole-current length, width and annual dimension range. Keep ranking, annual-extrema and geographic-playback eligibility false. The scalar series may support chart playback. It cannot define longitude, an upstream gate, a route axis, geographic edges or changing current width. Apply E01–E05 and the existing M01–M13 rules before any later map/length/width admission.

## Reproduce and verify

```powershell
python analysis/acquire_local_paper_fixtures.py
python analysis/build_indian_sec_monthly_bifurcation.py
python -m unittest discover -s analysis -p test_indian_sec_monthly_bifurcation.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python analysis/test_rust_index_store_browser.py
python analysis/test_rust_index_page_browser.py
```

The output is available through the checked source store at document `research/indian-sec-monthly-bifurcation-extraction.json`, pointer `/series`. Required publication CI and internal source/presentation review remain separate from scientific admission.

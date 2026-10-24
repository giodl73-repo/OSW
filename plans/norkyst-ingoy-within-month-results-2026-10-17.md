# Continuous Ingoy sections: first complete months

Research stage on the existing current-gap branch/PR 83. This report does not admit a physical current width or a seasonal width range.

## Retained results

| Quantity | January 2024 | July 2024 |
| --- | ---: | ---: |
| Complete calendar hours | 744 | 744 |
| Acquired hours including filter halo | 816 | 816 |
| Fixed section positions per hour | 191 | 191 |
| Raw and low-pass support at every position | 744 / 744 | 744 / 744 |
| Earlier day-15 noon reading | All 2,400 packed grid cells match | All 2,400 packed grid cells match |

Seventy daily requests retain 1,632 distinct model timestamps and 3,916,800 source grid positions, each with salinity and two velocity components. No selected source position is nonwet or missing. This is the selected offshore patch; it is not complete spatial coverage of the Norwegian Coastal Current.

Six deterministic ZIP archives retain 140 original field/metadata members, each with an individual byte pin. The parsed monthly section asset retains 1,488 core hours and both raw and low-pass fields in a standard NPZ container. The JSON report supplies every section position's support count, mean, population standard deviation and 5th/50th/95th hourly-sample quantiles. Those quantiles describe model temporal variation, not uncertainty bounds or confidence intervals.

The figure compares the two continuous months with the previously retained single-hour readings. Total and low-pass heatmaps use the same symmetric velocity scale across both months. Profiles and salinity use common comparison axes. The dashed heatmap line identifies the earlier reading; it is not a current boundary. The figure has SVG title/description, a source caption and an accompanying numeric report/asset.

## Method and provenance

The unchanged original sampling declaration is `plans/norkyst-ingoy-within-month-support-2026-10-17.md`, with its frozen JSON preflight. The local declaration preceded new within-month field acquisition. Its first version-controlled publication also contains acquired data; no external preregistration or independent timestamp proof is claimed. The twelve older snapshots had already been viewed, as stated in the declaration.

The first-day January/July metadata came from the metadata-only probe. Its recorded batch-completion time is an upper bound; individual response times were not retained. The acquisition receipt labels that time basis explicitly rather than using the later cache-copy time. Other originals retain their first response completion times. Revalidation preserves source pins and acquisition times.

The filter is an explicitly defined convolution of 24-, 24- and 25-hour boxcars, with 71 weights and 35 hours of support on each side. The 36-hour acquisition halo leaves one additional unused hour at each end. Filtering does not cross missing data or the January–July gap. It attenuates tidal bands and other high-frequency variability; it is not a harmonic tide solution. All source fields remain model results.

Original source bytes must match exactly. Derived floating arrays are compared with a small numerical tolerance (1e-11 in source units) across numerical environments; displayed summary comparisons allow one unit in their eighth decimal place. These are reproducibility tolerances, not physical uncertainty. Rebuilding twice in one environment must preserve derived asset and SVG bytes. Default tests inspect retained originals offline and do not refresh sources or overwrite the retained derived asset.

Reference build environment: Python 3.14.2, NumPy 2.4.1, pyproj 3.7.2 and Matplotlib 3.10.8. NumPy and pyproj match the existing geography/projection requirements. The plot is an independent OSW rendering of CC BY 4.0 Norkyst data, with attribution; no publisher figure is redistributed.

## Commands

```text
python analysis/fetch_norkyst_ingoy_continuous.py
python analysis/build_norkyst_continuous_sections.py
python analysis/build_norkyst_continuous_figure.py
python -m pytest analysis/test_norkyst_continuous_source.py analysis/test_norkyst_continuous_sections.py -q
```

The first command is an explicit network acquisition/revalidation. The analysis uses the local original archives. `--all-months` on acquisition and analysis is the next stage, under the existing twelve-month declaration. A twelve-month figure needs its own reviewed layout; the two-month figure must not silently omit ten months.

## Remaining work and release scope

Acquire the other ten months and retain the same temporal/source checks. Then add the complete temporal support and its visualization to the shared query/current UI. Current association, coastal/spatial coverage, paired physical boundaries, obliquity and a width operator still require review before a current-width or annual-range claim.

The published inventory remains 149 scoped width records across 79 owners. The 296 indexed documents, 45 collections and 40 diagnostics are unchanged by this research preparation. Existing routes, map features, figures, hourly readings and seasonal frames are unchanged. These new research files are not yet registered or compiled into the UI.

The separate clean 1,619-test gate runs at 8130086, before this research addition. Its result cannot be represented as coverage of these new tests. Dedicated source/filter/reproduction checks cover this preparation; the rolling branch still needs the eventual combined release gate.

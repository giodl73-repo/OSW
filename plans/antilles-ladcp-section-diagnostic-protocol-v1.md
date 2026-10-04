# Antilles observed-section diagnostic protocol v1

Status: derived local diagnostic requiring scientific review. This does not
admit a canonical width or modify the current measurement inventory.

## Source, sampling and units

Acquire only the NOAA/AOML AB0505 final LADCP velocity directory and assessment
readme, with original bytes, URL, acquisition time and SHA256 per file.
Default regeneration is offline; `--acquire` explicitly downloads a new initial
snapshot and refuses to replace an existing pinned manifest.

Provider headers declare depth in meters and velocities/error velocity in cm/s.
Convert velocity components to m/s by division by 100. Keep UTC average cast
times; they are not occupation start/end times. Retain all metadata and tide
removal status (`no`). Do not equate 400 m with 400 dbar. Unexpected units,
malformed samples, nonmonotonic depth or undocumented sentinel-like velocities
stop parsing for review.

Source readme and file headers name the LADCP processing package differently
(IMF-GEOMAR versus LDEO) at version 10.8. Preserve both names. No exact original
software environment is claimed.

## Geography and quality

By date and position, casts 1–23 match the first Abaco occupation on May 4–8,
2005; casts 37–63 match the repeat on May 18–23. Meinen et al. (2019), Table 2,
provides occupation context. Casts 64–70 belong to other cruise sections and
are excluded. Casts 24–36 have no LADCP data according to the provider; they
are not zero-velocity profiles. These ranges are a local membership assignment
requiring independent review, not a universal mapping for other cruises.

Keep provider caution profiles in the inventory and graph as separate crosses.
Exclude them from numerical boundary walking; do not fill their gaps. Error
velocity is retained but is not assumed to be a Gaussian uncertainty, nor does
the provider's usable label guarantee a precise width.

## Fixed-depth one-sided diagnostic

1. Select the exact 400 m depth sample from each cast; no vertical extrapolation.
2. Order casts west to east. Independently for each occupation, find the largest
   positive northward velocity among provider-usable samples.
3. Set the boundary threshold to half that sampled peak. This is an OSW
   exploratory threshold, not a source-defined physical edge.
4. Walk eastward from the sampled peak. Stop unresolved on a missing/caution
   cast or at the section end. Never bridge a gap or skip an intervening cast.
5. At the first bracket, interpolate latitude and longitude linearly by velocity
   fraction; use WGS84 geodesic distance from sampled peak to crossing.
6. Retain both bracketing cast IDs and their distances from the sampled peak.
   Their approximately 35–50 km span is station support, not a confidence
   interval, extrema or propagation of velocity errors.

The first occupation is unresolved under these gates. The repeat produces
37.352311 km before display rounding to about 37 km. The nearshore boundary
is not diagnosed; the shallowest inshore cast has no 400 m sample. The sampled
peak may not be the true cross-current core. Do not double this span, call it
full width, assume exact flow-normal orientation or apply it along the current.

## Time and admission boundary

Several days compose each section; neither is an instantaneous whole-current
snapshot. Both occupations occurred in May. No seasonal phase animation,
annual minimum/maximum, along-current length or ranking is justified.

Before measurement admission: independently review membership and parsing,
unremoved tides, velocity errors, threshold sensitivity, sampling sufficiency,
sampled-peak representativeness and both depth-compatible boundaries. Along-
current axes and annual coverage remain separate requirements.

## Regeneration and checks

```powershell
python analysis/acquire_antilles_ladcp_profiles.py --acquire
python analysis/build_antilles_ladcp_section_diagnostic.py
python -m unittest discover -s analysis -p test_antilles_ladcp_diagnostic.py
```

After initial acquisition, omit the acquisition command: the diagnostic builder
checks pinned bytes and regenerates inventory, calculation and Matplotlib SVG
offline. Matplotlib 3.10.8 and pyproj WGS84 were used for this local run.
Use `analysis/test_antilles_sections_browser.py` with `OSW_TEST_BROWSER` set to
an installed Playwright-compatible Chromium executable for presentation checks.

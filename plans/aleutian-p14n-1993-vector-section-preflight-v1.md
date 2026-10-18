# Aleutian/Subarctic Current: P14N observed section preflight

Declared before inspecting the newly acquired velocity fields. Metadata and Chen and Firing (2006), doi:10.1029/2005JC003064, were consulted first. Continue the same branch and PR #83.

## Question and source

Can archived, directly measured shipboard vector velocities resolve the two Subarctic Current branches on WOCE P14N in July 1993? The existing 2013 OSCAR monthly component diagnostic does not answer this observational question. JASADCP identifies cruise TT9306/P14N, EXPOCODE 325023_1, SAC_ID 00016, Thompson, Gunnar Roden; data cover 29 June–11 August 1993. Provider metadata describe 153 kHz RDI acquisition, four-metre native bins and five-minute ensembles, editing, gyro calibration and GPS selective availability. The reduced product is nominally hourly with ten-metre depth levels. Retain its exact representation and missing values.

Primary archive gateway: <https://uhslc.soest.hawaii.edu/sadcp/DATABASE/00016.html>. Acquire the reduced NetCDF, original provider cruise metadata, format description and gateway bytes, with URLs, retrieval time, hashes, byte lengths and acquisition-code identity. Do not replace earlier raw data or change definitions after seeing the new values. This is one dated ship transect, not a seasonal climatology.

## Fixed analysis choices

- Source association follows the paper's northern and southern Subarctic branches near 45 N and 42 N. Keep the Alaskan Stream and Aleutian North Slope Current distinct.
- First display the entire observed 40–48 N meridional reach, restricted to 7–18 July 1993 and longitude 178–180 E. Preserve original sample timestamps, positions, both velocity components, depth support and missing masks. Windows are selection support, not measured geographic edges.
- Use the paper's 100–300 m layer for a primary vector-section comparison. Compute a depth-thickness weighted layer mean only where at least 80% of that layer has valid joint u/v support. Require monotone depth coordinates and verify provider units before conversion. Do not substitute magnitude for eastward velocity or mix independently valid u/v supports.
- Record native sample spacing, maximum gaps, temporal order and track heading. Do not average a transit leg together with another crossing, interpolate across missing samples, or silently use a nonmonotone transect.
- Northern and southern branch search windows are 44–46 N and 41–43 N respectively, fixed from the cited paper before field inspection. Do not expand or shift these windows to obtain a preferred result.
- Any later diagnostic half-peak span must retain both crossing brackets, spacing sensitivity, source dates and the actual along-track orientation. A missing boundary is unresolved, not zero. Two branches must not be collapsed into one scalar by summing widths or filling intervening water.

## Admission and visualization

First deliver the observed vector section, acquisition/provenance, validity counts and branch-association limits. No physical current width, whole-current dimension, annual extrema, confidence interval, mapped ribbon or observed edge geometry is admitted by source acquisition alone. Do not promote an eastward velocity lobe to a named cold Subarctic branch without checking water-mass correspondence and separation from adjacent jets/eddies. Recover matching CTD support if required. Preserve all 155 earlier scoped measurements and the existing OSCAR diagnostic.

The UI should show both components against latitude and source dates, with layer coverage and a numeric alternative. Use a regional sampling-track map as context only. A spatial section is not an animation through the year. Keep unknowns visible and make the actual original and extracted records inspectable.

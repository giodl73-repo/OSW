# Monthly regional field maps from the continuous acquisition

Extension of the frozen within-month sampling rules, declared before computing the new regional monthly maps. The two-month section results and earlier twelve instantaneous field maps have already been viewed, and the year downloader has read additional hourly field values. No fully blinded or externally preregistered map analysis is claimed.

## Fixed quantities

Use the same 48 by 50 retained source patch, 10 m layer, 2024 UTC calendar months and packed salinity/eastward/northward fields. These are regional model fields in Norwegian Coastal Current context, not the current's occupied extent. Retain the original projected coordinates and 3.2 km sampled spacing; the patch has no coastline.

Produce the complete-calendar mean of each total field and the mean of its 24/24/25-hour low-pass field at each source cell. Use the same three-field paired wet/non-fill support as the section analysis. A missing required sample invalidates that cell's monthly mean; do not renormalize weights around gaps or fill with zero. Do not infer physical current identity, edges, width, annual extrema, area or OSW state containment from these maps.

## Exact linear evaluation of a low-pass monthly mean

For a complete hourly sequence, averaging the centered filtered samples is the same linear operation as weighting the original values by the convolution of the calendar-month averaging window and the 71-point filter kernel. Use that identity to accumulate monthly field means without retaining an entire year's spatial fields in memory.

- The raw mean uses weight `1 / calendar_hours` for each core hour and zero for halo hours.
- The low-pass mean uses `convolve(ones(calendar_hours) / calendar_hours, kernel)` across the month plus its 35-hour support on either side. The first and last extra hours of the acquired 36-hour halos have zero weight.
- All positive-weight source hours must have paired wet/non-fill support. The validity test includes every such hour, even a very small positive weight. A missing zero-weight extra halo hour does not invalidate the mean.
- Verify the identity independently against explicit filtering then averaging, for constant, linear and varying signals, including missing values and unused halo hours. This is a computational identity, not a tidal or uncertainty model.
- Do not derive filtered standard deviations or quantiles by this shortcut. The section's full hourly arrays and explicit filter continue to supply those statistics.

## Visual grammar and data access

Use the existing Norkyst native polar stereographic map conventions, equal projected X/Y scale and source-coordinate geographic context. Show salinity with a common scale across all twelve months. Rotate true east/north vector directions into the plotting plane before drawing arrows and keep the arrow reference scale fixed. Label total-field and low-pass monthly means distinctly; neither is an observation or a physical footprint.

Provide month, year, layer, model, units, data support, source credit and missing-cell treatment with the maps. Numeric source-cell means and support counts accompany the figure and later query UI. Keep the prior instantaneous maps and two-month comparison unchanged. Time controls must select actual recorded/derived months; do not synthesize unobserved current advection or physical boundaries.

# Pacific NECC paired vectors and native-column sensitivity v1

This extension closes the missing meridional-velocity field in the existing 2013 OSCAR section and checks the two adjacent native columns. It does not itself admit physical current width. The target-column u data and prior diagnostic have already been viewed. Metadata may be inspected before acquisition. No new v or neighboring velocity values have been inspected at declaration; no fully blinded or externally timestamped preregistration is claimed.

## Original support and exact request

Use the same NOAA PIFSC mirror of ESR OSCAR version 2017.0, dataset yearly_336c_0b32_9cd3. Request u and v for all 72 available timestamps from 2013-01-01 through 2013-12-28, nominal depth coordinate 15 m, latitudes 0-12 N, target 220 E and the immediately adjacent native longitudes. Requested longitude bounds are 219.666667-220.333333 E; retain the server's actual coordinates. Expected grid is 72 times by 37 latitudes by three longitudes: 7,992 vector positions. The nominal depth is product context, not a direct instrument slice or a depth-resolved measurement.

Preserve original CSV bytes, metadata, request, acquisition clocks and checksums. Metadata product/version/units must match the old source. Compare every target u value and mask against the old 2,664 target positions by coordinate/time, not row order; any difference stops downstream interpretation as the same source. Do not replace the old original or change the earlier diagnostic.

## Paired monthly operator

1. Validate exact rectangular source support, unique coordinate/time keys, canonical UTC timestamps, nominal depth and both m/s variables. Source nonfinite/fill values become null, never zero. Refuse duplicate or missing records and unexpected coordinate changes.
2. Require the existing 72-timestamp cadence, 37-latitude target grid and at least five samples in each UTC month. Use equal-sample monthly means, not exact daily/time-weighted means or a multi-year climatology. Retain real source times, including six-day gaps.
3. At each native cell, both components must be finite for every expected sample in that month; otherwise both monthly means remain unresolved. Store finite-pair and missing-pair counts. Never interpolate missing vectors.
4. Reuse the unchanged declared peak/connected-component operator: strongest eastward peak in 2-10 N, ties to lower latitude, peak at least 0.1 m/s; first paired-supported u=0 crossings on each side; stop at missing values or domain edge. Repeat at 0.05 and 0.1 m/s as boundary-definition sensitivity. Native brackets remain explicit. Meridional WGS84 distance is longitude invariant; retain actual source longitude when reporting geography.
5. Compare target paired monthly u profiles and zero-crossing results to the old u-only diagnostic. Preserve both if missing v prevents reproduction; do not force the old result through incomplete pairs.
6. At the selected eastward peak, report paired u, v, speed and signed atan2(v,u) direction in degrees from east. An attention flag at absolute direction above 15 degrees is an OSW diagnostic choice, not a scientific admission threshold or an uncertainty interval. Do not cosine-correct a component span into physical flow-normal width.
7. Across the three native columns, retain each month's peak, source span and direction separately. Flag peak-latitude differences above two native latitude cells as a diagnostic sensitivity check. Same-product spatial agreement is not independent validation, measurement error, an annual range or proof of current association.

## Interpretation and output

Keep the NECC, equatorial EUC and deeper Tsuchiya/NEUC names separate. Historical section descriptions remain association context; this one product/year does not establish full current identity, physical paired edges, an axis, length, seasonal geometry, annual extrema or whole-current widths. No new inventory width, polygon or rank entry is admitted automatically.

Produce pinned vector evidence with explicit units, source-pair counts, monthly direction/column comparisons and data-oriented tables. Plot u/v and directional/native-column context without presenting sampled spans as physical current footprints. Integrate useful evidence with the existing current card and query/source UI after review. The previous u-only product remains reconstructible unchanged.

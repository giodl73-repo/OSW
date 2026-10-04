# Pacific NECC OSCAR section diagnostic v1

Draft editorial method, 2026-10-04; independent scientific admission pending.

## Scope and source

Archived ESR OSCAR third-degree surface-current product version 2017.0,
NOAA PIFSC ERDDAP mirror `yearly_336c_0b32_9cd3`. Use zonal `u` in m/s at
220 degrees east (140 W), latitudes 0–12 N, nominal depth coordinate 15 m.
This is a satellite-derived near-surface field, not a measured instrument slice.
Use all 72 available five-day timestamps in calendar 2013. Source bytes,
metadata, request and acquisition manifest are checksum pinned. Default builds
are offline; acquisition is explicit and refuses replacement.

## Monthly profiles and boundaries

1. Group timestamps by UTC calendar month. Require at least five samples per
   month, a complete 37-latitude grid, at most six days between timestamps and
   at least 350 days of year coverage. Preserve actual first/last sample times.
2. Calculate an equal-sample monthly mean of `u` at each latitude. Do not claim
   an exact daily/time-weighted mean or a multiyear climatology. A missing sample
   makes its monthly latitude mean unresolved; never interpolate missing data.
3. Find the largest monthly eastward peak in 2–10 N. Ties resolve to the lower
   latitude. Require peak >= 0.1 m/s; this eligibility rule is an OSW choice.
4. Starting at that peak, find the first crossing of `u=0` on each side within
   the acquired 0–12 N section. Linearly interpolate between adjacent finite
   latitude samples. Stop at missing data or domain boundary without crossing.
   Include only the connected positive-flow component containing that peak;
   do not bridge westward gaps or combine distinct eastward branches.
5. If either boundary is unresolved, record null full span. Do not infer zero
   width from weak flow or an unclosed section. Record each resolved boundary
   and its two bracketing grid samples separately.
6. Measure meridional span between resolved boundaries with WGS84. Retain
   unrounded calculations, round display to 10 km, and state the section metric.
   This is width of a monthly mean zonal-velocity component, not mean width of
   instantaneous profiles, exact flow-normal width or a whole-current envelope.
7. Repeat at `u=0.05` and `0.1 m/s` to expose boundary-definition sensitivity.
   These choices do not create confidence intervals or source error margins.
   They do not replace the zero-crossing result.

## Temporal and geographic limits

The span of resolved monthly results is a 2013 local monthly-mean diagnostic,
not annual whole-current extrema or evidence for every year. This section
cannot determine current length, western connectivity or a complete axis.
No Tsuchiya/NEUC width, transport, eddy boundary or NASA animation footprint is
inferred. Satellite product errors, smoothing and coarse latitude sampling
remain limitations; quantitative width uncertainty is unresolved. Hsin and Qiu
(2012) used a different grid (1 degree) and 1992–2010 period, so this calculation
does not reproduce their climatology. Independent review and compatible
repeat-section/other-product checks are required before measurement admission.

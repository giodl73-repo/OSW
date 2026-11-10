# South Indian paired-profile diagnostic v1

Declared while the frozen source acquisition is running, before inspecting
its field values or monthly profiles. The source selection and known older
OSCAR failures are recorded separately. This is exploratory diagnosis, not
a blind confirmation or admission of current identity or physical dimensions.

Stramma (1992), printed p. 422, identifies the subtropical front using maximum
near-surface salinity and temperature gradients, giving salinity priority
because temperature varies seasonally. This motivates retaining gradients,
but does not establish a universal numerical threshold or identify any model
peak as the front. The two products differ in date, velocity reference and
spatial/vertical support. Our full-paper review records these differences.

Use every frozen HYCOM month, both depths and all three meridians. Keep native
latitude order, spacing, sample counts and missing means. At each depth and
meridian calculate adjacent-cell differences for all four monthly mean fields
divided by WGS84 meridional geodesic separation in kilometres. No smoothing,
interpolation, clipping, threshold tuning, background subtraction or gap filling.
Each gradient belongs to its two-node latitude bracket, not an observed front
coordinate. Gradients of monthly means are not means of daily gradients:
adjacent cells may have different valid dates even though the four fields
within one cell use common valid times. No such temporal equivalence is claimed.

Retain all positive local salinity-gradient maxima and all positive local
eastward-component maxima. A maximal equal-valued native plateau is one event;
retain its entire index/latitude support instead of inventing a new core point.
Require strict dominance over each available finite immediate flank. Missing
or domain-end flanks remain explicit censored events, never confirmed peaks.
A positive plateau with no finite flanks is retained as doubly censored.
Negative/zero values are not positive-peak candidates; their full gradients
and field values remain available. No candidate is dropped by latitude, rank,
velocity magnitude, temperature contrast or proximity to another candidate.

For each eastward event retain its same-cell U/V/T/S values and every closest
positive salinity-gradient bracket. Distance is the minimum WGS84 separation
between their finite latitude supports (zero when supports overlap); ties
within 1e-9 km are retained. The diagnostic distance is a spatial association
aid, not a current width, observational error or identity score. Censored
gradient maxima remain censored when linked. All non-nearest candidates stay
in the profile's complete candidate list, with stable local indices.

The 15 m gradients are near-surface model diagnostics. The 1000 m gradients
are deep context, not surface fronts or a vertically integrated circulation.
List all 72 selections and every missing/censored result. The report can
support a subsequent explicit feature-association assessment; it cannot itself
admit a named current, transverse width, axis, path length, seasonal footprint,
annual extrema, NASA match or state intersection. Keep existing measurements,
source reports and their frozen operators unchanged.

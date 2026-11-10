# South Australian HYCOM section span protocol v1

2026-10-13. Declare rules before acquiring velocity data. Use the single
GOFS 3.0 HYCOM+NCODA reanalysis experiment, 2012 daily 00Z output at 132 E,
100 m, over 38–32 S. Verify native coordinates rather than assuming index
origins: longitude index 3900 is 132 E, depth index 19 is 100 m; 6990–7355
are all 366 Gregorian days of 2012. This is an independent model diagnostic,
not a reconstruction of Duran et al.'s CARS-Aus8/MOM01 fields or their epochs.

Preserve original u/v response bytes and source metadata, Int16 values,
missing -30000 flags and scale factor 0.001 m/s. Both components must be valid
at each day/cell. Average complete pairs by UTC month only when their count
is at least ceil(0.8 × calendar days in that month). No gap interpolation.

Select the strongest positive eastward component within 35.5–33.5 S; ties
choose the lowest latitude. Require at least 0.02 m/s. This search window is
an OSW investigation choice informed by eastern-GAB source geography, not
current edges. Record edge peaks and named-current association as unresolved.

For 40/50/60% of that peak, walk through the connected band to the first
crossing in each direction. Interpolate only between the adjacent valid
bracket values. Missing cells, masks or a domain edge before a crossing leave
that side unresolved. A coast mask is not a velocity crossing; do not bridge,
choose a farther band or double a one-sided span into full width.

Compute WGS84 geodesic boundary separation, rounded to 10 km, when both sides
resolve. Native grid brackets and finite threshold sensitivity are separate
from measurement uncertainty, which stays null. Flag spans narrower than
four nominal 0.08-degree grid spacings. Native spacing does not establish
effective model resolution. No annual extrema, climatology, flow-normal width,
occupied-current polygon, state containment or NASA identification follows.

Keep unresolved monthly profiles and both mean velocity components. A width
of a monthly-mean profile is not mean instantaneous width; one year does not
establish annual physical extrema. Source South Australian naming and local
branch association require review. Seasonal plot inspection may highlight
recorded readings; it must not imply a tracked geographic current footprint.

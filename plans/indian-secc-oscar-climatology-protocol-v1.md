# Indian SECC region: native sections, yearly means and climatological spans

The preflight fixes two native OSCAR2017.0 columns bracketing 80.5 E, latitude
domain 12 S to the equator, years1995–2016, and a 6–2.5 S peak-search window.
Huang et al. (2023), doi:10.1029/2022JC019147, uses 1/3-degree OSCAR in this
period. Its frequency/phase bands are not lateral velocity boundaries. The
paper's 80.5 E section is not a native longitude in these archived responses.
Do not label either retained column as exactly 80.5 E or interpolate between
columns to create an observed section. Keep the columns' results separate.

Preserve unchanged public provider metadata and CSVs, exact requests, timestamps,
units, missing values, vector components and checksums. OSCAR is a diagnostic
near-surface product, not direct 15 m instrumentation or a depth-resolved flow.
The archive nominal depth coordinate is15 m; the paper describes top30 m
support. Do not equate this with ORAS5's differing depth descriptions.

For each year and calendar month, compute a cell's paired u,v mean only when at
least five records have both components present. For each calendar month,
average these year-month vectors with equal year weights, using the same valid
years for u and v and requiring at least18 of22 years. Keep valid-year counts
and original sample counts. This differs from pooling all five-day records,
the mean of instantaneous widths, or the mean of yearly widths.

Apply the existing component-span operator to each yearly monthly profile and
each climatological monthly profile: locate the largest eastward component in
the predeclared search window above0.02 m/s; walk to the nearest contiguous
40%,50%,60% threshold crossings on both sides. Never bridge missing cells,
disjoint peaks, westward/weak flow or the domain edge. Interpolate only a
crossing between adjacent finite native cells. Use WGS84 meridional distances,
round displayed spans to10 km, and retain unrounded crossings and grid brackets.

The nominal50% result, 40–60% threshold sensitivity, native-cell bracketing and
year-to-year spread are four different quantities. None is a confidence interval
or measurement error. Report how many yearly means resolve before displaying
their finite range. A spread of January monthly means is not annual physical
extrema. Preserve nulls and flags for search-edge peaks, fewer than four grid
spacings, and crossings beyond the frequency-classification window. Do not cap
a crossing at that window or assume it identifies one named current.

Keep all528 yearly monthly profiles and24 monthly climatological profiles
queryable with their separate source support. Figures must distinguish signed
velocity, derived spans, missing values and year-to-year coverage. Monthly
charts and local-section maps are allowed. Whole-current width, annual physical
ranges, ranked lengths, occupied polygons and seasonal current-footprint
playback remain ineligible pending identification and scientific review.

Archive the older no-numeric published-width assessment. These derived local
diagnostics do not change what that literature review established. All previous
width records, source definitions, routes and canonical names remain intact.

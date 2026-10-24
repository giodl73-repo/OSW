# EAC section spans: calendar distributions v1

Exploratory extension, 20 October 2026. Existing dated diagnostics and their
overall/monthly summaries have already been inspected. This is not blinded
selection or a new physical-width method.

Use every profile in the unchanged, pinned
`research/eac-csiro-100m-section-core-spans.json` (SHA256
`9339acdab74f9c520cb8beea8273a74f20b184b6b0f76c7b988b2b0c820c244e`).
Retain all three supplied-magnitude scenarios and all three threshold
fractions. The existing central 0.5 case remains primary. Do not change the
component projection, peak choice, velocity cutoff, boundary rules or failures.

## Grouping and denominators

Build twelve calendar-month groups, pooling source dates across the retained
record, and separate calendar-year groups. Use the source UTC date; do not
shift dates into local time. Preserve original profile indices. Reject duplicate
dates, inconsistent indices/year/month fields, absent scenarios/fractions,
nonfinite resolved spans and any non-null unresolved span. Check that every
date between the original first and last dates is represented, including
all-missing profiles. Never fabricate dates outside that interval.

Each group retains attempted and resolved dates, every source outcome count,
and contributing year-month support. A year records its full-calendar day
denominator and partial-calendar flag. Month groups retain each year's
attempted/resolved counts so unequal and missing support is visible.
Do not discard low-coverage years or choose a better-supported date range.

## Statistics and precision

For each group/scenario/fraction, describe only successfully bracketed section
spans with minimum, 10th percentile, median, 90th percentile and maximum.
Use sorted daily values with linear interpolation at index `(n-1)*p` (the
usual type-7 sample quantile). An empty resolved set has null statistics.
Carry source indices for minimum/maximum values; exact ties retain all indices.
Use decimal arithmetic on the serialized source values and round calculated
readbacks to 0.001 km, half-up. Public figure labels use whole kilometres.
This output precision is not observational accuracy.

The month distribution gives each resolved mapped source date equal weight;
it is not an equal-year average, width of an averaged velocity field, official
climatology, independent daily sample, confidence interval or physical annual
range. The filtered, SOM-filled mapped source dates are correlated, failures
may be selective, and unresolved outcomes remain in the denominator. Do not
pool scenario distributions into an uncertainty interval or connect pooled
months into a dated observed current trajectory.

## Presentation and admission

Draw an independent twelve-month comparison of the primary case with min/max,
10th–90th percentile segments, median points and resolved/attempted counts.
Add a separate year comparison showing partial-year support. No geographic
buffer, current edge, seasonal map footprint, ranked dimension or physical
width is admitted. All prior source fields, diagnostics and canonical rows
remain unchanged. Expose all nine cases in the data; the figure emphasizes
the pre-existing primary case rather than selecting a favorable scenario.

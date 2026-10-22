# North Atlantic Current nominal-section geographic bound v1

Declared before calculation, 2026-10-22. Extends the working measurements;
the historical v0.1.0 release and seven existing gate audits stay immutable.

## Source and scope

Caínzos et al. (2023), doi:10.5194/os-19-1009-2023, section 3.1.10
identifies the North Atlantic Current at nominal 47°N and 58°N sections.
Section 2 warns that station latitudes deviate from nominal sections;
the northern section combines western 53°N and eastern 58°N portions.
Only the explicit eastern NAC 58°N description is used. The cruises and
layers differ. No simultaneous axis, branch connection, actual endpoint
coordinates or common fixed layer is inferred.

## Operator

Compute WGS84 shortest meridional separation between nominal latitudes
47 and 58 degrees using an abstract common longitude of zero. This
longitude is a calculation device, never a flow position. Retain distance
to six decimal kilometres for arithmetic readback, then round down to a
100 km multiple as the conditional geographic floor.

Independently shift each nominal gate by -0.5, 0, +0.5 degrees and retain
all nine scenarios. This editorial scenario envelope is neither source
positional uncertainty nor a physical, seasonal or statistical interval.
Report the source's section-location warning alongside the result. A
nominal gate distance is not a guaranteed minimum for actual station
positions or for an identified continuous flow.

## Admission

Replace only the working North Atlantic length assessment with
`derived_lower_bound`; attach the original source and this method. Admit
one unranked `length_lower_bound` measurement explicitly marked as a
conditional geographic gate floor. Whole-current
length, rank, uncertainty, annual extrema, width, observed date, fixed
layer and geographic endpoint coordinates remain unspecified. Do not
change the existing illustrated map-arrow span or make a physical state
join. The qualified published-length count remains 12 of 101.

## Verification

Retain original CC BY 4.0 publisher content with acquisition metadata and
SHA-256. Verify gate descriptions and the nominal-section warning from
that original. Check independent WGS84 arithmetic, all nine scenarios,
floor rounding, unchanged historical release and existing scientific
reports, and native/WASM queries. Reject edited values, owner, source,
rank, dependency receipts and admission records. Provide an accessible
scalar figure and direct links from the existing mapped current card.

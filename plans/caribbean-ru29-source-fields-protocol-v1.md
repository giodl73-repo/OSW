# Caribbean RU29 source fields: prospective protocol v1

## Scope and custody

Read back all variables, dimensions, global attributes and variable attributes
of the eleven selected original NetCDF members in the pinned custody manifest.
These are provider products from Gradone et al. (2026),
https://doi.org/10.5194/os-22-735-2026, dataset
https://doi.org/10.5281/zenodo.18332586 (CC BY 4.0).
The full 1,070,927,767-byte ZIP was not downloaded. Its publisher MD5 is
recorded, not independently verified. Exact ranged compressed payloads were
decoded and checked against ZIP member CRC32 and uncompressed sizes; local
SHA256 pins bind the selected originals. This is selected-member custody,
not verification of the complete archive or reproduction from raw beams.

Freeze this protocol, producer, synthetic tests, selected originals, source
facts and preflight in Git before running the producer on actual arrays.
Retain any failure. Corrections require a new scientific version.

## Complete readback

Store original packed values in original dimension order, with original dtype
and all attribute values. Tag nonfinite values as `NaN`, `Infinity` and
`-Infinity` strings; JSON null is never a substitute for zero. Store the
NetCDF library's default decoded mask separately, even if no elements are
masked. The raw array, attribute scales/offsets, dtype, shape and mask allow
lossless interpretation without silently changing provider packing. Keep
variable-length strings and exact integers, including nanosecond clocks.
No rows, contour points, link slots, variables or source categories are
dropped. Preserve untracked, short-track and correspondence products as
distinct source files. Their track numbers are local identifiers, not names
or globally interchangeable identities. Do not trim zero contour padding or
apply `num_point_e/s`, which describe pre-resampling point counts.

Summaries report raw finite/missing counts and raw ranges, explicitly marked
as packed raw quantities. They do not report physical eddy radii or dates.
Track inventories, if produced later, must namespace IDs by source member
and distinguish observed from virtual positions using observation_flag.
Correspondence `virtual` fill slots must not be counted as observed events.

## Current visualization

Display both complete provider interpolated occupations (100 depth by 97
latitude cells, two velocity components each). Every source cell has a
rectangle; nonfinite cells are grey. Depth increases downward and latitude
increases rightward. Cell edges are adjacent-coordinate midpoints, with
half-spacing extrapolation at endpoints; these display edges do not imply
observed water outside the grid or an identified current boundary.
Require finite strictly increasing coordinate centres and exact array shapes.
Use a shared fixed diverging scale of -0.5 to +0.5 m/s for all four panels;
count and state finite values beyond this display scale. Preserve full
unclipped values in the mirror. Units m/s and m are attributed to paper
section 2.1.1 and the Final author notebook, not invented NetCDF attributes.
The source's regular longitude -69 degrees is a constructed section grid,
not the exact glider trajectory. The multiweek occupations are not snapshots.

## Source support and open discrepancies

Source code Final commit 5029c77bb75905d4cb5dc461035bff8ddac59395 defines
occupation windows 2024-04-27T20:05:00Z–2024-05-18T12:00:00Z and
2024-05-18T12:00:00Z–2024-06-06T00:00:00Z, a nominal 6 km latitude grid,
and separate linear interpolation of u/v from jointly valid source profiles.
Most current variables have no source unit attributes. Source eddy contour
latitude metadata incorrectly says degrees_east/axis X; retain that text.
Paper section 2.2 describes removal of a Gaussian 10 by 5 degree background
and 1 cm contour intervals; commented notebook code instead describes a
500 km Bessel filter and 0.002 contour interval. Do not claim reconstruction
of either pipeline from archived output alone. No contour interpretation or
eddy-method comparison is performed by v1.

The paper states navigation missed the full current width and approximately
1000 m depth sampling missed some vertical flow. Do not derive whole-current
length, physical width, seasonal margins, annual extrema, official eddy names,
OSW state intersections or rank eligibility from this readback. Do not treat
transect span, mission distance or eddy diameter as current dimensions.
Source RMS velocity uncertainty O(0.05) m/s is contextual, not independent
per-cell error bars or a confidence interval. No transport calculation or
reconciliation with the paper's reported transport occurs in v1.

## Verification and resource sequencing

Synthetic fixtures cover packed scales, fill masks, exact integers, strings,
nonfinite values, coordinate rejection, cell retention and shared display
limits. All source SHA256 and byte sizes must match before reading arrays.
Public products are a complete raw mirror, concise inventory report and SVG.
Run alone at BelowNormal priority on one logical CPU. No build or browser
overlap. Native/query/browser integration follows as a separate delivery step.

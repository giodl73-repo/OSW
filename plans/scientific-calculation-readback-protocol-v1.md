# Scientific calculation readback protocol v1

20 October2026. Applies only to the explicitly listed derived report fields.
Recorded after Windows/Linux reproduction diagnostics, before rebuilding the
affected reports. Original source arrays/files and their checksums stay exact.

## Derived readback precision

| Computed quantity | Decimal places | Readback increment |
|---|---:|---|
| Geodesic distance in km | 6 | 1mm |
| Geodesic piece length in m | 3 | 1mm |
| Bearing or tangent azimuth in degrees | 6 | 1e−6degree |
| Calculated midpoint longitude/latitude in degrees | 8 | 1e−8degree |
| Interpolated velocity, speed and along-path component in m/s | 8 | 1e−8m/s |
| Calculated bilinear weight or geometric ratio | 8 | 1e−8 |

These increments describe calculation serialization, not instrumental accuracy,
effective resolution, confidence, threshold sensitivity or physical uncertainty.
They exceed the observed platform differences while retaining precision far
finer than the source's physical support and public reporting increments.
Use Python decimal-place round (ties to even); canonicalize derived signed
zero to positive zero. No universal rounding of scientific JSON is permitted.

## Exact boundary

The producer calculates geometry, interpolation, support, thresholds and
eligibility using its declared full-precision operators. Normalize only the
listed output readbacks. A changed outcome or count is not normalized away.
Original source coordinates, velocities, corner values, masks, QC, clocks,
indices, protocol parameters and native stored bits remain untouched. Stored
Loop route vertices remain at the prior six-decimal convention; raw ADT
contours are retained as before. Whole-current/width/annual admission flags
are unchanged. Calculated readback cannot supply a physical error budget.

For the NorKyst distance coordinate shared by JSON and derived NPZ, apply the
same1mm readback to that derived coordinate in both artifacts. Model fields,
original grids, interpolation weights, filtering, masks and statistics remain
unchanged. Repository-relative dependency keys use POSIX separators.

## Explicit profiles

The implementation declares JSON pointer patterns per report schema, matching
only named derived fields. Initial profiles cover Aleutian observed track
geometry, hydrography pairing distances, component-span geometry, native run
geometry, underway/composite separations, NECC calculated spans, NorKyst section
distances and Loop contour midpoint/interpolation readbacks. Embedded original
vectors and original corner arrays are outside the whitelist.

Each normalized report pins this protocol and its implementation. Any future
field requires an explicit profile/protocol review; new numeric fields are
never silently rounded. Nonfinite values in a selected computed field are
errors; original source null/missing conventions remain preserved.

## Accounting and verification

Independent distance checks must account for the declared stored-piece
quantization: the sum of N pieces can differ from the full-precision geodesic
sum by at most N×0.5mm, plus floating-point summation roundoff. Check that bound
explicitly rather than expecting micrometre equality from millimetre readbacks.
Interpolation reconstruction similarly retains original corner values and
declared weight/velocity readback increments. No blanket JSON tolerance.

Require exact retained/rebuilt bytes at the declared precision on Windows and
Linux, source/shape/QC/order/count/status preservation and mutation rejection.
Rebuild all dependent hashes, figures, query/index data and Rust/WASM. Preserve
the prior artifacts through Git. Public approximate values and scientific
outcomes must remain unchanged; otherwise investigate and review the change.
Do not restart or mutate the existing live full-suite checkout to implement
this repair. A clean successor gate follows its terminal state.

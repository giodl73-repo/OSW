# South Indian paired-profile diagnostic v2: portable meridian arithmetic

Supersedes the v1 diagnostic implementation for the canonical atlas result.
The original v1 operator, preflight and report remain unchanged as historical
artifacts. Linux run39791437671 at5e9bb09 found platform-dependent PROJ
meridian-rounding differences up to about1.8e-12km. The original33 scientific
report byte gates remain unchanged. The replacement34th diagnostic must pass
the same exact-byte gate; no tolerance, rounded output or semantic-only gate
is substituted. The source archive, monthly arrays/JSON, masks and sample
cohort remain unchanged.

Keep all v1 event, plateau, censoring, native-grid, common-time, missing-data,
nearest-support tie and no-admission rules. Change only computation of the
WGS84 meridian separation used by gradients and nearest-support distances.
Same-longitude separations are independent of longitude on this ellipsoid.
Use a=6378137m and f=1/298.257223563, e²=f(2-f).

The meridian radius is a(1-e²)/(1-e²sin²φ)^(3/2). Integrate its binomial
series using c0=1, cn=c(n-1)(2n+1)/(2n), I0=φ and
In=((2n-1)I(n-1)-sin^(2n-1)φ cosφ)/(2n). The signed equator-to-latitude
arc is a(1-e²) sum(n=0..16) cn(e²)^n In.

Compute with Decimal precision70, round-half-even, the pinned π
literal, and70 Taylor terms each for sine/cosine. Convert each original
binary64 latitude exactly with Decimal.from_float. Subtract arcs and divide
by1000 in Decimal; round only that result once to binary64. Field differences
and gradient division retain full Float64 outputs. No scientific value is
rounded for publication. The geometric series' omitted tail is far below
binary64 metre resolution at these latitudes; validate against independent
Gauss-Legendre meridional-curvature integration and PROJ. Numerical comparison
tolerances in those accuracy tests are not replay tolerances or physical errors.

WGS84 definition reference: ESA Earth Observation CFI conventions, Table5,
https://eop-cfi.esa.int/REPO/PUBLIC/DOCUMENTATION/CFI/EOCFI/BRANCH_4X/releases/4.12/C-Docs/MCD_conventions_v4_12.pdf

Declare v2 helper/operator/protocol, old report/operator, source and dependency
pins before regenerating. Record the known v1/Linux outcome; this is a numerical
portability correction after source acquisition, not a blind experiment.
Compare all event counts, supports, censoring and association flags with v1.
Any classification difference requires explicit review. No current identity,
width, axis, length, annual extrema or occupied footprint is admitted.

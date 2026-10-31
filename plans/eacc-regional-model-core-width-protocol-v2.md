# EACC regional model-core diagnostic protocol v2

Status: prospective implementation protocol; **not frozen for an original
case**. Only tiny synthetic arrays have exercised the new operator. No EACC
model velocity payload has been requested or inspected under this method.
Provider coordinate selection is now verified, as recorded below. The custody
workflow, complete scientific dependency preflight and presentation are still
required. Heavy work remains disabled. The v1 files and review remain unchanged;
v2 resolves a grid-coordinate tie discovered before any velocity acquisition.

## Scientific target and source envelope

Test whether a locally coherent northward model core near 9 S supports two
connected 40/50/60% projected-velocity crossings. A positive numerical result
is a regional, model/depth/time-specific core diagnostic. It does not establish
EACC identity, whole-current width, observed seasonal extrema, an eddy identity,
transport, a full-current polygon, a state intersection, a length rank or a
NASA animation feature identity.

The proposed source is the official HYCOM experiment53.X 2013 endpoint, with
38â€“44 E / 13â€“5 S source coverage, exact 15 m provider depth, and daily 00Z
paired east/north vectors. These are prospective choices. Fresh DDS/DAS
declarations are retained in `research/source-data/eacc-hycom-2013-metadata-v1/`.
Fresh coordinate metadata is retained separately in
`research/source-data/eacc-hycom-2013-coordinates-v1/`. The reproducible candidate
selection is `research/eacc-hycom-2013-source-selection-candidate-v1.json`.
Provider depth index7 is exactly15m. Regional indices are latitude1338–1437
(100 rows, -12.960000038146973 to -5.039999961853027 degrees), longitude2725–2800
(76 columns, 38–44E). These are the provider cells inside the editorial window,
not exact13S/5S physical boundaries or a current outline. Velocity payload
availability/validity remains unverified; do not substitute another level.

Monthly vectors require paired valid daily samples at each native cell on at
least ceil(0.8 Ã— Gregorian calendar days). Preserve inadequate counts and masks.
Sum packed valid integers before decoding with the exact binary32 scale
promoted to float64. These means describe daily model samples, not all model
times, observations or climatology. Freeze exact requests and this calculation
before acquiring velocity fields. No smoothing, filling or extrapolation.

## Native seed selection

`analysis/eacc_model_core_seed_v2.py` selects the provider latitude nearest9S
inside the source latitude range. If native rows are equally near within
1e-12 degrees, choose the southern row, retain both indices and the fixed rule,
and keep the northern row as offset+1 sensitivity. Actual nearest rows are
regional49/50 at -9.039999961853027/-8.960000038146973 degrees. This rule was
chosen from coordinate metadata before velocity acquisition; no flow result
informed it. Equal **velocity** peaks remain unresolved. Search 39â€“41 E for the largest northward component among finite
paired native samples; retain finite/missing candidate counts. Equal peaks
within 1e-10 m/s remain unresolved. The winner needs four paired finite bilinear
corners, northward velocity >=0.1 m/s, and direction within 45 degrees of north.
No fallback to a more convenient runner-up is permitted. Missing cells are not
zero ocean flow, and the available-cell/window maximum is not a global maximum.

Use native-row offsets -1/0/+1, retaining the primary longitude. A neighbor has
its own corner and northward checks but cannot rescue an unsupported primary.
These offsets are method sensitivity, not independent samples or error bounds.

## Local geometry and axis support

`analysis/eacc_model_core_diagnostic_v2.py` reuses the frozen `Field`, geodesic
normal sampling, peak audit and adaptive RK4 helpers; it never calls the old
Indian SECC eastward-seed case operator or swaps Earth-frame components.

At bearing beta, q = U Ã— sin(beta) + V Ã— cos(beta), in m/s. WGS84 geodesic
normals increase toward bearing+90 degrees. Transport the tangent perpendicular
to the normal at each sample. Four paired finite corners and supported segment
rectangles are required. Preserve the first failed sample on each side.
Profiles use 5 and 10 km steps, at most 600 km per side. Neither a source mask
nor a profile limit supplies a velocity crossing.

Refine a supported seed once to a unique interior projected-velocity maximum
within +/-40 km. The frozen peak helper requires >=0.02 m/s projected flow,
strict adjacent declines, and >=1% contrast against both +/-40 km endpoints.
Equal peaks within 1e-10 m/s, missing endpoints and search-edge peaks fail.
Recheck the refined vector against the >=0.1 m/s and 45 degree northward guards.
Initial refinement may move inside the 40 km window; the displacement gate
below applies to each subsequently recomputed streamline-station normal.

The primary seed receives stations at -100,-50,0,+50,+100 km streamline arc
parameters. Reuse adaptive RK4 with maximum 10 km / minimum 0.1 km trial,
0.01 km local step-doubling error tolerance and 0.005 m/s speed guards. Shorter
final station remainders are allowed. Preserve partial paths, failure reasons,
chord sums and local error estimates. A short streamline of a monthly mean is
not a particle track, a measured current axis or a whole-current length.
Neighbor seeds receive only station zero.

At each station recompute the normal. Local axis support requires the peak
audit above, peak displacement <=10 km, and vector direction difference <=15
degrees from the transported tangent at the peak. Five stations are required
for a supported primary segment. Retain failed stations and diagnostics rather
than dropping them from monthly summaries.

## Connected edges and native resolution

For each 0.4/0.5/0.6 fraction, walk outward from the selected peak to the first
sample at or below that threshold. Interpolate only its adjacent supported
bracket, retain the actual evaluated residual, and keep both edge positions.
Stop at missing support or the domain/profile limit. Never bridge a gap, close
at land or double a one-sided distance.

Before a threshold crossing, track the running minimum projected component.
An outward rise greater than 1% of the central peak censors that side as an
unresolved possible competing core. This is an editorial method gate, not a
physical eddy classifier. A separated band beyond the first threshold crossing
does not replace that crossing. The chosen rule may censor real undulations;
report its failures without post-result tolerance changes.

For paired crossings, compute WGS84 edge separation in km. Resolution support
uses the largest of all four native cell-edge distances for every cell touched
by the retained sample-segment rectangles between the outer crossing brackets.
Require width / largest native scale >=4. This conservative rule accounts for
anisotropic and changing spacing; it does not prove effective model resolution.
Five-kilometre display sampling cannot improve native source support.

Keep paired `diagnostic_span_km` even if the local axis or native-resolution
gate fails. Set `resolved_span_km` only when both gates pass. Successful
numerical gates still do not verify named-current association or observation
uncertainty. Width thresholds are core definitions, not full dynamic boundaries.

## Complete outcomes and comparisons

Retain 12 months Ã— 3 native offsets Ã— 2 profile steps =72 cases. Missing months
produce explicit missing-field cases; never omit months or convert nulls into
zero widths. Include all 0.4/0.5/0.6 edge statuses, sampled vectors, cell indices,
failure reasons, source support counts and paths. Decision arithmetic precedes
display rounding; packed helper samples retain the frozen readback convention.

`diagnose_year` produces 12 primary monthly summaries, 84 station-specific
5-vs-10 km comparisons and 48 central-vs-neighbor seed comparisons. Differences
are computed only when both selected spans are resolved. Incomplete comparison
support retains each side's status and a null difference. Seed and step
sensitivity remain distinct from threshold choice and physical variability.

Every result retains false source/current-association and rank/join eligibility
flags, and null whole-current length/width, annual physical extrema and
measurement uncertainty. A source/custody envelope and a later admission review
must establish any stronger claim. A width of a monthly mean is not a mean
instantaneous width; twelve monthly sample means do not prove annual extrema.

## Required visualization and semantic evidence

The original case must retain twelve geographic source-neighborhood maps and
station normal-profile views, including unsupported months. Use a declared
regional longitude/latitude projection with labeled degrees, WGS84 distance
scale, actual dates, depth, model identity, source/method links and threshold
legend. A velocity mask is not a coastline: label masked support as such unless
separately sourced land/bathymetry is supplied. Distinguish missing, censored,
out-of-domain and resolved statuses using words and line patterns as well as
color. Do not depict a filled whole-current footprint from normal spans.

Provide equivalent semantic monthly/station/threshold tables with paired-edge
support, null explanations, native scales and method differences. A reader
must be able to reach sources and select a month/station using the keyboard,
without hover or color as the sole path. Keep mobile/reflow and reduced-motion
behavior in the later saved-cloud browser gate. A changing diagnostic view
must not be labeled seasonal physical-current playback.

## Gates and execution sequence

1. Complete source coordinate/citation/selection verification; retain bounded
   metadata receipts. No velocity request until exact requests are frozen.
2. Finish source-acquisition and monthly-mean operators and parser/packing/
   missing-time tests. Isolate all new paths from executed earlier cases.
3. Resolve internal role findings, pin this protocol, seed/diagnostic/tests,
   source logic, environment and complete imported scientific dependencies in
   a new committed preflight before the first original velocity payload.
4. Run one original cloud job, one request/worker at a time. Preserve all source
   responses, failures and all72 outcomes. No local model-array processing.
5. Review actual regional association maps, profiles and source support. A
   failed diagnostic is retained; it is not evidence of absence of the EACC.
6. Prepare typed query/card/atlas delivery only for the reviewed evidence
   class. Build native, then WASM, then browser validation, sequentially in the
   cloud. Reuse saved cohorts for presentation fixes. Do not rerun science for
   a layout change. No new PR per gap.

Do not alter v2 after its first original result; changed scientific decisions
require a new version. The current phase is source review with heavy work
disabled. The separate Rotschi1972 default-offline/release gate remains open;
synthetic method checks do not establish a full regression pass, main merge,
scientific release or current-wide measurement completeness.


## Source preparation and provider limitations

`analysis/eacc_hycom_source_selection_v1.py` verifies DDS/DAS frame, units,
packing, clock and distribution declarations and reproduces the exact candidate
selection from the three original metadata responses. It proposes82 sequential
requests with at most six daily samples each, an8MiB response cap and one
concurrent request. All363 available daily00Z indices occur exactly once.
August14 and December25,2013 are absent at00Z. Preserve those gaps; monthly
thresholds remain25/23/25/24/25/24/25/25/24/25/24/25 paired calendar days. No
velocity request is authorized by the candidate alone: it explicitly remains
unfrozen and requires an external committed scientific preflight and later
cloud phase. Metadata parsing and synthetic packed means are not an original
velocity case.

The provider's [product documentation](https://www.hycom.org/dataserver/gofs-3pt1/reanalysis)
identifies GOFS3.1/experiment53.X and explains that GLBv0.08 fields are remapped
from the computational grid and interpolated onto40 standard depth levels.
Here, "native source cell" means the supplied remapped output cell, not an
unmodified model mesh cell;15m is a standard output depth. The documentation
also describes Pacific-region grid/assimilation instabilities and warns that
other locations may be affected. Those notes neither demonstrate nor rule out
an EACC problem. Retain source limitations and any diagnosed anomalies; do not
interpret apparent grid detail as validated physical accuracy. The documentation
and metadata distribution statements do not supply measurement uncertainty.

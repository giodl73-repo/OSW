# EACC regional model core width: method draft v1

Status: prospective research draft, not an executable or frozen case protocol.
No EACC model velocity fields have been requested or inspected for this method,
and no new length, width, annual range, observation or geometry is admitted.
This follows the literature/source-scope checks; it is not a blind experiment.

## Falsifiable target

Test whether a locally coherent northward model core near 9 S has two supported
half-peak velocity crossings on a geodesic normal. A successful result would be
a regional, depth/time/model-specific core span. It would not establish the
width of the entire named EACC or resolve a published historical width claim.
Failure includes missing/censored edges, insufficient resolution, nonunique
peaks, incoherent local direction or unresolved association with the EACC.

9 S is an OSW investigation choice inside the reported 11–3 S EACC region,
away from its northern confluence. It is not a source-reported endpoint or
observational station. Its relationship to islands, other branches and the
modeled boundary flow must be checked on actual neighborhood maps before any
named-current admission. A maximum northward velocity alone does not prove
current identity.

## Proposed source and support

Evaluate the official GOFS3.1 HYCOM+NCODA GLBv0.08 expt53.X 2013 archive,
already used by the separately frozen Indian SECC source method. Verify fresh
provider DDS/DAS and coordinate metadata; do not assume unchanged indices,
packing, units, depth, time origin or complete source availability. An exact
provider 15 m level is proposed; do not substitute another depth if absent.
No source access or source identity is established by this draft.

Proposed fixed viewport: 38–44 E, 13–5 S. Before velocity acquisition, finalize
and commit every actual source-index request against checked metadata. Bound
responses and use one request at a time. Do not request a global velocity cube.
All new source preparation must be isolated from existing executed artifacts.

Use exact daily 00Z paired east/north velocities for Gregorian 2013. Monthly
vector means require ceil(0.8 × calendar days) valid pairs at each native cell;
retain all inadequate counts and missing values. Decode Float32 packing scales
as binary32 promoted to float64, and sum valid packed integers before scaling.
These would be means of daily model samples, not full-frequency monthly means,
observations or climatology. Keep the real source distribution/citation terms.

## Proposed selection and geometry

For each month, use the native latitude nearest 9 S and search 39–41 E for the
strongest positive northward component. These are editorial investigation
windows, not current boundaries. Reject missing/nonunique peaks and peaks
below 0.1 m/s. Require the seed direction to lie within 45 degrees of true
north. Do not choose a more convenient month, longitude or depth after results.

Reuse frozen sampling/geodesic helpers where their assumptions hold. The
existing Indian SECC case has an **eastward** seed guard; it cannot be called
unchanged for a northward EACC case. A new tested operator must explicitly
implement the northward selection, preserve actual Earth east/north vectors
and compute normal geometry without swapping components or geographic axes.

At core tangent bearing beta, use projected velocity
q = eastward_velocity × sin(beta) + northward_velocity × cos(beta).
Generate WGS84 local-normal profiles and retain the transported tangent
convention. Bilinear samples require all four paired wet-cell corners. No
interpolation across masks, missing cells or outside the source domain.

Proposed robustness checks retain the existing local-axis method's +/-40 km
refinement window, unique-peak tolerance, 1% endpoint contrast, <=10 km peak
displacement and <=15 degree direction change. Check five stations at -100,
-50, 0, 50 and 100 km arc parameters with both 5 and 10 km profile steps.
Test neighboring native-latitude seeds separately. Their distances are method
perturbations, not independent observations or numerical uncertainty bounds.

Walk the connected core to the first 40/50/60% peak crossings on both sides.
Missing support, masks, a competing unresolved core or a domain edge censors
the corresponding result. Never bridge to another band, use a mask as a
velocity crossing or double a one-sided distance. Require at least four native
cell spacings for a resolved span; grid spacing is not effective resolution.

## Required work before the first original case

Finalize exact metadata/source selection and support thresholds. Implement a
new operator with positive northward Gaussian cases and failures for eastward
seeds, equal peaks, missing corners, one-sided masks, inadequate resolution,
direction changes and endpoint/domain truncation. Verify expected synthetic
half-peak spans and preserve every failed/unsupported month. Then review source
association and dimensional/geodesic conventions through the repository roles,
commit all exact operator/test/protocol/dependency pins and freeze a new
preflight before requesting velocity fields or calculating original spans.

Retain the complete source neighborhood/profile figures, monthly counts and
all threshold outcomes. Do not tune v1 after its first original result; make a
new version if the method changes. A zero-support outcome remains a valid
failed diagnostic, not evidence that the current is absent.

Any later admission requires explicit evidence of regional/current association
and must identify model, level, dates, metric, resolution and censored cases.
Threshold/seed/step differences are method sensitivity; measurement uncertainty
stays unknown. A width of a monthly mean is not mean instantaneous width.
Twelve sampled monthly means do not establish annual physical extrema.
No full-current polygon, state intersection, route length/rank, NASA identity
or seasonal geographic playback follows. The broader current gap stays open
until its actual required support is present and reviewed.

No local original-array processing, native/WASM build or browser run is allowed.
An eventual source/diagnostic case must be a later single cloud job after the
current candidate, presentation and installation sequence has finished.

## Implemented preparation checkpoint (no original case)

`analysis/eacc_model_core_seed_v1.py` now implements the prospective seed
selection separately from the frozen eastward Indian SECC case. Its companion
`analysis/test_eacc_model_core_seed_v1.py` passed 23 tiny synthetic checks on
2026-10-24, with one logical CPU, BelowNormal priority and one numerical worker.
No network, original model arrays, build, browser or map rendering was used.

The native row must bracket the target latitude in the source domain. Equally
near native latitudes within 1e-12 degrees are retained as an unresolved tie.
Within 39–41 E, select the largest northward component among finite paired
native cells, retaining missing-cell counts. Numerical peak ties within
1e-10 m/s are unresolved. This maximum is conditional on the available paired
cells and editorial window; it is not a claim about missing cells or the
whole current. The winning vector must also pass the four-corner bilinear
support, 0.1 m/s northward and 45 degree direction checks. A failed winner does
not trigger selection of a more favorable runner-up.

Neighboring-row perturbations retain the primary longitude and move by exactly
one native row, with their own paired-corner and direction checks. They do not
reselect a peak. An unsupported primary seed cannot be rescued by a neighbor.
The checks include an independently specified northward Gaussian with sigma
40 km: its expected half-peak span is 2 × 40 × sqrt(2 × ln(2)) km, recovered to
within 1 km by the frozen geodesic profile helpers on the synthetic grid.

This is a seed-selection component, not the complete new diagnostic operator.
Remaining prerequisites include verified provider metadata and exact source
requests; full local-axis/connected-edge/competing-core/resolution decisions;
all-month and station retention; geographic source-association figures and
semantic alternatives; operator tests; role review; and a committed frozen
preflight. Neither a successful synthetic seed nor this checkpoint authorizes
source acquisition or scientific admission. The cloud heavy-work phase stays
disabled while preparation continues.

Fresh provider DDS/DAS metadata was retrieved sequentially on 2026-10-24 and
retained with byte hashes, timestamps and one-attempt receipts in
`research/source-data/eacc-hycom-2013-metadata-v1/`. The review is
`research/eacc-hycom-metadata-review-v1.json`. Both requests returned HTTP 200;
total response content was 6,957 bytes. Headers declare paired Int16 eastward
and northward velocities, Float32 packing scales, metres-per-second units,
Gregorian time and depth positive down. These checks establish declarations,
not payload validity. Coordinate arrays were not requested: exact depth,
dates, daily support and regional indices remain unverified. No velocity
request manifest is frozen, and source velocity acquisition remains disabled.

The prospective diagnostic is now implemented separately in
`analysis/eacc_model_core_diagnostic_v1.py`, with its detailed decisions in
`plans/eacc-regional-model-core-width-protocol-v1.md`. Synthetic coverage now
includes connected-edge censoring, overlapping-core rises, conservative native
resolution, five-station paths and all72 retained yearly attempts. The new
protocol remains unfrozen. The geographic figures, source selection/custody
and first original cloud case are still outstanding; earlier checkpoint
requirements are not claims that those deliverables have already run.

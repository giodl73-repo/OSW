# Pacific NEC connected westward core diagnostic

## Question and custody

The previous centroid experiment failed all12 months and108 sensitivity cases:
an average latitude can lie in eastward flow between westward patches. Preserve
that failed operator and its withheld values. This revision tests a different
object: a connected westward product-core path, not a centroid or fluid streamline.
It also tests whether successive monthly section spans refer to overlapping
local branches rather than whichever peak happens to be fastest.

Reuse only the exact source artifact12903990715 from run40887454328 attempt2,
source f11587af695883500cce9500b72ac2840d97929f, ZIP37597803bytes,
SHA25654de0d3099ca3f23ab93226a063248b34f48c176723864928ad0bbe0fb1bba7a.
It contains metadata.json, vectors.csv and acquisition.json. Verify archive
custody, exact member names, sizes and original acquisition hashes before parsing.
No new provider download or extension of the4–26N,130–240E source crop is allowed.
Preserve2013 only, original timestamps, product/layer/units and equal-sample
monthly means exactly as in the previous parser. Use the same cached source for
all choices; do not rerun or weaken a failing gate after seeing results.

## Spatial components

In each monthly vector field, restrict the graph to the fixed8–18N native grid.
For each threshold0,0.025,0.05m/s, a cell is eligible only if both monthly vector
components are complete/finite and u < -threshold. Label all4-neighbor connected
components. Record component sizes, source-grid-boundary contact and which
components touch both130E and240E gates. These are zonal-sign components,
not established current footprints. Keep components separate even when their
centroid or bounding boxes overlap. Missing cells are never filled.

## Directed core path

For every month and threshold, construct paths westward from240E to130E, taking
exactly one native column per step. Allowed latitude changes are0 or±one native
cell. A diagonal also requires at least one eligible orthogonal corner cell;
it cannot jump across two diagonally touching patches or eastward/missing cells.
Both endpoint vectors must align with the westward path leg within the chosen
maximum angle45,60,90degrees. Calculate this screening direction in the local
equirectangular tangent plane with longitude scaled by cos(mean latitude);
this is a declared numerical direction test, not a physical uncertainty estimate.

Use a layered dynamic program. Maximize the sum of per-leg average westward
zonal speeds minus p times the squared latitude step in native-cell units.
The frozen penalties p are0,0.02,0.05m/s; nominal0.02. Nominal threshold0.025m/s
and maximum angle60degrees. All three thresholds × three penalties × three
angles × twelve months give324 retained cases. This optimization defines the
OSW product-core operator; it is not an author-reported axis or fastest streamline.
Unresolved score ties within absolute1e-12 are ambiguous and withhold the length.
Do not bridge failed columns, insert a convenience vertex or shorten the gates.

Retain the winning witness path, its score, source vector values, connected
component identity, every rejection and each scenario's exact path hash. Every
qualified path must belong to one4-neighbor component and touch both fixed gates.
Measure WGS84 geodesic leg sums, round nominal lengths to100km, and label them
regional lengths of this source-product operator. Source resolution, threshold,
angle and penalty sensitivity do not become confidence intervals. Whole-current
length, physical endpoints and whole-current ranking remain unresolved.

## Width and temporal identity

At137E,180E and220E, locate the source latitude cell used by the nominal core
path. Follow its own connected negative-u meridional interval, using the original
4–26N halo, to both zero crossings. Use linear edge interpolation and WGS84
meridional distance, preserving the fixed-meridian component-span definition.
Do not switch to the strongest disconnected peak. Missing/boundary-censored
edges withhold the paired span. Retain the selected cell, local interval,
component, edges and source profile. Also retain the previous fastest-peak span
for explicit comparison; it is not a second independent observation.

For each consecutive2013 month, record intersections, union and directional
overlap fractions of full-gate8–18N components. Mutual overlap of at least0.5
with unique one-to-one partners defines a diagnostic component continuation.
Retain all alternative overlaps; splits, merges, ties or failed thresholds are
ambiguous. Do not wrap December to January: this is a dated year, not climatology.
At each section independently require mutual overlap of at least0.5 between
successive selected local negative-u intervals. A complete tracked regional
monthly span range requires12 paired widths and all11 component and local
continuation checks; otherwise retain partial candidate values without calling
their extrema a tracked seasonal range. Even a passing numerical track requires
physical/source review before current-width admission or seasonal playback.

## Visualization and execution

Render all12 nominal witness paths or an explicit failure reason for each month,
plus length and section-span panels. An entirely withheld panel must have no
numeric distance axis and must say the quantities are withheld. Label disconnected
or temporally ambiguous span series as candidates. Mark missing months without
placing a zero measurement. Show source product, nominal15m coordinate, year,
regional gates and method. Inspect actual PNGs before product admission.

One cloud job, one low-priority CPU; maximum local heavy jobs0. No native/WASM
build, browser automation, original fields downloaded locally, packet/index
installation, main update or automatic physical admission. Return compact derived
metadata and figures. Preserve full scenario witness paths on the cloud for
reproducibility. After scope/physical review, integrate accepted evidence into
the existing Rust query UI, cards, dashboard and OSW atlas with original coordinates.

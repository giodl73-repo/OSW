# EAC 100 m section-normal core spans: exploratory protocol v1

Declared 20 October 2026 against source-intake commit
`82c290a8163e2978ff1cd1dec81073e231113273`, before computing this operator's
spans or success counts. Original source fields, their overview and availability
have been inspected. This is not a blinded experiment or scientific admission.

Compass-label correction after the first calculation: the actual source
bearings are about81 degrees, so the right-hand normal is generally southward
with an eastward component. The initial wording said southwestward. Only that
description was corrected; projection signs, geometry, thresholds, scenarios,
membership and numeric outcomes were unchanged. Initial protocol SHA256:
`f44ea15abb340b636948e7ce27e5460054c8760a8080229085c4183332f479c3`.

## Question and scope

Can the retained processed EAC product bracket a peak-connected core on its
fixed sampling section at100m on each recorded date? A resolved span measures
distance **along this source section**, not a flow-normal physical width,
whole-current width, annual extrema or independent daily observations. The
mapped source has five-day filtering, SOM filling and much wider original
instrument separation than its output spacing. The two unresolved documentary
QC/mapping discrepancies in the source intake remain unresolved here.

Use only the pinned100m subset and quality/query contracts from the intake.
Attempt all3770source dates in original order, including629all-missing dates.
Do not repair source fields, substitute another depth or deployment, select
cleaner dates, fill nulls or rotate by an angle inferred from a desired answer.

## Section geometry and component

1. Use WGS84 inverse geodesics for consecutive original longitude/latitude
   positions in source order. Their cumulative distance is the section
   abscissa. It is not the distance travelled by a parcel.
2. For position i, obtain the forward bearing theta along the section from
   position i-1 to i+1. At either end use its only adjacent pair. Bearings are
   clockwise from true north in degrees; convert to radians for trigonometry.
   No regression, velocity fit or smoothing chooses the bearing.
3. The source-order tangent is `(sin(theta), cos(theta))` in east/north
   components. Its right-hand normal is `(cos(theta), -sin(theta))`. Preserve
   that declared orientation on every date: positive denotes the generally
   southward side of this offshore-going section, not speed magnitude.
   Do not flip orientation to make a date's strongest flow positive.
4. Project paired geographic source velocities as
   `q = UCUR*cos(theta) - VCUR*sin(theta)`. Retain U, V, bearings and projected
   q as separate values. A locally varying normal changes the diagnosed
   component; it does not reconstruct a continuous current axis.
5. Exclude source positions with `BOTTOM_DEPTH <= 100 m` from this diagnostic,
   while keeping them unchanged in the original corpus. These include the
   prescribed bottom-zero cells. Missing/bottom exclusions are barriers, not
   measured zero-flow endpoints. No boundary crossing may use such a cell.

## Prespecified central cases

For each original date and fractions0.4,0.5,0.6:

- Select the global maximum finite q over eligible positions. Exact ties use
  the smallest source index. If absent, retain an absent-profile outcome.
  If the peak is below0.3m/s, retain a weak-positive-core outcome. Do not replace
  it by a different lobe or by absolute/reversed flow.
- Set threshold to the fraction times that case's peak. Starting at the peak,
  walk each way through the connected run with q at least the threshold.
  Stop at the first below-threshold eligible pair, missing/bottom barrier or
  section-domain endpoint. No alternate lobe, gap bridge or coast extension.
- Interpolate a crossing only within two adjacent eligible, finite cells that
  bracket the threshold. Preserve both complete endpoint cells and their
  source indices/distances/values. Equality selects the first threshold point
  reached outward from the peak; do not extend an equal-valued plateau.
- Report paired crossing separation only when both sides resolve. Preserve
  each one-sided result and its barrier reason otherwise; never assign zero
  width to a missing side. The0.5case is primary, not selected after results.
- Retain the minimum/maximum possible separations between the two boundary
  cell brackets as **sampling-support intervals**, not error bars. Source grid
  spacing is not physical resolving power. Display central spans to whole km;
  preserve raw calculation values for reproduction. Do not rank whole currents
  from these regional diagnostic spans.

## Supplied-error sensitivity, without a confidence claim

At each eligible position with paired nonnegative supplied velocity uncertainty
fields, define
`a = abs(cos(theta))*UCUR_uncertainty + abs(sin(theta))*VCUR_uncertainty`.
This is the conservative algebraic sum of projected supplied magnitudes. It
assumes neither component independence nor a universal confidence convention;
it is not a statistical interval or a proved bound on actual velocity error.

Apply the same component-span rules independently to q-a and q+a, with the
same three fractions and0.3m/s peak gate. Every scenario selects its own global
peak under the same deterministic rule, retaining peak changes and failures.
Do not interpolate a missing uncertainty or borrow the central case's success.
Keep all nine outcomes per date (33930attempts) labelled central, minus supplied
component magnitudes, plus supplied component magnitudes. Their spread is
assumption sensitivity, not temporal variability or width uncertainty.

## Required records, figures and verification

Store every date, scenario, threshold, masks, peak index/component, full
crossing brackets, resolved/unresolved reason and optional central separation.
For resolved peaks retain original U/V and the ratio of along-section to normal
velocity as a local obliqueness diagnostic; do not use it as a width correction.
Zero/absent normal components retain undefined ratios, not infinities.

Summaries expose attempted and resolved denominators per original calendar
month and scenario; missing dates stay attempted and separately labelled.
Any numerical distribution is explicitly conditional on successful bracketing,
not a physical annual min/max or seasonal climate range. Different years are
not collapsed into an invented representative animation.

The standalone figure must show all central primary outcomes including gaps,
monthly denominators and fixed example source indices0,1885,3769. Examples
are not replaced if unresolved. Interactive views must expose every source
date, failure, scenario, crossing cell support, exact raw fields and the fixed
section map; diagnosed crossings remain section intersections, not polygons.

Independent tests cover projection orientation/known vectors, local bearings,
bottom barriers, missing sides, weak/reversed flow, plateaus, ties, multiple
lobes, equal thresholds, irregular spacing, source-error scenarios and exact
source reconstruction. Native/WASM queries and the real browser must agree.
No physical width, annual range, observation-date promotion or existing
inventory/sample change is authorized by this diagnostic protocol.

Primary context: [Sloyan, Cowley and Chapman (2024)](https://doi.org/10.1038/s41597-023-02857-x),
[CSIRO source DOI](https://doi.org/10.25919/sfw7-hc46), and the exact intake
acquisition/quality receipts. These sources establish the product and support;
the threshold and projection operator above is an explicit OSW exploratory
choice, not a method attributed to the provider.

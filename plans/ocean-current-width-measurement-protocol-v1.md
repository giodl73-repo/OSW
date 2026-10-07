# OSW current width measurement protocol v1.20

Effective 2026-10-04. Editorial width evidence remains separate from canonical
lengths and from OSW reference-route sensitivity. Not an official standard.

## Definition and required records

### General angular ensemble summaries

Use `ensemble_angular_summary` for author-reported general meridional jet
scales without a specific section center or occupation. Preserve angular units
and normalize approximately to kilometres using WGS84 at the equator only when
the scope is equatorial. This computational latitude is not a current location;
no geographic edges, fixed depth, exact dates or seasonal extrema are invented.
Keep a shared source-claim ID when one statement supports multiple current
records: linked identities are not independent measurements. Preserve regional
narrowing, merged-current boundary ambiguity and sampling limits. Hide the
width bar; retain static route context separately. Record source-audit checksum
and require renewed extraction if it changes. Neither PV-front scales nor core
position excursions may become current width or annual width ranges.


### Hydrographic core records

Preserve a source's property-based boundary equation and environmental reference
alongside local width evidence. A salinity-core boundary is a water-mass metric;
it does not establish paired velocity edges or a fixed-depth current envelope.
Source section-distance coordinates remain separate from reconstructed axes.
Keep regional spans, local values, mixed occupation dates and source conflicts
explicit. Their spread is neither annual variation nor a confidence interval.
PGW extractions use phase kind `campaign_hydrographic_core`, with source audit
checksum and section IDs. Compare each value/range directly to that pinned
extraction; retain null exact combined dates and fixed-depth geometry. They
count as scoped editorial evidence, with ranking and full-current admission
false. Never animate mixed section locations as seasons.

Width is a transverse span of a declared current feature, at a specified
region/section, time and vertical support. A current name does not define one
constant width. Retain local and seasonal values separately.

1. Identify stable current ID, branch/feature and geographic scope.
2. Identify the width metric: velocity core, broader velocity envelope,
   hydrographic front/water mass, plume, author-reported current width or
   fixed-orientation section span. Different metrics are not interchangeable.
   A one-sided core-to-edge span must retain that label: it is neither a full
   paired-boundary width nor evidence for doubling it. Record boundary sides.
3. Declare depth/layer and season/dates. A vertically integrated current extent
   does not imply that width applies at every depth.
4. Record boundary definition, section orientation/geometry, source URL,
   citation, passage and retrieval date. Unspecified published boundaries
   remain explicitly unspecified, not replaced by an invented speed threshold.
5. Separate published observations, published regional summaries, OSW
   model-derived estimates and editorial hypotheses. An approximate prose
   value may be retained as source evidence without claiming independent
   scientific approval or uniform full-current coverage.
6. Store kilometres, approximate value and/or range, with range meaning.
   Unknown is null, never zero. Retain source precision for published values;
   choose justified rounding for new estimates. A seasonal pair is not an
   uncertainty interval.
7. Do not infer width from drawn line thickness, route-coordinate offsets,
   movie swirls, cross-stream core position, distance to coast, shelf width
   or a transport number alone. Fixed-orientation section spans must not be
   relabelled perpendicular-to-flow widths without geometric evidence.
8. Do not apply a local width uniformly along an entire reference route or
   generate an occupied polygon by buffering a line with that number. Width
   evidence alone cannot establish state containment/intersection or NASA
   identification. No whole-current area equals length times local width.
9. Do not rank incompatible width types or multiply them into volume or
   transport estimates. Full-current representative width requires explicit
   along-route weighting and temporal/layer support, independently reviewed.
10. Pin ledger/protocol provenance, preserve evidence records and record review
    gates. Proposed identity additions remain separate until canonical admission.

## Future model-derived widths

Use a suitable velocity product at a declared depth or averaging layer and
source-defined current corridor. Define cross-flow sections perpendicular to
a reproducibly diagnosed local axis. Declare speed/direction thresholds,
reference/background subtraction if used, interpolation, coast treatment,
missing-data rules and splitting/merging rules. Measure geodesic boundary
separation. Keep each section and time sample, test sensitivity to boundary
choices, and report regional variation. Product resolution must resolve the
current; a coarse product cannot validate a narrow shelf current merely by
returning a number. No universal threshold is adopted for every current here.

## Initial inventory and verification

Two Northern Current seasonal values (about 25 km winter, 40 km summer) are
published regional summaries from Berta et al. (2018), introduction. They are
not the December 2011 survey widths and not a matched width profile for the
OSW 700 km reference route. Four existing ledger width mentions are queued for
source/definition review. The remaining 95 names are not yet assessed.

`analysis/check_current_width_inventory.py` checks identity coverage, metadata,
finite positive values, range meanings, nonadmission status and provenance.
Scientific boundary support and representativeness require review. Changing
metric definitions or aggregation rules requires a protocol revision and impact
assessment; adding scoped source records does not.

## Seasonal variation, ranges and margins

Keep three separate meanings: temporal/seasonal variation, a span of observed
samples and measurement/assumption uncertainty. Each range records its kind,
sampling coverage and aggregation method. Retain approximate seasonal values
with seasons attached; their span is not proof of absolute annual extrema.
For seasonal lengths, match object, branch, layer, extraction method and gate
convention, or explicitly record incompatible scope. The two Somali routes
currently have different spatial extents and cannot supply a full annual
minimum/maximum by taking their smallest and largest lengths. Existing length
scenario envelopes are assumption sensitivity, not annual variability.
Annual min/median/max requires a declared adequate time series; incomplete
seasonal coverage stays incomplete. Unavailable error margins remain null.

## v1.1 impact assessment

Added explicit one-sided boundary support and mixed-evidence playback rules.
Existing Northern seasonal summaries and Azores dated sections retain their
definitions and numerical values. New Mediterranean Undercurrent observations
remain separate by method, location and sampling: the ensemble offshore span
and May 1993 survey band do not form a seasonal pair. Automatic playback needs
an explicitly compatible seasonal group or labelled seasonal route frames;
multiple observations alone do not authorize seasonal animation. Velocity
variability is not width uncertainty. No canonical measurements are changed.

## v1.2 source-reported ranges without a midpoint

A source may report only a typical regional span, without a single value or
paired dated measurements. Preserve that span and its source precision. Leave
the approximate single width null; do not manufacture its midpoint, mean,
median, seasonal endpoints or confidence interval. Record the range kind as
`reported_typical_regional_width_span`, with region, layer, temporal support
and missing boundary definition. A regional summary is not a seasonal pair.
Do not render a single-value width bar for a range-only record. Annual extrema
and measurement uncertainty remain unknown unless separately supported.

Impact: existing single-value records and seasonal summaries retain their
values and definitions. Gaspé can retain its sourced 10-20 km typical range
without a new representative width. Derived section-series provenance must be
refreshed against this protocol; its numerical algorithm is unchanged.

## Transport-integration boundary example (v1.2 clarification)

A fixed coast-to-mooring integration interval can include reversals and background
flow. It does not diagnose lateral current edges by itself. The Antilles study's
49.4 km coastline-to-site-B integration span is retained as a rejected width
inference in its source-scope audit, not admitted as a physical width. This
applies existing rules 2, 4 and 7; no metric or aggregation definition changes.


## v1.3 author-defined fitted-profile scales

A published effective width may be a fitted profile parameter rather than a
paired-edge span. Retain the source's terminology, model equation, parameter
units, fitted component, centering convention, sample count and sampling scope.
Use a distinct metric `gaussian_e_folding_distance_from_profile_center` for a
profile `V(x) = A exp(-(x/a)^2)`, where `a` is in kilometres. The algebraic
interpretation of `a` as the center-to-e-folding distance is an OSW inference
from the stated equation. It is not a paired-boundary full width, standard
deviation or full width at half maximum. No conversion to those metrics is
admitted by this record. Unknown geographic edges stay unknown.

Classify a multi-crossing fitted profile as `survey_profile_composite`, not a
seasonal summary. Store the cruise window separately from actual sampling
bounds: a cruise window does not prove the first/last observation dates of the
composite, particularly where a source says summer expeditions in the plural.
An explicitly described vertical average for one illustrated section must not
be transferred to the entire composite without evidence. If that support is
unresolved, state it and leave fixed layer bounds null. Preserve missing fit
uncertainty as null; the fit scale is neither a confidence interval nor annual
variability. No rank, seasonal animation, route buffering, area or transport
inference follows.

Impact: previous eight scoped width records retain values and definitions.
North Cape Northern-branch evidence adds a separate approximately 8 km fitted
scale from 15 frontal crossings in 2007. It does not describe the Central branch
or the full North Cape system. Existing Gulf Stream derived-series numerical
algorithm and frames remain unchanged; refresh general-protocol provenance.


## v1.4: Source angular section spans with month precision

Retain an explicitly author-reported latitude width as an angular section-span
metric. Convert latitude degrees to approximate kilometres using WGS84 meridional
distance, normalized symmetrically around the source-reported center latitude.
Normalization limits are computational support only: they do not establish
observed paired edges, an occupied footprint or exact flow-normal width. Store
source angular span, center, section longitude, conversion method, unrounded
result and rounding to 10 km. Unknown threshold and fixed-depth support remain
unknown. Do not substitute chosen transport boxes or model half-widths.

Use `phase_kind: month_dated_section`, `time_precision: month`, and
`observed_month: YYYY-MM` when only a survey month is reported. Keep
`observed_period`, `calendar_months`, `section_geometry` and fixed-depth bounds
null. A validation-only first day may check calendar syntax, but must never be
stored or displayed as the observation date. Preserve one record per source
survey month; matching widths in different years do not establish a seasonal
cycle, climatology, persistence, annual extrema or an uncertainty interval.
No seasonal playback, whole-current width, buffering or width ranking admission.

Application: Bourles et al. (1999), section 4.8, p. 21163, reports a two-degree
latitude width centered at 5 N at 35 W in February 1993 and April 1996. Its WGS84
unit conversion is about 221.17 km, reported as approximately 220 km. This is
not the 2019 model half-width or the 2020 fixed transport box. Source boundary
threshold remains unspecified and the historical density-core context does not
become a uniform 65–270 m layer.


## v1.5: Reported flow bands in composite coast-distance profiles

An author-described current band between two offshore distances may be retained
as a local profile-band span, with value equal to farther minus nearer coast
distance. Record both source distances in km. They locate the band; the farther
offshore distance alone is not its width, and the two distances are not a width
range, uncertainty interval or seasonal extrema. The span describes the named
band in the source profile, not necessarily the entire current or every depth.
An unspecified velocity threshold stays unknown.

Use `phase_kind: ensemble_profile_band`, measurement type
`published_composite_coast_distance_flow_band`, and metric
`author_reported_offshore_flow_band_span`. Retain averaging-bin dimensions,
overlap and sampling-context month windows. These windows are intermittent
context, not continuously observed dates for the particular band. No exact
observation period, fixed-depth bounds, map section geometry or calendar-phase
assignment may be inferred. Seasonal play, whole-current width, rank and annual
extrema remain ineligible. Source distance-axis orientation does not establish
an exact flow-normal section or footprint.

For a regional segment of a broader named current, retain the original source
current label and parent ID, plus the explicitly editorial segment assignment.
Validate the parent relation against the current ledger. Do not duplicate the
measurement as two independent observations or transfer parent seasonal widths.

Application: Poulain et al. (2012), section 4 pp. 273–274 and discussion p. 276,
reports Northern Current flow off Menton–Nice between 15 and 35 km from coast:
approximately 20 km local band span. The source uses 4 km cross-shore by 30 km
along-shore bins with 50% cross-shore overlap. Source sampling context is
June–October 2007 and October–November 2008. CODE/ARGOSPHERE surface drifters
have different water-following properties; wind slip and temporal intermittency
remain explicit. Source Imperia limit of 20–30 km from shore is a distinct
coast-to-limit statement and is not admitted as a paired width here.


## Relative-velocity threshold section

`survey_threshold_section` records a published local section width whose two
lateral boundaries are defined relative to a stated jet velocity maximum.
Retain the fractional threshold and exact reference statistic; neither is a
universal current-width criterion. A campaign month window is context, not
exact section occupation dates or a recurring calendar phase. Keep fixed
layer bounds and section endpoints unknown if not extracted. A separately
reported frontal depth scale is not a uniform depth layer for the width.
No whole-current width, annual extrema, confidence interval or seasonal
playback follows from one such section.


## Mean velocity-profile zero-contour section

`mean_velocity_section` records a published width bounded by zero contours of
a time-averaged cross-section velocity profile. Average velocity first, then
find boundaries: this is not the average of instantaneous widths. Retain
section position, signed component, averaging period at source precision and
method/grid limits. A two-core current can occupy one reported mean-flow band;
do not assign that band independently to each core or to a selected branch
route. Preserve unknown edge coordinates and depth bounds.

Different section widths are spatial samples, not a seasonal range, uncertainty
interval or annual extrema. Whole-current widths and seasonal playback remain
ineligible. A half-maximum domain used for current intensity is distinct from
the zero-contour width definition.


## v1.8: Dated subsurface current/water-mass band spans

An author-described latitude band occupied by strong flow and a water-mass
signature over a depth range can support a local meridional band-span record.
It does not establish velocity-defined paired edges, an occupied polygon or
full width at every depth. Preserve the reported latitude limits and depth
range separately. A depth range for the feature is not a uniform axis layer.
An unspecified speed threshold stays unknown. Do not use the survey's full
latitude coverage or transport integration box as this span.

Use `phase_kind: dated_band_section`, type
`published_dated_subsurface_band_span`, metric
`author_described_subsurface_meridional_band_span` and day-precision campaign
bounds when explicitly reported. Convert between the source latitude limits
with WGS84 at the source section longitude; store the unrounded result and
round to 10 km. Keep section geometry and fixed axis-layer bounds null.
Whole-current width, ranking, annual extrema and seasonal playback remain
ineligible. Display the metric as a described subsurface band span, with no
full-width bar or route buffer. Existing metrics and values are unchanged.

Application: Siswanto, Kusmanto and McPhaden (2019), Results/Conclusions,
reports a strong saline eastward band from 1.2 S to 1.5 N at 90 E, in the
80–150 m depth range during 1–3 March 2017. Its meridional span is about
300 km. This differs from the 2 S–2 N survey support and does not set a
current-wide dimension or connect observations at other longitudes.

## v1.9: spatial distribution of a climatological three-dimensional core

Retain a source-reported median and min/max across longitude sections as
`climatological_core_distribution`, with metric
`maximum_meridional_extent_of_3d_threshold_core`. Identify the velocity
component, strict threshold, model/version, averaging years/months and the
source's cross-depth extent rule. The scalar is the median across longitudes;
`width_range_km` is a spatial range, labelled
`spatial_range_of_climatological_threshold_core_spans`.

These are widths of a climatological threshold-core diagnostic. They are not
averages of instantaneous widths, fixed-depth paired-edge full widths,
flow-normal widths, seasonal extrema or uncertainty intervals. The median
must lie within the spatial range. Retain null section geometry, fixed depth
bounds, exact observation dates and calendar playback; full-current width,
ranking, annual extrema and playback eligibility remain false. Omit the
full-width bar. Do not buffer an editorial route with this median or range.

Version impact: additive evidence class; existing 16 records keep their
metrics and values. Revalidate all width records and refresh the protocol
and seasonal-association provenance hashes. No earlier range is reclassified.

### Classification regions are not width edges

A latitude domain identified by dominant frequency, harmonic amplitude, phase
or EOF mode is a classification region. Do not convert its angular span into
current width unless an independently stated velocity-boundary metric supports
that interpretation. A meridional section label alone does not supply paired
edges or annual minima/maxima. Preserve product/depth/time definitions and
text/caption inconsistencies; review different depth averages separately.


## v1.10: author-reported width span of a seasonal mean section

Use `seasonal_mean_width_range` for a source's approximate width interval
reported for a seasonal mean velocity section. Retain a null representative
scalar and `author_reported_width_span_of_seasonal_mean_section` range kind.
Declare section/reference latitude, spatial pooling, averaging sample years,
cruise identifiers, sampled months, source season months and the averaging rule.
The source season may include months absent from its actual sampling; distinguish
those explicitly. Record layer context without manufacturing a fixed-depth
width or paired edges. Retain null exact dates and unextracted geometry.

The interval is neither annual extrema nor a confidence interval. Width of a
mean section is not the mean of instantaneous widths. No midpoint, full-width
bar, route buffer or seasonal playback is inferred. An adjacent transport
integration span and surface-flow corridor are separate quantities. This additive
class leaves the existing 17 records and metrics unchanged.


## v1.11: month-dated reported current-band limits

A month-dated section may describe latitude limits of a current band without
calling it a paired-edge width at one depth. Retain `month_dated_section` and
`author_reported_meridional_angular_span`, but supply the reported limits in
`angular_span_conversion.source_reported_latitude_limits_degrees`. Set the
source-reported center to null and compute `normalization_center_latitude_degrees`
from those limits strictly for WGS84 unit conversion. Record the center's role
as `computed_from_reported_limits_for_unit_conversion_only`. Neither limits nor
center become a current axis, fixed-depth edges or a flow-normal width.

Display as a described meridional band span with no full-width bar. Month
precision, unextracted geometry, depth-dependent counterflow, missing exact days
and annual gaps remain explicit. Reproducible conversion and 10 km rounding do
not add observational precision. Existing records keep their metrics and values.

## v1.15: regional scalar prose width summaries

Use `regional_scalar_summary` with `published_regional_scalar_width_summary`
and `author_reported_regional_current_scale` when a source gives an approximate
regional current width without paired section edges, occupied dates or a fixed
measurement layer. Preserve a single scalar and null width range. Retain a pinned
scope-audit file and hash, source paragraph, branch exclusions and access limits.
Geographic latitude limits describe the regional extent, not cross-stream edges.
Bottom-depth contours describe bathymetry, not instrument or averaging depths.
Neither contextual mean-speed ranges nor publication year supply a boundary
threshold or an observation period. Never buffer a route by this scalar.

Display the value as a regional source summary with no full-width bar, inferred
edge locator or seasonal playback. Full-current representativeness, confidence
intervals, annual extrema and width-ranking eligibility remain false; exact
section geometry, fixed layer, observation period and calendar months remain
null. Underlying observations and definitions require independent review before
any canonical measurement admission. Existing measurements retain their values.

## v1.16: oblique mean-section velocity spans

Existing `mean_velocity_section` zero-contour metrics may use an oblique source
section. Declare `section_axis_kind=oblique`, source section ID, rotation angle,
source flow label and month-precision mean-field period. A section's latitude
coverage is not its along-section distance: use the author's kilometre value
without a meridional conversion. Keep section longitude and endpoints null until
coordinates are recovered; rotation does not supply a location. Pin a source
scope audit and preserve the source-specific identity mapping. Continuation names
must not merge canonical currents or imply a hard physical naming boundary.

Width is bounded by zero contours of the time-mean rotated cross-section
component. A half-peak intensity window is a separate metric. Averaging before
edge detection does not produce a mean of instantaneous widths. Preserve table
and prose discrepancies as unresolved conventions; they are not error intervals
or seasonal extrema. Keep annual/ranking/whole-current/playback flags false,
fixed depth and occupied dates null, and omit edge locators and full-width bars
when geometry is unextracted. Multiple regional sections do not supply one
representative system width or a seasonal range.

## v1.17: institutional regional prose summaries

The regional scalar class also permits an institutional science-plan summary.
Pin each permitted source audit to the current identity, scalar, source URL and
exact locator. Identify synthesis and access limits; cited underlying studies
remain unverified until inspected. A typical depth extent is contextual, not a
fixed measurement layer. Do not combine a typical current width with a separate
strong-influence scale, array span or eddy diameter into a width range. General
seasonal strength statements do not supply seasonal width values. Keep the same
null section/time/layer fields and false full-current, annual, ranking and
playback eligibility as other regional scalars. Existing numerical series are
unchanged; refresh general-protocol provenance.

## v1.18: monthly climatological fitted widths

Use `monthly_climatological_fit` for source-reported calendar-month averages
of widths diagnosed per cycle from a fitted profile. Preserve averaging order:
mean fitted widths are not widths of the monthly mean velocity field. Retain
profile equation, width coefficient, angle convention and source boundary
description. Do not silently replace an approximate half-maximum coefficient
with an exact mathematical threshold. Pin source PDF and scope audit hashes.
A calendar month is not an occupied date. Retain unresolved period labels,
null exact occupation/section/layer geometry, and false whole-current, ranking,
confidence, annual extrema and playback flags while the complete monthly curve
is unextracted. Keep filter-window lengths, transport-layer assumptions and RMS
variability separate from width, measurement depth and confidence intervals.
Do not interpolate missing months or animate them as a complete annual cycle.

## Stream means of diagnosed threshold widths

Use `stream_mean_threshold_summary` for source-reported temporal and along-stream summaries of cross-stream spans diagnosed at repeated time steps. Retain velocity component, cutoff, section orientation, original product and interpolation grid, diagnosis-before-averaging order, regional domain and study years. Keep unresolved averaging weights and season-to-month membership explicit. A study year range is not exact occupied section dates; a bathymetric isobath is not a fixed measurement layer.

Distinguish seasonal means from study-period means using `temporal_statistic` and `season`. Neither is width of the mean velocity field. Local seasonal tendencies can oppose the regional mean. Do not combine values into a physical annual range or assign confidence intervals from core-position standard deviations, alternate-product means, interpolation grid, or intrusion reach. Source graph geometry requires its own extraction; scalar means never create map edges or route buffers. Pin PDF and scope audit; retain false whole-current, ranking, annual extrema, full-width and playback admission flags.

## Total-flow boundary and anomaly separation

Paired boundaries must belong to the declared total-flow metric and reference
state. Zero crossings of a velocity anomaly do not define total-current width.
Model/averaging-window limits likewise do not constitute observed edges.
Relative-geostrophic fields retain their reference pressure, separately from the
current layer and axis depth. Combining a mean and anomaly requires reviewed
compatibility of layer, reference state, averaging, grid and method. Keep local
section diagnostics, velocity-anomaly spans and whole-current width claims
distinct. This clarifies the existing source, boundary and comparability gates;
it does not change any existing admitted value or range calculation.

## v1.20: coast-to-mean-isotach section spans

Use `eulerian_mean_section_span` for an author-reported offshore distance from
the coast to a mean zero-velocity isotach. Preserve section identity, approximate
section latitude, month-precision averaging window and the stated boundary
convention. A coastal boundary is not a second extracted zero contour. Keep the
author's mean convention without claiming independent reconstruction of the
averaging order. A fixed transport integration boundary and an instantaneous
moving jet boundary are separate methods.

Pin the source audit and preserve access limitations. A reported vertical
extent is not a fixed measurement layer; averaging months are not exact section
occupations or seasonal membership. Leave boundary coordinates, confidence,
annual extrema, whole-current/ranking and geographic playback eligibility
unresolved or false. Omit a map footprint and full-width bar. Different arrays,
periods or model products remain separate records rather than an annual range.

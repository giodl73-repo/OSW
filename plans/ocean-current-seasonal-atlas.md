# Seasonal ocean-current atlas

Working plan, 2026-10-03. User intent: animated current pages showing how
length, width and geography evolve throughout the year, with margins/ranges.

## Current pilot

`almanac/seasons.html` indexes all 100 names, defaults to Northern Current,
and cycles sourced winter/summer regional width summaries of about 25/40 km.
No complete annual length series or seasonal footprint is admitted. Static
reference geography is labelled independently of the changing width bar.
Animation tween values are display transitions, not interpolated measurements.
Unknown records disable playback and hide the numeric bar. Reduced motion
removes the transition; playback is user initiated and pauses on hidden tabs.

## Required next data for spatial annual animation

Each frame must carry stable current/branch ID, measurement/protocol versions,
time window or seasonal regime, layer/depth average, source/product version,
source locator, extraction algorithm and hashes. Preserve route centerline and
source-backed paired boundaries or occupied geometry separately. A width
summary cannot be substituted for a footprint. Keep length/width estimates,
range kind, raw sampling coverage and uncertainty methods attached to frames.

Choose a coherent annual cycle per current. A documented climatology may
supply month averages; dated observations supply a specific-year sequence.
Do not mix unrelated years and call it one observed year. If published seasonal
states have no exact calendar boundaries, show named phases without invented
monthly values. Northern/Southern Hemisphere and monsoon regimes have their
own source-defined calendars. Monthly values require monthly evidence.

Before computing annual length ranges, align object, layer and gate convention.
Seasonal route separation/termination may move physically, but its naming rule
must remain reproducible. Record topology changes, reversals, mergers and
branches explicitly. The current two Somali routes are different scopes and
cannot define annual whole-current extrema by taking the smallest/largest.

Before computing width ranges, retain cross-flow section definitions and
sampling locations per frame. Distinguish core, current envelope, front/plume
and fixed-orientation section spans. Report regional distributions and
along-route weighting explicitly; do not multiply a local width into whole
current area, volume or transport. Unknown error margins remain null.

## Presentation target

- Play/pause and timeline, keyboard-accessible controls and reduced motion.
- Source-backed monthly or named-season maps, direction and branch changes.
- Synchronized scoped length/width values with separate seasonal/sample spans
  and uncertainty bands; no inferred confidence level from editorial offsets.
- Visible missing frames; interpolated geometry allowed only as an explicitly
  labelled illustration with no new measured extrema or evidence joins.
- OSW state intersections recomputed from each eligible frame geometry, with
  physical/editorial relation meaning retained. Centerline intersection and
  occupied-footprint intersection are different relations.
- NASA crop/film links by geography and compatible time/layer evidence. A
  geographic crop match alone does not identify a physical current or season.
- Source and method provenance plus downloadable frame series for each page.

## Delivery gates

First extend source-backed seasonal measurements and identify suitable
velocity products. Review layer/resolution and extraction rules per current.
Generate and inspect frame geometry; audit full series and field consistency;
compare independent observations where available. Only then animate changing
physical shapes. Admit reviewed data into canonical measurements/releases
through existing science/release gates. Internal .roles review is separate.

## Verification

Width inventory checker and 20 focused tests pass; full atlas checker and
Chromium browser suite pass. Tests cover winter-to-summer playback, pause,
unknown current, static-map loading, seasonal-range interpretation and mobile
320 px reflow. Desktop page screenshot visually inspected.

## Somali spatial phase playback (2026-10-03)

Two hash-pinned existing editorial route candidates now supply discrete Somali
map frames: northeast winter monsoon southward branch (about 1,500 km;
1,100-1,800 km sensitivity) and June-July northward southern limb (about 600 km;
500-700 km). Source scopes differ; annual length/width ranges remain null.
Source-supported June-July months are recorded; winter exact months remain
unspecified. No intermediate path morph, occupied footprint or observed monthly
field inferred. The map image and contextual route/NASA link change with phase;
Northern Current continues to use its static reference route with width playback.

Check with `python analysis/check_current_seasonal_route_frames.py`. Associations
pin reports and repeat their source/layer/time fields. Validator rejects stale
associations, duplicate frames, incompatible metadata, invalid calendar entries
and false annual-extrema admission. Direct `?current=somali` navigation and
route-card links open the relevant current. Canonical lengths/ranks unchanged.

Verification: 22 focused tests, frame/width/protocol audits and full almanac
checker pass. Full browser suite covers phase direction, map replacement,
length/envelope, changing scope, unknown width and annual-range exclusion.
Somali summer page screenshot visually inspected.

## Dated Azores section widths (2026-10-03)

Added two 110 km meridional spans for Azores Current and Azores Countercurrent
from Comas-Rodriguez et al. (2011), abstract/data/current-domain discussion.
26 Oct-1 Nov 2009 station dates recorded; source caption's 2010 conflicts with
explicit data text and is retained as an open provenance issue. Each record
has section-limit geometry, vertical support and boundary definition; the
geometry is a section, not a current footprint. Not a perpendicular-flow axis
width, seasonal typical value or uniform full-current width. No supplied error
range or annual extrema inferred.

Inventory: four width records for three of 100 names, two mentions pending
source review and 95 not assessed. Temporal evidence distinguishes seasonal
summaries from dated sections. A single dated record disables playback and
shows its dates; bar scale adapts without clipping 110 km to a 50 km limit.
No new route length or canonical measurement admitted.

Azores verification: 23 focused tests, width/frame/route-protocol audits, full
almanac checker and full Chromium browser suite pass. Azores screenshot
visually inspected. Seven-role audit:
`signals/roles/check/azores-section-widths-roles-check-2026-10-03.md`.

## Mixed boundary and sampling evidence (2026-10-03)

Mediterranean Undercurrent: Bower, Serra and Ambar (2002), detailed sections
3.1-3.2, distinguish a roughly 30 km ensemble core-to-offshore-zero-crossing
span from a roughly 10 km May 1993 Portimao geostrophic band. The former is
one-sided and cannot be doubled into a full width. Velocity standard deviation
is not width uncertainty. Float deployment dates do not equal the observation
window. These records can be inspected separately and cannot play as seasonal
phases or define a 10-30 km annual range.

Width protocol v1.1 adds boundary-side and compatible-playback rules, with
impact assessment; prior numerical values remain unchanged. Current coverage:
six records, four of 100 names, one Gaspé mention pending full-source review,
95 unassessed. Gaspé original publisher retrieval returned 403 and the alternate
PDF failed; its legacy range has not been admitted.

Verification: width checker, 24 focused tests and full Chromium almanac browser
suite pass. New checks reject one-sided/full-width relabelling and false
seasonal types; browser checks two manually selectable Mediterranean records
with playback disabled. Screenshot visually inspected at 1100 px; existing
suite exercises 320 px reflow. No canonical measurements or annual series added.

## Dated spatial timeline (2026-10-03)

`almanac/dated-current.html` plays five pinned NOAA LSA daily surface geostrophic
diagnostics, 18 and 24-27 September 2026. `analysis/build_current_dated_timeline.py`
reconstructs geometry from existing local velocity subsets using the same fixed
seed [-72.875,36.875], 10 km midpoint steps and speed/gate stop rules. Each frame
retains dates, coordinates, stop reason, traced length, source/algorithm/map
hashes and recomputed diagnostic-line intersections with OSW states.

The 18 September trace stops early at 1,550 km; it is explicitly truncated,
not a shortening of the Gulf Stream. Gate-reaching dates trace about
2,297/2,277/2,290/2,338 km. These are scoped frozen-field diagnostic lengths,
not whole-current lengths or canonical ranks. Width and positional uncertainty
remain unknown. Five intervening unsampled days are visible; playback advances
observations at equal screen time and does not interpolate geometry or time.

This develops the dated geometry/measurement/state-link presentation needed for
the annual atlas, while full-year comparable sampling remains outstanding.
NOAA CoastWatch product documentation was checked 2026-10-03; existing pinned
receipts preserve experimental product status and RADS 4.8.1. Attribution is
shown. No source refresh, new physical footprint or canonical admission.

Verification: dated-frame validator recomputes all five traces and state joins;
27 focused tests and full Chromium browser suite pass. Negative checks reject
annual inference, missing dates, false gate success and altered geometry.
Browser checks map/date replacement, truncation, gap labels, links and 320 px
reflow. Desktop timeline screenshot visually inspected.

## Twelve daily samples across 2025 (2026-10-03)

The timeline now defaults to 2025, with a selector retaining the September 2026
sequence. `analysis/fetch_current_annual_samples.py` explicitly acquires the
fifteenth day of every month, predetermined before download. Twelve pinned
daily subsets and an acquisition manifest preserve source bytes, retrieval
times, provider, grid, units, time bounds, processing algorithm and status.
`python analysis/build_current_dated_timeline.py --annual` builds twelve maps,
geometries, diagnostic lengths and dated state joins offline.

These are daily monthly-spaced snapshots, not monthly means or a climatology.
Eight traces reach the 50 W gate; January, September and October stop at low
speed and December at the integration distance cap. December circulates near
the seed, illustrating why accumulated streamline distance is not a current
axis measurement. The inherited tracer's cap check permits a final 10 km step
beyond the nominal 4,000 km cap (4,010 km recorded); this is retained as its
diagnostic algorithm outcome, not converted to a current length.

Processing changes from RADS 4.7.0 (January-July) to 4.7.1 (August-December),
all experimental. Each frame retains its version, and the UI cautions that
differences cannot be assigned entirely to ocean change. Annual ranges and
width/positional uncertainty stay null. Source/algorithm/state-map/figure hashes
remain pinned; new samples do not modify canonical lengths or ranks.

Verification: both five- and twelve-frame series validate with full trace and
state-join recomputation. 28 focused tests and full Chromium browser suite pass,
including year switching, all twelve fixed dates, failure retention, processing
breakpoint, cap explanation, download selection and 320 px reflow. 2025 August
screenshot visually inspected. Next: assess seed dependence and diagnose a
physically supported axis/boundary series before deriving seasonal lengths or
widths. Full-year sampling alone does not resolve those scientific gates.

## Seed/step sensitivity and hard cap correction (2026-10-03)

Each of the 17 dated frames now evaluates the full Cartesian grid of seed
latitudes 36.625/36.875/37.125 N at fixed 72.875 W and integration steps
5/10/20 km. All nine outcomes retain diagnostic distance, stop reason and
endpoint. Only gate-reaching scenarios enter a span, rounded outward to 10 km.
The span is finite methodological sensitivity, not statistical confidence,
positional error, width or seasonal variability. Failed scenarios remain in
the visible table; no successes means a null span. A selected failed trace can
sit outside the successful-alternative span, which is explicitly explained.

July 2025: nine successes, 3,480-3,690 km span. September: one success, not a
robust axis determination. December: zero successes and null span. Alternative
seeds can follow different branches or recirculations; this is an unresolved
axis diagnosis, not proof of current boundaries. The primary plotted line and
its state intersections remain independently scoped; no scenario width added.

The inherited cap overshoot recorded in the previous section is now fixed:
integration limits each step to remaining distance and stops at the cap, with
floating-point tolerance. December primary trace is now exactly 4,000 km, still
a failed downstream diagnostic. Original September representative and repeat
audits pass without numerical changes. Both timelines were regenerated and
their trace-algorithm/generator/figure provenance refreshed.

Verification: both timeline validators reconstruct every nine-scenario grid
and its aggregation; 31 focused tests and full browser suite pass. Negative
tests reject missing scenarios, altered spans, confidence/width relabelling,
invalid steps and cap overshoot (including a nondivisible final step). Browser
checks successful/no-success spans, nine visible rows, hard cap, expanded table
at 320 px and selector playback. July screenshot visually inspected.

## Fixed-section width candidates (2026-10-03)

`analysis/build_current_section_width_series.py` adds seventeen research-only
70 W section spans for the same dated fields, with native profiles, peak
selection, paired boundary brackets, interpolation, geodesic separation and
resolution flags. Its current-specific protocol is
`plans/gulf-stream-section-width-protocol-v1.md`; no universal width rule is
imposed on other currents. Select maximum eastward velocity in 35-41 N, require
0.15 m/s, and take nearest contiguous 50%-peak crossings on both sides. Missing
data or unbracketed sides yield unknown. This is a fixed-meridional eastward
component metric, not rotated total-speed/current-axis width.

Archer et al. (2017), section 3.4 and Appendix A, supplies relative-threshold
method context from Florida Current HF radar in jet coordinates. OSW's
location, gridded altimetry, component and section orientation differ; this is
not a reproduction of its numerical widths or evidence of their applicability.

Each frame shows the local candidate (nearest 10 km), 40/50/60% threshold-choice
span (outward 10 km), grid-bracket separation and nominal grid-spacing count.
Fewer than four spacings is flagged for resolution review; four or more does
not independently validate boundaries. Twelve sampled 2025 nominal values
span roughly 70-150 km, with count and processing versions retained. This is a
sampled candidate-value span, not annual extrema or isolated physical change.
The section peak is independent of the plotted streamline; widths are not
applied to it, buffered into polygons or used for state joins.

Width inventory now distinguishes six extracted records/four names, one
derived candidate series/Gulf Stream System, one Gaspé mention pending source
review and 94 names unassessed. The candidate file and its digest are linked to
the inventory. Source/identity/orientation/boundary and resolution gates remain
open before canonical admission; no existing published measurement changed.

Verification: section-series and width-inventory validators pass; 35 focused
tests include known triangular-profile crossings, missing/weak boundaries,
threshold/resolution tampering, false confidence and false annual-span claims.
Browser checks local values, definition, marginal-resolution warning, threshold
span and sampled-value span. July screenshot visually inspected.

## Davidson historical regional season — 2026-10-03

The full government report *Potential Pacific Coast Oil Ports*, Volume II
(Fisheries and Environment Canada, February 1978), Appendix II section II.1,
printed II-1 to II-2 / PDF pages 12-13, describes a northward surface strip
approximately 64 km wide along California and Oregon from October through
March, strongest in January. Retain source precision and source year, PDF
digest, geographic/layer scope and explicit month passage. This is a historical
regional synthesis, not a present-day width survey or monthly climatology.

Possible penetration into Vancouver Island coastal waters remains conditional;
the width is not extended there. Measurements 25 and 50 km off Tofino are
observation locations, not paired width boundaries. The separately described
50 km California Undercurrent below 200 m remains a different feature and layer.
No source figures are republished or buffered into occupied polygons.

The seasonal page permits inspecting this single historical phase; playback is
disabled. April-September width and seasonal route geometry remain unknown.
Missing phases do not imply zero width or absence, and no annual width range,
uncertainty margin, state join or canonical measurement is admitted. Width
inventory coverage is now seven extracted records across five names, one
derived series pending review, one pending source mention and 93 unassessed.
Existing measurement definitions and protocol v1.1 remain unchanged.

The width validator checks supported calendar months and historical year/digest
metadata; negative tests reject unsupported months and forged provenance.
Verification: inventory checker, six width tests and full browser suite pass;
Davidson screenshot visually inspected. Internal seven-role review records
historical applicability and boundary support as remaining scientific conditions.

### Davidson route and width association

One historical October-March frame now links the California-Oregon editorial
route to the existing 64 km regional source summary. The selector shows one
combined phase, avoiding duplicate width/map phases. Its role is explicitly
regional source context, never uniform route width or occupied footprint.
Association validation requires matching identity, source, calendar and phase;
source inventory is hash-pinned. Missing/wrong identities, changed calendar
and uniform-buffer roles are rejected by tests. Playback stays disabled for
this single phase. Three route frames across two names remain incomplete
annual coverage. The previous Davidson map-unknown state is superseded by this
scoped historical reference, not by an observed seasonal geometry.

## Balearic reviewed width unknown — 2026-10-03

Full Garcia-Ladona et al. (1996) PDF review finds a qualitative broader/shallower
comparison, not a numerical current-width definition. Storm Blas article
section 3 reports a 10-20 km upwelled-water band during a wind-driven event;
this thermal feature is not the named current velocity width. One prose date
2022 conflicts with its title/caption 2021; no dated metric is extracted.

A source-reviewed-without-comparable-width decision now records those passages
and source links, distinct from unassessed names. Its representative width and
annual range remain null, with no new measurement row. Tests reject numerical
admission or unsupported review status. Width coverage: seven records across
five names, one derived series pending review, one pending mention, one reviewed
unknown and 92 unassessed. Seasonal width-inventory digest refreshed.

Balearic selector shows the static editorial route with width unavailable and
play disabled. No summer/winter route or width pair is invented. Approximate
island-centre markers improve map orientation without replacing coastline
verification or changing any metric calculation.


## Gaspé typical regional range — 2026-10-03

The accessible author thesis verifies a typical 10-20 km regional width in
printed page 5 / PDF page 21 and an upper-width statement on printed page 14 /
PDF page 30. Its adjacent summer speed statement does not date the width range.
This is a regional literature summary, not a new dated transect observation.
Retain the thesis URL, digest, page locators, publication date and retrieval date.
The blocked AMS source remains blocked; no recovered-access claim is made.

Width protocol v1.2 adds a range-only regional record: representative width is
null, source range remains 10-20 km, and annual extrema and statistical confidence
remain unknown. No midpoint or single-value bar is rendered. Gaspé can be
inspected with its static regional route; playback is disabled. No seasonal
pair, uniform route buffer, state footprint or canonical metric is admitted.
The general protocol digest and existing derived-series provenance were refreshed;
all existing width values and the 17 derived section values are unchanged.

Coverage: eight extracted records across six names, one derived series awaiting
review, zero pending mentions, one reviewed unknown and 92 unassessed names.
Three route frames across two names remain incomplete annual coverage. Tests
reject fabricated midpoint, confidence/annual claims, seasonal phase, reversed
or invalid range endpoints and unsupported calendar months. All 39 current tests,
three measurement validators and full browser checks pass; screenshots inspected.


## Norwegian coastal seasonal evidence lead — 2026-10-03

The naming/scope audit records qualitative winter versus summer structure from
Skagseth et al. (2011), including the local Figure 4/5 hydrographic calendars.
No compatible numerical width pair, annual extrema or seasonal route geometries
are admitted. The new editorial route supplies static regional context only;
width inventory counts and seasonal playback eligibility remain unchanged.
Norkyst hindcast fields described by Christensen et al. (2026) are the next
potential source for monthly evolution. Inspect access/licensing, fixed sections,
layer and physical boundary definitions before extracting animation frames.


## Norkyst Ingøy hourly annual sequence — 2026-10-03

The archive's individual files are accessible through DAP2, despite aggregate
metadata timeouts and failure of the web reader for the catalog. Twelve 2024
snapshots are now pinned: fifteenth day, noon UTC, 10 m depth, same projected
index box and four-cell stride. Individual DAS metadata verifies source project,
dates, packing and CC BY 4.0. Raw responses, daily metadata, URLs, acquisition
receipts and retrieval times are retained. No full model volume is downloaded.

The fixed 24 E / 71.10-73.00 N section supplies 191 display samples per frame.
Bilinear interpolation requires four wet non-fill corners. Source coordinate
checks verify projection alignment; denser display samples add no resolution
to the 3.2 km subset. Velocity and salinity plots retain fixed axes across dates.
The page almanac/norkyst-section.html provides discrete playback, manual month
selection and a readable values table, and is linked from the seasonal explorer.

These hourly model snapshots include tides and weather variability. They are
not monthly averages, observed trajectories, climatology or annual extrema.
The section is regional coastal-to-offshore context, not exclusively the named
current. Source-water or velocity boundary rules remain unadmitted: whole-current
length, width and state footprint are still unknown. Existing width inventory
and route ranking counts are unchanged. Protocol v1.0 is hash-pinned to the
profile series. CC BY 4.0, provider credit and OSW modifications are visible.

Three focused tests verify reconstruction and reject invented metrics, dates,
values and annual extrema; land/fill profiles remain unavailable. The browser
check covers all twelve timestamps, actual profile changes, source links,
191-row tables, play/pause/manual/hidden controls, reduced motion and 320 px
layout. Desktop screenshot visually inspected. No verification process remains
running. Scientific admission is not supplied by this internal review.


### Synchronized Ingøy regional maps — 2026-10-03

Twelve maps now accompany the twelve section profiles. Both views use the
same pinned hourly model receipt, timestamp and 10 m layer. Fixed salinity
color limits (33.0-35.2) and arrow scaling permit comparison between frames.
The map uses the source polar stereographic grid with geographic contours;
true east/north model components are rotated into the projected plane while
preserving speed. Direct display of east/north on tilted X/Y would be incorrect.

The patch is entirely offshore. It is regional field context, not a coastline,
named-current occupied extent, inferred eddy identity or state footprint. The
24 E section is drawn independently; colors, arrows and orange line provide
no current-width boundary. No advection or intervening dates are invented.
A loading token hides the previous map until the selected image is decoded,
preventing an old map from being paired with a new date/profile during load.

Protocol v1.1 records map rules. Figure, source, helper, generator and protocol
hashes are pinned in the downloadable map catalog. Six focused tests pass,
including independent cardinal-direction projection checks, speed preservation,
source/profile synchronization and rejection of altered scope, dates and scales.
The browser checks all twelve map files, actual loaded images, dates and control
behavior. January and December screenshots inspected; footer/axis overlap fixed.
Existing canonical measurements and current-width inventory remain unchanged.


## Canary source-specific seasonal scope — 2026-10-03

The new scope audit keeps regional seasonal path descriptions separate from a
static reference route and from Lanzarote Passage upper/intermediate flows.
The 2015 study's Table 1 places the fall cruise in October, whereas section
2.1 prose says November. Resolve original station times before dated frames;
no silent choice or month assignment is admitted. Source data-access links
are research leads, not already acquired or validated records. Transport
uncertainties are not length/width uncertainties. Width inventory, playable
phase coverage and canonical measurements remain unchanged.


## Portugal seasonal identity guards — 2026-10-03

A static offshore reference route now has three northern gate conventions,
not three seasonal states. The scope audit separates near-surface offshore
Portugal flow from coastal current/countercurrent and slope undercurrents.
Irregular 1993–1994 drifter sampling cannot define twelve monthly geometries;
a statistical box and coastal drifter distance cannot supply offshore width
or whole length. Annual length/width ranges remain null and playback disabled.
The seasonal UI now labels static reference sources correctly. Browser checks
verify this wording, explicit unknown seasonal length, loaded static map,
disabled Portugal playback, Somali seasonal source wording and 320 px reflow.


## West Spitsbergen seasonal and branch conventions — 2026-10-03

The reference corridor is static; its 600–900 km editorial scenario envelope
is not annual variability. Summer 2014–2017 branch maps and primarily
autumn/winter glider sections cannot form twelve common-boundary monthly
frames. Svalbard/Yermak/Yermak Pass named branches are separate proposals.
Source-specific Svalbard/core naming and Spitsbergen Atlantic alias remain
unresolved. Dated geometry, consistent width and annual ranges are unknown.

Glider archive and summer ADCP data links are recorded as acquisition leads.
Dundas/Fer defines autumn/winter around 15 November and references altimetry
to replace erroneous glider DAC; those conventions must survive extraction.
No raw data or seasonal geometry acquired in this step.


## North Cape Northern-branch profile scale — 2026-10-03

Full primary Morozov et al. (2017) PDF supplies a 15-crossing fitted northward
velocity composite and an approximately 8 km author-defined effective scale.
Protocol v1.3 distinguishes the Gaussian center-to-e-folding parameter from
paired-edge width, standard deviation and FWHM. The algebraic metric
interpretation is OSW inference from the published equation. Exact composite
depth averaging and sample dates remain unresolved; cruise dates and the Fig. 1
track label are contextual records, not silently substituted observation bounds.
The Central branch, full system length/width, annual extrema and seasonal
footprints remain unknown. No route is fabricated from a width parameter.

Coverage is now nine scoped extracted records across seven names, one derived
candidate, two nonnumeric source reviews and 90 unassessed current names.
The seasonal inspector permits static examination with an explicit fitted-scale
label, omits the full-width bar, and disables animation for this composite.
General-protocol provenance is refreshed for the existing Gulf Stream series;
its numerical frames and algorithm remain unchanged. Canonical ledger and
release are unchanged. Dashboard scope-note and width fingerprints update.
Verification: inventory/derived-series validators, 15 width/dashboard unit tests,
and focused browser checks for table, inspector and retained seasonal pilot.


### 2026-10-03: Month-dated historical angular section widths

Width protocol v1.4 adds source-reported angular section spans with month
precision. Bourles et al. (1999), section 4.8, reports two-degree latitude width
at 35 W centered at 5 N in February 1993 and April 1996. Both convert to about
221.1656 km using WGS84, rounded to approximately 220 km. Computational
normalization around the center does not establish observed edge coordinates.
Exact days, lateral threshold and uniform depth bounds remain unknown.

Two separate historical records replace the pending width mention. They are
not seasonal states, annual extrema or whole-current widths. The explorer
labels them Historical section observation, retains their months, disables
seasonal playback and displays static route context. General protocol hashes
and the Gulf Stream derived-series metadata are refreshed; its 17 numeric
frames are unchanged by this metadata update.

Current width coverage: 11 scoped numeric records / eight current names,
one derived series candidate, three reviewed nonnumeric decisions, zero
pending historical mentions and 88 unassessed. Route coverage remains
46 candidates / 44 of 89 names / 45 pending routes. Canonical ledger unchanged.
Focused verification: 29 unit checks; historical width/route browser check;
17-frame section-width provenance checker. Browser integration results and
role review are recorded in the corresponding verification notes.

## 2026-10-03 · Cape Farewell threshold-section display

The East Greenland Coastal Current entry preserves Sutherland and Pickart
(2008), section 3.1: approximately 30 km at Cape Farewell, bounded at 15% of
the maximum inner jet velocity. July–August 2004 is campaign context, not
an exact section occupation date or a recurring summer climatology. The
separate 75 m frontal depth scale is not an assigned width averaging layer.

Width protocol v1.6 records this relative-velocity section class. The explorer
labels it Survey section observation, states the threshold, and disables
seasonal playback. Whole-current width, annual range, exact section geometry
and a fixed depth layer remain unresolved.

Verification: 12 width inventory unit tests, including rejection of invented
dates, layers, annual ranges and invalid thresholds; inventory provenance
checker; desktop and 320 px browser checks. Screenshot:
`figures/egcc-threshold-width-review.png`. Current inventory: 13 scoped numeric
records across 10 names. Independent scientific admission remains pending.

## Pacific NECC saved monthly section playback — 2026-10-04

`atlas-monthly-section.js` renders the pinned 2013 diagnostic inside the global
current atlas card. The selector and explicit playback show twelve monthly
mean profiles, local grid-sample locations and algorithmic zero-crossing marks.
This is diagnostic profile playback; the data's seasonal-measurement admission
flag remains false. It does not claim twelve observed current routes or a
representative annual footprint. The source year, longitude, nominal product
layer, averaging order and local component metric remain visible.

Playback uses fixed 2.2-second steps without inter-month interpolation, no
autoplay or year wrapping. Visibility change, current switch and world reset
stop it. `atlas-section` stores the selected monthly record; the standalone
review page's return link preserves it. Main-map zoom does not change the card
extent. Grid samples expose signed values through hover/focus and keyboard
activation. Source errors retain the standalone link; disposed fetches cannot
reopen cards. Renderer rejects invented annual dimensions and reversed paired
boundaries. Browser checks cover all twelve records, data fallback, keyboard,
mobile, playback and navigation. Source diagnostic admission remains pending.


### North Brazil–Guyana oblique mean section widths — 2026-10-04

Dimoune et al. (2023) supplies three source mean-width values: NBC1/HS1 about
520 km, NBC2/HS2 about 220 km and NBC3/HS3 about 440 km. They are cross-section
zero-contour spans of the January 1993–December 2017 mean rotated surface
geostrophic component, not instantaneous widths, seasonal extrema or current
lengths. HS1–HS3 use a 45-degree rotation. Source kilometre values are retained;
oblique latitude coverage is not converted as a meridional section.

NBC1/2 attach to North Brazil; NBC3 attaches to Guiana under the source's Guyana
continuation naming convention. The HS3 band straddles 10 N; no hard physical
boundary or canonical alias merge is admitted. Exact section longitude/endpoints
and boundary geometry remain unextracted. The mean-width table lists NBC2 about
220 km, while section 4.1 says 20 km in a different comparison. This unresolved
prose/table discrepancy is shown; it is not a 20–220 km uncertainty interval.

Protocol v1.16 and pinned audit:
`research/north-brazil-guiana-oblique-mean-width-scope-audit.json`.
The seasonal explorer displays mean oblique sections with no edge locator,
full-width bar or playback. Existing contextual routes retain their own scope;
Guiana still has no route estimate. Width coverage is 31 records / 21 names /
72 unassessed / five reviewed nonnumeric / two derived series pending review.
Canonical ledger, 11 published length ranks and 62 route candidates unchanged.
The Gulf Stream series receives only a new general protocol hash; its numerical
frames remain unchanged. Source review covers publisher HTML relevant sections
and indexed publisher PDF table text; no raw data or source figure digitization.

Verification: 21 width tests, 18 dashboard tests, both width provenance validators,
three-record browser checks (saved view, identity/scope/conflict, atlas/table
navigation and 320 px reflow). No complete release-gate claim; scientific
measurement/identity admission remains pending. Visual receipt:
`figures/guiana-oblique-mean-width-review.png`.

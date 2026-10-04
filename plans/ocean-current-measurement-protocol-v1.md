# OSW current measurement protocol v1.2

Effective 2026-10-03. Applies to OSW editorial reference-route candidates.

## Source season conventions

Preserve source season labels and explicit month windows, including boreal
or austral conventions that differ from the feature's geographic hemisphere.
Do not silently substitute meteorological seasons. Unlisted months remain
unrepresented sampling context, not evidence of absent flow. Sampling seasons,
local velocity seasonality and dated whole-route geometry are separate.
A source-season receipt alone cannot enable annual geometry, length/width
ranges or playback. When recorded, `source_season_convention` identifies its
label basis, source locator and month windows, retains the role
`source_observation_labels_only`, and sets `supports_annual_route_geometry`
to false. Actual seasonal routes require separate geometry evidence.
This is an OSW convention, not an official scientific standard. Published
lengths and future diagnosed velocity axes retain their separate methods.

## What we measure

Length is the sum of shortest WGS84 ellipsoidal geodesic legs through a
specified ordered polyline, in kilometres. It measures the declared route
and scope, not water-parcel travel, coastline length or all observed meanders.
A current name alone is insufficient to define a measurement.

## Rules that every candidate must follow

| ID | Rule | Required record / acceptance |
| --- | --- | --- |
| M01 | Identify the measured object before drawing. | Stable current ID; system, branch or regional scope; exclusions. Families require basin members; networks require a declared route. Never silently sum branches. |
| M02 | Declare vertical and temporal support. | Layer and time convention, including seasonal direction and source/model dates. Temperature-index gates are labelled as such, not velocity-core observations. |
| M03 | Separate source facts from OSW choices. | Primary source URL, citation, passage locator and retrieval date; coordinate-selection explanation identifies editorial vertices and gates. An inaccessible full text cannot be described as read. |
| M04 | Choose named-flow gates, not convenient numbers. | Explain start/end and alternatives. A survey boundary, upwelling band, Gulf boundary, eddy loop or movie crop is not automatically a current endpoint. Unresolved gates remain explicit. |
| M05 | Preserve the route geometry and method. | OGC:CRS84 longitude/latitude, finite valid coordinates, at least two vertices; no ambiguous 180-degree leg. Dateline routes opt into the documented shortest-geodesic/periodic-display policy. |
| M06 | Compute and check the same path everywhere. | WGS84 leg sum; display densification at at most 10 km; every scenario clears coarse OSW land. Coarse clearance does not establish shelf, bathymetric or velocity correspondence. Inspect the figure. |
| M07 | Specify sensitivity before interpreting its range. | Nominal route and explicit alternatives/offset grid, including zero offsets. Distinguish source-supported conventions from editorial perturbations. Offsets are not standardized physical uncertainty. Retain every scenario; do not discard inconvenient lengths. |
| M08 | Round without overstating precision. | Positive declared rounding increment, normally 100 km for current editorial regional geography. Round nominal to nearest increment, lower envelope down and upper envelope up. Raw computed values are calculation precision only. |
| M09 | Preserve measurement type and comparability. | Published estimate, bound, studied reach, hypothesis and editorial route remain distinct. Studied reaches excluded from route ordering. Other regional routes may be provisionally ordered with scope visible; no uniform whole-current rank asserted. |
| M10 | Explain ordering sensitivity. | Descending nominal order, with independent rounded-envelope position bounds and touching intervals counted as overlaps. These bounds are neither probabilities nor confidence intervals. Different scopes may be scientifically incomparable despite numeric order. |
| M11 | Keep navigation claims within their evidence. | Use measured geodesic route for state/crop display joins; projected overlap fractions are not physical kilometres. NASA crop links provide context, not current identification or date matching. |
| M12 | Make each result reproducible and reviewable. | Input/generator/map/tile hashes, retained scenarios and review gates. Generator changes require regenerating all reports. Source/geometry changes create an auditable revision and may change ordering. |
| M13 | Keep admission separate from calculation. | Editorial, nonpublished status remains until independent scope/physical review and canonical release review. Internal .roles review does not supply scientific approval. Unknown is a valid outcome. |

## Consistency does not mean identical physical assumptions

### Closed circuit rule

A closed reference circuit declares `route_topology: closed_circuit`, its
clockwise/counterclockwise direction and
`circuit_anchor_role: arbitrary_repeat_vertex_not_origin`. Its first vertex
is repeated at the end, and all nominal, alternative and scenario paths must
be simple closed rings with the declared orientation. Count each leg once,
including the closing leg. Independent endpoint offsets remain `[0]`; shape
alternatives and uniform longitude offsets may preserve closure. A repeated
anchor is not a source, termination, residence time or parcel travel period.
Seasonally disconnected flows cannot become an annual continuous circuit
merely because the editorial reference line is closed.

State navigation may exclude a raw polygon contact only with a declared
state code and geographic reason in `state_semantic_exclusions`. Keep raw
nominal/scenario contacts in the candidate and excluded-contact audit; do not
change the measured route to make a state association disappear. Explain
the exclusion in the visual card. A coarse display-region extension does
not establish membership in a physically distinct basin.

The algorithm, record requirements, provenance and display meanings are shared.
The geography, layer, season, gates and sensitivity choices are current-specific.
A 0.15-degree offset or 54 scenarios is not a universal standard or comparable
confidence level. No universal curvature multiplier is permitted. Do not extend
a regional candidate to a whole current merely to fill the ranking.

## Historical name and dimension conflicts (M01/M03/M09 clarification)

Preserve a source's reported dimensions with its named-flow interpretation,
sampling support and inspected access level. A reused name does not establish
equivalence between historical and modern flow objects. Until that equivalence
and the measurement method are reviewed, retain the numbers as unadmitted
source context, outside current measurements, ordering and seasonal ranges.
An interval in an abstract is not automatically annual extrema; a scale depth
is not a fixed axis layer. Keep survey or model release boundaries separate
from current gates. Agreement of integrated transport cannot alone validate
the flow's width: different speed and width biases can compensate.

## Before adding the next current

1. Resolve identity and select a primary evidence source; read the relevant text.
2. Write scope, layer, time, exclusions, gates and coordinate-selection rationale.
3. Choose and explain alternatives/offsets; retain an unknown decision if insufficient.
4. Generate candidate and inspect geometry, land checks and figure annotations.
5. Rebuild catalog and run the protocol audit, focused tests and affected browser checks.
6. Record .roles findings, amendments and remaining independent review gates.

## Enforcement and remaining review

`analysis/check_current_measurement_protocol.py` audits all stored candidates:
metadata/status/CRS, valid retrieval dates, input/report agreement and generator
pins, complete declared scenario grids, finite-number recomputation, rounding,
nominal inclusion, land-check outcome and proposed-identity separation. Its
report pins this protocol and the audited reports. It cannot judge whether a
source passage scientifically supports a gate, an axis or current continuity.
Those M01-M04/M06/M07/M09/M13 judgments remain explicit reviewer work.

The catalog builder runs this audit before writing its output and pins the
protocol and audit hashes in the catalog. Rejection leaves the previous catalog
intact. Run `python analysis/check_current_measurement_protocol.py` directly
when inspecting a batch without rebuilding the catalog.
The existing generator/catalog enforce geometry, scenario and inventory gates;
focused tests exercise numerical and seam behaviour. Full atlas/browser checks
verify presentation and joins. The protocol audit is an editorial conformance
record, not scientific approval or publication admission.

## Versioning

Changes to the definition, algorithm, rounding or comparison rules require a
new protocol version, impact assessment and re-audit of existing candidates.
New current-specific geography is a candidate revision under the same protocol.
Do not retroactively describe old editorial offsets as empirical error bars.

Initial audit coverage: 29 candidates for 27 names, with 2,052 scenarios.
Future coverage is recorded in the generated audit rather than this versioned
rule document. Existing source claims and eleven published ranks are unaffected.

## Frontal anchor observations (M02/M03 clarification)

A reported front crossing can support a declared regional geographic proxy.
It does not become a velocity-core position or set the current axis depth.
When used, `source_anchor_observations` retains a distinct identifier,
longitude/latitude matching the nominal source vertex, source locator,
month-precision sampling window and the role
`observed_front_crossing_not_current_axis`. Keep each sampling window separate;
points from different years cannot form a simultaneous observed geometry.
Endpoint offsets in synthetic route scenarios test editorial drawing choices,
not errors on those observed frontal positions. A temperature criterion at
150 m does not establish a current axis at 150 m. A climatological frontal
band also does not establish a complete transverse current width.

## Historical composites and contested continuity (M02/M03 clarification)

A composite made from different surveys, years or diagnostic methods must
retain each source set, its geographic coverage and any coverage gaps. A
most-probable or mean path is not a simultaneous observed current axis.
If newer evidence questions a persistent connection, retain the competing
interpretation in the source-scope audit before drawing or measuring a route.
Choose explicitly among a historical composite, dated jet, mean-flow connection
and transport corridor; these describe different objects and cannot share a
length without a reviewed equivalence. Do not force a single polyline through
interrupted or multiple branches merely to populate the ranking.

A meander latitude band is not transverse current width. A steric-height
reference depth is not a current-axis depth. Preserve conflicting printed
durations and calendar spans as unresolved source statements until the
original evidence resolves them. Historical composites cannot enable annual
geometry playback. These are source-scope clarifications under v1.2; the
geodesic algorithm, rounding and comparison rules are unchanged.

## Mean flow, anomalies and diagnostic domains (M02/M03 clarification)

Every proposed axis must identify whether its supporting velocity is total,
relative geostrophic, an anomaly, a layer average or a model diagnostic. Reference
pressure is not current-axis depth. A zero anomaly contour marks where departure
from a reference state changes sign; it does not identify where the current stops.
An averaging box, wind-forcing domain or model boundary cannot supply named-flow
endpoints. Do not combine a mean and an anomaly unless layer, reference state,
time averaging, grid and method are compatible and the combination is reviewed.
Do not connect separated positive-flow components without source-supported
continuity. These clarify existing source/identity gates under v1.2; algorithms,
rounding and ranking eligibility are unchanged.

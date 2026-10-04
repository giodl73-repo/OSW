# Ocean motion atlas: candidate data methods

Version: 0.1.0 candidate. Read `coverage.json` for generated counts and
`manifest.json` for exact input and output hashes. This method describes OSW's
curated join of a declared source set. It does not define an official NASA,
NOAA, or global oceanographic classification.

## Identity and names

NAVO FREDDIES detections use `navo-freddies:<date>:<provider code>` IDs and
`operational_eddy_detection` type. A code on one receipt is not evidence of a
historically named eddy, formation date, lifetime, or continuity across dates.
The four 2026-09-25 detections have canonical polygon records copied without
simplification from the pinned source receipt; the state-observation rows
reference their geometry IDs. Rendering simplification remains a separate
source-join field. State containment uses the full polygons against approximate
coast-masked display states, not surveyed state boundaries.

The source ZIP has no `.prj`; its numeric coordinates are interpreted as
longitude/latitude degrees with an unspecified exact datum. JSON/CSV records
retain that uncertainty. `geometries.geojson` contains only records explicitly
assigned `OGC:CRS84`; `coverage.json` lists excluded geometry IDs. The four NAVO
polygons are excluded rather than silently declared WGS84. Their pending
source-use status also excludes these entities, designations, polygons, and
dependent observations from the rights-screened preview.

The full candidate's `object.html?id=navo-freddies:<date>:<code>` page reads
canonical entity, geometry, observation, and claim records. Its footprint is an
equal angular longitude/latitude plot, north up, with no basemap or state
boundary drawn. The source center is a separate cross symbol. Text gives the
state relation and all positional/identity limits. Atlas outline links and
state readings navigate to the same dated ID. A downloadable review packet
contains the selected canonical records, related states, cited source metadata,
and NASA state/crop context rows and claims. Crop overlap is with the state's
display area; it neither identifies the detection nor matches the observation
date. This full-candidate view does not change pending source-use decisions.

`entities` assigns stable OSW IDs to named currents, named eddies, NASA
descriptions, and the 56 approximate OSW states. A current family, circulation
system, named segment, recurring eddy region, and individual eddy have
different `identity_level` values. `names` preserves a preferred label and
source-linked aliases. A name alone does not establish one continuous path,
fixed footprint, eddy trajectory, or equivalence between source records.
The OSW editorial facets and admission rules are in `taxonomy.json`.

NASA objects are entered only when the source page or related source ledger
names or describes them. The 70 Perpetual Ocean 2 movies in `tiles` are
regional views, not 70 named objects. A media link to a current or eddy is a
geographic address unless the source explicitly identifies that feature.
NASA's model years, visualized depth range, and release credits belong to
NASA's original pages; the pinned SVS API receipt supports bibliographic
metadata, not OSW's identities or boundaries.

## Lengths and ranks

`length_assessments` covers every current entity, including records with no
numeric along-current length. Only a published approximate along-current or
current-system length admitted as an established flow receives a
`published_rank`. Ranks order that source set's estimates in descending
kilometres, with equal numbers sharing a rank. The source's definition of the
current and its scope accompany the value. Differing start and end gates,
reference paths, depth ranges, and system boundaries limit comparison.
The [source-passage audit](RANKED-LENGTH-EVIDENCE-AUDIT.md) checks all eleven
ranked values and records their different object scopes and source limits. The
California and Kuroshio claims now cite direct oceanographic sources. These
claims still await individual scientific decisions.

Published lower bounds, OSW geographic lower bounds, surveyed reaches,
cross-stream sections, and proposed continuity hypotheses remain unranked.
An OSW geographic floor uses specified source gates and a rounded distance
smaller than their direct geodesic separation; it is not a measured path.
For the seven geographic spans, `gate_distance_sensitivity` recomputes shortest
WGS84 distances after independently shifting each latitude gate by -0.5, 0,
or +0.5 degrees; point gates also shift longitude. The finite set contains
9 or 81 scenarios. Its minimum and maximum describe this editorial what-if
choice, not a source-reported error or statistical confidence interval. They
do not bound every continuous coordinate choice or estimate meandering flow
length. A best/worst position compares these seven gate separations only;
overlapping ranges admit alternative positions, including ties. These
positions never enter `published_rank`. The source gates, perturbation choice,
and regeneration method are in `ocean-current-gate-distances.json`.
`measurements` retains source-specific quantities and variants. The separate
`illustrated_span_km` is half the geodesic perimeter of the narrowest drawn
map-arrow polygon available for a named current. It ranks illustrations only.
Arrow width sensitivity is not physical uncertainty, and an illustrated span
is never substituted for current length or a lower bound.

## Atlas geometry and state relations

`geometries.geojson` contains approximate editorial points and a dated pair of
NAVO analyzed Gulf Stream surface-front lines, plus a dated partial NOAA LSA
geostrophic streamline in `OGC:CRS84`. A point offers
an atlas address and has no asserted current core, eddy center, observed path,
or footprint. The current/state relation matrix
examines every current against every approximate OSW state. It retains
cartographic-arrow intersections, OSW schematic and editorial line crossings,
point candidates, and unresolved pairs as separate evidence kinds. A map
symbol or locator does not prove physical passage. An unresolved relation is
neither absence nor zero crossing. Physical crossing requires compatible
source or model geometry and an uncertainty assessment, which this candidate
does not yet supply for whole currents. The NAVO front lines are a first
physical observation layer: 306 north-wall and 204 south-wall coordinates
dated 2026-09-28. The source says they follow maximum sea-surface temperature
change over 10 nautical miles in infrared satellite analyses. OSW intersects
each line with approximate coast-masked state shapes and records eight
front/state observations across five states. This is a one-day front position,
not the current axis, corridor, or perennial passage. Coordinate reuse
remains under source-specific review.
The package also reports WGS84 geodesic lengths of the reported north and
south wall polylines and of their segments clipped by each approximate OSW
state shape. These are dated analyzed-front lengths, never inputs to the
current-length ranking. Decimal output records the calculation, not the
positional accuracy of the fronts or state boundaries.

The 2026-09-25 partial Gulf Stream diagnostic samples NOAA LSA's daily
0.25-degree altimetry-derived absolute surface geostrophic `ugos` and `vgos`
fields. Its relation evidence class is `derived_field`, distinct from direct
observed geometry and from OSW's editorial map lines. The source NetCDF
SHA-256 and raw packed velocity subset are pinned.
At 72.875°W, the seed is the grid center with greatest eastward speed in
36.5–37.0°N. A WGS84 geodesic midpoint integrator follows the frozen field
in 10 km steps, using bilinear wet-cell interpolation, until its first
eastward crossing of 50°W or a speed below 0.15 m/s. The chosen seed reaches
50°W after approximately 2,277 km. Its dated line intersects approximate
`GFST` and `NWCS` shapes over approximately 1,317 and 960 km. Five and 20 km
integration steps differ by less than 1 km in total reach, but a seed 0.25°
north stops below the speed threshold after roughly 620 km. That spatial
sensitivity rules out a robust whole-current length inference. The reported
reach and clipped lengths are unranked; this is not a measured axis, parcel
trajectory, depth-integrated flow, or permanent state passage. Product
acknowledgment credits NOAA LSA and NOAA CoastWatch.

A research-only [five-date repeat audit](../../research/gulf-stream-geostrophic-repeat-20260918-20260927.json)
applies the same seed gate and integration rules to 18 and 24–27 September
2026. The selected 36.875°N seed reaches the 50°W stop gate on four dates,
with partial reaches of 2,277–2,338 km; on 18 September it stops at 1,550 km
when midpoint speed falls below the threshold. Only three of ten adjacent-seed
traces reach the gate. These deliberately selected dates are a diagnostic
sample, not a temporal census or uncertainty estimate. The repeat receipts
are pinned in `research/` and are not part of this release package. No stable
axis, whole-current rank, or permanent state passage is inferred from them.

`named_current_source_observations` separately records published, dated local
studies of named currents. One entry is Berta et al.'s Northern Current
study off Toulon during 2–19 December 2011, with glider and HF radar support.
Its `MEDI` state association follows the paper's named Mediterranean locality.
The approximate OSW `NECS` display polygon overlaps part of the coastal
strip, so this is a semantic state association rather than a digitized
observation/polygon intersection. The study's map and velocity field are not
copied. The row supports local presence during the study window; it does not
establish the whole current's path, length, or persistent state passage.
Four further named currents are supported by source-reported cross-stream
bands from the 2009 ORCA survey. The Canary band intersects two approximate
OSW states (`NAST E` and `CNRY`); the Portugal, Azores, and Azores
Countercurrent bands intersect `NAST E`. One survey band can therefore produce
more than one state association. The published bounds are kept as coordinates
and checked against the coast-masked state shapes, but are not digitized
current axes. Survey dates are the known station or cruise windows, not exact
occupation dates for every band. Neither section widths nor state overlaps
enter the whole-current length ranking.

`tile_state_relations` compares NASA crop rectangles and coast-masked OSW
state polygons in the atlas display projection, including horizontal wrap.
The coverage fraction is the fraction of a state's **display area** covered
by a crop, not geodesic or physical flow area. It supports movie navigation
and never identifies a current, eddy, or NASA-endorsed state boundary.

## Dated eddy observations

NOAA CoastWatch MUNSTER v1.0 daily identification files were sampled on
1 March, June, September, and December in each of 2021–2023. The 12 NetCDF
source URLs and byte digests are pinned in the seasonal manifest. Each derived
snapshot retains an eddy center, polarity, radius, area, and state contour
containment or intersection. Compressed CSV exports in `observations/` preserve
the dated detections; `observation_sets` records product, date, and per-state
counts. The product's approximately 60°S–60°N spatial support and twelve
sample days do not form a continuous census. A MUNSTER tracker ID is not an
identity match to a named Horizon ring or a NASA movie feature. Seven-day
trajectory evidence exists only for the three June windows and remains
source-file scoped.

`named_eddy_state_assessments` explicitly covers every one of the 136 named
eddy records against all 56 OSW states. A reported center, sample point,
editorial regional locator, or shared Gulf of Mexico gateway can make a state
a candidate, but none is a dated closed eddy footprint. Accordingly every
named-eddy containment/intersection decision remains unknown. Unresolved
pairs are retained, including named regions outside the present OSW state
coverage. This matrix must not be conflated with the separate NOAA dated
contour intersections.
One Kraken state candidate also comes from an OSW georeferencing audit of the
red solid and dashed curves in Figure 2 of Beron-Vera et al. (2018). The
three dated panel images are examined at their source JPEG resolution, with
each axis tick perturbed independently by ±3 pixels. All nominal selected red
pixels map into `CAMR`; in the worst calibration corner 3,406 of 3,408 May
pixels do, while all August and October pixels do. This supports a dated
figure-derived location candidate for the depicted coherent-core and shielding
curves. The authors' closed boundary coordinates and the whole ring footprint
are still unavailable in the package, so physical containment and intersection
remain unknown. The paper PDF and embedded figure SHA-256 values, threshold,
axis calibration, state geometry digest, and three pixel envelopes are pinned
in the source audit. The audit can be repeated offline with its source PDF.
`named_eddy_source_observations` pins papers that identify Kraken, Thor, Ursa,
Cameron, or Darwin in dated observational maps or analyses. The Cameron and
Darwin observing paper explicitly credits the names to Horizon Marine; the
measurements are independent, while the labels are source-attributed. Their
paper-sourced atlas records remain separate from the Horizon event-register
records; the possible same-ring IDs in the research ledger are not verified
identity matches. Their
published figure boundaries are linked; the authors' closed boundary polygons
are neither reconstructed nor packaged. Paper
map windows are not treated as complete eddy lifetimes, OSW state footprints,
NASA model identities, or matches to NOAA MUNSTER tracking IDs.
The packaged `loop-eddy-cameron-darwin-name-date-conflict.json` audit records
two incompatible name/date assignments within Wang et al. (2019) and compares
them with Horizon initial-separation dates. That paper evaluates forecasts
against simulated GoM-HYCOM SSH. Its publisher erratum concerns figure
references elsewhere and leaves this chronology unresolved. The audit does
not establish a source-to-source identity match or a formation-date correction.
It also records separate 2009 western Gulf observations from Kolodziejczyk
et al. (2012), [JGR Oceans, doi:10.1029/2012JC007890](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2012JC007890).
That paper combines moorings with altimetry but explicitly credits the
Cameron and Darwin names to Horizon Marine. Its January 20 Cameron center
near 22.5°N, 95°W projects into the approximate `CAMR` state as a point
candidate. The July 25 Darwin observation does not give an exact center.
Neither is an initial separation date or a whole-eddy state footprint. The
audit keeps them separate from the unresolved 2019 formation chronology.

`operational_eddy_state_observations` adds four NAVO/NCEI FREDDIES polygons
from its 2026-09-25 North Atlantic package. The provider labels `W26001`,
`W26002`, `C26001`, and `C26002` are operational designations for that release,
not stable historical eddy names. The source polygon is intersected with each
coast-masked OSW state shape in the atlas display projection. All four are
contained within one approximate state each: one in `GFST`, one in `NWCS`, and
two in `NADR`. The ZIP SHA-256, shapefile member digests, original polygon
coordinates, and source public-release statement are pinned in the source
ledger. The ZIP has no `.prj` member, so longitude/latitude degrees are
inferred from its coordinate ranges and provider center fields; the datum is
not declared. These are dated polygon/state relations, not a continuous
census, a confirmed match to a cataloged named eddy, or evidence of the
feature in NASA's movie.
The map draws outlines simplified to 0.005 degree for legibility. All
state intersections and containment decisions use the full pinned polygons.

## Claim links and review status

Every `relations`, `measurements`, `tile_state_relations`,
`named_eddy_state_assessments`, and dated named-current, named-eddy,
NAVO operational-eddy/state, or diagnosed-current-path observation row has a stable `claim_id` pointing to one
normalized claim record. This is a provenance
crosswalk, not a new independent source. The claim carries the target row ID,
source ID, evidence class, observation time where recorded, and value or
object. For 5,600 current/state assessments and 877 NASA crop/state overlap
decisions, a JSON pointer identifies the exact row in the pinned OSW ledger.
The 7,616 named-eddy/state assessments and 128 source-record relations point
to their source eddy or NASA object record;
that record supplies point, gateway, or figure-derived red-curve context, not a whole-eddy footprint or
physical state intersection. These pointers are checked by the package
validator. The other 97 claims have specific source passages, fields, or
provider-record locators, including dated NOAA velocity, NAVO eddy, and NAVO
frontal observations. The generated `source-locator-worklist.csv` has no
pending rows; passage location does not establish scientific review or source
reuse rights. Method text is present for
14,130 claims, 27 refer to a method ledger, and 161 lack a recorded method in
their target row. All 14,318 claims are
marked `not_individually_reviewed`, with no invented reviewer or review date.
The generated 97-row `claim-science-review-first-pass.csv` prioritizes external
assertions. A reviewed decision is accepted only when its fingerprint matches
the exact claim and it records a reviewer, ISO date, decision, and note; the
separate pinned review ledger currently has zero decisions.
An unresolved claim documents an unresolved assessment and does not assert
physical absence. Source review queue impact counts exclude this normalized
duplicate collection.

## Sources, reproducibility, and publication limits

`sources` links assertions to external URLs or pinned OSW source ledgers.
Crossref metadata for DOI sources, NASA SVS page metadata, and the dated NAVO
front receipt are explicit receipts; a normal build is offline. Original NASA videos, paper PDFs,
Marine Regions gazetteer geometry, and cartographic arrow polygons are not
redistributed in this package. The source review queue records 85 narrow
current-use rights decisions and 17 remaining rights questions, including
the 16 rows carrying provider values and the credited arrow layer. Fifty-seven
linked factual sources have reviewed structured Crossref citation fields;
the other nine have reviewed source-page or institutional citations. Preferred
The ten used NASA SVS links have reviewed page citations and exact item credits;
citation reviews for the 17 rights-pending sources remain open.
See `THIRD-PARTY-NOTICES.md`
and `plans/ocean-motion-linked-facts-use-decision.md` in the repository.
The FREDDIES eddy refresh is explicit: with `pyogrio==0.12.1` installed,
run `py analysis/fetch_navo_freddies_eddy_snapshot.py`, then
`py analysis/build_navo_freddies_eddy_state_join.py`. Those commands fetch
the current ZIP and require a fresh date/identity review if it differs from
the pinned 2026-09-25 source. Normal builds consume the pinned JSON and make
no network request.

From the repository root, run:

```text
py analysis/build_ocean_motion_release.py
py analysis/check_ocean_motion_release.py
py analysis/check_motion_almanac.py
py analysis/test_motion_almanac_browser.py
```

The builder copies source ledgers and writes JSON, CSV, GeoJSON, schema,
coverage, and a manifest with SHA-256 digests. The validator checks input
digests, generated file digests, row contracts, cross references, export
agreement, and observation contents. Browser checks cover the interactive
routes, but human screen reader review and the repository publication gate
remain open. No DOI or external publication is asserted by this candidate.

## Alaska Coastal Current admission and offline navigation refresh

The Gulf of Alaska entry follows Stabeno et al. (2016), accepted manuscript
abstract, PDF page 2, lines 25-28: approximately 1,700 km between Seward and
Samalga Pass. Its preferred OSW name adds the Gulf qualifier; the paper name
is a source-linked alias. This coastal system is separate from the offshore
Alaska Current and Alaskan Stream. The estimate describes the source
region, with intermittent observations during 1984-2014, rather than a
simultaneous measured current axis. No observations or route geometry from
the paper are imported. The three map points are OSW editorial locators.

Recompute current-to-crop navigation using the existing audited 70-crop
catalog without fetching NASA:

```powershell
python analysis/build_nasa_perpetual_ocean_tile_join.py --reuse-pinned-tiles
python analysis/build_ocean_current_nasa_crosswalk.py
```

The default tile builder still performs an explicit source refresh. Offline
reuse requires the expected schema, picker URL, and 70 unique crop IDs. The
Alaska addition remains regional navigation only, with no NASA naming or
frame identification claim. New reported-length measurement 0028 follows
existing measurements so their IDs and passage fingerprints remain intact.
Source-use decisions may specify an individual review date; existing decisions
retain the ledger default date. Scientific claim decisions remain pending.

## Dated Shelikof Sea Valley association

Stabeno et al. (2016), published article Table 1 caption (PDF page 4,
printed page 26), identifies 10 May-15 July 1989 as a sea-valley transport
interval. Section 2.2 (PDF page 5, printed page 27) also locates the 1989
mooring arrays in the sea valley rather than at the exit to Shelikof Strait.
OSW records this as a local observation and assigns ALSK by the reported
Gulf of Alaska locality. It is not a source-coordinate/polygon intersection,
current axis, section endpoint pair, whole-current passage, or BERS evidence.
The 1985 interval is not imported because caption and methods describe
differing bounds; the 1989 interval has no such disagreement in these passages.

The published PDF, independently retrieved from AOOS on 2026-10-02, has
SHA-256 `dc354e753e33e2f0af9a17a66a9f291d9b31e8e77c15bd8152967daa5cc03ba9`.
The source registry records its file URL and date alongside that digest.
It does not identify the earlier accepted-manuscript bytes. The new source
observation and local-presence relation append after existing records,
preserving previous claim IDs. The screened record page shows dated local
observations with locality, time details, state limits, and a paper link.

## Source-scoped regional classifications

`classification_vocabularies.json` and `.csv` preserve cited regional
classification definitions separately from the OSW editorial facets. The
Thompson et al. (2018) Antarctic shelf/slope vocabulary defines Fresh Shelf,
Dense Shelf, and Warm Shelf using shelf access by neutral-density layers,
dense-water formation, and a 0.5 degrees Celsius shelf-water threshold.
The 28.0 threshold uses the source neutral-density gamma_n convention, not
absolute seawater mass density. Definitions are paraphrases with a DOI and
section locator. Each vocabulary has a claim whose review fingerprint binds
its terms, criteria, density note, requirements, and empty assignment list.
A vocabulary record is not an observed regime assignment. Assignments require
regional, time, depth, and compatible hydrographic support; surface movie
patterns alone are insufficient. Both current pages and the screened entity
packet carry these definitions and limits. Scientific claim review remains
pending. No paper, figure, or provider field is redistributed.

## Kuroshio local mooring evidence

A 2025 study by Wang et al. supplies three instrument positions east of Luzon
for January 2018-May 2020. The observation keeps month precision rather than
inventing deployment days. All three reported positions project into the
approximate CHIN display polygon. The current core is west of the array;
these positions do not trace its axis or prove whole-current state passage.
Depth coverage is uneven: the middle station downward instrument failed, and
the upper 50 m were excluded. The deeper Luzon Undercurrent is distinct.
Coordinates, precision, depth and state limits are included in the observation
claim fingerprint. The source is attributed under its publisher CC BY 4.0
notice; instrument series, model fields and figures are not reproduced.
The candidate now has eight local current/state observations for seven named
currents. Scientific claim review remains pending.

## Kraken dated figure contour candidate

`named_eddy_footprint_candidates.json` and `.csv` contain an attributed OSW
digitization candidate for the 29 May 2013 instantaneous SSH contour shown
in Beron-Vera et al. (2018), Figure 2. The nominal polygon has 456 traced
vertices plus a closing coordinate, with source pixel positions, axis ticks,
PDF/figure/geometry hashes and segmentation/calibration scenarios retained.
Its datum is unspecified by the figure, so geometry 0158 stays in JSON/CSV
and is excluded from CRS84 GeoJSON. No paper or original figure is packaged.
The later blue curves are advected material and supply no new instantaneous
footprints. Red material-core and shielding boundaries remain distinct.
CAMR intersection is robust across the tested scenarios; CARB intersection
is calibration-sensitive; whole-ring containment remains unresolved. Display
overlap fractions are not surveyed areas or statistical confidence intervals.
The candidate claim binds geometry checksum and state/sensitivity support.
Kraken and CAMR/CARB pages and packets expose the same candidate geometry.
The full package has 158 geometries; the screened copy has 151, including this
proxy. Both GeoJSON exports omit it. Independent scientific review and the
public release gate remain outstanding.


### Dated footprint to NASA crop navigation

`footprint_movie_context` contains ten geographic navigation rows for the
2013-05-29 Kraken SSH contour candidate. Periodic longitude crop rectangles
are intersected with the nominal figure polygon in angular display space.
Fractions are not physical area estimates and exclude segmentation/calibration
uncertainty. The recommended crop is the highest zoom with complete nominal
coverage, then smallest wrapped crop-center distance, then stable tile ID.
For this candidate it is `level2_B_3`. The declared NASA model period is
2021–2023, outside the contour date; no Kraken identity or movie-frame match
is established. These rows are separate from media identification and state
intersection claims. Each navigation claim binds the row and supports the
candidate claim; eddy and state packets retain the crop/source closure.


### Malvinas conference estimate

The eleventh ranked value is the 2,000 km northward Malvinas loop extent in
Spadone, Provost and Sennechael's EGU2009-12242 conference abstract. The source
is a one-page conference abstract, not a journal reference-path measurement.
Its northern ACC-branch context is retained, with unspecified end gates, depth,
centerline, time convention and uncertainty. No route or state passage is
inferred. The related 2009 journal article is contextual reading and is not
assigned the conference number. Measurement 0030 appends after prior records;
its source-passage audit is bound to the exact claim fingerprint.

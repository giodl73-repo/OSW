# OSW ocean motion data release candidate

The `v0.1.0/` directory is a generated, self-contained candidate data package.
It is an OSW crosswalk of declared source sets, not a NASA or NOAA publication
and not a complete global census. Do not assign a DOI or describe it as a
published release until the repository publication gate is complete.

Build and validate from the repository root:

```text
py analysis/build_ocean_motion_release.py
py analysis/check_ocean_motion_release.py
```

The manifest records SHA-256 hashes for every copied source ledger and output.
`METHODS.md`, `CHANGELOG.md`, and `DATASET-CITATION-DRAFT.json` are copied into
the candidate package and hashed by the manifest. The citation draft is not a
registered DataCite record: its publisher, publication year, landing page,
rights statement, and DOI require the reviewed public release decision.
The JSON tables retain stable IDs, cross references, evidence classes, and
source IDs. CSV cells containing lists or objects store JSON text. The GeoJSON contains editorial locator points and the admitted dated line
roles. A point does not assert a current or eddy footprint. Polygons with
unspecified datum remain in JSON/CSV and are excluded from CRS84 GeoJSON. `schema.json` lists required row fields
and controlled evidence and geometry roles. `coverage.json` records counts and
claim limits.
`claims.json` and `.csv` contain one evidence record for each relation,
measurement, NASA movie crop/state display-overlap, named-eddy/state
assessment, and dated named-current, named-eddy, NAVO operational-eddy/state,
or diagnosed-current-path observation row. Each target row
has a `claim_id`. Claims retain the source, dated scope when available,
method, source locator, and explicit review status; an unresolved relation's
claim is an unresolved assessment, not a positive physical assertion.
Of 14,318 claim records, 6,477 point to exact rows in pinned OSW state or
movie-crop ledgers, 7,744 point to source eddy or NASA object records (named
eddy/state physical relations remain unknown), and the other 97 have specific
source passages, fields, or provider-record locators. The generated
`source-locator-worklist.csv` has no pending rows. All claims remain
`not_individually_reviewed`; a reviewed source
use decision is not an individual scientific claim review. Claim rows are
normalized views of target records and are excluded from source review queue
impact counts to avoid counting the same assertion twice.
`claim-science-review-first-pass.csv` orders the 86 externally located claims
for scientific review, beginning with ranked lengths. Each claim has a
`review_fingerprint`; completed decisions must be entered in the pinned
`ocean-motion-claim-reviews.json` source ledger with a reviewer, date, and note.
The [review workflow](CLAIM-REVIEW-WORKFLOW.md)
describes the remaining internal-ledger audit and decision rules.
`taxonomy.json` freezes OSW's facet definitions, NASA motion-form vocabulary,
and admission rules. The 158 exported geometries include 150 editorial
locator points (134 current and 16 NASA object locators), two NAVO analyzed
Gulf Stream surface-front lines dated 2026-09-28, and one NOAA LSA partial
geostrophic streamline dated 2026-09-25, and four dated NAVO operational eddy
polygons with unspecified datum. Those four polygons remain in JSON/CSV and
are excluded from the CRS84 GeoJSON. None is a complete current footprint;
coordinate reuse remains under review. Their geodesic lengths and state-clipped
segment lengths describe only those dated observations and never enter
whole-current length rankings.
`length_assessments.json` and `.csv` give all 100 named-current records an
explicit length evidence status. The eleven admitted published-estimate ranks,
lower bounds, proposed length, and 24 ranked drawn-arrow spans occupy separate
fields. A map-arrow span is not a physical length or lower bound.
The [ranked-length evidence audit](RANKED-LENGTH-EVIDENCE-AUDIT.md) checks the
eleven source passages and records their different measurement scopes and scope
warnings. The claims remain individually unreviewed.
The [length source triage](../../plans/ocean-motion-length-source-triage.md)
records five tempting numbers excluded because they describe only a branch,
study region, coastline, or partial reach.
`sources.csv` includes per-source usage counts and a current-use terms status to
make the remaining source review sortable.
`source-review-queue.csv` orders the 111 used external sources by package impact
and lists the entity IDs and next review action for each source. For a MUNSTER
file, `derived_detection_count` counts exported observation rows separately
from `record_count`, which counts direct canonical-table references;
`total_packaged_row_count` drives the review order. Its
`material_use_class` separates compiled names/dates, dated derived observations,
cartographic derived values, gazetteer matching, movie navigation, and
source-scoped factual claims. `provider_asset_redistributed` is true for 16
external source rows: the Horizon register's names and dates, 12 NOAA MUNSTER
files' extracted eddy centers and measurements, the NAVO front coordinates,
the NAVO/NCEI FREDDIES polygons, and the NOAA LSA packed regional velocities.
It means provider record values are carried into the package even if the
original file or page is absent. Source videos, papers, full raw NetCDF files,
and the arrow polygon layer are absent. These use classes scope the rights
review; they are not permission decisions.
The explicit current-use decisions in
`research/ocean-motion-source-use-reviews.json` cover 94 of the 111 used
external sources. Seventeen rights decisions remain pending: 16 source rows
carrying provider values and one credited cartographic service. Of 82 linked
factual sources, 65 have DOI metadata and 17 have source-page, agency, or
institutional citations. The narrow
[linked-facts decision](../../plans/ocean-motion-linked-facts-use-decision.md)
records this scope. A reviewed link or name-context use does not authorize
copying a linked media file or provider dataset. Including the separate figure-derived source,
the 66 DOI citations are read from the pinned
`research/ocean-motion-crossref-metadata.json` receipt. Refresh that receipt
explicitly with `py analysis/fetch_ocean_motion_crossref_metadata.py`; normal
build and validation do not call Crossref.
The seven NASA SVS release-page titles, release dates, update dates, credits,
and API response digests are pinned in
`research/ocean-motion-nasa-svs-metadata.json`. Refresh this receipt explicitly
with `py analysis/fetch_ocean_motion_nasa_svs_metadata.py`; normal builds are
offline. Source-page metadata does not settle rights for individual media.
Sixty-nine source URL labels are pinned in
`research/ocean-motion-source-metadata-overrides.json`.

`tiles.json` and `tiles.csv` list all 70 NASA regional movie crops separately
from the 247 object-to-movie navigation records. A crop is a spatial video
address, not evidence that NASA named an object in that crop.
`tile_state_relations.json` and `.csv` preserve 877 approximate state/crop
display-overlap decisions, including the fraction of each state's display area
covered by the crop. These are map navigation measures, not physical relations.
`named_eddy_state_assessments.json` and `.csv` cover all 7,616 named-eddy ×
state pairs with explicit point/gateway candidate evidence or an unresolved
status. No named eddy has a verified containment or intersection claim in
this candidate; NOAA's dated, unnamed contour observations are separate.
`named_eddy_source_observations.json` records three named Loop Current rings
with independently published dated analyses and direct paper citations; no
figure geometry is reproduced.
The [Kraken Figure 2 state audit](../../research/kraken-2013-figure2-state-audit.json)
adds one dated red-curve location candidate for `CAMR`, including source-image
hashes and axis sensitivity. It does not claim containment of the whole ring.
The [named-eddy publication and state-join worklist](../../plans/ocean-motion-named-eddy-next-join.md)
tracks the separate paper-sourced records needed for these names to survive
rights screening and the dated footprints required for physical state claims.
`operational_eddy_state_observations.json` and `.csv` add four 2026-09-25
NAVO/NCEI operational eddy polygons with dated state containment. Their
`W26001`-style codes are provider labels for one release, separate from the
136 historical named-eddy source records. Five journal-sourced records may
refer to the same physical rings as Horizon entries; the source-scoped count is
not a count of unique physical eddies. Source coordinates and archive digests are
in the pinned ledger; the source ZIP has no declared CRS or reuse license.
The full research candidate now provides one detection detail page per dated
code, linked from atlas outlines and state readings. It shows the canonical
polygon, state evidence, provider/source limits, and downloadable JSON packet.
NASA crop links are regional state-overlap context only. These pending-source
pages and records are not part of the isolated screened review site.
`named_current_source_observations.json` records a published December 2011
Northern Current study off Toulon and four named currents' reported
cross-stream bands from the 2009 ORCA survey. The Toulon locality is assigned
semantically to `MEDI`; the ORCA bands intersect approximate OSW state shapes.
The Alaska Coastal Current sea-valley study adds a seventh state-association
row and a sixth distinct current, with semantic ALSK association and no
digitized section geometry. These rows do not assert
whole-current paths, lengths, or permanent state crossings.
`diagnosed_current_path_observations.json` and `.csv` record one unranked,
2026-09-25 Gulf Stream partial surface geostrophic streamline. Its pinned
NOAA velocity subset, seed gate, 50°W stop gate, state intersections, and
seed/step sensitivity are in the source ledgers. It is a dated diagnostic
reach rather than the whole current's path or length.
A [five-date research audit](../../research/gulf-stream-geostrophic-repeat-20260918-20260927.json)
checks the same method on nearby dates and seeds. The selected trace stops
early on one of five dates, and most adjacent-seed traces stop before 50°W.
These research receipts are not included in `v0.1.0/` and do not establish a
stable Gulf Stream route.
`almanac/movies.html` lets readers search every crop and follow these
navigation links to OSW state and motion object pages.
The 12 NOAA daily eddy samples and their 92,891 detections are preserved as
separate compressed observation tables under `v0.1.0/observations/`. The
source snapshots and original product digests are retained. A dated detection
is an observation, not a named eddy identity. `observation_sets.json` records
date, product, source, and per-state contained/intersected contour counts.

Use `object.html?id=current:acc`, `object.html?id=eddy:horizon:loop-81-primary`,
or `object.html?id=state:CAMR` from the almanac directory to inspect an object.
Each page reads this candidate package. The main almanac continues to provide
the more detailed source-ledger tables while the presentation migrates.

The next release work is a source licensing audit, independent review of NASA
identifications and name equivalences, final dataset citation metadata, browser and
accessibility review, and the existing `plans/release-reconciliation.md` gate.
The initial source family review and unresolved terms are in
`source-terms-audit.md`.

The Alaska Coastal Current record includes a separately dated local
Shelikof Sea Valley observation (10 May-15 July 1989), assigned to ALSK by
source-reported regional geography. No section endpoints or whole-current
footprint are inferred. The published-article PDF available through AOOS
is pinned by SHA-256 with its own file URL and retrieval date; it is distinct
from the accepted manuscript cited for the ranking and is not redistributed.

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

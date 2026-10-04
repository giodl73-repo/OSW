# Ocean motion atlas: data release and presentation contract

Status: draft for OSW review; no external release authorized

Date: 2026-09-30

## Release identity

Publish this as an **OSW curated relational atlas of ocean motion**, with a
separate citable dataset release and an interactive reading surface. NASA,
NOAA, Marine Regions, and research papers remain attributed sources. An OSW
join or taxonomy decision is an OSW editorial result, not a NASA or NOAA
endorsement. The exact public title should name the source set and version;
avoid “all ocean currents” or “all eddies” while global completeness is
unverified.

The first release should freeze a declared source set, not a permanent count.
The 2026-10-02 working snapshot has 22 NASA named/described motion records,
70 NASA regional movie crops, 100 named-current records, 136 named-eddy source
records, and 56 OSW states. The current/state matrix records all 5,600 pairs,
including unresolved pairs. Those counts are a release baseline to validate,
not a claim that every feature visible in NASA footage has been identified.

The full candidate also has four distinct NAVO FREDDIES dated detection
entities for 2026-09-25, with canonical source polygon records and geometry
references from their state observations. They are not part of the named-eddy
count and remain excluded from the screened atlas while source use is pending.
Their exact datum is unspecified, so their rings remain in JSON/CSV rather
than the CRS84 GeoJSON export. The full candidate now has 318 entities and
158 geometry records; the screened copy has 218 entities, 150 editorial
locator points and one dated figure-derived SSH contour proxy. The Kraken
29 May 2013 proxy is a separate candidate claim and geometry, with robust
CAMR intersection across tested calibrations, calibration-sensitive CARB
intersection and unresolved containment. Its unspecified datum keeps it out
of CRS84 GeoJSON. Both object/state views and packets carry the same limits. The full candidate now has a canonical detection detail view
with the dated polygon, state relation, source, downloadable evidence packet,
and regional NASA context. Atlas outlines and state readings navigate to the
same dated IDs. Source-use and coordinate limitations remain beside the
footprint; pending-source detections are excluded from the isolated screened
site. The next admission gate for these records is source-specific reuse and
coordinate metadata, followed by scientific review of the spatial assertion.

## Canonical data model

Use stable OSW identifiers and source-scoped assertions. The release package
should have these linked tables or JSON collections:

| Collection | Required content |
| --- | --- |
| `entities` | Stable ID, preferred OSW label, object type, identity level, basin, temporal behavior, vertical setting, review state. A current system, an eddy region, an individual eddy, and a dated detection are distinct entities. |
| `names` | Source spelling, aliases, source ID, validity/context, and whether the equivalence is confirmed, proposed, or unresolved. |
| `claims` | One claim per row: subject, predicate, value or target, source passage/locator, method, publication or observation time, evidence class, reviewer, and review date. Competing length scopes remain separate claims. |
| `relations` | Typed links such as `feeds`, `part_of`, `member_of`, `source_named`, `nasa_described`, `state_locator_candidate`, `cartographic_crossing`, `observed_contour_intersection`, and `regional_movie_context`. Each edge points to its supporting claim. |
| `geometries` | Geometry plus its role: editorial locator, map symbol, source activity region, observed center, observed contour, or model centerline. Include spatial reference, source, timestamp where applicable, and method. A point is never silently promoted into a footprint. |
| `measurements` | Quantity, value, unit, object scope, route/section/gates, product, time/depth window, method, uncertainty, and rank eligibility. Published estimates and map-arrow spans occupy separate measurement classes. |
| `media` | NASA release and crop URL, media group or time cue, spatial/temporal alignment method, and relation to an entity. Link to NASA media; do not repackage its movies as OSW data. |
| `sources` | Persistent URL/DOI, title, authors/publisher, version or access date, license/terms, source snapshot hash where retained. |

The current research JSON files remain source-specific ledgers. Generate the
canonical package from them, rather than hand-editing a second master copy.
Publish full-fidelity JSON and flat CSV tables; publish GeoJSON only for
geometries with explicit roles and coordinate metadata. Do not convert an
unresolved physical relation into a zero, false, or empty geometry. Add JSON
Schema validation for IDs, foreign keys, evidence classes, units, coordinates,
time fields, and required provenance.

## Evidence and authority rule

Every public statement needs a source-linked evidence type:

1. `source_identified`: NASA or another named source explicitly identifies the
   object or name in its own text, map, or data product.
2. `source_associated`: an independent source connects two named objects, but
   NASA does not make that connection or use that name.
3. `observed_geometry`: a dated source center, contour, or track supports a
   spatial relation for that observation and product.
4. `atlas_geometry`: OSW or a credited cartographic source provides a
   schematic line, arrow, activity box, or locator. The geometry's role must
   accompany every map and state relation.
5. `unresolved`: evidence is absent, conflicting, or insufficient for the
   stated physical relation.

Keep the existing finer status values beneath these presentation groups.
Crosswalk OSW motion facets to NOAA CMECS where meanings align; keep OSW
identity levels and provenance rules as an explicitly local extension. An
eddy tracker ID and a human name require a separate, evidenced identity edge.
The [Cameron/Darwin name-date audit](../research/loop-eddy-cameron-darwin-name-date-conflict.json)
shows why: Wang et al. (2019) assigns opposite July 2008 and February 2009
names in its Sections 2.1 and 3.4. Its reference SSH field is a HYCOM
simulation. Section 3.4 agrees with the Horizon Cameron month, while its
February 2009 Darwin separation differs from Horizon's initial December 2008
date. No cross-source identity join or additional observed-eddy record follows
from that paper without a corrected chronology or independent dated evidence.

## Release package and citation

The dataset release should include the canonical tables, schemas, a manifest
with file hashes and row counts, a method book, source and license register,
coverage/unknowns report, changelog, and deterministic build command. Freeze
the git commit and generated files together. Provide a distinct dataset
citation and version; keep `CITATION.cff` for the software. A version-specific
DOI and a concept DOI can be minted when the owner approves an external
archive. Record upstream DOI/URLs in the dataset metadata and display them on
the site. The existing third-party notices need an almanac source/licensing
pass before deposition.

The publication gate in `plans/release-reconciliation.md` still applies:
reconcile the live branch and hosted target, citation/version metadata,
source register, validation, accessibility, and explicit publication
authority. This draft does not change those decisions or deploy anything.

### Rights-screened review export (2026-09-30)

`py analysis/build_ocean_motion_safe_preview.py` derives
`almanac/release/v0.1.0-rights-screened-preview/` from the full candidate;
`py analysis/check_ocean_motion_safe_preview.py` validates its manifest,
schemas, CSV parity, and claim references. It excludes 23 pending external
source rows, including the 17 used sources with unresolved terms, and removes
dependent provider observations, Horizon Loop eddy names, and ArcGIS-derived
arrow measures. The resulting preview has 100 named currents, 40 source-scoped named eddies,
22 NASA motion entities, 56 states, and all ten source-reported ranked length
estimates. Its README and screening report explain the omissions. It is an
internal review artifact: only screened claim-pointer excerpts of five source
ledgers are included, the public site still uses the full candidate, and
scientific and accessibility review remain open.
The NASA movie-crop directory now loads the screened preview, while the main
almanac and object pages still use full research data. The
`analysis/audit_ocean_motion_publication_boundary.py --gate` check deliberately
fails until the static site tree and pending source uses are reconciled; see
`almanac/release/PUBLICATION-BOUNDARY.md`. Moving one page to the preview does
not clear a site tree that still serves the full candidate by direct URL.
An isolated `site-review/ocean-motion-screened/` review atlas now reads only
the screened export and provides an object directory, schematic locator map,
ten-value length table, state passports, and 70 NASA crop links. It is built
and checked separately from the full site and remains a partial, unapproved
review artifact. State passports have direct `?state=` links and list both
supported candidates and unresolved current/eddy relations by evidence type.
The screened site's length section lists all 100 retained current records and
separates ten ranked estimates, seven OSW geographic floors, proposed lengths,
and unknowns. The newest floors are source-gated latitude separations for the
Benguela Current system, Brazil Current, and North Atlantic Deep Western
Boundary Current. They are not measured flow paths or ranked lengths.
Each of its 218 objects has a downloadable screened JSON packet containing its
record rows, claims, related-object labels, and source metadata. Packet URLs
are indexed and covered by the preview and site manifests; the packets remain
review copies without a public dataset DOI.

## Presentation: one entity, several evidence views

The public landing page should answer “What is this?”, “What can I search?”,
and “What does the evidence prove?” before showing totals. A persistent
searchable object page should contain:

1. name, aliases, identity level, and source status;
2. map with selectable geometry roles and a visible evidence legend;
3. dated observations or source claims, including conflicting scopes;
4. current/eddy/system relations as a small navigable graph;
5. NASA film chapter, crop, or media-group link with a precise relation label;
6. OSW state relations split by observed contour, cartographic crossing,
   schematic line, point locator, and unresolved;
7. measurements with method, units, scope, and rank eligibility;
8. direct download of that entity's records and a citation link.

Keep three entry routes to the same IDs: a global object search, NASA film and
regional-crop navigation, and a 56-state passport. The almanac ranking is a
fourth route. Use one backend/package so the table, map, state page, and movie
view cannot disagree about counts or evidence status. Every map marker should
open the same object page; unknown footprint should be rendered as unknown,
not as an apparently precise dot or filled state.

## Minimum release gates

- Regenerate every dependent join from frozen source receipts and compare
  output checksums. The current local checks are
  `py analysis/check_nasa_perpetual_ocean_series.py`,
  `py analysis/check_motion_almanac.py`, and
  `py analysis/test_motion_almanac_browser.py`; extend them to validate the
  normalized package and all foreign keys.
- Audit every NASA-identified record against its release page or transcript,
  and every movie address against the live NASA picker. Count movie variants
  separately from distinct objects.
- Verify a sampled object page in each evidence class and a state passport
  containing both supported and unresolved relations. Keyboard and screen
  reader review must cover search, map alternatives, tables, and media links.
- Publish a coverage table showing source-set counts, unresolved pairs,
  physical-geometry coverage, length-estimate coverage, and dates/products of
  eddy observations. A global-completeness claim requires a separate audit.
- Reconcile the existing release gate and obtain the owner's explicit
  publication decision only after the candidate package and site are
  reviewable.

## Order of work

### Next evidence increments after the 2026-10-02 classification admission

The Antarctic shelf/slope vocabulary is now exported with cited definitions
and displayed on both current pages. It has no observed regime or OSW state
assignments.

Completed next local-evidence increment: Kuroshio mooring observations east
of Luzon, January 2018-May 2020, from Wang et al. (2025). Three reported
instrument points fall in approximate CHIN; month precision, depth/instrument
limits and current-core distinction are retained in both atlas views and
entity packets. This is local instrument-point support, not a dated whole-
current footprint. Local current/state observation rows now total eight
across seven named currents. Scientific claim review remains pending.

The next priorities are:

1. Strengthen current/eddy-to-state joins using dated footprints or explicit
   source observations. Keep center-point presence, intersection, containment,
   and editorial navigation as separate relations with their spatial limits.
2. Expand the ten published-estimate length ranks with source-defined scope
   and endpoints. Keep measured sections, system spans, geographic floors,
   and drawn-arrow spans separate; do not infer physical length from a movie.
3. Build a regional classification assignment pilot only where compatible
   hydrography, depth, time, and geographic support are available. Allow mixed
   and unknown results. The source vocabulary alone supplies no assignment.
4. Complete independent scientific claim review, source-use decisions, human
   accessibility review, citation metadata, and the repository release gate
   before a reviewed public dataset and site decision.

1. Normalize current ledgers into the canonical IDs, claims, relations,
   geometry roles, and source registry; preserve source-specific JSON files.
2. Generate schemas, CSV/GeoJSON exports, manifest, and a deterministic
   coverage report; validate the package independently of the browser.
3. Rebuild the public atlas around stable entity pages and state passports,
   then test deep links and evidence labels in the browser.
4. Prepare the versioned dataset archive and site release candidate; run the
   repository publication gate and request the final owner decision.

Relevant external specifications: [NOAA CMECS](https://www.ncei.noaa.gov/products/coastal-marine-ecological-classification-standard),
[W3C PROV-O](https://www.w3.org/TR/prov-o/),
[DataCite metadata](https://schema.datacite.org/), and
[Zenodo versioning](https://zenodo.org/help/versioning).


Dated figure footprints now have direct, claim-bound NASA crop navigation.
Kraken supplies the first example: ten nominal geographic crop overlaps and
one recommended full view. Its 2013 contour is outside the NASA 2021–2023
model period; neither event identity nor frame alignment is asserted. The
next evidence expansion should prioritize dated boundaries and observations
with explicit time, depth and geometry, before adding more inferred joins.


Length expansion now includes eleven source-reported estimates. Malvinas is
2,000 km from EGU2009-12242, explicitly a conference abstract. This admission
adds a published contextual extent without asserting a measured path or new
state passage; a stronger primary route reconstruction remains future work.

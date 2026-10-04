---
skill: roles-check
topic: ocean-motion-atlas
date: 2026-09-29
roles_used: 7
p1_count: 1
verdict: NEEDS-WORK
source_commit: 5298e8b33a918752496ab334fc7e597fed32dc24
working_tree: modified and untracked candidate files; review applies to the working tree, not that commit alone
---

# OSW role review: ocean motion data candidate and object pages

## Artifact and selection

Reviewed `analysis/build_ocean_motion_release.py`,
`analysis/check_ocean_motion_release.py`, `almanac/release/v0.1.0/`,
`almanac/object.html`, `almanac/object.js`, `almanac/index.html`, and the
publication/source notes. This is a generated data package and public atlas
interface. CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, and LOGBOOK apply.
ORBIT is excluded because this artifact makes no planetary comparison.

## CURRENT — physical oceanography

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| C1 | All 5,432 current/state pairs remain physically unresolved, although 208 have atlas links. The package cannot answer literal physical passage or intersection yet. | P2 | `coverage.json`; `build_ocean_motion_release.py` state relation loop | Add dated observed or model current footprints with depth and time support before promoting physical state claims. |
| C2 | Named eddy/state links are regional gateways or locators, not tracked eddy containment. The object page shows this only after opening the relation detail. | P2 | `build_ocean_motion_release.py` eddy state relation loop; `object.js` relation renderer | Put the physical limitation beside each eddy/state link and add observed contours where available. |
| C3 | Six published current lengths are ranked separately from bounds, sampled reaches, and variants. This prevents false precision. | P3 | `measurements.json`; `coverage.json` | Preserve scope labels and rank eligibility in future updates. |

## SOUNDER — data stewardship

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| S1 | External source rights and citation terms are not audited across the candidate source set. External deposition remains blocked. | P1 | `sources.json` has URLs but no rights field; `almanac/release/README.md` lists audit as remaining | Complete a source-by-source terms and attribution table before archival publication. |
| S2 | Lower-bound measurements point to the OSW length ledger rather than the originating paper or gate calculation receipt. | P2 | `build_ocean_motion_release.py`, `length_lower_bound` row creation | Attach primary source IDs and the calculation/geometry receipt to each bound. |
| S3 | External source rows lack title, provider, version or publication date, access date, and preferred citation. URLs alone are weak archival metadata. | P2 | `build_ocean_motion_release.py` `add_source`; `sources.json` | Enrich the source registry from ledgers and manually verify missing fields. |

## CHART — ocean cartography

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| G1 | The 16 exported point geometries are labelled editorial locators and have CRS84, but lack point-specific method and positional uncertainty. | P2 | `geometries.geojson`; `build_ocean_motion_release.py` NASA locator loop | Add locator method, precision, and uncertainty or an explicit unknown value. |
| G2 | Current/state arrow decisions carry source arrow IDs, but the release does not carry the arrow geometries needed to independently inspect each crossing. | P2 | `relations.json` `cartographic_source_arrow_ids`; copied state matrix | Archive permitted source geometry or a compact crossing receipt with geometry digest and method. |
| G3 | The separate tile collection now preserves all 70 NASA crops and their unwrapped longitude boxes, with a geographic role label. | P3 | `tiles.json`; `check_ocean_motion_release.py` tile check | Keep the crop inventory separate from object identity. |

## BEACON — public-science editing

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| B1 | The object page turns internal predicates into space-separated code words, such as “shared source region gateway only.” | P2 | `object.js` relation renderer | Write a small reviewed label and explanation dictionary for the public view. |
| B2 | Repeated “Source” links do not tell readers which NASA release, paper, or register supports a claim. | P2 | `object.js` `sourceLink` | Display a short source title next to each claim and retain the direct link. |
| B3 | The candidate and almanac explain that movie geography and locators do not prove object identity or footprint. | P3 | `object.html`; `almanac/index.html` | Keep this qualification beside future map and film views. |

## HARBOR — accessibility

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| H1 | Object search uses a 306-option datalist and only reacts to `change`; keyboard and assistive technology behavior needs a dedicated review. | P2 | `object.html` search control; `object.js` change handler | Add a clear submit action and test keyboard selection, free-text IDs, and screen reader announcements. |
| H2 | A failed package fetch changes a paragraph that is not a live region, so the load error may not be announced. | P2 | `object.js` catch; `object.html` `#object-summary` | Add an appropriate status or alert region and visible recovery guidance. |
| H3 | The review has no narrow viewport, zoom, contrast, or screen reader evidence for the new object page. | P2 | `test_motion_almanac_browser.py` candidate page checks | Run the repository accessibility and browser gate on this route. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| K1 | `schema.json` mainly names required fields. The validator does not check all types, numeric ranges, URL shape, or the generated GeoJSON/CSV values against those schemas. | P2 | `build_ocean_motion_release.py` schema block; `check_ocean_motion_release.py` | Make collection schemas executable and validate coordinate, numeric, enum, and cross-format constraints. |
| K2 | Browser coverage checks three object IDs, not every evidence class or the full tile and source-link routes. | P2 | `test_motion_almanac_browser.py` object-page checks | Add representative cases for all evidence and identity classes and link resolution. |
| K3 | SHA-256 receipts, copied source ledgers, offline cross-reference checks, and a guard against `python -O` make this candidate reproducible. | P3 | `manifest.json`; `check_ocean_motion_release.py` | Retain a deterministic rebuild check in CI. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| L1 | The manifest hashes inputs and outputs but does not record the builder source commit or a code digest. The candidate currently lives in an uncommitted working tree. | P2 | `manifest.json`; Git status at review | Record a code digest and commit identifier when freezing the reviewed candidate. |
| L2 | The repository's top-level public status and dataset citation are not yet reconciled with this candidate. | P2 | `README.md`, `CITATION.cff`, `plans/release-reconciliation.md` | Reconcile them only for a reviewed public promotion; keep software and dataset citations distinct. |
| L3 | The package, page, and plan clearly say “release candidate”; no DOI or remote publication is claimed. | P3 | `manifest.json`; `object.html`; `plans/ocean-motion-atlas-publication.md` | Preserve this status until the publication gate is complete. |

## Synthesis

Roles reviewed: 7  
P1 blockers: 1 | P2 issues: 15 | P3 notes: 5  
Verdict: **NEEDS-WORK** for external publication. The local candidate is useful
for continued review.

Top finding: rights and citation terms are missing from the source registry.
SOUNDER and LOGBOOK agree that provenance must be archival before deposition;
CURRENT and CHART agree that map links must not become physical flow claims.

Three priority amendments:

1. Extend `sources.json` with verified rights, provider, title, date, citation,
   and source receipt for every external source; block deposition until complete.
2. Add source or model geometry and uncertainty for any physical current/state
   or eddy/state claim, while keeping locator-only rows explicitly unresolved.
3. Make schemas executable, finish object-page keyboard and screen reader
   review, and pin code plus data together in the eventual release manifest.

## Corrections made during this review

- Fixed object-page links back to current, eddy, and state almanac entries.
- Registered all URLs on NASA object relations and preserved the source-backed
  alias URL where provided.
- Made copied source-ledger paths resolve inside the package.
- Added CRS84 to editorial locators and exported all 70 NASA movie crops as a
  separate collection, with cross-reference validation.
- Made the release validator reject optimized Python execution, where
  assertions would otherwise be disabled.

Validation after corrections: `py analysis/build_ocean_motion_release.py`,
`py analysis/check_ocean_motion_release.py`, `py analysis/test_motion_almanac_browser.py`,
and `node --check almanac/object.js` passed. The broader release gate and
accessibility review were not run in this role check.

## Follow-up corrections on 2026-09-29

The finding counts above record the initial review. Subsequent work attached
the five derived lower bounds to their original sources and gate-distance
receipts (S2), added descriptive source labels and public relation text (B1/B2),
made object search an explicit submit form with a live load status (H1/H2),
and tested keyboard submission and a 375 px viewport. JSON Schema validation
now runs for every collection row with types, ranges, and controlled values
(K1); the validator also compares CSV and GeoJSON against their JSON records.
The manifest hashes the build and interface code (L1). Locator rows now state
their editorial method and unquantified positional uncertainty (G1). A source-family
terms review is recorded in `almanac/release/source-terms-audit.md`.

The P1 external-publication block remains: the Horizon register, research
sources, and cartographic provider still need a complete source-specific terms
and citation pass. A subsequent observation export adds 12 NOAA sample dates
and 92,891 dated detections as a collection separate from named eddy entities;
the source review queue now has 96 used external source rows. The candidate is
not approved for deposition.

## Citation follow-up

An explicit Crossref refresh retrieved publisher-deposited bibliographic
metadata for all 30 DOI URLs in the used-source queue. The offline package now
pins title, authors, publisher, date, and response digests for those records.
The source review queue still flags their citation review and content rights as
pending. Marine Regions' own citation and current service-link request are
recorded in `THIRD-PARTY-NOTICES.md`. This narrows SOUNDER S3 but does not
change the external-publication verdict.
The object-page browser check now verifies accessible names and roles for its
search combobox, submit button, and NOAA state table, as well as keyboard
submission and narrow-screen reflow. A human screen reader review remains.
The candidate now exports the OSW motion taxonomy and all 125 editorial
current locators alongside the 16 NASA object locators. Each point remains
labelled as an approximate atlas address, with no observed-path claim.

## Movie directory follow-up

The candidate now exports all 877 display-overlap decisions between NASA's 70
regional crop rectangles and OSW's 56 approximate state polygons as a distinct
`tile_state_relations` collection. Its predicate is `display_overlap`, its
physical relation remains `unresolved`, and the validator compares every
fraction against the pinned source ledger. The new `almanac/movies.html`
directory exposes all 70 crops with search, zoom and state filters, NASA links,
and OSW object/state navigation. Browser checks cover the full row count,
filters, a state link, and a 375 px viewport. This closes a navigation gap;
it does not resolve the P1 source terms issue or supply physical flow geometry.

The subsequent source audit pinned official NASA SVS API bibliography and
credits for all seven release pages, including response digests, and identified
the July 2017 NOAA *Marine Weather Information Guide* behind 11 current
records. The live Horizon register displays a Woods Hole Group copyright
notice, so compilation reuse remains an explicit unresolved publication gate.

The candidate now includes a 97-row `length_assessments` collection built from
the source-specific length evidence and illustrated-span ledgers. It keeps
published length ranks, lower bounds, proposed length, and drawn-arrow span
ranks in separate columns and exposes each current's status on its object
page. This improves full-inventory auditability; it does not increase the
number of source-backed whole-current length estimates (six).

NOAA's product page now anchors title, version, date, and multi-provider credits
for all 12 sampled MUNSTER NetCDF files. This raises source-title coverage to
53 of 96 used external sources. Their upstream attribution and data terms
remain in the release review queue.

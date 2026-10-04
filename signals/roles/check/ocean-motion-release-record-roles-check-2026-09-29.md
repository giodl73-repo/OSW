---
skill: roles-check
topic: ocean-motion-release-record
date: 2026-09-29
roles_used: 7
p1_count: 1
verdict: NEEDS-WORK
working_tree: review of the local release candidate; no published dataset or frozen commit
---

# OSW role review: ocean motion release record

## Artifact and selection

Reviewed `almanac/release/METHODS.md`, `CHANGELOG.md`,
`DATASET-CITATION-DRAFT.json`, their hashed copies in `v0.1.0/`, the package
manifest, source review queue, object-page length status, and the build and
validation code. This is a scientific dataset candidate and atlas reading
surface. CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, and LOGBOOK apply.
ORBIT does not apply because no planetary comparison is made.

## CURRENT — physical oceanography

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| C1 | The method correctly says cartographic and editorial state links cannot establish physical current passage, but the desired per-state current inventory remains physically unresolved. | P2 | `METHODS.md` atlas section; 5,432 current/state relation rows | Add dated source or model current paths with depth and uncertainty before stating passage. |
| C2 | Twelve MUNSTER days and three short June track windows cannot identify every eddy or establish a continuous seasonal climatology. | P2 | `METHODS.md` eddy section; `observation_sets.json` | Preserve dates and product support beside all derived eddy counts. |
| C3 | Published estimates, geographic floors, proposed lengths, and drawn arrows are explicitly separated. | P3 | `METHODS.md` length section; `length_assessments.json` | Keep rank eligibility scoped to published estimates. |

## SOUNDER — data stewardship

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| S1 | Rights and citation review remains pending for all 96 used external sources, with the Horizon compilation and credited arrow layer high impact. | P1 | `source-review-queue.csv`; `source-terms-audit.md` | Complete source-specific rights and attribution decisions before deposition. |
| S2 | The citation draft carries a proposed creator from the software record; dataset authorship, publisher, year, rights, DOI, and landing page are deliberately unconfirmed. | P2 | `DATASET-CITATION-DRAFT.json` | Confirm them with the owner and archive only after the package passes publication review. |
| S3 | Source titles exist for 53 of 96 used external sources, with Crossref, SVS, and MUNSTER receipts; the remaining 43 need item-level bibliographic work. | P2 | `coverage.json`; pinned metadata ledgers | Continue the review queue in record-impact order. |

## CHART — ocean cartography

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| G1 | Current locator points have CRS and an explicit uncertainty limit but no measured flow boundary. | P2 | `geometries.geojson`; `METHODS.md` | Keep point symbols and text alternatives visibly distinct from footprints. |
| G2 | Arrow-derived spans are reproducible from the cited source layer and digest, yet raw arrow polygons are absent from this package while their redistribution terms are unresolved. | P2 | `length_assessments.csv`; `THIRD-PARTY-NOTICES.md` | Retain compact calculation receipts and only archive source geometry when permitted. |
| G3 | NASA crop overlap uses display area and is explicitly labelled geographic navigation. | P3 | `tile_state_relations.csv`; `METHODS.md` | Preserve the `display_overlap` predicate in future atlas views. |

## BEACON — public-science editing

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| B1 | The first proposed citation title could be read as physical state relations; it was changed to “Atlas Relations” during this review. | P3 | `DATASET-CITATION-DRAFT.json` | Keep the final title equally specific. |
| B2 | The method book states what each join can and cannot prove, but its detailed explanation is several clicks from some object views. | P2 | `METHODS.md`; `object.html` | Link the method and source review beside the relevant object claims. |
| B3 | The landing page calls the package a release candidate and links the draft citation rather than claiming a DOI. | P3 | `almanac/index.html` | Retain this status until public promotion. |

## HARBOR — accessibility

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| H1 | Automated browser checks cover object search, the movie directory, and narrow reflow; a human screen reader pass for the integrated release routes is still missing. | P2 | `analysis/test_motion_almanac_browser.py` | Review search, tables, source links, and evidence labels with a screen reader before promotion. |
| H2 | The new release document links have meaningful names in the almanac introduction. | P3 | `almanac/index.html` | Keep visible link text specific as more files are added. |
| H3 | The candidate method book is plain structured Markdown with headings and lists. | P3 | `METHODS.md` | Verify accessible rendering on the final host. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| K1 | The manifest hashes the three new release documents and the validator checks byte equality and draft status. | P3 | `manifest.json`; `check_ocean_motion_release.py` | Retain these checks after version freeze. |
| K2 | The current validator checks candidate documents and row contracts, but a clean-checkout full repository validation has not been run for this package. | P2 | Local command record; `plans/release-reconciliation.md` | Run the full documented gate from the reviewed checkout before promotion. |
| K3 | Source metadata refresh commands are explicit and normal builds are offline. | P3 | `fetch_ocean_motion_crossref_metadata.py`; `fetch_ocean_motion_nasa_svs_metadata.py` | Preserve receipt hashes and avoid implicit network calls in validation. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| L1 | The candidate package is still in a modified, untracked working tree, so no source commit can yet identify its published bytes. | P2 | Git status; `manifest.json` | Freeze reviewed code, data, and document hashes together before deposition. |
| L2 | The citation draft explicitly leaves publication metadata blank, and public Atlas status still needs the separate release reconciliation gate. | P2 | `DATASET-CITATION-DRAFT.json`; `plans/release-reconciliation.md` | Reconcile public status, author, archive, and version at the final owner decision. |
| L3 | A changelog now records the first candidate without implying an earlier DOI or public supersession. | P3 | `CHANGELOG.md` | Append changes only for a new reviewed version. |

## Synthesis

Roles reviewed: 7  
P1 blockers: 1 | P2 issues: 11 | P3 notes: 9  
Verdict: **NEEDS-WORK** for external publication. The local candidate is
reviewable and continues to improve.

Top finding: the source review queue still lacks rights and citation decisions
for the used external source set. SOUNDER and LOGBOOK agree that a DOI and
publisher must follow, not precede, a reviewed release. CURRENT and CHART
agree that geographic aids must remain distinct from physical flow geometry.

Three priority amendments:

1. Complete the source-specific rights and bibliographic queue, beginning with
   the Horizon compilation and credited arrow layer.
2. Acquire source or model current paths and uncertainty to move selected
   current/state relations beyond map-symbol evidence.
3. Finish the integrated accessibility and clean-checkout release gate, then
   confirm the dataset citation and publication destination with the owner.

During this review, the proposed dataset title was narrowed to “Atlas
Relations,” and the draft gained explicit unresolved rights and upstream
source fields. Object pages gained direct methods and source-audit links near
the measurement explanation. The new release documents are hashed in the
generated manifest. Finding counts above reflect the review before that fix.

## Source evidence follow-up

A direct source-page and PDF pass verified titles and response digests for ten
more used external URLs, raising title coverage to 63 of 96. The NOAA PMEL
Johnson et al. article explicitly forbids further electronic redistribution;
the candidate keeps only its link and factual source-scoped decisions. The
University of Western Australia thesis's Leeuwin Current lower-bound wording
was checked on PDF viewer page 108 and that locator now travels with the
measurement. These observations narrow source traceability but do not resolve
the Horizon compilation or other outstanding rights decisions.

## Material-use scope follow-up

The 96-source queue now distinguishes one compiled name/date register, twelve
derived NOAA daily products, one derived cartographic layer, one gazetteer
crosswalk, eleven NASA navigation/description sources, and seventy sources for
source-scoped factual claims. All external source assets are recorded as absent
from the package. This makes SOUNDER S1 actionable by use, while every
source-specific permission and attribution decision stays pending.

## Bibliographic follow-up

The source metadata pass now identifies all 96 used external sources by
verified title, including 48 curated source URL records and three NASA
media-group addresses that inherit pinned release-page metadata. NOAA's Loop
Current page date is recorded as a source update, not a publication date.
The package build, release validator, full motion almanac check, browser check,
and `git diff --check` pass after this change. The publication verdict remains
**NEEDS-WORK**: title coverage is not a source-specific rights decision, and
physical current/state passage remains largely unresolved.

## Dated physical-front follow-up

NOAA OPC's public NAVO bulletin supplied a dated 2026-09-28 Gulf Stream
frontal analysis. The candidate now pins 306 north-wall and 204 south-wall
coordinates and records eight front intersections across five approximate OSW
states. This is a physical observation of analyzed surface fronts, not a
current axis, complete footprint, or perennial passage. The state passport
and object page expose the date and relation label. SOUNDER S1 remains P1:
unlike the linked NASA films and absent cartographic polygons, the reported
NAVO coordinates are redistributed in the candidate. Their terms and required
attribution need provider-specific review before external deposition.

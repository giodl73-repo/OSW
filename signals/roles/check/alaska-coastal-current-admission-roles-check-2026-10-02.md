---
skill: roles-check
topic: alaska-coastal-current-admission
date: 2026-10-02
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Alaska Coastal Current: atlas admission review

Source commit: `5298e8b33a918752496ab334fc7e597fed32dc24`, with the current
uncommitted atlas changes. This review covers the new named-current entry,
source-scoped extent, navigation joins, release tables, and presentation.
It is an OSW functional review, not independent scientific peer review.

Selected roles: CURRENT for identity and measurement scope; SOUNDER for
source provenance; CHART for spatial meaning; BEACON for reader claims;
HARBOR for textual and keyboard access; KEEL for regeneration and checks;
LOGBOOK for release status. ORBIT is excluded because this admission makes
no planetary comparison.

Primary evidence: [Stabeno et al. (2016), NOAA repository record](https://repository.library.noaa.gov/view/noaa/13254),
[accepted manuscript](https://repository.library.noaa.gov/view/noaa/13254/noaa_13254_DS1.pdf),
abstract PDF page 2, lines 25–28; introduction PDF page 3, lines 42–59.
The numerical fact is linked and paraphrased; article prose and geometry are
not copied into the release. The pinned Crossref record supplies bibliographic
metadata, not scientific approval or a publication reuse license.

## Findings

| Role | Finding | Severity | Evidence and recommendation |
| --- | --- | --- | --- |
| CURRENT | The coastal system must remain distinct from the offshore Alaska Current and Alaskan Stream. | P3 | Introduction identifies those offshore gyre currents separately. The new `alaska-coastal-gulf` entity, Gulf qualifier, and source-linked alias implement the distinction. Do not merge on shared Alaska wording. |
| CURRENT | The approximate 1,700 km value applies to the paper's regional coastal system. | P3 | Abstract gives Seward and Samalga Pass; the ledger and ranked warning retain those endpoints. Do not extend this value to all coastal flows using the name. |
| CURRENT | A simultaneous whole-current axis and a common depth convention remain unavailable. | P2 | Scope records intermittent 1984–2014 observations and excludes a measured reference streamline. Obtain compatible route/layer evidence before promoting physical state crossings or a common-method length rank. |
| SOUNDER | The source and manuscript locators resolve the factual assertion. | P3 | DOI, six authors, journal, volume, pages, year, and manuscript page/lines are recorded. Retain manuscript-versus-journal dates rather than treating September 2015 as the journal publication. |
| SOUNDER | Direct PDF byte acquisition was denied even though the repository manuscript was readable through the research tool. | P2 | HTTP 403 prevents an independently retrieved PDF digest in this pass. The passage audit explicitly records that limit. Acquire a permitted archival copy before claiming a byte-pinned manuscript receipt. |
| SOUNDER | Source-use chronology previously depended on a single old ledger date. | P3 | The builder now honors per-entry `review_date`, with the existing default retained. The new factual-use decision is dated 2026-10-02; older decisions retain their recorded date. Preserve that distinction. |
| CHART | Three locator points are not a connected coastal route. | P3 | The locator basis identifies offshore Seward, southwest Kodiak, and the Samalga vicinity as independently authored navigation points. Do not connect them into a measured path or calculate current length from them. |
| CHART | ALSK and BERS are candidate point associations only. | P2 | The 56-state matrix retains two `editorial_locator_candidate` rows and unknown physical relations in every state. Compatible observed route or footprint evidence is required for a crossing assertion. |
| CHART | NASA crops supply geographic navigation without feature identification. | P3 | The new crosswalk is `regional_movie_only`; all 70 audited crops are preserved. Keep this label and do not infer a NASA-named current from the movie address. |
| BEACON | The visible name exposes the source's geographic convention. | P3 | Preferred label is Alaska Coastal Current (Gulf of Alaska); the literal paper name remains an alias. Keep the qualifier in directory, rank, record, and packet views. |
| BEACON | The rank is an almanac of differing published extents. | P3 | The new row shows approximately 1,700 km, rank 8, endpoints, and a scope warning; Florida moves to rank 9. Retain the common-method limitation beside the table. |
| BEACON | Inventory size does not establish a global census. | P2 | The source set now has 99 current records and nine admitted length estimates. Continue the unknown-length and route work; preserve source-set wording rather than claiming all currents have been measured. |
| HARBOR | The scope warning is readable as table text. | P3 | The third emphasized warning appears beside the coastal estimate, with source and endpoints. Meaning does not depend on marker color or animation. Retain semantic table markup. |
| HARBOR | The entry has a direct record address and downloadable evidence packet. | P3 | The screened browser check exercises `?id=current%3Aalaska-coastal-gulf`, record title, rank, scope, pending review text, and packet fetch. Keep this route available without selecting a map marker. |
| HARBOR | Automated browser checks do not complete human accessibility review. | P2 | Existing tests cover search, keyboard focus, skip link, reflow, and zoom, but not a complete screen-reader assessment. Human accessibility review remains a publication condition. |
| KEEL | Older ranked measurement IDs and exact passage fingerprints are preserved. | P3 | The new reported length is appended as `measurement:0028` after existing observations and geographic floors. The release checker verifies the nine editorial bindings, including all eight earlier fingerprints. Preserve this admission ordering. |
| KEEL | Navigation joins can be recomputed without a live NASA refresh. | P3 | `--reuse-pinned-tiles` validates schema, picker URL, and 70 unique crop IDs before recomputing point joins. Default operation remains an explicit source refresh. Document and retain the offline option. |
| KEEL | New inventory growth exposed stale test expectations. | P3 | Checks now expect 99 currents, 5,544 pairs, nine ranked rows, and the additional locator markers. Browser assertions verify the new scientific scope and packet, not only changed totals. Regenerate manifests after checker or source edits. |
| LOGBOOK | Candidate documentation had older counts than the generated tables. | P3 | README, METHODS, publication plan, boundary notes, and changelog now use the generated census and claim locator/method counts. Keep documentation reconciled at each release freeze. |
| LOGBOOK | Linked factual use does not grant article redistribution rights. | P3 | The source-use decision and third-party notice export the name/number and OSW notes only. NOAA hosting is not described as an Elsevier reuse license. Re-review any future copied figure, track, or dataset use. |
| LOGBOOK | The complete atlas remains an unpublished candidate. | P2 | The screened copy excludes the pending provider uses; 17 used external source decisions remain pending in the full candidate. Scientific decisions are not prefilled. Continue source, geometry, scientific, and publication work before dataset deposition. |

Roles reviewed: 7. P1 blockers: 0. P2 conditions: 6. P3 findings: 15.
Verdict: APPROVED-WITH-CONDITIONS for this source-scoped admission, not a
public-release approval. CURRENT, CHART, and BEACON agree that the source
extent and editorial point joins do not establish a dated whole-current route.

## Amendments and verification

1. Added a distinct qualified identity, literal source alias, manuscript
   locators, observation-window limits, and a visible scope warning.
2. Preserved existing ranked measurement IDs, appended the new measurement,
   added per-source review dates, and supplied offline crop-join regeneration.
3. Reconciled counts across the data, UI, documentation, and checks, including
   a direct-link and packet test for the new entity.

The full release and screened data/site checks pass. Both screened and
full-almanac browser checks pass, including the new record, rank, and packet.
The research almanac check and screened JavaScript syntax check also pass.
Remaining P2 conditions concern broader
measurement, acquisition, accessibility, and publication work; they do not
justify upgrading this admission to an observed crossing or scientific approval.

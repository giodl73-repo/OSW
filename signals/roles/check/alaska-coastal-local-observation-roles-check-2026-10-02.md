---
skill: roles-check
topic: alaska-coastal-local-observation
date: 2026-10-02
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Dated Alaska Coastal Current local-observation review

Source commit: `5298e8b33a918752496ab334fc7e597fed32dc24`, plus the current
uncommitted atlas changes. This review covers the Shelikof Sea Valley
observation, its ALSK association, source receipt, and screened record display.
The seven roles cover science, provenance, cartography, editing, access,
regeneration, and repository status; ORBIT has no applicable planetary claim.
These are functional OSW review lenses, not external scientific peer review.

Primary evidence is Stabeno et al. (2016), the published article available at
[AOOS](https://workspace.aoos.org/files/2656915/Stabeno_etal_2016_Longterm_Obs_ACC.pdf):
Table 1 caption on printed page 26 (PDF page 4), section 2.2 on printed page
27 (PDF page 5), and the section 3.3 coastal-current context. The paper was
retrieved independently; its bytes have the SHA-256 recorded in the source
registry. The PDF and its figures are linked, not redistributed.

| Role | Finding | Severity | Evidence and recommendation |
| --- | --- | --- | --- |
| CURRENT | The observation supports local current presence, not the complete coastal route. | P2 | The row retains a local-only physical relation and no section endpoints. Obtain compatible observed route geometry before asserting a whole-current state crossing. |
| CURRENT | The 1989 array was in the sea valley, not at the strait exit. | P3 | Table 1 caption and section 2.2 agree on the location exception. Keep the sea-valley locality explicit in the atlas. |
| CURRENT | No transport value or current-axis length is inferred from this observation. | P3 | Only locality and dates are admitted. The nine published length estimates and measurement IDs remain unchanged. Keep these evidence classes separate. |
| SOUNDER | The cited transport interval has explicit day-level bounds. | P3 | The caption supplies 10 May-15 July 1989. Preserve those bounds instead of substituting the entire 1984-2014 paper window. |
| SOUNDER | The analogous 1985 dates are not mutually consistent across the paper passages. | P2 | That interval is excluded; caption and methods state differing bounds. Resolve that discrepancy before admitting a 1985 row. |
| SOUNDER | A PDF digest needs an identified document version. | P3 | The source registry now exports file URL and retrieval date with the AOOS published-PDF SHA-256. It does not identify the accepted manuscript. Retain version-specific file metadata. |
| CHART | ALSK is assigned by the published regional locality. | P3 | The assignment method and boundary limit explicitly identify a semantic Gulf-of-Alaska association. Do not describe it as a measured polygon intersection. |
| CHART | This observation adds no BERS evidence. | P3 | Only ALSK receives the local-presence relation; the two editorial locator candidates remain independent. Preserve the distinction. |
| CHART | No station coordinates or line were digitized. | P3 | The observation has null section endpoints and a no-digitized-geometry status. Do not draw a footprint from the locality name. |
| BEACON | Readers can distinguish a dated study from an atlas locator. | P3 | The screened record adds a separate Published local current observations card with dates, locality, time detail, and spatial limits. Retain the distinct heading. |
| BEACON | The local study must not appear as validation of the 1,700 km ranking. | P2 | The ranking and source-specific estimate retain separate claim IDs. Keep the local-only sentence beside the observation. |
| BEACON | Source access includes the particular publication copy. | P3 | The card provides a DOI citation and a link to the identified published PDF when source_file_url is present. Keep the direct copy link. |
| HARBOR | The observation meaning is available as semantic text. | P3 | Dates and scope are ordinary paragraphs, with no dependence on animation or color. Preserve this representation. |
| HARBOR | State evidence uses a disclosure control. | P3 | The browser test opens Source-reported local presence before reading the dates; closed details are not expected to be visible. Keep keyboard access to the summary. |
| HARBOR | Automated testing leaves human accessibility review open. | P2 | Browser checks cover existing focus, reflow, and zoom behavior, not a complete screen-reader assessment. Retain this publication condition. |
| KEEL | Existing screened claim identities are preserved. | P3 | A comparison against the previous site package verified all 8,633 earlier IDs and fingerprints. The new local relation is appended after existing relations. Preserve this admission behavior. |
| KEEL | Canonical exports retain exact source facts and explicit unknown geometry. | P3 | Release checks assert the observation ID, ALSK, dates, locality, null endpoints, physical limit, and registry file metadata. Preserve these checks. |
| KEEL | The observation is present in the entity evidence packet. | P3 | The browser assertion checks its event ID in the downloaded screened packet. Keep packet and UI evidence connected. |
| LOGBOOK | The full candidate and screened counts differ intentionally. | P3 | Full candidate: 14,244 claims and seven current observations. Screened copy: 8,635 claims and the same seven current observations. Methods and changelog record the new rows. |
| LOGBOOK | The factual-use decision was updated for the newly exported locality and dates. | P3 | No station table, transport numbers, series, figure, or PDF is republished. Re-review future provider data or publication copying. |
| LOGBOOK | This remains an unpublished candidate with scientific decisions pending. | P2 | Seventeen used external source decisions remain open in the full package. Continue scientific, source-use, and release work before deposition. |

Roles reviewed: 7. P1 blockers: 0. P2 conditions: 5. P3 findings: 16.
Verdict: APPROVED-WITH-CONDITIONS for the local observation and presentation.
CURRENT, CHART, and BEACON agree that the published locality is not an
observed whole-current footprint or a length-rank validation.

Three amendments are implemented: retain the sea-valley exception and exact
1989 dates; identify the published-PDF version alongside its digest; expose
local studies on current record pages while preserving existing claim IDs.
Full release and screened package/site checks pass. The screened browser test passes, including the current card, explicit ALSK
disclosure interaction, direct publication-copy link, and evidence packet.
The JavaScript syntax check passes. An initial test assertion incorrectly
read a closed disclosure; the test was corrected to open it. A later initial
navigation failed transiently, and the completed rerun passed. No regular
user browser or source observation was altered by that diagnostic.

The full-almanac browser test also passes, including the new Alaska Coastal
Current record's dates, sea-valley locality, and semantic-state limit.

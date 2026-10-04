---
skill: roles-check
topic: navo-operational-eddy-atlas
date: 2026-09-30
roles_used: 7
p1_count: 1
verdict: NEEDS-WORK
---

# Role review: NAVO operational eddy state observations

Artifact: the pinned 2026-09-25 FREDDIES eddy receipt, state join, candidate
release table, state passport, object page, methods, source notice, and checks.
This is an observational data and atlas presentation change. CURRENT,
SOUNDER, CHART, BEACON, HARBOR, KEEL, and LOGBOOK apply. ORBIT does not apply.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| C1 | Four polygons support a dated surface-feature inventory, not eddy persistence or a multi-year census. | P2 | Source receipt and methods | Keep release date and identity limit on every row and state view. |
| C2 | Warm/cold and cyclonic/anticyclonic are provider classifications, not independently remeasured by OSW. | P3 | Source fields and browser text | Continue attributing these properties to NAVO. |
| C3 | No source match links these four provider codes to historical named rings or NASA model eddies. | P2 | State views | Preserve the separate operational observation class. |

## SOUNDER — data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| S1 | The ZIP has a public-release statement but no item-level reuse license; source polygon coordinates are redistributed in the candidate ledger. | P1 | Source receipt, source review queue | Resolve rights and attribution before public dataset deposition. |
| S2 | The source ZIP has no `.prj`; the datum is unspecified despite degree-like coordinates and matching center fields. | P2 | Source receipt, methods | Confirm the CRS with provider metadata before treating locations as survey-grade. |
| S3 | ZIP and member digests, retrieval time, provider fields, and source URL are pinned. | P3 | Source receipt | Retain these when the source refreshes. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| G1 | Containment is calculated against approximate coast-masked display shapes; it is not a jurisdictional or physical boundary. | P2 | State join, methods | Keep the qualifier beside each containment claim. |
| G2 | The four source polygons fall wholly inside GFST, NWCS, and NADR at this map scale. | P3 | Recomputed state join | Preserve the source geometry and boundary digest for audit. |
| G3 | The atlas lists codes and states but does not yet draw the four polygon outlines on the map. | P2 | Main state view | Add a distinct dated operational polygon layer with a text equivalent. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| B1 | `W26001` and `C26001` can look like lasting names unless identified as one-release provider codes. | P2 | State passport and object page | Keep code, date, and identity limit together. |
| B2 | The state view gives a direct NCEI source link and plain warm/cold/rotation language. | P3 | State passport | Keep a short route to the exact source package. |
| B3 | The four operational polygons must remain distinct from the 131 historical named-eddy records. | P2 | Landing and methods | Preserve separate tables and counts. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| H1 | Native details/summary and list markup make the new state rows keyboard accessible in principle. | P3 | State passport | Include them in a human keyboard and screen reader pass. |
| H2 | Provider code, polarity, rotation, containment, source, and date are available in text; no color inference is required. | P3 | State and object pages | Maintain the text alternative when drawing polygons. |
| H3 | The new rows increase live state-result content; a human announcement and reflow review is still missing. | P2 | State passport | Test the final state route with a screen reader and narrow zoom. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| K1 | The offline builder uses a pinned JSON receipt and the validator recomputes state intersections. | P3 | Build and release checks | Keep network refresh explicit and separate. |
| K2 | The optional source refresh depends on `pyogrio==0.12.1` and rejects changed date/code sets. | P2 | Fetch script | Document a deliberate refresh path for the next provider version. |
| K3 | The browser check covers the GFST disclosure and two NADR codes; NWCS remains covered by the data validator. | P3 | Browser and release checks | Add a broader viewport check when the polygon map layer is drawn. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| L1 | The release remains a candidate with an unresolved source-specific license and no DOI. | P2 | Release notes and source queue | Resolve the source gate before deposition. |
| L2 | Methods and notices now identify the exact 2026-09-25 source and its public-release statement without claiming a license. | P3 | Documentation | Retain that distinction in public copy. |
| L3 | The working tree and candidate package are not a frozen source commit. | P2 | Manifest and Git state | Run release reconciliation from a reviewed commit before public promotion. |

## Synthesis

Roles reviewed: 7  
P1 blockers: 1 | P2 issues: 11 | P3 notes: 9  
Verdict: **NEEDS-WORK** for external dataset publication. The candidate is
usable for source-linked, dated state inspection. SOUNDER and LOGBOOK agree
that a public-release statement alone does not settle the package's reuse
license. CURRENT, CHART, and BEACON agree that operational designations and
dated polygons cannot be presented as persistent named eddies.

Three amendments:

1. Resolve the NAVO/NCEI package's exact reuse and attribution terms before deposition.
2. Confirm source CRS, then draw a dated polygon layer with matching text claims.
3. Review the state route with keyboard and screen reader, and freeze the source commit for release reconciliation.

During this review, G3 was addressed in the candidate atlas: a separate dated
outline layer and a visible toggle were added. Its simplified display paths
are not used in the state join, and the state readings remain the text
alternative. A human screen reader and zoom pass remains open.

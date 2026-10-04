---
skill: roles-check
topic: ocean-motion-claims-contract
date: 2026-09-30
roles_used: 7
p1_count: 1
verdict: NEEDS-WORK
---

# Role review: ocean-motion claim records and object-page provenance

Artifact: generated `claims` JSON/CSV, target `claim_id` links, schema and
manifest, release validator, coverage metrics, methods, and the object-page
claim panel. The data contract and public reading surface call for CURRENT,
SOUNDER, CHART, BEACON, HARBOR, KEEL, and LOGBOOK.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| C1 | All 7,336 named-eddy/state claims retain unknown physical containment; an eddy source record supplies name or point context, not a dated footprint. | P3 | Eddy assessment claims | Keep `unresolved_assessment` even when a candidate gateway exists. |
| C2 | The Gulf Stream diagnostic claim carries only a dated partial geostrophic reach. | P3 | Diagnosed claim | Do not allow it into whole-current ranks or permanent passage statements. |
| C3 | Current/state atlas decisions are map and locator evidence, not observed circulation paths. | P2 | 5,488 matrix claims | Keep the evidence class and physical-relation qualifier with every reuse. |

## SOUNDER — data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| S1 | 6,365 claims point to exact state or crop decision rows; 7,464 point to source eddy or NASA object records. The validator checks both pointer types. | P3 | Internal provenance | Keep pointer validation when source ledgers change. |
| S2 | All 64 external-source claims have source passages or provider-field locators; the generated locator worklist has zero pending rows. A locator records where evidence can be checked, not a completed scientific review. | P3 | Claim coverage | Preserve locator checks and review each assertion's interpretation and scope. |
| S3 | Every claim has a null reviewer/date and `not_individually_reviewed`. A fingerprint-bound decision ledger and 64-row first-pass worksheet now support individual review without inventing completed decisions. | P2 | Review fields | Complete scientific decisions before public dataset promotion. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| G1 | Crop/state claims use a display-overlap predicate and unresolved physical relation. | P3 | Tile claims | Retain this wording on map and state pages. |
| G2 | Internal pointers for named-eddy/state assessments resolve to one source eddy record, not a polygon for each state pair. | P2 | Eddy pointers | Label these as source-record pointers rather than exact state-geometry evidence. |
| G3 | Dated NAVO polygon and NOAA geostrophic claims remain in separate evidence classes. | P3 | Observation claims | Keep their time and geometry roles distinct in later maps. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| B1 | The object page exposes counts for exact ledger rows, source eddy records, and specific source locators. | P3 | Claim panel | Preserve the separate labels as review progresses. |
| B2 | “Claim record” could sound like a verified finding even when it normalizes an unresolved assessment. | P2 | Object-page heading | Keep the candidate, unresolved, and pending review explanation near the heading. |
| B3 | Six source-reported local current relations now link to their underlying observation claims. | P3 | Support links | Expand this pattern when additional dated observations are admitted. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| H1 | The claim panel uses a semantic section and native details control for locator gaps should they recur. | P3 | Object page | Retain semantic controls rather than custom disclosure JavaScript. |
| H2 | Claim counts and locator status are in text, independent of map color. | P3 | Object page | Keep text parity with map evidence classes. |
| H3 | A human screen-reader and keyboard pass of the new claim panel has not been recorded. | P2 | Accessibility gate | Complete it before public promotion. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| K1 | Claims are generated offline, manifest-hashed, schema-validated, and linked one to one to target rows. | P3 | Build and validator | Keep generation deterministic. |
| K2 | The validator resolves every internal JSON pointer and checks relation/measurement values and claim references. | P3 | Validation | Retain the pointer and foreign-key checks. |
| K3 | The claim collection duplicates target records for normalization but is excluded from source review impact counts. | P2 | Source accounting | Keep the exclusion documented so source priority is not inflated. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| L1 | README, methods, changelog, schema, coverage, and object page now state the claim collection's scope. | P3 | Release record | Update counts together after any source-set change. |
| L2 | Narrow factual use is recorded for 66 further sources; 17 rights questions remain, including 16 provider-value source rows and one credited cartographic service. | P1 | Publication gate | Resolve those uses before public release; the claim table does not grant rights. |
| L3 | The package remains a local candidate without frozen source commit, DOI, or owner publication decision. | P2 | Release status | Keep publication wording conditional until reconciliation passes. |

## Synthesis

Roles reviewed: 7  
P1 blockers: 1 | P2 issues: 7 | P3 notes: 13  
Verdict: **NEEDS-WORK** for public dataset publication. The claim contract is
suitable for candidate review. SOUNDER and LOGBOOK agree that provenance
structure does not substitute for source rights or individual review. CURRENT
and CHART agree that state and eddy pointers preserve atlas context without
proving physical passage or containment.

Three amendments:

1. Resolve source-specific publication terms for the 16 provider-value rows and the credited cartographic service before assigning a public dataset license.
2. Complete individual scientific reviews using the fingerprint-bound workflow, prioritizing the six ranked-length passages and source-identified NASA relations; retain the empty locator worklist as a regression check.
3. Complete a human accessibility pass on the claim panel and freeze a reviewed source commit before public promotion.

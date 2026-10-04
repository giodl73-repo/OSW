---
skill: roles-check
topic: ocean-motion-rights-screened-preview
date: 2026-09-30
roles_used: 7
p1_count: 2
verdict: NEEDS-WORK
---

# Role review: rights-screened ocean-motion preview

Artifact: `analysis/build_ocean_motion_safe_preview.py`, its checker, and
`almanac/release/v0.1.0-rights-screened-preview/`. Type: derived data export.
Selected roles: CURRENT for physical claims, SOUNDER for source lineage, CHART
for map relation semantics, BEACON for public interpretation, HARBOR for
accessible alternatives, KEEL for reproducibility, and LOGBOOK for release
status. This is an internal role-lens review, not external scientific approval.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| C1 | All six ranked estimates survive, but their incompatible system scopes and unreviewed status survive too. | P2 | `length_assessments` | Carry the source-passage audit into any reader-facing use. |
| C2 | Excluding the dated NOAA and NAVO products removes observational eddy contours and the partial Gulf Stream path; the remaining 56-state relation matrix is predominantly unresolved or cartographic. | P2 | `relations`, `observation_sets` | Present remaining state links by evidence class, never as current-core or eddy-footprint intersections. |
| C3 | A source-rights filter cannot decide whether a physical claim is correct. | P3 | `claims` | Require independent claim decisions before scientific endorsement. |

## SOUNDER — data stewardship

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| S1 | The preview removes pending external source IDs and direct URLs, and strips 24 retained ArcGIS illustrated spans. | P3 | Builder and checker | Keep the exclusion rule executable. |
| S2 | Internal-ledger locators remain in the preview while their ledger files are absent; the preview is therefore not independently reproducible. | P1 | `claims`, `sources` | Create a separately screened provenance bundle or keep this strictly as a review artifact. |
| S3 | Dependence on provider values can hide behind an OSW ledger source ID; the ArcGIS arrow IDs were caught, but future joins need an explicit upstream-dependency field. | P2 | Source graph | Record source lineage on every derived row and validate it. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| G1 | Removing ArcGIS arrow relations avoids showing their source geometry as settled current crossings. | P3 | `relations` | Preserve the conservative exclusion. |
| G2 | The 141 retained geometries are editorial locators; none is an observed current footprint. | P2 | `geometries` | Keep geometry role and uncertainty beside every map symbol. |
| G3 | State relation coverage is now partial; a missing row does not mean a current or eddy is absent. | P2 | `relations`, `named_eddy_state_assessments` | Display excluded/unassessed separately from observed absence. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| B1 | “Rights-screened preview” is accurate; “public dataset” would overstate readiness. | P3 | Status | Keep the preview label visible in every download surface. |
| B2 | Counts fall from 98 to 95 named currents and 131 to 35 named eddies; unexplained count changes would look like a scientific revision. | P2 | Coverage | Explain that these are source-use exclusions, not discoveries or retractions. |
| B3 | The six-source length audit is not copied into the preview folder. | P2 | Reader path | Link or include the audit before putting rank rows in a public interface. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| H1 | CSV and JSON give text routes to the data. | P3 | Export | Preserve both formats. |
| H2 | No preview-specific reader interface or explanation currently announces excluded observations. | P2 | Presentation | Add a plain-language coverage and unknowns page before publishing the preview. |
| H3 | The existing atlas still needs a human keyboard, zoom, and screen-reader pass. | P2 | Site | Record the pass against the actual release candidate. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| K1 | Builder and independent checker pass schema, manifest, CSV parity, and claim graph checks. | P3 | Validation | Run both after every source-set edit. |
| K2 | The preview manifest pins the full candidate manifest but does not include screened source ledgers or a standalone build environment. | P2 | Manifest | Add reproducibility materials before citable deposition. |
| K3 | The checker validates retained references, but upstream dependency classification is presently encoded in script-specific rules. | P2 | Checker | Move dependencies into canonical metadata and test them generically. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| L1 | The full candidate and public-facing atlas still include values associated with unresolved source uses; the preview does not replace them. | P1 | Repository and site | Reconcile all public surfaces and source terms before release. |
| L2 | The preview carries no dataset DOI, publication authority, or human claim review. | P2 | Status | Retain candidate status and seek final owner decision only after the gates pass. |
| L3 | The screening report counts 23 pending external source rows, while the release gate tracks 17 **used** pending sources; the six catalog-only NASA rows explain the difference. | P3 | Coverage | State both denominators where counts are compared. |

## Synthesis

Roles reviewed: 7  
P1 blockers: 2 | P2 issues: 12 | P3 notes: 7  
Verdict: **NEEDS-WORK** for public dataset publication.

Top finding: source-use filtering alone cannot make the preview a reproducible
or publishable dataset while upstream ledgers, site surfaces, scientific review,
and accessibility remain unresolved. SOUNDER and KEEL agree on the missing
standalone provenance; CHART and BEACON agree that excluded rows must never be
interpreted as observed absence.

Three amendments:

1. Build explicit upstream-dependency metadata and a screened provenance bundle.
2. Add a preview coverage explanation and ensure the site does not silently mix
   full-candidate counts with screened-preview counts.
3. Complete scientific claim review, human accessibility review, and source-use
   decisions before archive publication.

## Post-review changes

The builder now copies the ranked-length audit and a preview README into the
manifest-hashed export. The README explains the reduced counts, source-use
exclusions, and meaning of missing rows, addressing B2 and B3 for the data
download path. It also copies four screened ledger excerpts and verifies all
8,078 retained internal JSON pointers against the full candidate; S2's
missing-pointer concern is resolved for review. The excerpts are not full
source-acquisition records, and the public-surface gate in L1 remains open.
Source usage counts are now recalculated after screening, and the report
separates direct pending-source references from 118 internal-ledger relations
that carried ArcGIS arrow IDs.
The NASA crop directory now reads the screened export. A separate static-site
boundary audit finds the main almanac, object pages, and directly served full
candidate still expose 17 pending used external sources, so L1 remains a P1
publication blocker. The boundary check compares the exact pending source-ID
digest against the preview rather than relying on a count alone.

---
skill: roles-check
topic: ocean-motion-provider-value-audit
date: 2026-09-30
roles_used: 4
p1_count: 1
verdict: NEEDS-WORK
---

# Role review: provider values in the ocean-motion release candidate

Artifact: corrected `provider_asset_redistributed` flags and validator,
source queue, rights audit, notices, four source-specific decision packets,
and prepared inquiry drafts. The issue is provenance and release status, so
SOUNDER, KEEL, LOGBOOK, and BEACON are the applicable installed roles. The
scientific geometries and UI have not changed in this correction.

## SOUNDER — data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| S1 | Twelve MUNSTER files contribute 92,891 exported centers and properties; the absence of NetCDF files does not mean the candidate merely links to NOAA. | P2 | Source queue | Retain all 12 `provider_asset_redistributed=true` flags. |
| S2 | The Horizon register contributes 96 named eddy records and dates; it is a materially carried compilation. | P2 | Source queue | Retain its true flag and source-specific rights decision. |
| S3 | NOAA's MUNSTER page gives credit phrases, but applicability of upstream and extracted-record redistribution terms remains unresolved. | P1 | MUNSTER decision packet | Obtain an authoritative source-specific answer before public publication. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| K1 | The generated queue now shows exactly 16 provider-value rows and the validator asserts the 12 MUNSTER URLs plus four other sources. | P3 | Builder and validator | Keep the invariant when new source families are added. |
| K2 | `provider_asset_redistributed` is a broad boolean for copied source values, including a compilation, extracted rows, source coordinates, and packed fields. | P2 | Source schema | Retain the README definition and consider a more detailed material inventory in a later schema version. |
| K3 | The rebuild, package validator, browser check, and almanac check pass after the source metadata correction. | P3 | Validation | Keep these checks in release reconciliation. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| L1 | The release audit and third-party notices now state which exported values need redistribution decisions. | P3 | Rights audit and notices | Keep their counts synchronized with the generated queue. |
| L2 | Four extra LSA subsets outside `v0.1.0/` would still be exposed by public repository publication. | P2 | LSA packet and notices | Review the repository boundary as well as the dataset archive. |
| L3 | Inquiry drafts exist, but no provider has been contacted and no reply is evidence of permission. | P3 | Outreach drafts | Record respondent, scope, and date before changing rights status. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| B1 | Saying “no raw NetCDF” alone could lead a reader to believe no NOAA product data is redistributed. | P2 | Release README | Keep the extracted-value explanation beside the absence statement. |
| B2 | The public candidate status remains explicit; neither OSW nor its atlas is presented as a NOAA or Horizon publication. | P3 | Release README | Preserve this wording until the release gate passes. |
| B3 | The outreach drafts specify website, repository, and archive uses separately, making a provider response easier to apply without overgeneralizing it. | P3 | Inquiry drafts | Keep those destinations distinct in the eventual decision record. |

## Synthesis

Roles reviewed: 4  
P1 blockers: 1 | P2 issues: 5 | P3 notes: 6  
Verdict: **NEEDS-WORK** for public publication. The corrected queue is
appropriate for candidate review. SOUNDER and BEACON agree that extracted
provider values must remain visible in release language. SOUNDER and LOGBOOK
agree that the NOAA and Horizon use scopes require affirmative source-specific
decisions before rights status changes.

Three amendments:

1. Obtain and record source-specific terms for all 16 provider-value source rows, starting with the 12 MUNSTER files and Horizon compilation.
2. Inventory the exact fields and repository/package destinations in any eventual permissions and preserve those limits in the source ledger.
3. Rerun the generated source queue and release validation after each accepted rights decision; do not treat prepared inquiry drafts as provider approval.

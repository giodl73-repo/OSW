---
skill: roles-check
topic: gulf-stream-geostrophic-path
date: 2026-09-30
roles_used: 7
p1_count: 1
verdict: NEEDS-WORK
---

# Role review: dated Gulf Stream geostrophic reach

Artifact: the pinned NOAA LSA 2026-09-25 velocity subset, frozen-time
streamline method, state join, generated candidate rows, map and object-page
reading, and tests. This scientific data and atlas surface calls for CURRENT,
SOUNDER, CHART, BEACON, HARBOR, KEEL, and LOGBOOK. ORBIT does not apply.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| C1 | Surface geostrophic velocity omits ageostrophic and vertical flow, so the line is not a parcel path or full current axis. | P2 | Methods and geometry | Keep the frozen-field and surface qualifiers beside the line and length. |
| C2 | The north adjacent seed stops at 620 km while the chosen and south seeds reach 50°W; the path is seed sensitive. | P2 | Sensitivity receipt | Do not enter 2,277 km in the whole-current rank. |
| C3 | The 50°W gate makes the result a partial regional reach with deliberately bounded endpoints. | P3 | Seed and stop method | Preserve gates and do not compare it to published whole-current estimates. |

## SOUNDER — data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| S1 | The exact NOAA NetCDF and packed 0.25° velocity subset are pinned with SHA-256, field units, fill value, and time bounds. | P3 | Source receipt | Keep raw packed values and source digest in future refreshes. |
| S2 | NOAA labels the NRT source experimental; field uncertainty and track positional error are not quantified in this pilot. | P2 | Source metadata and method | Add an ensemble or multi-date support study before stating a stable route. |
| S3 | NOAA LSA specifies acknowledgment; the candidate redistributes a velocity subset and still needs item-level reuse/citation review for deposition. | P1 | Source queue and notices | Resolve source-specific terms and citation before public dataset release. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| G1 | The dotted green line and map key distinguish this diagnostic from the NAVO analyzed fronts and editorial locators. | P3 | Map layer | Keep dates and evidence class visible together. |
| G2 | Clipped line segments cross GFST and NWCS only under approximate coast-masked OSW state shapes. | P2 | State join | Keep the approximate-boundary qualifier beside both state lengths. |
| G3 | The route is represented by 229 geodesic integration points in CRS84; no formal uncertainty corridor is drawn. | P2 | Geometry table | Derive a corridor only after seed and product variability are quantified. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| B1 | A prominent “2,277 km” can be repeated as “the Gulf Stream is 2,277 km long.” | P2 | Map caption and object page | Keep “partial seed-to-50°W reach” in the same sentence as the number. |
| B2 | The state reading explains the northern seed failure and links to NOAA's product page. | P3 | State passport | Retain the caveat beside the local intersection lengths. |
| B3 | The candidate retains six published-estimate ranks; the diagnosed reach is explicitly unranked. | P3 | Length table | Preserve separate quantities and tables. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| H1 | The map layer has a labeled checkbox and matching text in state and object views. | P3 | Atlas reading | Keep textual lengths and limitations when map styling changes. |
| H2 | Dotted styling and a separate legend label avoid relying on green color alone. | P3 | Map key | Verify contrast and non-color legibility at zoom. |
| H3 | A human screen reader and keyboard pass of the integrated state route is still open. | P2 | Atlas route | Complete it before public promotion. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| K1 | A trial interpolation error was caught before data admission; gridpoint and midpoint tests now guard the decoder. | P3 | Path test | Retain the focused independent numerical checks. |
| K2 | Five, 10, and 20 km integration steps agree to less than 1 km for the selected seed. | P3 | Sensitivity receipt | Keep step-size results with any reported reach. |
| K3 | The builder is offline and recomputes the path and state joins from pinned velocity bytes. | P3 | Release validator | Continue hashing source and code inputs in the manifest. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| L1 | The candidate and source queue identify open terms, and no DOI or final publication is claimed. | P3 | Release notes | Keep the candidate status until rights and release reconciliation pass. |
| L2 | Source citation, NOAA acknowledgment, and method limits are in the notices and methods. | P3 | Documentation | Preserve them in any eventual landing page. |
| L3 | The package remains in a modified, untracked worktree, without a frozen source commit. | P2 | Git and manifest | Review and freeze a source commit before deposition. |

## Synthesis

Roles reviewed: 7  
P1 blockers: 1 | P2 issues: 8 | P3 notes: 12  
Verdict: **NEEDS-WORK** for public dataset publication. The dated diagnostic
is suitable for candidate atlas inspection. CURRENT and BEACON agree that
the 2,277 km reach must stay outside whole-current ranks. SOUNDER and
LOGBOOK agree that attribution and source-specific reuse review precede
deposition.

Three amendments:

1. Resolve NOAA LSA source-specific reuse and citation terms for the packaged velocity subset.
2. Add multi-date and adjacent-seed diagnostics before claiming a stable Gulf Stream axis or permanent state passage.
3. Complete human accessibility review and release reconciliation from a reviewed source commit.

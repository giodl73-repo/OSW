---
skill: roles-check
topic: claim-level-literature-spine
date: 2026-08-28
source_commit: a93999f
roles_used: [CURRENT, SOUNDER, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
verdict: APPROVED
---

# Roles check: claim-level literature spine

## Artifact identification

- **Type:** systematic literature signal, claim-level citation UI, source-register correction, and regression test.
- **Reviewed:** the 15-source literature map, Research Note claims/literature sections, corrected source register, tests, and desktop render.
- **Scope:** private researcher preview; primary references support and constrain claims but do not constitute external peer review of OCEANLINES.

## Role selection

CURRENT checks physical and causal scope; SOUNDER checks dataset and literature identity; BEACON checks citation proximity and public interpretation; HARBOR checks accessible reading; KEEL checks executable guards; LOGBOOK checks attribution and repository truth. CHART and ORBIT are excluded because this delta changes neither map encoding nor planetary comparison.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | ACC-front citations pair persistent hydrographic structure with multiple jets, branching, bathymetric control, and direct eddy exchange. | P3 | Literature spine | Keep “regulates” and “leaky” together in public prose. |
| 2 | Drake closure is explicitly a model counterfactual and is paired with evidence against gateway-only paleoclimate causation. | P3 | Claims ledger | Continue rejecting a deterministic melt prediction. |
| 3 | The observing-system papers support the separation of surface temperature, full-depth storage, and section transport. | P3 | Claims and literature map | Require depth and velocity evidence before promoting any transport conclusion. |

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Fifteen sources have real titles, author fields, years, venues, claim mappings, positions, and findings. | P3 | Literature map | Preserve DOI-based identity if display citations are shortened. |
| 2 | The one metadata-recovery event is explicit: Crossref rate-limited the Thompson record and a university publication record supplied the full authors. | P3 | Recovery note | Retain the recovery note as provenance for the corrected cell. |
| 3 | OISST DOI and complete response checksums remain adjacent to the observational receipt rather than being replaced by literature citations. | P3 | Research receipt | Keep dataset citation and scientific-context citation distinct. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Decisive citations now sit inside the claims ledger, reducing the distance from statement to support and limitation. | P3 | Claims ledger | Preserve this adjacency in excerpts. |
| 2 | The eight-card literature spine explains what each paper carries rather than presenting a prestige list. | P3 | Literature spine | Keep cards limited to one support function each. |
| 3 | Contrary evidence is named as such and appears beside the Drake counterfactual, not buried after the supporting paper. | P3 | Claims and literature map | Maintain the paired presentation in email copy. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Literature roles are stated in text labels, headings, and prose; no claim position depends on color. | P3 | Literature cards | Preserve the labels if card colors change. |
| 2 | Direct DOI links have descriptive author-year text and remain keyboard accessible. | P3 | Claims and literature spine | Add article titles to accessible names only if citations become ambiguous. |
| 3 | The two-column literature grid collapses to one column at narrow widths while tables retain bounded horizontal scrolling. | P3 | Responsive CSS | Recheck at 200% zoom before public release. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The offline suite now has 26 passing tests and asserts the corrected primary-author labels. | P3 | `analysis/test_atlas.py` | Keep the stale-label negative assertions. |
| 2 | Tests require the literature heading and contrary citation in the rendered research note and resolve its local audit link. | P3 | Research-note test | Add DOI syntax validation if the register grows substantially. |
| 3 | Browser JavaScript syntax and the tall desktop research-page render pass without new runtime dependencies. | P3 | Validation | Keep literature content static and offline-capable. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Three inaccurate shorthand attributions were corrected: England, Hodel, and Rosevear now match the DOI metadata. | P3 | Source register O5/O7/O17 | Treat DOI metadata as authoritative for future display labels. |
| 2 | The systematic literature artifact records search claims, threshold, tiers, contrary evidence, recovery, and recommendation. | P3 | Literature signal | Version future refreshes instead of silently replacing this review. |
| 3 | No new public-release claim, recipient reference, private-project reference, or unlicensed asset enters the repository. | P3 | Boundary scan | Preserve private-preview status until publication is authorized. |

## Synthesis

```text
Roles reviewed: 6
P1 blockers: 0  |  P2 issues: 0  |  P3 notes: 18

Verdict: APPROVED

Top finding: The Drake claim now travels with both its idealized coupled-model support and the strongest constraint against gateway-only causation.
Cross-role consensus: The literature spine materially improves professional auditability because support, contrary evidence, exact attribution, and evidence boundary are co-located.
```

## Amendments applied

1. Corrected three source-register display attributions against DOI metadata and protected them with regression tests.
2. Added eight direct primary references to the researcher page, including observed exchange, regional barrier, measurement, counterfactual, and contrary roles.
3. Added a 15-source systematic literature map covering foundational, recent, contrary, and methodological tiers.

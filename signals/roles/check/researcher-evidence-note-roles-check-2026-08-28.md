---
skill: roles-check
topic: researcher-evidence-note
date: 2026-08-28
source_commit: c57e5a6
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
verdict: APPROVED
---

# Roles check: researcher-facing evidence note

## Artifact identification

- **Type:** researcher-facing HTML note and navigation delta.
- **Reviewed:** `research/`, README entry routes, Atlas navigation, Atlas method link, and structural tests.
- **Domain signals:** physical oceanography, climate-data provenance, scientific visualization, public explanation, accessibility, reproducibility, and repository status.
- **Scope:** private Atlas 08 preview, not a public release or external peer review.

## Role selection

CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, and LOGBOOK intersect the artifact. ORBIT is intentionally excluded: the note makes no Earth–gas-giant comparison and does not transfer a planetary mechanism.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Storage, transport, and anomaly are defined as distinct physical objects, including the section and velocity requirement for transport. | P3 | Question | Preserve this three-part contract in every future layer. |
| 2 | The current limit states that the preview does not diagnose a full-depth budget or validate the twelve footprints. | P3 | Question boundary | Replace the statement only when depth-resolved storage and section transports are implemented. |
| 3 | The Drake statement is explicitly classified as a model counterfactual and rejects a unique outcome or modern ice-loss forecast. | P3 | Claims ledger | Keep geometry, equilibration time, and feedbacks explicit in any expanded counterfactual. |

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Product, version, variable IDs, date, retrieval time, native resolution, display stride, shape, baseline, and DOI are visible in one reading path. | P3 | Reproduction receipt | Keep the receipt generated from artifact metadata when snapshots change. |
| 2 | Complete source-response SHA-256 values are shown and link to committed artifacts containing full NCSS queries and schemas. | P3 | Receipt table | Continue distinguishing response checksums from repository-file checksums. |
| 3 | The note declares missing/land preservation and separates native source resolution from the coarser display sample. | P3 | Reproduction receipt | Add quality-flag treatment when a product with flags is introduced. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The claims ledger labels product-mask geometry separately from circulation and explicitly rejects transport inference. | P3 | Claims ledger | Keep mask diagnostics visually and verbally distinct from current or front layers. |
| 2 | The note routes readers to the Atlas method for projection, scale, palette, and sampling details rather than duplicating partial map metadata. | P3 | Inspection routes | Retain the direct method route beside any future embedded figure. |
| 3 | Evidence classes are redundantly encoded by text labels and borders rather than color alone. | P3 | Claims ledger | Preserve the written class names if the palette changes. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The headline frames the map as a question-organizing instrument rather than a discovery claim. | P3 | Hero | Keep the invitational framing for private outreach. |
| 2 | Each claim is paired with a “does not establish” boundary in the same row, preventing caveats from becoming footnotes. | P3 | Claims ledger | Use this paired structure for all new headline findings. |
| 3 | The note creates a short route from question to current evidence, exact bytes, quantitative next work, and source inspection. | P3 | Page sequence | Resist adding literature narrative before the claims ledger. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Semantic header, main, article, sections, headings, tables, lists, navigation labels, and footer provide a coherent nonvisual outline. | P3 | Document structure | Preserve heading order as sections expand. |
| 2 | Tables have explicit headings and horizontal scroll containers, while evidence classes remain readable without hue. | P3 | Claims and receipts | Add captions if tables are detached from their section headings. |
| 3 | Focus indicators, responsive single-column routes, compact mobile navigation, and readable link text support keyboard and narrow-screen use. | P3 | Styles | Retest at 200% zoom before public release. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Automated tests require the note and stylesheet, verify decisive claims and exact checksums, and resolve every local route. | P3 | `analysis/test_atlas.py` | Add metadata-driven generation if receipt duplication becomes frequent. |
| 2 | The default suite remains offline and passed 25 tests; browser JavaScript syntax also passed. | P3 | Validation | Keep live-source refresh outside the default gate. |
| 3 | Desktop and narrow render paths were exercised without adding runtime dependencies or scripts to the note. | P3 | Browser rendering | Add a visual regression threshold only if the layout begins changing frequently. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The note calls itself a private review preview and does not imply that Atlas 08 is already the public release. | P3 | Status grid | Update this field only when remote publication actually changes. |
| 2 | Citation guidance names the project version, license, `CITATION.cff`, and the obligation to cite the underlying NOAA dataset separately. | P3 | Footer | Align the displayed version with `CITATION.cff` at release time. |
| 3 | No recipient identity, private-project reference, machine path, secret, or unsupported endorsement appears in the tracked artifact. | P3 | Public-boundary scan | Preserve neutral, reusable language in outreach packages. |

## Synthesis

```text
Roles reviewed: 7
P1 blockers: 0  |  P2 issues: 0  |  P3 notes: 21

Verdict: APPROVED

Top finding: A professional reader can now move from the organizing question to bounded claims and exact source receipts without reconstructing the scientific contract from multiple files.
Cross-role consensus: The note is appropriate for private researcher review because claim class, inferential boundary, provenance, and next measurement are co-located.
```

## Amendments applied

1. Added a four-row claims ledger that pairs every statement with evidence class and an explicit non-claim.
2. Added a complete OISST reproduction receipt with DOI, variable IDs, time, grid transformation, and full source-response checksums.
3. Added a quantitative path and direct inspection routes so the conceptual taxonomy leads to falsifiable measurements rather than ending at the graphic.


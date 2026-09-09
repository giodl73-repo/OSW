---
skill: roles-check
topic: atlas-08-preview-status
date: 2026-08-28
source_commit: f254971
roles_used: [CURRENT, SOUNDER, BEACON, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
verdict: APPROVED
---

# Roles check: Atlas 08 preview status

## Artifact identification

- **Type:** repository status contract, milestone record, publication checklist, and validation guard.
- **Reviewed:** `PREVIEW-STATUS.md`, root README status/milestones, publication checklist, citation-version boundary, and status regression test.
- **Scope:** truthfulness of the private Atlas 08 branch relative to the released Atlas 07.

## Role selection

CURRENT and SOUNDER check that evidence maturity is not overstated; BEACON checks public interpretation; KEEL checks executable status guards; LOGBOOK governs release and milestone truth. CHART, HARBOR, and ORBIT are excluded because this delta changes no map, interaction, or planetary claim.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The status file distinguishes the unchanged surface OISST layer from the new conceptual and researcher-presentation layers. | P3 | Evidence state | Preserve this distinction if Atlas 08 is promoted. |
| 2 | Missing depth-resolved heat content, section transport, bathymetric diagnostics, sea-ice coupling, and validated boundaries are enumerated. | P3 | Still not present | Remove items only when corresponding reviewed evidence exists. |
| 3 | Owner visual approval and the next quantitative layer remain explicit open decisions. | P3 | Decisions open | Do not convert presentation approval into physical validation. |

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The fixed 2026-08-01 OISST evidence date remains visible in the Atlas 08 milestone. | P3 | README milestones | Update only with a newly receipted snapshot. |
| 2 | Component reviews cite exact source commits, preventing a later artifact from silently inheriting an earlier verdict. | P3 | Reviewed components | Continue recording source and review commits separately. |
| 3 | Source refreshes are described as explicit network operations outside the default offline gate. | P3 | Validation state | Preserve the offline/live-source boundary. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Local readers are directed to Atlas 08 while the public URL is accurately labeled Atlas 07. | P3 | README entry and status | Keep both labels adjacent until promotion. |
| 2 | “Approved for private preview” avoids implying public release or external scientific validation. | P3 | Milestone verdict | Do not shorten the phrase to “approved” in excerpts. |
| 3 | The status file gives a concise current/not-present/open-decisions path for readers who do not need Git history. | P3 | Preview status | Link this page in any private handoff. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The status page lists the complete offline validation commands for tests, syntax checks, and table regeneration. | P3 | Validation state | Keep commands synchronized with CI if release gates expand. |
| 2 | The default suite passes 29 tests and asserts the public/private distinction plus both unchecked promotion decisions. | P3 | Status regression test | Retain negative/open-state assertions until owner action. |
| 3 | Regenerating research tables remains deterministic and does not change tracked output. | P3 | Offline validation | Continue checking generated diffs before packaging. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | README, milestone table, checklist, preview status, current branch, and `CITATION.cff` consistently distinguish public v0.8.0 Atlas 07 from private Atlas 08. | P3 | Repository-wide status | Change them together only after an authorized promotion decision. |
| 2 | Four reviewed Atlas 08 component commits and their review artifacts are explicitly mapped. | P3 | Reviewed components | Add later component reviews to this table rather than rewriting history. |
| 3 | The branch is recorded as unpushed, the public destination is unchanged, and no new release/version claim is made. | P3 | Preview status | Confirm remote state again immediately before any publication action. |

## Synthesis

```text
Roles reviewed: 5
P1 blockers: 0  |  P2 issues: 0  |  P3 notes: 15

Verdict: APPROVED

Top finding: A reader can now tell exactly which Atlas is public, which components of Atlas 08 were privately reviewed, what evidence is unchanged, and which decisions remain open.
Cross-role consensus: The repository status is truthful because presentation maturity, scientific evidence maturity, and publication state are recorded separately.
```

## Amendments applied

1. Replaced stale local “Explore Atlas 07” language with Atlas 08 preview wording while preserving the public Atlas 07 link and version.
2. Added a component-level preview status ledger with exact reviewed source commits and explicit missing scientific layers.
3. Added regression checks that keep owner approval and public-promotion decisions visibly open.

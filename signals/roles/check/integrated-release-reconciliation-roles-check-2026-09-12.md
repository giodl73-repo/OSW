---
skill: roles-check
topic: integrated-release-reconciliation
date: 2026-09-12
source_commit: b8c8369
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 2
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — Integrated release reconciliation

**Artifact type:** release-gate documentation and status reconciliation.  
**Reviewed:** `ROADMAP.md`, `PREVIEW-STATUS.md`, `PUBLICATION-CHECKLIST.md`,
the committed Event/Exchange/Atlas evidence-control contracts, and the focused
offline test result recorded on 2026-09-12.  
**Approval scope:** the truthfulness of the review-status and release-gate
records only. This is not approval of a public release, the RTOFS depth
candidates, or an oceanographic conclusion.

ORBIT is not selected: no planetary comparison is made by this artifact. The
seven selected roles cover physical limits, source custody, interface meaning,
accessibility, reproducibility, and repository status.

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The record keeps the frozen D13/D14 0–50 m screen separate from mutable-source deep candidates. | P3 | Preview status | Preserve the non-reproduction hold. |
| 2 | It names storage, horizontal motion, and surface forcing as screens rather than a closed budget. | P3 | Preview status | Keep causal and closure limits adjacent to any later results. |
| 3 | The release gate does not treat the 128-edge matrix as a validated zoning decision. | P3 | Integrated gate | Require multiyear, multiproperty support before changing borders. |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The documentation now identifies the changed RTOFS acquisition family as the reason candidate results are withheld. | P3 | Event depth/time | Retain the frozen-source checksum chain on promotion review. |
| 2 | The evidence filter is described as a classification interface, not a new scientific result. | P3 | Later integrated review work | Keep receipt routes available for every displayed class. |
| 3 | A reproducible 100 m/200 m comparison still lacks a reconciled source registration. | P2 | Integrated gate | Do not admit candidate values until a source can reproduce the frozen 0–50 m baseline or is explicitly versioned as a separate comparison family. |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Atlas's evidence filter is correctly limited to feature cards and shapes; it does not hide observed map modes. | P3 | Evidence-controls contract | Preserve separate observed-mode labels. |
| 2 | Province handoffs are described as routing, not province-wide measurement or boundary validation. | P3 | Preview status | Retain reference-geography wording in future interfaces. |
| 3 | Default projection remains an explicit owner decision. | P3 | Publication checklist | Do not infer it from the working Atlas 10 view. |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The new status text pairs the Event route with what its D1–D14 screens cannot establish. | P3 | Opening status | Keep this concise limitation in visitor-facing introductions. |
| 2 | The receipt ledger offers a direct route from claim type to supporting records. | P3 | Evidence controls | Preserve it in ordinary reading order. |
| 3 | “Integrated successor” could be mistaken for a decided replacement by a skimming reader. | P2 | Publication checklist heading | Keep the unchecked owner-approval and public-target gate immediately beneath the heading. |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The evidence vocabulary uses words and controls, not color alone. | P3 | Evidence-controls contract | Keep filter labels and match count text exposed. |
| 2 | The release gate explicitly includes keyboard, focus, URL, reduced-motion, and narrow-screen checks. | P3 | Integrated gate | Execute and record those browser checks before promotion. |
| 3 | No reviewed cross-browser result is attached to this release-gate record. | P3 | Integrated gate | Attach browser evidence to the eventual candidate rather than treating this documentation review as a substitute. |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Focused Event, Exchange, and evidence-control tests passed before this review. | P3 | Validation state | Retain those tests as a required route-level gate. |
| 2 | Refresh downloads remain outside the offline default test path. | P3 | Event depth/time | Keep retrieval explicit and checksummed. |
| 3 | A full clean-checkout validation must still be rerun for the exact release candidate. | P3 | Integrated gate | Record the command, commit, and result with the candidate. |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | README/public Atlas 07, citation metadata, and Pages are explicitly retained as separate from review work. | P3 | Required records | Change them only after owner authorization. |
| 2 | The prior Atlas 08–10 status is now joined to later Event, Exchange, and candidate-depth status. | P3 | Preview status | Update this record whenever a later review changes the admission state. |
| 3 | The untracked deep source and receipts are intentionally excluded from the release evidence chain. | P3 | Event depth/time | Preserve or archive them separately; do not commit them as canonical evidence without reconciliation. |

## Synthesis

```text
Roles reviewed: 7
P1 blockers: 0  |  P2 issues: 2  |  P3 notes: 19

Verdict: APPROVED-WITH-CONDITIONS
Top finding: The 100 m and 200 m RTOFS outputs remain candidates because the refreshed source does not reproduce the frozen 0–50 m result.
Cross-role consensus: Documentation accurately preserves review-versus-release separation, but no public promotion can follow until source custody, browser evidence, and owner decisions are complete.
```

## Amendments applied

1. Added the integrated release-gate checklist with explicit reconciliation, browser, asset-budget, RTOFS-candidate, and owner-approval controls.
2. Reconciled `PREVIEW-STATUS.md` and the roadmap with the later Event,
   Exchange, province-handoff, evidence-control, and depth-candidate work.
3. Retained a strict hold on mutable-source RTOFS depth candidates rather than
   treating their values as extensions of D13/D14.

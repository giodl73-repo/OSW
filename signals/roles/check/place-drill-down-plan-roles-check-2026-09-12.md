---
skill: roles-check
topic: place-drill-down-plan
date: 2026-09-12
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED
---

# Roles check — Place drill-down plan

**Artifact type:** cross-interface implementation specification  
**Artifact:** [`plans/place-drill-down.md`](../../../plans/place-drill-down.md)

ORBIT is not selected: this slice makes no planetary comparison. The seven
roles below cover its evidence, map, interface, validation, and release terms.

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Provinces remain reference geography, not containers. | P3 | Truth contract | Keep this boundary beside selection. |
| 2 | Exchange/event supports are incompatible. | P3 | Truth contract | Do not combine their results. |
| 3 | The SANT--SSTC pilot is bounded. | P3 | Interaction | Retain non-general wording. |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A copied support list could drift from destination records. | P2 | Implementation shape | Add a parity-tested declarative registry. |
| 2 | Classic 56 and footprint 54 differ. | P3 | Truth contract | Render edition/absence status. |
| 3 | No new aggregate is admitted. | P3 | Non-goals | Retain that constraint. |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Cards must not imply impermeable borders. | P3 | Atlas handoff | Keep reference-geography caveat visible. |
| 2 | Map selection remains the geographic context. | P3 | Interaction | Do not add a competing miniature map. |
| 3 | Missing footprints need text. | P3 | Truth contract | Preserve the V4 absence notice. |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Limits must travel with every continuation. | P3 | Atlas handoff | Keep availability text on cards. |
| 2 | General routes could look state-specific. | P3 | Interaction | Label them as general. |
| 3 | The plan offers a short source path. | P3 | Atlas handoff | Retain method/directory link. |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Selection changes require a textual announcement. | P3 | Accessible behavior | Use existing polite status. |
| 2 | Disabled cards need explanatory prose. | P3 | Interaction | Never make a dead button the only absence route. |
| 3 | Cards may change reflow. | P3 | Verification | Review at 390 CSS pixels. |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Existing Atlas URL updates replace history. | P2 | URL and history | Define push, replace, and popstate behavior. |
| 2 | Enabled links need offline resolution tests. | P3 | Verification | Test paths and allowed parameters. |
| 3 | The slice is offline by design. | P3 | Implementation shape | Keep it dependency-free. |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The slice must not imply promotion. | P3 | Acceptance gate | Retain the explicit no-promotion term. |
| 2 | The review itself needs versioning. | P3 | This artifact | Commit this record with implementation. |
| 3 | It authorizes no remote push. | P3 | Non-goals | Keep the boundary. |

## Synthesis

```text
Roles reviewed: 7
P1 blockers: 0  |  P2 issues: 2  |  P3 notes: 19

Verdict: APPROVED
Top finding: State availability must be tested against bounded destination records, not inferred from shared province names.
Cross-role consensus: A handoff must preserve evidence limits rather than turn selection into a universal state claim.
```

## Amendments applied

1. Added `atlas/state-handoffs.js` and required parity checks against Column,
   Exchange, and event admission records.
2. Defined push/replace/popstate behavior for the promised history contract.
3. Retained explicit unsupported-destination text and the 56/54 distinction.

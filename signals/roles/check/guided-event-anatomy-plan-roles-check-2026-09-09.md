---
skill: roles-check
topic: guided-event-anatomy-plan
date: 2026-09-09
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — Guided Event Anatomy plan

**Artifact type:** public-interface and evidence-composition specification

**Reviewed baseline:** `912d138c0822127c2f4ed13c79c3718f03c5766b`

ORBIT is not selected because this route makes no planetary comparison.

## Role selection

CURRENT reviews physical claims; SOUNDER reviews the D-series source contract;
CHART reviews the stable map frame; BEACON reviews the public narrative; HARBOR
reviews equivalent navigation and meaning; KEEL reviews offline failure gates;
LOGBOOK reviews public/repository status.

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “How heat accumulated and moved” presupposed a resolved mechanism. | P2 | Product question | Ask what each evidence screen reveals instead. **Resolved.** |
| 2 | The partial residual could be mistaken for a missing named process. | P2 | Evidence boundaries | Keep it explicitly unresolved and prohibit process relabeling. **Resolved.** |
| 3 | D12–D14 remain crossed-system or offline magnitude screens. | P3 | Scene table | Preserve those evidence classes beside every finding. **Accepted.** |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Read from JSON” did not freeze which values may become headlines. | P2 | Data contract | Add an explicit selector, unit, and meaning manifest. **Resolved.** |
| 2 | Schema identity must fail before any value is shown. | P2 | Loading | Validate expected schema per source and expose bounded failure. **Resolved.** |
| 3 | Seven admitted records are sufficient; NetCDF is unnecessary for this composition. | P3 | Loading | Keep the visitor payload narrow. **Accepted.** |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Stable frame” could crop or distort unlike SVG layouts. | P2 | Scene anatomy | Use a common containing stage without crop, stretch, or scale comparison. **Resolved.** |
| 2 | Evidence class needs redundant visual and textual encoding. | P2 | Visual grammar | Use words and marks, not palette alone. **Resolved.** |
| 3 | Reusing committed figures prevents an unreceipted redraw. | P3 | Visible result | Preserve each SVG's title, description, projection, and native composition. **Accepted.** |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Large enough to matter” was vague and invited causal interpretation. | P2 | Motion question | Ask how advection compares with the storage scale. **Resolved.** |
| 2 | Five scenes can sound like a closure sequence. | P2 | Evidence boundaries | Repeat that screens are not additive model terms or attribution. **Resolved.** |
| 3 | Question-led scenes give readers a memorable path through technical evidence. | P3 | Scene anatomy | Retain one question and one primary finding per scene. **Accepted.** |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Tabs cannot be the only no-script reading path. | P2 | Responsive contract | Keep all five static summaries in order until enhancement is active. **Resolved.** |
| 2 | Scene updates must not steal focus. | P2 | Route contract | Announce status politely and retain the initiating focus. **Resolved.** |
| 3 | A data-oriented text summary must add meaning beyond the SVG title. | P3 | Scene anatomy | Require finding, support, and limitation in page text. **Accepted.** |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Browser-only selectors would be hard to verify offline. | P2 | Implementation | Export pure schema, selector, URL, and formatting functions for Node tests. **Resolved.** |
| 2 | Missing sources and fields need negative fixtures. | P2 | Acceptance | Test invalid schema, file, field, and scene behavior. **Resolved.** |
| 3 | Existing committed receipts make exact regression checks possible. | P3 | Acceptance | Compare every displayed selector with source JSON. **Accepted.** |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | ROADMAP still names a review branch and pre-merge test count. | P2 | Repository status | Reconcile stale baseline language during closeout. **Resolved in plan.** |
| 2 | A merge must not silently promote Atlas 10 or replace Atlas 07. | P2 | Non-goals | Keep release status explicitly unchanged. **Resolved.** |
| 3 | The route should be discoverable without adding another README link corridor. | P3 | Route contract | Replace the top entry area with three primary entrances. **Accepted.** |

## Synthesis

```text
Roles reviewed: 7
P1 blockers: 0  |  P2 issues: 14  |  P3 notes: 7

Verdict: APPROVED-WITH-CONDITIONS
Top finding: The journey must present evidence screens, not imply a resolved heat mechanism or budget closure.
Cross-role consensus: Freeze the data selectors and keep evidence class plus limitation beside every scene.
```

All 14 P2 conditions have been incorporated into the implementation baseline.
Implementation may begin. Browser inspection, exact value checks, complete
offline validation, and a fresh native-role closeout remain required.

## Amendments

1. Reframed the product and motion questions to avoid presupposing causation.
2. Added the frozen scene-field manifest and cross-platform test seam.
3. Defined uncropped figure containment, progressive enhancement, and roadmap
   reconciliation without changing release status.

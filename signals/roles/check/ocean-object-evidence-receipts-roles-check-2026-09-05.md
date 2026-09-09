---
skill: roles-check
topic: ocean object evidence receipts
date: 2026-09-05
roles_used: 8
p1_count: 0
verdict: APPROVED
---

# Roles check — Ocean object evidence receipts

## Artifact

Guide 14, a four-example machine-readable receipt collection, deterministic
builder and tests, plus four additions to the ocean-object registry and six
qualified relations. Source commit:
`556edacd5c5b9ca0b1829e804ae05384635a730b`; reviewed artifact is the current
uncommitted working-tree snapshot. Full gate after final amendments:
`python -m pytest analysis -q` → 393 passed, 10 subtests passed. The expanded
110-object matrix was rendered in Edge at 1600 × 1200 and visually inspected.

All eight OSW roles apply: physical quantities (CURRENT), evidence provenance
(SOUNDER), representation semantics (CHART), public interpretation (BEACON),
equivalent access (HARBOR), deterministic contracts (KEEL), repository truth
(LOGBOOK), and transfer beyond Earth (ORBIT).

## Review findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The registry lacked volume transport, heat transport, heat content, and ocean surface heat flux despite OSW computing or discussing each. | P2 | Registry | **Resolved:** added OBJ107–OBJ110 within the existing flux/budget type. |
| 2 | Surface flux, section transport, convergence, storage tendency, and inventory remain distinct quantities. | P3 | OER003/OER004 | Preserve explicit non-claims in every budget receipt. |
| 3 | The heat-transport receipt declares reference temperatures instead of implying an absolute heat flow independent of convention. | P3 | OER003 | Retain convention sensitivity beside values. |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A single “measured flux” label conflated source origin with claim stage. | P2 | Guide index | **Resolved:** separated origin, claim stage, and identity-test outcome. |
| 2 | Exact transformed-artifact hashes and upstream-response hashes could be confused. | P2 | Source blocks | **Resolved:** named both separately and omit upstream hash when not present. |
| 3 | Each example records variable, units, vertical support, time, spatial support, baseline/sign, and source schema. | P3 | Measurements | Preserve these minimum dimensions. |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Representation class is independent of object type and scientific status. | P3 | Receipt axes | Expose all three in future atlas tooltips. |
| 2 | Raster appearance is correctly denied as sufficient evidence for heatwave, water mass, content, or transport. | P3 | OER001/OER002 | Keep non-claims adjacent to each layer. |
| 3 | The expanded Flux/Budget count remains legible in the matrix with no overlap or clipping. | P3 | Matrix visual check | Preserve visual regression inspection after registry growth. |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “What did this dataset earn?” gives readers a concrete question stronger than generic provenance language. | P3 | Guide title/rule | Use as the tooltip entry point. |
| 2 | `not_tested` avoids calling valid evidence a failure merely because a different identity test was never attempted. | P3 | Worked receipts | Explain this distinction wherever the status appears. |
| 3 | Each earned claim sits beside a short list of tempting but unsupported claims. | P3 | Four examples | Preserve this paired wording. |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The guide and JSON expose all meaning without colour, interaction, or pointer position. | P3 | Whole artifact | Retain text as the canonical equivalent. |
| 2 | Receipt status is expressed in words rather than icons alone. | P3 | JSON / tables | Use the same words in future visual badges. |
| 3 | Structured `supports`, `does_not_support`, and `next_evidence` fields provide a data-oriented alternative. | P3 | Receipt schema | Keep them mandatory. |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | `evidence_status` was used but initially absent from the governed vocabulary. | P2 | Schema vocabulary | **Resolved:** added and validate the status vocabulary. |
| 2 | Builds are byte-deterministic and source artifact hashes are recomputed in tests. | P3 | Builder/tests | Keep source refresh outside the default suite. |
| 3 | Registry IDs, names, identity tests, receipt links, and pass results are cross-validated offline. | P3 | Contract tests | Preserve as the merge gate. |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Current README, classification, guide index, history, matrix, and tests agree on 110 objects and 107 relations. | P3 | Companion files | Continue synchronized count updates. |
| 2 | The history explains why four terms were added rather than celebrating a round number. | P3 | History | Preserve the gap-driven record. |
| 3 | The receipt vocabulary is called a worked OSW contract, not a community standard. | P3 | Guide boundary | Keep version `v1` and the adoption boundary visible. |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Planetary receipts must name radiance or retrieval rather than silently asserting deep atmospheric heat. | P3 | Planetary boundary | Require the actual remote observable. |
| 2 | A visible planetary band can remain a field or candidate without becoming a jet or material body. | P3 | Planetary boundary | Apply the same identity-test outcome axis. |
| 3 | No Earth heat reference, depth convention, or material boundary is automatically transferred. | P3 | Cross-world use | Pair every analogy with its non-analogy. |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0 | P2 issues: 4 (all resolved) | P3 notes: 20
Verdict: APPROVED
Top finding: evidence origin, claim stage, and identity-test outcome must remain separate.
Cross-role consensus: a valid field or integral earns only its declared claim;
unsupported neighboring nouns belong inside the receipt, not in fine print.
```

## Amendments applied

1. Added four missing heat/transport quantities and six relations to the live registry.
2. Replaced the coarse “measured flux” label with independent receipt axes.
3. Distinguished transformed-artifact checksum from upstream-response checksum.
4. Governed and validated the `evidence_status` vocabulary.

Remaining non-blocking work: display these receipts in atlas layer tooltips and
add a first true detected-object receipt from a continuous event or feature
detection pipeline.

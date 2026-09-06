---
skill: roles-check
topic: ocean object visual matrix and naming guide
date: 2026-09-05
roles_used: 8
p1_count: 0
verdict: APPROVED
---

# Roles check — Ocean object visual matrix

## Artifact

Generated SVG matrix, stable JSON summary, generator, tests, and Guide 13 for
choosing among 110 editorial terms in 13 primary types. Source commit:
`556edacd5c5b9ca0b1829e804ae05384635a730b`; reviewed artifact is the current
uncommitted working-tree snapshot. Full gate: `python -m pytest analysis -q` →
391 passed, 10 subtests passed. The SVG was also rendered in Edge at 1600 ×
1200 and inspected for overlap, clipping, hierarchy, and legibility.

All eight OSW roles apply: physical identity (CURRENT), measurement provenance
(SOUNDER), visual semantics (CHART), public explanation (BEACON), accessibility
(HARBOR), generated-artifact contracts (KEEL), repository truth (LOGBOOK), and
planetary transfer (ORBIT).

## Review findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The five-step ladder keeps a measured field from automatically becoming a body, event, pool, or transport. | P3 | Evidence ladder | Preserve the progression without implying every study uses every step. |
| 2 | Primary types are explicitly non-exclusive, allowing fronts, currents, bodies, and budgets to relate without collapsing identity. | P3 | Guide / type cards | Keep relations in the separate graph. |
| 3 | The matrix reports editorial coverage, not a natural hierarchy or exhaustive ocean partition. | P3 | Header / footer | Repeat this warning wherever the figure is embedded. |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The decision path begins with measurand and observation method rather than image colour. | P3 | Start with the measurand | Retain as the first diagnostic. |
| 2 | Worked examples distinguish property, thresholded event, volume integral, and velocity-weighted flux. | P3 | Worked examples | Add real data receipts as future companions. |
| 3 | JSON counts and identity tests are derived from the registry rather than copied into prose. | P3 | Generated summary | Keep the CSV as the authoritative source. |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Thirteen equal-area cards initially risked becoming thirteen cramped columns. | P2 | Type overview | **Resolved:** arranged as a 7 + 6 equal-card grid. |
| 2 | Long matrix headings initially clipped and confused the type correspondence. | P2 | Matrix header | **Resolved:** use explicit compact codes with full names in cards and text alternative. |
| 3 | The sparse dot field reveals discriminating tests without implying abundance or geography. | P3 | Identity matrix | Preserve direct row and column labels. |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Begin with what was measured. Earn the noun afterward.” is memorable and supported by the workflow. | P3 | Guide opening | Use as the public-facing rule. |
| 2 | Four familiar ambiguous marks—orange, green, white, and an arrow—make the grammar concrete. | P3 | Worked examples | Keep examples beside their required evidence. |
| 3 | The guide answers a practical question rather than presenting the registry as a vocabulary dump. | P3 | Whole guide | Link it as the entry point for new readers. |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Secondary SVG text initially fell below the project's 14-pixel readability floor. | P2 | Cards / rows / footer | **Resolved:** raised all informational text to at least 14 pixels. |
| 2 | Colour is redundant with labels, position, counts, and dot coordinates; meaning survives grayscale. | P3 | Whole SVG | Preserve redundant encoding. |
| 3 | The SVG has a concise description and semantic groups, while Guide 13 supplies the complete text alternative. | P3 | SVG metadata / guide | Keep the guide link in the footer. |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | An initial test expected 25 identity tests although the registry contains 24. | P2 | Matrix contract | **Resolved:** corrected the assertion to the source-derived count. |
| 2 | Temporary builds are byte-equal to committed SVG and JSON outputs. | P3 | Determinism test | Retain deterministic sorting and formatting. |
| 3 | The generator uses the Python standard library and rejects duplicate IDs, names, and unknown types. | P3 | Generator | Keep validation ahead of rendering. |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | README, guide index, history, registry, and generated counts agree on 110 objects and 13 types. | P3 | Companion files | Update these surfaces together. |
| 2 | The history records synthesis, not priority or discovery of a natural taxonomy. | P3 | History | Preserve the editorial wording. |
| 3 | The review names an uncommitted snapshot and makes no release claim. | P3 | Artifact | Commit or publish only when authorized. |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Visual resemblance between ocean and planetary bands is denied as sufficient evidence for shared object identity. | P3 | Crossing to another world | Preserve the mechanism-first test. |
| 2 | Forcing, stratification, rotation, depth, compressibility, boundaries, and sampling method are named transfer checks. | P3 | Crossing to another world | Use them before exporting Earth terms. |
| 3 | Guide 07 remains the detailed planetary comparison rather than overloading this decision aid. | P3 | Cross-link | Maintain one canonical treatment. |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0 | P2 issues: 4 (all resolved) | P3 notes: 20
Verdict: APPROVED
Top finding: begin with the measurand; earn the ocean-object noun afterward.
Cross-role consensus: type, scientific status, and visual representation are
separate axes, and registry coverage is not natural prevalence or geography.
```

## Amendments applied

1. Replaced a thirteen-column overview with a 7 + 6 equal-card grid.
2. Replaced clipped matrix headings with stable, explicit compact codes.
3. Raised secondary SVG text to a 14-pixel minimum and visually inspected it.
4. Corrected the identity-test contract from 25 to the registry's 24.
5. Added a mechanism-first planetary-transfer boundary to Guide 13.

Remaining non-blocking work: connect the decision guide to interactive atlas
tooltips and add worked data receipts for selected real observations.

---
skill: roles-check
topic: marine heatwave temporal-gap identity bakeoff
date: 2026-09-06
roles_used: 8
p1_count: 0
verdict: APPROVED
---

# Roles check — OSW-D4 gap-identity bakeoff

## Artifact

OSW-D4's policy-sensitivity JSON, OER008, acquisition and overlap analysis,
contract tests, documentation, and four-panel identity-bakeoff SVG. Reviewed as
the current uncommitted working-tree snapshot. Final gate:
`python -m pytest analysis -q` → **424 passed, 10 subtests passed**. The SVG was
rendered in Edge at 1200 × 760 and visually inspected.

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Reappearing threshold cells do not prove returning water parcels. | P2 | Public wording | **Resolved:** say grid locations “reactivate” and deny material continuity. |
| 2 | The one-day rule defines event identity; it does not fill the missing thermal observation. | P2 | Policy bakeoff | **Resolved:** retain both split and join outcomes and state zero August 11 inheritance. |
| 3 | Exact geographic overlap requires no current, transport, or causal explanation. | P3 | Bridge metric | Preserve zero-dilation as geometry only. |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The bridge must use the same checksum-pinned NOAA fields as the prior receipts. | P3 | Source artifacts | All source, point, and lineage hashes are recomputed offline. |
| 2 | The independently seeded post-gap run must itself satisfy duration. | P2 | Qualified runs | **Resolved:** verify the exact seven-day August 12–18 lineage. |
| 3 | Absence on the gap day must remain explicit. | P3 | Gap receipt | Record zero of 145 prior pixels active on August 11. |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Before, gap, after, and overlap require identical frames. | P3 | Four panels | All use one local equirectangular extent and standard parallel. |
| 2 | The first draft lacked geographic scale. | P2 | Map furniture | **Resolved:** add a 100 km scale and projection statement. |
| 3 | The gap should not look like missing data. | P3 | August 11 panel | Use a hatched ghost footprint plus “0 / 145 active,” not a blank panel. |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Temporal, not spatial” is supported because surrounding shapes overlap exactly. | P3 | Headline | Retain with the one-day threshold caveat immediately visible. |
| 2 | Readers need both answers, not a forced verdict. | P2 | Result boxes | **Resolved:** show SPLIT and JOIN as policy-conditioned results. |
| 3 | `policy_dependent` is clearer than treating ambiguity as failure. | P3 | Receipt vocabulary | Retain as a governed identity outcome. |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Overlap cannot depend on color mixing alone. | P2 | Overlay | **Resolved:** crosshatch the 122 shared grid locations and state the count. |
| 2 | Policy outcomes need words and contrast beyond red/blue tint. | P3 | Result boxes | SPLIT/JOIN headings and full reasons provide redundant encoding. |
| 3 | The SVG description must carry the full conclusion. | P3 | Accessible text | Description states exact overlap, missing day, and divergent policy results. |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Overlap fractions need separate denominators. | P3 | Bridge metrics | Test IoU, prior-retained, and post-inherited fractions independently. |
| 2 | The committed result requires an offline checksum and policy contract. | P2 | Tests | **Resolved:** validate all three sources, exact metrics, policy booleans, and duration. |
| 3 | Live NOAA refresh remains outside the default suite. | P3 | Acquisition | Preserve explicit network generation and offline artifact validation. |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Identity sensitivity is a claim stage, not a new ocean-object term. | P3 | Schema | Registry remains 110 objects; receipt vocabulary gains the new stage. |
| 2 | Eight-receipt counts and terminology must agree everywhere. | P2 | Repository surfaces | **Resolved:** synchronize README, guide, history, builder, analysis docs, and signal. |
| 3 | No remote publication occurred. | P3 | State | Continue describing this as local, uncommitted work. |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A missing observation day in cloud tracking poses the same identity choice. | P3 | Transfer | Transfer the policy grammar, not Earth's one-day value. |
| 2 | Image overlap does not establish conserved atmospheric material. | P3 | Analogy | Preserve the grid-location versus parcel distinction. |
| 3 | Cadence and resolution control apparent gaps. | P3 | Falsification | Re-run the bakeoff under target instrument sampling before naming one object. |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0 | P2 issues: 10 (all resolved) | P3 notes: 14
Verdict: APPROVED
Top finding: the only assumption needed to reconnect these footprints is permission to cross one threshold-inactive day.
Cross-role consensus: shared grid locations support spatial continuity, not material continuity.
```

## Amendments applied

1. Replaced parcel-suggestive “return” language with exact grid-location
   reactivation throughout the visual and documentation.
2. Added the scale, hatched gap/overlap encodings, and explicit SPLIT/JOIN
   policy panels.
3. Added `identity_sensitivity` and `policy_dependent` to the receipt grammar,
   OER008, source-chain contracts, and synchronized repository documentation.

Remaining non-blocking work: test minimum-overlap thresholds and eight-neighbor
connectivity, then study whether atmospheric forcing or ocean advection better
explains the observed disappearance and reactivation.

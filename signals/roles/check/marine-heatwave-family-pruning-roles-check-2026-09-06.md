---
skill: roles-check
topic: marine heatwave family pruning
date: 2026-09-06
roles_used: 8
p1_count: 0
verdict: APPROVED
---

# Roles check — OSW-D8 family pruning

## Artifact

OSW-D8's six-cutoff area-pruning JSON, OER012, generators, tests,
documentation, and scale-ladder SVG. Reviewed as the current uncommitted
working-tree snapshot. Final offline gate: python -m pytest analysis -q →
**439 passed, 10 subtests passed**. The SVG was rendered in Edge at 1200 × 800
and visually inspected.

## Role selection

All eight OSW roles apply because the artifact converts a graph-visualization
choice into a measurable scientific identity sensitivity with public wording,
provenance, accessibility, testing, and planetary-transfer implications.

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Removing a small threshold component does not show that it is physically false or unimportant. | P2 | Interpretation | **Resolved:** state this directly in the plate, receipt, and guide. |
| 2 | Area pruning tests representation, not mechanism. | P3 | Boundary | Keep forcing, advection, and impacts separate. |
| 3 | The primary trunk's stability is empirical only across this declared ladder. | P3 | Finding | Retain product-, grid-, event-, and cutoff-specific scope. |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | D8 must remain byte-linked to the exact D7 graph it prunes. | P2 | Source artifact | **Resolved:** store and test the D7 SHA-256. |
| 2 | A pixel-count cutoff would silently depend on latitude and grid resolution. | P2 | Threshold variable | **Resolved:** use spherical component area in km². |
| 3 | Cutoffs are post hoc diagnostic values, not calibrated standards. | P3 | Method | Preserve the explicit illustrative-threshold statement. |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Every scale” overstated six tested area cutoffs. | P2 | Headline | **Resolved:** say “every tested cutoff.” |
| 2 | Each card prints side, split, merge, and trunk counts independently of color. | P3 | Scale ladder | Preserve redundant labels. |
| 3 | This is a topology-sensitivity diagram rather than a geographic map. | P3 | Visual form | Map projection and scale bar are not applicable; retain spatial source metadata. |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The public summary must separate stable trunk from unstable family topology. | P2 | Main claim | **Resolved:** place both clauses in the title and conclusion. |
| 2 | “Pruned” can sound like “debunked.” | P2 | Public explanation | **Resolved:** explain that small does not mean false. |
| 3 | Concrete removal steps make the abstract sensitivity understandable. | P3 | Explanation cards | Retain component areas and topology changes. |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Branch loss cannot rely on the fading orange palette. | P2 | Cards | **Resolved:** print thresholds and all counts in every card. |
| 2 | Singular split/merge grammar must read correctly. | P3 | Cards | Corrected one split and one merge labels. |
| 3 | The SVG description provides the entire six-step result. | P3 | Alternative text | Preserve the textual ladder. |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Pruning can strand eligible nodes outside the anchor's family. | P2 | Algorithm | **Resolved:** recompute weak reachability after node and edge removal. |
| 2 | Tests must lock topology at every threshold, not merely the trunk count. | P2 | Contract tests | **Resolved:** assert side counts, split counts, and merge counts across all six cutoffs. |
| 3 | D8 is derived fully offline from D7. | P3 | Reproducibility | Preserve this separation from live NOAA refresh. |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | OER012 adds identity depth, not a new ocean-object term. | P3 | Registry | Keep 110 objects separate from twelve receipts. |
| 2 | Twelve-receipt counts and D8 links must agree across entry points. | P2 | Documentation | **Resolved:** synchronize README, Guide 14, history, analysis docs, and receipt collection. |
| 3 | No remote release occurred. | P3 | Repository state | Keep this stage local and uncommitted. |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Apparent cloud branches are likewise resolution- and area-threshold-dependent. | P3 | Transfer | Transfer the sensitivity method, not Earth's cutoffs. |
| 2 | Planetary pixel area may vary strongly across the image. | P3 | Geometry | Use physical projected area, not raw pixel count. |
| 3 | Feature pruning cannot establish atmospheric mechanism. | P3 | Analogy boundary | Preserve the causal limit. |

## Synthesis

Roles reviewed: 8  
P1 blockers: 0 | P2 issues: 10 (all resolved) | P3 notes: 14  
Verdict: APPROVED  
Top finding: the 21-node trunk survives all six tested area cutoffs, while every split/merge count is scale-conditioned.  
Cross-role consensus: minimum area is an explicit representation contract, not a truth test for small fluid features.

## Amendments applied

1. Replaced the universal-sounding headline with “every tested cutoff” and
   retained product-, grid-, and event-specific boundaries.
2. Used physical area, recomputed anchor reachability after pruning, and exposed
   every topology step without relying on color.
3. Locked the full ladder in offline tests and synchronized OER012 and the
   twelve-receipt documentation.

Remaining non-blocking work: add the August 11 gap as a separately typed
temporal bridge, then investigate physical drivers without interpreting graph
or pruning topology as causation.

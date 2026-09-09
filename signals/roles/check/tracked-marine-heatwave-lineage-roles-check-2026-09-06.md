---
skill: roles-check
topic: tracked marine heatwave footprint lineage
date: 2026-09-06
roles_used: 8
p1_count: 0
verdict: APPROVED
---

# Roles check — OSW-D3 tracked footprint lineage

## Artifact

OSW-D3's 21-day primary-overlap lineage, OER007, tracking code and contract
tests, Guide 14 additions, history and analysis documentation, and the
six-frame lineage plate. The reviewed artifact is the current uncommitted
working-tree snapshot. All eight OSW roles apply because this is simultaneously
a physical-ocean interpretation, derived-data lineage, map, public claim,
accessible SVG, reproducible pipeline, repository milestone, and potential
planetary analogy substrate.
Final gate: `python -m pytest analysis -q` → **419 passed, 10 subtests passed**.
The final SVG was rendered in Edge at 1200 × 820 and visually inspected.

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Exact footprint overlap tracks a threshold state, not materially advected water. | P2 | Claim boundary | **Resolved:** deny parcel motion and heat transport in JSON, guide, and plate. |
| 2 | The 450 km centroid path is geometric displacement, not current speed or heat delivery. | P2 | Summary metric | **Resolved:** label it centroid path and make no velocity or mechanism claim. |
| 3 | The point event and spatial lineage legitimately end on different dates. | P3 | OER005/OER007 | Preserve the discrepancy as a result rather than forcing agreement. |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Every daily field must remain tied to the 32 checksum-pinned NOAA files. | P3 | Source chain | SHA-256 verification occurs before tracking; OER007 pins source and seed artifacts. |
| 2 | A stopped lineage needs evidence for the failed transition, not only its last successful day. | P2 | Lineage limits | **Resolved:** record July 20 and August 11 zero-inheritance stop receipts and reasons. |
| 3 | NOAA CRW categories remain a derived observation product. | P3 | Provenance | Preserve the origin class and CoralTemp baseline rather than relabeling as raw SST. |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Shape comparison requires identical frames. | P3 | Six snapshots | All panels use one geographic extent and local equirectangular standard parallel. |
| 2 | The initial plate omitted projection and scale. | P2 | Map furniture | **Resolved:** add projection wording, 41.55°N standard parallel, and a 100 km scale. |
| 3 | The collapse must remain visible without rescaling each panel. | P3 | Snapshot sequence | Retain common frames and paired area labels. |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “The shape has a life of its own” could imply material persistence. | P2 | Headline | **Resolved:** subtitle, footer, and guide immediately define exact-pixel threshold-state inheritance. |
| 2 | The memorable finding is the August 11 disagreement between point and footprint identity. | P3 | Callout | Keep the break prominent and explain why reconnection would be a method choice. |
| 3 | Branch ambiguity belongs in the primary reading path. | P2 | Metrics | **Resolved:** display five ambiguous steps beside the weakest IoU. |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Moderate and strong categories initially depended on color. | P2 | Palette | **Resolved:** add diagonal texture to strong pixels and label both legend classes. |
| 2 | The map's central evolution must be recoverable as text. | P3 | SVG description | Title/description and Guide 14 report duration, growth, collapse, displacement, ambiguity, and break. |
| 3 | Six panels follow chronological reading order without interaction. | P3 | Layout | Retain static small multiples as the canonical accessible overview. |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Live downloads cannot be part of the default offline gate. | P3 | Acquisition | Tracking refresh stays explicit; committed metrics are validated offline. |
| 2 | A source or seed change must invalidate the lineage. | P2 | Contract test | **Resolved:** recompute both artifact hashes and assert exact dates, metrics, counts, and limit receipts. |
| 3 | Split selection needs deterministic tie-breaking. | P3 | Tracker | Greatest intersection, then IoU, then native-grid cell order is deterministic and unit-tested. |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Tracked-object is a new evidence stage, not a new taxonomy term. | P3 | Receipt vocabulary | Add `tracked_object` while keeping the registry at 110 objects. |
| 2 | README, guide, history, source signal, and receipt collection must agree. | P2 | Repository surfaces | **Resolved:** all now describe seven receipts and the 21-day lineage. |
| 3 | Remote/release reality remains unchanged. | P3 | Git state | Do not imply commit, push, or publication; this snapshot remains local and uncommitted. |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Threshold-component tracking can transfer across planets only at the method level. | P3 | Analogy boundary | Require a governed observable and threshold in the target atmosphere. |
| 2 | Cloud-feature overlap would not prove materially conserved gas. | P3 | Material identity | Preserve the same threshold-state versus parcel distinction. |
| 3 | Earth connectivity, grid scale, and daily cadence are not universal. | P3 | Transfer conditions | Re-test adjacency, cadence, and persistence under target resolution and dynamics. |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0 | P2 issues: 10 (all resolved) | P3 notes: 14
Verdict: APPROVED
Top finding: the 21-day footprint lineage and 27-day point event are both valid, but they are different identities.
Cross-role consensus: exact overlap is reproducible, not uniquely inevitable or materially Lagrangian.
```

## Amendments applied

1. Added explicit preceding/following failed-transition receipts and offline
   checksum/metric contract tests.
2. Added projection, standard parallel, scale, category legend, textured strong
   pixels, weakest IoU, and branch-ambiguity count to the plate.
3. Added the tracked-object evidence stage and synchronized OER007 across the
   receipt builder, Guide 14, README, history, analysis documentation, and
   research signal.

Remaining non-blocking work: seed and track the post-gap component, then run
connectivity, overlap-threshold, gap-bridging, split, and merge sensitivities
before deciding whether two lineages should ever share one public name.

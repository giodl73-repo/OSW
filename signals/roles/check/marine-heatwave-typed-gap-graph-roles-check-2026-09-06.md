---
skill: roles-check
topic: marine heatwave typed gap graph
date: 2026-09-06
roles_used: 8
p1_count: 0
verdict: APPROVED
---

# Roles check — OSW-D9 typed temporal edge

## Artifact

OSW-D9's multi-edge-type graph JSON, OER013, generators, tests,
documentation, and strict-versus-conditional SVG. Reviewed as the current
uncommitted working-tree snapshot. Final offline gate:
python -m pytest analysis -q → **443 passed, 10 subtests passed**. The SVG was
rendered in Edge at 1200 × 800 and visually inspected.

## Role selection

All eight OSW roles apply because the artifact encodes an event-identity policy
inside an observation-derived graph and exposes it through a public visual with
reproducibility and planetary-transfer implications.

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Exact endpoint overlap across an inactive day is not material or dynamical continuity. | P2 | Bridge meaning | **Resolved:** label the edge as policy-conditioned and deny parcel/mechanism claims. |
| 2 | Zero inherited activity is scoped to the August 10 footprint, not the whole ocean. | P3 | Gap metric | Preserve the explicit metric name. |
| 3 | Driver attribution remains a separate experiment. | P3 | Next evidence | Do not infer atmospheric or advective cause from the bridge. |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The composite must remain tied to exact D7, D4, and D3 artifacts. | P2 | Provenance | **Resolved:** store and test all three hashes. |
| 2 | August 11 is observed threshold inactivity, not missing source data. | P2 | Terminology | **Resolved:** replace “missing day” with “threshold-inactive day.” |
| 3 | Post-gap nodes carry coordinate-set hashes and original summaries. | P3 | Node identity | Preserve the deterministic derivation. |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A conditional bridge must never look like an ordinary daily edge. | P2 | Visual grammar | **Resolved:** solid daily edges, dashed bridge, and hatched inactive date. |
| 2 | The D7 branch marks summarize split dates rather than redraw all nodes. | P3 | Pre-gap label | State this directly below the graph. |
| 3 | Dates and policy outcomes share one left-to-right axis. | P3 | Timeline | Preserve the common geometry. |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Readers need both legitimate answers instead of a forced join. | P2 | Result cards | **Resolved:** retain STOP and CONTINUE with graph counts. |
| 2 | “Missing” could be repeated as data absence. | P2 | Lead/footer | **Resolved:** use threshold-inactive and active-threshold-evidence language. |
| 3 | The one-sentence takeaway is that the edge type carries the convention. | P3 | Headline | Retain “A gap edge is not a daily edge.” |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Edge meaning cannot rely on color or dash perception alone. | P2 | Legend and cards | **Resolved:** print solid/dashed definitions and both policy outcomes. |
| 2 | Hatching distinguishes the inactive date from background. | P3 | Gap band | Preserve the redundant label. |
| 3 | The SVG description states counts, dates, and zero gap-day inheritance. | P3 | Alternative text | Keep the complete nonvisual conclusion. |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The six post-gap edges must be proven ordinary one-day exact-overlap edges. | P2 | Contract tests | **Resolved:** assert type, elapsed days, inactive days, and positive overlap. |
| 2 | The bridge must lock two elapsed days, one inactive day, 122 cells, and zero dilation. | P2 | Bridge contract | **Resolved:** test every field offline. |
| 3 | D9 is derived entirely from committed receipts. | P3 | Reproducibility | Keep live NOAA access outside this stage. |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | OER013 adds an edge vocabulary, not a new natural-object term. | P3 | Registry | Keep 110 objects separate from thirteen receipts. |
| 2 | Thirteen-receipt counts and D9 links must agree across entry points. | P2 | Documentation | **Resolved:** synchronize README, Guide 14, history, analysis docs, and receipt collection. |
| 3 | No remote publication occurred. | P3 | Repository state | Keep the work local and uncommitted. |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A cloud feature can also reappear across an inactive or unobserved interval. | P3 | Transfer | Distinguish inactive measurement from missing cadence before bridging. |
| 2 | Endpoint image overlap does not conserve atmospheric material. | P3 | Analogy boundary | Transfer the typed-edge grammar only. |
| 3 | Instrument cadence controls the number of elapsed and inactive steps. | P3 | Falsification | Re-run under target sampling. |

## Synthesis

Roles reviewed: 8  
P1 blockers: 0 | P2 issues: 10 (all resolved) | P3 notes: 14  
Verdict: APPROVED  
Top finding: one explicitly typed edge can conditionally extend the graph without erasing the observed threshold-inactive day.  
Cross-role consensus: edge semantics are scientific metadata; dash style alone is insufficient.

## Amendments applied

1. Replaced missing-day language with observed threshold inactivity and retained
   the zero-inheritance metric.
2. Made daily and conditional edges structurally, visually, and textually
   distinct while exposing both STOP and CONTINUE outcomes.
3. Locked all source hashes, bridge fields, and six post-gap daily edges, then
   synchronized OER013 and the thirteen-receipt documentation.

Remaining non-blocking work: build a complete post-gap branch family if the
extra topology is decision-relevant, then compare physical drivers around
August 7–12 without treating the graph bridge as causal evidence.

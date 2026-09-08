---
skill: roles-check
topic: central-roadmap
date: 2026-09-06
roles_used: 7
p1_count: 0
verdict: APPROVED
---

# Roles check — OSW central roadmap

**Artifact type:** product and research roadmap, site-delivery proposal, and
governance/adoption status

**Source commit:** `6285bdd3b74b8924f006e8f8e4582d2673564c95` plus reviewed working-tree changes

**Reviewed artifacts:** `ROADMAP.md` and its two `README.md` entry links

## Role selection

CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, and LOGBOOK were selected
because the roadmap sequences scientific claims, data custody, cartography,
public explanation, accessibility, verification, and release state. ORBIT was
not selected because the roadmap introduces no new planetary comparison or
transfer claim.

## Review findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Surface forcing, storage, horizontal advection, missing processes, and closure are kept distinct. | P3 | Operating rules / Current baseline | Preserve this separation in the guided story. **Accepted.** |
| 2 | The first draft named deeper tests but did not make the missing-term archive audit equally explicit. | P2 | Science track | Require a native tracer/vertical/mixing/assimilation availability audit and prohibit proxy inflation. **Resolved.** |
| 3 | Zoning follows transport tests instead of treating a visually satisfying partition as physical evidence. | P3 | Zoning track | Retain the merge/split/move/demote outcomes. **Accepted.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | D1-D14 study-stage labels can be confused with the source register's D38-D51 IDs. | P2 | Motion and heat evidence | State both namespaces and their relationship. **Resolved.** |
| 2 | The crossed GFS/RTOFS lineage and partial-budget status remain visible. | P3 | Motion and heat evidence | Keep product crossing beside every integrated view. **Accepted.** |
| 3 | Scene-level provenance could disappear behind the guided narrative. | P2 | Recommended next slice | Require depth/time/support and direct JSON receipt access in every scene. **Resolved.** |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Oceanic Mollweide is identified as the strongest present overview without promoting experimental projections to measured geography. | P3 | Atlas vocabulary | Preserve explicit projection identity and experiment status. **Accepted.** |
| 2 | A stable map frame is useful only if local event views still expose projection, extent, and support. | P3 | Recommended next slice | Carry the existing map metadata contract into the slice specification. **Assigned.** |
| 3 | Global, province, event, and control-volume scales are connected without claiming one metric partition. | P3 | Operating rules | Test the scale transition visually before release. **Accepted.** |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The north-star chain gives a non-specialist a memorable route from place to evidence. | P3 | North star | Use this as the landing-page information architecture. **Accepted.** |
| 2 | Calling the current repository “research-rich but link-heavy” accurately identifies the visitor problem. | P3 | Decision surface | Replace the corridor incrementally while preserving a complete index. **Accepted.** |
| 3 | The five-scene event story pairs each insight with a limitation rather than ending at a dramatic residual. | P3 | Recommended next slice | Keep the evidence badge and adjacent caveat visible. **Accepted.** |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Keyboard navigation, direct URLs, reset, text alternatives, and non-color evidence status are required. | P3 | Acceptance gate | Verify them together as one user journey. **Accepted.** |
| 2 | The initial acceptance gate did not explicitly cover state-change announcements. | P2 | Acceptance gate | Announce scene, evidence, loading, and error changes without stealing focus. **Resolved.** |
| 3 | Mobile acceptance protects the relationship among map, claim, and limitation. | P3 | Acceptance gate | Test a narrow viewport rather than merely permitting reflow. **Accepted.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The first draft named a test class without exact runnable commands. | P2 | Acceptance gate | Record pytest, unittest/CI, compile, browser syntax, and diff checks. **Resolved.** |
| 2 | JavaScript “subtests” were initially described as a separate Node suite. | P2 | Acceptance gate | Clarify that pytest reports the parameterized subtests and remove the nonexistent command. **Resolved.** |
| 3 | Asset optimization had no comparison basis. | P2 | Site-quality track | Measure the hosted baseline, reject unexplained regression, then adopt an evidence-based numeric budget. **Resolved.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | `PREVIEW-STATUS.md` predates later motion and D-series evidence and cannot silently define the next release. | P2 | Delivery and governance | Record the drift and require reconciliation before promotion. **Resolved.** |
| 2 | OSW has neither formal VTRACE/pitfalls artifacts nor a canonical TRACKER registry row. | P2 | Delivery and governance | State each absence plainly and reserve TRACKER registration for a separate portfolio decision. **Resolved.** |
| 3 | A central roadmap is ineffective if readers cannot find it. | P2 | README entry | Link it from the repository header and destination table. **Resolved.** |

## Synthesis

```text
Roles reviewed: 7
P1 blockers: 0  |  P2 issues: 10  |  P3 notes: 11

Verdict: APPROVED

Top finding: the next product slice should turn the existing D1-D14 evidence
chain into a guided atlas journey without converting a partial budget into a
causal or closed mechanism.

Cross-role consensus: scientific distinctions, provenance, accessibility, and
release truth must remain adjacent to the visual story rather than being moved
into repository-only documentation.
```

## Amendments

1. Added a current-state/next-decision table, the D-label namespace note, and
   the explicit stale-preview reconciliation gate.
2. Added exact offline validation commands and corrected the meaning of the ten
   pytest subtests.
3. Added assistive-technology announcements and an evidence-based asset-weight
   baseline before any numeric performance budget is chosen.

No external scientific peer review is implied by this repository role check.

---
skill: roles-check
topic: conops
date: 2026-09-06
roles_used: 8
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — OSW VTRACE CONOPS

**Artifact type:** concept of operations for public atlas use, scientific
audit/contribution, zoning challenge, release promotion, and planetary
comparison

**Source commit:** `6285bdd3b74b8924f006e8f8e4582d2673564c95` plus reviewed working-tree changes

**Reviewed artifacts:** `docs/vtrace/CONOPS.md`, stage status in
`docs/vtrace/README.md` and `docs/vtrace/STAGE_EXECUTION.md`, the Mission and
pitfall parents, and the related `ROADMAP.md` status update

## Role selection

All eight native OSW roles were selected because the operating scenarios span
physical interpretation, data/source custody, cartography, public explanation,
accessibility, reproducibility, repository/release control, and planetary
comparison.

## Review findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The guided event path could imply that its ordered scenes establish an ordered causal chain. | P2 | `OPS-SCN-OSW-001` | End with measured terms and an unresolved partial residual, not a causal verdict. **Resolved.** |
| 2 | The contribution path stops unsupported units, grids, sensitivity, and closure claims before promotion. | P3 | `OPS-SCN-OSW-004` | Preserve null and negative results as legitimate outputs. **Accepted.** |
| 3 | The zoning workflow allows conflicting diagnostics and demotion rather than forcing one score or count. | P3 | `OPS-SCN-OSW-005` | Define scoring details later without weakening individual diagnostics. **Accepted.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A research audit must identify the exact field before attempting reproduction. | P2 | `OPS-SCN-OSW-002` | Require provider/product, variable, units, sign/reference, time, depth, support, grid/mask, transformation, and checksum. **Resolved.** |
| 2 | Upstream disappearance or mutation must not be silently replaced by present-day bytes. | P2 | `OPS-SCN-OSW-002` degraded path | Preserve request, acquisition time, expected checksum, and bounded failure. **Resolved.** |
| 3 | The scenarios keep local deterministic verification separate from optional network acquisition. | P3 | System boundary / assumptions | Carry this separation into Requirements and Interfaces. **Accepted.** |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A missing province aggregation could otherwise be replaced by an attractive but unsupported fill. | P2 | `OPS-SCN-OSW-003` | Preserve direct grid projection and the explicit “no state aggregation” status. **Resolved.** |
| 2 | Seam identity, coastline context, missing/land/ice treatment, projection, and boundary class are present in the exploration workflow. | P3 | `OPS-SCN-OSW-003` | Make these interface invariants later. **Assigned.** |
| 3 | The zoning scenario separates classic reference identities from OSW organizational and diagnosed boundaries. | P3 | `OPS-SCN-OSW-005` | Preserve those as different data types. **Accepted.** |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Degraded states could become technical dead ends for public readers. | P2 | Operational states / scenarios | Preserve the last supported view and explain the unavailable comparison in plain language. **Resolved.** |
| 2 | The guided workflow consistently pairs one finding with its strongest limitation. | P3 | `OPS-SCN-OSW-001` | Use that pair as the scene-level editorial contract. **Accepted.** |
| 3 | Educator reuse receives stable links, text alternatives, caveats, and sources without creating a distinct truth surface. | P3 | Actors | Preserve the shared evidence route. **Accepted.** |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | URL, focus, announcement, map state, and text alternative must change as one transaction. | P2 | `OPS-SCN-OSW-003` | Make their synchronization a later interface requirement. **Resolved at CONOPS level; assigned to Requirements/Interfaces.** |
| 2 | An unknown URL or failed locally hosted overlay lacked an explicit accessible fallback in the first draft. | P2 | `OPS-SCN-OSW-003` degraded path | Announce the rejected state, retain the usable base map, and identify the unavailable overlay. **Resolved.** |
| 3 | Accessibility actors include keyboard, screen reader, low vision, reduced motion, touch, and narrow layouts. | P3 | Actors / validation evidence | Validate the complete scientific journey rather than isolated controls. **Accepted.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The contribution scenario needs explicit safe failure for malformed scientific inputs and stale generated artifacts. | P2 | `OPS-SCN-OSW-004` | Stop preview promotion and retain the negative evidence. **Resolved.** |
| 2 | PITFALL was linked but initially not exercised scenario by scenario. | P2 | Pitfall integration | Add a scenario-to-pitfall matrix with required behavior. **Resolved.** |
| 3 | Clean-checkout reproduction and a deliberately invalid fixture are both included. | P3 | `OPS-SCN-OSW-004`, `OPS-SCN-OSW-006` | Turn them into exact verification procedures later. **Assigned.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Release, preview, experiment, intake, and degraded states need distinct permitted claims. | P2 | Operational states | Define the five states and prohibit fabricated fallback results. **Resolved.** |
| 2 | Release promotion reconciles repository, citation, checklist, hosted target, commit, and owner decision. | P3 | `OPS-SCN-OSW-006` | Keep deployment smoke evidence separate from pre-deployment verification. **Accepted.** |
| 3 | TRACKER registration remains an explicit external owner decision. | P3 | `OQ-OSW-008` | Do not change portfolio metadata inside a product stage. **Accepted.** |

### ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Planetary analogy should not enter review before both quantities are defensible independently. | P2 | `OPS-SCN-OSW-007` handoff | Put CURRENT and SOUNDER ahead of ORBIT review. **Resolved.** |
| 2 | The scenario requires exact objects, shared property, non-analogous conditions, and a falsifier. | P3 | `OPS-SCN-OSW-007` | Preserve this as the comparison contract. **Accepted.** |
| 3 | A deliberately visual-only comparison is included as a negative validation case. | P3 | `OPS-SCN-OSW-007` validation | Retain it to prevent stripe/color resemblance from becoming mechanism. **Accepted.** |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 11  |  P3 notes: 13

Verdict: APPROVED-WITH-CONDITIONS

Top finding: OSW needs one operating chain in which public exploration,
research audit, contribution, and release share the same bounded evidence
instead of becoming separate truth systems.

Cross-role consensus: degraded paths are part of correctness. Missing sources,
unsupported aggregation, invalid URL state, failed overlays, and held releases
must remain legible without fabricating continuity.
```

All P2 findings were resolved or assigned to their named later stage with an
accepted CONOPS behavior. Conditions are stage boundaries: Requirements must
convert the scenarios into testable product statements, and later Interfaces
must control synchronized URL/focus/announcement state and scientific receipt
identity. No implementation or release is authorized.

## Amendments

1. Added the scenario-to-PITFALL exercise matrix so recurring risks participate
   in operations rather than remaining a detached register.
2. Added explicit unknown-URL and failed-local-overlay behavior that preserves
   a usable base map and announces degradation.
3. Recorded the current no-account/no-upload/no-cookie/no-telemetry boundary;
   any future change requires explicit change control.

Fixed-point decision: `pass_with_risk` for CONOPS only. Requirements is the
only VTRACE stage authorized to open next.

No external scientific peer review, NASA authorship, NASA endorsement, or
public-release approval is implied by this repository role check.

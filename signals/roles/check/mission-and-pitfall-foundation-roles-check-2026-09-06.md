---
skill: roles-check
topic: mission-and-pitfall-foundation
date: 2026-09-06
roles_used: 8
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — OSW VTRACE Mission and PITFALL foundation

**Artifact type:** VTRACE Mission/Need baseline, staged-adoption control, and
recurring-failure register

**Source commit:** `6285bdd3b74b8924f006e8f8e4582d2673564c95` plus reviewed working-tree changes

**Reviewed artifacts:** `docs/vtrace/MISSION.md`, `docs/vtrace/README.md`,
`docs/vtrace/STAGE_EXECUTION.md`, `design/pitfalls/README.md`, and the related
governance updates in `ROADMAP.md`

## Role selection

All eight OSW roles were selected. Mission scope controls physical claims,
source custody, cartography, public understanding, accessibility,
reproducibility, repository state, and Earth/gas-giant comparison. The initial
pitfall register crosses the same boundaries.

## Review findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The Mission must prevent a surface field, current arrow, residual, or open section from inheriting a stronger heat-budget claim. | P2 | Constraints | Separate every physical quantity and prohibit remainder-as-process or proximity-as-closure. **Resolved by `CON-OSW-003` and `CON-OSW-004`.** |
| 2 | Zoning could become a goal that preserves an attractive region count. | P2 | Mission needs / Constraints | Make merge, split, move, and demotion valid outcomes under transport tests. **Resolved by `NEED-OSW-007` and `CON-OSW-011`.** |
| 3 | The challenge scenario correctly treats a changed depth, time, product, or missing term as informative rather than adversarial failure. | P3 | `VAL-SCN-OSW-008` | Preserve this falsification posture through Requirements and Validation. **Accepted.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Regenerate the bytes” would be false when an upstream archive changes or a source is not redistributable. | P2 | `NEED-OSW-003` | Promise committed derived reproducibility and enough upstream identity to explain or challenge differences. **Resolved.** |
| 2 | Evidence-class labels alone do not identify an exact scientific field. | P2 | Constraints | Require variable, units, time, depth, support, reference, missing-data treatment, request, transformation, checksum, and custody as applicable. **Resolved by `CON-OSW-002` and `CON-OSW-008`.** |
| 3 | Observations, objective analyses, operational models, reanalyses, derived diagnostics, and cross-system screens remain distinguishable. | P3 | Operating context | Carry those source lineages into CONOPS scenarios and interface contracts. **Accepted.** |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Ocean-first” could be misread as removing the coastline context needed to recognize a place. | P2 | `CON-OSW-006` | Permit subdued land orientation while preventing land from covering ocean evidence. **Resolved.** |
| 2 | The Mission explicitly controls projection, seams, polar support, clipping, missing support, and boundary class. | P3 | Constraints / `VAL-SCN-OSW-004` | Allocate exact rendering behavior at the Interface and Design stages. **Assigned.** |
| 3 | The cartographic pitfall statuses are conservative; existing atlas tests do not prove every future standalone map safe. | P3 | `CA-01`, `CA-02` | Retain `mitigated` until a shared admission path covers all map families. **Accepted.** |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A technically accurate atlas could still fail if a non-specialist cannot repeat the main caveat. | P2 | Success criteria | Validate finding-and-limitation recall for the first guided story. **Resolved by `MSC-OSW-002`.** |
| 2 | The mission distinguishes an inviting public path from a researcher audit path without giving them different scientific truths. | P3 | `NEED-OSW-005` | Preserve one shared claim boundary beneath both paths. **Accepted.** |
| 3 | Non-goals directly reject the most tempting sensational claims about barriers, deep-time interventions, and deterministic causation. | P3 | Non-goals | Keep those boundaries adjacent to future counterfactual explanations. **Accepted.** |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Accessibility must preserve the scientific claim and limitation, not merely expose controls. | P2 | `CON-OSW-007`, `VAL-SCN-OSW-003` | Require keyboard, screen-reader, non-color, reduced-motion, zoom, and narrow-view validation as one scientific journey. **Resolved.** |
| 2 | The mission includes users on ordinary connections through the payload constraint. | P3 | `CON-OSW-014`, `MSC-OSW-008` | Establish a measured hosted baseline before setting a numeric budget. **Assigned.** |
| 3 | Direct URLs are correctly treated as an accessibility and resumability surface. | P3 | `VAL-SCN-OSW-003` | Define focus and announcement behavior during CONOPS and Interfaces. **Assigned.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Mission success initially named verification generally without exact commands. | P2 | Mission-stage verification | Record pytest, CI-equivalent unittest, compile, browser syntax, and diff gates. **Resolved.** |
| 2 | The pitfall register needs trace parents now rather than waiting for Requirements. | P2 | Pitfall register | Bind every initial pitfall to one or more Mission constraints. **Resolved.** |
| 3 | No pitfall is overstated as solved merely because an artifact-specific regression test exists. | P3 | Pitfall status rule | Preserve the structural-prevention-plus-test definition. **Accepted.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Starting VTRACE makes the roadmap's prior “no formal VTRACE” statement stale. | P2 | Roadmap governance | Record Mission as the only settled stage and keep every later stage unopened. **Resolved.** |
| 2 | The stage board must prevent parallel drafting from manufacturing apparent completeness. | P2 | Stage execution | Mark Mission settled, authorize CONOPS next, and leave later stages not started. **Resolved.** |
| 3 | OSW remains absent from TRACKER's canonical registry and the Mission does not silently claim otherwise. | P3 | Adoption boundary | Treat portfolio registration as a separate owner decision. **Accepted.** |

### ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The first Mission draft constrained planetary analogy but did not give it a mission-level success criterion. | P2 | Success criteria | Require the shared property, non-analogous conditions, and a possible falsifier. **Resolved by `MSC-OSW-009`.** |
| 2 | Forcing, stratification, rotation, depth, compressibility, boundaries, and observation method are all named as transfer checks. | P3 | `CON-OSW-012` | Preserve these dimensions in later comparison scenarios. **Accepted.** |
| 3 | The Mission does not make gas-giant visual resemblance a priority over Earth-side evidence. | P3 | Operating context / Non-goals | Keep comparison downstream of the exact Earth object and quantity. **Accepted.** |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 12  |  P3 notes: 12

Verdict: APPROVED-WITH-CONDITIONS

Top finding: OSW's mission is not merely to make the ocean visually legible;
it is to preserve the chain from place and motion to a correctly bounded
physical quantity and its evidence.

Cross-role consensus: the public journey and researcher audit must share one
claim boundary, with accessibility, provenance, projection, and limitations
treated as parts of correctness.
```

All P2 findings were repaired in the reviewed working tree. The conditions are
stage boundaries rather than unresolved Mission defects: CONOPS must define
actors and degraded paths; Requirements must make the accepted needs testable;
and no implementation or release is authorized by this Mission gate.

## Amendments

1. Tightened reproducibility scope, added exact Mission verification commands,
   and required each pitfall to name its parent Mission constraint.
2. Made subdued land orientation explicit and added accessibility as a
   complete claim-and-limitation journey rather than control conformance alone.
3. Added an independently reviewable success criterion for planetary analogy
   and synchronized the roadmap and stage board with the Mission fixed point.

Fixed-point decision: `pass_with_risk` for Mission only. No unresolved P1 or P2
Mission finding remains. The initial pitfall register contains open and
mitigated risks intentionally carried into later stages.

No external scientific peer review, NASA authorship, NASA endorsement, or
public-release approval is implied by this repository role check.

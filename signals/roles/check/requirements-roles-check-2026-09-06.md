---
skill: roles-check
topic: requirements
date: 2026-09-06
roles_used: 8
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — OSW VTRACE Requirements

**Artifact type:** controlled target product requirements for atlas experience,
scientific claims, data custody, cartography, accessibility, reproducibility,
contribution, release, compatibility, and planetary comparison

**Source commit:** `6285bdd3b74b8924f006e8f8e4582d2673564c95` plus reviewed working-tree changes

**Reviewed artifacts:** `docs/vtrace/REQUIREMENTS.md`, its Mission/CONOPS and
PITFALL parents, VTRACE stage status, and the related `ROADMAP.md` update

## Role selection

All eight OSW roles were selected because the Requirements baseline allocates
obligations across every native review domain. Role names in the requirement
table designate one accountable lens; cross-role checks remain explicit in
verification methods.

## Review findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Quantity names need a controlled identity rather than repeated prose caveats. | P2 | `REQ-OSW-006` through `REQ-OSW-008` | Require typed quantities, independently receipted budget terms, and incompatible motion-only claim ceilings. **Resolved.** |
| 2 | Requiring every zoning diagnostic could falsely imply unavailable evidence may be filled or ignored. | P2 | `REQ-OSW-009` | Require each diagnostic or explicit unavailable status and keep the boundary provisional when support is insufficient. **Resolved.** |
| 3 | Forecast, intervention, and authority exclusions remain product requirements rather than editorial suggestions. | P3 | `REQ-OSW-011` | Preserve the capability/content negative tests. **Accepted.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Receipt completeness differs legitimately by quantity and source. | P2 | `REQ-OSW-012` | Require the full identity envelope “as applicable” and test omission of each applicable field. **Resolved.** |
| 2 | Silent coercion at data boundaries is broader than checksum/schema failure. | P2 | `REQ-OSW-016` | Include dimensions, coordinate order, unit, sign, mask, collocation, partial cell, stencil, and time support. **Resolved.** |
| 3 | Source/intermediate/result/display/prose identities are separated. | P3 | `REQ-OSW-013` | Baseline current formats and gaps before selecting one schema. **Assigned to Specification Baseline.** |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Map metadata cannot all occupy the primary visual field at every viewport. | P2 | `REQ-OSW-017` | Require it to remain exposed/reachable, with exact placement deferred to interface/design evidence. **Resolved.** |
| 2 | Existing shared-atlas seam/mask tests do not cover every standalone figure. | P2 | `REQ-OSW-018` | Apply the invariant to every admitted map family and baseline current exceptions next. **Resolved.** |
| 3 | Boundary classes and metric limitations are machine-readable as well as editorial. | P3 | `REQ-OSW-019`, `REQ-OSW-020` | Preserve both data and redundant rendering checks. **Accepted.** |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “No more than three” primary routes could technically pass with zero, one, or two. | P2 | `REQ-OSW-001` | Require the named three and controlled change for addition/removal/rename. **Resolved.** |
| 2 | A receipt link alone does not protect a public claim from overstatement. | P2 | `REQ-OSW-003` | Require principal finding, strongest limitation, evidence identity, and receipt together. **Resolved.** |
| 3 | The D1-D14 sequence is required to end at unresolved terms rather than narrative closure. | P3 | `REQ-OSW-002` | Preserve this as the first story acceptance condition. **Accepted.** |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Visual selection and accessible state can drift during URL/history/loading/error transitions. | P2 | `REQ-OSW-022` | Require URL, selection, focus context, programmatic state, announcement, and text alternative to agree transactionally. **Resolved.** |
| 2 | Viewport, zoom, contrast, target, assistive-technology, and announcement thresholds are not yet evidence-based. | P2 | `REQ-OSW-021` through `REQ-OSW-024`; `DREQ-OSW-004` | Keep the behavior mandatory and defer exact thresholds to the observed-current baseline and validation plan. **Resolved by controlled deferral.** |
| 3 | Unknown URL and failed overlay behavior retains a usable supported state. | P3 | `REQ-OSW-022`, `REQ-OSW-033` | Exercise direct entry, reload, and history as well as control activation. **Accepted.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Several draft rows assigned two or three “owners,” leaving no decisive lens. | P2 | Requirement tables | Assign exactly one accountable native role and name supporting inspections in the verification method. **Resolved.** |
| 2 | Detailed verification methods could be misread as evidence that implementations already exist. | P2 | Scope / requirement language | State that every row is accepted target behavior and current status is reserved for Specification Baseline. **Resolved.** |
| 3 | PITFALL coverage maps all ten initial patterns to detecting/preventing requirements. | P3 | PITFALL coverage | Use the next baseline to identify which controls are current, partial, or absent. **Accepted.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Controlled artifact” and exactly-one lifecycle state are target concepts not yet proven across the repository. | P2 | `REQ-OSW-030` | Keep the obligation but classify the current registry/state reality next. **Resolved by stage boundary.** |
| 2 | Release reconciliation must include the hosted target and post-deployment check, not only repo files. | P2 | `REQ-OSW-031`, `REQ-OSW-032` | Separate candidate readiness from successful transition and preserved prior release. **Resolved.** |
| 3 | The static no-account/no-upload/no-cookie/no-telemetry boundary is protected against casual expansion. | P3 | `REQ-OSW-034` | Require controlled change and review before any exception. **Accepted.** |

### ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | ORBIT cannot validate an analogy built on an unidentified Earth or planetary quantity. | P2 | `REQ-OSW-010` | Make ORBIT accountable while requiring CURRENT/SOUNDER inspection first. **Resolved.** |
| 2 | A positive-only example would not prove visual resemblance is rejected. | P2 | `REQ-OSW-010` | Require paired defensible and deliberately visual-only fixtures. **Resolved.** |
| 3 | The requirement names both transfer dimensions and a falsifying outcome. | P3 | `REQ-OSW-010` | Keep exact metrics/thresholds for later design and validation. **Accepted.** |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 16  |  P3 notes: 8

Verdict: APPROVED-WITH-CONDITIONS

Top finding: the Requirements baseline must convert OSW's careful caveats into
testable product obligations without pretending those controls already govern
every existing artifact.

Cross-role consensus: one accountable role per requirement, paired with
cross-role verification where needed, is clearer than shared ownership.
```

All P2 findings are resolved in the accepted target baseline or explicitly
controlled by a named later-stage deferral. The principal condition is the next
stage itself: Specification Baseline must classify each relevant current
behavior as current, partial, conflicting, deprecated, or unknown before
Architecture or implementation planning.

## Amendments

1. Replaced ambiguous multi-role ownership with one accountable role per
   requirement and retained supporting lenses in verification methods.
2. Tightened the three-route requirement and distinguished required reachable
   map metadata from an assumption that everything must occupy the main map.
3. Added complete Mission/CONOPS and PITFALL coverage tables plus controlled
   deferrals for thresholds, schemas, architecture, custody, and validation.

Fixed-point decision: `pass_with_risk` for Requirements only. Thirty-four
accepted target requirements trace to all eight Mission needs, all seven
CONOPS scenarios, and all ten initial pitfalls. No implementation or public
promotion is authorized.

No external scientific peer review, NASA authorship, NASA endorsement, or
public-release approval is implied by this repository role check.

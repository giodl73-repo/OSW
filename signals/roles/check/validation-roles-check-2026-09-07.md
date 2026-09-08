---
skill: roles-check
topic: validation
date: 2026-09-07
roles_used: 8
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — OSW VTRACE Validation

**Artifact type:** human, scientific, cartographic, accessibility,
reproducibility, performance, and transition validation protocol

**Source commit:** `6285bdd3b74b8924f006e8f8e4582d2673564c95` plus reviewed working-tree changes

**Reviewed artifacts:** `docs/vtrace/VALIDATION.md`, Mission scenarios and
success criteria, CONOPS actors/degraded paths, Requirements, Verification,
Implementation Plan, Work Packages, PITFALL controls, and OSW native roles

**Fixed-point artifact identity:**

| Artifact | SHA-256 |
|---|---|
| `docs/vtrace/VALIDATION.md` | `87DCB37AE8A7CA0AB98FC66A7A5F39F97B87051B23E0C521DBA194AF0B2171AC` |

## Role selection

All eight roles were selected. The eight scenarios explicitly test physical
interpretation, receipt/source audit, map belief, public explanation,
accessible equivalence, reproducible operation, repository/release truth,
zoning decisions, and planetary mechanism transfer.

## Review findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Reader completion could pass even if the journey teaches budget closure or causal attribution. | P2 | Principles; VAL-SCN-OSW-001 | Make closure, causation, and motion-as-delivery critical zero-tolerance misconceptions. **Resolved.** |
| 2 | A scientific challenge selected after seeing results could merely defend the preferred story. | P2 | VAL-SCN-OSW-008 | Freeze the alternative, method, support, and tolerance; retain weakening, reversal, null, or unavailable outcomes. **Resolved.** |
| 3 | Boundary validation must permit abandoning the current region count. | P3 | VAL-SCN-OSW-005 | Keep blind-first dispositions and retain/merge/split/move/demote outcomes. **Accepted.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Reproduce the result” could hide use of different products, support, or processing. | P2 | VAL-SCN-OSW-002/008 | Bind exact artifacts, receipts, environment, method, support, and explain any divergence. **Resolved.** |
| 2 | One successful regenerated artifact cannot validate all admitted families. | P2 | VAL-SCN-OSW-006 | Require one supported regeneration/integrity path per admitted family or its declared bounded unavailable result. **Resolved.** |
| 3 | Contrary and unavailable source outcomes are legitimate validation evidence. | P3 | Principles/evidence envelope | Preserve them in the decision packet rather than filtering them from aggregates. **Accepted.** |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | General visual approval would miss seam, pole, land, ice, missing, and comparison-limit defects. | P2 | VAL-SCN-OSW-004 | Require a frozen map-family applicability inventory and explicit edge/support cases. **Resolved.** |
| 2 | A polished zoning map could bias reviewers before they inspect exchange evidence. | P2 | VAL-SCN-OSW-005 | Use frozen candidates and blind-first independent CURRENT/CHART dispositions. **Resolved.** |
| 3 | Text equivalence is part of map validity, not only accessibility. | P3 | VAL-SCN-OSW-003/004 | Compare map and text belief/state identity in both scenarios. **Accepted.** |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Educators were named mission users but had no explicit reuse trial. | P2 | VAL-SCN-OSW-001 | Add a separate educator/communicator task requiring stable link, text, source, evidence class, and caveat preservation. **Resolved.** |
| 2 | Facilitator or coder interpretation could move the recall rubric after seeing responses. | P2 | Scenario protocol | Freeze task/rubric, double-code responses with an independent coder, retain disagreements, and version/rerun changes. **Resolved.** |
| 3 | Five-reader gates are formative, not population estimates. | P3 | Scenario matrix note | State the limit explicitly and make failures trigger repair/retest rather than general claims. **Accepted.** |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Expert simulation alone cannot validate lived screen-reader operation. | P2 | VAL-SCN-OSW-003 | Require at least one routine screen-reader user and one routine non-pointer/zoom user, allowing one person to cover both; otherwise remain blocked. **Resolved.** |
| 2 | Browser screenshots cannot demonstrate equivalent state, focus, announcements, or meaning. | P2 | Environment/evidence envelope | Record the full browser/AT/input matrix, state digest, focus sequence, announcements, text, errors, and request state. **Resolved.** |
| 3 | Numeric contrast and target-size thresholds are still measurement decisions. | P3 | Controlled environment | Require values and HARBOR approval in the execution packet before public candidacy. **Accepted.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Validation could silently reuse pending Verification targets as if they passed. | P2 | Scope/scenario prerequisites | Block every scenario on explicit prerequisite VFY results and state that surrogates are not human/scientific validation. **Resolved.** |
| 2 | Maintainer validation did not necessarily prove provider isolation or verifier cleanliness. | P2 | VAL-SCN-OSW-006 | Require enforced network denial, before/after manifest, no private knowledge, and family-complete regeneration/integrity. **Resolved.** |
| 3 | All 20 VFY IDs should be mechanically discoverable. | P3 | Coverage | Add an expanded verification inventory rather than relying only on typographic ranges. **Accepted.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Participant evidence could violate the atlas no-collection/privacy boundary if raw records enter the repo. | P2 | Evidence envelope | Commit only pseudonymous minimal observations/aggregates; keep consent/contact/raw recordings in separately authorized, dated custody. **Resolved.** |
| 2 | A validation-plan fixed point could be mistaken for permission to contact participants or release. | P2 | Scope/gate | Explicitly withhold participant contact, implementation, push, deployment, endorsement, and release authority. **Resolved.** |
| 3 | Performance and hosted-transition decisions require owner acceptance. | P3 | Performance/release | Record numeric budgets and release decision only after measurement/rehearsal. **Accepted.** |

### ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Readers might remember visual similarity while missing regime differences. | P2 | VAL-SCN-OSW-007 | Require recall of mechanism/property, at least two material differences, and a weakening outcome. **Resolved.** |
| 2 | Presentation order could bias supported versus resemblance-only judgment. | P2 | VAL-SCN-OSW-007 | Randomize pair order and retain zero-tolerance material-equivalence/full-depth-heat errors. **Resolved.** |
| 3 | Expert admission and reader understanding answer different questions. | P3 | VAL-SCN-OSW-007 | Require both ORBIT/CURRENT/SOUNDER records and reader evidence. **Accepted.** |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 16  |  P3 notes: 8

Verdict: APPROVED-WITH-CONDITIONS

Top finding: OSW validation must measure the belief a map or story leaves
behind—not merely whether a participant clicked through it or an expert liked
its appearance.

Cross-role consensus: freeze tasks and identities before observation, treat
unsupported stronger interpretations as hard failures, include actual access
users and independent scientific/repository operators, and retain negative
results without turning participation into endorsement.
```

All 16 P2 findings are repaired in the reviewed Validation plan. Remaining
conditions are deliberately blocked execution evidence: prerequisite features
and VFY items do not yet exist; participants have not been recruited or
contacted; hosted performance and transition mechanisms are unknown; no
scenario has run or passed.

## Amendments

1. Defined eight controlled scenario protocols with hard misconception gates,
   formative reader thresholds, independent research/cartographic/scientific
   operation, exact prerequisites, and honest blocked states.
2. Added educator reuse, routine screen-reader/non-pointer participation,
   double-coded prompt-free recall, full browser/access evidence, and minimal
   pseudonymous data custody.
3. Preserved null/contrary/unavailable evidence, blind-first zoning,
   randomized planetary pairs, measurement-before-budget, pure release
   rehearsal, and no-contact/no-release authority boundaries.

Fixed-point decision: `pass_with_risk` for the Validation plan only. The plan
is ready to govern later scenario execution; all acceptance evidence remains
blocked. Trace may open next but is not opened by this review.

No validation execution, participant recruitment/contact, implementation,
scientific endorsement, commit, push, deployment, public release, external
approval, or NASA affiliation is authorized or implied.

---
skill: roles-check
topic: verification
date: 2026-09-07
roles_used: 8
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — OSW VTRACE Verification

**Artifact type:** repository-wide verification plan, controlled command
catalog, fixture catalog, and evidence ledger

**Source commit:** `6285bdd3b74b8924f006e8f8e4582d2673564c95` plus reviewed working-tree changes

**Reviewed artifacts:** `docs/vtrace/VERIFICATION.md`, all settled left-side
VTRACE artifacts, current tests and CI, planned physical seams, nine proposed
work packages, the PITFALL register, and OSW native roles

**Fixed-point artifact identity:**

| Artifact | SHA-256 |
|---|---|
| `docs/vtrace/VERIFICATION.md` | `580088409CF8D59395673ADE79D1C6EB63456C2388EDA743994131219FE7C6A0` |

## Role selection

All eight native roles were selected because verification spans physical
quantities and budgets, provenance and custody, projections and support,
reader-facing claims, equivalent accessible state, executable offline gates,
release truth, and planetary-comparison falsification.

## Review findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A numeric near-balance test could pass while the prose asserts physical closure. | P2 | VFY-OSW-004/014 | Verify quantity identity and prohibited claim language alongside calculation results. **Resolved.** |
| 2 | Sensitivity tests could reward only the preferred depth/time/product outcome. | P2 | FIX-OSW-013 | Require frozen selection, controls, contrary/null results, and independent calculation with named tolerance. **Resolved.** |
| 3 | Zoning diagnostics must remain disaggregated. | P3 | VFY-OSW-015 | Preserve unavailable and contradictory fields and the attractive-false-border case. **Accepted.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Passing one family fixture cannot prove complete admitted-family coverage. | P2 | VFY-OSW-002/012 | Require complete family inventories and one representative mutation/integrity path per admitted family. **Resolved.** |
| 2 | A normalized receipt could pass after silently losing historical fields. | P2 | FIX-OSW-003 | Require lossless source identity, preserved unknowns, and explicit unavailable meaning. **Resolved.** |
| 3 | Exact bytes are not always the scientific contract. | P3 | Verification rule 6 | Use semantic/numeric/geometry checks unless byte identity is explicitly authoritative. **Accepted.** |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Map-family correctness cannot be inferred from the common atlas alone. | P2 | VFY-OSW-009 | Require an applicability inventory and family-level seam/pole/support/boundary/comparison proof. **Resolved.** |
| 2 | Sea ice could be tested only as missing paint, recreating the support-model defect. | P2 | VFY-OSW-005; FIX-OSW-005/010 | Test orthogonal axes and valid subsurface-under-ice in visual and text outputs. **Resolved.** |
| 3 | Screenshots do not prove comparison capability or map semantics. | P3 | Evidence envelope | Record view/state digest, metadata, text equivalent, and controlled inspection. **Accepted.** |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Registry completeness alone cannot show that each scene communicates one bounded idea. | P2 | VFY-OSW-008 | Verify question/finding/strongest-limitation/receipt/value binding for every ordered scene. **Resolved.** |
| 2 | Automated prose checks cannot establish reader comprehension. | P2 | Scope; gaps | Keep comprehension and recall in Validation and label automated cases as surrogates. **Resolved.** |
| 3 | Non-authority language requires both positive boundaries and prohibited examples. | P3 | VFY-OSW-013; FIX-OSW-018 | Retain forecast/navigation/intervention/endorsement/release negatives. **Accepted.** |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A generic browser matrix omits the state needed to reproduce an accessibility failure. | P2 | Evidence record envelope | Record browser/AT/input/viewport/zoom/motion, focus, announcements, text, digest, and request state. **Resolved.** |
| 2 | Screenshots and DOM presence do not prove keyboard or assistive equivalence. | P2 | VFY-OSW-010 | Require complete action paths and same accepted state/finding/limitation in every channel. **Resolved.** |
| 3 | Acceptance thresholds for reflow and comprehension belong to Validation. | P3 | Verification gaps | Verify instrumentation/behavior now and defer accepted human thresholds explicitly. **Accepted.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Tests that happen not to fetch are not proof of operation with network denied. | P2 | VFY-OSW-001; L1 | Remove the baseline overclaim and add an enforced outbound-denial target with optional-dependency isolation. **Resolved.** |
| 2 | `git diff --check` cannot detect ignored/untracked residue or a verifier rewriting an already dirty candidate. | P2 | VFY-OSW-020 | Require declared before/after manifests and accepted-artifact hashes around every gate. **Resolved.** |
| 3 | Future commands must remain pending while their modules do not exist. | P3 | Verification matrix | Preserve baseline/target state separation and block package readiness. **Accepted.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Evidence without commit/artifact/environment identity cannot be compared later. | P2 | Evidence record envelope | Require immutable identities, exact command revision, environment, result, diagnostics, and evidence-file identity. **Resolved.** |
| 2 | A release test could mutate citation/current state while deciding readiness. | P2 | VFY-OSW-017/018 | Separate pure reconciliation from staged effects and require retain/restore before metadata advancement. **Resolved.** |
| 3 | Verification approval is not implementation, push, deployment, or release authority. | P3 | Scope/gate | Keep every work package proposed and the owner release gate explicit. **Accepted.** |

### ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A planetary fixture could validate schema completeness while leaving only visual resemblance. | P2 | VFY-OSW-016 | Require independent quantities, regime/observability differences, and a weakening/falsification outcome. **Resolved.** |
| 2 | Earth-side and planetary evidence could be collapsed into one analogy score. | P2 | FIX-OSW-015 | Keep identities and domain admissions separate; verify supported and resemblance-only records. **Resolved.** |
| 3 | Planetary verification must not block the first Earth-ocean journey. | P3 | Work-package L2 map | Retain WP-OSW-008 as independently deferred. **Accepted.** |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 16  |  P3 notes: 8

Verdict: APPROVED-WITH-CONDITIONS

Top finding: a passing current test run is not evidence for a future target,
an enforced network-denial environment, a clean verifier, or human validity;
each needs its own controlled evidence identity.

Cross-role consensus: verify scientific identity, support, public meaning, and
artifact custody together at their narrow boundaries, then reserve human
usefulness and accepted thresholds for Validation.
```

All 16 P2 findings are repaired in the reviewed Verification plan. Remaining
conditions are forward evidence, not missing plan content: target modules and
fixtures must be implemented and executed; URL, family, responsive,
performance, and deployment discoveries must settle; Validation must accept
human/scientific/operational thresholds; owner authority remains required for
promotion.

## Amendments

1. Split current baseline evidence from target-pending proof, removed the
   unearned network-disabled claim, and added enforced network/optional-
   dependency isolation plus before/after non-mutation evidence.
2. Added 20 controlled verification items, 20 fixture classes, an immutable
   evidence envelope, explicit requirement/interface/invariant/rigor/package
   coverage, and L0/L1/L2 gates.
3. Strengthened claim-language, family completeness, lossless adaptation,
   orthogonal support, accessibility-state reproduction, planetary
   falsification, and pure-release/retain-restore paths.

Fixed-point decision: `pass_with_risk` for Verification planning only. Current
baseline evidence is recorded; target evidence remains pending. Validation may
open next but is not opened by this review, and work packages remain proposed.

No implementation, scientific endorsement, work-package execution, commit,
push, deployment, public release, external approval, or NASA affiliation is
authorized or implied.

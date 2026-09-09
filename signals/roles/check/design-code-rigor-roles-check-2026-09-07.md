---
skill: roles-check
topic: design-code-rigor
date: 2026-09-07
roles_used: 8
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — OSW VTRACE Design and Code Rigor

**Artifact type:** detailed component/state/evidence/release design plus tailored
multi-language implementation rigor baseline

**Source commit:** `6285bdd3b74b8924f006e8f8e4582d2673564c95` plus reviewed working-tree changes

**Reviewed artifacts:** `docs/vtrace/DESIGN.md`, `docs/vtrace/CODE_RIGOR.md`,
the settled Architecture/Interfaces, a controlled IF-OSW-009 support-model
amendment, current browser and Python source shape, tests, and PITFALL controls

**Fixed-point artifact identities:**

| Artifact | SHA-256 |
|---|---|
| `docs/vtrace/DESIGN.md` | `90C91DBA6624966F388EC9979B20EA44FD4E2B784DFB96711EE53CEAD6F0D486` |
| `docs/vtrace/CODE_RIGOR.md` | `C0B2AF6A01BD8C1BAC569F174B258FA8D54C52FB1C46DA4BDEE9DD6E8A9968B3` |
| `docs/vtrace/INTERFACES.md` (support-model amendment) | `2FAD6626D70D930BE9C7A63F85703251717DE22AF44E952C42C480FB13EEEE29` |

## Role selection

All eight native roles were selected. The paired artifacts define physical
quantity/support behavior, evidence adapters, map/view construction, public
route/scene behavior, transactional accessible state, executable rigor,
release effects, and planetary/zoning validators.

## Review findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The prior single support enum made sea ice mutually exclusive with valid ocean data, which is false for subsurface measurements beneath ice. | P2 | IF-OSW-009 amendment; DES-OSW-008 | Replace it with orthogonal geometry, data-status, and surface-condition axes and add a beneath-ice fixture. **Resolved.** |
| 2 | Scientific adapters and display formatting must never infer unit, sign, reference, support, or operator from filenames/prose. | P2 | Evidence normalization; CR-OSW-006–010 | Reject ambiguity, require typed bindings, and keep budget residual identities immutable. **Resolved.** |
| 3 | Zoning still has no opaque composite score or design-time threshold. | P3 | DES-OSW-014; DES-UNK-OSW-006 | Preserve diagnostic-by-diagnostic evidence until scientific validation. **Accepted.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Normalizing historical records could manufacture completeness unless source bytes, unknown fields, and unavailable meanings survive. | P2 | DES-OSW-006; CR-OSW-010, 013 | Require contract-specific lossless adapters, source identity, explicit unavailability, and round-trip/preservation proof. **Resolved.** |
| 2 | Download, validation, accepted replacement, calculation, and publication in one effectful path would risk corrupting custody. | P2 | DES-OSW-011; CR-OSW-011, 012 | Stage candidate bytes, validate first, replace atomically, and keep calculation/publication separate. **Resolved.** |
| 3 | A future schema dependency requires a bakeoff rather than being selected by documentation. | P3 | DES-UNK-OSW-002 | Carry stdlib/custom versus pinned-validator choice to implementation planning. **Accepted.** |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Independent visual and text calculations could disagree even if both read the same data file. | P2 | DES-OSW-009; CR-OSW-017 | Build one validated view model and require shared view/state identity across both projections. **Resolved.** |
| 2 | A single support enum or alpha channel would conflate land, missingness, invalid data, and sea ice. | P2 | Support propagation; CR-OSW-008 | Preserve three support axes and test valid subsurface values beneath ice. **Resolved.** |
| 3 | Hit testing may return only identities already present in the admitted view model. | P3 | View-model design | Preserve negative geometry/identity fixtures. **Accepted.** |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Hard-coded route and next/back branches would let the visible journey drift from its semantic order. | P2 | DES-OSW-004 | Use ordered route/scene registries with complete claim/limitation/receipt bindings. **Resolved.** |
| 2 | Public numbers copied into prose can outlive their result or formatting convention. | P2 | DES-OSW-005; INV-OSW-005 | Resolve structured value bindings and block the scene when a path/checksum changes. **Resolved.** |
| 3 | Progressive enhancement keeps route outcomes and limitations available without JavaScript. | P3 | DES-OSW-001 | Validate with a no-script public-route inspection. **Accepted.** |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Current control callbacks mutate global state incrementally and silently clamp some values; the target design must not copy that pattern. | P2 | DES-OSW-002, 003 | Separate parse/adapt/validate/prepare/commit and return one consolidated diagnostic set. **Resolved.** |
| 2 | “One canonical state” could still leave focus, URL, text, and canvas updates partially committed. | P2 | Canonical state algorithm; INV-OSW-001 | Require a shared digest and all-or-previous transactional projections. **Resolved.** |
| 3 | Measured viewport, zoom, contrast, target, and AT thresholds remain Validation work. | P3 | DES-UNK-OSW-004 | Preserve instrumentation and mandatory semantic behavior without invented numbers. **Accepted.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The 60/100-line rules would falsely imply current conformance or trigger unsafe mass refactoring without a measured grandfathered baseline. | P2 | Tailoring; waivers | Record 1,404-line `atlas/app.js`, 76 Python functions over 60 physical lines, and 19 over 100; require touched-unit characterization/decomposition or focused waiver. **Resolved.** |
| 2 | Generic “add tests” language would not constrain admission algebra, diagnostic stability, generated families, or verification mutation. | P2 | CR-OSW-003, 004, 013, 019, 022, 023 | Require negative/property/mutation fixtures, stable codes, family comparisons, and clean-candidate verification. **Resolved.** |
| 3 | Seven L0/L1/L2 profiles proportion rigor to docs, Python, browser, maps, data, multi-boundary, and release changes. | P3 | Language profiles | Preserve no-network default and L2 escalation for high-risk behavior. **Accepted.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Deployment side effects inside readiness evaluation could publish before drift/owner/admission checks finish. | P2 | DES-OSW-013; CR-OSW-020 | Make reconciliation pure and require an immutable ready report before a separate deployment adapter. **Resolved.** |
| 2 | Legacy waivers could become permanent permission to copy debt or bypass release gates. | P2 | Exceptions and migration waivers | State that waivers are current debt only, give owners/revisit triggers, and forbid core scientific/privacy/access/release exceptions. **Resolved.** |
| 3 | Deployment and rollback mechanism remains explicitly unknown while required outcomes are designed. | P3 | DES-UNK-OSW-005; WAIVER-OSW-005 | Carry to Implementation Plan. **Accepted.** |

### ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A standalone analogy renderer could bypass quantity, receipt, and domain-admission logic. | P2 | DES-OSW-014; INV-OSW-016 | Consume shared admitted identities and add only comparison-specific regimes/differences/falsification. **Resolved.** |
| 2 | Visual resemblance needs a stable negative path, not reviewer memory. | P2 | EDGE-OSW-014; Code Rigor hooks | Require resemblance-only fixture and CURRENT/SOUNDER/ORBIT dispositions. **Resolved.** |
| 3 | No planetary framework or separate truth store is introduced. | P3 | Design scope | Preserve this boundary during implementation planning. **Accepted.** |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 16  |  P3 notes: 8

Verdict: APPROVED-WITH-CONDITIONS

Top finding: scientific support is multidimensional—geometry, data validity,
and surface condition must remain orthogonal or sea ice will erase valid ocean
evidence and missingness will become false data.

Cross-role consensus: implement new contracts through pure, testable seams and
lossless adapters around the working system; do not use rigor as a pretext for
a wholesale rewrite or as paperwork that leaves failures silent.
```

All P2 findings are repaired in the reviewed Design/Code Rigor pair and the
controlled IF-OSW-009 amendment. Remaining conditions are bounded forward work:
physical module/schema/tool selections and fixture ownership in Implementation
Plan; executed procedures in Verification; measured user/performance thresholds
in Validation; deployment mechanism before release readiness.

## Amendments

1. Replaced the mutually exclusive support model with three orthogonal axes,
   updated interface/design/rigor invariants, and added a valid-subsurface-under-
   ice edge case.
2. Defined pure transactional reader state, shared view-model projections,
   lossless evidence adapters, staged custody replacement, federated admission,
   selected-view loading, and pure release reconciliation.
3. Tailored 25 constraints and seven L0/L1/L2 profiles, measured legacy size
   debt, added six owned migration waivers, and made the 60/100-line rules apply
   prospectively to touched critical units rather than triggering a rewrite.

Fixed-point decision: `pass_with_risk` for Design and Code Rigor only. All 15
interfaces map to decisions/invariants; high-risk change classes require L2;
legacy debt is explicit and bounded. Implementation planning may open next but
is not opened by this review.

No code implementation, framework/schema/tool adoption, work package,
deployment, public release, scientific endorsement, or NASA affiliation is
authorized or implied.

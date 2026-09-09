---
skill: roles-check
topic: interfaces
date: 2026-09-06
roles_used: 8
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — OSW VTRACE Interfaces

**Artifact type:** durable public/internal interface, descriptor, diagnostic,
compatibility, and fixture-obligation baseline

**Source commit:** `6285bdd3b74b8924f006e8f8e4582d2673564c95` plus reviewed working-tree changes

**Fixed-point artifact SHA-256:**
`bbfa59f27c66fe5dbb3bb3c7e1b43a0861a190aca3f62e5ac993796af0123260`

**Reviewed artifacts:** `docs/vtrace/INTERFACES.md`, the settled Specification
Baseline and Architecture pair, current atlas URL/state behavior, representative
evidence receipts, source/custody surfaces, tests, and PITFALL controls

## Role selection

All eight native roles were selected because these contracts cross every domain
veto established by Architecture. CURRENT governs quantity and physical claim;
SOUNDER provenance/support; CHART map semantics; BEACON scenes/routes; HARBOR
state equivalence; KEEL composition/integrity; LOGBOOK release/privacy; ORBIT
planetary transfer.

## Review findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Quantity class alone cannot distinguish two physically different records without time/depth/space, sign/reference, and operator identity. | P2 | IF-OSW-007 | Require all physical support and convention fields and block incompatible combinations. **Resolved.** |
| 2 | A budget interface could recreate false closure if residual identity changed when terms happened to be numerically close. | P2 | IF-OSW-007 | Make budget an ordered set of independently receipted terms plus an immutable residual class. **Resolved.** |
| 3 | Zoning score combination remains deferred while unavailable evidence is prohibited from becoming a supporting score. | P3 | IF-OSW-015 | Preserve diagnostic-by-diagnostic state and CURRENT/CHART admission. **Accepted.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The first draft placed receipt structure under the release interface, permitting release to appear authoritative over evidence identity. | P2 | IF-OSW-003, IF-OSW-005 | Move the complete evidence envelope to the scene/evidence interface and make release consume immutable admitted receipt identities only. **Resolved.** |
| 2 | Historical receipt variants cannot safely be rewritten to pretend currently absent provenance fields existed. | P2 | Scope; IF-OSW-003 | Require lossless adapters/additive sidecars and explicit unavailable states that constrain claims. **Resolved.** |
| 3 | Current evidence-origin vocabulary is preserved separately from method/display class. | P3 | IF-OSW-007 | Keep origin and transformation status orthogonal in later schemas. **Accepted.** |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Registered boundary class” is insufficient unless initial meanings and no-promotion behavior are controlled. | P2 | IF-OSW-004 | Name the seven initial classes and forbid adapters from promoting one to another. **Resolved.** |
| 2 | Existing ring values are clamped silently; target direct-URL behavior requires a visible/announced rejection rather than invisible coercion. | P2 | IF-OSW-002 | Record the current 0–89° range and target diagnostic behavior explicitly. **Resolved.** |
| 3 | Comparison capabilities include area, shape, distance, direction, and cross-panel limits rather than a generic projection caveat. | P3 | IF-OSW-004 | Preserve per-capability reasons in map fixtures. **Accepted.** |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | `route_id` was initially described as one field with three values rather than a registry containing exactly three route records. | P2 | IF-OSW-001 | Define one ordered three-record registry with stable IDs and separately controlled labels/targets/outcomes. **Resolved.** |
| 2 | A guided scene could satisfy navigation while hiding either its strongest limitation or the receipt route. | P2 | IF-OSW-003, IF-OSW-008 | Bind finding, limitation, evidence identity, receipt, and value paths in one scene contract. **Resolved.** |
| 3 | The seven required scientific stages may be grouped visually but remain present in semantic order. | P3 | IF-OSW-008 | Validate comprehension and unresolved terminal state later. **Accepted.** |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The current URL vocabulary includes aliases and asymmetric defaults that must be inventoried before a compatibility promise is credible. | P2 | IF-OSW-002 | Record current mode/lens/view/depth/property/clock/pressure/ring/probe tokens and target state additions. **Resolved.** |
| 2 | Field-by-field fallback could commit visual state before accessible state or scatter multiple announcements. | P2 | Contract conventions; IF-OSW-002 | Require transactional state and one consolidated visible/announced diagnostic without focus theft. **Resolved.** |
| 3 | Numeric reflow, zoom, contrast, and target-size thresholds remain Validation inputs, not fabricated interface constants. | P3 | Open risks | Preserve semantic obligations while deferring measured thresholds. **Accepted.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Interface prose without stable diagnostics would not support negative fixtures or actionable degraded behavior. | P2 | Diagnostic allocation | Allocate stable symbolic codes across version, state, claim, receipt, map, privacy, quantity, support, admission, acquisition, artifact, review, zoning, and release failures. **Resolved.** |
| 2 | A generated-artifact inventory needs comparison semantics and payload class, not only a generator command. | P2 | IF-OSW-012 | Require input/output identities, dependency profile, comparison mode, negative fixture, lifecycle/admission, and four payload classes. **Resolved.** |
| 3 | Actual fixtures and work-package ownership remain unopened while their minimum contract shape is controlled. | P3 | Contract-boundary and fixture impact | Preserve stage boundary. **Accepted.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Evidence identity and release identity must not share an authority surface. | P2 | IF-OSW-003, IF-OSW-005 | Make hosted release bind but never backfill or reinterpret admitted evidence. **Resolved.** |
| 2 | Compatibility policy must preserve shared unversioned links without promising indefinite support for every historical token. | P2 | IF-OSW-002 | Treat current unversioned links as legacy-v0, emit v1, dual-read one prior version for at least one subsequent public release, and require controlled retirement. **Resolved.** |
| 3 | Hosted proof and retain/restore mechanics remain implementation unknowns while their required outcome record is fixed. | P3 | IF-OSW-005; open risks | Carry to Implementation Plan. **Accepted.** |

### ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A comparison contract that names only a shared mechanism could still omit differing regimes and observation methods. | P2 | IF-OSW-014 | Require both quantities/receipts and all forcing, stratification, rotation, depth, compressibility, boundary, and observation differences. **Resolved.** |
| 2 | Missing planetary evidence must not be silently represented as measured equivalence. | P2 | IF-OSW-014; IF-OSW-010 | Permit only clearly speculative bounded comparison and retain CURRENT/SOUNDER/ORBIT admissions. **Resolved.** |
| 3 | The weakening/falsifying outcome is a durable field that cannot disappear through a same-version prose edit. | P3 | IF-OSW-014 | Preserve it in fixtures and claim admission. **Accepted.** |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 16  |  P3 notes: 8

Verdict: APPROVED-WITH-CONDITIONS

Top finding: evidence and release require separate interfaces; release may bind
admitted evidence but can never define, repair, or reinterpret it.

Cross-role consensus: every durable interface needs explicit identity,
versioning, negative behavior, diagnostic, and domain veto—not merely a happy
path or a prose caveat.
```

All P2 findings are repaired in the reviewed Interface baseline. Remaining
conditions are intentionally allocated forward: physical record schemas and
adapters, component form, and algorithms to Design; L0/L1/L2 enforcement to
Code Rigor; fixture files and work ownership to Implementation Plan; executed
proof and user thresholds to Verification/Validation; deployment mechanism to
Implementation Plan.

## Amendments

1. Separated evidence receipts from hosted release state, made release a
   read-only consumer of admitted identities, and required lossless historical
   adapters or explicit unavailability.
2. Replaced ambiguous route/state descriptions with an exact three-route
   registry, current URL vocabulary, v1/legacy compatibility policy,
   transactional fallback, and state diagnostics.
3. Added controlled quantity/evidence/boundary/support vocabularies, federated
   admission composition, generated-family payload/comparison classes, and
   eighteen stable diagnostic allocations with required fixture classes.

Fixed-point decision: `pass_with_risk` for Interfaces only. Fifteen interfaces
preserve all six prior public IDs, cover all 45 specification items, and define
the contract inputs later stages must implement and prove. Design and Code
Rigor may open next as their paired stage but are not opened by this review.

No implementation, schema library, framework, deployment, public release,
scientific endorsement, or NASA affiliation is authorized or implied.

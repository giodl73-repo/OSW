---
skill: roles-check
topic: wp001a-implementation
date: 2026-09-08
roles_used: 8
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — WP-OSW-001A implementation

**Artifact type:** Python contract kernel, invented fixtures, tests, and tool
decision

**Source commit:** `2e511ca8fc5d1f271a5bb4342e94132e845d4b6d` plus the reviewed 001-A
candidate

**Reviewed artifacts and fixed-point identities:**

| Artifact | SHA-256 |
|---|---|
| `analysis/osw_diagnostics.py` | `80B17B1F894CFA881DE19BB6D2EE3206F67718918215986B9F00445A79BBE116` |
| `analysis/osw_contracts.py` | `402DBB6490092E26455D0E0E9F2C2C5692E5B0F5235BBD5CCB56DBFA509F09C1` |
| `analysis/test_osw_contracts.py` | `9A13656B942FE90C9EF7ED21ECAC099CF2E4E0F9E8367A3AFAA223E908E8A90A` |
| `analysis/fixtures/osw-contracts/valid-contract-identities.json` | `BF61DE471EBA34F98520BB0F44EA7C1BCFD734A46E2C719851C6A9B40DE3E77C` |
| `analysis/fixtures/osw-contracts/invalid-secret-context.json` | `761B45EEFCC66C4D17C40DB9FA304558A6BCFC429C7D414D18EF93FABB309D94` |
| `context/waves/2026-09-08-wp001a-contract-foundation/TOOL_BAKEOFF.md` | `D49ADCF3E03AD23856323CFB87F00E0BFD959A6446010B7D89A9176ACC252F91` |

## Role selection

All eight roles were selected. These internal types encode physical quantity,
data/support, map-facing state, public-safe diagnostics, access-relevant
unknowns, executable identity, repository authority, and a boundary that later
planetary comparison must consume without widening.

## Review findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The initial point/sample operator spelling was an invented serialization rather than the reviewed interface term. | P2 | `IntegrationOperator` | Use the exact reviewed `point/sample` value and fixture. **Resolved.** |
| 2 | Quantity identity could be mistaken for scientific calculation or causal admission. | P2 | Module boundary / `QuantityIdentity` | State the non-calculation boundary and require an explicit nonempty `does_not_support` ceiling. **Resolved.** |
| 3 | The core vocabulary correctly keeps temperature, heat content, transport, advection, convergence, transformation, and residual distinct. | P3 | `QuantityClass` | Preserve these classes through 001-B adapters. **Accepted.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | String subclasses, whitespace, case folding, or Unicode-confusable IDs could alias exact evidence identity. | P2 | Exact validators | Require exact built-in strings, lowercase grammar, no normalization, and negative fixtures. **Resolved.** |
| 2 | Repository paths could alias through drive syntax, backslashes, dot segments, double separators, or trailing separators. | P2 | `ArtifactIdentity` | Require canonical repository-relative POSIX spelling and lowercase SHA-256. **Resolved.** |
| 3 | Family unavailable fields remain explicit and immutable rather than being synthesized. | P3 | `ArtifactFamilyIdentity` | Preserve this behavior in 001-B. **Accepted.** |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A single support enum would erase the difference between land, missing data, and sea ice. | P2 | `SupportIdentity` | Keep geometry, data status, and surface condition as independent closed axes. **Resolved.** |
| 2 | “Sea ice” could incorrectly invalidate a valid subsurface ocean value. | P2 | Support fixture | Retain ocean + valid + sea-ice as a tested, representable identity. **Resolved.** |
| 3 | No renderer, map data, figure, or public page changed in this pulse. | P3 | Scope inspection | Keep map behavior in WP-OSW-003. **Accepted.** |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Errors originally risked echoing caller-supplied labels or unknown values. | P2 | Contract exceptions | Emit only allocated code, canonical field, and fixed reason; replace unsafe field labels with `unknown_field`. **Resolved.** |
| 2 | Direct construction or custom specs could bypass the safe diagnostic factory. | P2 | `DiagnosticEnvelope` | Revalidate canonical context and require exact membership in the global allocation. **Resolved.** |
| 3 | Diagnostic meaning and required disposition remain adjacent in the registry. | P3 | Registry | Retain this pairing when presentation text is added later. **Accepted.** |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Silent normalization of unknown controlled values would make later UI fallback impossible to explain or announce. | P2 | `parse_closed` | Fail exact unknowns with a stable field-local diagnostic. **Resolved.** |
| 2 | Identity types alone could be overstated as proof of accessible interaction. | P2 | Module and evidence boundary | Keep UI/state work and VAL-SCN-OSW-003 blocked. **Resolved.** |
| 3 | Stable code plus bounded context can later support equivalent visual and announced errors. | P3 | `DiagnosticEnvelope` | Preserve code identity across channels. **Accepted.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Frozen dataclasses alone do not prevent constructor bypass through mutable collections or a directly built envelope. | P2 | Constructors/tests | Require exact tuples, duplicate checks, canonical revalidation, and direct-constructor adversarial tests. **Resolved.** |
| 2 | A count-only registry test could miss replacement of one allocated diagnostic by another invented code. | P2 | Registry test | Compare the exact 18-code set and deterministic order. **Resolved.** |
| 3 | All functions remain below the 60-line soft cap and all new files have zero lines beyond 120 characters. | P3 | Rigor metrics | Recompute at closeout. **Accepted.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Artifact identity could retain private machine paths or review identity could imply endorsement/release authority. | P2 | `ArtifactIdentity` / `ReviewIdentity` | Reject machine/parent paths and require both authority booleans to remain exactly false. **Resolved.** |
| 2 | Tool adoption could quietly add dependency/configuration or network work outside the entry packet. | P2 | Tool bakeoff | Record installed-state evidence and explicitly reject external tool adoption for 001-A without installing anything. **Resolved.** |
| 3 | The failed initial tests and shell metadata probes remain visible in closeout evidence. | P3 | Evidence history | Preserve them with their corrective outcomes. **Accepted.** |

### ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A generic shared registry could accidentally register or admit an Earth/gas-giant comparison. | P2 | Scope / family identity | Keep comparison records, mechanism transfer, and WP-OSW-008 entirely absent. **Resolved.** |
| 2 | `conceptual_synthesis` origin might be mistaken for mechanism evidence. | P2 | Quantity boundary | Keep evidence origin separate from method and require explicit support/non-support claims; identity grants no admission. **Resolved.** |
| 3 | ORBIT has no product artifact or dependency in the pulse. | P3 | Scope inspection | Review again only when comparison identity is actually proposed. **Accepted.** |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 16  |  P3 notes: 8

Verdict: APPROVED-WITH-CONDITIONS

Top finding: every immutable identity and diagnostic construction path must
enforce the same exact grammar, safe context, and non-authority boundary.

Cross-role consensus: do not normalize evidence identity, collapse support
axes, echo rejected input, or let a foundational vocabulary imply scientific,
accessibility, comparison, validation, or release success.
```

All 16 P2 findings are repaired in the reviewed candidate. The remaining
conditions are closeout evidence: commit these exact bytes as the single 001-A
rollback unit, rerun the controlled gates on that commit, record manifests and
limitations, and stop before 001-B.

## Evidence inspected

- Focused suite: 19 tests pass, including exact allocation, constructor bypass,
  path aliasing, immutability, unknown values, orthogonal support, stale review,
  authority, and secret/redaction cases.
- Full pytest: 477 tests and its parameterized subtests pass.
- Independent unittest discovery: 346 tests pass.
- Compile, browser syntax, diff hygiene, and candidate before/after manifests
  pass; manifest remained `8e7f56775c30318c03ebb77d6cb85b314bf2cc96`.
- Network denial was not enforced and is not claimed as VFY-OSW-019.

## Amendments

1. Closed exact construction paths and canonical repository artifact identity.
2. Preserved independent support axes, claim limits, and non-authority fields.
3. Added exact allocation, mutation/bypass, redaction, aliasing, size, tool, and
   non-mutation evidence without adding a dependency.

Fixed-point decision: `pass_with_risk` for the exact WP-OSW-001A candidate.
It may be committed as the one implementation rollback unit, then must pass
commit-bound closeout. No 001-B work, push, merge, deployment, validation,
release, external contact, or cross-repository change is authorized.

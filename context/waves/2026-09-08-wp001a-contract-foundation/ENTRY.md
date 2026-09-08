---
wave: 2026-09-08-wp001a-contract-foundation
work_package: WP-OSW-001
pulse: 001-A
date: 2026-09-08
status: ready_at_native_role_fixed_point
entry_decision: pass_with_risk
---

# WP-OSW-001A Contract Foundation Entry

## Decision

This packet admits **WP-OSW-001 pulse 001-A only** for implementation on the
exact baseline below. The pulse may establish the diagnostic registry and
closed identity vocabularies with local fixtures. It must stop for a separate
closeout and 001-B entry decision.

This packet authorizes no adapter migration, federated admission, scientific
calculation, atlas rendering, public-state change, external acquisition,
validation session, push, merge, deployment, release, or cross-repository
change.

## Immutable entry basis

| Field | Value |
|---|---|
| Repository | OSW — Ocean States of the World |
| Branch | `atlas-08-private-preview` |
| Baseline commit | `da7b463a2720794bbe9baa43a55924d3be9bbb3c` |
| Baseline tree | `202342e3ffde0ee0dfc5d5eade1eab7277debf8e` |
| Tracked-index manifest | `fd84b77674b353acca30e89e4669cf537f525027` |
| Final Review SHA-256 | `09A5A462A8DE0EA0F3F646DE62E8771A5D50D90FC0E4FC8EC8B5D16ED2467CF3` |
| Entry worktree state | clean before this packet was created |
| Runtime | Python 3.14.2; Node v22.22.3; Windows / PowerShell |
| Network claim | ordinary local environment; outbound denial was not enforced |

The initial Git tree probe used an unquoted `HEAD^{tree}` in PowerShell and
failed as a metadata command. It changed no files and did not affect pytest.
The corrected quoted command produced the tree identity recorded above. This
diagnostic is retained rather than silently omitted.

## Baseline L1 receipt

| Check | Time (America/Los_Angeles) | Result | Boundary |
|---|---|---|---|
| `python -m pytest analysis -q` | 2026-09-08 07:12:19–07:15:03 | pass — 458 tests, 10 subtests | Current baseline only; not target VFY proof. |
| `python -m unittest discover -s analysis -p "test_*.py"` | 2026-09-08 07:15:14–07:16:24 | pass — 327 tests | Independent discovery runner. |
| `python -m compileall -q analysis` | 2026-09-08 07:16:34 | pass | Current Python syntax. |
| `node --check atlas/app.js` | 2026-09-08 07:16:34 | pass | Current integration-shell syntax. |
| `git diff --check` | 2026-09-08 07:16:34 | pass | Clean immutable entry state. |
| `git status --porcelain=v1` | 2026-09-08 07:16:34 | pass — zero entries | Before packet creation. |

This receipt refreshes the VFY-OSW-001 current-baseline observation. It does
not pass VFY-OSW-002–020. In particular, it is not VFY-OSW-019 because network
denial was not enforced, and it is not VFY-OSW-020 because the controlled
sentinel/ignored-path/temporary-output protocol has not executed.

## Controlled parents

| Family | IDs admitted for this pulse |
|---|---|
| Work | WP-OSW-001 pulse 001-A |
| Requirements | REQ-OSW-006, REQ-OSW-011, REQ-OSW-013, REQ-OSW-014, REQ-OSW-016, REQ-OSW-026, REQ-OSW-027, REQ-OSW-029 |
| Specifications | SPEC-OSW-011, SPEC-OSW-012, SPEC-OSW-017, SPEC-OSW-018, SPEC-OSW-019, SPEC-OSW-020, SPEC-OSW-021, SPEC-OSW-022, SPEC-OSW-033, SPEC-OSW-034, SPEC-OSW-035, SPEC-OSW-036 |
| Interfaces | IF-OSW-003, IF-OSW-007, IF-OSW-009, IF-OSW-010, IF-OSW-012, IF-OSW-013 |
| Design | DES-OSW-005, DES-OSW-006, DES-OSW-007, DES-OSW-008, DES-OSW-011, DES-OSW-012, DES-OSW-014, DES-OSW-015 |
| Rigor | CR-OSW-001–013, CR-OSW-019, CR-OSW-021–025 |
| Pitfalls | SI-01, SI-02, SI-03, DN-01, DN-02, CA-01, CA-02, DL-01, DL-02, DL-03 |
| Target verification | VFY-OSW-002, VFY-OSW-005, VFY-OSW-012, VFY-OSW-013; pulse-local portions only, all remain pending until executed |
| Candidate fixtures | FIX-OSW-001, FIX-OSW-002, FIX-OSW-005, FIX-OSW-018; identity/diagnostic subsets only |

The full WP-OSW-001 parent set remains controlling. The narrower list above
identifies the meanings 001-A may implement; it cannot retire or reinterpret
the remaining package parents.

## Frozen vocabulary surface

001-A may encode, but not widen, the controlled meanings already defined in
Interfaces:

- quantity classes and their explicit identity fields;
- orthogonal `geometry_support`, `data_status`, and `surface_condition` axes;
- exactly-one lifecycle state;
- immutable review/artifact identity and stale-review disposition;
- generated-artifact family identity/class and explicit unavailable fields; and
- the 18 diagnostic codes allocated in `INTERFACES.md`, with stable code,
  owning interface, safe field-local context, and required disposition.

An unknown value is rejected or represented as an explicit bounded
unknown/unavailable state where its parent contract permits. It is never
silently coerced into a known identity.

## Owned and prohibited mutations

| Class | Declared path | Expected mutation |
|---|---|---|
| Product code | `analysis/osw_diagnostics.py` | New pure registry, safe envelope, uniqueness and lookup behavior. |
| Product code | `analysis/osw_contracts.py` | New closed identity types/validators required by 001-A only. |
| Tests | `analysis/test_osw_contracts.py` | New focused positive, negative, duplicate, unknown, ordering, and redaction tests. |
| Fixtures | `analysis/fixtures/osw-contracts/` | New small invented JSON/text fixtures containing no real secret or provider payload. |
| Execution evidence | this wave directory and `signals/roles/check/` | Entry, pulse evidence, and native-role review records. |

No existing receipt, research result, generated figure, atlas asset, public
page, source register, preview/release status, citation, workflow, dependency
manifest, or external repository is an owned mutation. A different product path
requires an amended entry packet before editing.

The pulse adds no runtime/build/test dependency by default. Any proposed tool
or dependency first receives the WAIVER-OSW-003 bakeoff: defect signal, overlap
with existing checks, configuration/churn, maintenance, version/license, and
missing-tool behavior. Adoption requires a separate recorded decision; absence
of a new tool does not waive the contract tests.

## Invariants and negative cases

| Invariant | Required failure evidence |
|---|---|
| Diagnostic code identity is unique and deterministic. | Duplicate/unknown code fails with no partial registry. |
| Envelopes contain bounded safe context only. | Token, credential, signed-URL, oversized response, and arbitrary object cases are rejected/redacted without echo. |
| Exact identities do not alias after normalization. | Case/whitespace/type-confusable candidates remain distinct or fail explicitly according to the frozen grammar. |
| Support axes remain orthogonal. | Valid subsurface-under-ice remains ocean + valid + sea ice; land/missing/ice cannot substitute for one another. |
| Lifecycle state is exactly one controlled value. | Missing, multiple, and unknown lifecycle states fail. |
| Review credit binds exact artifact bytes. | Missing or changed SHA-256 yields `OSW-REVIEW-STALE`; no authority transfers. |
| Family identity is explicit and non-authoritative. | Unknown family/class or unavailable required identity blocks the affected record without rewriting source. |
| Registry/validator code has no ambient effects. | Imports and focused tests cause no network, filesystem write, environment mutation, logging initialization, or product-state change. |

## Rigor, waivers, and stop rules

Profiles: `PY`, `DATA`, `MULTI`; L0 during implementation, full L1 plus
pulse-specific evidence at closeout. New hand-authored functions follow the
60-line soft cap and 100-line hard review trigger. Complex decisions are pure
and decomposed; exact identities use exact comparison; order is deterministic.

- WAIVER-OSW-001 is not applicable because `atlas/app.js` is not owned.
- WAIVER-OSW-002 remains open; 001-A does not adapt historical families.
- WAIVER-OSW-003 is active and receives the declared tool bakeoff.
- WAIVER-OSW-004 and WAIVER-OSW-005 remain unrelated and open.
- WAIVER-OSW-006 triggers only if an existing oversized Python function is
  touched; no such function is currently owned.

Stop immediately on any diagnostic collision, ambiguous/aliased identity,
secret disclosure, lossy source representation, collapsed support axis,
nondeterminism, hidden dependency or ambient I/O, undeclared path mutation,
test-driven candidate repair, stronger scientific/release claim, or unresolved
P1/P2 finding. Rollback is the single 001-A implementation commit; no historical
artifact is rewritten.

## Closeout evidence contract

Before 001-A can close, record:

1. exact implementation commit and before/after tree manifests;
2. changed functions, sizes/branches, dependency/tool decision, and waivers;
3. applicable L0 and full L1 command receipts;
4. focused identity/diagnostic tests, mutation/adversarial cases, and redaction
   inspection mapped to the controlled parents above;
5. explicit status for every candidate VFY/FIX subset without promoting the
   unimplemented remainder;
6. CURRENT, SOUNDER, KEEL, and LOGBOOK decisions, plus CHART/HARBOR/ORBIT for
   the vocabulary they inspect; and
7. a separate closeout decision followed by a hard stop before 001-B.

## Entry result

Decision: `pass_with_risk` for WP-OSW-001 pulse 001-A implementation only.
The immutable baseline and ordinary L1 checks pass; controlled network-denial,
non-mutation, target contract evidence, Validation, and release remain pending
or blocked exactly as their parent plans state.

## Source links

- [Final VTRACE Review](../../../docs/vtrace/REVIEW.md)
- [Work Packages](../../../docs/vtrace/WORK_PACKAGES.md)
- [Verification Plan](../../../docs/vtrace/VERIFICATION.md)
- [Interfaces](../../../docs/vtrace/INTERFACES.md)
- [Code Rigor](../../../docs/vtrace/CODE_RIGOR.md)
- [PITFALL register](../../../design/pitfalls/README.md)
- [Native roles](../../../.roles/ROLE.md)
- [Entry roles check](../../../signals/roles/check/wp001a-entry-roles-check-2026-09-08.md)

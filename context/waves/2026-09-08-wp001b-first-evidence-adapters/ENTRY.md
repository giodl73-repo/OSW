---
wave: 2026-09-08-wp001b-first-evidence-adapters
work_package: WP-OSW-001
pulse: 001-B
date: 2026-09-08
status: ready_at_native_role_fixed_point
entry_decision: pass_with_risk
---

# WP-OSW-001B First Evidence Adapters Entry

## Decision

This packet admits **WP-OSW-001 pulse 001-B only**: pure, versioned,
meaning-preserving adapters for exactly three existing D-series research
records. The candidate families are D12 surface forcing, D13 fixed-column
storage, and D14 horizontal advection/partial-budget screening because they are
the quantitative bridge needed by the planned guided event anatomy.

The native-role review linked below has reached a fixed point. Adapter
implementation may begin only after these exact packet and review bytes are
committed. The pulse must stop for a separately reviewed closeout before 001-C
or any reader, map, scene, or release work.

## Immutable entry basis

| Field | Value |
|---|---|
| Repository | OSW — Ocean States of the World |
| Branch | `atlas-08-private-preview` |
| Baseline commit | `1bdfbc31d14cfd1092d8c5a1216e5764d34f4392` |
| Baseline tree | `b2de0a29433fe343fdf62a5f46004d29b08d32cc` |
| Tracked-index manifest | `e077d58c4b5f4dd544727f81c68ff2aed8030e57` |
| Tracked files | 878 |
| Final Review SHA-256 | `09A5A462A8DE0EA0F3F646DE62E8771A5D50D90FC0E4FC8EC8B5D16ED2467CF3` |
| 001-A implementation | `f203e437f23141b4bf535c0ae731430a0e704873` |
| 001-A closeout | `1bdfbc31d14cfd1092d8c5a1216e5764d34f4392` |
| Entry worktree state | clean before this packet was created |
| Runtime | Python 3.14.2; Node v22.22.3; Windows / PowerShell |
| Network claim | ordinary local environment; outbound denial was not enforced |

The baseline is also the pushed remote branch tip. That publication of the
already closed 001-A work does not authorize a later push, merge, deployment,
release, or cross-repository change.

## Baseline L1 receipt

All commands ran with Python bytecode and pytest cache creation disabled.

| Check | Time (America/Los_Angeles) | Result | Boundary |
|---|---|---|---|
| `python -m pytest analysis -q` | 2026-09-08 09:29:00–09:30:58 | pass — 477 tests, 36 subtests | Existing baseline only; not adapter proof. |
| `python -m unittest discover -s analysis -p "test_*.py"` | 2026-09-08 09:30:58–09:31:37 | pass — 346 tests | Independent discovery runner. |
| `python -m compileall -q analysis` | 2026-09-08 09:31:37 | pass | Existing Python syntax. |
| `node --check atlas/app.js` | 2026-09-08 09:31:37 | pass | Existing browser-shell syntax. |
| `git diff --check` | 2026-09-08 09:31:37 | pass | Clean immutable entry basis. |
| `git status --porcelain=v1` | 2026-09-08 09:31:37 | pass — zero entries | Before packet creation. |

This refreshes only the current-baseline observation. VFY-OSW-002–020,
Validation, and release remain pending, blocked, or unauthorized as recorded.

## Frozen historical-family inventory

Only these exact source bytes may be read by 001-B adapters:

| Family | Historical schema | Path | Bytes | SHA-256 |
|---|---|---|---:|---|
| D12 | `osw.ocean-object-gfs-surface-flux-screen.v1` | `research/osw-d12-gfs-surface-flux-screen-2026.json` | 320827 | `D3D9627319179EB1D6CD5A2D3BBEE1DA03FE431A04C96C31A71740C027DF7666` |
| D13 | `osw.ocean-object-rtofs-upper-ocean-storage-screen.v1` | `research/osw-d13-rtofs-mhw-upper-ocean-storage-2026.json` | 195250 | `E418B2B5BCCCBB5AFD8CC4CCE29EF504652DBE38CB04C85B0805D0DBF9AFBC27` |
| D14 | `osw.ocean-object-rtofs-upper-ocean-advection-screen.v1` | `research/osw-d14-rtofs-mhw-upper-ocean-advection-2026.json` | 217931 | `9DE6E342CEA1630767E04B1620DEBE643B64E9E3C9F8A1FC70582CAA30290672` |

The three records share a broad top-level shape but remain three distinct
families. D13 refers to D12 comparison evidence; D14 combines D13 storage and
D12 forcing with its own RTOFS advection diagnostic. The adapter must preserve
those identities and must not flatten them into one purported native budget.
Referenced D11, source payload, and provider records remain opaque source
identities: 001-B neither recursively adapts them nor implies that their
provenance fields are complete.

No D1–D11, motion, M2/M3/M4, atlas-data, receipt, SVG, or source-acquisition
family is admitted by this inventory. Adding even one source family requires
an amended entry and new role decision.

## Controlled parents

| Family | IDs admitted for this pulse |
|---|---|
| Work | WP-OSW-001 pulse 001-B |
| Requirements | REQ-OSW-006–016, REQ-OSW-026–029 |
| Specifications | SPEC-OSW-011–024, SPEC-OSW-033–036 |
| Interfaces | IF-OSW-003, IF-OSW-007, IF-OSW-009, IF-OSW-011, IF-OSW-012 |
| Design | DES-OSW-005, DES-OSW-006, DES-OSW-008, DES-OSW-011, DES-OSW-012, DES-OSW-014, DES-OSW-015 |
| Rigor | CR-OSW-001–013, CR-OSW-019, CR-OSW-021–025 |
| Pitfalls | SI-01–03, DN-01–02, CA-01–02, DL-01–03 |
| Target verification | VFY-OSW-002, VFY-OSW-005, VFY-OSW-012, VFY-OSW-013, VFY-OSW-020; pulse-local subsets only |
| Candidate fixtures | FIX-OSW-001, FIX-OSW-002, FIX-OSW-005, FIX-OSW-018, FIX-OSW-020; adapter subsets only |

IF-OSW-010 federated admission is deliberately excluded. Adapter success
means only that a historical record can be represented without semantic loss;
it does not make that record admitted, publishable, validated, or authoritative.

## Authorized result

001-B may add a pure adapter seam that:

1. recognizes only the three exact historical schema IDs above;
2. checks source path and SHA-256 identity before adaptation;
3. binds the raw-byte SHA-256 and preserves every parsed source field and value
   in an immutable canonical representation suitable for semantic round-trip
   comparison;
4. emits a versioned in-memory evidence-envelope candidate with explicit
   provenance, quantity identity, support axes, transformation lineage, claim
   ceiling, checks, and unavailable-field reasons;
5. keeps source, derived diagnostic, comparison, and unresolved remainder
   identities separate across D12, D13, and D14;
6. represents geometry support, data status, and surface condition as
   orthogonal axes without manufacturing cell-level metadata absent upstream;
7. returns stable diagnostics instead of repairing malformed, unknown,
   mismatched, or mutated candidates; and
8. performs no filesystem writes, network calls, provider acquisition,
   scientific recalculation, rendering, logging initialization, or ambient
   environment mutation.

“Lossless” means the raw-byte identity remains bound and the accepted parsed
JSON tree can be reproduced without field/value/order loss. It does not mean
that whitespace or numeric lexemes are regenerated from the parsed tree, or
that absent modern-envelope fields can be recovered. Such fields remain
explicitly unavailable with a field-local reason and a corresponding claim
restriction.

## Owned and prohibited mutations

| Class | Declared path | Expected mutation |
|---|---|---|
| Product code | `analysis/osw_adapters.py` | New pure version dispatch, source-identity checks, lossless snapshots, and D12/D13/D14 adapters. |
| Product code | `analysis/osw_contracts.py` | Minimal additive adapter-envelope types only if the 001-A identities cannot express the reviewed contract. |
| Tests | `analysis/test_osw_adapters.py` | Focused preservation, version, mutation, missingness, support, and no-effect tests. |
| Fixtures | `analysis/fixtures/osw-adapters/` | Small invented positive/negative records plus checksum-pinned references to the three committed families. |
| Execution evidence | this wave directory and `signals/roles/check/` | Entry, implementation, closeout, and native-role review records. |

The three historical JSON files are read-only inputs and must remain byte-for-
byte unchanged. Their generators, source payloads, figures, public receipts,
`SOURCE-REGISTER.md`, atlas files, README/status/citation files, workflows,
dependencies, and external repositories are not owned. Derived sidecars and
rewritten receipts are prohibited in 001-B; adapter output remains in memory or
inside invented test fixtures.

## Adapter and fixture contract

| Required case | Required evidence |
|---|---|
| Golden family | Each pinned D12/D13/D14 record dispatches to exactly one adapter and retains its schema, detection ID, source-artifact array, method, interval/map payloads, evaluation, next evidence, and boundary. |
| Round trip | Canonical serialization of the preserved source snapshot reproduces the parsed source structure and values; source-byte SHA-256 remains separately bound. |
| Unknown fields | Invented nested scalar, array, object, and explicit `null` survive adaptation and round trip without becoming authority. |
| Parser ambiguity | Duplicate object names, non-finite numbers, invalid encoding, and trailing data fail before dispatch; no last-key-wins or repair behavior is allowed. |
| Unavailable fields | Missing provider version, license, acquisition query, uncertainty, mask mapping, or surface condition receives an explicit field path, reason, and claim restriction; no default is invented. |
| Mutation | Changed source bytes, schema, detection ID, unit, sign/reference, boundary, source linkage, interval support, or nested array order fail with a stable diagnostic. |
| Orthogonal support | A valid subsurface-under-ice case remains ocean + valid + sea ice; source-absent cell axes remain unavailable, never inferred from map values or zero/null. |
| Cross-system ceiling | D12–D14 remain diagnostic comparisons; no adapter labels their arithmetic a native closure, measured convergence, vertical process, or causal attribution. |
| No source rewrite | Hashes and tracked content of all three inputs are identical before and after focused/full tests. |
| Ambient effects | Import and adapter execution perform no network, filesystem write, environment mutation, logging setup, or atlas/research state change. |

The adapter may derive envelope metadata only through explicit deterministic
rules reviewed in its family mapping table. It may traverse D12–D14's embedded
source-reference objects but must not open their paths or fetch their URLs. A
value requiring scientific interpretation rather than structural mapping is
unavailable until a later domain validator or scientific work package decides
it.

## Diagnostics, failure, and determinism

Failures use the 001-A registry. At minimum, checksum, schema, unit, sign,
mask/support, time-support, family-integrity, unsafe-diagnostic, and unknown-
value mismatches must remain distinguishable. A failed adapter returns no
partially accepted envelope and never includes source payload fragments or
sensitive values in diagnostic context.

The parser must use UTF-8 JSON with duplicate-name detection and must reject
non-finite numbers and trailing content before schema dispatch. Exact source
numbers retain their JSON numeric value; tests include large integers and
decimal/exponent spellings whose parsed values must not drift.

Dispatch order, unavailable-field order, preserved-field traversal, and
canonical serialization are deterministic. Exact IDs are not case-folded,
trimmed, path-normalized, guessed from filenames, or selected by structural
similarity.

## Rigor, waivers, and stop rules

Profiles: `PY`, `DATA`, `MULTI`; L0 during implementation, full L1 plus
pulse-specific evidence at closeout. New functions retain the 60-line soft cap
and 100-line hard review trigger. The pulse adds no dependency; the 001-A tool
bakeoff remains controlling unless adapter complexity triggers its recorded
revisit criteria.

- WAIVER-OSW-001 is not applicable because `atlas/app.js` is not owned.
- WAIVER-OSW-002 is active and may close only for these three exact adapter
  families after preservation and no-rewrite evidence passes.
- WAIVER-OSW-003 reopens only if a new tool/dependency is proposed.
- WAIVER-OSW-004/005 remain unrelated and open.
- WAIVER-OSW-006 triggers if an existing oversized function is touched.

Stop immediately on lossy adaptation, source mutation, inferred scientific
metadata, collapsed support axes, cross-system closure language, ambiguous
dispatch, nondeterminism, secret disclosure, ambient I/O, undeclared path
mutation, new dependency without review, or unresolved P1/P2 finding. Rollback
is one implementation commit; it never includes reverting historical evidence.

## Closeout evidence contract

Before 001-B can close, record:

1. exact entry and implementation commits, trees, manifests, and every changed
   file hash;
2. a family mapping table naming every mapped and unavailable envelope field;
3. golden, preservation, round-trip, unknown-field, unavailable-field,
   mutation, orthogonal-support, cross-system ceiling, diagnostic-safety, and
   ambient-effect results;
4. before/after SHA-256 for the three historical inputs plus tracked-tree and
   declared-temporary-output inspection;
5. applicable L0 and full L1 command receipts, metrics, dependency decision,
   and waiver dispositions;
6. honest pulse-local VFY/FIX status without promoting 001-C admission,
   Validation, reader, map, release, or scientific evidence; and
7. all eight native role decisions followed by a hard stop before 001-C.

## Entry result

Decision: `pass_with_risk` for WP-OSW-001 pulse 001-B implementation only. The
clean immutable baseline, current offline checks, and native-role entry review
pass. Adapter behavior does not yet exist, no target VFY item is claimed, and
all later pulses and external/release effects remain blocked.

## Source links

- [001-A closeout](../2026-09-08-wp001a-contract-foundation/CLOSEOUT.md)
- [Final VTRACE Review](../../../docs/vtrace/REVIEW.md)
- [Work Packages](../../../docs/vtrace/WORK_PACKAGES.md)
- [Verification Plan](../../../docs/vtrace/VERIFICATION.md)
- [Interfaces](../../../docs/vtrace/INTERFACES.md)
- [Code Rigor](../../../docs/vtrace/CODE_RIGOR.md)
- [PITFALL register](../../../design/pitfalls/README.md)
- [Native roles](../../../.roles/ROLE.md)
- [Entry roles check](../../../signals/roles/check/wp001b-entry-roles-check-2026-09-08.md)

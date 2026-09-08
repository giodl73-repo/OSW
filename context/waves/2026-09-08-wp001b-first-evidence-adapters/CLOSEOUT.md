---
wave: 2026-09-08-wp001b-first-evidence-adapters
work_package: WP-OSW-001
pulse: 001-B
date: 2026-09-08
status: closed_with_risk
decision: pass_with_risk
implementation_commit: acb6145810e66653fd0d6f6b0b7e340664ac2526
---

# WP-OSW-001B First Evidence Adapters Closeout

## Decision

WP-OSW-001 pulse 001-B is closed at its exact implementation commit. It
delivers pure, versioned adapter candidates for the three frozen D12–D14
families without rewriting source evidence or promoting any candidate through
federated admission.

Decision: `pass_with_risk` for 001-B only. WP-OSW-001 remains open until 001-C
implements domain admission and the complete admitted-family inventory.

## Immutable implementation identity

| Field | Value |
|---|---|
| Entry commit | `29b7c47` |
| Entry amendment commit | `762ed5c5f2ce699a1993ef16bf1d9bde8aa5aa72` |
| Implementation commit | `acb6145810e66653fd0d6f6b0b7e340664ac2526` |
| Implementation tree | `beaa3a3c1eb5cb0bd0900dcb441d2111a07aee3e` |
| Tracked-index manifest | `0500633f17e5d29e910763568cceade6c672b1d1` |
| Tracked files | 889 |
| Worktree at commit gate | clean |
| Runtime | Python 3.14.2; Node v22.22.3; Windows / PowerShell |
| Network boundary | adapter accepts caller bytes and performs no network operation; enforced process-wide denial remains pending VFY-OSW-019 |

## Delivered surface

| Artifact | SHA-256 | Result |
|---|---|---|
| `analysis/osw_contracts.py` | `6EFF5CA12863369E50A8DB5A4D149C477D184F23DBD450BFC6047759659664CA` | Adds the reviewed `surface_heat_flux` quantity class. |
| `analysis/osw_adapters.py` | `0CA31ABDC346BB8E9E9AE589526ABAAC7FDBBBA45222BD294253065D649EF209` | Strict immutable JSON, exact three-family registry, adapter candidates, unavailable fields, and explicit support helper. |
| `analysis/test_osw_adapters.py` | `A05AB12E40354860C797B7073243B570A42304603AEC6C6AE64E1AD12D3FD270` | Sixteen focused tests with adversarial subtests. |
| `strict-valid.json` | `6DD0A6A0C994327B0C8A31F16ACEC40889E28546F57D16DE82D11851216EF607` | Invented unknown/null/order/number preservation fixture. |
| `invalid-duplicate.json` | `5D9CF41F8CCCACF473CE552466F315D7F1F70624BEFA382428F45F2715A8AAAB` | Invented duplicate-name rejection fixture. |
| `invalid-nonfinite.json` | `2BC91A179478B20DE6EC239AE8B6FCB2FE2695C2BF4DBA15B34E0249755F6F47` | Invented non-finite-number rejection fixture. |
| `family-bindings.json` | `259523C539FC7535719A6CBEF14A10C523E1F1FA83BE7C853F763F89779B5971` | Exact ordered family binding and orthogonal-support fixture. |
| Implementation roles check | `3AF31D4BA21D4F8BE49509B259DFDB5448E8CB3E185A2372D7186CF3F826E00B` | Eight roles; zero P1 and all P2 repaired. |

No historical receipt, research result, source payload, figure, atlas file,
public status/citation, dependency, workflow, or external repository changed.

## Frozen-family result

| Candidate | Principal mapped quantity | Source references | Explicit unavailable fields | Admission |
|---|---|---:|---:|---|
| D12 | `surface_heat_flux` at the air–sea boundary; positive downward | 3 | 18 | false |
| D13 | fixed 0–50 m `storage_tendency`; positive heat gain | 2 | 18 | false |
| D14 | depth-integrated `horizontal_advection`; positive warming contribution | 3 | 18 | false |

D12's mixed-layer temperature conversions, D13's crossed-system surface-flux
comparison, and D14's crossed-system residual remain present in the immutable
source snapshot but do not receive manufactured complete quantity identities.
D14 remains offline advection, not native tracer flux or conservative
convergence. None of the three candidates establishes closure or causation.

## Source custody and preservation

| Historical input | SHA-256 before and after |
|---|---|
| `research/osw-d12-gfs-surface-flux-screen-2026.json` | `D3D9627319179EB1D6CD5A2D3BBEE1DA03FE431A04C96C31A71740C027DF7666` |
| `research/osw-d13-rtofs-mhw-upper-ocean-storage-2026.json` | `E418B2B5BCCCBB5AFD8CC4CCE29EF504652DBE38CB04C85B0805D0DBF9AFBC27` |
| `research/osw-d14-rtofs-mhw-upper-ocean-advection-2026.json` | `9DE6E342CEA1630767E04B1620DEBE643B64E9E3C9F8A1FC70582CAA30290672` |

Each candidate retains immutable raw bytes, verifies their SHA-256, and binds
them to a recursively frozen parsed tree. Canonical semantic serialization
preserves object/array order, unknown fields, explicit nulls, strings, booleans,
and numeric lexemes. Embedded paths and URLs remain opaque and are never opened.

## Modern-envelope availability map

| Group | Mapped in 001-B | Explicitly unavailable or deferred |
|---|---|---|
| Identity | source path/hash, schema, D-series ID, family/version, research-intake lifecycle | federated admission and release identity |
| Source | opaque source-artifact paths/hashes/roles | provider, product/version, URL, citation, license, redistribution |
| Acquisition | interval evidence retained in source | query and acquisition timestamp |
| Quantity | one principal quantity per family with unit, dimension, time/depth/space, sign/reference, operator, origin/method, ceiling | secondary conversions/comparisons and mixed-origin residual identity |
| Support | record-level time/depth/space wording; explicit three-axis helper | cell geometry/data/ice state, mask map, exact bounds/order/longitude convention, uncertainty |
| Transformation | historical method and all inputs retained losslessly | new scientific recomputation or domain acceptance |
| Claim | exact historical boundary and principal claim ceiling | closure, causation, native-flux, and stronger interpretations |
| Checks | source SHA-256, exact schema/path/detection registry, semantic anchors, reference/time checks | 001-C domain composition and full family admission |

## Verification evidence

Commit-bound commands ran on clean commit `acb6145` with bytecode and pytest
cache generation disabled.

| Check | Time (America/Los_Angeles) | Result |
|---|---|---|
| Focused adapter + 001-A contracts | pre-commit exact bytes and post-correction | pass — 35 tests, 50 subtests |
| `python -m pytest analysis -q` | 2026-09-08 10:54:48–10:56:55 | pass — 493 tests, 60 subtests |
| `python -m unittest discover -s analysis -p "test_*.py"` | 2026-09-08 10:56:55–10:57:38 | pass — 362 tests |
| `python -m compileall -q analysis` | 2026-09-08 10:57:38 | pass |
| `node --check atlas/app.js` | 2026-09-08 10:57:38 | pass |
| `git diff --check` | 2026-09-08 10:57:39 | pass |
| `git status --porcelain=v1` | 2026-09-08 10:57:39 | pass — zero entries |

The tests cover strict UTF-8 JSON, duplicate names, non-finite and oversized
input, trailing content, immutable construction, exact inventory, raw/semantic
round trip, source-reference opacity, ambient effects, schema/detection/status/
source/time/sign/reference/checksum mutations, orthogonal support, explicit
unavailability, quantity ceilings, and no source rewrite.

## Rigor and failure history

- All implementation imports are standard library or local OSW modules.
- No dependency, tool configuration, network client, file writer, logger,
  environment mutation, public renderer, or admission engine was introduced.
- New functions top out at 54 physical lines; Python/fixture files have zero
  lines over 120 characters.
- WAIVER-OSW-002 closes only for these three pinned adapter candidates; the
  repository-wide historical-family inventory remains open for 001-C.
- WAIVER-OSW-003 remains satisfied by the no-new-tool decision; other waivers
  are unchanged.

The first focused run produced 15 failures because nested lists reached frozen
object validation before recursive conversion. The correction separated
duplicate-name collection from recursive freezing; subsequent focused and full
runs pass. Later review hardening added byte/tree revalidation, explicit
support/provenance gaps, size/recursion guards, registry uniqueness, and direct-
constructor binding. Failed evidence remains recorded rather than relabeled.

## Evidence disposition

- Pulse-local portions of VFY-OSW-002, 005, 012, 013, and 020 pass for the
  three frozen adapter candidates; every full VFY item remains pending.
- IF-OSW-010 domain admission, complete family inventory, and role-veto
  composition remain 001-C work.
- All human/scientific Validation scenarios remain blocked.
- Reader, map, guided-scene, public-release, and planetary-comparison claims
  remain unimplemented or unauthorized.

## Result and next boundary

001-B is reversible as one implementation commit and closed with bounded risk.
The next package action is a separately reviewed 001-C entry proposal for pure
domain dispositions and the complete admitted-family inventory. Separately,
the owner has requested an Ocean Column State scientific definition; that work
must preserve the distinction between exhaustive reference addresses and
diagnosed physical layers and receive its own scope/review before product use.

No 001-C implementation, public atlas change, push, merge, deployment,
Validation, release, external contact, or cross-repository change is authorized
by this closeout.

## Source links

- [Entry](ENTRY.md)
- [Entry amendment](ENTRY-AMENDMENT-01.md)
- [Implementation roles check](../../../signals/roles/check/wp001b-implementation-roles-check-2026-09-08.md)
- [Closeout roles check](../../../signals/roles/check/wp001b-closeout-roles-check-2026-09-08.md)
- [Work packages](../../../docs/vtrace/WORK_PACKAGES.md)
- [Verification](../../../docs/vtrace/VERIFICATION.md)
- [PITFALL register](../../../design/pitfalls/README.md)

# OSW Verification Plan

Status: settled at native-role fixed point, 2026-09-07

## Scope

Repo: OSW — Ocean States of the World

This plan defines the executable evidence required to show that OSW conforms
to its settled requirements, interfaces, design invariants, code-rigor rules,
and proposed work-package contracts. It distinguishes:

- **baseline evidence**: commands or inspections executed against the current
  repository and recorded with an actual result; and
- **target evidence**: controlled commands, fixtures, or demonstrations that
  remain pending until the corresponding implementation exists.

Naming a target check is not evidence that it passes. Verification asks whether
the product was built to its contract. Whether people understand and benefit
from it, whether scientific generalization is persuasive, and which measured
performance/accessibility thresholds are acceptable belong to Validation.

No work package, implementation, merge, deployment, or release is authorized
by this plan.

## Verification rules

1. A verification result binds the immutable commit/artifact identities,
   command or inspection version, fixture identities, environment, result, and
   evidence path.
2. A target check stays `pending` until executed against implemented behavior.
   Absence, `unknown`, or unjustified `not_applicable` never becomes `pass`.
3. Tests and validators are read-only observers. They may write only to bounded
   temporary custody and must leave the candidate tree semantically unchanged.
4. Default L0/L1 verification is offline. Provider acquisition and hosted
   release rehearsals are explicit L2 effects with separate authority.
5. Failure is local to the affected optional capability or claim but closed for
   admission and release. The prior accepted artifact/view/release remains.
6. Full-byte comparison is used only when bytes are the contract; otherwise
   schema, identity, geometry, numeric, semantic, and rendering invariants are
   asserted explicitly.
7. A role review supplements executable evidence; it cannot replace a missing
   required test, grant scientific endorsement, or authorize release.

## Controlled verification matrix

| ID | Contract surface | Method | Controlled command / inspection | Expected evidence | State |
|---|---|---|---|---|---|
| VFY-OSW-001 | Current repository baseline | test / syntax / structure | L1 baseline command set below | Full default suite, syntax, links/tables/IDs, and diff check pass. | baseline passed 2026-09-07; network isolation not asserted |
| VFY-OSW-002 | Quantity, receipt, review, family, lifecycle, and compatibility contracts | test / mutation | `python -m unittest analysis.test_osw_contracts` | Golden and field-omission cases return stable dispositions/diagnostics; adapters preserve source identity and unavailable fields. | target pending |
| VFY-OSW-003 | Federated admission | exhaustive test / property analysis | `python -m unittest analysis.test_osw_admission` | Every required-domain combination passes only when all required domains pass; no veto override. | target pending |
| VFY-OSW-004 | Quantity, budget, motion, claim ceiling | analysis / negative test | `python -m unittest analysis.test_osw_claim_boundaries` | Invalid quantity labels, residual-as-process, near-closure, motion-as-delivery, and authority claims are rejected. | target pending |
| VFY-OSW-005 | Geometry, data status, surface condition, mismatch propagation | property / rendering test | `python -m unittest analysis.test_osw_support_contract` | All axes remain orthogonal; mismatch stops the affected claim; valid subsurface-under-ice remains valid and separately annotated. | target pending |
| VFY-OSW-006 | Acquisition and accepted custody | fault injection / hash comparison | `python -m unittest analysis.test_osw_acquisition_contract` | Timeout, checksum, schema, rights, and identity failures preserve accepted bytes and emit redacted diagnostics. | target pending |
| VFY-OSW-007 | Canonical URL/reader state | state-machine / compatibility test | `node --test analysis/js/state.test.mjs analysis/js/state-compatibility.test.mjs` | Current/legacy/unknown/conflicting/direct/history/reset transitions commit one URL/visual/focus/programmatic/announcement state or preserve the prior state. | target pending; URL policy discovery required |
| VFY-OSW-008 | Routes and guided scenes | registry / mutation / navigation test | `node --test analysis/js/routes.test.mjs analysis/js/scenes.test.mjs`; `python -m unittest analysis.test_atlas analysis.test_guides` | Exactly three entrances; complete ordered scenes; bound finding/limitation/receipt; broken or mutated value paths block scene admission. | target pending; existing Python coverage passes partially |
| VFY-OSW-009 | Map/view-model contract | schema / geometry / equivalence test | `node --test analysis/js/view-model.test.mjs`; `python -m unittest analysis.test_atlas` | Admitted family metadata is complete; visual/text digests agree; land/seam/pole/support/boundary/comparison rules hold. | target pending; existing atlas coverage passes partially |
| VFY-OSW-010 | Keyboard, focus, non-color, motion, and equivalent text | automated inspection / browser demonstration | State tests plus controlled Edge/Chrome/Firefox keyboard, zoom, reduced-motion, and assistive-technology matrix | Every primary action is operable and all channels expose the same finding and limitation without unexpected focus movement. | target pending; human thresholds in Validation |
| VFY-OSW-011 | Selected payload, integrity, privacy, and performance instrumentation | request/storage trace / fault test | `node --test analysis/js/asset-manifest.test.mjs`; controlled browser request trace | Only declared same-origin selected assets load; integrity failure retains prior view; no account/upload/cookie/telemetry/storage; measurements emitted without invented budget. | target pending; budgets in Validation |
| VFY-OSW-012 | Generated artifact families | regeneration / integrity comparison | Family-registry commands declared by each admitted family plus `python -m unittest analysis.test_osw_family_registry` | Every admitted family has controlled inputs/dependencies/generator/comparison/update rule and representative mutation failure. | target pending |
| VFY-OSW-013 | External review and non-authority boundary | contract / content / secret inspection | Contract tests plus BEACON/LOGBOOK review and bounded secret/private-path scan | Review binds immutable artifact and disposition; forecast/navigation/intervention/endorsement/release authority language is absent; diagnostics are redacted. | target pending |
| VFY-OSW-014 | Heat-budget challenge/generalization | independent calculation / sensitivity / controls | Focused RTOFS/GFS/OISST storage/advection/flux tests named below plus new package-specific tests | Depth/time/product/control results retain distinct identities, tolerances, unresolved terms, contrary/null outcomes, and source receipts. | target pending; existing 0–50 m evidence tests pass |
| VFY-OSW-015 | Transport-tested zoning | analysis / negative scenario | Existing motion partition/region tests plus future `analysis.test_osw_zoning_scorecard` | Every diagnostic and unavailable/contrary result remains visible; attractive exchange-poor border cannot advance class. | target pending |
| VFY-OSW-016 | Planetary comparison | paired fixture / content review | Future `analysis.test_osw_planetary_comparison` plus CURRENT/SOUNDER/ORBIT review | Both quantities and regime differences resolve; resemblance-only case weakens/rejects mechanism claim. | target pending |
| VFY-OSW-017 | Lifecycle and release reconciliation | exhaustive drift / no-effect test | Future `python -m unittest analysis.test_osw_release_reconciliation` | Exactly-one lifecycle state; every mismatched surface produces hold; reconciliation makes no deployment/status/citation change. | target pending |
| VFY-OSW-018 | Hosted transition and retain/restore | staged fault demonstration / smoke | Host-specific command chosen after SPEC-OSW-039 discovery | Hosted commit and primary journeys match candidate; failed deploy/smoke preserves prior release and metadata. | discovery pending; cannot pass locally |
| VFY-OSW-019 | Network-disabled default gate and optional dependency isolation | environment fault test | Run L1 with outbound access denied; run declared missing-dependency fixtures | No scientific-provider request occurs; unavailable optional capability fails locally and unrelated atlas/tests pass. | target pending |
| VFY-OSW-020 | Verification non-mutation and temporary custody | before/after manifest / fault test | Hash tracked files and inventory untracked/ignored paths before and after each gate; compare against declared temporary outputs | Tests do not repair or regenerate accepted artifacts; undeclared residue is a failure; bounded temporary output is removed. | target pending |

## Requirement-to-verification coverage

Every accepted requirement is spelled out so orphan detection does not depend
on interpreting ranges.

| Verification IDs | Requirement IDs |
|---|---|
| VFY-OSW-007, VFY-OSW-008 | REQ-OSW-001, REQ-OSW-002, REQ-OSW-003, REQ-OSW-004, REQ-OSW-033 |
| VFY-OSW-004, VFY-OSW-005, VFY-OSW-009, VFY-OSW-015, VFY-OSW-016 | REQ-OSW-005, REQ-OSW-006, REQ-OSW-007, REQ-OSW-008, REQ-OSW-009, REQ-OSW-010, REQ-OSW-011 |
| VFY-OSW-002, VFY-OSW-004, VFY-OSW-005, VFY-OSW-006, VFY-OSW-012, VFY-OSW-013 | REQ-OSW-012, REQ-OSW-013, REQ-OSW-014, REQ-OSW-015, REQ-OSW-016, REQ-OSW-026, REQ-OSW-027, REQ-OSW-028, REQ-OSW-029 |
| VFY-OSW-009, VFY-OSW-010, VFY-OSW-011 | REQ-OSW-017, REQ-OSW-018, REQ-OSW-019, REQ-OSW-020, REQ-OSW-021, REQ-OSW-022, REQ-OSW-023, REQ-OSW-024, REQ-OSW-025 |
| VFY-OSW-011, VFY-OSW-013, VFY-OSW-017, VFY-OSW-018 | REQ-OSW-030, REQ-OSW-031, REQ-OSW-032, REQ-OSW-034 |

## Interface and invariant coverage

| Verification IDs | Interfaces | Principal invariants |
|---|---|---|
| VFY-OSW-007, 008 | IF-OSW-001, IF-OSW-002, IF-OSW-008 | INV-OSW-001–005, INV-OSW-020 |
| VFY-OSW-002, 004 | IF-OSW-003, IF-OSW-007 | INV-OSW-004–006, INV-OSW-009 |
| VFY-OSW-005, 009, 010 | IF-OSW-004, IF-OSW-009 | INV-OSW-001, INV-OSW-006–008 |
| VFY-OSW-003 | IF-OSW-010 | INV-OSW-012, INV-OSW-013 |
| VFY-OSW-006 | IF-OSW-011 | INV-OSW-009–011 |
| VFY-OSW-011, 012 | IF-OSW-006, IF-OSW-012 | INV-OSW-011, INV-OSW-012, INV-OSW-018 |
| VFY-OSW-013 | IF-OSW-013 | INV-OSW-015, INV-OSW-020 |
| VFY-OSW-016 | IF-OSW-014 | INV-OSW-016 |
| VFY-OSW-015 | IF-OSW-015 | INV-OSW-017 |
| VFY-OSW-017, 018 | IF-OSW-005 | INV-OSW-014, INV-OSW-019 |

Machine-expanded invariant inventory: INV-OSW-001, INV-OSW-002,
INV-OSW-003, INV-OSW-004, INV-OSW-005, INV-OSW-006, INV-OSW-007,
INV-OSW-008, INV-OSW-009, INV-OSW-010, INV-OSW-011, INV-OSW-012,
INV-OSW-013, INV-OSW-014, INV-OSW-015, INV-OSW-016, INV-OSW-017,
INV-OSW-018, INV-OSW-019, and INV-OSW-020.

## Controlled fixture catalog

Fixtures are target proof inputs until the named path exists and passes. Each
promoted fixture must record owner work package, parent contracts, inputs,
expected result/diagnostic/evidence, custody/redaction, stale behavior, and
update rule.

| Fixture ID | Class | Owner | Target path / content | Expected result |
|---|---|---|---|---|
| FIX-OSW-001 | golden | WP-OSW-001 | `analysis/fixtures/osw-contracts/quantity-receipt-valid.json` | Complete typed quantity/receipt passes required domains. |
| FIX-OSW-002 | negative matrix | WP-OSW-001 | one omitted/incompatible applicable field per contract | Stable field-local diagnostic; affected artifact not admitted. |
| FIX-OSW-003 | compatibility | WP-OSW-001 | historical receipt variants plus unknown fields | Lossless adapter preserves source and marks unavailable meaning. |
| FIX-OSW-004 | property matrix | WP-OSW-001 | all required-domain dispositions | Admission iff every required domain passes. |
| FIX-OSW-005 | cross-axis regression | WP-OSW-001/003 | ocean + valid + sea-ice subsurface value | Value remains valid; sea ice remains separately exposed. |
| FIX-OSW-006 | adversarial custody | WP-OSW-001 | timeout/checksum/schema/rights/secret-bearing response | Prior accepted bytes retained; diagnostic redacted. |
| FIX-OSW-007 | compatibility/state | WP-OSW-002 | current, legacy, unknown, conflicting and removed URLs | One usable accepted state and announced rejection. |
| FIX-OSW-008 | state failure | WP-OSW-002 | failed transition/loading/overlay | Prior state/view/focus retained with bounded announcement. |
| FIX-OSW-009 | scene mutation | WP-OSW-004 | missing/reordered scene and changed result path/value | Scene admission fails; no stale number appears. |
| FIX-OSW-010 | map/support matrix | WP-OSW-003 | seam/pole/land/ice/missing/invalid/out-of-domain cases | Visual and text outputs share identity and truthful encoding. |
| FIX-OSW-011 | invalid comparison | WP-OSW-003 | unsupported area/shape/distance comparison | Capability rejected and limitation remains adjacent. |
| FIX-OSW-012 | request/privacy | WP-OSW-005 | selected/unselected/bad-integrity/cross-origin assets | Only minimal declared same-origin request set succeeds; no storage. |
| FIX-OSW-013 | scientific sensitivity | WP-OSW-006 | depth/time/product/control/null/contrary cases | Distinct results and unresolved terms; no preferred-story coercion. |
| FIX-OSW-014 | zoning contradiction | WP-OSW-007 | attractive border with strong exchange/depth conflict | No promotion; diagnostics remain disaggregated. |
| FIX-OSW-015 | planetary pair | WP-OSW-008 | mechanism-supported and resemblance-only records | First may pass; second weakens/rejects mechanism claim. |
| FIX-OSW-016 | release drift | WP-OSW-009 | one mismatch per lifecycle/status/citation/artifact/review surface | Pure reconciler returns hold with zero effects. |
| FIX-OSW-017 | deploy failure | WP-OSW-009 | staged publish or smoke failure | Prior hosted release and current/citation metadata retained/restored. |
| FIX-OSW-018 | authority/secret | WP-OSW-001/009 | forecast/endorsement/release claim and secret-like diagnostics | Claim rejected; sensitive value absent from evidence/log output. |
| FIX-OSW-019 | environment fault | all packages | outbound-provider access denied and each optional dependency absent in turn | Default gate stays local; only the affected optional capability fails with stable diagnostic. |
| FIX-OSW-020 | verifier mutation | all packages | sentinel accepted artifact plus declared/undeclared temporary output | Sentinel hash unchanged; declared temporary output removed; undeclared residue fails. |

## Evidence record envelope

Every executed verification item records: verification and fixture IDs;
work-package and parent-contract IDs; immutable commit plus affected artifact
hashes; exact command/inspection revision; OS/runtime/dependency versions;
network policy; start/end time; exit code and bounded output; before/after tree
manifest; result (`pass`, `fail`, `blocked`, or `not_applicable` with accepted
rationale); diagnostic IDs; and evidence-file identity. Browser evidence also
records browser/engine version, viewport, zoom, input method, reduced-motion
state, OS/assistive-technology combination when applicable, accepted state/view
digest, focus sequence, announcements/text alternative, and request/storage
trace. Screenshots alone are not sufficient accessibility or state evidence.

## Command catalog

### L0 — changed-surface sanity

Run the commands applicable to the active package and all changed profiles:

```powershell
python -m compileall -q analysis
node --check atlas/app.js
git diff --check
```

When planned browser seams exist, syntax-check each changed file explicitly:

```powershell
node --check atlas/state.js
node --check atlas/routes.js
node --check atlas/scenes.js
node --check atlas/view-model.js
node --check atlas/asset-manifest.js
```

Focused tests must name modules rather than relying on a substring selector.
Until Verification records an implemented test module, the owning package
remains `proposed`, not `ready`.

### L1 — full offline confidence

```powershell
python -m pytest analysis -q
python -m unittest discover -s analysis -p "test_*.py"
python -m compileall -q analysis
node --check atlas/app.js
git diff --check
```

The runner-count difference is expected: pytest also reports parameterized
subtests. A package records both outcomes; it may not treat one successful
runner as evidence that the other was executed.

L1 is not called network-disabled until VFY-OSW-019 executes under an enforced
outbound-denial environment. A package also records VFY-OSW-020 before/after
manifests; a clean textual diff alone is insufficient non-mutation proof.

### L2 — integration/readiness proof

L2 includes L1 plus the package row below. Human interpretation thresholds are
deferred to Validation; L2 Verification still requires observable, recorded
behavior rather than reviewer memory.

| Package | Required L2 verification before package closure |
|---|---|
| WP-OSW-001 | VFY-OSW-002–006, 012, 013, 019, 020; FIX-OSW-001–006, 018–020; all required domain roles. |
| WP-OSW-002 | VFY-OSW-007, 008, 010, 011, 019, 020; FIX-OSW-007, 008, 019, 020; browser/keyboard and privacy inspection. |
| WP-OSW-003 | VFY-OSW-005, 009, 010, 019, 020; FIX-OSW-005, 010, 011, 019, 020; CHART/HARBOR rendered inspection. |
| WP-OSW-004 | VFY-OSW-004, 008–010, 013, 019, 020; FIX-OSW-009, 019, 020; executable surrogate for VAL-SCN-OSW-001/002/003/008 pending Validation. |
| WP-OSW-005 | VFY-OSW-010–012, 019, 020; FIX-OSW-012, 019, 020; measured request/reflow evidence, with acceptance thresholds from Validation. |
| WP-OSW-006 | VFY-OSW-004–006, 012, 014, 019, 020; FIX-OSW-013, 019, 020; independent calculation and frozen control/second-case selection. |
| WP-OSW-007 | VFY-OSW-005, 009, 012, 015, 019, 020; FIX-OSW-014, 019, 020; CURRENT/CHART scorecard inspection. |
| WP-OSW-008 | VFY-OSW-002–004, 009, 012, 016, 019, 020; FIX-OSW-015, 019, 020; CURRENT/SOUNDER/ORBIT decision. |
| WP-OSW-009 | VFY-OSW-003, 011–013, 017–020; FIX-OSW-016–020; staged host/retain-restore and owner decision. |

## Existing focused scientific command groups

These commands protect current evidence while new package-specific tests are
added; passing them does not prove the future target by itself.

```powershell
python -m unittest analysis.test_rtofs_mhw_upper_ocean_storage analysis.test_rtofs_mhw_upper_ocean_advection analysis.test_rtofs_mhw_advection analysis.test_gfs_mhw_surface_flux analysis.test_oisst_mhw_bridge_crosscheck
python -m unittest analysis.test_motion_partition_sensitivity analysis.test_motion_partition_robustness analysis.test_motion_region_audit analysis.test_region_membership_motion
python -m unittest analysis.test_atlas analysis.test_guides analysis.test_ocean_object_evidence_receipts
```

## Code-rigor verification

| Verification IDs | Code-rigor constraints | Required method |
|---|---|---|
| VFY-OSW-001 | CR-OSW-001, CR-OSW-002, CR-OSW-005, CR-OSW-022, CR-OSW-023, CR-OSW-025 | Size/branch report for touched critical units, profile checks, behavioral test review, before/after tree inspection. |
| VFY-OSW-002–006, 012–016 | CR-OSW-003, CR-OSW-004, CR-OSW-006, CR-OSW-007, CR-OSW-008, CR-OSW-009, CR-OSW-010, CR-OSW-011, CR-OSW-012, CR-OSW-013, CR-OSW-019, CR-OSW-021, CR-OSW-024 | Negative/property/mutation/fault fixtures, independent calculation, deterministic integrity, dependency/rights and redaction inspection. |
| VFY-OSW-007–011 | CR-OSW-014, CR-OSW-015, CR-OSW-016, CR-OSW-017, CR-OSW-018 | Pure state tests, safe DOM inspection, browser/AT/non-color matrix, shared-digest equivalence, request/storage trace. |
| VFY-OSW-017, 018 | CR-OSW-020 | Pure reconciliation, deliberate drift, staged hosted proof, retain/restore fault scenario. |

All 25 `CR-OSW-*` constraints are represented. WAIVER-OSW-001 and
WAIVER-OSW-006 trigger touched-unit characterization/decomposition; each first
historical family triggers WAIVER-OSW-002; WP-OSW-001 records the
WAIVER-OSW-003 tool bakeoff; WP-OSW-005 and WP-OSW-009 own the evidence needed
to revisit WAIVER-OSW-004 and WAIVER-OSW-005 respectively.

## Evidence ledger

| Evidence ID | Type | Evidence | Covers | Result |
|---|---|---|---|---|
| EVID-VFY-OSW-001 | pytest baseline | `python -m pytest analysis -q` | Current default test behavior | passed: 458 tests, 10 subtests, 2026-09-07; not an enforced network-denial run |
| EVID-VFY-OSW-002 | unittest baseline | `python -m unittest discover -s analysis -p "test_*.py"` | Independent discovery runner | passed: 327 tests, 2026-09-07 |
| EVID-VFY-OSW-003 | syntax baseline | `python -m compileall -q analysis`; `node --check atlas/app.js` | Current Python/browser syntax | passed, 2026-09-07 |
| EVID-VFY-OSW-004 | planning structure | Requirement/spec/interface/boundary/work-package orphan check; Markdown link/table check | VTRACE planning integrity | passed, 2026-09-07 |
| EVID-VFY-OSW-005 | change hygiene | `git diff --check` | Current working changes | passed with known Git CRLF warning only, 2026-09-07 |
| EVID-VFY-OSW-006 | native-role review | Eight-role verification review | Scientific/data/map/public/access/repro/repo/planetary coverage | passed: 8 roles, 0 P1, 16 P2 resolved |
| EVID-VFY-OSW-007 | contract and fixture evidence | VFY-OSW-002–006, 012, 013 | WP-OSW-001 | target pending |
| EVID-VFY-OSW-008 | reader/map/scene evidence | VFY-OSW-007–011 | WP-OSW-002–005 | target pending |
| EVID-VFY-OSW-009 | research evidence | VFY-OSW-014–016 | WP-OSW-006–008 | target pending |
| EVID-VFY-OSW-010 | release evidence | VFY-OSW-017, 018 | WP-OSW-009 | target/discovery pending |
| EVID-VFY-OSW-011 | isolation/non-mutation evidence | VFY-OSW-019, 020 | all work packages | target pending |

## Verification gaps and ownership

| Gap | Impact | Disposition | Owner / next stage |
|---|---|---|---|
| URL vocabulary/window owner decision absent | VFY-OSW-007 cannot pass compatibility policy. | discovery; WP-OSW-002 remains proposed | HARBOR/LOGBOOK, Validation |
| Complete admitted artifact/map-family inventories absent | VFY-OSW-002, 009, 012 cannot claim family completeness. | implement inventory before first adaptation | SOUNDER/CHART/KEEL, WP-OSW-001/003 |
| Controlled viewport/zoom/AT cases and acceptance thresholds absent | VFY-OSW-010 can test mechanics but not validate usability. | measure and accept separately | HARBOR/BEACON, Validation |
| Hosted performance budget absent | VFY-OSW-011 can emit measurements but cannot judge regression. | accept measured baseline/budget | KEEL/HARBOR, Validation |
| Deployment host/proof/retain-restore mechanism absent | VFY-OSW-018 cannot execute. | explicit discovery; no release readiness | LOGBOOK/KEEL, WP-OSW-009 and Validation |
| Human comprehension and scientific usefulness evidence absent | Automated surrogates cannot establish mission success. | execute VAL-SCN cases after implementation | All applicable roles, Validation |

## Verification gate

Decision: `pass_with_risk`

- [x] All 34 accepted requirements map to controlled verification IDs.
- [x] All 15 interfaces and 20 design invariants have verification coverage.
- [x] All 25 code-rigor constraints and six waivers have a verification path.
- [x] All nine proposed work packages have L0/L1/L2 closure requirements.
- [x] Baseline-passed and target-pending evidence are visibly distinct.
- [x] Negative, compatibility, property, mutation, adversarial, scientific, accessibility, privacy, and release-fault cases are controlled.
- [x] Validation-only thresholds and hosted discovery are not invented here.
- [x] All eight native roles resolve every P1/P2 verification finding.

Validation is authorized next but remains unopened. Work packages remain
proposed; target verification evidence remains pending and no execution is
authorized.

## Source links

- [Implementation Plan](IMPLEMENTATION_PLAN.md)
- [Work Packages](WORK_PACKAGES.md)
- [Requirements](REQUIREMENTS.md)
- [Specification Baseline](SPECIFICATION_BASELINE.md)
- [Interfaces](INTERFACES.md)
- [Detailed Design](DESIGN.md)
- [Code Rigor](CODE_RIGOR.md)
- [PITFALL register](../../design/pitfalls/README.md)
- [Native roles](../../.roles/ROLE.md)
- [Verification roles review](../../signals/roles/check/verification-roles-check-2026-09-07.md)

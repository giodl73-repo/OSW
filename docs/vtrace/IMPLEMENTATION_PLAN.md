# OSW Implementation Plan

Status: settled at native-role fixed point, 2026-09-07

## Scope

Repo: OSW — Ocean States of the World

Implementation baseline: convert the settled Mission-through-Design contracts
into bounded, reviewable work without implementing them. The first integrated
product outcome is the guided North Atlantic marine-heatwave anatomy. Later
science, zoning, planetary-comparison, and release work remain independent so
they cannot silently expand that first slice.

No package in this plan is authorized for execution. Verification must define
the executable gate before a package can move from `proposed` to `ready`.

## Baseline inputs

| Artifact | Status | Planning use |
|---|---|---|
| `MISSION.md` | accepted | Needs, non-goals, eight validation scenarios. |
| `CONOPS.md` | accepted | Normal/degraded paths and authority handoffs. |
| `REQUIREMENTS.md` | accepted | Thirty-four product requirements. |
| `SPECIFICATION_BASELINE.md` | accepted | Forty-five current/target/unknown controls. |
| `ARCHITECTURE.md`, `PACKAGE_BOUNDARIES.md` | accepted | Eleven boundaries and one-way evidence authority. |
| `INTERFACES.md` | accepted | Fifteen durable contracts and stable failures. |
| `DESIGN.md`, `CODE_RIGOR.md` | accepted | Component behavior, invariants, profiles, and waivers. |
| `ROADMAP.md`, PITFALL register | accepted planning controls | Product sequence and recurring failure classes. |
| `VERIFICATION.md` | accepted planning baseline | Defines current-versus-target evidence, 20 verification IDs, 20 fixture families, and package L0/L1/L2 gates. |
| `VALIDATION.md` | accepted planning baseline; execution blocked | Defines eight controlled human/scientific/access/map/reproduction/comparison scenarios; no acceptance evidence exists yet. |

## Implementation strategy

Build through incremental seams around the working static atlas:

1. establish contract validators, adapters, diagnostic identities, and fixtures;
2. isolate pure reader-state transitions and controlled route/scene registries;
3. construct one admitted map view model for visual and textual projections;
4. assemble the guided event journey from bound D-series results and receipts;
5. inventory payloads and measure responsive/performance baselines;
6. only then open separately justified science, zoning, planetary, or release work.

Historical artifacts remain immutable inputs. New contracts adapt them
losslessly and mark unavailable meaning; no package bulk-rewrites research
history. Browser code remains progressively enhanced and same-origin. Public
rendering never calculates science, repairs support, or overrides admission.

### Planned physical seams

Names are planning allocations, not permission to create code. A package may
change a name during execution only if it records the same ownership and
dependency direction before editing.

| Planned path | Owner / role | Purpose | Must not own |
|---|---|---|---|
| `analysis/osw_contracts.py` | PKG-OSW-006 / SOUNDER | Pure record, quantity, support, review, family, and compatibility validation. | Provider I/O, scientific calculation, publication effects. |
| `analysis/osw_admission.py` | PKG-OSW-006 / KEEL with domain vetoes | Compose immutable domain dispositions without override. | Domain-specific truth or release decision. |
| `analysis/osw_diagnostics.py` | PKG-OSW-006 / KEEL | Stable diagnostic code registry and safe envelopes. | Free-form provider payloads or secrets. |
| `analysis/test_osw_contracts.py`, `analysis/fixtures/osw-contracts/` | PKG-OSW-009 / KEEL | Golden, negative, mutation, compatibility, and adversarial proof inputs. | Repair or regeneration of accepted artifacts. |
| `atlas/state.js` | PKG-OSW-002 / HARBOR | Pure candidate parsing, compatibility, transition, and accepted state. | Rendering, science, network I/O. |
| `atlas/routes.js`, `atlas/scenes.js` | PKG-OSW-001/003 / BEACON | Controlled public route and guided-scene registries. | Unbound quantitative constants. |
| `atlas/view-model.js` | PKG-OSW-004 / CHART | Join accepted state and admitted display records for visual/text projection. | Support repair or claim authoring. |
| `atlas/asset-manifest.js` | PKG-OSW-005 / SOUNDER | Same-origin asset identity, integrity, and payload class. | Dynamic provider URLs or analytics. |
| `atlas/app.js` | Existing integration shell | Temporary orchestration and legacy-compatible adapters during extraction. | New independent state/contract authority. |

## Sequencing

| Order | Product capability | Principal surfaces | Work package | Why this order |
|---:|---|---|---|---|
| 1 | Contract and fixture kernel | receipts, registries, validators, `analysis/test_*.py` | WP-OSW-001 | Every later package needs executable identities, failures, and admission. |
| 2 | Canonical reader state and entrances | `atlas/index.html`, state/navigation seam, research index | WP-OSW-002 | Routes and direct addresses must settle before scenes and maps integrate. |
| 3 | Admitted map/view-model seam | renderer seam, styles, display manifest/data | WP-OSW-003 | Guided scenes need equivalent visual/text output and honest support. |
| 4 | Guided marine-heatwave anatomy | scene registry, D-series content, receipts, atlas shell | WP-OSW-004 | First consequential visitor outcome; integrates 001–003 without new science. |
| 5 | Responsive and payload baselines | selected-view loader, asset inventory, browser evidence | WP-OSW-005 | Measure the integrated journey before accepting numeric budgets. |
| 6 | Heat-budget challenge and generalization | acquisition/analysis/results/guides | WP-OSW-006 | Extends science only after current evidence is correctly presented. |
| 7 | Transport-tested zoning | scorecards, analysis, atlas zoning views | WP-OSW-007 | Motion evidence, not visual neatness, governs boundary revision. |
| 8 | Mechanism-safe planetary comparison | comparison records, guide/scene, receipts | WP-OSW-008 | Reuses admitted Earth quantities without blocking the core atlas. |
| 9 | Lifecycle reconciliation and release | status/citation/publication/hosting | WP-OSW-009 | Promotion follows integrated proof and explicit owner decision. |

WP-OSW-001 and WP-OSW-002 may be developed in separate worktrees only after
Verification proves their shared diagnostic/state contracts. WP-OSW-003
depends on their accepted contract outputs. WP-OSW-004 depends on 001–003.
WP-OSW-005 measures that integration. WP-OSW-006–009 are not prerequisites for
the first guided preview unless a discovered defect directly invalidates it.

WP-OSW-001 executes as three separately reviewable pulses: (A) diagnostics and
closed identity vocabularies, (B) lossless adapters plus orthogonal support,
and (C) federated admission plus family inventory. Each pulse leaves the full
offline suite green; no later pulse may weaken an earlier failure disposition.

## Source-to-work-package mapping

| Source IDs | Work package | Disposition | Notes |
|---|---|---|---|
| REQ-OSW-006–016, 026–029; SPEC-OSW-011–024, 033–036 | WP-OSW-001 | implement / characterize | Shared quantity, custody, adapter, admission, diagnostics, family, and review contracts. |
| REQ-OSW-001, 004, 021–023, 033, 034; SPEC-OSW-001–003, 008, 009, 017, 018, 027, 028, 041–045 | WP-OSW-002 | implement / preserve / discovery | Includes URL-policy discovery for SPEC-OSW-042 and no-collection preservation. |
| REQ-OSW-005, 014, 017–024; SPEC-OSW-010, 021, 022, 025–030 | WP-OSW-003 | implement / discovery | Includes responsive-case discovery for SPEC-OSW-029. |
| REQ-OSW-002, 003, 007, 012, 013, 021–024; SPEC-OSW-004–007, 011, 012, 019, 020, 027, 028 | WP-OSW-004 | implement | Uses existing D1–D14 results; it does not claim closure or causation. |
| REQ-OSW-025, 026, 028, 034; SPEC-OSW-023, 024, 029–034, 044, 045 | WP-OSW-005 | discovery / implement | Measures before setting budgets; inventory closes WAIVER-OSW-004. |
| REQ-OSW-006–008, 012–016, 026–028; SPEC-OSW-011, 012, 019–024, 033, 034 | WP-OSW-006 | defer until 004 | Depth/time sensitivity, missing-term availability, controls, second case. |
| REQ-OSW-009, 014, 017–020, 026–028; SPEC-OSW-013, 014, 022, 025, 026, 033, 034 | WP-OSW-007 | defer until transport evidence | No commitment to retain 11/22 or 56-unit organization. |
| REQ-OSW-010–012, 017, 026–029; SPEC-OSW-015, 016, 018–020, 025, 026, 033–036 | WP-OSW-008 | defer / implement independently | Requires admitted Earth and planetary identities plus weakening outcome. |
| REQ-OSW-011, 025, 029–034; SPEC-OSW-017, 018, 031, 032, 035–040, 044, 045 | WP-OSW-009 | discovery / defer until candidate | Includes deployment discovery for SPEC-OSW-039; cannot self-authorize release. |

All 34 accepted requirements and all 45 specification items occur in at least
one row. Observed/current items mean preserve and characterize; target items
mean implement; unknowns remain discovery and cannot be treated as passed.

### Machine-expanded orphan coverage

These rows intentionally spell out every ID so a validator need not interpret
typographic ranges.

| Work package | Requirement IDs |
|---|---|
| WP-OSW-001 | REQ-OSW-006, REQ-OSW-007, REQ-OSW-008, REQ-OSW-009, REQ-OSW-010, REQ-OSW-011, REQ-OSW-012, REQ-OSW-013, REQ-OSW-014, REQ-OSW-015, REQ-OSW-016, REQ-OSW-026, REQ-OSW-027, REQ-OSW-028, REQ-OSW-029 |
| WP-OSW-002 | REQ-OSW-001, REQ-OSW-004, REQ-OSW-021, REQ-OSW-022, REQ-OSW-023, REQ-OSW-033, REQ-OSW-034 |
| WP-OSW-003 | REQ-OSW-005, REQ-OSW-014, REQ-OSW-017, REQ-OSW-018, REQ-OSW-019, REQ-OSW-020, REQ-OSW-021, REQ-OSW-022, REQ-OSW-023, REQ-OSW-024 |
| WP-OSW-004 | REQ-OSW-002, REQ-OSW-003, REQ-OSW-007, REQ-OSW-012, REQ-OSW-013, REQ-OSW-021, REQ-OSW-022, REQ-OSW-023, REQ-OSW-024 |
| WP-OSW-005 | REQ-OSW-024, REQ-OSW-025, REQ-OSW-026, REQ-OSW-028, REQ-OSW-034 |
| WP-OSW-006 | REQ-OSW-006, REQ-OSW-007, REQ-OSW-008, REQ-OSW-012, REQ-OSW-013, REQ-OSW-014, REQ-OSW-015, REQ-OSW-016, REQ-OSW-026, REQ-OSW-027, REQ-OSW-028 |
| WP-OSW-007 | REQ-OSW-009, REQ-OSW-014, REQ-OSW-017, REQ-OSW-018, REQ-OSW-019, REQ-OSW-020, REQ-OSW-026, REQ-OSW-027, REQ-OSW-028 |
| WP-OSW-008 | REQ-OSW-010, REQ-OSW-011, REQ-OSW-012, REQ-OSW-017, REQ-OSW-026, REQ-OSW-027, REQ-OSW-028, REQ-OSW-029 |
| WP-OSW-009 | REQ-OSW-011, REQ-OSW-025, REQ-OSW-029, REQ-OSW-030, REQ-OSW-031, REQ-OSW-032, REQ-OSW-033, REQ-OSW-034 |

| Work package | Specification IDs |
|---|---|
| WP-OSW-001 | SPEC-OSW-011, SPEC-OSW-012, SPEC-OSW-013, SPEC-OSW-014, SPEC-OSW-015, SPEC-OSW-016, SPEC-OSW-017, SPEC-OSW-018, SPEC-OSW-019, SPEC-OSW-020, SPEC-OSW-021, SPEC-OSW-022, SPEC-OSW-023, SPEC-OSW-024, SPEC-OSW-033, SPEC-OSW-034, SPEC-OSW-035, SPEC-OSW-036 |
| WP-OSW-002 | SPEC-OSW-001, SPEC-OSW-002, SPEC-OSW-003, SPEC-OSW-008, SPEC-OSW-009, SPEC-OSW-017, SPEC-OSW-018, SPEC-OSW-027, SPEC-OSW-028, SPEC-OSW-041, SPEC-OSW-042, SPEC-OSW-043, SPEC-OSW-044, SPEC-OSW-045 |
| WP-OSW-003 | SPEC-OSW-010, SPEC-OSW-021, SPEC-OSW-022, SPEC-OSW-025, SPEC-OSW-026, SPEC-OSW-027, SPEC-OSW-028, SPEC-OSW-029, SPEC-OSW-030 |
| WP-OSW-004 | SPEC-OSW-004, SPEC-OSW-005, SPEC-OSW-006, SPEC-OSW-007, SPEC-OSW-011, SPEC-OSW-012, SPEC-OSW-019, SPEC-OSW-020, SPEC-OSW-027, SPEC-OSW-028 |
| WP-OSW-005 | SPEC-OSW-023, SPEC-OSW-024, SPEC-OSW-029, SPEC-OSW-030, SPEC-OSW-031, SPEC-OSW-032, SPEC-OSW-033, SPEC-OSW-034, SPEC-OSW-044, SPEC-OSW-045 |
| WP-OSW-006 | SPEC-OSW-011, SPEC-OSW-012, SPEC-OSW-019, SPEC-OSW-020, SPEC-OSW-021, SPEC-OSW-022, SPEC-OSW-023, SPEC-OSW-024, SPEC-OSW-033, SPEC-OSW-034 |
| WP-OSW-007 | SPEC-OSW-013, SPEC-OSW-014, SPEC-OSW-022, SPEC-OSW-025, SPEC-OSW-026, SPEC-OSW-033, SPEC-OSW-034 |
| WP-OSW-008 | SPEC-OSW-015, SPEC-OSW-016, SPEC-OSW-018, SPEC-OSW-019, SPEC-OSW-020, SPEC-OSW-025, SPEC-OSW-026, SPEC-OSW-033, SPEC-OSW-034, SPEC-OSW-035, SPEC-OSW-036 |
| WP-OSW-009 | SPEC-OSW-017, SPEC-OSW-018, SPEC-OSW-031, SPEC-OSW-032, SPEC-OSW-035, SPEC-OSW-036, SPEC-OSW-037, SPEC-OSW-038, SPEC-OSW-039, SPEC-OSW-040, SPEC-OSW-044, SPEC-OSW-045 |

| Work package | Interface IDs | Boundary IDs |
|---|---|---|
| WP-OSW-001 | IF-OSW-003, IF-OSW-007, IF-OSW-009, IF-OSW-010, IF-OSW-011, IF-OSW-012, IF-OSW-013 | PKG-OSW-005, PKG-OSW-006, PKG-OSW-007, PKG-OSW-008, PKG-OSW-009, PKG-OSW-011 |
| WP-OSW-002 | IF-OSW-001, IF-OSW-002, IF-OSW-006, IF-OSW-008 | PKG-OSW-001, PKG-OSW-002, PKG-OSW-003, PKG-OSW-005, PKG-OSW-009 |
| WP-OSW-003 | IF-OSW-002, IF-OSW-004, IF-OSW-006, IF-OSW-009, IF-OSW-010, IF-OSW-012, IF-OSW-015 | PKG-OSW-002, PKG-OSW-004, PKG-OSW-005, PKG-OSW-006, PKG-OSW-009 |
| WP-OSW-004 | IF-OSW-001, IF-OSW-002, IF-OSW-003, IF-OSW-004, IF-OSW-006, IF-OSW-007, IF-OSW-008, IF-OSW-009, IF-OSW-010, IF-OSW-012 | PKG-OSW-001, PKG-OSW-002, PKG-OSW-003, PKG-OSW-004, PKG-OSW-005, PKG-OSW-006, PKG-OSW-009, PKG-OSW-011 |
| WP-OSW-005 | IF-OSW-004, IF-OSW-005, IF-OSW-006, IF-OSW-012 | PKG-OSW-001, PKG-OSW-002, PKG-OSW-004, PKG-OSW-005, PKG-OSW-009, PKG-OSW-010 |
| WP-OSW-006 | IF-OSW-003, IF-OSW-007, IF-OSW-009, IF-OSW-010, IF-OSW-011, IF-OSW-012 | PKG-OSW-005, PKG-OSW-006, PKG-OSW-007, PKG-OSW-008, PKG-OSW-009, PKG-OSW-011 |
| WP-OSW-007 | IF-OSW-004, IF-OSW-007, IF-OSW-009, IF-OSW-010, IF-OSW-012, IF-OSW-015 | PKG-OSW-004, PKG-OSW-005, PKG-OSW-006, PKG-OSW-007, PKG-OSW-008, PKG-OSW-009, PKG-OSW-011 |
| WP-OSW-008 | IF-OSW-003, IF-OSW-004, IF-OSW-007, IF-OSW-010, IF-OSW-012, IF-OSW-014 | PKG-OSW-003, PKG-OSW-004, PKG-OSW-005, PKG-OSW-006, PKG-OSW-008, PKG-OSW-009, PKG-OSW-011 |
| WP-OSW-009 | IF-OSW-005, IF-OSW-006, IF-OSW-010, IF-OSW-012, IF-OSW-013 | PKG-OSW-006, PKG-OSW-009, PKG-OSW-010, PKG-OSW-011 |

## Boundary-to-work-package mapping

| Work package | Boundary IDs | Interface IDs | Integration rule |
|---|---|---|---|
| WP-OSW-001 | PKG-OSW-005–009, 011 | IF-OSW-003, 007, 009–013 | Validators observe candidates and never repair source truth. |
| WP-OSW-002 | PKG-OSW-001–003, 005, 009 | IF-OSW-001, 002, 006, 008 | One accepted state drives URL, focus, controls, announcements, and consumers. |
| WP-OSW-003 | PKG-OSW-002, 004–006, 009 | IF-OSW-002, 004, 006, 009, 010, 012, 015 | One admitted view model feeds visual and text renderers. |
| WP-OSW-004 | PKG-OSW-001–006, 009, 011 | IF-OSW-001–004, 006–010, 012 | Scenes bind admitted records; no copied authoritative numbers. |
| WP-OSW-005 | PKG-OSW-001, 002, 004, 005, 009, 010 | IF-OSW-004–006, 012 | Measure selected-view requests and reflow without adding collection. |
| WP-OSW-006 | PKG-OSW-005–009, 011 | IF-OSW-003, 007, 009–012 | Scientific results stop at admission; publication is separate. |
| WP-OSW-007 | PKG-OSW-004–009, 011 | IF-OSW-004, 007, 009, 010, 012, 015 | Scorecards retain every diagnostic and contrary/unavailable result. |
| WP-OSW-008 | PKG-OSW-003–006, 008, 009, 011 | IF-OSW-003, 004, 007, 010, 012, 014 | Comparison cannot widen either source claim. |
| WP-OSW-009 | PKG-OSW-006, 009–011 | IF-OSW-005, 006, 010, 012, 013 | Pure reconciliation precedes every hosting side effect. |

## Branch and change control

- Baseline branch: `atlas-08-private-preview`; record the immutable start SHA
  in each package execution record.
- Worktree: one bounded package or declared compatible pair per worktree. Never
  share generated-output directories across concurrent executions.
- Trigger: changes to quantity/support meaning, URL vocabulary, public route,
  payload/privacy class, lifecycle, interface version, diagnostic allocation,
  or accepted artifact identity require parent-artifact and role re-review.
- Rollback: revert the bounded package commit and regenerate only explicitly
  owned derivatives. Never overwrite historical receipts to make rollback fit.
- Existing dirty-tree ownership remains with the user; execution must begin
  from an inventoried baseline and may not absorb unrelated changes.

## Commit, push, and integration policy

Each commit should close one package pulse and include its focused tests.
Generated outputs travel with their generator/input identity when the package
owns them. Push is allowed only after required L0/L1 evidence and role lanes
pass; merge or preview promotion additionally needs the package's L2 evidence.
No package may push, merge, deploy, change citation/current status, or update a
TRACKER pointer merely because this planning document exists.

Integration order is contract → state/view → scene → measured integrated
journey. An integration failure leaves the prior accepted atlas usable and
cannot be hidden by substituting another dataset or weakening a claim.

## Product, process, and verification split

| Work packages | Product result | Implementation area | Verification responsibility | VTRACE-only closeout |
|---|---|---|---|---|
| 001–003 | Trustworthy contracts, resumable state, equivalent map meaning | data/Python/browser/map seams | Focused contract, negative, compatibility, and equivalence fixtures | evidence, trace, review, package status |
| 004 | Five-scene event-to-motion public journey | routes/scenes/content/atlas integration | Complete direct-URL, keyboard, receipt, claim-limit scenario | evidence, validation pointer, review |
| 005 | Responsive selected-view atlas with measured baseline | loader/assets/styles/browser measurement | request/storage/reflow/browser matrix | accepted thresholds and waiver disposition |
| 006–008 | New bounded research products | science/zoning/comparison pipelines | independent/second-case and domain-role validation | receipts, trace, review, status |
| 009 | Truthful candidate/release transition | lifecycle/reconciler/deploy adapter | drift, staged smoke, retain/restore, owner decision | release evidence and current-status update |

## Proposed verification ladder

Verification owns the final command IDs and thresholds. Planning proposes:

```powershell
python -m compileall -q analysis
node --check atlas/app.js
python -m pytest analysis -q
python -m unittest discover -s analysis -p "test_*.py"
git diff --check
```

| Level | Scope | Required evidence | Required before |
|---|---|---|---|
| L0 | Affected DOCS/PY/WEB/MAP/DATA/RELEASE profiles | Syntax/parse/link/schema/ID checks and focused tests; no unexpected tree mutation. | package commit |
| L1 | Package plus boundary integration | Full offline suite, compatibility/negative fixtures, generated integrity, clean-diff inspection. | push or review request |
| L2 | Consequential scientific/user/release outcome | Applicable VAL-SCN, independent or second-case evidence, browser/AT/rendered review, federated roles, or staged release rehearsal. | merge, preview admission, or public release as applicable |

## Planning risks

| ID | Risk | Control | Owner |
|---|---|---|---|
| IPR-OSW-001 | Contract foundation expands into a rewrite. | Characterization first; incremental seams; touched-unit waiver rules. | KEEL |
| IPR-OSW-002 | Guided story outruns the partial crossed-system budget. | Receipt binding, unresolved remainder, CURRENT veto. | CURRENT |
| IPR-OSW-003 | Map paint collapses support or creates authority. | Orthogonal support axes, shared view model, CHART admission. | SOUNDER / CHART |
| IPR-OSW-004 | Accessibility is postponed until visual completion. | State/text/AT exit criteria in WP-002–004, not a later cleanup package. | HARBOR |
| IPR-OSW-005 | Performance budgets are invented before measurement. | WP-005 discovery produces controlled baselines first. | KEEL |
| IPR-OSW-006 | Research packages block the first public learning path. | WP-006–008 remain independent and deferred. | BEACON / LOGBOOK |
| IPR-OSW-007 | Planning language is mistaken for execution or release approval. | All packages remain proposed; Verification and owner gates are explicit. | LOGBOOK |

## Implementation-readiness gate

Decision: `pass_with_risk`

- [x] Every accepted requirement and specification is mapped or explicitly dispositioned.
- [x] Every package names boundaries, interfaces, design direction, and rigor level.
- [x] Guided event anatomy is the first integrated product outcome.
- [x] Unknown thresholds/mechanisms remain discovery rather than invented decisions.
- [x] Product implementation is separated from VTRACE-only closeout.
- [x] No work package, commit, push, deployment, or release is authorized.
- [x] All eight native roles resolve every P1/P2 planning finding.

Verification is authorized next but remains unopened. All work packages remain
proposed and require controlled Verification IDs before execution.

## Source links

- [Work Packages](WORK_PACKAGES.md)
- [Detailed Design](DESIGN.md)
- [Code Rigor](CODE_RIGOR.md)
- [Interfaces](INTERFACES.md)
- [Package Boundaries](PACKAGE_BOUNDARIES.md)
- [Central roadmap](../../ROADMAP.md)
- [PITFALL register](../../design/pitfalls/README.md)
- [Native roles](../../.roles/ROLE.md)
- [Implementation Planning roles review](../../signals/roles/check/implementation-planning-roles-check-2026-09-07.md)

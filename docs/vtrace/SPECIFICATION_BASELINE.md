# OSW Specification Baseline

Status: settled at native-role fixed point, 2026-09-06

## Scope

Repo: OSW — Ocean States of the World

Baseline type: mixed existing-repository baseline

Baseline date: 2026-09-06

This artifact separates behavior observed in the repository from behavior that
the accepted requirements demand. `current` means evidence exists in this
checkout; `target` means the behavior is accepted but is not yet complete;
`deprecated` means an observed behavior must cease to be the controlling
behavior; and `unknown` means OSW lacks the measurement or owner decision needed
to state a credible target. A requirement that is partly met therefore maps to
separate current and target specification items rather than a fictional
“partial” behavior state.

This baseline does not choose components, schemas, frameworks, storage,
deployment machinery, work packages, or implementation order. Those decisions
remain closed until their VTRACE stages open.

An **admitted** scene, map, comparison, or generated-artifact family is one the
eventual release process permits to support a public OSW claim. Presence in the
working tree does not itself constitute admission. “Same claim context” means
the finding and strongest limitation are simultaneously available from the
scene without leaving it; progressive disclosure may hold technical detail,
but may not hide the existence of the limitation or receipt route.

Current classifications are a repository snapshot at source commit
`6285bdd3b74b8924f006e8f8e4582d2673564c95` plus the reviewed working-tree
documentation. They are neither release promotion nor a claim that every
historical artifact shares the observed behavior.

## Specification sources

| Source | Evidence | Status | Notes |
|---|---|---|---|
| Public entry and research corpus | `README.md`, `atlas/`, `research/index.html`, `guides/`, `figures/` | current | Research-rich and directly linked; not yet the three-route guided entry. |
| Hosted/review release description | `PREVIEW-STATUS.md`, `PUBLICATION-CHECKLIST.md`, `CITATION.cff`, `ROADMAP.md` | current + conflicting | The public/review distinction is stated, but later review-branch work has outgrown parts of the preview description. |
| Automated behavior | `analysis/test_atlas.py` and the broader `analysis/test_*.py` suite | current | Strong artifact-specific contracts; not a universal admission framework. |
| Scientific custody | `SOURCE-REGISTER.md`, `research/*.json`, `research/ocean-object-evidence-receipts.json`, `research/claims-ledger.csv` | current | Rich receipts and caveats with heterogeneous historical formats. |
| Interactive atlas | `atlas/index.html`, `atlas/app.js`, `atlas/styles.css`, `atlas/data/` | current | Static, local-data application with addressable atlas state and multiple evidence modes. |
| Generated analyses | `analysis/`, `figures/`, `research/` | current | Many deterministic offline generation and integrity paths; coverage is not yet declared by artifact family. |
| Accepted product obligations | `MISSION.md`, `CONOPS.md`, `REQUIREMENTS.md`, `design/pitfalls/README.md` | target | Controls intended behavior but is not evidence that behavior exists. |

## Controlled specification items

### Entry, story, place, and scientific meaning

| Spec ID | Parent REQ IDs | Type | State | Specification statement | Verification method | Validation method | Owner | Risk | Status |
|---|---|---|---|---|---|---|---|---|---|
| SPEC-OSW-001 | 001 | product | current | The README is the public corpus directory and exposes the atlas, guides, research records, and standalone figures through a long-form link hierarchy. | README/link inspection | Existing-reader walkthrough | BEACON | medium | observed |
| SPEC-OSW-002 | 001 | product | deprecated | The undifferentiated README link corridor is the controlling primary entry experience. It may remain as a complete secondary research index but must no longer be the only route to the principal outcomes. | Route inspection | Non-specialist walkthrough | BEACON | medium | accepted deprecation |
| SPEC-OSW-003 | 001 | product | target | The public entry offers exactly three controlled primary routes—explore the ocean, follow heat, inspect evidence—and keeps every accepted legacy destination reachable in a secondary research index. | Desktop/narrow route and link tests | Non-specialist task review | BEACON | high | accepted |
| SPEC-OSW-004 | 002 | product | current | D1–D14 event qualification, lineage, temperature, forcing, storage, advection, and unresolved-term artifacts exist as separately addressable research records and figures. | Corpus inventory and artifact tests | Researcher inspection | CURRENT | medium | observed |
| SPEC-OSW-005 | 002 | product | target | One directly addressable journey orders the accepted event scenes from qualification through unresolved terms, preserves their quantity distinctions, and ends without a causal or closed-budget claim. | Ordered route/state scenario | Researcher and public-reader walkthrough | CURRENT | high | accepted |
| SPEC-OSW-006 | 003 | product | current | Many standalone evidence figures state a finding, a material boundary, and a source or research-record identity, but no repository-wide scene admission contract proves that combination. | Figure/receipt sample inspection | BEACON review | BEACON | medium | observed |
| SPEC-OSW-007 | 003 | product | target | Every admitted guided scene exposes one principal finding, its strongest material limitation, evidence identity, and a direct receipt route in the same claim context. | Missing-field rejection fixture and rendered inspection | Public-reader and researcher review | BEACON | high | accepted |
| SPEC-OSW-008 | 004, 033 | interface | current | Atlas province selection is keyboard-operable, URL-addressable, zoomable, retained across supported view changes, and represented in visible and non-color text state; supported parameters include existing atlas mode and evidence controls. | `analysis/test_atlas.py`; browser inspection | Keyboard walkthrough | HARBOR | medium | observed |
| SPEC-OSW-009 | 004, 021, 022, 033 | interface | target | Pointer, keyboard, search, direct entry, reload, history, reset, and incompatible-state fallback converge on one province/scene state that preserves every compatible projection, evidence mode, depth, hierarchy preference, and onward route and announces rejected state. | State-transition and browser matrix | Keyboard and assistive-technology review | HARBOR | high | accepted |
| SPEC-OSW-010 | 005 | product | current | Direct source-grid evidence remains direct and the atlas explicitly states “no state aggregation”; no inferred province statistic or province fill is produced. | Existing assertion and negative-content tests | SOUNDER/CHART inspection | SOUNDER | low | observed |
| SPEC-OSW-011 | 006–008 | science | current | Quantity distinctions, explicit residuals, and motion/path claim ceilings are present in source-register entries, receipts, figures, and artifact-specific tests, but not enforced by one common admission contract. | Corpus and test inventory | CURRENT/SOUNDER audit | CURRENT | high | observed |
| SPEC-OSW-012 | 006–008 | science | target | Each admitted quantitative object declares its quantity identity; budget terms require independent receipts and retain an explicit unresolved remainder; motion/path/open-section evidence cannot inherit delivery, probability, residence, convergence, volume, or heat-transport claims it does not measure. | Valid and invalid quantity/budget/object fixtures | CURRENT/SOUNDER review | CURRENT | high | accepted |
| SPEC-OSW-013 | 009 | science | current | OSW has provisional organizational regions, boundary classes, motion diagnostics, sensitivity studies, and repeated warnings that visual fit and a preferred count are not diagnosed borders. | Registry, figure, and claim inspection | CURRENT/CHART review | CURRENT | medium | observed |
| SPEC-OSW-014 | 009 | science | target | Every zoning decision retains its boundary class and publishes persistence, exchange, retention, convergence, vertical agreement, gate dependence, contradictory evidence, and unavailable diagnostics before a retain/merge/split/move/demote outcome. | Candidate scorecard fixtures | CURRENT/CHART decision review | CURRENT | high | accepted |
| SPEC-OSW-015 | 010 | science | current | The gas-giant guide frames comparison around transferable mechanisms and names major forcing, stratification, depth, compressibility, boundary, and observation differences; a uniform valid/negative comparison fixture is absent. | Guide and source inspection | CURRENT/ORBIT review | ORBIT | medium | observed |
| SPEC-OSW-016 | 010 | science | target | Every planetary comparison identifies both quantities, the shared mechanism, material regime differences, and a weakening observation; resemblance-only cases are rejected or explicitly labeled speculative. | Paired mechanism/resemblance fixtures | CURRENT/SOUNDER/ORBIT review | ORBIT | high | accepted |
| SPEC-OSW-017 | 011 | product | current | Repository prose repeatedly limits OSW outputs to explanatory research artifacts and does not provide forecasting, warning, navigation, intervention, peer-review, approval, or operational-decision capability. | Capability and claim-language inspection | LOGBOOK/BEACON review | LOGBOOK | medium | observed |
| SPEC-OSW-018 | 011 | product | target | Every admitted public claim and capability remains inside that non-authority boundary and is rejected when it implies a prohibited operational or institutional role. | Negative capability/claim fixtures | LOGBOOK/BEACON review | LOGBOOK | high | accepted |

### Evidence custody and degraded operation

| Spec ID | Parent REQ IDs | Type | State | Specification statement | Verification method | Validation method | Owner | Risk | Status |
|---|---|---|---|---|---|---|---|---|---|
| SPEC-OSW-019 | 012, 013 | evidence | current | OSW maintains a source register, claims ledger, checksummed research receipts, layered source/derived/display artifacts, and many exact result-to-figure/prose checks, with historical receipt shapes that are not yet one complete contract. | Inventory and representative mutation tests | SOUNDER audit | SOUNDER | high | observed |
| SPEC-OSW-020 | 012, 013 | evidence | target | Every quantitative scene resolves through distinct source, intermediate, result, display, and claim identities to one receipt carrying all applicable provenance, quantity, support, transformation, checksum, evidence-class, claim-ceiling, and rights fields; dependent public values fail on drift. | Field-omission and mutation fixtures | Independent receipt reconstruction | SOUNDER | high | accepted |
| SPEC-OSW-021 | 014 | evidence | current | Shared atlas features distinguish land and absent ocean support and exact feature-shape tests subtract land; some scientific pipelines preserve additional missing/invalid states, but no cross-family proof covers all required mask classes. | Existing mask tests and family inventory | SOUNDER/CHART/HARBOR inspection | SOUNDER | high | observed |
| SPEC-OSW-022 | 014, 016, 018 | evidence | target | Land, sea ice, source-missing, quality-rejected, analysis-invalid, and out-of-domain support retain distinct machine and rendered identities through every admitted family; seam, coordinate, unit, sign, mask, collocation, partial-cell, stencil, time-support, schema, dimension, or checksum mismatch stops only the affected claim. | Cross-family mask and mismatch fixtures | Rendered and diagnostic review | SOUNDER | high | accepted |
| SPEC-OSW-023 | 015, 028 | ops | current | Default atlas use and the committed verification suite use local assets; network acquisition is separate, and optional-provider paths have localized dry-run/failure handling in several pipelines. | Network-disabled test execution and script inspection | Clean-checkout operator run | KEEL | medium | observed |
| SPEC-OSW-024 | 015, 016, 028 | ops | target | Network refresh is explicit and receipted, cannot overwrite accepted artifacts after failure or mismatch, and optional dependency/provider failure emits an actionable bounded diagnostic without breaking unrelated offline use. | Fault-injected acquisition/dependency fixtures | Clean-checkout degraded-path run | KEEL | high | accepted |

### Cartography, accessibility, and performance

| Spec ID | Parent REQ IDs | Type | State | Specification statement | Verification method | Validation method | Owner | Risk | Status |
|---|---|---|---|---|---|---|---|---|---|
| SPEC-OSW-025 | 017–020 | cartography | current | The common atlas exposes projection and evidence context, non-color boundary classes, ocean-only masking, seam continuity, polar mirrors, and provisional-language safeguards; standalone/experimental families carry uneven metadata and comparison limits. | Existing atlas tests plus family inventory | CHART/HARBOR review | CHART | high | observed |
| SPEC-OSW-026 | 017–020 | cartography | target | Every admitted map family passes one map contract for applicable projection/aspect, extent, time, depth, source/evidence class, quantity/units, scale, boundary class, uncertainty, ocean masks, seam identity, polar support, coastline context, redundant boundary encoding, and explicit metric/discontinuity limits. | Cross-family admission and invalid-comparison fixtures | CHART/SOUNDER/HARBOR review | CHART | high | accepted |
| SPEC-OSW-027 | 021–023 | accessibility | current | The atlas supplies keyboard province controls, focus/status cues, URL state, non-color summaries, and textual polar/selection equivalents; complete public-route, focus-state, touch-target, reduced-motion, loading, and failure coverage is not established. | Existing accessibility assertions and browser sample | Keyboard inspection | HARBOR | high | observed |
| SPEC-OSW-028 | 021–023 | accessibility | target | All routes, modes, objects, scenes, evidence links, and reset actions are keyboard/touch operable; URL, focus, programmatic, announced, visual, and text states agree; scientific meaning never depends on color, hover, or motion; reduced-motion users receive an equivalent. | State-machine, token, and browser/AT matrix | HARBOR/CHART review | HARBOR | high | accepted |
| SPEC-OSW-029 | 024 | nonfunctional | unknown | The controlled narrow viewport, browser zoom level, and two-dimensional-scroll criterion required for integrated map/finding/limitation/control/receipt use have not been measured and accepted. | Responsive baseline study | HARBOR/BEACON participant review | HARBOR | high | discovery required |
| SPEC-OSW-030 | 024 | nonfunctional | target | Once the controlled cases are accepted, the active map, finding, limitation, controls, and receipt route remain jointly usable in each case without hidden meaning or two-dimensional page scrolling. | Responsive browser matrix | HARBOR/BEACON review | HARBOR | high | accepted, threshold pending |
| SPEC-OSW-031 | 025 | nonfunctional | unknown | No accepted hosted critical-path transfer, request-count, render, interaction, or eager-payload baseline currently supports a numerical performance budget. | Hosted measurement study | KEEL/HARBOR review | KEEL | high | discovery required |
| SPEC-OSW-032 | 025 | nonfunctional | target | The released critical path loads only necessary selected-view research payloads eagerly and rejects an unexplained regression against the subsequently accepted measured budget. | Request/performance trace | KEEL/HARBOR review | KEEL | high | accepted, budget pending |

### Reproducibility, review, release, compatibility, and privacy

| Spec ID | Parent REQ IDs | Type | State | Specification statement | Verification method | Validation method | Owner | Risk | Status |
|---|---|---|---|---|---|---|---|---|---|
| SPEC-OSW-033 | 026–028 | ops | current | Numerous artifact generators are deterministic and offline-tested, proposals commonly carry plans/sources/claims/role reviews, and optional imports are isolated in many paths; no accepted family register proves complete coverage. | Generator/test/intake inventory | KEEL/CURRENT review | KEEL | medium | observed |
| SPEC-OSW-034 | 026–028 | ops | target | Every admitted generated-artifact family has a deterministic offline regeneration or integrity path, pinned applicable dependencies and inputs, explicit comparison, and a pre-implementation intake covering question, source, rights, result, claim ceiling, demonstration, reuse, and PITFALL disposition. | Family-coverage and intake fixtures | Clean-checkout and null-result review | KEEL | high | accepted |
| SPEC-OSW-035 | 029 | governance | current | Native-role reviews record artifact/lens, findings, severity, dispositions, and gate decisions, but historical records do not uniformly bind an immutable artifact digest. | Review-record inventory | LOGBOOK review | LOGBOOK | medium | observed |
| SPEC-OSW-036 | 029 | governance | target | An external review binds immutable artifact identity, reviewer lens, findings, severity, and disposition and explicitly grants neither endorsement nor release authority. | Invalid/valid review-record inspection | External-review dry run | LOGBOOK | high | accepted |
| SPEC-OSW-037 | 030, 031 | release | current | Public, review-preview, experiment, and research-intake labels exist across preview status, publication metadata, plans, and artifacts, but they are not reconciled through one lifecycle registry and currently drift. | Cross-surface release audit | LOGBOOK/KEEL review | LOGBOOK | high | observed conflict |
| SPEC-OSW-038 | 030, 031 | release | target | Each controlled artifact has exactly one legal lifecycle state, only a released commit defines hosted current behavior, and a candidate cannot deploy until one immutable review packet reconciles all declared release surfaces, generated evidence, findings, owner decision, and hosted target. | Lifecycle transition and deliberate-drift fixtures | Owner release rehearsal | LOGBOOK | high | accepted |
| SPEC-OSW-039 | 032 | release | unknown | The deployment host, hosted-commit proof, atomicity, smoke path, and retain/restore mechanism have not been baselined. | Deployment discovery rehearsal | LOGBOOK/KEEL review | LOGBOOK | high | discovery required |
| SPEC-OSW-040 | 032 | release | target | Publication verifies the hosted commit and primary journeys; failure retains or restores the prior release and leaves citation/current-release claims unchanged. | Staging and fault-injected deployment | Owner rollback rehearsal | LOGBOOK | high | accepted, mechanism pending |
| SPEC-OSW-041 | 033 | interface | current | Existing atlas query parameters preserve several selection/mode/depth/projection states and unknown values have some safe fallback behavior; no declared URL version or migration period exists. | Query-state test inventory | Shared-link walkthrough | HARBOR | medium | observed |
| SPEC-OSW-042 | 033 | interface | unknown | The supported parameter inventory, version marker, compatibility window, and migration/retirement policy have not received an owner decision. | URL inventory and compatibility study | HARBOR/LOGBOOK review | HARBOR | high | discovery required |
| SPEC-OSW-043 | 033 | interface | target | Province, object, mode, depth, event, scene, and projection URLs follow the accepted compatibility policy; unknown, conflicting, or removed values fall back to a usable state and expose and announce the rejection. | Compatibility and migration fixtures | Shared-link/browser review | HARBOR | high | accepted, policy pending |
| SPEC-OSW-044 | 034 | privacy | current | The static atlas has no account, user-upload, cookie, telemetry, or declared user-data collection capability. | Static source and request inspection | LOGBOOK privacy-boundary review | LOGBOOK | low | observed |
| SPEC-OSW-045 | 034 | privacy | target | That no-collection boundary remains controlling unless a later accepted requirement, privacy/security review, public disclosure, and validation plan authorize a change. | Capability/request gate | LOGBOOK owner review | LOGBOOK | high | accepted |

## Public contracts

These rows control externally observable behavior only. They do not allocate
components or prescribe a data format.

| Contract ID | Spec IDs | Surface | Compatibility rule | Change-control trigger | Owner | Verification evidence |
|---|---|---|---|---|---|---|
| IF-OSW-001 | 001–003 | Public entry and research links | Accepted corpus destinations remain reachable; the three primary route names are controlled. | Primary route or accepted destination added, removed, or renamed. | BEACON | Local-link and route inspection. |
| IF-OSW-002 | 008, 009, 041–043 | Atlas URL state | Current supported links must resolve safely; incompatible values cannot create a false or unusable state. Exact version/window is `SPEC-OSW-042` discovery. | Parameter semantics, default, name, or retirement changes. | HARBOR | Query-state compatibility fixtures. |
| IF-OSW-003 | 019, 020 | Evidence receipt reached from a scene | A receipt identity is stable and its claim ceiling cannot broaden silently; exact common representation is deferred to Interfaces. | Applicable provenance field, quantity semantics, checksum identity, or rights posture changes. | SOUNDER | Receipt completeness and mutation fixtures. |
| IF-OSW-004 | 025, 026 | Rendered map and text alternative | Machine evidence and rendered/text states describe the same admitted view; family-specific additions may not weaken the common contract. | Projection, mask, boundary class, quantity, or comparison capability changes. | CHART | Cross-family map admission suite. |
| IF-OSW-005 | 037–040 | Released hosted state and citation | Only the verified released commit may update current-release and citation claims. | Candidate promotion, failed deployment, rollback, or hosted-target change. | LOGBOOK | Release packet and hosted smoke evidence. |
| IF-OSW-006 | 044, 045 | Browser requests and persistence | No accounts, uploads, cookies, telemetry, or user-data collection without controlled approval and disclosure. | Any new persistence, third-party request, collection, or upload capability. | LOGBOOK | Static/request inspection. |

## Package and language allocation

No package, module, schema, framework, or language allocation is authorized in
this stage. Architecture must allocate responsibilities without weakening these
specifications. Until then, observed locations above are evidence pointers, not
approved future boundaries.

| Spec IDs | Allocation | Responsibility | Forbidden responsibility | Validation profile |
|---|---|---|---|---|
| 001–045 | Unallocated — Architecture stage | Preserve controlled behavior and discovery obligations. | Treat the present file layout as approved architecture or expose VTRACE machinery as visitor-facing ocean content. | To be assigned after Architecture and Interfaces. |

## Nonfunctional constraints

| Constraint ID | Parent spec IDs | Constraint | Threshold / rule | Verification method | Status |
|---|---|---|---|---|---|
| SPEC-NF-OSW-001 | 023, 024, 033, 034 | Deterministic offline default | The default released-site use and verification gate require no live scientific provider; affected optional paths fail locally. | Network-disabled clean-checkout gate. | accepted target; substantial current evidence |
| SPEC-NF-OSW-002 | 027–030 | Accessible state and reflow | Semantic equivalence is mandatory; numerical viewport/zoom cases remain controlled discovery under `SPEC-OSW-029`. | Browser/AT matrix. | threshold unknown |
| SPEC-NF-OSW-003 | 031, 032 | Critical-path performance | Baseline first; no numerical budget may be invented before hosted measurement. Only selected-view necessary payloads load eagerly. | Request and performance trace. | budget unknown |
| SPEC-NF-OSW-004 | 037–040 | Release atomicity | Hosted behavior, commit identity, citation, and current-release claim change together or remain at the prior release. | Fault-injected release rehearsal. | mechanism unknown |
| SPEC-NF-OSW-005 | 044, 045 | Privacy boundary | Zero undeclared collection, user persistence, upload, cookie, or telemetry requests. | Source/request inspection. | current and accepted target |

## Assumptions and unknowns

| ID | Item | Impact | Disposition | Owner |
|---|---|---|---|---|
| SPEC-UNK-OSW-001 | Controlled viewport, zoom, browser, assistive-technology, contrast, and target-size cases. | Blocks final verification thresholds for 021–024, not Architecture. | Discovery before Interfaces/Validation acceptance; do not invent values. | HARBOR |
| SPEC-UNK-OSW-002 | Hosted transfer, request-count, render, and interaction baseline. | Blocks numerical performance budget and confident payload regression gate. | Measure before Design/Validation; retain DL-03 open. | KEEL |
| SPEC-UNK-OSW-003 | Complete generated-artifact-family inventory. | Prevents a claim that every artifact is reproducible. | Inventory and classify before implementation work-package acceptance. | KEEL |
| SPEC-UNK-OSW-004 | URL version, compatibility window, and migration/retirement policy. | Blocks durable shared-state acceptance. | Inventory current parameters, then owner decision before Interfaces settles. | HARBOR |
| SPEC-UNK-OSW-005 | Deployment target, hosted-commit proof, atomic transition, and rollback mechanism. | Blocks release verification design, not product Architecture. | Allocate in Architecture/Implementation Plan and rehearse before release. | LOGBOOK |
| SPEC-UNK-OSW-006 | External validation participants and success thresholds. | Prevents mission validation claims. | Carry to Validation; no endorsement inference. | BEACON |
| SPEC-UNK-OSW-007 | Common representation for quantity, receipt, boundary, claim-ceiling, and lifecycle contracts. | Affects interoperability and uniform admission tests. | Architecture assigns ownership; Interfaces controls representation. | SOUNDER |
| SPEC-UNK-OSW-008 | Exact zoning score combination and decision thresholds. | Prevents diagnosed promotion of organizational borders. | Carry to Design/Validation; current borders remain provisional. | CURRENT |

No unknown above is silently accepted as current behavior. Each is a bounded
discovery obligation; none prevents this mixed baseline from controlling the
next Architecture stage.

## Requirement-to-spec coverage

| Requirement | Spec IDs | Coverage status | Current-baseline finding |
|---|---|---|---|
| REQ-OSW-001 | 001–003 | covered | Current corridor retained as index; primary-route replacement is target. |
| REQ-OSW-002 | 004, 005 | covered | Evidence exists separately; integrated journey is target. |
| REQ-OSW-003 | 006, 007 | covered | Common scene contract is target. |
| REQ-OSW-004 | 008, 009 | covered | Selection exists; complete state convergence/search is target. |
| REQ-OSW-005 | 010 | covered | Observed current behavior. |
| REQ-OSW-006 | 011, 012 | covered | Rich conventions exist; common admission is target. |
| REQ-OSW-007 | 011, 012 | covered | Explicit residual examples exist; universal rule is target. |
| REQ-OSW-008 | 011, 012 | covered | Claim ceilings exist; universal rejection is target. |
| REQ-OSW-009 | 013, 014 | covered | Provisional diagnostics exist; complete scorecard is target. |
| REQ-OSW-010 | 015, 016 | covered | Guide exists; comparison contract is target. |
| REQ-OSW-011 | 017, 018 | covered | Capability boundary exists; admission rejection is target. |
| REQ-OSW-012 | 019, 020 | covered | Heterogeneous receipts exist; complete common contract is target. |
| REQ-OSW-013 | 019, 020 | covered | Many layered checks exist; complete dependency enforcement is target. |
| REQ-OSW-014 | 021, 022 | covered | Some mask states are proven; cross-family preservation is target. |
| REQ-OSW-015 | 023, 024 | covered | Offline default exists; universal safe refresh is target. |
| REQ-OSW-016 | 022, 024 | covered | Mismatch contract is target. |
| REQ-OSW-017 | 025, 026 | covered | Common atlas strong; universal metadata is target. |
| REQ-OSW-018 | 022, 025, 026 | covered | Common atlas strong; all families are target. |
| REQ-OSW-019 | 025, 026 | covered | Common atlas classes exist; machine-readable universality is target. |
| REQ-OSW-020 | 025, 026 | covered | Limitations exist unevenly; admission rule is target. |
| REQ-OSW-021 | 009, 027, 028 | covered | Atlas keyboard support exists; all public journeys are target. |
| REQ-OSW-022 | 009, 027, 028 | covered | Several states agree; complete transition contract is target. |
| REQ-OSW-023 | 027, 028 | covered | Non-color support exists; reduced-motion completeness is target. |
| REQ-OSW-024 | 029, 030 | covered with discovery | Behavior target accepted; exact controlled cases unknown. |
| REQ-OSW-025 | 031, 032 | covered with discovery | Budget unknown; eager-loading rule accepted. |
| REQ-OSW-026 | 033, 034 | covered | Many paths exist; family completeness is target. |
| REQ-OSW-027 | 033, 034 | covered | Practice exists unevenly; admission contract is target. |
| REQ-OSW-028 | 023, 024, 033, 034 | covered | Local isolation exists; universal degraded behavior is target. |
| REQ-OSW-029 | 035, 036 | covered | Review records exist; immutable binding is target. |
| REQ-OSW-030 | 037, 038 | covered | Lifecycle labels conflict; one-state registry is target. |
| REQ-OSW-031 | 037, 038 | covered | Release surfaces exist and drift; reconciled packet is target. |
| REQ-OSW-032 | 039, 040 | covered with discovery | Outcome accepted; deployment mechanism unknown. |
| REQ-OSW-033 | 008, 009, 041–043 | covered with discovery | State exists; compatibility policy unknown and target behavior accepted. |
| REQ-OSW-034 | 044, 045 | covered | Observed boundary preserved as controlled target. |

## Spec-to-verification coverage

Verification IDs are reserved for the later Verification stage. This table
records credible method families without pretending that planned evidence has
already run.

| Spec IDs | Planned method | Expected result | Current evidence pointer | Status |
|---|---|---|---|---|
| 001–010 | Route, state-transition, local-link, and negative aggregation tests | Entry and place semantics agree without invented province data. | `README.md`, `atlas/`, `analysis/test_atlas.py`, D1–D14 artifacts | current evidence + planned coverage |
| 011–018 | Quantity, budget, boundary, analogy, and authority fixtures | Invalid claim escalation is rejected and limitations remain adjacent. | `SOURCE-REGISTER.md`, guides, claims ledger, research receipts | current evidence + planned admission tests |
| 019–024 | Receipt mutation, mask/mismatch, network-off, and fault injection | Drift or mismatch stops only the affected claim and accepted artifacts survive. | `research/`, `analysis/`, source register | current evidence + planned cross-family tests |
| 025–032 | Map admission, state/accessibility, responsive, and performance matrices | Every admitted view is semantically complete and usable within accepted budgets. | Common atlas tests; performance/reflow baselines absent | partial evidence; discovery required |
| 033–036 | Artifact-family and review-record fixtures | Each family is reproducible and reviews are immutable and bounded. | Generators, tests, `.roles` reviews | current evidence + planned completeness audit |
| 037–045 | Lifecycle, release, deploy, URL compatibility, and request inspection | One release truth changes atomically; links degrade safely; no undeclared collection. | Preview/publication/citation files, atlas query tests | current evidence + discovery + planned gates |

## Specification gate

Decision: pass_with_risk

Required before Architecture opens:

- [x] Every accepted `REQ-OSW-*` maps to one or more `SPEC-OSW-*` items.
- [x] Observed, target, deprecated, and unknown behavior are separated.
- [x] Public contracts have owners through their parent specification items and
  explicit change-control triggers.
- [x] Unknowns are bounded as discovery work and are not presented as current.
- [x] Verification and validation method families are credible for each claim.
- [x] Package/language allocation remains deferred to Architecture.
- [x] All eight native roles have reviewed the baseline and every P1/P2 finding
  has been repaired or explicitly controlled.

Architecture is authorized as the next separately reviewed stage but remains
unopened. Risk is bounded to the eight owned discovery items above; none is
silently treated as current behavior or an implementation prerequisite.

## Source links

- [Mission](MISSION.md)
- [CONOPS](CONOPS.md)
- [Requirements](REQUIREMENTS.md)
- [PITFALL register](../../design/pitfalls/README.md)
- [Central roadmap](../../ROADMAP.md)
- [Native roles](../../.roles/ROLE.md)

The native-role fixed-point review is recorded in
[`specification-baseline-roles-check-2026-09-06.md`](../../signals/roles/check/specification-baseline-roles-check-2026-09-06.md).

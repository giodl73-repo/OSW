# OSW Work Packages

Status: planning baseline settled at native-role fixed point, 2026-09-07;
all packages remain proposed

## Scope and authority

These packages partition the settled OSW design into product-bearing changes.
They are proposals, not execution records. Verification must assign controlled
verification IDs and commands before any package becomes `ready`.

VTRACE status, review, readiness, fixtures, and package state remain internal
controls. The public product receives ocean maps, explanations, controls, and
receipts—not project-management concepts or commands.

## Package register

| ID | Objective | Principal product requirement | Parent IDs | Affected surfaces | Entry | Exit | Rigor | VTRACE-only closeout | Status |
|---|---|---|---|---|---|---|---|---|---|
| WP-OSW-001 | Establish contract, adapter, diagnostic, admission, and fixture kernel. | Quantities and evidence fail closed without rewriting history. | REQ-OSW-006–016, 026–029; SPEC-OSW-011–024, 033–036; DES-OSW-005–008, 011, 012, 014, 015 | PKG-OSW-005–009, 011 | Verification IDs and complete admitted-family inventory accepted. | Three bounded pulses deliver pure validators/adapters and positive/negative/mutation/fault fixtures; tool bakeoff recorded. | DATA/PY/MULTI L2 | evidence/trace/review/status | proposed |
| WP-OSW-002 | Implement canonical reader state and three controlled entrances. | Resumable accessible routes and selections. | REQ-OSW-001, 004, 021–023, 033, 034; SPEC-OSW-001–003, 008, 009, 027, 028, 041–045; DES-OSW-001–004, 009, 012, 015 | PKG-OSW-001–003, 005, 009 | WP-OSW-001 state vocab/diagnostics; URL discovery decision. | Transactional state, routes, compatibility, keyboard/focus/announcement fixtures pass. | WEB/MULTI L2 | evidence/trace/review/status | proposed |
| WP-OSW-003 | Create admitted view model and equivalent visual/text map rendering. | Every displayed location and support state means the same in every channel. | REQ-OSW-005, 014, 017–024; SPEC-OSW-010, 021, 022, 025–030; DES-OSW-007–010, 012, 015 | PKG-OSW-002, 004–006, 009 | WP-OSW-001 contracts and WP-OSW-002 accepted state. | Map admission, orthogonal support, seam/polar/land, comparison-limit, non-color, and text-equivalence fixtures pass. | MAP/WEB/DATA/MULTI L2 | evidence/trace/review/status | proposed |
| WP-OSW-004 | Deliver guided marine-heatwave event anatomy. | A reader follows event → surface → boundary → column → motion with receipt and limitation at every scene. | REQ-OSW-002, 003, 007, 012, 013, 021–024; SPEC-OSW-004–007, 011, 012, 019, 020, 027, 028; DES-OSW-004, 005, 009, 012, 015 | PKG-OSW-001–006, 009, 011 | WP-OSW-001–003 accepted; D-series identity inventory frozen. | VAL-SCN-OSW-001/002/003 candidate passes; no copied values, false closure, or hidden limitation. | MULTI/PY/DATA/WEB/MAP L2 | evidence/validation pointer/trace/review/status | proposed |
| WP-OSW-005 | Measure and control payload, reflow, browser, and privacy behavior. | The integrated journey remains usable and loads only selected-view evidence. | REQ-OSW-024–026, 028, 034; SPEC-OSW-023, 024, 029–034, 044, 045; DES-OSW-010–012, 015 | PKG-OSW-001, 002, 004, 005, 009, 010 | WP-OSW-004 integrated candidate; measurement cases declared. | Accepted baseline/budgets, asset classes, request trace, reflow/browser matrix, and no-collection gate pass. | WEB/DATA/MULTI L2 | thresholds/waiver/evidence/trace/review | proposed |
| WP-OSW-006 | Challenge and generalize the heat-budget result. | Depth/time/product/control cases expose sensitivity and missing terms without invented closure. | REQ-OSW-006–008, 012–016, 026–028; SPEC-OSW-011, 012, 019–024, 033, 034; DES-OSW-006–008, 011, 012, 015 | PKG-OSW-005–009, 011 | WP-OSW-001; scientific intake and sources/rights accepted. | 0–100/0–200 m or explicit unavailable result, missing-term inventory, frozen selection rule, control/second case, receipts and CURRENT/SOUNDER review. | PY/DATA/MAP/MULTI L2 | evidence/trace/review/status | proposed-deferred |
| WP-OSW-007 | Test candidate ocean-state boundaries with transport evidence. | Retain/merge/split/move/demote follows explicit diagnostics, not appearance or count. | REQ-OSW-009, 014, 017–020, 026–028; SPEC-OSW-013, 014, 022, 025, 026, 033, 034; DES-OSW-007–009, 012, 014, 015 | PKG-OSW-004–009, 011 | WP-OSW-001/003; candidate and diagnostic method frozen before inspection. | Scorecard retains persistence/exchange/retention/convergence/depth/gate evidence and contrary/unavailable states; VAL-SCN-OSW-005 passes. | PY/DATA/MAP/MULTI L2 | evidence/trace/review/status | proposed-deferred |
| WP-OSW-008 | Publish one mechanism-safe Earth/gas-giant comparison. | Shared mechanism and non-analogous regime/observability remain inseparable. | REQ-OSW-010–012, 017, 026–029; SPEC-OSW-015, 016, 018–020, 025, 026, 033–036; DES-OSW-006, 007, 009, 012, 014, 015 | PKG-OSW-003–006, 008, 009, 011 | Admitted Earth and planetary identities; comparison question frozen. | Valid and resemblance-only fixtures plus VAL-SCN-OSW-007 and CURRENT/SOUNDER/ORBIT review pass. | DATA/MAP/DOCS/MULTI L2 | evidence/trace/review/status | proposed-deferred |
| WP-OSW-009 | Reconcile lifecycle and prove safe public transition. | Only verified hosted bytes become current; failed publication preserves prior release. | REQ-OSW-011, 025, 029–034; SPEC-OSW-017, 018, 031, 032, 035–040, 044, 045; DES-OSW-007, 010, 012, 013, 015 | PKG-OSW-006, 009–011 | Integrated candidate, accepted thresholds, host/rollback discovery, owner target/decision. | Pure drift reconciliation, staged hosted commit/journey smoke, retain/restore, privacy/payload, citation/status atomicity pass. | RELEASE/MULTI L2 | release evidence/trace/review/status | proposed-deferred |

Ranges use the full `*-OSW-*` prefixes named in the source artifacts; detailed
interface and constraint bindings follow below.

## Detailed package contracts

### WP-OSW-001 — contract and fixture kernel

| Field | Contract |
|---|---|
| Interfaces | IF-OSW-003, 007, 009–013 |
| Design / rigor | DES-OSW-005–008, 011, 012, 014, 015; CR-OSW-001–013, 019, 021–025 |
| Scenarios | VAL-SCN-OSW-002, 006, 008 |
| Product touches | Versioned contract/adapter modules, diagnostic allocation, admission validators, family inventory, local fixtures, focused tests. |
| Forbidden | Rewrite historical receipts; one score overriding domain vetoes; validators repairing candidates; live provider in default tests. |
| Required fixtures | Golden quantity/receipt; field omission; sign/reference mismatch; orthogonal support including subsurface-under-ice; veto/unknown composition; stale review; acquisition fault; mutation lineage. |
| Tool decision | Measure minimal Python/JS/docs lint/static checks against current defects and churn; adopt or explicitly reject each with evidence, closing WAIVER-OSW-003 without inventing a mandatory dependency. |
| Stop condition | Any lossy adapter, unowned diagnostic, missing required domain, or unbounded source-family inventory. |

Execution pulses are mandatory and separately reviewable:

| Pulse | Result | Exit before next pulse |
|---|---|---|
| 001-A | Diagnostic registry and closed quantity/support/lifecycle/review/family identities. | ID uniqueness, safe envelopes, valid/invalid identity fixtures, full offline baseline. |
| 001-B | Versioned lossless adapters for the first admitted historical families. | Preservation, unavailable-field, mutation, and orthogonal-support fixtures; no source rewrite. |
| 001-C | Pure domain validators, non-overridable admission composition, and complete admitted-family inventory. | Exhaustive disposition combinations, one representative fixture per admitted family, and role-lane decisions. |

### WP-OSW-002 — canonical state and entrances

| Field | Contract |
|---|---|
| Interfaces | IF-OSW-001, 002, 006, 008 |
| Design / rigor | DES-OSW-001–004, 009, 012, 015; CR-OSW-001–005, 012, 014–18, 21–25 |
| Scenarios | VAL-SCN-OSW-001, 003 |
| Product touches | Route registry, semantic shell, state parsing/adaptation/reducer seam, controls, URL/history, research index. |
| Discovery | Owner accepts version marker, parameter inventory, compatibility interval, and retirement policy before code changes emit a new canonical URL. |
| Required fixtures | Unversioned/current/legacy/unknown/conflicting state; direct/reload/history/reset; pointer/keyboard/search; loading/failure; no-script route; request/storage absence. |
| Forbidden | Silent clamp, split visual/AT state, dynamic provider request, hard-coded duplicate route authority, VTRACE state in browser state. |
| Stop condition | URL-policy decision absent or behavior cannot be characterized before extracting the touched `atlas/app.js` seam. |

### WP-OSW-003 — admitted map view model

| Field | Contract |
|---|---|
| Interfaces | IF-OSW-002, 004, 006, 009, 010, 012, 015 |
| Design / rigor | DES-OSW-007–010, 012, 015; CR-OSW-001–005, 008, 010, 013–19, 21–25 |
| Scenarios | VAL-SCN-OSW-003, 004, 005 |
| Product touches | View-model builder, renderer seam, equivalent text, manifest entries, map-contract adapters, CSS/SVG/canvas behavior and tests. |
| Required fixtures | Land/ocean/out-of-domain; valid/missing/rejected/invalid; open-water/sea-ice combinations; seam/pole/coast; boundary classes; unsupported metric comparison; failed asset retaining prior view. |
| Responsive discovery | Measure candidate viewport/zoom/reflow cases; do not declare SPEC-OSW-029/030 passed from desktop screenshots. |
| Forbidden | Palette alpha as support truth, renderer-created data, independent text calculation, crisp styling that promotes boundary class. |
| Entry refinement | A complete admitted map-family applicability inventory identifies projection/aspect, extent, time/depth, quantity, scale, boundary, uncertainty, support, seam/polar, and comparison-capability fields before the first family is adapted. |
| Stop condition | Visual/text digests diverge or any admitted family lacks applicable map/support metadata. |

### WP-OSW-004 — guided marine-heatwave anatomy

| Field | Contract |
|---|---|
| Interfaces | IF-OSW-001–004, 006–010, 012 |
| Design / rigor | DES-OSW-004–009, 012, 015; CR-OSW-003–010, 013–19, 21–25 |
| Scenarios | VAL-SCN-OSW-001, 002, 003, 008 |
| Product touches | Ordered scene registry, five connected public scenes, result bindings, limitations, receipt routes, atlas integration and public entry. |
| Required scene result | Event qualification/lineage; surface-temperature bridge; surface-energy screen; 0–50 m storage; horizontal advection plus unresolved partial remainder. |
| Required fixtures | Missing/reordered scene; removed/mutated result field; receipt/claim incompatibility; direct URL/back/next/reset; keyboard/focus/announcement; narrow/reduced-motion/non-color; no-script evidence route. |
| Forbidden | Duplicate authoritative numbers, residual renamed as process, crossed-system near-balance called closure, motion called delivery, hidden strongest limitation. |
| Stop condition | Any scene lacks an admitted result/receipt or the integrated result requires new scientific computation not separately admitted. |

### WP-OSW-005 — payload and responsive baseline

| Field | Contract |
|---|---|
| Interfaces | IF-OSW-004–006, 012 |
| Design / rigor | DES-OSW-009, 010, 012, 015; CR-OSW-003–005, 012, 013, 016–018, 21–24 |
| Scenarios | VAL-SCN-OSW-001, 003, 006 |
| Product touches | Asset-family inventory, manifest payload classes, selected-view loader, measurement harness/evidence, responsive styles. |
| Discovery | Measure hosted and local critical-path bytes, request count, render/interaction proxy, viewport/zoom cases, and candidate custody strategy before setting thresholds. |
| Required fixtures | Selected versus unselected requests; integrity/load failure; same-origin allowlist; no storage/telemetry; narrow/zoom/reflow/touch; unchanged route/receipt access. |
| Forbidden | Arbitrary budget, eager custody payload, third-party preload, hidden limitation to satisfy layout, performance test that mutates accepted assets. |
| Stop condition | Measurement cannot distinguish critical, selected, on-demand, and external-custody payloads. |

### WP-OSW-006 — heat-budget challenge

| Field | Contract |
|---|---|
| Interfaces | IF-OSW-003, 007, 009–012 |
| Design / rigor | DES-OSW-006–008, 011, 012, 015; CR-OSW-001–13, 19, 21–25 |
| Scenarios | VAL-SCN-OSW-002, 006, 008 |
| Product touches | Explicit acquisition, analysis kernels, sensitivity/control results, receipts, admitted derivatives, research explanation. |
| Required result | Depth/time alternatives; native-term availability ledger; frozen case-selection rule; at least one control and one second case/product or explicit justified absence. |
| Forbidden | Remainder assignment, product crossing without separate identities, silent collocation/support change, cherry-picked generalization. |
| Stop condition | Source/rights/support unavailable for the proposed claim or independent calculation disagrees beyond named tolerance. |

### WP-OSW-007 — transport-tested zoning

| Field | Contract |
|---|---|
| Interfaces | IF-OSW-004, 007, 009, 010, 012, 015 |
| Design / rigor | DES-OSW-007–009, 012, 014, 015; CR-OSW-003–010, 013, 017, 019, 21–25 |
| Scenarios | VAL-SCN-OSW-004, 005, 008 |
| Product touches | Candidate definitions, diagnostic analyses/results, scorecard records, map/text presentation, receipts. |
| Required result | Each border exposes persistence, normal exchange, retention/leakage, convergence, vertical agreement/reversal, gate sensitivity, contradictions and unavailable fields. |
| Forbidden | Composite score hiding disagreement, assumed 11/22/56 outcome, appearance/count promotion, multipart convenience overriding physics. |
| Stop condition | Candidate/method changes after outcome inspection or unavailable evidence is coerced into neutral/passing evidence. |

### WP-OSW-008 — planetary comparison

| Field | Contract |
|---|---|
| Interfaces | IF-OSW-003, 004, 007, 010, 012, 014 |
| Design / rigor | DES-OSW-006, 007, 009, 012, 014, 015; CR-OSW-003–007, 010, 013, 017, 019, 21–25 |
| Scenarios | VAL-SCN-OSW-002, 007 |
| Product touches | Comparison record, evidence adapters, optional map/diagram, guide/scene, receipts and fixtures. |
| Required result | Independent quantities; shared property/mechanism; forcing, stratification, rotation, depth, compressibility, boundary and observation differences; weakening/falsification outcome. |
| Forbidden | Cloud color/temperature as full-depth heat, visual resemblance as mechanism, Earth vocabulary exported without regime check, planetary story overriding Earth evidence. |
| Stop condition | Either side lacks admitted identity or the weakening outcome cannot be stated honestly. |

### WP-OSW-009 — lifecycle and release

| Field | Contract |
|---|---|
| Interfaces | IF-OSW-005, 006, 010, 012, 013 |
| Design / rigor | DES-OSW-007, 010, 012, 013, 015; CR-OSW-002–005, 010–13, 018–24 |
| Scenarios | VAL-SCN-OSW-006 |
| Product touches | Lifecycle registry, pure reconciler, candidate packet, status/citation/publication surfaces, deploy adapter, hosted smoke/rollback evidence. |
| Discovery | Identify host, immutable hosted-commit proof, staging target, atomic or compensating retain/restore mechanism, and owner decision path before effectful code. |
| Required fixtures | One-state lifecycle; drift per release surface; stale review; vetoed admission; undeclared payload/request; failed deploy/smoke retaining prior metadata/site; successful hosted commit. |
| Forbidden | Reconciler deploying, role review granting endorsement/release, candidate updating current/citation, secret-bearing logs, public promotion without owner decision. |
| Stop condition | Retain/restore cannot be rehearsed or hosted bytes cannot be tied to the candidate commit. |

## Common execution and closure contract

Every package execution record must name its immutable baseline SHA, branch or
worktree, owned files, parent IDs, diagnostic/fixture IDs, affected profiles,
current waivers, and expected tree mutations before editing.

| Level | Required for all packages | Package-specific addition |
|---|---|---|
| L0 | Affected-profile syntax/parse/link/schema checks, focused tests, `git diff --check`, before/after tree inspection. | Named in Verification before `ready`. |
| L1 | Full offline pytest and unittest discovery, compile and JS syntax, interface/invariant fixtures, generated integrity where affected. | Boundary integration and compatibility paths. |
| L2 | Required VAL-SCN or controlled surrogate, relevant rendered/scientific/release evidence, all applicable native-role decisions. | Independent/second-case, browser/AT, or staged-host proof according to package. |

V closure is pending for every proposed package:

| V area | Required closeout |
|---|---|
| Need / CONOPS | Confirm parent scenario and degraded path remain satisfied. |
| Requirements / Specification | Record affected IDs and no orphaned/contradicted controls. |
| Architecture / Interface | Verify allowed dependency direction and interface compatibility/version result. |
| Design / Code Rigor | Record invariants, profiles, metrics, waiver changes, and negative paths. |
| Implementation | Identify commits, outputs, diagnostics, fixtures, and deviations. |
| Verification | Record controlled command IDs and results; tests cannot repair candidate. |
| Validation | Execute applicable scenario or record accepted deferral/blocker without claiming readiness. |
| Trace / Gate | Update trace and role/gate decision; keep package open on any required pending/blocked lane. |

## Assurance and role lanes

| Package | Systems / trace | V&V / software | Source custody | Access / cartography | Science / comparison | Configuration / release |
|---|---|---|---|---|---|---|
| 001 | required | KEEL required | SOUNDER required | CHART/HARBOR as affected | CURRENT; ORBIT for comparison contract | LOGBOOK required |
| 002 | required | KEEL required | SOUNDER consulted | HARBOR and BEACON required | CURRENT consulted | LOGBOOK required |
| 003 | required | KEEL required | SOUNDER required | CHART and HARBOR required | CURRENT required for quantity/support | LOGBOOK consulted |
| 004 | required | KEEL required | SOUNDER required | BEACON/HARBOR/CHART required | CURRENT required | LOGBOOK required |
| 005 | required | KEEL required | SOUNDER required for payloads | HARBOR/CHART required | CURRENT consulted | LOGBOOK privacy required |
| 006 | required | KEEL required | SOUNDER required | CHART as mapped | CURRENT required | LOGBOOK required |
| 007 | required | KEEL required | SOUNDER required | CHART/HARBOR required | CURRENT required | LOGBOOK required |
| 008 | required | KEEL required | SOUNDER required | CHART/HARBOR/BEACON required | CURRENT and ORBIT required | LOGBOOK required |
| 009 | required | KEEL required | SOUNDER for artifact identities | HARBOR for journeys | Domain vetoes retained | LOGBOOK and owner required |

No package closes while a required lane is pending or blocked. OSW is
explanatory research, not operational forecasting/navigation or intervention;
the safety/mission-impact lane is therefore a required non-authority inspection
rather than a safety-critical certification.

## Orphan and readiness check

- [x] Every accepted `REQ-OSW-*` is assigned or dispositioned.
- [x] Every `SPEC-OSW-*` is assigned, including all discovery-required items.
- [x] Every package names affected `IF-OSW-*` and `PKG-OSW-*` boundaries.
- [x] Every package names applicable `DES-OSW-*` and `CR-OSW-*` controls.
- [x] Every package has entry, exit, stop, fixture, and L0/L1/L2 expectations.
- [x] VTRACE-only closeout is separate from product behavior.
- [x] No package is cleanup without a product requirement or discovery source.
- [x] Verification assigns controlled command/fixture IDs; target evidence remains pending.
- [x] Native-role planning review resolves every P1/P2 finding.

Package status remains `proposed` or `proposed-deferred`; execution is not
authorized by this file.

## Source links

- [Implementation Plan](IMPLEMENTATION_PLAN.md)
- [Requirements](REQUIREMENTS.md)
- [Specification Baseline](SPECIFICATION_BASELINE.md)
- [Package Boundaries](PACKAGE_BOUNDARIES.md)
- [Interfaces](INTERFACES.md)
- [Detailed Design](DESIGN.md)
- [Code Rigor](CODE_RIGOR.md)
- [Central roadmap](../../ROADMAP.md)
- [PITFALL register](../../design/pitfalls/README.md)
- [Implementation Planning roles review](../../signals/roles/check/implementation-planning-roles-check-2026-09-07.md)

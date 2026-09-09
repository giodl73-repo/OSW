# OSW Package Boundaries

Status: settled with the Architecture-stage native-role fixed point, 2026-09-06

## Scope

This companion inventory makes the logical boundaries in
[ARCHITECTURE.md](ARCHITECTURE.md) concrete against the existing repository.
A boundary is an authority seam, not a required new package. “Current unit”
records where behavior is found now; “target allocation” records what that unit
may own after later design. No file move, schema, framework, or implementation
work is authorized here.

## Boundary inventory

| ID | Current unit | Language/toolchain | Accountable role | Target responsibility | Public interfaces | Downstream consumers |
|---|---|---|---|---|---|---|
| PKG-OSW-001 | `README.md`, `atlas/index.html`, `research/index.html` | Markdown, HTML, CSS | BEACON | Public entry routes and complete secondary research index. | IF-OSW-001, 005 | Readers; PKG-002 |
| PKG-OSW-002 | State/navigation portions of `atlas/app.js` and semantic controls | Browser JavaScript, HTML | HARBOR | Canonical accepted URL/navigation/selection/focus/announcement state. | IF-OSW-001, 002 | PKG-003, 004 |
| PKG-OSW-003 | Atlas explanation panels, D-series content, guides | JavaScript, HTML, Markdown | BEACON | Assemble admitted finding, limitation, evidence identity, and receipt route. | IF-OSW-003 | Readers; PKG-001, 002 |
| PKG-OSW-004 | Rendering portions of `atlas/app.js`, SVGs, `atlas/styles.css` | Browser JavaScript, SVG, CSS | CHART | Render projection, masks, classes, legends, interactions, and equivalent text from accepted state/data. | IF-OSW-004 | Readers; PKG-002, 003 |
| PKG-OSW-005 | `atlas/data/`, admitted `figures/`, public research JSON | JSON, JavaScript data modules, SVG | SOUNDER | Immutable selected-view web derivatives and their evidence/receipt identities. | IF-OSW-003, 004 | PKG-002–004 |
| PKG-OSW-006 | `SOURCE-REGISTER.md`, claims ledger, receipts, classifications, admission tests | JSON, CSV, Markdown, Python validation | SOUNDER for registry integrity; domain roles retain admission vetoes | Shared identities and composition of physical, evidence, map, access, proof, lifecycle, and comparison decisions. | IF-OSW-003–006 | PKG-003–005, 009, 010 |
| PKG-OSW-007 | Fetch/download/intake scripts, source receipts, acquired inputs | Python, provider tooling | SOUNDER | Explicit acquisition, request/response identity, rights posture, immutable accepted custody. | Internal; exact interface deferred | PKG-008, 009 |
| PKG-OSW-008 | `analysis/analyze_*`, generators, scientific helpers | Python, optional NetCDF/xarray stack | CURRENT | Scientific transformation, diagnostics, sensitivity, typed results, display derivatives. | Internal; exact interface deferred | PKG-005, 006, 009 |
| PKG-OSW-009 | `analysis/test_*.py`, node syntax checks, `.github/workflows/validate.yml` | Python unittest/pytest, Node, CI | KEEL | Read-only offline verification, failure isolation, admission and release evidence. | Verification records deferred | PKG-006, 010 |
| PKG-OSW-010 | Publication/status/citation files and hosting workflow | Git, CI/hosting, Markdown/YAML | LOGBOOK | Lifecycle reconciliation, immutable candidate, measurement, deploy/smoke, retain/restore. | IF-OSW-005, 006 | Hosted site, maintainers |
| PKG-OSW-011 | `guides/`, `plans/`, `signals/`, `.roles/`, `docs/vtrace/`, history | Markdown, CSV, BibTeX | LOGBOOK | Research explanation and internal governance record; expert audit routes. | IF-OSW-001, 005 where explicitly published | Humans; constrains all boundaries |

## Dependency direction

| From | To | Allowed? | Rationale | Verification concept |
|---|---|---|---|---|
| 001 | 002, 003, 004 | yes, orchestration | Entry launches routes and connects state, presentation, and rendering without owning their semantics. | Route/link/import tests. |
| 002 | 005 | yes, read-only | Pure state transitions may validate against accepted identity/compatibility metadata. | State transition/request tests. |
| 003, 004 | 002 | yes, read-only | Presentation and rendering project the one accepted state. | Cross-output state-equivalence tests. |
| 002 | 007, 008, external providers | no | Reader state cannot invoke acquisition or scientific computation. | Runtime import/request inspection. |
| 003 | 005, 006 outputs | yes, read-only | Claims consume admitted identities and web assets. | Claim/receipt binding tests. |
| 003 | 008 | no | Presentation cannot calculate or repair science. | Dependency and uncontrolled-constant inspection. |
| 004 | 002, 005 | yes, read-only | Rendering consumes accepted state and typed display evidence. | Renderer contract tests. |
| 004 | 003, 006 authority | no | Rendering cannot author claims or admission state. | Negative boundary tests. |
| 005 | 006, 008 outputs | generated lineage only | Display artifacts descend from admitted scientific results. | Checksums and lineage. |
| 007 | external providers | yes, explicit | Acquisition is the only provider-facing boundary. | Receipted dry-run/fault tests. |
| 008 | 007, 006 contracts | yes | Transformations consume pinned inputs and emit controlled identities. | Scientific fixtures. |
| 009 | 001–011 | yes, read-only | Verification observes all candidates without repairing them. | Clean-worktree/mutation check. |
| 010 | 006, 009, 011 | yes, read-only | Release uses admission, gate evidence, and owner/status decisions. | Reconciliation fixture. |
| 011 | 001 | link/generation only | Selected public research material may be linked or built into public pages. | Static request/navigation inspection. |
| 001–005 | internal VTRACE/role state in 011 | no runtime authority | Engineering process cannot become public product state. | Runtime data/request inspection. |

## Boundary rules

| Boundary ID | Allowed changes | Forbidden changes | Change-control trigger |
|---|---|---|---|
| PKG-OSW-001 | Improve route language, hierarchy, and index reachability. | Hide accepted corpus destinations or turn internal stage status into visitor navigation. | Primary route/destination/status semantics change. |
| PKG-OSW-002 | Add validated state dimensions and pure transitions. | Silent fallback, duplicate state authorities, or scientific calculation. | URL/state/default/history semantics change. |
| PKG-OSW-003 | Simplify language within an admitted claim ceiling. | Hide limitation/receipt, create stronger claims, or copy uncontrolled values. | Finding, limitation, evidence identity, or receipt route changes. |
| PKG-OSW-004 | Add projections/encodings that pass admission. | Infer masks/classes/uncertainty or support invalid comparison. | Projection, palette, boundary, mask, legend, or text-equivalent change. |
| PKG-OSW-005 | Add web derivatives with lineage and selective-load classification. | Mutable provider endpoints, unreceipted values, or heavyweight eager inputs. | Artifact identity, payload class, quantity, support, or receipt changes. |
| PKG-OSW-006 | Add versioned adapters, shared identities, and composed domain dispositions. | Rewrite source truth, manufacture evidence, overrule a domain veto, or confer release/endorsement. | Shared contract, evidence class, claim ceiling, boundary, lifecycle, or admission-composition semantics change. |
| PKG-OSW-007 | Add explicit receipted provider paths. | Default-test/runtime downloads or overwriting accepted artifacts on failure. | Provider/product/request/license/custody changes. |
| PKG-OSW-008 | Add bounded analyses and sensitivities. | Publish directly, silently coerce mismatches, or rename residuals/processes. | Quantity, algorithm, support, collocation, sign/reference, or dependency changes. |
| PKG-OSW-009 | Add deterministic read-only checks and fixtures. | Repair outputs, require network by default, or declare scientific endorsement. | Gate command, coverage family, fixture, or failure-severity changes. |
| PKG-OSW-010 | Reconcile and publish accepted candidates. | Change science, promote before owner/hosted proof, or update current metadata non-atomically. | Lifecycle, target, version, deploy, rollback, or citation change. |
| PKG-OSW-011 | Preserve controlled research/governance records and publish selected explanations. | Become runtime truth, expose private paths/secrets, or imply peer review/endorsement. | Public/internal boundary or controlled decision changes. |

## Language tailoring

Detailed L0/L1/L2 rigor profiles remain for the Code Rigor stage. Architecture
sets only the controlling direction.

| Boundary | Profile direction | L0 minimum now | L1/L2 decision deferred |
|---|---|---|---|
| 001–004 | Browser/public experience | Syntax, local links, semantic state, non-color/text equivalence. | Browser matrix, responsive thresholds, component rigor. |
| 005–008 | Data/scientific production | Schema/shape/checksum/range/mask/quantity assertions and deterministic local fixture paths. | Common representations, family-specific numerics, independent reproduction. |
| 009 | Verification | Same documented offline commands locally and in CI; negative fixtures. | Coverage thresholds and release-grade fault matrices. |
| 010 | Release | Immutable commit/status reconciliation and current hosted checks where available. | Atomic deployment/retain-restore mechanism. |
| 011 | Research/governance | Local links, artifact identity, status/authority boundaries. | Publication generation and immutable external-review representation. |

## Generated artifact classes

This is an architectural inventory, not the complete family registry required
by `SPEC-UNK-OSW-003`.

| Class | Current examples | Source of truth | Allowed public role | Required boundary |
|---|---|---|---|---|
| Scientific result | `research/osw-*.json` | Pinned inputs + PKG-008 method | Evidence/receipt target, not necessarily direct display. | 006, 008, 009 |
| Display-ready field | `atlas/data/*.js`, selected JSON | Scientific result or receipted source derivative | Selected-view atlas input. | 005, 006, 009 |
| Figure/map | `figures/*.svg` | Generator + result/geometry/contract | Standalone or integrated admitted view. | 004–006, 009 |
| Registry/table | claims ledger, classifications, object/geometry registers | Controlled source records and export logic | Expert audit and admission input. | 006, 009, 011 |
| Public prose/status | README, guides, preview/publication/citation surfaces | Admitted claims + owner/release decisions | Entry, explanation, release identity. | 001, 003, 006, 009–011 |
| Review/governance record | `signals/roles/check/`, `docs/vtrace/` | Immutable reviewed artifact + role/gate decision | Internal control; optional expert audit link only. | 009–011 |

## Open boundary questions

| ID | Question | Must be answered by | Owner |
|---|---|---|---|
| PKG-UNK-OSW-001 | Which existing receipt/claim/boundary variants need preservation, adaptation, migration, or retirement? | Interfaces | SOUNDER |
| PKG-UNK-OSW-002 | What exact URL state vocabulary/version and compatibility interval are supported? | Interfaces | HARBOR |
| PKG-UNK-OSW-003 | Which artifact families are admitted and which are research-only, experiment, degraded, or superseded? | Interfaces / Implementation Plan | LOGBOOK |
| PKG-UNK-OSW-004 | Which assets are critical-path display derivatives versus on-demand evidence versus external custody? | Design / Validation | KEEL |
| PKG-UNK-OSW-005 | Does physical separation inside `atlas/app.js` materially improve contract verification, and at what granularity? | Design | KEEL |
| PKG-UNK-OSW-006 | Which deployment mechanism can prove hosted commit and retain/restore atomically? | Implementation Plan | LOGBOOK |

## Boundary gate

Decision: pass_with_risk

- [x] Every logical component has a concrete current-repository evidence seam.
- [x] Browser, science, admission, verification, release, and governance authority are separated.
- [x] Dependency direction is explicit and prohibits dangerous reverse dependencies.
- [x] Current units are not mistaken for mandatory future packages.
- [x] Detailed schema, API, algorithm, rigor, performance, validation, and deployment choices remain deferred.
- [x] Eight-role review resolves all Architecture-stage P1/P2 findings.

Exact contract shapes remain unopened Interfaces work. The Architecture-stage
[native-role review](../../signals/roles/check/architecture-roles-check-2026-09-06.md)
records the fixed-point decision.

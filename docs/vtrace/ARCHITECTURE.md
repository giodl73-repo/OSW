# OSW Architecture

Status: settled at native-role fixed point, 2026-09-06

## Scope

Repo: OSW — Ocean States of the World

This stage allocates the 45 controlled specification items to logical system
boundaries. It preserves the static, local-first product shape while separating
scientific production from public interpretation and release governance. It
does not choose contract field layouts, URL syntax, frameworks, deployment
providers, performance budgets, zoning algorithms, validation thresholds, or
implementation work packages. Those remain owned by later stages and the
unknowns already recorded in the Specification Baseline.

## Architecture summary

OSW is a **build-time evidence system with a thin static reader**. Scientific
providers are contacted only by explicit acquisition tools. Offline scientific
pipelines transform pinned inputs into identified results and display-ready
derivatives. Admission gates bind results, claims, limitations, maps, and
receipts before the static publication boundary exposes them. The browser may
navigate, select, filter, project, and explain admitted evidence; it may not
silently acquire live scientific data, calculate new scientific quantities,
aggregate provinces, broaden claim ceilings, or mutate evidence receipts.

```text
external scientific providers
          |
          v  explicit, receipted acquisition only
  source custody  --->  offline scientific pipelines
                              |
                              v
                 result + receipt + claim ceiling
                              |
                              v
                  admission and verification gate
                     |                    |
                     v                    v
             display-ready assets   release packet
                     |                    |
                     v                    v
           static atlas reader  <--- verified hosted release

research/governance corpus constrains admission and release;
it is not a runtime dependency or a visitor-facing control plane.
```

The principal architectural invariant is one-way authority: presentation may
select from accepted evidence but cannot strengthen, repair, or replace it.

## Architectural decisions

| Decision ID | Decision | Rationale | Controlled by | Status |
|---|---|---|---|---|
| ADR-OSW-001 | Keep the released product statically hostable and local-data-first. | Preserves offline use, privacy, reproducibility, and bounded failure without requiring accounts or a scientific provider at runtime. | `SPEC-OSW-023`, `024`, `044`, `045`; `SPEC-NF-OSW-001`, `005` | accepted architecture |
| ADR-OSW-002 | Separate scientific production from browser presentation at an admitted-artifact boundary. | Prevents client code from inventing quantities, province aggregates, budget closure, or receipts. | `SPEC-OSW-010`–`012`, `019`–`024` | accepted architecture |
| ADR-OSW-003 | Use one canonical public navigation/state responsibility even if rendering and content remain separately implemented. | Keeps URL, focus, selection, text, and visual states coherent across routes and modes. | `SPEC-OSW-003`, `005`, `008`, `009`, `027`–`030`, `041`–`043` | accepted architecture |
| ADR-OSW-004 | Keep cartographic rendering downstream of typed display evidence and upstream of equivalent visual/text outputs. | A renderer may project and encode accepted fields but may not infer evidence class, boundary authority, masks, or scientific claims. | `SPEC-OSW-021`, `022`, `025`–`028` | accepted architecture |
| ADR-OSW-005 | Treat receipts, quantity identities, claim ceilings, boundary classes, and lifecycle states as shared contracts owned outside individual figures. | Makes artifact-specific safeguards eligible for system-wide admission and drift checks. | `SPEC-OSW-011`–`020`, `035`–`038` | accepted architecture; representation deferred |
| ADR-OSW-006 | Separate admission from release. | A scientifically admitted artifact may still be an experiment or review preview; only a reconciled release packet and verified hosted transition make it current. | `SPEC-OSW-034`–`040` | accepted architecture |
| ADR-OSW-007 | Keep VTRACE, role reviews, and internal readiness records outside visitor navigation and ocean-object semantics. | Engineering control must not become a second public product or contaminate scientific vocabulary. | Mission boundary; roadmap operating rule 7 | accepted architecture |
| ADR-OSW-008 | Preserve the research corpus as a secondary expert surface behind the three-route public entry. | The guided experience can improve without deleting auditability or legacy destinations. | `SPEC-OSW-001`–`007` | accepted architecture |
| ADR-OSW-009 | Keep Earth/gas-giant comparison inside the same claim-admission path, with ORBIT as an added review lens rather than an independent truth system. | Planetary analogy cannot bypass Earth quantity identity, evidence, or claim ceilings. | `SPEC-OSW-015`, `016` | accepted architecture |
| ADR-OSW-010 | Compose admission from domain-owned decisions rather than one universal gatekeeper. | CURRENT retains physical-claim authority, SOUNDER evidence identity, CHART map fidelity, HARBOR equivalent access, KEEL executable proof, LOGBOOK lifecycle/release truth, and ORBIT comparison transfer; the shared registry coordinates identities but cannot overrule a domain rejection. | `SPEC-OSW-006`–`028`, `033`–`045` | accepted architecture |

## Logical components

Logical components define authority and dependency direction. They are not a
mandate to create one directory, class, service, or package per row.

| Component ID | Component | Boundary ID | Responsibility | Parent spec IDs | Interfaces | Current evidence |
|---|---|---|---|---|---|---|
| ARCH-OSW-001 | Public entry and research index | PKG-OSW-001 | Present the three primary routes, preserve the secondary corpus index, and expose release-safe status without becoming a scientific calculator. | 001–007, 017, 018 | IF-OSW-001, 005 | `README.md`, `atlas/index.html`, `research/index.html`, guides |
| ARCH-OSW-002 | Canonical reader state and navigation | PKG-OSW-002 | Own accepted province/object/mode/depth/event/scene/projection state, transitions, fallback, history, focus context, and announcements. | 003, 005, 008, 009, 027–030, 041–043 | IF-OSW-001, 002 | URL and selection logic in `atlas/app.js`; atlas tests |
| ARCH-OSW-003 | Scene and claim presentation | PKG-OSW-003 | Assemble admitted finding, strongest limitation, evidence class, and receipt route without changing scientific meaning. | 004–007, 011, 012, 015–020 | IF-OSW-003 | D1–D14 figures/receipts, guides, claims ledger |
| ARCH-OSW-004 | Cartographic renderer and text equivalent | PKG-OSW-004 | Project accepted display evidence, preserve masks/seams/poles/coasts/boundary classes, and emit synchronized visual and data-oriented text outputs. | 008–010, 021, 022, 025–030 | IF-OSW-004 | `atlas/app.js`, interactive SVGs, projection experiments, atlas tests |
| ARCH-OSW-005 | Display-ready evidence bundle | PKG-OSW-005 | Carry only admitted web-scale fields, geometries, descriptors, and receipt identities needed by selected public views. | 010–012, 019–028, 031, 032 | IF-OSW-003, 004 | `atlas/data/`, selected `research/*.json`, `figures/` |
| ARCH-OSW-006 | Contract registry and admission coordinator | PKG-OSW-006 | Preserve shared quantity, receipt, claim-ceiling, boundary, map, analogy, artifact-family, and lifecycle identities and compose domain-owned admission decisions without overruling them. | 006, 007, 011–022, 025, 026, 033–038, 044, 045 | IF-OSW-003–006 | Source register, receipt collection, claims ledger, tests, role reviews |
| ARCH-OSW-007 | Scientific acquisition and custody | PKG-OSW-007 | Explicitly acquire or register source inputs, record request/response and rights identity, preserve accepted inputs on failure, and never run in the public reader. | 019, 020, 023, 024, 033, 034 | Internal acquisition boundary; exact contract deferred | Acquisition scripts, source register, committed inputs and receipts |
| ARCH-OSW-008 | Offline scientific transformation | PKG-OSW-008 | Transform pinned inputs into typed scientific results, sensitivity records, masks, and display derivatives while preserving provenance and stopping on mismatches. | 010–016, 019–024, 033, 034 | Internal evidence boundary; exact contract deferred | Python analysis/generation scripts and research outputs |
| ARCH-OSW-009 | Verification and degraded-operation gate | PKG-OSW-009 | Exercise contracts offline, isolate optional failures, check generated artifacts and browser syntax/state, and produce admission/release evidence without rewriting artifacts. | 012, 016, 018, 020, 022–028, 030–038, 040, 043–045 | Verification records; exact shape deferred | `analysis/test_*.py`, CI workflow, syntax commands |
| ARCH-OSW-010 | Release reconciler and publisher | PKG-OSW-010 | Bind lifecycle state, commit, status surfaces, citation, source register, artifact identities, role findings, hosted target, measurements, smoke evidence, and retain/restore outcome. | 031, 032, 035–045 | IF-OSW-005, 006 | Publication checklist, preview status, citation, Git/GitHub Pages history |
| ARCH-OSW-011 | Research and governance corpus | PKG-OSW-011 | Preserve guides, plans, source signals, role reviews, VTRACE records, history, and expert audit routes while remaining outside reader runtime authority. | 001, 006, 013–018, 033–038 | IF-OSW-001, 005 | `guides/`, `plans/`, `signals/`, `docs/vtrace/`, history files |

## Authority boundaries

| Boundary | May do | Must not do |
|---|---|---|
| Public reader | Select, route, project, filter, zoom, summarize, and link admitted assets. | Fetch mutable scientific providers, derive new scientific quantities, aggregate provinces, assign residuals, widen claims, edit receipts, or decide release state. |
| Scene/claim presentation | Choose plain-language expression within the admitted claim ceiling and keep the limitation/receipt adjacent. | Turn interpretation into observation, hide the limiting condition, or copy uncontrolled quantitative constants. |
| Cartographic renderer | Transform coordinates for a declared projection and render declared masks/classes/scales. | Infer missing values, repair support, invent object borders, change evidence class, or permit unsupported metric comparisons. |
| Contract registry/admission coordination | Preserve shared identities, collect domain decisions, and report why a candidate does not pass. | Overrule a CURRENT/SOUNDER/CHART/HARBOR/KEEL/LOGBOOK/ORBIT rejection, manufacture evidence, endorse external science, or promote a release. |
| Scientific pipeline | Acquire explicitly, compute declared quantities, preserve alternatives, and emit receipts/results. | Publish directly, overwrite accepted artifacts after failed acquisition, or substitute an attractive proxy for a missing term. |
| Verification gate | Observe and reject contract violations reproducibly. | Mutate the candidate to make tests pass or treat network availability as the default gate. |
| Release boundary | Reconcile and publish only admitted, verified, owner-approved artifacts. | Reinterpret science, waive unknowns silently, or update citation/current status before hosted verification. |
| Governance corpus | Record intent, review, evidence, history, and controlled decisions. | Become public atlas controls, ocean-object categories, or an alternate runtime database. |

## Package and language boundaries

The detailed inventory is recorded in
[PACKAGE_BOUNDARIES.md](PACKAGE_BOUNDARIES.md). Architecture-level decisions
are summarized here.

| Boundary ID | Current/future unit | Language/toolchain | Responsibility | Allowed dependencies |
|---|---|---|---|---|
| PKG-OSW-001 | Public entry/index surfaces | HTML, Markdown, CSS | Entry routes and expert index | Accepted navigation metadata and release-safe content only |
| PKG-OSW-002 | Reader state/navigation | Browser JavaScript + semantic HTML | Canonical client state and pure transitions | Read-only contract metadata from PKG-005; presentation/rendering consume state rather than becoming state dependencies |
| PKG-OSW-003 | Scene/claim presentation | Browser JavaScript, HTML, Markdown-derived content | Finding/limitation/evidence/receipt assembly | PKG-005, PKG-006 outputs only |
| PKG-OSW-004 | Cartographic rendering | Browser JavaScript, SVG, CSS | Map projection, encoding, interaction, text equivalent | PKG-002 and PKG-005 only |
| PKG-OSW-005 | Display-ready bundle | JSON, JavaScript data modules, SVG | Immutable web inputs for admitted views | Produced from PKG-006/008; read by PKG-002/003/004 |
| PKG-OSW-006 | Contract registry/admission coordination | JSON/CSV/Markdown now; representation deferred | Shared identities and composition of domain-owned admissions | Reads pipeline outputs and controlled docs; feeds gates and bundles but cannot override domain vetoes |
| PKG-OSW-007 | Acquisition/custody | Python and provider-specific tooling | Explicit source acquisition and request/rights receipts | External providers only here; writes pinned custody inputs |
| PKG-OSW-008 | Scientific transformation | Python with pinned optional scientific libraries | Analysis, sensitivity, result and display generation | PKG-007 custody inputs and controlled contracts |
| PKG-OSW-009 | Verification | Python unittest/pytest, Node syntax checks, CI | Offline contract and artifact gates | Read-only across all candidate boundaries |
| PKG-OSW-010 | Release/publishing | Git, CI/hosting workflow, metadata/docs | Reconciliation, measurement, deployment, smoke, retain/restore | Only admitted outputs plus owner decision and verification evidence |
| PKG-OSW-011 | Research/governance corpus | Markdown, CSV, BibTeX, role/VTRACE records | Human-readable scientific and engineering record | May constrain all boundaries; no reader runtime authority |

## Dependency direction

| From | To | Allowed | Rationale | Verification concept |
|---|---|---|---|---|
| Public entry/shell 001 | Reader state, scenes, and renderer 002–004 | yes, orchestration only | The shell connects independently owned reader concerns. | Import/event and state-owner inspection. |
| Reader state 002 | Display bundle 005 | yes, read-only | State validation may use accepted identity/compatibility metadata. | Pure state-transition fixtures. |
| Scene and renderer 003–004 | Reader state 002 | yes, read-only | Presentation and rendering project one accepted state. | State-equivalence fixtures. |
| Public reader boundaries 001–004 | Display bundle 005 | yes, read-only | Static reader consumes admitted web assets. | Request inventory and mutation guard. |
| Public reader boundaries 001–004 | Acquisition 007 or external provider | no | Runtime science would break offline, privacy, custody, and reproducibility boundaries. | Network/request negative test. |
| Public reader boundaries 001–004 | Scientific transformation 008 | no | Scientific quantities must be produced and reviewed before publication. | Import/runtime capability inspection. |
| Cartographic renderer 004 | Scene claims 003 | no authority | Renderer reports state; it cannot create the scientific claim. | Claim constants absent from rendering layer. |
| Acquisition 007 | External providers | yes, explicit only | Source refresh is a separately invoked, receipted operation. | Dry-run/fault injection/request receipt. |
| Transformation 008 | Acquisition custody outputs 007 | yes, pinned input | Reproducible science begins from identified bytes or documented reconstruction. | Checksum and contract validation. |
| Transformation 008 | Admission contracts 006 | yes | Outputs must declare quantities/support/claim ceilings. | Schema/semantic fixtures, representation later. |
| Display bundle 005 | Transformation results 008 | yes, generated lineage | Web derivatives retain trace to scientific results. | Result/display checksum lineage. |
| Admission coordination 006 | Research/governance corpus 011 | yes, controlled input | Requirements, sources, reviews, and limitations constrain admission; each native domain retains its veto. | Trace and domain-disposition inspection. |
| Verification 009 | All candidate boundaries | yes, observational | The gate may use ephemeral outputs but cannot repair or overwrite accepted candidates. | Clean-worktree/mutation check. |
| Release 010 | Admission 006 and verification 009 | yes | Publication consumes decisions/evidence but cannot replace them. | Reconciled release fixture. |
| Governance corpus 011 | Public reader runtime | no runtime dependency | Public pages may be generated or linked, but internal process is not a control plane. | Static request and navigation inspection. |

## Primary data flows

### Scientific evidence production

```text
question + claim ceiling
  -> source/rights decision
  -> explicit acquisition or accepted local fixture
  -> source receipt + immutable input identity
  -> transformation contract
  -> typed result + sensitivity/mask record
  -> display derivative + lineage
  -> admission checks
  -> admitted display bundle
```

Failure before admission leaves the prior accepted artifacts unchanged and
produces a bounded diagnostic; it does not emit a degraded scientific claim.

### Public reader state

```text
route or compatible URL
  -> parse candidate state
  -> validate compatibility
  -> accepted state or announced safe fallback
  -> load selected-view necessary bundle
  -> synchronized visual + text + focus/announcement state
  -> finding + strongest limitation + receipt route
```

The selected view may change projection, depth, or presentation, but not the
underlying quantity identity, missingness, evidence class, or claim ceiling.

### Admission and release

```text
candidate artifact family
  -> scientific/data/cartographic/accessibility/reproducibility admission
  -> lifecycle decision (never implicit release)
  -> immutable release candidate + reconciled packet
  -> owner decision
  -> deployment + hosted commit/primary-journey smoke
  -> atomic current/citation update OR prior release retained/restored
```

## External and optional dependencies

| Dependency class | Purpose | Boundary/risk | Architectural containment | Verification |
|---|---|---|---|---|
| Scientific data providers | Source observations, analyses, reanalyses, and model fields. | Mutable services, access control, licensing, changed archives, large payloads. | Reachable only from explicit acquisition; no public-reader or default-test dependency. | Local fixtures, request receipts, checksum/schema fault cases. |
| Optional Python scientific libraries | NetCDF and multidimensional analysis. | Absent or version-sensitive environments. | Isolated to scientific transformation/acquisition paths and pinned where applicable. | Dependency-removal and representative regeneration tests. |
| Natural Earth/coastline sources | Geographic context and masks. | Version/licensing/projection lineage. | Pinned custody and derived display geometry with receipt. | Geometry checksum, seam, coast, mask tests. |
| Browser platform | Static interaction, SVG, URL/history, accessibility APIs. | Browser variance and unsupported state. | Standards-based thin reader; controlled compatibility and responsive matrix later. | Multi-browser, keyboard, zoom, reduced-motion inspection. |
| Git/CI/hosting | Version identity, checks, static publication. | Drift between commit, hosted bytes, metadata, and rollback state. | Confined to release boundary with immutable candidate and post-deploy proof. | Deliberate mismatch and fault-injected release rehearsal. |

## Failure modes

| Failure ID | Failure mode | Impact | Architectural mitigation | Evidence parent |
|---|---|---|---|---|
| FAIL-OSW-001 | Browser reaches a live/mutable scientific source. | Non-deterministic, privacy-visible, possibly unavailable public state. | Prohibit reader-to-provider dependency; publish only admitted local assets. | `SPEC-OSW-023`, `024`, `044`, `045` |
| FAIL-OSW-002 | Browser derives or aggregates a stronger quantity. | False heat, transport, convergence, or province claim. | Build-time science boundary and display-bundle claim ceiling. | `SPEC-OSW-010`–`012`, `019`, `020` |
| FAIL-OSW-003 | Renderer repairs or conflates masks/seams/support. | Fabricated ocean objects or values. | Typed support enters renderer; shared cartographic admission tests every family. | `SPEC-OSW-021`, `022`, `025`, `026` |
| FAIL-OSW-004 | Visual, URL, text, and announced state diverge. | Different users receive different scientific states. | One reader-state authority; renderers are projections of accepted state. | `SPEC-OSW-009`, `027`, `028`, `043` |
| FAIL-OSW-005 | Figure/prose survives after receipt/result changes. | Claim/artifact drift. | Result-to-display-to-claim lineage and admission mutation tests. | `SPEC-OSW-019`, `020`, `033`, `034` |
| FAIL-OSW-006 | Optional dependency or provider failure becomes global. | Offline atlas/tests fail unrelated capabilities. | Separate acquisition/transformation capabilities; bounded diagnostics and prior-artifact preservation. | `SPEC-OSW-023`, `024`, `033`, `034` |
| FAIL-OSW-007 | Scientific admission implies public release. | Preview or experiment becomes current by implication. | Separate admission and lifecycle/release authorities. | `SPEC-OSW-035`–`040` |
| FAIL-OSW-008 | Internal governance becomes visitor-facing state. | Confusing second product and polluted scientific ontology. | No runtime dependency from reader to VTRACE/role/readiness records. | Mission boundary; `ADR-OSW-007` |
| FAIL-OSW-009 | Heavy evidence is eagerly loaded or committed without custody strategy. | Slow atlas and expensive clone while reproducibility remains unclear. | Display bundle contains selected-view web derivatives; custody remains separately receipted. | `SPEC-OSW-031`–`034`; DL-03 |
| FAIL-OSW-010 | Analogy bypasses scientific admission. | Visual rhyme presented as mechanism. | Planetary claims pass shared quantity/evidence controls plus ORBIT review. | `SPEC-OSW-015`, `016` |

## Specification-to-component coverage

| Spec range | Principal components | Coverage |
|---|---|---|
| 001–007 | 001, 002, 003, 011 | Entry, index, event journey, and claim context allocated. |
| 008–010 | 002, 004, 005 | Province/state behavior and non-aggregation allocated. |
| 011–018 | 003, 006, 008, 011 | Quantity, budget, zoning, analogy, and authority allocated. |
| 019–024 | 005–009 | Receipt lineage, masks, mismatch, acquisition, and degraded operation allocated. |
| 025–030 | 002, 004, 005, 006, 009 | Map contracts, equivalent state, accessibility, and reflow allocated. |
| 031–034 | 005, 007–010 | Payload measurement, custody, reproducibility, and intake allocated. |
| 035–040 | 006, 009–011 | Review identity, lifecycle, release packet, deploy proof, and rollback allocated. |
| 041–043 | 002, 009, 010 | URL compatibility and announced fallback allocated. |
| 044–045 | 001, 002, 009, 010 | No-collection boundary and controlled change allocated. |

## Open architectural risks

| Risk ID | Risk | Consequence | Control/disposition | Owner |
|---|---|---|---|---|
| ARCH-RISK-OSW-001 | `atlas/app.js` currently concentrates state, rendering, content, and data loading. | Future integrated scenes could create cross-state drift and untestable coupling. | Preserve logical boundaries now; decide physical separation only in Design/Implementation. | KEEL |
| ARCH-RISK-OSW-002 | Historical evidence/receipt shapes are heterogeneous. | Shared admission could either miss fields or force lossy migration. | Interfaces must inventory variants and define adapters/versioning without rewriting source truth. | SOUNDER |
| ARCH-RISK-OSW-003 | Display-ready versus custody payload membership is not inventoried. | DL-03 may persist despite thin-reader intent. | Measure hosted requests and classify artifact families before performance/custody design. | KEEL |
| ARCH-RISK-OSW-004 | Release host/rollback mechanism is unknown. | Atomic publication cannot yet be verified. | Allocate outcome to release boundary; select mechanism only in Implementation Plan. | LOGBOOK |
| ARCH-RISK-OSW-005 | A single canonical state owner could become a monolithic implementation. | Accessibility improves while maintainability degrades. | Canonical authority is a contract, not necessarily one file; Design must preserve separable pure transitions and render projections. | HARBOR |
| ARCH-RISK-OSW-006 | “Admission” could become bureaucratic rather than executable. | Research slows without improving correctness. | Interfaces/Verification must make admission minimum, typed, testable, and family-aware; null results remain valid. | CURRENT |
| ARCH-RISK-OSW-007 | The secondary corpus can still overwhelm the public entry. | Three routes exist nominally but do not improve comprehension. | Validation must test real route outcomes, not count navigation links. | BEACON |
| ARCH-RISK-OSW-008 | Comparison content could duplicate Earth evidence or receipt logic. | Planetary claims drift from the underlying ocean claim. | Comparison consumes shared admitted identities and adds only comparison-specific fields/review. | ORBIT |

## Architecture gate

Decision: pass_with_risk

- [x] Every controlled specification range is allocated to one or more logical components.
- [x] Authority and forbidden responsibilities are explicit.
- [x] Dependency direction prevents runtime science, silent aggregation, claim escalation, and implicit release.
- [x] Current file locations are evidence, not mandates for a framework rewrite.
- [x] Interfaces, thresholds, algorithms, deployment mechanisms, and work packages remain deferred.
- [x] VTRACE and role machinery remain outside visitor runtime semantics.
- [x] Detailed package boundaries and all eight native-role reviews reach a fixed point with no unresolved P1/P2.

Interfaces is authorized as the next separately reviewed stage but remains
unopened. Remaining risks have named later-stage dispositions and do not weaken
the one-way evidence authority or forbidden dependency directions.

## Source links

- [Specification Baseline](SPECIFICATION_BASELINE.md)
- [Detailed package boundaries](PACKAGE_BOUNDARIES.md)
- [Requirements](REQUIREMENTS.md)
- [PITFALL register](../../design/pitfalls/README.md)
- [Central roadmap](../../ROADMAP.md)
- [Native roles](../../.roles/ROLE.md)

The native-role fixed-point review is recorded in
[`architecture-roles-check-2026-09-06.md`](../../signals/roles/check/architecture-roles-check-2026-09-06.md).

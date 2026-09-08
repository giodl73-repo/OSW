# OSW Code Rigor

Status: settled at native-role fixed point, 2026-09-07

## Scope

Repo: OSW — Ocean States of the World

Risk level: **high** for scientific-claim, evidence-custody, accessibility-state,
and release logic; medium for presentation-only changes; not safety-critical
because OSW explicitly does not provide forecasts, warnings, navigation,
intervention, or operational decisions.

Language/toolchain: Python; browser JavaScript; semantic HTML/CSS; SVG;
JSON/CSV/Markdown/BibTeX/YAML; Git and static-host CI.

These constraints govern future implementation against the settled Design.
They do not assert that every historical file already conforms. Existing
concentration and heterogeneous records have explicit migration waivers below;
new or materially changed critical logic must meet the tailored profile.

## Rigor levels

| Level | Meaning | Required use |
|---|---|---|
| L0 | Fast local structural integrity. | Every changed surface before review. |
| L1 | Boundary behavior and negative cases. | Every interface-affecting change. |
| L2 | Cross-boundary scenario, independent scientific check, browser/user workflow, or release rehearsal. | High-risk scientific claim, state/accessibility, admission, privacy, or release changes. |

Passing a higher level does not waive lower levels. Network acquisition is
never part of the default L0/L1 gate.

## Coding constraints

| ID | Constraint | Applies to | Verification | Exception rule |
|---|---|---|---|---|
| CR-OSW-001 | A new or materially changed hand-authored function has a 60-logical-line soft cap; one exceeding 100 logical lines triggers mandatory decomposition or written waiver before merge. | Python/JavaScript critical logic | Function-size report plus review. | Waiver identifies invariant, why split harms clarity, focused tests, owner, revisit trigger. |
| CR-OSW-002 | Complex control flow is decomposed into pure decisions and effect adapters; nesting/branch growth must be justified and exhaustively fixture-tested. | State, adapters, scientific calculations, admission, release | Complexity/branch inventory and negative tests. | Only with evidence that decomposition would duplicate or obscure the invariant. |
| CR-OSW-003 | Invalid input, unavailable data, and incompatible state produce allocated diagnostics; no silent return, clamp, coercion, catch-all success, or fallback in meaning-bearing logic. | IF-OSW-002–015 | Diagnostic and mutation fixtures. | Presentation-only best-effort enhancement may fail closed with visible bounded message. |
| CR-OSW-004 | Critical invariants have assertions, property tests, negative fixtures, or independent calculations at the narrowest boundary. | All Design invariants | Invariant-to-test inspection. | External-only validation requires an explicit local surrogate and open limitation. |
| CR-OSW-005 | Static analysis, syntax, compile, formatter/lint, local links, and generated-structure checks are clean or carry an owned dated waiver. | Whole changed scope | Profile L0 commands. | Waiver states tool, finding, risk, owner, expiry/revisit. |
| CR-OSW-006 | Scientific values retain explicit units, dimensions, sign/orientation, reference, time/depth/space support, constants, and operator identity; conversions occur once at named boundaries. | Scientific inputs/results/value bindings | Synthetic identities, dimensional/range checks, CURRENT/SOUNDER review. | None for admitted quantitative claims. |
| CR-OSW-007 | Floating comparison uses a named physical/numerical rationale, scale-aware tolerance, and boundary cases; exact identities use exact comparison. | Scientific calculations and generated results | Tolerance inspection, analytic/synthetic fixture. | No anonymous global epsilon. |
| CR-OSW-008 | Geometry support, data status, and surface condition use orthogonal categorical axes with shared shape/order contracts; falsy numeric handling cannot determine validity and sea ice cannot erase valid subsurface data. | Scientific and cartographic arrays/geometry | Property, cross-axis, and end-to-end support fixtures. | None for admitted maps/results. |
| CR-OSW-009 | Budget terms are independently receipted and residuals remain residuals; calculations cannot assign causal process names. | Storage/advection/transport/convergence/budget code | Identity and prohibited-claim tests. | None. |
| CR-OSW-010 | Source/intermediate/result/display/claim identities and checksums remain distinct; public values resolve through controlled bindings. | Pipelines, adapters, scenes, figures | Mutation and lineage tests. | Inspection-only historical artifacts remain non-admitted until adapted. |
| CR-OSW-011 | Acquisition writes to a bounded candidate location, validates before atomic accepted replacement, redacts credentials, and preserves accepted artifacts on every failure. | Provider-facing Python/tooling | Fault injection and before/after hashes. | None for accepted custody. |
| CR-OSW-012 | Default tests and public reader use no live scientific provider; optional imports/network paths fail only the affected capability. | Python, browser, CI | Network-disabled suite and dependency-removal fixtures. | Explicit separately invoked acquisition is outside default gate and still receipted. |
| CR-OSW-013 | Generated artifacts are deterministic or normalize declared nondeterminism; generator/integrity command, inputs, dependencies, comparison mode, and update rule are controlled by family. | JSON, JS data, SVG, tables, prose/status generation | Regeneration/integrity diff and family registry. | Inspection-only comparison requires reason and cannot support high-risk quantitative admission. |
| CR-OSW-014 | Canonical state transitions are pure and transactional; renderers/controls never mutate independent scientific or accessibility state. | Browser JavaScript/HTML | Transition matrix, history/reload, visual/text/AT equivalence. | None for admitted routes. |
| CR-OSW-015 | DOM updates use semantic elements and safe text/attribute operations; dynamic HTML requires a fixed trusted template with no user/provider string interpolation. | Browser presentation | Static inspection and adversarial text fixture. | Reviewed static markup literals only. |
| CR-OSW-016 | Every interaction is keyboard/touch operable, has visible focus and stable programmatic state; color/hover/motion never carries unique meaning. | Public HTML/CSS/JS/SVG/canvas | HARBOR/CHART browser matrix and token inspection. | None for admitted public paths. |
| CR-OSW-017 | Visual and data-oriented text render from one view model and expose the same state/view identity and scientific limitation. | Map/scene renderers | Cross-output digest/equivalence tests. | Static figure may use a separately bound adjacent alternative. |
| CR-OSW-018 | Runtime requests are manifest-declared, same-origin, selected-view minimal, and storage/collection free; unexpected requests or persistence block release. | Public browser | Request/storage trace and privacy gate. | Deliberate user-activated external links are navigation, not background requests. |
| CR-OSW-019 | Federated admission is a closed decision algebra; missing, fail, unknown, or unjustified not-applicable cannot pass or be overridden. | Admission coordinator | Exhaustive combination/property tests. | None. |
| CR-OSW-020 | Release reconciliation is pure and side-effect free; only an immutable ready report enters deployment, and failure cannot advance citation/current metadata. | Release/publishing | Drift fixtures and fault-injected retain/restore scenario. | None for public promotion. |
| CR-OSW-021 | Diagnostics use allocated stable codes and safe envelopes; secrets, tokens, signed URLs, or excessive provider responses never enter logs, fixtures, SVG/HTML, or review records. | All error/report surfaces | Code allocation and secret/redaction scan. | Redacted diagnostic examples only. |
| CR-OSW-022 | Tests assert behavior/invariants rather than incidental formatting, except when bytes/text are themselves the public contract; each regression states the failure it prevents. | Test suite | Test review and mutation evidence. | Exact snapshots require a declared semantic reason and focused review. |
| CR-OSW-023 | No test or validator repairs the repository candidate; temporary output is isolated and cleaned, and accepted changes require explicit generation outside assertion logic. | Verification tooling | Clean-worktree before/after check. | None. |
| CR-OSW-024 | Third-party and optional dependencies are minimal, pinned where reproducibility requires, license-compatible, and isolated behind narrow adapters. | Python/browser/tooling | Dependency/rights inventory and missing-dependency fixture. | Stdlib/custom code still requires tests; “no dependency” is not an automatic preference. |
| CR-OSW-025 | Comments/docs state why a scientific or compatibility rule exists, its units/support/claim limit, and source interface—not a stale narration of syntax. | Critical hand-authored code and contracts | Review inspection. | Trivial self-evident code needs no comment. |

## Language and artifact profiles

| Profile ID | Applicability | L0 | L1 | L2 |
|---|---|---|---|---|
| PROFILE-OSW-DOCS-001 | Markdown/BibTeX/YAML governance, research, and public prose. | `git diff --check`; local-link/table/ID checks; parse YAML/CFF where changed. | Claim/receipt/status cross-check and relevant role lanes. | Reader/release scenario when public claims or status change. |
| PROFILE-OSW-PY-001 | Python acquisition, analysis, generation, validation. | `python -m compileall -q analysis`; changed CLI `--help`; import/syntax smoke. | Focused unittest/pytest including negative fixtures; schema/checksum/range/dimension/support checks. | Independent synthetic calculation, regeneration, provider-fault or end-to-end evidence scenario according to risk. |
| PROFILE-OSW-WEB-001 | Browser JavaScript/HTML/CSS. | `node --check atlas/app.js`; local asset/selector/semantic inspection. | State/reducer/component tests; keyboard/non-color/request/error fixtures; every mode offline. | Current Edge/Chrome/Firefox plus narrow/zoom/reduced-motion/AT workflow for affected primary journey. |
| PROFILE-OSW-MAP-001 | SVG/canvas/projection/display assets. | XML/SVG parse, required metadata/text identities, geometry finiteness. | Mask/seam/polar/projection/palette/boundary/text-equivalence fixtures. | CHART/HARBOR rendered inspection and scientific comparison-capability review. |
| PROFILE-OSW-DATA-001 | JSON/CSV/JS data/NetCDF-derived records. | Parse/schema/ID uniqueness/checksum/shape/order/range/unit checks. | Family regeneration or integrity comparison plus mutation/support fixtures. | Independent reproduction or cross-product/sensitivity scenario for high-risk claims. |
| PROFILE-OSW-MULTI-001 | Change crossing science, data, browser, docs, or release boundaries. | Every affected profile L0. | Boundary integration and full offline suite. | Consequential user/research/release scenario with federated role review. |
| PROFILE-OSW-RELEASE-001 | Lifecycle, citation, publication, hosting. | Manifest/status/hash consistency and zero secret/private-path scan. | Immutable candidate reconciliation and deliberate drift/hold cases. | Staged deploy, hosted commit/journey smoke, fault-injected retain/restore, owner decision. |

## Risk-to-profile assignment

| Change class | Minimum profile/level | Escalation trigger |
|---|---|---|
| Editorial wording with no claim/status/interface change | DOCS L0 | A limitation, source, number, route, or lifecycle statement changes → L1/L2. |
| Presentation-only style preserving semantics | WEB/MAP L0 + focused L1 | Meaning, interaction, responsive behavior, or palette/category changes → L2. |
| State, URL, route, scene, accessibility, loader | WEB L1 + MULTI L1 | Primary journey, fallback, request, or AT behavior changes → L2. |
| Receipt/schema/adapter/generated family | DATA/PY L1 + MULTI L1 | Lossy migration, public quantitative claim, or custody change → L2. |
| Scientific quantity, boundary, transport, budget, mechanism | PY/DATA/MAP as affected, always L2 | No downgrade; CURRENT/SOUNDER and often CHART required. |
| Admission, privacy, lifecycle, release/deploy | MULTI/RELEASE, always L2 | No downgrade; owner and relevant domain vetoes required. |

## Tailoring rules

| Area | Rule | Rationale |
|---|---|---|
| Function size | 60 logical lines soft cap; 100-line tripwire for new/materially changed hand-authored units. | Enables focused review while allowing cohesive scientific kernels with explicit waiver. |
| Existing files | File size alone does not force a rewrite; touched critical behavior must gain a seam, characterization test, or waiver. | Avoids risky churn in a working research system. |
| Python dependencies | Standard library for default validators where practical; scientific libraries may be optional/pinned within scientific profiles. | Offline gate and scientific capability have different needs. |
| JavaScript | No build framework required; pure modules/functions may be introduced incrementally when tests justify extraction. | Preserves static deployment while reducing monolithic state risk. |
| Numerical tolerances | Named per quantity/operator/source resolution; store full result precision and format only at presentation boundary. | Avoids hidden epsilon and prose-value drift. |
| Randomness/time | Fixed seed and declared algorithm; generated timestamps excluded from semantic comparisons or supplied explicitly. | Makes generation reproducible. |
| Network | Explicit acquisition only; tests use local fixtures and may assert zero provider requests. | Provider availability cannot control merge/release verification. |
| Generated SVG/HTML | Semantic assertions plus parse/geometry checks; full-byte snapshot only when byte identity is contractually meaningful. | Reduces brittle tests while protecting meaning. |
| Failures | Fail closed for affected claim/release, fail locally for optional capability, preserve last accepted public/artifact state. | Matches interface diagnostics and degraded operation. |

## Exceptions and migration waivers

Waivers describe current debt; they do not authorize new behavior to copy it.

| ID | Constraint | Current exception | Rationale | Owner | Revisit trigger |
|---|---|---|---|---|---|
| WAIVER-OSW-001 | CR-001, 002, 014, 017 | `atlas/app.js` currently concentrates state, data selection, rendering, relations, and content beyond new-code size/complexity targets. | A wholesale rewrite before characterization fixtures is higher risk. | KEEL | First work package materially changing route/state/scene behavior must extract or isolate the touched decision seam. |
| WAIVER-OSW-002 | CR-010, 013 | Historical receipts and generated records use heterogeneous `oceanlines.*`/`osw.*` shapes and do not all have family registry rows. | They preserve real research history and cannot be truthfully normalized retroactively without adapters. | SOUNDER | First admission of each historical family requires adapter/integrity record and explicit unavailable fields. |
| WAIVER-OSW-003 | CR-005, 024 | The repo has no single enforced formatter/linter/typechecker across all Python/JavaScript/docs surfaces. | Adding tools without a measured signal could create churn and new dependency burden. | KEEL | Code Rigor implementation planning must bake off minimal checks and adopt or explicitly reject each tool with evidence. |
| WAIVER-OSW-004 | CR-018 | Critical-path and selected/on-demand/custody payloads have not been completely inventoried or budgeted. | Hosted measurement is a controlled unknown. | KEEL | Before any integrated atlas public-release candidate. |
| WAIVER-OSW-005 | CR-020 | Hosted commit proof and atomic retain/restore implementation are not established. | Deployment mechanism remains intentionally deferred. | LOGBOOK | Before deployment work package or release readiness review. |
| WAIVER-OSW-006 | CR-001, 002, 006–010, 013 | Seventy-six existing Python functions exceed the 60-line guidance and nineteen exceed 100 lines; the largest mix orchestration, record construction, numerical kernels, and figure generation. | Mechanical decomposition without family-specific characterization could change scientific results or artifact bytes. | KEEL with CURRENT/SOUNDER for scientific functions | A work package materially changing one of these functions must inventory its size/branches, preserve output/quantity contracts, and decompose or issue a focused replacement waiver. |

No waiver permits false scientific claims, silent mask/value coercion,
credential exposure, accessibility state divergence, domain-veto override, or
unverified public promotion.

### Measured legacy baseline

| Measure | Observed 2026-09-07 | Interpretation |
|---|---|---|
| `atlas/app.js` physical lines | 1,404 | File-level concentration is grandfathered; three roughly parsed named functions exceed 60 lines and none exceeds 100. |
| Python functions over 60 physical source lines | 76 | Soft-cap debt across scientific analysis and artifact generators. |
| Python functions over 100 physical source lines | 19 | Existing tripwire debt requiring touched-unit review; largest observed function is a 532-line receipt builder. |

These are inventory measures, not complexity or quality verdicts. Physical
source lines overestimate logical lines but reliably identify review targets;
an implementation package must use a stable parser/report for its affected
language and record any exclusions.

## Required review checks

| Gate | Required questions |
|---|---|
| Design review | Does the change preserve architecture direction, all affected interfaces, state/evidence authority, negative paths, migration compatibility, and proportional rigor? |
| Product/research review | What consequential question is answered, what visible/research result exists, what was reused, does any new hand-authored unit cross the 100-line tripwire, and what independent/second-case evidence exists or remains blocked? |
| Implementation readiness | Does each future work package name parent design/interface/spec IDs, affected profiles and boundaries, entry/exit evidence, diagnostics, fixtures, docs/claims, and no-authority limits? |
| Test readiness | Are positive, negative, stale/adversarial, compatibility, inspect/report, and scientific boundary cases present with expected diagnostics/results? |
| Release readiness | Do immutable candidate, lifecycle/admission, current status/citation, hosted proof, payload/privacy checks, owner decision, and retain/restore evidence agree? |

## Verification evidence for this stage

| Evidence ID | Constraint IDs | Command/review | Expected result | Status |
|---|---|---|---|---|
| EVID-CR-OSW-001 | 005, 021, 023, 025 | Markdown links/tables/ID/coverage/hash checks and `git diff --check` | No malformed or unbound Design/Code Rigor controls. | passed at fixed point |
| EVID-CR-OSW-002 | 005, 012, 022–024 | `python -m pytest analysis -q` | Existing full offline behavior remains green. | passed: 458 tests and 10 subtests |
| EVID-CR-OSW-003 | 005, 012, 022–024 | `python -m unittest discover -s analysis -p "test_*.py"` | Independent discovery runner remains green. | passed: 327 tests |
| EVID-CR-OSW-004 | 005 | `python -m compileall -q analysis`; `node --check atlas/app.js` | Current Python/browser source remains syntactically valid. | passed |
| EVID-CR-OSW-005 | all | Eight native-role review | Three findings per role; every P1/P2 repaired or controlled. | passed: 8 roles, 0 P1, 16 P2 resolved |

## Code Rigor gate

Decision: `pass_with_risk`

- [x] Risk level is tailored by change class rather than treating all files equally.
- [x] L0/L1/L2 profiles cover every current language/artifact boundary.
- [x] Scientific, state/accessibility, custody, generated, admission, privacy, and release invariants have mandatory rigor hooks.
- [x] Function complexity, 60-line guidance, and 100-line tripwire are explicit without forcing a legacy rewrite.
- [x] Existing exceptions have owners and concrete revisit triggers.
- [x] Review and future work-package questions preserve product outcome and evidence limits.
- [x] Fixed-point commands pass and all eight native roles resolve every P1/P2 finding.

Implementation planning is authorized next but remains unopened.

## Source links

- [Detailed Design](DESIGN.md)
- [Interfaces](INTERFACES.md)
- [Architecture](ARCHITECTURE.md)
- [Package boundaries](PACKAGE_BOUNDARIES.md)
- [PITFALL register](../../design/pitfalls/README.md)
- [Native roles](../../.roles/ROLE.md)
- [Design and Code Rigor roles review](../../signals/roles/check/design-code-rigor-roles-check-2026-09-07.md)

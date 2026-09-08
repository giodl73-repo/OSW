# OSW Requirements

Status: settled at native-role fixed point, 2026-09-06

## Scope

Repo: OSW — Ocean States of the World

Baseline: accepted target product requirements derived from the settled
[Mission](MISSION.md) and [CONOPS](CONOPS.md). These requirements control what
OSW must make true for users and maintainers. They do not claim the current
repository already satisfies every row, select implementation architecture or
schema, authorize the guided event-anatomy implementation, promote a region
boundary, or approve a public release. Current, target, deprecated, and unknown
behavior are classified in the next Specification Baseline stage.

## Requirement language

- **must** is required for the first accepted integrated atlas baseline.
- **should** is required unless a later controlled artifact records a reasoned
  deferral before implementation planning.
- Verification methods name the required future evidence, not evidence that
  implementation already exists.
- Role names identify the accountable review lens; OSW remains the product
  owner.

## Product requirements

### Entry, story, and place

| ID | Requirement | Parent need / scenario | Rationale | Priority | Owner | Verification method | Status |
|---|---|---|---|---|---|---|---|
| REQ-OSW-001 | The public entry surface must offer the three primary routes—explore the ocean, follow heat, and inspect evidence—while retaining a complete secondary research index; adding, removing, or renaming a primary route requires controlled change. | `NEED-OSW-001`, `NEED-OSW-005`; `OPS-SCN-OSW-001`, `OPS-SCN-OSW-003` | Replaces the undifferentiated link corridor without hiding the corpus. | must | BEACON | Desktop/narrow user-route inspection reaches each primary outcome in one action and every legacy research destination remains reachable through the index. | accepted target |
| REQ-OSW-002 | The worked marine-heatwave route must connect event qualification/footprint, lineage, surface temperature, surface forcing, fixed-column storage, horizontal advection, and unresolved terms in an ordered, directly addressable journey. | `NEED-OSW-002`, `NEED-OSW-005`; `OPS-SCN-OSW-001` | Makes the strongest current evidence understandable as one study without asserting causality. | must | CURRENT | Scenario demonstration traverses all declared scenes in order, by direct URL and controls, and asserts that the final state remains partial and unresolved. | accepted target |
| REQ-OSW-003 | Every guided scene must present one principal finding beside its strongest material limitation and a direct route to its supporting receipt. | `NEED-OSW-003`, `NEED-OSW-005`; `OPS-SCN-OSW-001`, `OPS-SCN-OSW-002` | Keeps public explanation and researcher audit on one claim boundary. | must | BEACON | Content contract and rendered inspection reject a scene missing finding, limitation, evidence identity, or receipt target. | accepted target |
| REQ-OSW-004 | A province must be selectable by pointer, keyboard, search, or compatible direct URL; selection must preserve the active projection, lens/evidence mode, depth, hierarchy/hairline preference, and supported onward routes. | `NEED-OSW-001`, `NEED-OSW-004`; `OPS-SCN-OSW-003` | Treats ocean state as a resumable place rather than a transient highlight. | must | HARBOR | State-transition tests and browser scenarios exercise every entry path, reload, history navigation, reset, and incompatible-state fallback. | accepted target |
| REQ-OSW-005 | When evidence is projected directly on the source grid and no province aggregation exists, OSW must retain the direct field and state “no state aggregation”; it must not synthesize a province statistic or fill. | `NEED-OSW-003`, `CON-OSW-001`; `OPS-SCN-OSW-003`; `SI-01`, `CA-02` | Prevents the state metaphor from manufacturing quantitative support. | must | SOUNDER | Negative fixture and rendered inspection confirm absent aggregation remains absent, declared, and visually distinct. | accepted target |

### Scientific claim integrity

| ID | Requirement | Parent need / scenario | Rationale | Priority | Owner | Verification method | Status |
|---|---|---|---|---|---|---|---|
| REQ-OSW-006 | Every quantitative artifact must carry a controlled quantity identity that distinguishes temperature, anomaly, heat content/storage, velocity, volume transport, reference-relative heat transport, advection, convergence, transformation, and residual as applicable. | `NEED-OSW-002`, `CON-OSW-002`, `CON-OSW-003`; `OPS-SCN-OSW-001`, `OPS-SCN-OSW-004`; `SI-01` | Prevents a weaker observable from inheriting a stronger physical name. | must | CURRENT | Schema/admission fixtures plus CURRENT/SOUNDER inspection cover every quantity class and reject labels or claims inconsistent with the declared identity. | accepted target |
| REQ-OSW-007 | A budget view must enumerate independently supported terms and an unresolved remainder separately; only a term with its own source/transformation receipt may reduce or rename that remainder, and numerical proximity alone must not produce a closure claim. | `NEED-OSW-002`, `CON-OSW-004`; `OPS-SCN-OSW-001`, `OPS-SCN-OSW-004`; `SI-02` | Blocks residual-as-process and cross-system near-closure errors. | must | CURRENT | Budget identity tests plus invalid fixtures reject unsupported term assignment and closure language. | accepted target |
| REQ-OSW-008 | Motion arrows, streamlines, deterministic paths, parcel counts, and a single open-section flux must not produce delivery, probability, transported-volume, residence, convergence, or regional-budget claims without the additional evidence required for that quantity. | `NEED-OSW-004`, `CON-OSW-003`; `OPS-SCN-OSW-004`, `OPS-SCN-OSW-005`; `SI-03` | Preserves the distinct roles of M1, M2, M3, and M4 evidence. | must | CURRENT | Object-admission tests reject each prohibited claim from motion-only, path-only, and open-section fixtures. | accepted target |
| REQ-OSW-009 | A proposed ocean-state border must retain its boundary class and must not advance from organizational to diagnosed based on visual fit; any retain/merge/split/move/demote decision must expose persistence, cross-boundary exchange, retention, convergence, vertical-agreement, and gate-dependence evidence or explicit unavailable status. | `NEED-OSW-007`, `CON-OSW-005`, `CON-OSW-011`; `OPS-SCN-OSW-005`; `CA-02` | Makes zoning revisable under physics rather than count or aesthetics. | must | CURRENT | Candidate scorecard fixtures plus CURRENT/CHART inspection include supporting, contradictory, and missing diagnostics; an attractive exchange-poor border is rejected or demoted. | accepted target |
| REQ-OSW-010 | An Earth/gas-giant comparison must identify both quantities independently, name the shared mechanism/property, state forcing/stratification/rotation/depth/compressibility/boundary/observation differences, and provide an outcome that would weaken or falsify the analogy. | `NEED-OSW-008`, `CON-OSW-012`; `OPS-SCN-OSW-007` | Keeps mechanism transfer separate from visual rhyme. | must | ORBIT | Paired valid/visual-only fixtures and CURRENT/SOUNDER/ORBIT inspection accept the mechanism comparison and reject or label the resemblance-only case speculative. | accepted target |
| REQ-OSW-011 | OSW must not present its outputs as forecasts, hazard warnings, navigation advice, intervention outcomes, scientific peer review, institutional approval, or operational decisions. | Mission non-goals; system boundary; `OPS-SCN-OSW-004`, `OPS-SCN-OSW-006` | Preserves product and authority boundaries. | must | LOGBOOK | Capability and BEACON/LOGBOOK content inspection plus negative claim fixtures reject prohibited authority language and actions. | accepted target |

### Evidence, source custody, and degraded data

| ID | Requirement | Parent need / scenario | Rationale | Priority | Owner | Verification method | Status |
|---|---|---|---|---|---|---|---|
| REQ-OSW-012 | Every quantitative scene must resolve to a receipt that identifies provider/product, variable, version, units, sign/reference, time, depth/layer, spatial support, request/acquisition, grid/mask/missing-data treatment, transformation, source/derived checksums, evidence class, claim ceiling, and license/citation/redistribution posture as applicable. | `NEED-OSW-003`, `NEED-OSW-006`; `OPS-SCN-OSW-002`, `OPS-SCN-OSW-004`; `DL-02` | Makes the displayed claim independently identifiable and auditable. | must | SOUNDER | Receipt-schema completeness fixtures omit each applicable field independently and assert rejection; rendered scene resolves to the accepted receipt. | accepted target |
| REQ-OSW-013 | Source, normalized/intermediate, analysis-result, display-ready, and prose/claim artifacts must retain distinct identities and trace links; public headline values must be generated from or checked against the committed result receipt. | `NEED-OSW-003`, `NEED-OSW-006`; `OPS-SCN-OSW-002`, `OPS-SCN-OSW-004`; `DL-02` | Prevents transformation and prose drift. | must | SOUNDER | Mutation tests alter result values, checksums, or claim ceilings and require dependent artifacts to fail until regenerated or reconciled. | accepted target |
| REQ-OSW-014 | Land, sea ice, source-missing, quality-rejected, analysis-invalid, and out-of-domain support must remain distinguishable through acquisition, transformation, rendering, and text alternatives; none may be silently converted into ocean values. | `CON-OSW-002`, `CON-OSW-006`; `OPS-SCN-OSW-002`, `OPS-SCN-OSW-003`; `DN-02`, `CA-01` | Prevents support geometry from becoming false data. | must | SOUNDER | Mask-propagation fixtures and CHART/HARBOR rendered summaries verify each state end to end. | accepted target |
| REQ-OSW-015 | Default verification and released-site use must not require a live scientific provider; network acquisition/refresh must be explicit, separately invoked, receipted, and unable to overwrite an accepted artifact after a failed or mismatched response. | `NEED-OSW-006`, `CON-OSW-009`; `OPS-SCN-OSW-002`, `OPS-SCN-OSW-004` | Keeps review deterministic and safe when archives change or fail. | must | KEEL | Offline clean-checkout gate passes with network disabled; fault-injected acquisition preserves accepted artifacts and emits bounded failure receipts. | accepted target |
| REQ-OSW-016 | Checksum, schema, dimension, coordinate/order, unit, sign, mask, collocation, partial-cell, stencil, or time-support mismatch must stop the affected derived claim and identify the failed contract rather than silently coercing it. | `CON-OSW-002`, `CON-OSW-004`; `OPS-SCN-OSW-002`, `OPS-SCN-OSW-004`; `DN-01`, `DN-02` | Makes numerical and data-boundary failures observable. | must | SOUNDER | One negative fixture per mismatch class asserts no dependent result or preview promotion is emitted. | accepted target |

### Cartography and visual evidence

| ID | Requirement | Parent need / scenario | Rationale | Priority | Owner | Verification method | Status |
|---|---|---|---|---|---|---|---|
| REQ-OSW-017 | Every map view must expose projection/aspect, extent, date/interval, depth/layer, source/evidence class, variable/units, scale/legend, boundary class, and uncertainty/sensitivity or unavailable status as applicable. | `NEED-OSW-001`, `NEED-OSW-003`, `CON-OSW-006`; `OPS-SCN-OSW-001`, `OPS-SCN-OSW-003` | Prevents visual context from being inferred incorrectly. | must | CHART | Map-admission inspection rejects applicable missing metadata and SOUNDER review confirms field identity; narrow-view tests keep it reachable. | accepted target |
| REQ-OSW-018 | All admitted map families must preserve ocean-only feature masking, one identity across longitude seams, polar support, coastline context, and distinct land/ice/missing/out-of-domain treatment. | `NEED-OSW-001`, `NEED-OSW-004`, `CON-OSW-006`; `OPS-SCN-OSW-003`; `CA-01` | Prevents projection mechanics from fabricating object geometry. | must | CHART | Shared mask/seam/polar fixtures exercise every admitted family and fail any inconsistent derivative. | accepted target |
| REQ-OSW-019 | Conceptual, classic-reference, organizational/schematic, thresholded, diagnosed, modeled, and observed boundaries must have machine-readable classes and redundant line/label/legend/text treatments that remain distinguishable without color. | `CON-OSW-001`, `CON-OSW-005`, `CON-OSW-007`; `OPS-SCN-OSW-003`, `OPS-SCN-OSW-005`; `CA-02` | Prevents polish from manufacturing boundary authority. | must | CHART | Boundary fixtures and CHART/HARBOR rendered inspection reject missing class, provisional language, or non-color distinction. | accepted target |
| REQ-OSW-020 | A projection or small-multiple view must prohibit area/shape/distance comparison where its construction does not support that comparison and must expose discontinuities or panel-specific scale. | `CON-OSW-006`; `OPS-SCN-OSW-003`, `OPS-SCN-OSW-005` | Keeps experimental projections and HEATPLATES-like panels within their metric limits. | must | CHART | Distortion/metadata inspection plus deliberate invalid-comparison fixtures require the limitation beside the view. | accepted target |

### Accessibility, state, and performance

| ID | Requirement | Parent need / scenario | Rationale | Priority | Owner | Verification method | Status |
|---|---|---|---|---|---|---|---|
| REQ-OSW-021 | Every public route, map mode, selectable object, scene, evidence link, and reset action must be operable by keyboard with logical order, visible focus, and appropriately sized pointer/touch targets. | `NEED-OSW-005`, `CON-OSW-007`; `OPS-SCN-OSW-001`, `OPS-SCN-OSW-003` | Access to the evidence is part of product correctness. | must | HARBOR | Keyboard-only desktop and narrow-view browser scenarios traverse the complete primary journeys. | accepted target |
| REQ-OSW-022 | URL state, visual selection, focus context, programmatic name/state, live announcement, and data-oriented text alternative must describe the same accepted atlas state after navigation, selection, mode/depth/scene change, reload, fallback, loading, and error without unexpected focus movement. | `CON-OSW-007`; `OPS-SCN-OSW-001`, `OPS-SCN-OSW-003` | Prevents accessible and visual users from receiving different scientific states. | must | HARBOR | State-machine tests plus screen-reader/browser inspection cover valid, incompatible, unknown, loading, and failed-overlay transitions. | accepted target |
| REQ-OSW-023 | Sign, category, hierarchy, evidence class, uncertainty, missingness, and selection must not depend on color, hover, or motion; animation must honor reduced-motion preferences and have a non-animated equivalent. | `CON-OSW-007`; all public scenarios | Makes encoded scientific meaning recoverable through multiple channels. | must | HARBOR | Automated token checks and CHART/HARBOR perceptual inspection cover non-color, hover-free, and reduced-motion cases. | accepted target |
| REQ-OSW-024 | At a declared narrow viewport and browser zoom, the active map, principal finding, strongest limitation, controls, and evidence route must remain usable together without two-dimensional page scrolling or hidden meaning. | `NEED-OSW-005`, `CON-OSW-007`; `OPS-SCN-OSW-001`, `OPS-SCN-OSW-003` | Preserves the claim/caveat relationship on constrained displays. | must | HARBOR | Responsive browser matrix and BEACON/HARBOR zoom/reflow inspection at controlled viewport/zoom cases. | accepted target |
| REQ-OSW-025 | The released critical path must have a measured transfer/render baseline, load only the selected view's necessary research payloads eagerly, and reject unexplained regression against the accepted budget. | `CON-OSW-014`; `OPS-SCN-OSW-006`; `DL-03` | Prevents evidence growth from making the atlas inaccessible. | must | KEEL | Network/request trace and KEEL/HARBOR performance inspection compare candidate with accepted baseline and assert non-selected heavyweight payloads are deferred. | accepted target |

### Reproducibility and contribution

| ID | Requirement | Parent need / scenario | Rationale | Priority | Owner | Verification method | Status |
|---|---|---|---|---|---|---|---|
| REQ-OSW-026 | For every supported generated artifact, OSW must document and test a deterministic offline regeneration or integrity-check path with pinned applicable dependencies, local fixtures/committed inputs, and explicit output comparison. | `NEED-OSW-006`, `CON-OSW-009`; `OPS-SCN-OSW-002`, `OPS-SCN-OSW-004` | Makes generated evidence maintainable without a live source. | must | KEEL | Clean-checkout execution regenerates or verifies representative artifacts from each admitted artifact family and compares schema/checksum/content contracts. | accepted target |
| REQ-OSW-027 | A proposed scientific view must identify its consequential question, authoritative or explicitly synthetic source, rights posture, observable product result, claim ceiling, shortest demonstration, reuse decision, and applicable PITFALL scan before implementation planning. | `NEED-OSW-003`, `NEED-OSW-006`; `OPS-SCN-OSW-004` | Keeps contributions product-bearing and evidence-first. | must | CURRENT | CURRENT/SOUNDER/KEEL intake inspection rejects a proposal missing any applicable field and accepts a bounded null-result path. | accepted target |
| REQ-OSW-028 | Optional dependencies and network paths must fail with actionable diagnostics limited to the affected capability; their absence must not break unrelated offline atlas use or verification. | `CON-OSW-009`; `OPS-SCN-OSW-002`, `OPS-SCN-OSW-004` | Prevents external availability from becoming global product failure. | must | KEEL | Environment fixtures remove each optional dependency/network capability and assert bounded failure plus unaffected default gate. | accepted target |
| REQ-OSW-029 | An external review must bind to an immutable artifact identity, role/lens, findings, severity, and disposition while stating that review participation is not scientific endorsement or release authority. | `NEED-OSW-005`; ACT-OSW-008; `OPS-SCN-OSW-004`, `OPS-SCN-OSW-006` | Makes feedback useful without overstating authority. | must | LOGBOOK | Review-record inspection rejects missing artifact identity/disposition/boundary and confirms no automatic promotion. | accepted target |

### Release, compatibility, and privacy boundary

| ID | Requirement | Parent need / scenario | Rationale | Priority | Owner | Verification method | Status |
|---|---|---|---|---|---|---|---|
| REQ-OSW-030 | Every controlled artifact must carry exactly one lifecycle state from released, review preview, experiment, research intake, or degraded, and only released artifacts may define current hosted behavior. | `CON-OSW-010`; operational states; `OPS-SCN-OSW-006`; `DL-01` | Prevents preview and experiment evidence from becoming public release by implication. | must | LOGBOOK | State-registry validation rejects missing/multiple/illegal transitions and compares hosted claims with the released commit. | accepted target |
| REQ-OSW-031 | A release candidate must bind to an immutable commit and reconcile README, roadmap, preview status, source register, publication checklist, citation/version metadata, generated artifacts, role findings, owner decision, and intended hosted target before deployment. | `NEED-OSW-006`, `CON-OSW-010`; `OPS-SCN-OSW-006`; `DL-01`, `DL-02` | Creates one reviewable release truth. | must | LOGBOOK | Release fixture deliberately mismatches each surface and KEEL/LOGBOOK inspection asserts a hold; a complete candidate produces one review packet. | accepted target |
| REQ-OSW-032 | Deployment must verify the hosted commit and primary journeys after publication; failure must retain or restore the prior released site and must not update citation/current-release claims. | `CON-OSW-010`; `OPS-SCN-OSW-006` | Separates build readiness from successful public transition. | must | LOGBOOK | Staging and fault-injected deployment scenarios plus KEEL inspection verify smoke evidence, hold/rollback behavior, and metadata atomicity. | accepted target |
| REQ-OSW-033 | Direct URL parameters for province, object, mode, depth, event, scene, and projection must have a declared compatibility/version policy; unknown or incompatible values must fall back safely, announce the rejection, and preserve a usable supported state. | `NEED-OSW-004`, `CON-OSW-007`; `OPS-SCN-OSW-003`; `OQ-OSW-004` | Makes shared atlas states durable and accessible. | must | HARBOR | Compatibility fixtures plus HARBOR/LOGBOOK inspection cover current, migrated, unknown, conflicting, and removed parameters across reload/history/direct entry. | accepted target |
| REQ-OSW-034 | The current no-account, no-user-upload, no-cookie, and no-telemetry boundary must remain true unless a controlled requirement, privacy/security review, public disclosure, and validation plan approve a change. | CONOPS operational assumption; `OPS-SCN-OSW-006` | Prevents an unreviewed change to the static atlas's trust boundary. | must | LOGBOOK | Static capability/request inspection fails on undeclared collection, persistence, upload, or third-party telemetry behavior. | accepted target |

## Parent coverage

| Parent | Covered requirements |
|---|---|
| `NEED-OSW-001` | `REQ-OSW-001`, `REQ-OSW-004`, `REQ-OSW-017`, `REQ-OSW-018` |
| `NEED-OSW-002` | `REQ-OSW-002`, `REQ-OSW-006` through `REQ-OSW-008` |
| `NEED-OSW-003` | `REQ-OSW-003`, `REQ-OSW-005`, `REQ-OSW-012`, `REQ-OSW-013`, `REQ-OSW-017`, `REQ-OSW-027` |
| `NEED-OSW-004` | `REQ-OSW-004`, `REQ-OSW-008`, `REQ-OSW-018`, `REQ-OSW-033` |
| `NEED-OSW-005` | `REQ-OSW-001` through `REQ-OSW-003`, `REQ-OSW-021`, `REQ-OSW-024`, `REQ-OSW-029` |
| `NEED-OSW-006` | `REQ-OSW-012`, `REQ-OSW-015`, `REQ-OSW-026`, `REQ-OSW-027`, `REQ-OSW-031` |
| `NEED-OSW-007` | `REQ-OSW-009` |
| `NEED-OSW-008` | `REQ-OSW-010` |
| `OPS-SCN-OSW-001` | `REQ-OSW-002`, `REQ-OSW-003`, `REQ-OSW-006`, `REQ-OSW-007`, `REQ-OSW-017`, `REQ-OSW-021` through `REQ-OSW-024` |
| `OPS-SCN-OSW-002` | `REQ-OSW-003`, `REQ-OSW-012` through `REQ-OSW-016`, `REQ-OSW-026`, `REQ-OSW-028` |
| `OPS-SCN-OSW-003` | `REQ-OSW-001`, `REQ-OSW-004`, `REQ-OSW-005`, `REQ-OSW-014`, `REQ-OSW-017` through `REQ-OSW-024`, `REQ-OSW-033` |
| `OPS-SCN-OSW-004` | `REQ-OSW-006` through `REQ-OSW-008`, `REQ-OSW-011` through `REQ-OSW-016`, `REQ-OSW-026` through `REQ-OSW-029` |
| `OPS-SCN-OSW-005` | `REQ-OSW-008`, `REQ-OSW-009`, `REQ-OSW-019`, `REQ-OSW-020` |
| `OPS-SCN-OSW-006` | `REQ-OSW-011`, `REQ-OSW-025`, `REQ-OSW-029` through `REQ-OSW-034` |
| `OPS-SCN-OSW-007` | `REQ-OSW-010` |

## PITFALL coverage

| Pitfall | Preventing or detecting requirements |
|---|---|
| `SI-01` | `REQ-OSW-005`, `REQ-OSW-006`, `REQ-OSW-012`, `REQ-OSW-017` |
| `SI-02` | `REQ-OSW-007`, `REQ-OSW-013` |
| `SI-03` | `REQ-OSW-008`, `REQ-OSW-009` |
| `DN-01` | `REQ-OSW-006`, `REQ-OSW-012`, `REQ-OSW-016` |
| `DN-02` | `REQ-OSW-012`, `REQ-OSW-014`, `REQ-OSW-016`, `REQ-OSW-026` |
| `CA-01` | `REQ-OSW-014`, `REQ-OSW-017`, `REQ-OSW-018` |
| `CA-02` | `REQ-OSW-005`, `REQ-OSW-009`, `REQ-OSW-019`, `REQ-OSW-020` |
| `DL-01` | `REQ-OSW-030` through `REQ-OSW-032` |
| `DL-02` | `REQ-OSW-003`, `REQ-OSW-012`, `REQ-OSW-013`, `REQ-OSW-026`, `REQ-OSW-031` |
| `DL-03` | `REQ-OSW-025`, `REQ-OSW-031` |

## Requirement quality checklist

- [x] Every requirement uses a testable obligation rather than “support,”
  “handle,” or “robust.”
- [x] Every requirement has a Mission need, constraint, actor, or CONOPS
  scenario parent.
- [x] Every requirement has a priority and accountable OSW role lens.
- [x] Every requirement names a future automated test, inspection,
  demonstration, or review method.
- [x] Product behavior remains separate from VTRACE stage/status machinery.
- [x] Requirements do not choose application architecture, file schema,
  algorithm, framework, storage provider, or deployment mechanism.
- [x] Current implementation status is not asserted; that classification is
  reserved for `SPECIFICATION_BASELINE.md`.

## Controlled deferrals

| ID | Deferred decision | Reason | Revisit stage |
|---|---|---|---|
| DREQ-OSW-001 | Which existing behaviors satisfy, partly satisfy, conflict with, or remain unknown for each requirement. | Requires observed-current evidence inspection. | Specification Baseline |
| DREQ-OSW-002 | Route/component shape for guided event anatomy and province drill-down. | Product requirement precedes architecture. | Specification Baseline / Architecture |
| DREQ-OSW-003 | Common quantity, receipt, claim-ceiling, boundary, and lifecycle-state schemas. | Interface shape must follow accepted behavior and current-format audit. | Specification Baseline / Interfaces |
| DREQ-OSW-004 | Exact viewport, zoom, browser/assistive-technology matrix, contrast, target-size, and announcement thresholds. | Needs current baseline and validation-participant plan. | Specification Baseline / Interfaces / Validation |
| DREQ-OSW-005 | Numeric transfer, request-count, render, and interaction performance budgets. | Must be derived from measured hosted behavior and necessary evidence payloads. | Specification Baseline / Design / Validation |
| DREQ-OSW-006 | Git versus release-asset versus external/archive custody for heavyweight inputs. | Requires artifact inventory, rights, durability, and reconstruction analysis. | Architecture / Interfaces |
| DREQ-OSW-007 | Exact zoning score combination, thresholds, uncertainty, temporal/depth coverage, and change rule. | Requires scientific method design after the current baseline. | Design / Validation |
| DREQ-OSW-008 | Exact URL compatibility versioning and migration period. | Requires inventory of current shared parameters and architecture. | Specification Baseline / Interfaces |
| DREQ-OSW-009 | Deployment host, atomic transition, and rollback mechanism. | Requirement controls outcome, not implementation. | Architecture / Implementation Plan |
| DREQ-OSW-010 | External participant recruitment and success thresholds for non-specialist, researcher, and assistive-technology validation. | Requires owner-approved validation plan. | Validation |

## Source links

- [Mission](MISSION.md)
- [CONOPS](CONOPS.md)
- [PITFALL register](../../design/pitfalls/README.md)
- [Central roadmap](../../ROADMAP.md)
- [Native roles](../../.roles/ROLE.md)

The native-role fixed-point review is recorded in
[`requirements-roles-check-2026-09-06.md`](../../signals/roles/check/requirements-roles-check-2026-09-06.md).

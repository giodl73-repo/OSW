# OSW Detailed Design

Status: settled at native-role fixed point, 2026-09-07

## Scope

Repo: OSW — Ocean States of the World

This design turns the 15 settled interfaces into implementable component
behavior while preserving the thin static reader and build-time evidence
architecture. It defines algorithms, state transitions, invariants, edge cases,
adapter behavior, and migration order. It does not create code, schemas,
fixtures, work packages, deployment mechanisms, validation thresholds, or a
release candidate.

The design favors incremental extraction around current behavior. Existing
`atlas/app.js`, historical receipts, data modules, figures, and analysis scripts
remain valid evidence inputs; they are not declared conforming merely because
they exist, and they are not rewritten wholesale.

## Design decision summary

| ID | Decision | Parent interfaces | Rationale | Rejected alternative | Evidence / future proof |
|---|---|---|---|---|---|
| DES-OSW-001 | Preserve progressive-enhancement static HTML as the public shell. | 001, 002, 005, 006 | Keeps routes, limitations, and evidence links usable without a runtime service and preserves privacy/offline boundaries. | Application server or account-backed reader. | Static request inventory, route and no-script inspection. |
| DES-OSW-002 | Represent canonical reader state as an immutable value transformed by a pure transition function. | 002 | One accepted state can drive URL, focus, visual, text, and announcements transactionally. | Independent mutable globals owned by each renderer/control. | Transition fixtures and output-equivalence assertions. |
| DES-OSW-003 | Separate candidate-state parsing, compatibility adaptation, validation, commit, and announcement. | 002 | Invalid links must not partially update the experience or silently clamp values. | Parse-and-mutate control callbacks. | Legacy/current/unknown/conflicting state fixtures. |
| DES-OSW-004 | Store primary routes and guided scenes as ordered registries consumed by the shell. | 001, 003, 008 | Makes three-route identity and complete event semantics inspectable without hard-coded navigation branches. | Duplicated route markup and ad hoc next/back links. | Registry completeness, order, link, and scene-binding checks. |
| DES-OSW-005 | Bind scene quantitative prose through value references into admitted result records. | 003, 007, 008 | Prevents copied headline values and limitations from drifting away from receipts. | Independent numeric constants in HTML/JavaScript/Markdown. | Receipt mutation and rendered-value comparison. |
| DES-OSW-006 | Normalize historical evidence through versioned lossless adapters into a common in-memory contract; never rewrite source records during validation. | 003, 007, 009, 011, 012 | Preserves provenance while allowing uniform admission. | Bulk migration that invents or drops historical fields. | Round-trip/preservation fixtures and explicit unavailable fields. |
| DES-OSW-007 | Implement each domain admission as a pure validator returning a disposition; compose without override. | 004, 007, 009, 010, 013–015 | Preserves federated role vetoes and makes rejection executable. | One scoring function or shared “mostly passes” threshold. | Missing-domain, veto, unknown, and not-applicable fixtures. |
| DES-OSW-008 | Represent geometry support, data validity, and surface condition as orthogonal categorical companions to data, never a falsy numeric sentinel. | 004, 009 | Prevents land/missing/invalid states from becoming zero/valid ocean while preserving valid subsurface ocean data beneath sea ice. | One mutually exclusive support enum, `null`, NaN, zero, or palette alpha as the sole identity. | End-to-end fixtures for each axis and valid cross-axis combinations. |
| DES-OSW-009 | Build one view model from accepted reader state and admitted display bundle, then render visual and textual projections from it. | 002, 004, 009 | Ensures equivalent map meaning without forcing accessibility logic into SVG/canvas drawing code. | Independently computed visual and text summaries. | Shared view ID/state digest and equivalence tests. |
| DES-OSW-010 | Resolve selected-view assets through a static manifest with payload class and integrity identity. | 004, 006, 012 | Enables lazy selected-view loading and runtime request allowlisting without a service. | Eager inclusion of every research payload or dynamic provider URLs. | Request trace, unselected-payload negative test, integrity failure. |
| DES-OSW-011 | Split provider acquisition, response validation, accepted-custody replacement, scientific calculation, and publication generation into explicit phases. | 009, 011, 012 | A failed provider or mismatch cannot corrupt accepted local evidence or leak into default tests. | One script that downloads, overwrites, computes, and publishes in place. | Fault injection and before/after checksum assertions. |
| DES-OSW-012 | Allocate diagnostics centrally as constants/data, while each boundary supplies safe context and fallback. | all | Prevents string drift and makes negative fixtures stable without centralizing domain decisions. | Free-form exception messages as the only failure interface. | Diagnostic uniqueness, envelope, redaction, and mapping checks. |
| DES-OSW-013 | Reconcile release state into an immutable candidate report before any deployment side effect. | 005, 010, 012, 013 | Separates evidence/admission/readiness from hosting and makes holds deterministic. | Deployment script infers readiness while publishing. | Deliberate drift fixture and zero-side-effect hold assertion. |
| DES-OSW-014 | Treat planetary comparison and zoning scorecards as consumers of shared quantities/receipts plus their own domain fields. | 007, 010, 014, 015 | Avoids duplicate truth systems while retaining comparison/boundary-specific falsification. | Standalone narrative comparison or opaque composite zoning score. | Resemblance-only and attractive-false-border fixtures. |
| DES-OSW-015 | Use incremental seams around current files; extract only where a work package can preserve behavior and add proof. | all | Reduces migration risk and respects the current 458-test baseline. | Rewrite of the atlas or evidence corpus before contract fixtures exist. | Before/after route/state/artifact equivalence. |

## Component design

### Public shell, routes, and scenes

The shell reads an admitted route registry containing exactly `explore`,
`heat`, and `evidence`, then renders semantic landmarks and local links. The
secondary research index is separate and exhaustive. A route target can be
static HTML or an enhanced atlas state, but route identity and outcome remain
available without JavaScript.

The heat route reads an ordered scene registry. Every scene references its
question, principal claim, strongest limitation, receipt binding, optional map
view, text alternative, and compatible state. Back/next navigation is derived
from unique contiguous ordinals; the terminal scene explicitly names unresolved
terms. Visual grouping may combine panels but cannot remove semantic scenes.

### Canonical reader state

The state model contains only accepted values. Controls and addresses create a
candidate transition; they never mutate canonical state directly.

```text
raw URL or control intent
  -> parse syntactic candidate
  -> apply declared legacy adapter
  -> validate identity vocabularies
  -> resolve cross-field compatibility in dependency order
  -> accepted candidate + one diagnostic set
  -> prepare URL, view model, focus context, announcement, controls
  -> commit all projections together OR keep previous state
```

Validation order is foundational to dependent:

1. state contract version and primary route;
2. province and object identities;
3. event and scene identity/order;
4. evidence mode, projection, depth/pressure, lens/view/filters;
5. probe and presentation preferences.

When multiple fragments fail, the reducer preserves all compatible higher-level
state, removes the least foundational invalid fragments, and returns one ordered
diagnostic set. Direct URL initialization may fall back to the default route;
an in-session invalid transition retains the prior accepted state where that is
less surprising. Neither path commits split visual/programmatic state.

`legacy-v0` reading is an adapter before validation. `observed` maps to `sst`;
`feature` maps to `object` only when `object` is absent. The writer emits `v=1`
and canonical keys. Legacy aliases are never written.

### Evidence normalization and value binding

Each adapter is specific to a declared historical contract/version and returns:

- the untouched source artifact identity;
- normalized common fields;
- preserved unknown fields or a lossless source reference;
- explicit `unavailable`/`not_applicable` dispositions with reasons;
- adapter version and transformation evidence;
- diagnostics that block claims requiring unavailable meaning.

Adapters reject ambiguous unit, sign, reference, support, source, checksum, or
claim-ceiling mappings. They do not guess from filenames or prose. A display
value binding resolves a result artifact and structured field path, validates
quantity/unit compatibility, applies a declared presentation format, and
records the source value. Formatting may round for display but cannot alter the
receipt value or silently change units.

### Scientific production and support propagation

Provider-facing execution writes a candidate response into temporary custody,
validates request hash, response identity, rights posture, media/schema,
dimensions, coordinates, units, masks, and checksum, and only then performs an
atomic accepted-custody replacement. Failure deletes or quarantines only the
candidate and preserves the prior accepted artifact.

Scientific transformation reads accepted identities, validates preconditions,
computes one declared quantity, emits result and sensitivity/support records,
then optionally emits display derivatives. Source, intermediate, result,
display, and claim records keep distinct IDs and checksums. A result may be
scientifically useful without being admitted to the public bundle.

Support propagation is conservative and axis-preserving:

```text
geometry_support: ocean | land | out_of_domain
data_status:      valid | source_missing | quality_rejected | analysis_invalid
surface_condition: open_water | sea_ice | unknown | not_applicable

ocean value renderable = geometry_support == ocean AND data_status == valid
surface/ice annotation = independent of value renderability and depth support
```

An algorithm may define stricter family-specific propagation within an axis,
but never collapse the axes or convert non-ocean/non-valid input into a valid
quantity without a separately identified interpolation/analysis product and
receipt. Sea ice may coexist with valid ocean data and must not be used as a
generic missing-value code.

### View model and rendering

The view-model builder joins accepted reader state, one admitted map contract,
selected display assets, and scene claim/receipt bindings. It validates their
state version, quantity, support, projection, extent, time/depth, evidence,
boundary class, comparison capabilities, and artifact identities before
producing a view model.

The visual renderer receives geometry/data/support/presentation tokens. The
text renderer receives the same view model and reports selected place/object,
quantity/unit, time/depth, scale or category summary, missingness/support,
principal finding, and strongest limitation. Both expose the same `view_id` and
state digest. Canvas/SVG hit testing may select an identity but cannot invent
one not present in the accepted view model.

### Federated admission

The admission coordinator determines required domains from artifact-family
policy, calls domain validators independently, and records each immutable
disposition. It then applies only this composition rule:

```text
admitted = every required domain is present and decision == pass
```

`fail`, `unknown`, missing, or unjustified `not_applicable` yields false.
Composition has no score, waiver threshold, or override. Corrected candidates
receive a new artifact identity and new dispositions; prior review does not
transfer automatically.

### Selected-view loading and privacy

The static display manifest maps a view/family identity to same-origin assets
and payload classes. Initial shell assets plus the default view may be
`critical_path`; only active-view assets are `selected_view`; deeper receipts
and large evidence are `evidence_on_demand`; reproducibility-only bytes are
`custody_external`. A loader requests the minimal transitive set for accepted
state, verifies response/media/integrity when available, and renders a bounded
error without clearing the previous usable view.

The loader rejects undeclared or cross-origin runtime data requests. Deliberate
external citation navigation remains a normal link activation, not a preload,
telemetry request, or scientific data fetch.

### Release reconciliation

Reconciliation is a pure comparison over an immutable candidate manifest:

1. verify commit and exactly-one lifecycle state for every controlled artifact;
2. compare all declared public status/citation/source/generated identities;
3. require complete federated admissions and offline/browser/performance proof;
4. require explicit owner approve/hold decision and intended hosted target;
5. emit `ready` or diagnostic-rich `hold` without deployment side effects.

Only a ready report can reach a separately effectful deployment adapter.
Deployment then produces hosted commit and primary-journey smoke evidence. The
release record changes to `released` only after both pass; otherwise prior
release bytes and current/citation metadata remain or are restored together.

## Design invariants

| ID | Invariant | Interfaces protected |
|---|---|---|
| INV-OSW-001 | Canonical state is immutable; all visible, URL, focus, programmatic, announcement, and text projections share one committed state digest. | 002, 004 |
| INV-OSW-002 | Legacy adapters read aliases but canonical writers never emit them. | 002 |
| INV-OSW-003 | Three primary route IDs are present exactly once; every admitted corpus destination is reachable or explicitly retired/replaced. | 001 |
| INV-OSW-004 | Every guided scene has exactly one principal finding and strongest limitation plus a resolvable receipt binding. | 003, 008 |
| INV-OSW-005 | Displayed quantitative values resolve to admitted result fields and declared formatting; no uncontrolled duplicate constant is authoritative. | 003, 007, 008 |
| INV-OSW-006 | Presentation and rendering cannot widen a claim ceiling or change evidence origin/method. | 003, 004, 007, 014 |
| INV-OSW-007 | Geometry, data status, and surface condition remain orthogonal; non-ocean/non-valid support never becomes a valid ocean quantity, and sea ice never erases valid subsurface data. | 004, 009 |
| INV-OSW-008 | Projection cannot change data identity, support, boundary class, or comparison capability. | 004, 009, 015 |
| INV-OSW-009 | Source, intermediate, result, display, and claim identities/checksums are distinct and traceable. | 003, 011, 012 |
| INV-OSW-010 | A failed acquisition or transformation cannot overwrite the prior accepted artifact. | 009, 011, 012 |
| INV-OSW-011 | Default verification and public reader use perform no live scientific-provider request. | 006, 011, 012 |
| INV-OSW-012 | Every admitted generated family has deterministic offline regeneration or integrity comparison and a negative fixture. | 010, 012 |
| INV-OSW-013 | No domain admission decision can be omitted, averaged, or overridden. | 010 |
| INV-OSW-014 | Admission and release are distinct; admission never updates hosted/current/citation state. | 005, 010, 013 |
| INV-OSW-015 | External review becomes stale when bound artifact bytes change and never grants endorsement or release authority. | 013 |
| INV-OSW-016 | Planetary comparison references admitted Earth/planetary identities and always retains differences and weakening outcome. | 014 |
| INV-OSW-017 | Unavailable zoning evidence remains unavailable and cannot promote an organizational boundary. | 015 |
| INV-OSW-018 | Runtime requests are declared same-origin display assets; accounts/uploads/cookies/telemetry/user collection remain absent. | 006 |
| INV-OSW-019 | Release reconciliation has no deployment side effects; deployment failure cannot advance current metadata. | 005 |
| INV-OSW-020 | VTRACE, work-package, role-readiness, and pitfall state never becomes public reader state or ocean-object semantics. | 001, 002, 005, 006 |

## Edge cases

| ID | Edge case | Expected behavior | Future verification |
|---|---|---|---|
| EDGE-OSW-001 | Unversioned URL contains `feature` only. | Legacy adapter maps to canonical object, writer emits `v=1&object=...`. | Compatibility fixture. |
| EDGE-OSW-002 | URL contains conflicting `object` and `feature`. | Keep valid canonical object, reject alias, announce one conflict. | Negative state fixture. |
| EDGE-OSW-003 | `pressure` appears outside `mode=argo700`. | Remove pressure, preserve compatible state, announce incompatibility. | Cross-field fixture. |
| EDGE-OSW-004 | Only one of `lat`/`lon` is valid. | Reject pair, retain view/place state, no probe selection. | Pair-validation fixture. |
| EDGE-OSW-005 | Ring latitude is non-finite or outside 0–89. | Reject rather than silently clamp direct state; retain previous/default ring and announce. | Range fixture. |
| EDGE-OSW-006 | Selected province is valid but requested view has no aggregation. | Preserve province context; display direct field and “no state aggregation”; never synthesize fill/statistic. | Negative aggregation fixture. |
| EDGE-OSW-007 | Receipt adapter lacks a reference/sign field needed by a transport claim. | Mark unavailable and block that claim; retain source bytes and weaker supported claim. | Adapter/claim fixture. |
| EDGE-OSW-008 | A value binding path disappears after result regeneration. | Scene admission fails with receipt-binding diagnostic; stale number is not rendered. | Mutation fixture. |
| EDGE-OSW-009 | Renderer receives support axes and data arrays with different shapes/order. | Map admission/render fails; previous usable view remains. | Shape/order fixture. |
| EDGE-OSW-017 | A subsurface valid-ocean value lies beneath a sea-ice surface condition. | Preserve/render the valid subsurface value and separately expose sea ice; neither overwrites the other. | Cross-axis support fixture. |
| EDGE-OSW-010 | Selected asset fails integrity or loading. | Announce bounded view failure without losing navigation/focus or silently using another dataset. | Loader fault fixture. |
| EDGE-OSW-011 | One required admission domain is unknown. | Overall admission false; other domain results retained for diagnosis. | Composition fixture. |
| EDGE-OSW-012 | External review targets old artifact checksum. | Mark stale; no admission/release credit transfers. | Stale review fixture. |
| EDGE-OSW-013 | Zoning diagnostics disagree. | Expose supporting and contradictory records; no composite score implied; decision remains provisional unless controlled rule later passes. | Contrary-evidence fixture. |
| EDGE-OSW-014 | Planetary quantity exists only as cloud-top appearance. | Label comparison speculative/resemblance-only or reject mechanism claim. | ORBIT negative fixture. |
| EDGE-OSW-015 | Release surfaces all pass but hosted commit smoke fails. | Retain/restore prior release and leave citation/current metadata unchanged. | Fault-injected release scenario. |
| EDGE-OSW-016 | Browser encounters unknown optional contract field. | Preserve through adapters where possible; ignore only if meaning cannot change; never treat unknown meaning-bearing value as default. | Forward-compatibility fixture. |

## Migration and rollout design

This is compatibility order, not implementation work sequencing:

1. Freeze current behavior with URL, route, receipt, map, request, and generated-
   artifact inventories before extracting seams.
2. Add read-only adapters and validators beside historical artifacts; produce no
   rewritten accepted bytes.
3. Add canonical state parsing/reduction while maintaining legacy-v0 reads and
   current visual behavior.
4. Drive visual/text outputs from a shared view model and prove equivalence.
5. Introduce route/scene registries and value bindings; retain the complete
   research index.
6. Add display-manifest/payload classifications before changing load behavior.
7. Add federated admission and release reconciliation in report-only mode.
8. Only later work packages may switch writers/loaders/release gates after
   fixtures prove backward compatibility and owner-visible behavior.

At every step the prior static atlas remains usable. There is no flag that
silently makes an unadmitted artifact public. Removal of legacy adapters follows
the settled dual-read policy and a controlled release decision.

## Design-to-interface coverage

| Interface | Design decisions | Principal invariants |
|---|---|---|
| IF-OSW-001 | 001, 004, 015 | 003, 020 |
| IF-OSW-002 | 002, 003, 009, 015 | 001, 002, 020 |
| IF-OSW-003 | 004–006, 012 | 004–006, 009 |
| IF-OSW-004 | 008–010 | 001, 006–008 |
| IF-OSW-005 | 013, 015 | 014, 019 |
| IF-OSW-006 | 001, 010, 015 | 011, 018, 020 |
| IF-OSW-007 | 005–007, 011, 012, 014 | 005, 006, 009 |
| IF-OSW-008 | 004, 005, 009 | 003–005 |
| IF-OSW-009 | 006–009, 011 | 007–010 |
| IF-OSW-010 | 007, 012–015 | 012–015 |
| IF-OSW-011 | 006, 011, 012 | 009–011 |
| IF-OSW-012 | 006, 010–013, 015 | 009–012, 018 |
| IF-OSW-013 | 007, 012, 013 | 013–015 |
| IF-OSW-014 | 007, 012, 014 | 006, 013, 016 |
| IF-OSW-015 | 007–009, 012, 014 | 007, 008, 013, 017 |

## Code-rigor hooks

| Area | Risk | Required Code Rigor constraint |
|---|---|---|
| Canonical state reducer/adapters | Split or silently coerced reader state. | Pure deterministic functions, exhaustive transition/alias/error fixtures, bounded complexity. |
| Receipt/value adapters | Invented or lost provenance and stale public numbers. | Lossless-preservation tests, explicit unavailable states, no catch-all coercion. |
| Scientific quantities/support | Physically wrong units/sign/reference/masks or false closure. | Dimension/unit assertions, conservative support properties, negative physics fixtures, declared tolerances. |
| View model/renderers | Visual/text divergence and fabricated map geometry. | Shared identity digest, cross-output tests, no independent science calculations. |
| Acquisition/custody | Corruption or secret/rights leakage. | Temporary candidate writes, validation before atomic replacement, redaction, fault injection. |
| Generated families | Irreproducible or drifting artifacts. | Family registry, deterministic/offline commands, semantic/byte comparisons, mutation tests. |
| Admission composition | Missing or overridden domain veto. | Closed decision algebra and property tests over all disposition combinations. |
| Runtime loader/privacy | Eager payload regressions or undeclared requests/storage. | Static allowlist, request trace, integrity/error paths, zero-collection inspection. |
| Release reconciliation/deployment adapter | Broken preview promoted or metadata advanced after failure. | Pure readiness report, no-side-effect hold tests, immutable candidate, fault-injected retain/restore. |
| Planetary/zoning validators | Attractive visual story exceeds evidence. | Required difference/contradiction/unavailable fields and negative fixtures. |

## Open design questions

| ID | Question | Disposition | Owner |
|---|---|---|---|
| DES-UNK-OSW-001 | Exact physical module/file split inside the current atlas. | Choose per bounded work package after characterization tests; no rewrite prerequisite. | KEEL |
| DES-UNK-OSW-002 | Concrete schema language/validator for common contracts. | Bake off minimal stdlib/custom validation versus a pinned schema dependency during implementation planning. | SOUNDER |
| DES-UNK-OSW-003 | Exact family-specific support precedence where interpolation products are themselves valid sources. | Each family design must declare source-product meaning and receipt; common rule remains conservative. | SOUNDER |
| DES-UNK-OSW-004 | Numeric performance, browser, viewport, contrast, and target thresholds. | Measure and decide in Validation; design exposes necessary instrumentation points. | HARBOR |
| DES-UNK-OSW-005 | Deployment/atomic rollback adapter. | Select in Implementation Plan; pure release reconciler is mechanism-independent. | LOGBOOK |
| DES-UNK-OSW-006 | Zoning diagnostic combination and scientific thresholds. | Controlled scientific method design and validation, not generic scoring. | CURRENT |

## Design gate

Decision: `pass_with_risk`

- [x] Every one of the 15 interfaces maps to design decisions and invariants.
- [x] State, evidence, map, admission, acquisition, payload, privacy, and release algorithms have explicit success/failure behavior.
- [x] Migration preserves current addresses and source truth without a rewrite.
- [x] Edge cases include scientific, data, cartographic, accessibility, compatibility, degraded, trust, and comparison paths.
- [x] Code-rigor hooks identify every high-risk implementation area.
- [x] Open questions are owned and assigned to legitimate later decisions.
- [x] Paired Code Rigor and all eight native-role reviews reach a fixed point with no unresolved P1/P2.

Implementation planning is authorized next but remains unopened.

## Source links

- [Code Rigor](CODE_RIGOR.md)
- [Interfaces](INTERFACES.md)
- [Architecture](ARCHITECTURE.md)
- [Package boundaries](PACKAGE_BOUNDARIES.md)
- [PITFALL register](../../design/pitfalls/README.md)
- [Central roadmap](../../ROADMAP.md)
- [Native roles](../../.roles/ROLE.md)
- [Design and Code Rigor roles review](../../signals/roles/check/design-code-rigor-roles-check-2026-09-07.md)

# OSW Interfaces

Status: settled at native-role fixed point 2026-09-06; support-model amendment in Design review 2026-09-07

## Scope

Repo: OSW — Ocean States of the World

This stage defines durable contracts crossing the eleven settled architecture
boundaries. It preserves the six public contracts already allocated by the
Specification Baseline and adds the internal contracts needed to make them
honest. It does not implement a schema library, move files, choose a browser
framework, define scientific algorithms, set performance or validation
thresholds, select a deployment mechanism, or open work packages.

Existing artifacts remain evidence, not automatically conforming instances.
Historical `oceanlines.*` and `osw.*` records remain source truth; a new
contract may be provided by a lossless adapter or additive sidecar rather than
rewriting historical bytes. An artifact becomes conforming only after its
applicable domain admissions pass.

## Contract conventions

### Identity and version

Every durable machine-readable record defined here carries:

| Field | Type | Rule |
|---|---|---|
| `contract` | non-empty string | Stable contract name in the `osw.*` namespace. |
| `contract_version` | positive integer | Version of this record contract, independent of product/release version. |
| `id` | stable non-empty string | Unique within the contract namespace; identity cannot be reassigned. |
| `lifecycle_state` | enum | Exactly one of `released`, `review_preview`, `experiment`, `research_intake`, `degraded`. |
| `artifact_sha256` | 64 lowercase hexadecimal characters or explicit `not_applicable` reason | Required when the record binds immutable bytes. |

Additive optional fields may appear in the same version. A field removal,
rename, meaning change, unit/default change, closed-enum change, or previously
valid-record rejection requires a new contract version and an explicit adapter
or rejection path. Unknown fields are preserved by lossless adapters where
possible and ignored only when they cannot change meaning. Unknown values in a
meaning-bearing vocabulary block the affected admission rather than coercing
to a default.

### Applicability

Required scientific fields may use an explicit object of the form
`{"status":"not_applicable","reason":"..."}` only when the controlling
contract says the field is conditional. Missing, unknown, unavailable, and not
applicable are different states. `unavailable` requires a reason and normally
keeps the relevant claim provisional or blocked.

### Error and diagnostic envelope

Any machine-detected interface failure emits or makes inspectable:

| Field | Rule |
|---|---|
| `code` | Stable diagnostic from the allocation table below. |
| `interface_id` | Interface whose contract failed. |
| `record_id` or `state_fragment` | Identifies the affected input without exposing secrets. |
| `field` | Exact failing field or `not_applicable`. |
| `expected` / `received` | Bounded, safe comparison; sensitive provider values may be redacted. |
| `impact` | Claim, artifact, view, or transition that is blocked/degraded. |
| `fallback` | Preserved artifact or accepted reader state, when one exists. |
| `message` | Actionable human-readable explanation. |

Diagnostics never silently repair scientific evidence. Public reader state
errors are announced without moving focus; pipeline errors preserve the last
accepted artifact and return a non-success status.

## Interface inventory

The first six IDs preserve the public-contract identities established in the
Specification Baseline.

| ID | Interface | Type | Owner | Producers | Consumers | Compatibility rule | Verification |
|---|---|---|---|---|---|---|---|
| IF-OSW-001 | Public entry and research index | path/docs contract | BEACON | PKG-001, PKG-011 | Readers, PKG-002 | Three primary route identities are controlled; accepted corpus destinations remain reachable or carry an explicit redirect/replacement. | Route/link and destination inventory fixtures. |
| IF-OSW-002 | Canonical reader URL/state | path/state/event contract | HARBOR | PKG-002 | PKG-001, PKG-003, PKG-004 | Version-1 query policy below; unversioned current links remain readable; unsafe/unknown/conflicting values produce announced field-local fallback. | Compatibility, transition, reload, history, and AT fixtures. |
| IF-OSW-003 | Scene-to-evidence receipt | receipt/path contract | SOUNDER | PKG-003, PKG-006 | Readers, researchers, PKG-009 | Scene binding cannot change receipt identity or broaden claim ceiling in-place; broken bindings block admission. | Missing/broken/mutated receipt fixtures. |
| IF-OSW-004 | Map view and equivalent text | data/model/render contract | CHART | PKG-004–006 | Readers, PKG-002, PKG-003, PKG-009 | Visual and text forms share one view/state/quantity identity; a projection or support semantic change is versioned. | Cross-family visual/text/map admission fixtures. |
| IF-OSW-005 | Released hosted state | registry/trust contract | LOGBOOK | PKG-010 | Readers, maintainers, citation/status surfaces | Only verified hosted bytes for an immutable released commit may change current-release claims; failure retains/restores prior state. | Drift, staging, hosted smoke, and rollback fixtures. |
| IF-OSW-006 | Browser request and privacy boundary | request/custody contract | LOGBOOK | PKG-001–005 | Readers, PKG-009, PKG-010 | No account, upload, cookie, telemetry, user-data collection, or undeclared third-party request; any change requires a new accepted requirement and public disclosure. | Static request/storage/capability inspection. |
| IF-OSW-007 | Quantity identity and claim ceiling | data/model contract | CURRENT | PKG-006, PKG-008 | PKG-003–005, PKG-009 | Core quantity meanings are closed within a contract version; extensions require registration and CURRENT/SOUNDER review. | Valid/incompatible quantity and escalation fixtures. |
| IF-OSW-008 | Guided scene contract | data/model/docs contract | BEACON | PKG-003, PKG-006 | PKG-001, PKG-002, readers | Scene identity/order and claim/limitation/receipt bindings are stable; prose may clarify without changing bound scientific meaning. | Complete/missing/reordered scene fixtures. |
| IF-OSW-009 | Spatial support and missingness | data/model contract | SOUNDER | PKG-006, PKG-008 | PKG-004, PKG-005, PKG-009 | Support-state meanings are closed; no state may be converted to valid ocean data by an adapter or renderer. | One fixture per support/mismatch class. |
| IF-OSW-010 | Federated admission disposition | registry/trust contract | KEEL for composition; domain vetoes retained | CURRENT, SOUNDER, CHART, HARBOR, KEEL, LOGBOOK, ORBIT as applicable | PKG-005, PKG-009, PKG-010 | Overall admission cannot pass while any required domain is fail, unknown, or missing; no role can override another domain's rejection. | Domain omission/veto/composition fixtures. |
| IF-OSW-011 | Acquisition and custody receipt | API/provider/receipt contract | SOUNDER | PKG-007 | PKG-008, PKG-009 | Request and response identities are immutable; a failed/mismatched refresh cannot replace accepted custody bytes. | Dry-run, checksum, rights, timeout, and stale-source fixtures. |
| IF-OSW-012 | Generated artifact family and integrity | receipt/descriptor contract | KEEL | PKG-006, PKG-008, PKG-009 | PKG-005, PKG-010, maintainers | Family identity, generator, inputs, outputs, comparison mode, and payload class are versioned; all admitted families require an offline integrity path. | Representative family and mutation fixtures. |
| IF-OSW-013 | External review record | receipt/trust contract | LOGBOOK | External reviewer/maintainer handoff | PKG-006, PKG-010 | Review binds immutable artifact identity and disposition; it grants neither endorsement nor release authority. | Missing-identity, changed-artifact, and authority-language fixtures. |
| IF-OSW-014 | Planetary comparison | data/model/docs contract | ORBIT | PKG-003, PKG-006 | Readers, PKG-009 | Comparison references admitted quantity identities; regime differences and weakening outcome cannot be removed in-place. | Mechanism-valid and resemblance-only fixtures. |
| IF-OSW-015 | Zoning boundary scorecard | data/model/scenario contract | CURRENT | PKG-006, PKG-008 | CHART, PKG-009, researchers | Organizational/diagnosed class and each diagnostic remain explicit; unavailable evidence cannot be coerced into a score or promotion. | Retain/merge/split/move/demote and attractive-false-border fixtures. |

## IF-OSW-001 — public entry and research index

### Contract

| Field | Cardinality | Rule |
|---|---|---|
| `routes` | exactly one ordered registry of three records | Records have stable `route_id` values `explore`, `heat`, `evidence`; no fourth primary route without controlled change. |
| `label` | one per route record | Human-readable; label changes require controlled BEACON review but IDs remain stable. |
| `target` | one local address per route record | Must resolve in one action from the entry surface. |
| `outcome` | one per route record | Declares the reader task, not internal stage/process status. |
| `research_index` | exactly one reachable secondary destination | Contains every admitted legacy public destination or an explicit replacement/retirement record. |
| `release_status` | one | Derived from IF-OSW-005; cannot infer branch preview as released. |

Errors: missing/duplicate primary route, unresolved destination, corpus orphan,
or release-state disagreement blocks entry-surface admission. Internal VTRACE,
work-package, role-readiness, and pitfall IDs may appear in expert governance
documents but are forbidden as primary visitor route state.

## IF-OSW-002 — canonical reader URL/state

### Version-1 state fields

| Query key | State meaning | Value contract | Current/target posture |
|---|---|---|---|
| `v` | State contract version | Positive integer; target writer emits `1`; absence invokes legacy-v0 adapter. | target/additive |
| `route` | Primary journey | `explore`, `heat`, `evidence`. | target |
| `province` | Classic province identity | Registered province code. | current |
| `object` | Ocean-object identity | Registered object/feature ID; legacy `feature` is a read alias in v1. | target with current alias |
| `mode` | Evidence/map mode | Current canonical tokens `sst`, `anomaly`, `argo700`, `error`; `observed` is a legacy read alias for `sst`; conceptual is the absence/default. New values require registration. | current |
| `depth` | Conceptual depth filter | `surface`, `upper`, `intermediate`, `deep`, `bottom`, `full-column`, `seabed`; `all` is represented by absence. | current |
| `event` | Event identity | Registered event/study identity. | target |
| `scene` | Ordered event scene | Registered scene ID valid for selected event. | target |
| `projection` | Projection identity | Registered admitted projection ID. | target |
| `lens` | Conceptual geography lens | `waters`, `flows`, `edges`, `floor`, `life`, `events`; `all` remains readable; default is `waters`. | current |
| `view` | Conceptual layout | `reference`, `water-first`, `shape-first`; canonical default is `water-first`. | current |
| `property` | Conceptual property filter | `warm`, `cold`, `fresh`, `salty`, `dynamic`, `low-oxygen`, `nutrient-rich`, `nutrient-poor`, `relief`; `all` is represented by absence. | current |
| `clock` | Conceptual timescale filter | `persistent`, `seasonal`, `interannual`, `episodic`, `geologic`; `all` is represented by absence. | current |
| `pressure` | Argo pressure surface | `10`, `300`, `700`, `1000`, valid only with `mode=argo700` in v1. | current legacy token preserved |
| `ring` | Polar mirror latitude | Finite absolute latitude from 0 through 89 degrees; writer emits three decimal places. Target validation rejects rather than silently clamps an out-of-range direct value. | current range; target diagnostic |
| `lat`, `lon` | Coordinate probe | Finite pair with latitude −90…90 and longitude −180…180 degrees; neither acts alone; writer emits three decimal places. | current |
| `hierarchy` | Region/state hierarchy display | Registered display preference. | target |
| `hairlines` | Internal province-line display | Boolean token `on` or `off`. | target |

Compatibility policy:

1. Existing unversioned Atlas 07–10 links are treated as `legacy-v0` and remain
   readable throughout the first integrated v1 release line.
2. The v1 writer emits canonical keys, never the `feature` alias, while the v1
   reader accepts `feature` when `object` is absent. Conflicting `object` and
   `feature` values reject the alias and announce the conflict.
3. Additive optional keys/values require registry and fixture updates. Meaning,
   default, or token removal requires a new integer version.
4. A new version must dual-read the immediately preceding version for at least
   one subsequent public release. Retirement requires LOGBOOK owner approval,
   release notes, and a safe fallback fixture.
5. Unknown version blocks only the unsupported state fragment and returns to a
   usable default route. Unknown key/value and incompatible combination are
   exposed once as a consolidated diagnostic and announced without focus theft.
6. Fallback removes the least foundational invalid dimension first: probe,
   presentation preference, scene, event, object, province, then route. It
   preserves every still-compatible accepted dimension.

Canonical state is transactional: URL, internal state, visible selection,
focus context, programmatic name/state, live announcement, map/text output, and
receipt route commit together or remain at the previous accepted state.

## IF-OSW-003 — scene-to-evidence receipt

| Field | Cardinality | Rule |
|---|---|---|
| `scene_id` | one | Must resolve through IF-OSW-008. |
| `claim_id` | one | Principal finding identity; resolves to admitted claim ceiling. |
| `limitation_id` | one | Strongest material limitation for this scene; simultaneously discoverable with the finding. |
| `evidence_id` | one or more | Identifies result/display evidence supporting the claim. |
| `receipt_id` | one or more | Resolves to the evidence-receipt envelope below; no dead or ambiguous target. |
| `value_bindings` | zero or more | Each displayed quantitative value names result artifact, record path, unit, and formatting rule; uncontrolled copied constants are forbidden. |
| `evidence_class` | one | Registered origin/class consistent with the receipt. |
| `claim_ceiling_id` | one | Scene prose and alt text cannot exceed it. |

A receipt-binding mutation, missing limitation, changed result checksum,
broadened claim, or unresolved path blocks scene admission rather than leaving a
stale public value.

### Evidence-receipt envelope

| Group | Required fields |
|---|---|
| Identity | `contract`, `contract_version`, `id`, `lifecycle_state`, bound artifact paths and SHA-256 identities. |
| Source | provider, product, variable ID, product/version, source URL or catalogue identity, citation, license, redistribution posture. |
| Acquisition | request/query identity, acquisition time, requested interval/domain/depth/stride, source-response checksum, authentication/redaction posture. |
| Quantity | IF-OSW-007 identity, units, sign/orientation, reference state, constants/conventions. |
| Support | time, vertical/layer, spatial/grid, masks/missingness/quality, collocation/interpolation/partial-cell/stencil rules as applicable. |
| Transformation | generator/method identity, input identities, parameters, dependency/environment identity, output identities. |
| Claim | evidence origin/class, claim stage, supported statements, prohibited statements, limitation, next evidence, claim-ceiling ID. |
| Checks | source, intermediate, result, and display checksums plus performed validation/sensitivity identities. |

Historical receipts may be adapted into this envelope only when the adapter is
lossless for meaning-bearing fields and records unavailable fields explicitly.

## IF-OSW-004 — map view and equivalent text

| Field | Applicability | Rule |
|---|---|---|
| `view_id`, `state_version` | required | Same identity drives visual and text forms. |
| `projection_id`, `aspect`, `extent` | required for geographic maps | Registered projection and bounded domain. |
| `time_support`, `vertical_support` | required or explicit not-applicable | Never inferred from title alone. |
| `quantity_id`, `units` | required for quantitative maps | Resolve through IF-OSW-007. |
| `evidence_class`, `source_ids` | required | Consistent with receipts. |
| `scale`, `legend`, `palette_semantics` | applicable | Include order, midpoint/zero, clipping, categories, and unit. |
| `boundary_class` | applicable | One registered class with redundant line/label/legend/text treatment. |
| `uncertainty_or_sensitivity` | required | Evidence identity or explicit unavailable reason. |
| `support_contract_id` | required | Resolves through IF-OSW-009. |
| `seam_rule`, `polar_rule`, `coastline_context` | geographic maps | Explicit, even when not visually prominent. |
| `comparison_capabilities` | required | Booleans for area, shape, distance, direction, and cross-panel comparison with reasons when prohibited. |
| `text_alternative` | required | Data-oriented summary of the same accepted state, finding, scale/extrema/category, missingness, and limitation. |

Rendered geometry cannot change quantity, evidence, support, or boundary class.
An image-only standalone SVG may satisfy the text side through an adjacent
linked alternative, but admission binds both identities.

Initial boundary-class vocabulary is `conceptual`, `classic_reference`,
`organizational_schematic`, `thresholded`, `diagnosed`, `modeled`, and
`observed`. A new class requires a registered meaning and redundant visual/text
treatment; adapters may not promote one class to another.

## IF-OSW-005 — released hosted state

Evidence identity reaches this boundary only through IF-OSW-003 and federated
IF-OSW-010 admission. Release may bind those immutable identities but never
backfill, reinterpret, or change them.

### Record

| Field | Rule |
|---|---|
| `release_id`, `version`, `commit_sha` | Immutable candidate identity. |
| `prior_release_id`, `prior_commit_sha` | Required for retain/restore proof after the first release. |
| `intended_host` | Exact target identity; mechanism remains Implementation Plan work. |
| `lifecycle_registry_sha256` | Binds exactly-one state for every controlled artifact. |
| `surface_identities` | README, roadmap, preview status, source register, publication checklist, citation, generated artifacts, and release notes. |
| `admission_dispositions` | IF-OSW-010 identities with no missing/failed required domain. |
| `verification_evidence` | Offline gate identity plus required browser/performance evidence. |
| `owner_decision` | Explicit approve/hold identity; role approval alone is insufficient. |
| `hosted_commit_proof`, `journey_smoke` | Required before status/citation current-state update. |
| `outcome` | `released`, `held`, `retained_prior`, or `restored_prior`; failure detail uses diagnostic envelope. |

## IF-OSW-006 — browser request and privacy boundary

The admitted runtime request set consists only of same-origin static assets
declared by the selected view's display-bundle descriptor. The descriptor
records path, SHA-256 where practical, media type, payload class, and owning
view/family. Browser storage/capability inventory must report zero accounts,
uploads, cookies, telemetry, service-worker collection, user identifiers, and
undeclared third-party requests.

External source and citation links may navigate only after deliberate user
activation; they are not silently prefetched as scientific data or telemetry.
Any future exception is a new requirement and privacy/security review, not an
optional field in this contract.

## IF-OSW-007 — quantity identity and claim ceiling

| Field | Rule |
|---|---|
| `quantity_id` | Stable registered identity. |
| `quantity_class` | Core values: `temperature`, `temperature_anomaly`, `heat_content`, `storage_tendency`, `velocity`, `volume_transport`, `reference_relative_heat_transport`, `horizontal_advection`, `convergence`, `transformation`, `residual`; other ocean quantities require registered extension. |
| `variable_ids`, `units`, `dimensions` | Source variables and resulting dimensional identity. |
| `time_support`, `vertical_support`, `spatial_support` | Explicit measurement/integration support. |
| `reference_state`, `sign_orientation` | Required when meaning can change with reference/sign; otherwise explicit not-applicable. |
| `integration_or_operator` | Declares none, point/sample, area, depth, section, volume, derivative, convergence, transformation, or residual operation as applicable. |
| `evidence_origin`, `method_class` | Distinguishes observed, derived, assimilative/model, simulation, conceptual, and sensitivity evidence. |
| `supports`, `does_not_support` | Controlled claim ceiling; prohibited stronger interpretations are explicit. |

A budget record is an ordered set of independently receipted quantity IDs plus
an explicit residual identity. Numerical proximity does not change a term or
residual class. Motion/path/open-section classes prohibit delivery,
probability, residence, transported volume, convergence, and regional-budget
claims unless a separately admitted quantity supplies that evidence.

Initial `evidence_origin` values preserve the existing receipt vocabulary:
`observational_analysis`, `derived_observation_product`,
`assimilative_reanalysis`, `operational_assimilative_model`,
`operational_forecast_model`, `simulation`, and `conceptual_synthesis`.
`method_class` separately states whether the displayed result is source field,
derived diagnostic, sensitivity, comparison, or unresolved remainder; origin
and method must not be collapsed into one label.

## IF-OSW-008 — guided scene

| Field | Rule |
|---|---|
| `scene_id`, `event_id`, `ordinal` | Stable within the event route; ordinals are unique and contiguous. |
| `question` | One consequential reader question. |
| `finding_claim_id` | Exactly one principal finding. |
| `limitation_id` | Exactly one strongest material limitation, visible in the same claim context. |
| `receipt_binding_id` | Resolves through IF-OSW-003. |
| `map_view_id` | Optional only when the scene is explicitly non-map; otherwise IF-OSW-004. |
| `required_state`, `compatible_state` | Declares preserved and rejected state dimensions. |
| `previous_scene`, `next_scene` | Ordered journey; terminal scene has explicit unresolved outcome. |
| `text_alternative_id` | Required and state-synchronized. |

The first accepted heat journey contains event qualification/footprint,
lineage, surface temperature, surface forcing, fixed-column storage,
horizontal advection, and unresolved terms. These may be grouped visually, but
none may disappear from the ordered semantic route.

## IF-OSW-009 — spatial support and missingness

Every sampled cell/feature exposed to rendering carries three orthogonal axes:

| Axis | Values | Rule |
|---|---|---|
| `geometry_support` | `ocean`, `land`, `out_of_domain` | Only ocean geometry may carry an ocean value. |
| `data_status` | `valid`, `source_missing`, `quality_rejected`, `analysis_invalid` | Only valid data may carry the admitted quantity; non-valid states remain distinct. |
| `surface_condition` | `open_water`, `sea_ice`, `unknown`, `not_applicable` | Sea ice is an independent surface condition and does not erase otherwise valid subsurface ocean data. |

A record also declares grid/coordinate order, longitude convention, time/depth
support, source mask/flag mapping, and each transformation of all three axes.
Rendered treatment must make every applicable state recoverable without
conflating geometry, data validity, and surface condition.

Checksum, schema, dimension, coordinate/order, unit, sign, mask, collocation,
partial-cell, stencil, and time-support mismatch are distinct diagnostics. They
block the affected result/display/claim and cannot yield the combination
`geometry_support=ocean` with `data_status=valid`.

This orthogonal model supersedes the single mutually exclusive support enum in
the 2026-09-06 fixed point. The prior reviewed bytes remain identified by that
review's SHA-256; this amendment is reviewed with the paired Design/Code Rigor
stage and does not claim implementation.

## IF-OSW-010 — federated admission disposition

| Field | Rule |
|---|---|
| `candidate_id`, `artifact_sha256`, `family_id`, `lifecycle_state` | Immutable candidate context. |
| `spec_ids`, `interface_ids`, `pitfall_ids` | Exact controlled obligations exercised. |
| `domain` | One of `physical_claim`, `evidence_identity`, `cartography`, `public_explanation`, `accessibility`, `reproducibility`, `lifecycle_truth`, `planetary_transfer`. |
| `applicability` | `required` or reasoned `not_applicable`; comparison domain is conditional, all others follow family policy. |
| `decision` | `pass`, `fail`, or `unknown`; `unknown` never counts as pass. |
| `role`, `evidence_ids`, `finding_ids`, `decided_at` | Accountable native lens and immutable proof/disposition identities. |

Overall `admitted=true` only when every required domain is present and `pass`.
Any `fail`, `unknown`, missing domain, or unjustified `not_applicable` yields
`admitted=false`. The composition layer reports decisions and cannot change
them. Admission says nothing about release; lifecycle and IF-OSW-005 still
govern public current state.

## IF-OSW-011 — acquisition and custody

| Field group | Required content |
|---|---|
| Source identity | Provider, product, variable/version, endpoint/catalogue, citation, license/redistribution. |
| Request identity | Canonical request parameters, request hash, requested time/depth/domain/grid/stride, expected media/schema/dimensions. |
| Execution | Explicit command identity, environment/dependency identity, acquisition timestamp, authentication redaction. |
| Response | HTTP/provider status where applicable, byte count, media/schema/dimensions, SHA-256, validation result. |
| Custody | Local/external/archive location class, retention/reconstruction rule, downstream artifact IDs. |
| Failure | Diagnostic, retry posture, preserved prior accepted identity; no accepted-path overwrite. |

Dry-run records may prove request shape but must say `payload_acquired=false` and
cannot satisfy a scientific-result receipt.

## IF-OSW-012 — generated artifact family and integrity

| Field | Rule |
|---|---|
| `family_id`, `family_version`, `owner` | Stable generated-artifact family identity. |
| `artifact_class` | `scientific_result`, `display_field`, `figure_map`, `registry_table`, `public_prose_status`, or `review_governance`; extensions registered. |
| `generator_command` or `integrity_command` | Deterministic offline path; command may use local fixtures/accepted inputs only. |
| `dependency_profile`, `input_ids`, `output_ids` | Pinned applicable environment and complete lineage. |
| `comparison_mode` | Exact bytes, canonical structured equality, numeric tolerance with reason, SVG/HTML semantic contract, or inspection-only with explicit limitation. |
| `payload_class` | `critical_path`, `selected_view`, `evidence_on_demand`, or `custody_external`. |
| `admission_id`, `lifecycle_state` | IF-OSW-010 result and exactly-one controlled lifecycle state. |

An admitted family must have a representative positive fixture, at least one
contract-relevant negative/mutation fixture, and an explicit update rule. The
complete family inventory remains an implementation-planning prerequisite;
this interface defines its rows without claiming it already exists.

## IF-OSW-013 — external review

Required fields: review ID, reviewed artifact path and SHA-256, source commit,
reviewer identity or bounded anonymous identifier, role/lens, date, findings,
P1/P2/P3 severity, disposition, open conditions, and explicit
`scientific_endorsement=false`, `release_authority=false`. A later artifact
change makes the review stale rather than silently transferring approval.

## IF-OSW-014 — planetary comparison

Required fields: comparison ID; Earth and planetary quantity IDs; evidence
receipts for both; shared mechanism/property; forcing, stratification,
rotation, depth, compressibility, boundary, and observation-method differences;
explicit analogous, unknown, and non-analogous statements; nondimensional or
budget comparison where available; weakening/falsifying outcome; admission ID.
Missing planetary evidence may support a clearly speculative comparison but
cannot be represented as a measured equivalence.

## IF-OSW-015 — zoning boundary scorecard

Required fields: candidate boundary ID/version, geometry identity, current
boundary class, time/depth/domain support, and separate records for persistence,
cross-boundary exchange, retention, convergence, vertical agreement, and gate
dependence. Each diagnostic is `supporting`, `contradictory`, `neutral`, or
`unavailable` with evidence identity and sensitivity. Decision is one of
`retain`, `merge`, `split`, `move`, or `demote`, with rationale and CURRENT/CHART
admission. No arithmetic score or visual fit alone may promote a boundary to
diagnosed; exact combination/threshold remains Design/Validation work.

## Diagnostic allocation

| Code | Interface | Meaning | Required behavior |
|---|---|---|---|
| `OSW-IF-CONTRACT-VERSION` | all | Unsupported or missing required contract version. | Block affected record; preserve prior accepted state/artifact. |
| `OSW-IF-REQUIRED-FIELD` | all | Required/applicable field absent. | Block affected admission and name field. |
| `OSW-STATE-UNKNOWN` | 002 | Unknown key/value or unsupported version. | Field-local safe fallback plus visible/announced diagnostic. |
| `OSW-STATE-CONFLICT` | 002 | Values or aliases conflict. | Reject least-authoritative fragment and preserve compatible state. |
| `OSW-STATE-INCOMPATIBLE` | 002 | Individually valid fields form an invalid combination. | Transactional fallback; no split visual/semantic state. |
| `OSW-CLAIM-CEILING` | 003, 007, 008, 014 | Claim exceeds admitted quantity/evidence. | Block scene/comparison admission. |
| `OSW-RECEIPT-BINDING` | 003, 005 | Missing, stale, ambiguous, or checksum-inconsistent receipt path. | Block dependent scene/release. |
| `OSW-MAP-CONTRACT` | 004, 009 | Projection, support, boundary, comparison, or text/visual mismatch. | Block affected map family. |
| `OSW-PRIVACY-BOUNDARY` | 006 | Undeclared request, storage, upload, account, cookie, telemetry, or collection. | Block release. |
| `OSW-QUANTITY-IDENTITY` | 007 | Unknown/incompatible quantity, unit, reference, sign, support, or operator. | Block affected result and claim. |
| `OSW-SUPPORT-MISMATCH` | 009 | Any declared support/mask/numerical boundary mismatch. | Block affected result; never coerce valid ocean. |
| `OSW-ADMISSION-INCOMPLETE` | 010 | Required domain missing, failed, unknown, or unjustifiably not applicable. | Overall admission false; preserve domain decisions. |
| `OSW-ACQUISITION-FAILED` | 011 | Provider/request/response/rights/checksum validation failed. | Non-success; preserve prior accepted custody artifact. |
| `OSW-ARTIFACT-INTEGRITY` | 012 | Generator/input/output/comparison or family contract drift. | Block admission/release for affected family. |
| `OSW-REVIEW-STALE` | 013 | Reviewed bytes differ or required review field is absent. | Review cannot satisfy admission/release. |
| `OSW-ZONE-EVIDENCE` | 015 | Diagnostic missing/coerced or promotion unsupported. | Keep/demote provisional class; block diagnosed promotion. |
| `OSW-RELEASE-DRIFT` | 005 | Candidate commit, lifecycle, status, citation, artifact, or owner decision disagree. | Hold release without changing current claims. |
| `OSW-DEPLOY-UNVERIFIED` | 005 | Hosted commit/journey smoke absent or failed. | Retain/restore prior release and metadata. |

## Contract-boundary and fixture impact

| Interface group | Boundary classes | Minimum fixture classes | Docs/corpus effect |
|---|---|---|---|
| 001–002 | path/address, state/model, event, docs/corpus | golden, negative, compatibility, inspect/report | Public route and shared-link documentation. |
| 003–010 | data/model, receipt/evidence, descriptor, diagnostic | golden, negative, regression, corpus, inspect/report | Researcher receipt/claim/map/admission explanation. |
| 011–012 | API/provider, custody/rights, receipt, descriptor | golden dry-run, negative, adversarial, regression, corpus | Acquisition and reproducibility instructions. |
| 013–015 | trust/registry, scenario, docs/corpus | golden, negative, stale/adversarial, inspect/report | Review boundary, analogy guide, zoning research record. |
| 005–006 release aspects | trust/registry, custody/privacy, path/address | compatibility, adversarial, regression, inspect/report | Release status, citation, privacy disclosure. |

Actual fixture files and owning work packages remain unopened Design,
Implementation Plan, and Verification work. This stage controls their required
shape and diagnostic identities so later plans cannot omit negative paths.

## Interface coverage

| Specification range | Interfaces | Coverage |
|---|---|---|
| 001–007 | 001, 003, 008 | Entry, corpus preservation, guided journey, claim/limitation/receipt binding. |
| 008–010 | 002, 004, 007, 009 | Province/object state and direct non-aggregated evidence. |
| 011–018 | 003, 007, 010, 014, 015 | Quantity/budget/motion/zoning/analogy/authority ceilings. |
| 019–024 | 003, 005, 009, 011, 012 | Receipt lineage, masks, mismatch, offline acquisition/degraded operation. |
| 025–030 | 002, 004, 009, 010 | Map admission, accessibility, state equivalence, reflow contract inputs. |
| 031–034 | 006, 011, 012 | Payload class, custody, family integrity, intake-ready descriptors. |
| 035–040 | 005, 010, 012, 013 | Review identity, lifecycle, release reconciliation, hosted outcome. |
| 041–043 | 002 | URL inventory, version policy, migration, and announced fallback. |
| 044–045 | 006 | Static no-collection request/privacy boundary and controlled change. |

## Open interface risks and controlled deferrals

| Risk | Current disposition | Must close by | Owner |
|---|---|---|---|
| Existing schemas may not losslessly populate every new receipt field. | Adapter emits explicit unavailable fields and blocks claims needing them; never fabricates values. | Design before family admission | SOUNDER |
| The semantically awkward current `mode=argo700` token also carries other pressure levels. | Preserve through v1 to avoid link breakage; consider replacement only in a future version with dual-read adapter. | Later compatibility amendment | HARBOR |
| Complete artifact-family and runtime-request inventories do not yet exist. | IF-OSW-006/012 define the rows; inventory is required before implementation/release planning closes. | Implementation Plan / Validation | KEEL |
| Numeric performance, viewport, zoom, contrast, and target thresholds remain unmeasured. | Contract carries state/payload/semantic requirements; thresholds remain Validation inputs. | Validation | HARBOR |
| Hosted commit proof and atomic retain/restore mechanism remain unknown. | IF-OSW-005 fixes required evidence/outcome without selecting mechanism. | Implementation Plan | LOGBOOK |
| Zoning diagnostic combination/threshold is unresolved. | IF-OSW-015 prohibits unavailable-to-score coercion and visual-only promotion. | Design / Validation | CURRENT |

## Interface gate

Decision: pass_with_risk

- [x] All six existing public contract identities are preserved.
- [x] Every Architecture boundary crossing has an owned interface or explicit internal deferral.
- [x] All 45 controlled specification items map to interface contracts.
- [x] Versioning, applicability, error, compatibility, and safe-fallback rules are explicit.
- [x] Scientific quantity, receipt, support, map, scene, admission, acquisition, artifact, review, comparison, zoning, release, and privacy shapes are controlled.
- [x] Positive, negative, compatibility, stale/adversarial, and inspection fixture obligations are identified without opening work packages.
- [x] Historical records remain source truth and require lossless adapters or explicit unavailability, never invented fields.
- [x] All eight native roles have reviewed the interfaces and every P1/P2 finding is repaired or explicitly controlled.

Design and Code Rigor are authorized as the next paired, separately reviewed
stage but remain unopened. Remaining risks have explicit later-stage owners and
cannot be treated as implemented behavior.

## Source links

- [Architecture](ARCHITECTURE.md)
- [Package boundaries](PACKAGE_BOUNDARIES.md)
- [Specification Baseline](SPECIFICATION_BASELINE.md)
- [Requirements](REQUIREMENTS.md)
- [PITFALL register](../../design/pitfalls/README.md)
- [Central roadmap](../../ROADMAP.md)
- [Native roles](../../.roles/ROLE.md)

The native-role fixed-point review is recorded in
[`interfaces-roles-check-2026-09-06.md`](../../signals/roles/check/interfaces-roles-check-2026-09-06.md).

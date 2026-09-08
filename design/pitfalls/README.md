# OSW Pitfall Register

Recurring structural failure modes in ocean science, data processing,
cartography, and delivery. These are not individual bug reports. Each pitfall
states the pattern that permits a class of errors, the structural prevention
OSW should enforce, and the proof that would fail if that prevention vanished.

Owned by OSW's native `.roles`. CURRENT breaks scientific-inference ties,
SOUNDER data/numerical ties, CHART cartographic ties, and KEEL/LOGBOOK delivery
ties.

## Status rule

- **OPEN:** no adequate structural prevention exists.
- **MITIGATED:** controls or tests reduce the risk but another path can still
  reproduce the failure.
- **SOLVED:** a structural prevention makes the failure mode unavailable and a
  regression test fails if that prevention is removed.

The register never labels a pitfall solved from careful prose, reviewer memory,
or one passing example alone. It grows when OSW discovers a reusable failure
pattern and does not shrink; superseded entries retain their history.

## Register

| ID | Parent constraint | Specification controls | Domain | Pitfall | Status | Current proof or gap |
|---|---|---|---|---|---|---|
| SI-01 | `CON-OSW-003` | `SPEC-OSW-011`, `012`, `019`, `020`, `025`, `026` | Scientific inference | Temperature or anomaly is narrated as heat content or heat transport. | mitigated | Atlas and view tests assert claim-boundary language, but no shared typed quantity contract governs every artifact. |
| SI-02 | `CON-OSW-004` | `SPEC-OSW-011`, `012`, `019`, `020` | Scientific inference | A residual, correlation, or numerical near-balance is named as a physical process or causal closure. | mitigated | Nordic and D14 tests preserve remainder identities and “not closure” language; new prose can still bypass them. |
| SI-03 | `CON-OSW-003`, `CON-OSW-011` | `SPEC-OSW-011`–`014` | Scientific inference | One open section, streamline, or parcel count is presented as delivery, convergence, probability, or transported volume. | mitigated | `analysis/test_section_transport.py` and pathway-view tests reject several forms; coverage is artifact-specific. |
| DN-01 | `CON-OSW-002`, `CON-OSW-003` | `SPEC-OSW-011`, `012`, `019`, `020`, `022` | Data and numerics | Heat-transport sign or reference-temperature choice changes meaning without being exposed. | mitigated | Section and seasonal synthesis tests check signed branches and reference-change identities; interfaces are not yet globally controlled. |
| DN-02 | `CON-OSW-002`, `CON-OSW-009` | `SPEC-OSW-019`–`024`, `033`, `034` | Data and numerics | Grid staggering, masks, partial cells, interpolation, or time support silently change the sampled physical quantity. | mitigated | Mesh, mask, thickness, collocation, and stencil tests exist; offline diagnostics still depend on declared approximations. |
| CA-01 | `CON-OSW-006` | `SPEC-OSW-021`, `022`, `025`, `026` | Cartography | Land overlap, projection seams, or clipping creates or destroys an apparent ocean object. | mitigated | `analysis/test_atlas.py` checks ocean masks and seam continuations for the shared atlas; standalone and future views need the same structural path. |
| CA-02 | `CON-OSW-001`, `CON-OSW-005`, `CON-OSW-007` | `SPEC-OSW-010`, `013`, `014`, `025`, `026` | Cartography | Crisp boundaries, palette, or hierarchy makes schematic regions look uniquely physical or color becomes the only meaning. | mitigated | Atlas tests require provisional labels, hierarchy, and non-color summaries; the organizational partition remains visually persuasive. |
| DL-01 | `CON-OSW-010` | `SPEC-OSW-035`–`040` | Delivery | README, preview, citation, hosted release, and evidence registers describe different project states. | open | The baseline records known `PREVIEW-STATUS.md` drift; no single release-state contract prevents recurrence. |
| DL-02 | `CON-OSW-001`, `CON-OSW-002`, `CON-OSW-008` | `SPEC-OSW-006`, `007`, `019`, `020`, `033`–`038` | Delivery | Headline prose or generated figures drift from machine-readable receipts. | mitigated | Many analysis tests pin receipt values and SVG language; coverage is not yet registry-wide. |
| DL-03 | `CON-OSW-014` | `SPEC-OSW-031`–`034`, `037`, `038` | Delivery | Reproducibility payloads make the public repository or atlas unnecessarily heavy. | open | The current large push exposes the risk; no measured hosted baseline, load-on-demand contract, or external data-custody policy is settled. |

## Architecture containment

The settled Architecture does not mark any pitfall solved. It removes several
reverse-dependency paths and assigns the remaining structural work:

| Pitfalls | Architecture containment | Remaining proof |
|---|---|---|
| SI-01–SI-03, DN-01 | Build-time scientific transformation; the browser cannot derive, aggregate, widen a claim, assign a remainder, or overrule CURRENT. | Shared quantity/claim interfaces and cross-family negative fixtures. |
| DN-02 | Acquisition, custody, transformation, display derivative, and receipt remain separate identities; mismatches stop before admission. | Interface representation and family-complete mismatch tests. |
| CA-01, CA-02 | The renderer consumes typed masks/classes and canonical state; it cannot repair support or invent authority. | Cross-family cartographic admission and equivalent text/visual proof. |
| DL-01 | Scientific admission, lifecycle, owner decision, deployment, hosted proof, and current/citation update are separate ordered authorities. | Reconciled release contract and fault-injected hosted transition. |
| DL-02 | One-way result → display → claim lineage; presentation cannot copy uncontrolled quantities beyond the claim ceiling. | Common receipt/claim binding and mutation coverage. |
| DL-03 | The thin reader consumes selected-view web derivatives; heavyweight custody remains outside eager runtime loading. | Artifact-family inventory, hosted measurement, and custody policy. |

Architecture decisions and failure modes are recorded in
[`docs/vtrace/ARCHITECTURE.md`](../../docs/vtrace/ARCHITECTURE.md); detailed
authority seams are in
[`docs/vtrace/PACKAGE_BOUNDARIES.md`](../../docs/vtrace/PACKAGE_BOUNDARIES.md).

## Interface controls

| Pitfalls | Controlling interfaces | Failure that must become observable |
|---|---|---|
| SI-01, SI-02 | `IF-OSW-003`, `007`, `010` | Quantity/receipt incompatibility or claim-ceiling escalation blocks admission. |
| SI-03 | `IF-OSW-007`, `010` | Motion, path, or open-section evidence cannot satisfy delivery/convergence claims. |
| DN-01 | `IF-OSW-003`, `007`, `009`, `010` | Unit, sign, reference, support, or operator mismatch blocks the affected result. |
| DN-02 | `IF-OSW-003`, `009`, `011`, `012` | Sampling/support mismatch or failed acquisition preserves prior accepted artifacts. |
| CA-01, CA-02 | `IF-OSW-002`, `004`, `009`, `010`, `015` | Visual/text/map disagreement, fabricated support, or unsupported border promotion fails. |
| DL-01 | `IF-OSW-005`, `010`, `012`, `013` | Lifecycle/status/citation/commit/hosted disagreement holds release. |
| DL-02 | `IF-OSW-003`, `008`, `012` | Changed receipt/result invalidates bound scene values, figures, and prose. |
| DL-03 | `IF-OSW-005`, `006`, `011`, `012` | Undeclared eager payload or missing custody classification blocks release. |

Field-level contracts, compatibility rules, and stable diagnostics are recorded
in [`docs/vtrace/INTERFACES.md`](../../docs/vtrace/INTERFACES.md). Interface
definition mitigates these paths but does not solve them until implementations
and regression fixtures make the failure modes unavailable.

## Design and Code Rigor controls

The settled detailed design and rigor profiles keep every pitfall status
conservative. They specify the prevention seam and required proof, but no entry
becomes solved until implementation makes the failure unavailable and its
regression fixture passes.

| Pitfalls | Design / rigor containment | Remaining proof |
|---|---|---|
| SI-01–SI-03, DN-01 | Typed value bindings, lossless evidence adapters, pure domain validators, and physical-identity tests prevent prose or presentation from silently widening quantity and mechanism claims. | Implement the shared contracts and pass quantity, sign/reference, remainder, motion-only, and receipt-mutation fixtures. |
| DN-02 | Acquisition, validation, custody, calculation, and publication are separate phases; geometry support, data status, and surface condition are orthogonal axes. | Pass mismatch/fault-injection fixtures, including valid subsurface ocean data beneath sea ice. |
| CA-01, CA-02 | One admitted view model drives visual and textual renderers; map support and boundary authority cannot be invented by paint or projection. | Pass cross-render equivalence, land/seam, non-color, and attractive-false-border fixtures. |
| DL-01 | Pure release reconciliation must return `hold` before any deployment side effect when lifecycle, admission, status, citation, commit, payload, or hosted proof disagrees. | Select the deployment adapter and pass deliberate-drift plus failed-host rollback scenarios. |
| DL-02 | Guided-scene values resolve into admitted result records; changed or missing paths invalidate the scene instead of retaining copied numbers. | Implement registry-wide value bindings and receipt-mutation coverage. |
| DL-03 | A manifest classifies critical, selected-view, evidence-on-demand, and external-custody payloads; undeclared runtime requests fail. | Inventory payloads, measure the hosted baseline, set budgets, and pass selected/unselected request traces. |

The component algorithms and invariants are in
[`docs/vtrace/DESIGN.md`](../../docs/vtrace/DESIGN.md); the proportional L0/L1/L2
profiles, waivers, and evidence rules are in
[`docs/vtrace/CODE_RIGOR.md`](../../docs/vtrace/CODE_RIGOR.md).

## Implementation Planning containment

The settled plan does not change any pitfall status. It assigns structural work
and the proof that must exist before a future package may claim closure:

| Pitfalls | Owning proposed packages | Planning containment |
|---|---|---|
| SI-01–SI-03, DN-01, DN-02 | WP-OSW-001, WP-OSW-004, WP-OSW-006 | Contract/admission pulses precede presentation; guided and new science keep quantity, residual, support, sign/reference, custody, and mutation fixtures. |
| CA-01, CA-02 | WP-OSW-003, WP-OSW-007 | Complete map-family applicability inventory, one visual/text view model, orthogonal support, and attractive-false-border tests precede admission or zoning change. |
| DL-01 | WP-OSW-009 | Lifecycle/deployment discovery and pure drift reconciliation precede any effectful release attempt. |
| DL-02 | WP-OSW-001, WP-OSW-004 | Lossless adapters and scene value bindings make receipt/result mutation a required failure path. |
| DL-03 | WP-OSW-005 | Measurement and complete payload classification precede budgets or integrated public-release candidacy. |

All packages remain proposed. Verification must allocate controlled proof IDs
before execution, and a passing package still cannot label a pitfall solved
without an implemented prevention and a regression test that fails when it is
removed. See the [Implementation Plan](../../docs/vtrace/IMPLEMENTATION_PLAN.md)
and [Work Packages](../../docs/vtrace/WORK_PACKAGES.md).

## Verification containment

The settled Verification plan assigns executable target failures without
claiming that unimplemented checks pass:

| Pitfalls | Verification controls | Required failure evidence |
|---|---|---|
| SI-01–SI-03 | VFY-OSW-002–005, VFY-OSW-014 | Incompatible quantity, residual-as-process, motion-as-delivery, near-closure, and contrary/null sensitivity fixtures fail the affected claim. |
| DN-01, DN-02 | VFY-OSW-002, VFY-OSW-005, VFY-OSW-006, VFY-OSW-012, VFY-OSW-019 | Sign/reference, sampling/support, custody, family integrity, and network/dependency failures remain explicit and local. |
| CA-01, CA-02 | VFY-OSW-005, VFY-OSW-009, VFY-OSW-010, VFY-OSW-015 | Seam/land/pole/support/text disagreement and attractive false borders fail admission or promotion. |
| DL-01 | VFY-OSW-017, VFY-OSW-018 | Drift produces a side-effect-free hold; failed hosted transition retains/restores prior release and metadata. |
| DL-02 | VFY-OSW-002, VFY-OSW-008, VFY-OSW-012 | Mutated result/receipt/family identity invalidates dependent scenes and artifacts. |
| DL-03 | VFY-OSW-011, VFY-OSW-019, VFY-OSW-020 | Undeclared/eager requests, provider dependence, or verifier residue fail without repairing the candidate. |

See the [Verification Plan](../../docs/vtrace/VERIFICATION.md). These controls
leave every pitfall open or mitigated until implementation and regression
evidence make the corresponding failure structurally unavailable.

## Validation containment

The settled Validation plan tests the belief and operational outcome left by
implemented controls, while every scenario remains blocked today:

| Pitfalls | Validation scenarios | Acceptance boundary |
|---|---|---|
| SI-01, SI-02, SI-03 | VAL-SCN-OSW-001, VAL-SCN-OSW-002, VAL-SCN-OSW-008 | Readers and auditors retain quantity/receipt limits; closure, causation, motion-as-delivery, and preferred-story filtering are hard failures. |
| DN-01, DN-02 | VAL-SCN-OSW-002, VAL-SCN-OSW-006, VAL-SCN-OSW-008 | Independent operators recover sign/reference/support/method/custody and retain explained divergence, null, contrary, or unavailable results. |
| CA-01, CA-02 | VAL-SCN-OSW-003, VAL-SCN-OSW-004, VAL-SCN-OSW-005 | Actual access users and independent cartographic/zoning reviewers recover the same map meaning and can reject attractive false geometry. |
| DL-01 | VAL-SCN-OSW-006 | A fresh maintainer identifies every lifecycle hold without private knowledge; hosted transition remains separately blocked. |
| DL-02 | VAL-SCN-OSW-001, VAL-SCN-OSW-002 | Reader and auditor reach the controlling receipt and cannot retain a stale or stronger public value. |
| DL-03 | VAL-SCN-OSW-003, VAL-SCN-OSW-006 | Selected-view access remains usable while network-denied reproduction exposes payload and custody boundaries. |

See the [Validation Plan](../../docs/vtrace/VALIDATION.md). Formative reader
counts are not population claims; participant data remains minimal and
pseudonymous; no scenario pass or pitfall closure is claimed before execution.

## Trace containment

The settled [Trace Matrix](../../docs/vtrace/TRACE.md) connects every pitfall
to preventing requirement rows and required negative evidence. It also prevents
a governance failure common to all ten entries: a settled plan, current partial
test, neighboring success, or role review cannot promote implementation,
verification, validation, pitfall, or release status by inheritance.

Trace correction marks dependent rows stale, preserves superseded evidence,
and creates a new reviewed identity. All ten pitfall statuses remain unchanged;
their target verification remains pending and their validation evidence remains
blocked.

## Final Review containment

The settled [Implementation Entry Review](../../docs/vtrace/REVIEW.md) carries
every pitfall forward into execution. It authorizes only WP-OSW-001 pulse 001-A
after an immutable baseline commit and prohibits science calculation, receipt
rewrites, atlas rendering, external acquisition, validation, and release.

Any collision, ambiguous identity, secret-bearing diagnostic, lossy source
representation, hidden I/O, unrelated mutation, or weakened claim boundary
stops the pulse. Review authorization does not change any pitfall status: target
proof must still be executed, and later pulses require new entry decisions.

## Detailed controls

### SI-01 — quantity conflation

**Failure mode:** a visible warm patch, temperature anomaly, or current arrow is
allowed to inherit the words heat content, storage, transport, convergence, or
delivery without the additional dimensions and terms those quantities require.

**Structural prevention target:** quantitative artifacts carry a shared typed
quantity descriptor covering variable, units, dimensional support, integration,
sign/reference, evidence class, and prohibited stronger interpretations.

**Proof target:** schema and rendering tests reject a quantitative view whose
label or claim exceeds its typed descriptor.

### SI-02 — remainder becomes mechanism

**Failure mode:** an unexplained difference is assigned to atmosphere, vertical
motion, mixing, ice, or assimilation because that story is plausible.

**Structural prevention target:** budget artifacts enumerate measured terms and
an unresolved remainder separately; only an independently sourced term can
reduce or rename the remainder.

**Proof target:** a fixture attempting to relabel the remainder without a term
receipt fails validation and rendering.

### SI-03 — motion becomes delivery

**Failure mode:** current direction, a deterministic track, or one open-gate
flux is taken to prove source-to-destination heat delivery or regional
convergence.

**Structural prevention target:** motion, pathway, gate, and control-volume
objects have incompatible claim ceilings unless the required mass/heat budget
and closure evidence are present.

**Proof target:** object-admission tests reject delivery/convergence claims from
motion-only and single-open-section fixtures.

### DN-01 — hidden sign and reference

**Failure mode:** a transport number changes with outward/inward convention,
temperature reference, or unbalanced mass flux while the public meaning appears
unchanged.

**Structural prevention target:** transport artifacts require declared face
orientation, volume balance, reference temperature, and a reference-change
identity audit.

**Proof target:** synthetic balanced and unbalanced sections exercise sign and
reference changes and reject inconsistent identities.

### DN-02 — sampling geometry changes the quantity

**Failure mode:** center-to-face collocation, standard-depth interpolation,
partial-cell handling, masking, gradient stencil, or unmatched averaging window
is treated as an invisible implementation detail.

**Structural prevention target:** every derived diagnostic binds to one named
sampling/collocation contract and retains sensitivity alternatives where no
native conservative term is available.

**Proof target:** malformed masks, signs, layer thicknesses, coordinates, and
time supports fail; supported alternative methods produce an explicit
sensitivity record.

### CA-01 — cartographic object fabrication

**Failure mode:** land, seam, clipping, or projection behavior gives a feature a
false edge, overlap, split identity, or area comparison.

**Structural prevention target:** atlas features share one ocean mask and seam
identity system; every view declares projection and whether area comparison is
valid.

**Proof target:** mask equivalence, seam continuation, polar support, and
projection-label tests cover every admitted map family.

### CA-02 — schematic authority

**Failure mode:** visual polish makes an invented region hierarchy look like a
published, fixed, impermeable natural boundary.

**Structural prevention target:** boundary class is a required data attribute
and receives redundant line, label, legend, and text-alternative treatment.

**Proof target:** rendering fails when a schematic boundary lacks its class,
provisional label, non-color key, or limitation.

### DL-01 — release-state drift

**Failure mode:** branch, README, preview status, citation, publication
checklist, and hosted site disagree about what is released and supported.

**Structural prevention target:** one versioned release-state source generates
or validates all public status surfaces.

**Proof target:** a deliberate mismatch among branch baseline, README, preview,
citation, and hosted target fails the release gate.

### DL-02 — claim/artifact drift

**Failure mode:** copied headline values or caveats survive after the underlying
receipt, generator, or method changes.

**Structural prevention target:** public quantitative text is generated from or
validated against the committed receipt and its claim ceiling.

**Proof target:** altering a receipt value or boundary statement without
regenerating dependent artifacts fails offline tests.

### DL-03 — custody becomes payload

**Failure mode:** committing every acquired source byte makes cloning and
loading the public atlas expensive, while removing inputs would break
reproducibility.

**Structural prevention target:** define lightweight web derivatives, pinned
receipt/checksum custody, on-demand loading, and an explicit external location
for heavyweight reproducibility inputs where needed.

**Proof target:** a release check measures critical-path bytes, rejects eager
loading of non-selected research payloads, and verifies every externalized
input remains retrievable or reconstructable from its receipt.

## Adding a pitfall

1. State the reusable failure pattern, not the incident-specific symptom.
2. Assign its owning domain and native role.
3. Describe a structural prevention that removes the failure path.
4. Name the regression test or the exact proof gap.
5. Mark it open, mitigated, or solved using the rules above.
6. Link it to the relevant VTRACE constraint, requirement, specification, and
   verification row as those stages settle.

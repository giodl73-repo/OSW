---
skill: roles-check
topic: ocean-object-classification
date: 2026-09-05
roles_used: 8
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Native-role review — Ocean Object Classification v0.1

## Artifact identification

- **Artifact type:** research classification, machine-readable vocabulary, and
  relationship graph
- **Artifacts:** `CLASSIFICATION.md`, `research/ocean-object-classification.csv`,
  `research/ocean-object-relations.csv`, guide/root navigation, source register,
  discovery signal, history entry, and offline validators
- **Domain signals:** physical oceanography, semantic interoperability,
  cartography, public science, accessibility, reproducibility, repository
  stewardship, and planetary transfer
- **Source commit:** `556edacd5c5b9ca0b1829e804ae05384635a730b`
- **Snapshot:** named uncommitted working-tree files as reviewed 2026-09-05
- **Validation:** `python -m pytest analysis -q` — 389 passed, 10 subtests passed

## Role selection

All eight OSW roles apply. The classification is intended to govern later maps,
data bindings, explanations, and planetary comparisons, so limiting review to
data-schema concerns would miss scientific and public-meaning failures.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Separating bodies, structures, processes, events, places, and analyst constructs prevents category errors such as equating a water mass with a current or gate. | P3 | Axis A | Preserve the ontological-type axis. |
| 2 | Identity tests distinguish properties, gradients, velocity, trajectories, fluxes, budgets, anomalies, and terrain. | P3 | Axis B and object registry | Require an identity test for every new term. |
| 3 | Relationship qualifications prevent common coincidence from becoming physical identity or necessity. | P3 | Relationship registry | Never promote `qualified` to universal without a stated experiment. |

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The registry records external vocabulary families, but not yet exact versioned concept identifiers. | P2 | `external_anchor` | Before data binding, add exact CF/NVS/Marine Regions/GEBCO identifiers and vocabulary versions where matches exist. |
| 2 | The web signal grounds the architecture with 15 findings across standards, gazetteers, observations, and phenomenon ontologies. | P3 | Discovery signal | Retain the claim-by-claim evidence ledger. |
| 3 | Relationship rows carry qualification and status but not a claim-level evidence key. | P2 | Relationship registry | Add a source-register or receipt key before promoting a relation to map logic. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Geometry and coverage are independent fields, so a curve-like front cannot silently become an exhaustive province. | P3 | Object registry | Make both fields visible in future legends. |
| 2 | Substrate and phase objects are distinct from fluid structures, supporting different visual grammars for fixed, evolving, and oscillatory objects. | P3 | Type matrix | Use line/fill/texture or motion redundantly, not colour alone. |
| 3 | No geographic map is introduced in this increment, so projection and footprint fidelity are not yet testable. | P3 | Scope | Run a new CHART review when registry classes are rendered. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “What kind of thing?” and “What test identifies it?” provide a memorable explanation of the two-axis model. | P3 | Opening and axes | Preserve this language as the public entry point. |
| 2 | The text explicitly says 72 is editorial coverage rather than nature's exact object count. | P3 | v0.1 registry | Keep the count caveat adjacent to every count. |
| 3 | The coverage table directly answers why fronts, eddies, heatwaves, and plumes should not be padded into a state-like tiling. | P3 | Coverage promise | Carry this distinction into the Atlas filter language. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The central matrix and graph are available as headings, tables, prose, and CSV rather than image-only diagrams. | P3 | Classification document | Preserve the CSV as the data-oriented alternative. |
| 2 | The concept finder asks reader questions rather than requiring prior command of taxonomy terms. | P3 | Guide index | Extend the finder when planned guides land. |
| 3 | Machine codes are paired with plain-language preferred names and explanations. | P3 | Both registries | Ensure future interfaces never expose IDs as the only label. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Offline tests enforce 72 unique objects, 12 represented types, controlled fields, 44 valid relations, and referential integrity. | P3 | `analysis/test_guides.py` | Keep validation in the default suite. |
| 2 | A new uniqueness check exposed duplicate `O1–O5` source IDs from the preceding guide increment. | P2 | Source register | **Fixed:** move guide/classification sources to unique `C1–C10` IDs and retain the regression test. |
| 3 | The full repository suite passes after schema and navigation integration. | P3 | Full suite | Use the same command as the merge gate. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Root README, guide index, project history, source register, signal, schema, graph, and tests expose one coherent research increment. | P3 | Repository routes | Version these files together when the owner requests a commit. |
| 2 | The classification truthfully identifies itself as working v0.1 and not a replacement for controlled vocabularies. | P3 | Status and interoperability boundary | Retain that release boundary. |
| 3 | The source commit predates these dirty-tree artifacts. | P3 | Review metadata | Replace the snapshot note with the containing commit only after an actual commit exists. |

## ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The Earth classification does not silently assign terrestrial water masses or seabed features to gas giants. | P3 | Scope | Require an explicit cross-world mapping layer. |
| 2 | Wave, jet, vortex, boundary, and transport types can support comparison without claiming equal material or forcing. | P3 | Types and Guide 07 route | Compare identity tests and dimensionless regimes, not labels alone. |
| 3 | No new planetary equivalence is asserted in this increment. | P3 | Classification document | Re-run ORBIT when a planetary registry or mapped feature is added. |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 3  |  P3 notes: 21
Resolved P2: 1  |  Residual P2: 2

Verdict: APPROVED-WITH-CONDITIONS
Top finding: the type × identity-test matrix is physically and semantically
stronger than one universal hierarchy.
Cross-role consensus: object type, identity test, geometry, coverage, time,
status, and relation qualification must travel together into any map.
```

The classification is approved for research and guide development. Before any
registry row drives a published observed layer, its exact external concept match
and each operative relationship's evidence key remain required. This is native
OSW review, not external scientific peer review or a release decision.

## Amendments

1. **Completed:** added controlled-field and relation-integrity validation,
   including source-register ID uniqueness.
2. **Before data binding:** replace broad external-anchor families with exact,
   versioned identifiers when a true match exists.
3. **Before map logic:** add claim-level evidence keys to relationships used by
   rendering, inference, or automated explanation.

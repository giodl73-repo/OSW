---
skill: roles-check
topic: guide-08-seafloor-topographic-steering
date: 2026-09-05
roles_used: 8
p1_count: 0
verdict: APPROVED
---

# Native-role review — Guide 08: Seafloor and Topographic Steering

## Artifact identification

- **Type:** public-science guide plus classification-schema increment
- **Artifacts:** Guide 08, guide index, object/relationship registries, project
  history, root navigation, and offline guide contracts
- **Source commit:** `556edacd5c5b9ca0b1829e804ae05384635a730b`
- **Snapshot:** named uncommitted working-tree files on 2026-09-05
- **Validation:** `python -m pytest analysis -q` — 389 passed, 10 subtests passed

All eight roles apply because the chapter teaches physical mechanism, cites
data products, establishes a cartographic grammar, changes public navigation
and classification, and sharpens an Earth–gas-giant boundary condition.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The chapter treats bathymetry as a boundary condition rather than a complete circulation solution. | P3 | “How topography steers” | Preserve this governing qualification. |
| 2 | Terrain, choke-point interpretation, and measurement gate are physically separated. | P3 | “Three meanings” | Carry the distinction into every gateway map. |
| 3 | Connectivity and transport remain separate tests. | P3 | Decisive tests | Require velocity and properties before heat-delivery claims. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | GEBCO/IHO terminology and Thompson et al. support the general definitions and Antarctic mechanism. | P3 | Object cards and examples | Keep governed feature names separate from OSW interpretations. |
| 2 | The OSW numeric geometry examples originally linked figures but not receipts. | P2 | OSW examples | **Fixed:** link the Nordic and Indonesian machine-readable receipts. |
| 3 | The decisive tests require product version, datum, grid, resolution, masks, and uncertainty. | P3 | Decisive tests | Apply the checklist before importing bathymetry. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Relief is shown as a sectional schematic rather than a falsely geographic world map. | P3 | “Relief is nested” | Add projection review only when a mapped layer is built. |
| 2 | The guide separates raster depth cells, landform class, and named feature. | P3 | Relief explanation | Preserve all three as distinct legend concepts. |
| 3 | Fixed terrain and moving circulation receive different language rather than one hard-boundary symbol. | P3 | Throughout | Future maps should encode fixed versus diagnosed geometry redundantly. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “The seafloor is comparatively fixed; circulation is not” is memorable and supportable. | P3 | Opening | Retain as the chapter's repeatable sentence. |
| 2 | “Gate” is unpacked into three meanings that non-specialists commonly conflate. | P3 | “Three meanings” | Reuse this explanation beside Atlas gate controls. |
| 3 | Blocking language is immediately qualified by layer, connection, and intermittent exchange. | P3 | Steering diagram | Do not shorten away those limits. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Both schematics have equivalent prose and tabular explanations. | P3 | Relief and gate sections | Keep prose canonical. |
| 2 | Meaning does not depend on colour or pointer interaction. | P3 | Whole guide | Preserve the text-first version when visual maps follow. |
| 3 | Links name both visual artifacts and receipts. | P3 | OSW examples | Maintain distinct labels for viewing and auditing. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The standard guide test enforces diagram, common-mistake section, index route, and local link resolution. | P3 | Test contract | Keep Guide 08 in the enumerated page set. |
| 2 | Adding `sill` changes the exact registry and relation counts under test. | P3 | Classification registry | The passing count change demonstrates deliberate schema evolution. |
| 3 | The complete offline suite passes after integration. | P3 | Full suite | Retain as the merge gate. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Guide index, registry routes, history, and tests all report eight guides and 73 terms consistently. | P3 | Repository routes | Version the related files together when requested. |
| 2 | The history explains why `sill` became term 73 rather than presenting the count as fixed truth. | P3 | Project history | Preserve the evolutionary record. |
| 3 | The guide is an uncommitted research artifact, not a published Atlas release. | P3 | Review scope | Replace the working-tree snapshot with a commit only after commit. |

## ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The first draft left the planetary implication indirect. | P2 | End of guide | **Fixed:** add a “Planetary boundary” section and direct Guide 07 link. |
| 2 | The new section identifies shallow solid topography as asymmetric rather than forcing a one-to-one counterpart. | P3 | Planetary boundary | Keep the asymmetry explicit. |
| 3 | It does not imply that removing topography makes every remaining Earth and gas-giant mechanism identical. | P3 | Planetary boundary | Preserve the closing non-equivalence sentence. |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues found: 2 (2 resolved)  |  P3 notes: 22
Residual P1: 0  |  Residual P2: 0

Verdict: APPROVED
Top finding: natural landform, dynamic choke point, and measurement gate must
remain distinct objects even where they overlap geographically.
Cross-role consensus: bathymetry constrains circulation but cannot establish
velocity, water-mass identity, or heat transport by itself.
```

This approves Guide 08 for the working guide collection. It does not remove the
exact-vocabulary and per-edge-evidence promotion conditions recorded in the
classification v0.1 review, replace external peer review, or release an Atlas.

## Amendments completed

1. Added both OSW machine-readable geometry receipts.
2. Added the explicit planetary boundary-condition comparison.
3. Promoted eight substrate rows to Guide 08 and added `sill` as a separately
   tested 73rd term with a qualified gate relationship.

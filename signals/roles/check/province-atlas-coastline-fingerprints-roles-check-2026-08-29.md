---
skill: roles-check
topic: province-atlas-coastline-fingerprints
date: 2026-08-29
roles_used: 6
p1_count: 0
verdict: APPROVED
---

# Province Atlas coastline-fingerprint review

Source commits:

- `495ec4b` — real compressed coastline implementation
- `f5f6d35` — breakthrough history and next-stage shape contract

## Artifact identification

- Type: conceptual cartographic amendment, deterministic SVG generation,
  project-history record, and future design contract
- Domain signals: cartographic truth, source provenance, public interpretation,
  accessibility, deterministic generation, licensing, and project history
- Scope: continental context only; province geometry remains the previously
  reviewed non-metric cartogram

## Role selection

| Role | Why selected |
|---|---|
| SOUNDER | Natural Earth version, bytes, source role, and transformation must be exact. |
| CHART | Real coastlines inside a cartogram could create a false impression of geographic province accuracy. |
| BEACON | “Real” and “compressed” must remain paired in the primary explanation. |
| HARBOR | Thin coastline context cannot become required for recovering the map's meaning. |
| KEEL | The generated SVG must reject changed source bytes and remain deterministic. |
| LOGBOOK | The hallmark must be recorded without promoting the private experiment or hiding unresolved shape work. |

CURRENT was excluded because the amendment changes no province identity,
physical mechanism, observed field, dynamic-boundary claim, or heat budget.
ORBIT was excluded because no planetary comparison is present.

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The generator pins Natural Earth land to commit `ca96624a…`, exact raw URL, public-domain role, and SHA-256 `9e0729ee…`. | P3 | source constants and SVG metadata | Update all four identifiers together if coastlines are refreshed. |
| 2 | The source is admitted only as compressed continental context; no Longhurst geographic boundary product enters the artifact. | P3 | metadata and method | Require a separate source/license contract for true province footprints. |
| 3 | README distinguishes the downloaded source geometry from the committed transformed SVG and documents the exact regeneration input. | P3 | reproduction route | Preserve network acquisition as an explicit operation outside the offline gate. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Real coastline irregularity supplies geographic recognition while four narrow seams leave the provinces dominant. | P3 | visual hierarchy | Keep continental seams within the planned 8–12% width budget. |
| 2 | Page copy and SVG description say coastlines are horizontally compressed and province shapes remain schematic. | P3 | map semantics | Never describe this view simply as “geographic.” |
| 3 | Coastlines are linework on low-opacity seam beds, distinct from filled biome provinces and their dark shared borders. | P3 | visual encoding | Retain the lower contrast if more coastline detail is introduced. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Continental fingerprints” accurately conveys recognition without claiming preserved continental width. | P3 | experiment copy | Keep “compressed” in the same paragraph. |
| 2 | HISTORY records why the discovery matters and separately states what the first map cannot mean. | P3 | landmark record | Preserve the identity-versus-geometry sentence as the historical contract. |
| 3 | “Equal voice” and “True footprint” give the next work a memorable contrast while making clear that only the first exists now. | P3 | shape-system plan | Do not advertise the morph before a licensed true-footprint layer exists. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Province codes, fills, borders, directory, and alt text remain unchanged in function; coastline recognition is supplementary. | P3 | equivalent access | Keep continental linework nonessential to province identity. |
| 2 | The SVG description names the transformed coastlines and reiterates schematic province shape and area. | P3 | nonvisual description | Update the description if seam placement or source changes. |
| 3 | Coastline labels use text with a contrast stroke rather than requiring viewers to infer the seam solely from thin linework. | P3 | annotations | Recheck at browser zoom before public promotion. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A source hash mismatch aborts generation before writing transformed artifacts. | P3 | builder gate | Add a small rejection fixture if this generator enters CI. |
| 2 | Repeated generation from the pinned input produced byte-identical SVG and CSV outputs. | P3 | deterministic build | Keep coordinate formatting explicit and stable. |
| 3 | The 39-test offline suite and `git diff --check` pass and assert source, compression, coastline class, landmark, and future license guard. | P3 | regression gate | Add a visual snapshot only when the project adopts a browser test harness. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | `HISTORY.md` records discovery, implementation, approval, coastline amendment, permanent limitation, and next promise by commit. | P3 | project history | Keep conceptual landmarks separate from Atlas release numbering. |
| 2 | The shape plan explicitly says no public promotion is authorized and makes owner visual choice the first acceptance step. | P3 | future status | Record that choice without changing hosted-version claims. |
| 3 | Public-domain coastline context is compatible with the MIT repository, and the noncommercial Marine Regions boundary layer is still not redistributed. | P3 | license boundary | Preserve source-role tests and metadata in all derivative exports. |

## Synthesis

```text
Roles reviewed: 6
P1 blockers: 0  |  P2 issues: 0  |  P3 notes: 18

Verdict: APPROVED
Top finding: Horizontally compressed real coastlines add the irregular visual
definition the cartogram lacked without surrendering the canvas to land.
Cross-role consensus: SOUNDER, CHART, BEACON, and LOGBOOK agree that real
continental context must never be allowed to imply real province geometry.
```

Approval remains scoped to an additive private experiment. It approves the
coastline context and the historical/design record, not a true-footprint
Longhurst map or a public release.

## Amend

1. Keep compressed-coastline wording and Natural Earth provenance inside every
   exported version of this visual.
2. Build varied province puzzle pieces under the explicit non-metric contract
   before attempting a morph or area comparison.
3. Admit true geographic footprints only after the source/license and
   transformation gates in the shape-system plan are satisfied.


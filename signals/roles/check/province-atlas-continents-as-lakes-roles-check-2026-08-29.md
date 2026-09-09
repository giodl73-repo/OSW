---
skill: roles-check
topic: province-atlas-continents-as-lakes
date: 2026-08-29
roles_used: 6
p1_count: 0
verdict: APPROVED
---

# Province Atlas “continents as lakes” review

Source commit: `2327cec` (`Cut continents from monochrome Province Atlas`)

## Artifact identification

- Type: monochrome conceptual cartogram, generated SVG mask geometry, and
  projection-laboratory presentation amendment
- Domain signals: cartographic semantics, coastline provenance, non-color
  communication, accessible equivalence, deterministic generation, licensing,
  and private-preview status
- Scope: Experiment 03B; no observed field, true Longhurst footprint, area
  comparison, or public promotion

## Role selection

| Role | Why selected |
|---|---|
| SOUNDER | Real coastline geometry and schematic province geometry coexist in one artifact. |
| CHART | Continental holes may imply more geographic fidelity than the internal pieces possess. |
| BEACON | The state-map and lake analogies must remain memorable without becoming literal. |
| HARBOR | Removing biome color changes how categories and province identity are recovered. |
| KEEL | Mask construction, feature count, source pin, and dual outputs require regression coverage. |
| LOGBOOK | The new primary study must preserve the prior plate and remain a private experiment. |

CURRENT and ORBIT were excluded because this visual changes neither physical
mechanism nor planetary comparison.

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Continental cutouts derive from the same checksum-pinned public-domain Natural Earth source as the reviewed coastline fingerprints. | P3 | SVG metadata and generator | Keep source version, URL, hash, and role inseparable. |
| 2 | Metadata states that no geographic Longhurst boundary dataset is reproduced and the 56 province geometry remains original. | P3 | source firewall | Create a new contract before importing true footprints. |
| 3 | Explicit continental clipping windows resolve Natural Earth's combined Afro-Eurasia polygon before horizontal compression. | P3 | transformation | Document any later change to continental windows as a visual, not geodetic, revision. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Continents are actual negative-space masks: neighboring province fills terminate visually at irregular coastline holes instead of beside decorative seam graphics. | P3 | core visual | Preserve the mask relationship in all derived versions. |
| 2 | One neutral fill and dark internal borders make the artifact read much more like a state reference map while codes keep the 56 pieces distinct. | P3 | state-map grammar | Introduce varied shared boundaries next without reintroducing thematic color. |
| 3 | The map itself states that coastlines are compressed and province shape, size, distance, and most adjacency remain schematic. | P3 | method firewall | Keep this text inside the exported image, not only on the page. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Continents as lakes” correctly explains the inversion: ocean is the continuous mapped territory and land becomes negative space. | P3 | headline | Retain “as” to signal analogy. |
| 2 | “The ocean, as 56 provinces” is clearer than calling scientific provinces political states. | P3 | title | Use state-map only for the visual grammar, not the ontology. |
| 3 | The prior four-biome plate remains linked as a comparison rather than being erased by the new preference. | P3 | experiment history | Preserve both studies through owner selection. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Province identity no longer depends on biome color; all 56 codes are visible in a single high-contrast neutral treatment. | P3 | map encoding | Keep full names available in the linked 56-row directory. |
| 2 | SVG title and description explain continent holes, compression, and schematic province geometry without requiring visual inference. | P3 | nonvisual equivalent | Synchronize wording if the hole layout changes. |
| 3 | Hover/focus changes lightness and border weight rather than category hue, and the standalone province groups remain keyboard-focusable. | P3 | interaction | Add keyboard/zoom browser automation before public promotion. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | One generator emits the preserved color study, new monochrome lakes study, and 56-row directory from the same province registry. | P3 | build architecture | Keep outputs additive and atomically regenerated. |
| 2 | The lakes SVG contains exactly 56 province groups and a user-space continent mask; the offline suite locks both requirements. | P3 | tests | Add topology assertions when shared puzzle boundaries replace the grid. |
| 3 | Regeneration is byte-deterministic, the 39-test suite passes, browser JavaScript syntax checks pass, and `git diff --check` is clean. | P3 | validation gate | Retain the pinned-source build as an explicit non-default operation. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The monochrome lakes study becomes the primary Province Atlas link while the reviewed color study remains available and unchanged. | P3 | README and projection lab | Record later owner selection without deleting either artifact. |
| 2 | The artifact uses MIT-compatible original cartogram work plus public-domain land geometry; no noncommercial boundary product enters the repository. | P3 | license boundary | Preserve the metadata and source-role test. |
| 3 | The SVG calls itself Experiment 03B and a state-map study, not Atlas 11 or a public release. | P3 | version truth | Keep Atlas numbering reserved for explicit promotion decisions. |

## Synthesis

```text
Roles reviewed: 6
P1 blockers: 0  |  P2 issues: 0  |  P3 notes: 18

Verdict: APPROVED
Top finding: Continents now function as true negative-space holes in a unified
ocean field, which produces the requested state-map reading without pretending
the internal province polygons are geographic.
Cross-role consensus: CHART, BEACON, HARBOR, and LOGBOOK agree that the
monochrome lakes view is the strongest primary concept so far, while varied
shared province boundaries remain the next visual task.
```

Approval is scoped to a private conceptual study. It does not validate coast
contact, province area, internal topology, or geographic Longhurst footprints.

## Amend

1. Replace repeated beveled grid cells with unique, shared puzzle boundaries
   under the existing non-metric contract.
2. Keep the 56 codes and monochrome treatment stable while testing that new
   grammar so visual changes remain attributable to shape.
3. Do not introduce a true-footprint or morph claim until a compatible
   geographic province source and transformation receipt exist.


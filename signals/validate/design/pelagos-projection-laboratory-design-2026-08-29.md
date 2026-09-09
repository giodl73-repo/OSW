---
skill: validate-design
topic: pelagos-projection-laboratory
date: 2026-08-29
reviewer_count: 10
p1_count: 0
p2_count: 0
p3_count: 40
domain_roles_active: [Ocean Cartographer and Geodesist, Physical Oceanographer, Geospatial Data Steward, Accessibility Specialist]
---

# PELAGOS projection laboratory design review

Source commits: `92345ec` (`Add PELAGOS projection laboratory`) and
`dbe8165` (`Project defined heatmass areas in bakeoff`)

## BLOCK 0 — CONTENT SIGNAL CATALOGUE

| Signal phrase | Domain category |
|---|---|
| “Equal-area, ocean-led, and deliberately weakest over the Sahara” | cartography / geodesy |
| “reservoirs, anomalies, currents, and gates” | physical oceanography |
| “same checksum-pinned Natural Earth 1:110m coastlines” | geospatial data provenance |
| responsive comparison page, linked SVGs, and alternative text | accessibility |

## BLOCK 1 — EXPERT ROSTER

Stock table:

| Reviewer | Role |
|---|---|
| Architect | Stock |
| Code-Quality | Stock |
| Documentation | Stock |
| Testing | Stock |
| Process | Stock |
| Implementation | Stock |

Domain expert table:

| Signal detected | Expert added | Reason |
|---|---|---|
| “Equal-area, ocean-led, and deliberately weakest over the Sahara” | Ocean Cartographer and Geodesist | Projection properties, singularities, interruption, and visual distortion require specialist evaluation. |
| “reservoirs, anomalies, currents, and gates” | Physical Oceanographer | The selected geography must preserve the relationships the ocean mechanism claims depend upon. |
| “same checksum-pinned Natural Earth 1:110m coastlines” | Geospatial Data Steward | Reproducibility depends on source identity, transformation parity, and generated-artifact provenance. |
| responsive comparison page, linked SVGs, and alternative text | Accessibility Specialist | The projection tradeoffs must remain available without color, pointer use, or a wide viewport. |

BLOCK 1 domain count = 4

## BLOCK 1.5 — ROSTER COMMITMENT TABLE

| Reviewer | Role | Source |
|---|---|---|
| Ocean Cartographer and Geodesist | Domain expert | Domain |
| Physical Oceanographer | Domain expert | Domain |
| Geospatial Data Steward | Domain expert | Domain |
| Accessibility Specialist | Domain expert | Domain |
| Architect | Stock discipline | Stock |
| Code-Quality | Stock discipline | Stock |
| Documentation | Stock discipline | Stock |
| Testing | Stock discipline | Stock |
| Process | Stock discipline | Stock |
| Implementation | Stock discipline | Stock |

Conformance gate: 4 Domain rows equal BLOCK 1 domain count, and all Domain
reviewer names exactly match their BLOCK 1 expert names.

## BLOCK 2 — PER-REVIEWER FINDINGS

### Ocean Cartographer and Geodesist

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | PELAGOS correctly uses Lambert azimuthal equal-area, so relative surface area is preserved even though shapes distort away from the center. | P3 | method firewall | Keep “equal-area” separate from any claim of shape fidelity. |
| 2 | The center at 20°S, 165°W places the antipode at 20°N, 15°E; declaring the Sahara edge makes the unavoidable singularity inspectable. | P3 | PELAGOS card | Retain coordinates in every technical export. |
| 3 | The Spilhaus panel now uses a square clip matching the projection instead of implying a wide rectangular domain. | P3 | generated Spilhaus SVG | Lock the frame type in a generator test if layouts multiply. |
| 4 | Oceanic Goode provides a valid equal-area control whose visible lobe cuts expose the continuity tradeoff. | P3 | bakeoff | Do not describe Goode as inferior outside this ocean-pathway task. |

### Physical Oceanographer

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | The same warm pools, Blob, El Niño tongue, currents, buried Arctic inflow, gates, and ACC are projected in every candidate. | P3 | generator | Keep geographic feature inputs shared rather than tuning each panel. |
| 2 | PELAGOS renders the ACC as a closed ring around Antarctica, a useful topology test without claiming measured transport. | P3 | PELAGOS SVG | Preserve the “schematic” evidence label when reusing the ring. |
| 3 | Drake Passage and the Indonesian Throughflow are explicitly marked, allowing viewers to test whether constrictions survive projection. | P3 | shared overlay | Add additional gates only under a documented selection rule. |
| 4 | The Arctic inflow remains a buried schematic pathway and is not conflated with surface temperature or heat delivery. | P3 | shared overlay and method | Keep vertical-layer meaning in future interactive labels. |

### Geospatial Data Steward

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | Natural Earth input is locked to commit `ca96624a…` and SHA-256 `9e0729ee…`; a mismatch aborts generation. | P3 | builder constants and SVG metadata | Preserve the checksum gate. |
| 2 | All three SVGs are deterministic outputs of one Python command and record source provenance in metadata. | P3 | build pipeline | Never hand-edit an individual projection artifact. |
| 3 | The environment pins pyproj 3.7.2 and documents why the named Spilhaus operator is reconstructed from Adams Square II. | P3 | requirements and analysis README | Record the bundled PROJ version if byte identity becomes a release requirement. |
| 4 | Source Register entries distinguish the admitted projection property from the boundary on its interpretation. | P3 | P1–P3 | Keep projection sources separate from physical-ocean evidence. |

### Accessibility Specialist

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | Every embedded map has projection-specific alternative text, and each SVG also has a title and description. | P3 | candidate cards and SVG roots | Update both text layers together when feature geometry changes. |
| 2 | Projection properties and failures are stated in prose and a semantic table rather than encoded only by shape or color. | P3 | verdicts and scorecard | Preserve the redundant text route. |
| 3 | Candidate links have visible focus, the page reflows to one column, and the scorecard can scroll horizontally. | P3 | projection CSS | Add automated keyboard and 400% zoom checks when a browser harness is adopted. |
| 4 | Legend categories use shape, dash, and labels in addition to color. | P3 | generated SVG legends | Maintain non-color distinctions if the palette changes. |

### Architect

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | Projection generation, presentation, source registration, and atlas navigation are cleanly separated. | P3 | repository structure | Keep the projection lab independent from observed-layer rendering. |
| 2 | One candidate model drives three outputs, preventing geometry drift between comparison panels. | P3 | `Candidate` and shared renderer | Introduce a schema if candidates become data-defined. |
| 3 | PELAGOS remains a laboratory hypothesis and is not wired into the default atlas projection. | P3 | page status and atlas link | Require explicit owner and role approval before promotion. |
| 4 | The reusable projector interface permits later quantitative distortion diagnostics without replacing the renderer. | P3 | builder | Add diagnostics as generated evidence rather than prose estimates. |

### Code-Quality

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | Projection constants, source identity, layout dimensions, and candidate metadata are named rather than scattered magic values. | P3 | builder top level | Move schematic feature definitions to typed records if they expand. |
| 2 | Projection failures and non-finite coordinates are handled during global sampling and line segmentation. | P3 | `raw_bounds` and `projected_segments` | Add explicit failure counts if higher-resolution geometry is introduced. |
| 3 | Geographic lines are densified before projection, avoiding straight endpoint chords across curved projections. | P3 | `densify` | Document the two-degree rendering tolerance beside future resolution changes. |
| 4 | The Spilhaus construction cites its published constants and isolates the oblique rotation from the Adams operator. | P3 | `spilhaus_projector` | Add reference coordinate fixtures before altering the formula. |

### Documentation

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | The hero defines the reversed priority—preserve ocean relationships instead of continents—before naming a winner. | P3 | page hero | Keep the problem statement ahead of PELAGOS branding. |
| 2 | Each candidate pairs “what it proves” with “where it fails,” preventing promotional comparison. | P3 | candidate verdicts | Preserve this paired structure. |
| 3 | The method clearly says PELAGOS is a new aspect and cut policy, not a new mathematical equation. | P3 | method firewall | Repeat this in any paper abstract or social caption. |
| 4 | README, analysis instructions, source register, and atlas entry point all expose the laboratory. | P3 | repository routes | Add a release note only if the experiment is promoted. |

### Testing

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | The 65-test suite locks all three artifacts, projection operators, source hash, method claim, and shared feature classes. | P3 | `test_atlas.py` | Add numeric reference points for each projection next. |
| 2 | Python compilation, browser JavaScript syntax, relative-link checks, and diff checks pass. | P3 | local validation | Add HTML validation when a stable offline validator is accepted. |
| 3 | Desktop and narrow Edge renders were inspected; the narrow pass prompted explicit shrink and overflow fixes. | P3 | browser review | Replace manual viewport inspection with captured regression frames later. |
| 4 | Regeneration rejects a coastline response whose bytes do not match the pinned SHA-256. | P3 | builder main | Add a local fixture test for the rejection path. |

### Process

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | The bakeoff compares candidates against four declared criteria before selecting a leading hypothesis. | P3 | “The test” | Change the leader only by revisiting these criteria. |
| 2 | PELAGOS is labeled private and not adopted, preventing experimentation from masquerading as release state. | P3 | status and footer | Keep promotion as a separate decision. |
| 3 | Two review-discovered defects—Spilhaus framing and missing Arctic/gate vocabulary—were amended before this sign-off. | P3 | source commit | Preserve review-to-amend traceability. |
| 4 | No remote was changed and the public Atlas 07 state remains untouched. | P3 | repository state | Run publication governance separately before pushing. |

### Implementation

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | The renderer produces compact standalone SVGs that work as linked full-size artifacts and responsive page images. | P3 | generated outputs | Retain SVG as the canonical prototype format. |
| 2 | The named Spilhaus operator is not required; compatible installed Adams Square II plus explicit rotation makes the build work on PROJ 9.5. | P3 | Spilhaus implementation | Prefer the native operator only after parity fixtures agree. |
| 3 | PELAGOS and Goode use pyproj operators with explicit spherical parameters, keeping the bakeoff internally consistent. | P3 | candidate definitions | Do not mix ellipsoidal and spherical candidates silently. |
| 4 | Atlas navigation reaches the laboratory without making it a top-level evidence mode. | P3 | atlas conceptual actions | Promote to a map mode only after interaction and distortion requirements are specified. |

## BLOCK 3 — SYNTHESIS

Overall verdict: APPROVED

P1 blockers (must resolve before implementation):
  (None — implementation is complete.)

P2 conditions (must resolve before sign-off):
  (None — the square Spilhaus frame, complete shared feature grammar, and
  narrow-layout overflow were corrected before this review was recorded.)

Cross-reviewer consensus:
  The reviewers agree that PELAGOS is the strongest current OCEANLINES
  hypothesis because it combines equal-area comparison with an ocean-led
  interior while exposing its Sahara singular edge. They also agree that it
  must remain an experiment until numeric distortion diagnostics and external
  scientific/cartographic review accompany any default-atlas promotion.

Strongest signal:
  PELAGOS succeeds by moving the projection failure rather than pretending to
  eliminate it: the prototype makes that choice visible, reproducible, and
  scientifically subordinate to the unchanged schematic overlay.

## AMEND

1. Add numeric reference-coordinate and areal-distortion fixtures to
   `analysis/test_atlas.py` before altering projection centers or formulae, so
   a visually plausible mathematical regression cannot pass.
2. Add optional distortion diagnostics to the projection cards—such as
   Tissot indicatrices or local scale summaries—before public promotion, so
   “equal-area” is not mistaken for low distortion everywhere.
3. Specify an interactive PELAGOS contract before using it in the primary
   Atlas, including hit testing, labels, antimeridian behavior, keyboard
   access, and equivalence with the equirectangular observational products.

## Owner-feedback amendment — defined areas

The initial source commit projected heatmass centerlines as wide orange
strokes. Owner review correctly identified that those marks tested route
continuity but did not preserve the atlas's defined-area grammar. Follow-up
commit `dbe8165` replaces them with three shared irregular geographic polygons
and three inset shelf contours before projection.

- The same polygon coordinates are used in all candidates, so Spilhaus now
  visibly demonstrates areal distortion while Goode and PELAGOS preserve
  relative area.
- Transient anomalies and pathways retain their distinct round and linear
  grammar.
- Documentation states that the polygon edges are schematic rather than
  observed thresholds.
- A regression test requires at least three heatmass polygons and three shelf
  contours in every artifact and rejects the former 45-pixel stroke encoding.
- All 65 tests, Python compilation, JavaScript syntax, and diff checks pass;
  all three corrected SVGs were inspected in Edge.

Focused verdict: **APPROVED**. The amendment resolves a visual-semantic defect
without changing projection mathematics, evidence class, or release status.

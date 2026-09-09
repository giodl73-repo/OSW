---
skill: validate-design
topic: heatplates-shape-atlas
date: 2026-08-29
reviewer_count: 10
p1_count: 0
p2_count: 0
p3_count: 40
domain_roles_active: [Ocean Cartographer and Geodesist, Physical Oceanographer, Geospatial Data Steward, Accessibility Specialist]
---

# HEATPLATES shape-atlas design review

Source commit: `e91e67a` (`Add Equal Earth and HEATPLATES views`)

## BLOCK 0 — CONTENT SIGNAL CATALOGUE

| Signal phrase | Domain category |
|---|---|
| “local Lambert equal-area” and “panel-specific zoom” | cartography / geodesy |
| six named reservoirs, anomalies, and water masses | physical oceanography |
| checksum-pinned Natural Earth coastlines and generated SVG | geospatial data provenance |
| responsive figure, prose warning, and alternative text | accessibility |

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
| local equal-area panels with different centers and scales | Ocean Cartographer and Geodesist | The design must distinguish per-panel area fidelity from cross-panel size comparability. |
| schematic ocean heat features and nearby pathways | Physical Oceanographer | The panels must not turn conceptual geography into observed thresholds or transport claims. |
| shared coast source and deterministic projection pipeline | Geospatial Data Steward | Inputs, transformations, and output provenance must remain reproducible. |
| a dense six-panel visual embedded in a responsive page | Accessibility Specialist | Meaning must survive color loss, zoom, narrow screens, and non-visual reading. |

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

Conformance gate: 4 Domain rows equal BLOCK 1 domain count, and all Domain reviewer names exactly match their BLOCK 1 expert names.

## BLOCK 2 — PER-REVIEWER FINDINGS

### Ocean Cartographer and Geodesist

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | Each plate uses a locally centered Lambert azimuthal equal-area projection, giving its selected feature a flat, low-clutter setting. | P3 | generator | Keep the projection name in every panel footer. |
| 2 | Panel-specific bounds deliberately enlarge small features, so apparent footprint size cannot be compared across cards. | P3 | warning band | Preserve the explicit no-area-comparison warning in figure and prose. |
| 3 | Equal Earth supplies the requested continuous flat-world control and preserves relative global area. | P3 | candidate 03 | Retain it as a benchmark rather than declaring it the ocean-first winner. |
| 4 | Local panels avoid globe-edge and lobe-cut distractions while keeping nearby coastlines as orientation cues. | P3 | HEATPLATES | Add common-scale small multiples only when observed boundaries support them. |

### Physical Oceanographer

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | Reservoirs, seasonal reservoirs, transient anomalies, equatorial anomalies, buried heatmass, and annular heatmass remain visibly distinct. | P3 | panel subtitles and marks | Preserve these evidence-class labels as the set expands. |
| 2 | The Northeast Pacific Blob now has an irregular geographic silhouette rather than a generic circle. | P3 | panel 03 | Replace schematic geometry only with a documented observational criterion. |
| 3 | Atlantic Water and Circumpolar Deep Water are framed as heatmasses, not direct measurements of heat content or transport. | P3 | figure footer | Keep the “not heat content / not transport” firewall. |
| 4 | Coast context explains ocean setting without implying land creates every boundary. | P3 | all panels | Add mechanisms and gates in a separate explanatory layer, not inside the shape directory. |

### Geospatial Data Steward

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | HEATPLATES and all four global candidates are generated from one script and shared feature definitions. | P3 | build pipeline | Do not hand-edit generated SVGs. |
| 2 | Natural Earth identity remains checksum-pinned and is recorded in generated global artifacts. | P3 | source gate | Add the same machine-readable source metadata to HEATPLATES if downstream reuse grows. |
| 3 | Equal Earth is registered separately from LAEA and the experimental PELAGOS aspect. | P3 | source register P4 | Keep cartographic sources separate from physical-ocean evidence. |
| 4 | Dateline-crossing Indo-Pacific geometry is represented by two clipped paths without changing its conceptual identity. | P3 | panel 01 | Preserve a stable feature identifier if panels become interactive. |

### Accessibility Specialist

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | The six panel names and evidence classes are printed, not encoded only by hue. | P3 | HEATPLATES SVG | Retain redundant textual labels. |
| 2 | The embedded figure has descriptive alternative text naming all six subjects. | P3 | projection page | Keep alt text synchronized with panel additions. |
| 3 | The warning about unequal zoom appears in high-contrast text above the panels and again in page prose. | P3 | warning band and rule | Never rely on the small panel footers alone. |
| 4 | The page collapses to one column on narrow screens and the full SVG remains available as a direct link. | P3 | responsive CSS | Add automated 400% zoom and keyboard checks when browser automation is adopted. |

### Architect

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | HEATPLATES is additive: the previous Spilhaus, Goode, and PELAGOS experiments remain intact. | P3 | projection laboratory | Keep local and global experiments side by side. |
| 2 | Global comparison and local shape inspection answer different questions and are separated into two labeled experiments. | P3 | information architecture | Do not merge their score criteria. |
| 3 | Shared geographic inputs prevent per-projection editorial drift. | P3 | generator constants | Move features to a data schema when external contributors begin editing them. |
| 4 | The observational atlas remains independent from this conceptual projection laboratory. | P3 | repository routes | Require a new contract before adding HEATPLATES to observed modes. |

### Code-Quality

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | Candidate projection metadata stays data-driven and Equal Earth needs no renderer fork. | P3 | `Candidate` list | Preserve declarative candidates. |
| 2 | `screen_transform` accepts an explicit map box, enabling local panels without duplicating coordinate logic. | P3 | transform helpers | Add type records if layout parameters proliferate. |
| 3 | `local_bounds` samples projection windows consistently and avoids hidden hard-coded screen coordinates. | P3 | bounds helper | Add invalid-coordinate fixtures before supporting polar edge cases. |
| 4 | `geographic_blob` produces deterministic irregularity instead of a decorative random shape. | P3 | feature geometry | Keep deterministic output for reviewable diffs. |

### Documentation

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | “One ocean map cannot make every heatmass legible” states the design problem before the solution. | P3 | experiment 02 heading | Retain the problem-led framing. |
| 2 | The page explicitly says to compare shape and context, not footprint area. | P3 | HEATPLATES copy | Repeat this sentence in any shared caption. |
| 3 | README and analysis instructions now expose Equal Earth and HEATPLATES without displacing prior routes. | P3 | repository docs | Keep one canonical projection-lab entry point. |
| 4 | The method still distinguishes schematic boundaries from observed thresholds. | P3 | method and footer | Require sources and definitions before presenting measured boundaries. |

### Testing

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | The 66-test suite requires Equal Earth, HEATPLATES, all six names, the warning, and relevant projection operators. | P3 | `test_atlas.py` | Add numeric projection fixtures before changing centers. |
| 2 | The test accepts multiple paths for a single dateline-crossing panel while requiring at least six regions. | P3 | HEATPLATES regression | Add explicit panel-group IDs if SVG structure becomes an API. |
| 3 | Python compilation, JavaScript syntax, and whitespace checks pass. | P3 | local validation | Add an offline HTML validator when stable. |
| 4 | Edge inspection at 1200×900 confirms legible labels, coast context, distinct marks, and no clipping. | P3 | visual review | Capture narrow regression frames in a future browser harness. |

### Process

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | The owner requested additive exploration, and no previous projection was removed. | P3 | scope | Preserve additive experimentation until a separate pruning decision. |
| 2 | The circular Blob was identified during visual inspection and corrected before sign-off. | P3 | review loop | Continue inspecting generated outputs, not only source and tests. |
| 3 | Scientific caveats were implemented as visible interface content rather than hidden review notes. | P3 | warning and footer | Keep caveats adjacent to the claim they limit. |
| 4 | Work remains local on the private-preview branch and no remote was changed. | P3 | release state | Run publication governance separately before pushing. |

### Implementation

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | The 1200×900 standalone SVG is useful both inside the page and as a directly opened research graphic. | P3 | artifact | Retain SVG as the canonical prototype. |
| 2 | Six local projections share a consistent card grammar while allowing region-specific centers and extents. | P3 | renderer | Externalize panel configuration if the set expands materially. |
| 3 | The Circumpolar panel uses an annular mark, the equatorial feature an elongated polygon, and the Blob an irregular footprint. | P3 | visual grammar | Preserve geometry as an information channel. |
| 4 | Equal Earth integrates into the existing two-column candidate grid and mobile collapse without special layout code. | P3 | projection page | Recheck ordering and labels whenever another global candidate is added. |

## BLOCK 3 — SYNTHESIS

Overall verdict: APPROVED

P1 blockers (must resolve before implementation):
  (None — implementation is complete.)

P2 conditions (must resolve before sign-off):
  (None — the initial circular Blob was made irregular, and unequal-zoom interpretation is now blocked by repeated warnings.)

Cross-reviewer consensus:
  HEATPLATES succeeds as a shape directory because it explicitly gives up the
  pretense of one continuous world. Reviewers agree that its local equal-area
  panels improve feature silhouette and coastal context, provided viewers are
  never invited to compare apparent area across differently zoomed panels.

Strongest signal:
  The new view answers a different question from PELAGOS: not “what world map
  best preserves ocean relationships?” but “what does each named ocean feature
  look like when it is allowed to occupy the frame?”

## AMEND

1. Add common-scale companion panels only after feature boundaries are tied to
   reproducible observed criteria; until then, shape/context is the honest use.
2. Add stable feature IDs and machine-readable metadata before making the SVG
   interactive or exposing its regions as a downstream interface.
3. Add automated narrow-screen, keyboard, and 400% zoom captures when a browser
   regression harness is introduced.


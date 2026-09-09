---
topic: osw-ocean-states-aspect
artifact: figures/osw-state-projection-mollweide-oceanic.svg
method: validate-design + SCENE ASPECT v3.0
date: 2026-08-29
depth: standard
status: needs-work
---

# OSW Ocean States — ASPECT design review

## BLOCK 0 — Content signal catalogue

| Signal | What the work currently says | Design consequence |
|---|---|---|
| Primary claim | The ocean can be read as a complete, state-like geography rather than negative space around continents. | Ocean regions and states must dominate the composition. |
| Hierarchy | 11 realms → 22 regions → 56 state identities. | Three boundary levels need a visible, learnable grammar. |
| Geometry | Original geographic nearest-seed cells, clipped by real Natural Earth coastlines and transformed with an interrupted equal-area Mollweide. | The map is schematic and geographic at once; both models must be declared. |
| Continuity | Each of the 22 memberships is connected in the builder's unmasked geographic seed topology. | “Contiguous” must be qualified because land masks and projection seams can split the visible mark. |
| Polar structure | AAP, NPP, and ANP are difficult to read in the interrupted world projection. | Paired LAEA polar views are analytically necessary, not decoration. |
| Color | Twenty-two nominal region identities use twenty-two fills. | Color aids grouping but cannot be the only identifier; codes and borders must survive grayscale/color-vision loss. |
| Audience | Curious public first; ocean and visualization researchers second. | The map must work at a glance and remain auditable under study. |
| Reading context | Standalone browser figure, often scaled down in a page; downloadable SVG for close study. | Page-scale labels and the standalone artifact both need intentional layouts. |
| Evidence boundary | Classic 56-province vocabulary; not published Longhurst geometry and not measurable province areas. | Provenance and limitation text must be prominent and specific. |
| Current visual result | Strong central “ocean as countries” gestalt; undersized polar views and legend; overlapping state/region codes. | Preserve the breakthrough, rebuild the explanatory frame. |

## BLOCK 1 — Expert roster

Fixed reviewers: Architect, Code Quality, Documentation, Testing, Process, and Implementation. Domain reviewers selected from the content signals: Ocean Cartographer (projection/topology), Visual Perception & Accessibility Specialist (22-category system), and Scientific Classification & Data Integrity Reviewer (provisional taxonomy and evidence limits).

## BLOCK 1.5 — Roster commitment

Nine reviewers are committed. The three domain reviewers are necessary because the artifact's main risks are not generic UI risks: they arise from interrupted projection seams, dense categorical encoding, and the distinction between a published province vocabulary and OSW-authored boundaries/groupings.

## BLOCK 2 — Reviewer findings

### Architect

1. **P1 — The visual system lacks a single declared contract.** Encode `realm`, `region`, and `state` in one versioned registry used by the builders, legend, documentation, and tests.
2. **P2 — The main plate and polar insets behave like separate products.** Give both the same fills, line hierarchy, label grammar, and explicit projection metadata.
3. **P2 — The SVG's frame is optimized around a 900 px legacy canvas.** Establish a larger master canvas, then scale down responsively in HTML.
4. **P2 — “Hairlines off” is a parallel export rather than a semantic mode.** Keep the export, but ensure its title, description, and internal marks state the mode independently.

### Code Quality

1. **P1 — Region tuples are positional and under-specified.** Replace or serialize them into named fields including parent realm, members, anchor, color, and status.
2. **P2 — Layout coordinates are scattered through `render_state_projection`.** Introduce named layout constants for canvas, map, inset, legend, and footer geometry.
3. **P2 — Polar projection parameters are implicit.** Name cutoff and LAEA parameters once and reuse them in rendering and metadata.
4. **P3 — Repeated literal style values obscure the hierarchy.** Centralize line widths/colors or at least name the intended levels adjacent to the renderer.

### Documentation

1. **P1 — “22 contiguous regions” overstates what has been verified.** Use “22 contiguous schematic regions” and explain that contiguity is defined in the unmasked seed topology.
2. **P2 — The work does not distinguish inherited vocabulary from OSW invention soon enough.** State that the 56 identities are classic references while the 11/22 organization and geometry are provisional OSW constructs.
3. **P2 — The polar views omit their latitude cutoffs.** Put projection and extent in the SVG description/metadata and the projection page.
4. **P2 — The hierarchy key is prose only.** Show actual heavy, medium, and hairline samples with their meanings.

### Testing

1. **P1 — No machine-readable 22-region contract is tested.** Assert 22 records, 56 unique memberships, valid anchors, colors, and parent realms.
2. **P2 — Current tests count strings but do not verify disclosure completeness.** Test the provisional status, topology qualifier, projection definitions, and polar cutoffs.
3. **P2 — Color is tested only indirectly.** Assert unique region colors and require text codes for every region.
4. **P3 — Layout regressions can pass token tests.** Add structural assertions for enlarged canvas, inset size, legend type size, and hierarchy key.

### Process

1. **P2 — Seminal design decisions are in history but not versioned as a taxonomy release.** Give the region system a version and status.
2. **P2 — Generated SVGs and their source can drift.** Keep regeneration and validation in the same command/test handoff.
3. **P2 — The review signal should point to resolved changes.** Close each P1/P2 through code, documentation, or a declared deferral.
4. **P3 — Temporary browser captures should not become repository artifacts.** Keep review screenshots out of the tracked design surface.

### Implementation

1. **P1 — The legend is below readable size in the primary browser context.** Move to a larger canvas and use at least 10–11 px legend text in the SVG coordinate system.
2. **P2 — Polar circles are too small to justify their prominence.** Enlarge them enough to compare internal state structure and move labels outside the dense marks.
3. **P2 — Region and state codes collide.** Increase the scale, reduce state-label opacity/weight, and give region codes stronger casing and separation.
4. **P2 — The bottom caveat is visually recessive.** Add a compact `SCHEMATIC · PROVISIONAL` status badge near the title and retain the full qualification below.

### Ocean Cartographer

1. **P1 — Visible contiguity and topological contiguity are not the same.** Declare that seams and land masks can divide a region's rendered footprint.
2. **P2 — The interrupted equal-area property is named but the six-lobe cost is not mapped.** The tradeoff caption should explicitly say that lobe cuts break some ocean neighborhoods.
3. **P2 — Polar insets need projection identities.** Label them `LAEA 48°N–90°N` and `LAEA 45°S–90°S`.
4. **P2 — Coastlines are the sole geographic anchor and should remain visually subordinate.** Use near-white land with extremely quiet hatch/stroke; do not add conventional political geography.

### Visual Perception & Accessibility Specialist

1. **P1 — Twenty-two hues are not reliably nameable or distinguishable.** Pair every fill with a short code, boundary, and legend position; never ask color to carry identity alone.
2. **P2 — The current 4-column legend is dense and tiny.** Use a roomier grid with stronger code/name contrast and consistent count alignment.
3. **P2 — Dark field plus pale land works, but thin gray labels lose contrast at page scale.** Increase text size and reserve the lightest values for labels/casing.
4. **P2 — A written border key requires unnecessary inference.** Demonstrate the three stroke weights as marks, which also makes the no-hairline mode self-evident.

### Scientific Classification & Data Integrity Reviewer

1. **P1 — The map risks laundering a design taxonomy into a scientific taxonomy.** Mark the 11 realms and 22 regions as provisional OSW organizational constructs.
2. **P1 — “Classic 56 states” can be mistaken for exact Longhurst polygons.** Say “classic 56 province identities” and “approximate nearest-seed cells.”
3. **P2 — Counts are present but membership is not readily auditable.** Publish the complete region registry as CSV alongside the 56-province directory.
4. **P2 — The map forbids area inference only in small footer text.** Repeat this limitation in accessible SVG description and page copy.

## BLOCK 3 — ASPECT synthesis

| Dimension | Current | Target | Synthesis |
|---|---:|---:|---|
| Aim /15 | 13 | 15 | The ocean-first purpose is excellent; the explanatory furniture must stop competing with it. |
| School /20 | 16 | 19 | Declare the Type C synthesis: thematic cartography preserves real coast anchors and area; schematic cartography privileges a designed state topology. |
| Precision /15 | 10 | 14 | Larger polar views, controlled label collisions, a real line key, and a disciplined legend will make every mark earn its place. |
| Effect /15 | 13 | 15 | The “ocean as a world of states” gestalt already fires. A stronger frame can make the insight persist rather than dissolve into legend decoding. |
| Clarity /15 | 9 | 14 | Primary deficits are scale, hierarchy demonstration, and terminology. All are directly fixable. |
| Truth /20 | 12 | 19 | The geometry is responsibly sourced, but the novel data model must be declared in-work, not merely recoverable from adjacent prose. |
| **Total** | **73/100** | **96/100** | Strong concept, needs a publication-grade explanatory and disclosure layer. |

Priority order:

1. Truth contract: provisional status, precise nomenclature, topology/seam qualification, registry.
2. Clarity and Precision: larger master plate, enlarged polar views and legend, visible border key.
3. School declaration: name the cartographic/schematic synthesis and explain what each layer preserves.

## AMEND 3 — Binding design amendments

1. **Declare the model in the artifact.** Every master plate must state: classic 56 province identities; OSW-authored nearest-seed cells; provisional 11-realm/22-region organization; no area or boundary measurement.
2. **Make hierarchy learnable from marks.** Realm, region, and state boundaries must appear in a visual key using the same strokes as the map; color remains redundant rather than exclusive.
3. **Design the master, then derive the thumbnail.** The standalone SVG is the reference artifact with publication-scale type, polar insets, and legend. HTML scales it responsively without removing information.

Verdict: **NEEDS-WORK**, with a clear path to a high-ASPECT publication plate.

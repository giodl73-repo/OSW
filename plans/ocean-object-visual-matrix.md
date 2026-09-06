# Ocean-object visual matrix

**Status:** implementation candidate

## Purpose

Turn the 110-object registry into a single navigable explanation. A reader who
sees a coloured patch on an ocean map should be able to identify the kind of
claim being made and the evidence still needed before naming an object.

## Audiences and questions

- Curious reader: “What kind of thing am I looking at?”
- Researcher: “What identity test, geometry, time support, and uncertainty apply?”
- Map builder: “Which visual channel and metadata contract fit this evidence?”
- Maintainer: “Can the view regenerate deterministically from the CSV registry?”

## Artifacts

1. `figures/osw-ocean-object-matrix.svg`: static, self-describing overview.
2. `guides/13-HOW-TO-NAME-AN-OCEAN-PATCH.md`: decision path and textual matrix.
3. `analysis/build_ocean_object_matrix.py`: standard-library-only generator.
4. Tests for deterministic output, accessibility metadata, registry counts,
   category completeness, and guide links.

## Visual structure

The 1600 × 1100 SVG has three reading bands:

1. **Evidence ladder:** map mark/region/line/colour → measured representation →
   organized object → classified event → integrated pool or boundary flux. It
   occupies the top third as the primary reading path.
2. **13 type cards in a 7+6 grid:** one equal card per ontology type so frequency
   does not imply scientific importance. Each card shows name, decisive
   question, icon/shape code, and editorial object count.
3. **Evidence matrix:** rows for identity test, geometry, time, coverage, and
   mobility. Marks summarize available combinations; they do not locate ocean
   features or imply that absent combinations are impossible.

An adjacent five-step ladder distinguishes measured field, material/organized
object, classified event, integrated pool, and boundary flux.

## Encoding contract

- Type uses label + shape + restrained hue; colour is redundant.
- Observed representation class and registry evidence status are separate
  facets; neither substitutes for object type.
- Representation class uses distinct border/dash grammar and explicit text.
- Counts are editorial registry counts, not prevalence or area.
- No geographic projection appears; this is an ontology diagram, not a map.
- Every type receives equal visual area.
- Long names wrap; nothing falls below 14 px at native size.
- Text contrast meets at least 4.5:1 and the shape/label grammar survives grayscale.
- Dark ocean background, high-contrast warm text, cyan structure lines, and
  colour-blind-safe accents align with OSW visual language.

## Decision path

```text
What was measured?
├── property/composition ─► body, layer, boundary, or event?
├── velocity/trajectory ──► flow or connectivity structure?
├── repeating phase ──────► wave/oscillation?
├── terrain/contact ──────► substrate or contact boundary?
├── fractional cover ─────► phase/cover object?
└── integral across geometry
    ├── line/surface per time ─► flux
    └── volume at time ────────► pool/control volume

Then declare geometry + time + coverage + mobility + evidence status.
```

## Accessibility and text alternative

The SVG includes `<title>`, a concise `<desc>`, `role="group"` labels for major
bands, and no meaning carried by colour alone. Guide 13 is the complete,
reflowable textual equivalent and reproduces the decision path and all 13 type
cards. The generator emits a companion summary from the same CSV data so visual
and textual counts cannot drift.

## Data and generation

Inputs are the two UTF-8 CSV registries. Rows are sorted by declared object ID;
type order follows `CLASSIFICATION.md`. The script performs no network access,
uses no timestamps, and writes stable formatting. It fails on unknown enums,
duplicate IDs/names, empty anchors, or count disagreement with tests.

Build command: `python analysis/build_ocean_object_matrix.py`. The generator
owns the SVG and summary; generated files carry a do-not-hand-edit notice.
Canonical type order is declared once in the generator and tested against the
classification's type table.

## Non-goals

- Not a world map, natural hierarchy, scientific standard, or exhaustive claim.
- Not a substitute for exact external vocabulary identifiers.
- Not a display of frequency, size, importance, certainty, or geographic area.
- Not an interactive atlas in this increment.

## Acceptance checks

- All 110 objects contribute exactly once to one primary type count.
- All 13 types and every used identity test appear in SVG or textual alternative.
- SVG has title, description, evidence warning, and registry version/count.
- Major SVG bands have semantic group labels; all coordinates stay in viewBox.
- Text meets 4.5:1 contrast and the encoding remains legible in grayscale.
- Output rebuild is byte-stable and requires only Python standard library.
- Guide links resolve and full offline test suite passes.
- Rendered SVG is opened and visually inspected before roles sign-off.

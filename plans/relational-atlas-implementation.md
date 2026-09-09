# Relational Atlas implementation specification

Date: 2026-08-29  
Status: proposed for native-role review; private branch only  
Source commit: `9276891`

## 1. Intent

Turn the coast-masked 56-province / 36-feature Atlas from an illustrated
catalog into a relational map that can answer two complementary questions:

1. **Place first:** what schematic waters, flows, edges, relief, life zones,
   and events cross this ocean province?
2. **Object first:** which ocean provinces does this schematic feature cross?

The interface should also make individual shapes easier to read through
spotlighting, labels, a shape-first ground, coast-following clearance, explicit
Pacific-seam treatment, zoom anatomy, and evidence-class cues.

## 2. Truth contract

The crossing matrix is a deterministic relationship between two OCEANLINES
display artifacts: the approximate coast-owned province geometry and the
schematic feature geometry. It is a **rendered-overlap index**, not an observed
ecological boundary, transport diagnosis, water-mass analysis, or claim that a
whole province physically belongs to a feature.

Observed or modeled geometry may replace an interpretive feature only through
the separately validated admission path in Section 10. No visual improvement
may silently promote a feature's evidence class.

## 3. Constraints and non-goals

- Keep all current conceptual and observed Atlas modes.
- Preserve keyboard, touch, reduced-motion, narrow-screen, and text-directory
  access.
- Keep default validation offline and dependency-light.
- Reuse the exact province SVG coordinate system and Natural Earth land mask.
- Do not redistribute incompatible Longhurst or feature-boundary data.
- Do not call schematic crossings “true ocean boundaries” or use them to infer
  heat content, transport, causation, or future conditions.
- Do not promote Atlas 11 or push a remote without a later owner decision.

## 4. Stage A — rendered-overlap engine

### A1. Geometry intersection

After both inline SVGs load, compute a cached 36 × 56 tri-state matrix in the
shared `1600 × 1050` coordinate system.

For each province/feature pair, combine three deterministic tests:

1. sample every feature path at a maximum six-unit arc-length interval and test
   sampled points with the province path's `isPointInFill`;
2. sample a twelve-unit lattice inside the province bounding box and test
   province-contained points against feature child `isPointInFill` and
   `isPointInStroke`;
3. run a finer secondary pass around a detected near-contact without using the
   catalog anchor to create a positive relationship.

Classify every pair as `overlap`, `near-contact`, or `none`. A positive overlap
requires sampled rendered geometry inside both objects. `near-contact` records
a resolution-dependent or tangential relationship within the declared finer
tolerance; it is never silently collapsed into `none` or promoted to overlap.
Catalog anchors remain available only for label placement and diagnostics.

Record algorithm version and tolerances beside the matrix. Masked land does not
need a second test because province interiors already exclude the identical
Natural Earth land path.

### A2. Relational interaction

- Province selection lists and spotlights every overlapping feature, grouped
  by lens and ordered by catalog number.
- Feature selection lists and spotlights every overlapping province and lists
  near-contacts separately.
- Empty results say “no crossing in the schematic rendered geometry,” not “no
  ocean relationship.”
- Provide a browser-generated CSV export with all 2,016 pairs, tri-state result,
  hit method, coarse and fine tolerances, algorithm version, province edition,
  catalog version, feature evidence class, and SHA-256 values for both input
  SVGs. Serialize UTF-8 with LF endings, a fixed documented column order, and
  province-code / feature-number row ordering.
- Announce changed relation summaries through the existing polite live region.
- Render the same related features and provinces as operable button lists under
  accessible headings; counts alone are not the equivalent text route.

### A3. Verification

- Test the matrix dimensions, symmetry of the two lookup directions, stable
  ordering, declared method metadata, tri-state tokens, and CSV schema.
- Add curated fixture expectations for obvious cases such as Gulf Stream/GFST,
  Kuroshio/KURO, Drake Passage/FKLD–ANTA vicinity, and ACC Southern provinces.
- Check in a fixture produced by the versioned browser algorithm and run a local
  headless-browser smoke test when Edge is available; default structural tests
  still run offline without downloading a browser.

## 5. Stage B — focus, labels, and hierarchy

### B1. Selection spotlight

- Selecting a feature keeps it fully opaque, dims other visible features, and
  emphasizes all intersecting provinces.
- Selecting a province emphasizes it and its crossing features while retaining
  muted geographic context.
- Escape or an explicit reset restores the active lens without losing filters.
- Hover may preview but must not replace the persistent selected state.
- The focused object is never dimmed. Unrelated objects retain minimum contrast,
  and related/not-related state has a redundant solid/dashed stroke treatment.

### B2. Geographic labels

- Labels use names or reviewed short names, never catalog numbers.
- Labels appear for the active lens; the selected feature label always appears.
- Run deterministic screen-space collision resolution with bounded vertical
  displacement and restrained leader lines when displacement exceeds a
  threshold.
- Constrain displaced anchors to ocean and the feature's original side of the
  projection seam so a label never migrates onto land or across the Pacific cut.
- Labels remain subordinate to geometry, are removed from the tab order, and
  hide at narrow widths where the text directory is the equivalent route.

### B3. Ground hierarchy

Make **Quiet states** the default feature-reading ground while retaining
**Ocean states** for province reading. In quiet mode:

- province borders and codes recede;
- the selected province remains crisp;
- intersecting provinces receive a non-color emphasis;
- land remains dark and unmistakably unavailable to feature fills.

## 6. Stage C — geographic polish

### C1. Coast-following clearance

Expand the black land subtraction path with a small declared stroke so
schematic areas and lines sit just offshore instead of terminating directly on
the coastline. Gates explicitly exempted from the clearance may meet both
banks. The initial exemption registry covers Drake Passage, the Indonesian
passages, Gibraltar, and Bab el-Mandeb. This is fixed SVG-unit visual clearance,
not a physical buffer-distance measurement.

### C2. Pacific seam

- Mark every seam-crossing feature in generated SVG metadata.
- Render matched left/right continuation marks with shared shape identity.
- Treat the split Indo-Pacific warm pool as one selectable group and retain one
  label.
- Add a short method note that the equirectangular cut is a projection seam,
  not a physical break.

### C3. Shape-first view

Add a third conceptual ground, **Fluid shapes**, which removes province fills,
boundaries, and codes while retaining a low-contrast ocean field, dark land,
ghost coastlines, active shapes, and labels. It changes presentation only.

## 7. Stage D — feature anatomy and zoom

- Add “Zoom to feature” beside the selected feature and support activation from
  the shape itself without making single-click selection surprising.
- Fit the selected feature's masked bounding box with padding; preserve a clear
  return-to-world control and URL-addressable `feature=` state.
- Reveal existing anatomy at closer scale: source cores, shelves, branches,
  gyre spines, companion fronts, ridge flanks, trench teeth, oxygen cores, and
  plateau contours.
- Keep strokes legible at zoom and honor reduced motion.
- Province and feature zoom are mutually exclusive explicit frames; changing a
  lens preserves a valid feature frame and clears an invalid one accessibly.
- On explicit zoom, move focus to the frame summary; on reset, restore focus to
  the invoking control. Passive filter or mode changes never steal focus.

## 8. Stage E — evidence-status cues

- Normalize each record to `CONCEPTUAL`, `SYNTHESIS`, `OBSERVATIONAL`, or
  `MODELED/MIXED` without changing the underlying catalog wording.
- Show the status as text in the detail panel and directory.
- Add redundant line/fill treatment in the selected-state halo; never rely on
  status color alone.
- Put the precise source, boundary caveat, depth, clock, and evidence wording
  within the same reading path.
- State beside the badge that evidence class describes support for the named
  phenomenon, not validation of the hand-drawn footprint, and that the classes
  are types rather than an ordinal quality score. Planetary analogy status is
  not part of this Earth-feature badge.

## 9. Documentation and public explanation

- Replace stale point/marker wording in the CSV, JavaScript records, and method
  copy where shapes now exist.
- Use “schematic rendered overlap,” never “true crossing,” in controls,
  summaries, exports, and release notes.
- Explain rendered-overlap, coastline clearance, seam continuation, label
  displacement, and shape-first presentation in `atlas/README.md`.
- Add a non-color relational summary to the map for every selection.
- Add a compact “How to explore” disclosure covering place-first, object-first,
  and shape-only routes.
- Record the stage in project history only after owner visual acceptance.

## 10. Observed-geometry admission path

Create a versioned, machine-validated contract for future feature geometry.
Each candidate must declare:

- feature ID and geometry edition;
- evidence class and whether geometry is observed, diagnosed, modeled, or
  illustrative;
- provider, product/dataset, variable or diagnostic, version, source URL,
  SPDX-style license identifier, compatibility decision, decision authority,
  decision date, citation, acquisition time, and source checksum;
- CRS, longitude convention, depth/layer, time interval, baseline or threshold,
  missing-value handling, and simplification tolerance;
- transformation command, output checksum, and reviewer status.

The validator must reject missing provenance, incompatible license, undeclared
CRS, unknown feature IDs, non-finite coordinates, and evidence-class promotion.
Initial registry rows remain `schematic`; this stage creates the door, not fake
observations to walk through it.

The relational engine and registry are Earth-specific. Reuse for gas giants
requires a separately reviewed mechanism-level correspondence contract; Earth
province overlap and evidence badges do not transfer by visual analogy.

## 11. Files and interfaces

Expected primary changes:

- `atlas/app.js` — intersection engine, relational state, labels, zoom, URL,
  matrix export, evidence normalization;
- `atlas/index.html` — relation summary, feature zoom/reset, labels and ground
  controls, evidence badge, export control;
- `atlas/styles.css` — spotlight, related provinces, labels, shape-first ground,
  seam continuation, responsive and reduced-motion behavior;
- `analysis/build_atlas_feature_overlay.py` — coast clearance, seam metadata,
  label anchors and anatomy metadata;
- `analysis/test_atlas.py` — structural and contract tests;
- `research/feature-geometry-register.csv` and
  `research/feature-geometry-contract.schema.json` — future geometry admission;
- `analysis/validate_feature_geometry.py` — offline admission validator;
- `atlas/README.md` and the source register — method and provenance.

All new registries, schemas, fixtures, and exports receive repository-relative
source-register entries and explicit OCEANLINES ownership/status notes.

## 12. Acceptance gates

1. All eight native roles review this specification; every P1/P2 is amended or
   explicitly deferred with owner approval.
2. Exactly 36 features and 56 provinces produce 2,016 queryable tri-state pair
   records with stable schema and input checksums.
3. Province and feature lookups are reciprocal and never use the old centroid
   method alone.
4. Every active-lens shape has a non-numeric label route and collision fallback.
5. Land remains subtracted in all three conceptual grounds.
6. Seam-crossing features retain one identity and have visible continuation.
7. Feature and province zoom work by keyboard, pointer, URL, and reset.
8. Evidence status and limitations remain available without color or hover.
9. The geometry-admission validator passes the committed schematic registry and
   fails malformed, unlicensed, unknown-ID, and evidence-promotion fixtures.
10. The complete offline suite, JavaScript syntax check, generated-SVG XML
    parse, and six-lens browser review pass before commit.
11. A post-implementation native-role review records the final implementation
    commits; this plan review cannot approve code that did not yet exist.

## 13. Execution order and rollback

Implement in five independently reviewable commits: relational kernel;
focus/labels/hierarchy; geographic polish; anatomy/evidence; admission contract
and documentation. Each commit regenerates artifacts and passes the offline
suite. If a later stage fails visual review, retain earlier commits and remove
only that additive stage; do not revert the coast mask or character silhouettes.
The work remains private, receives no Atlas milestone, and is not pushed until
owner visual acceptance. The method/source register must describe every new
artifact before final implementation review.

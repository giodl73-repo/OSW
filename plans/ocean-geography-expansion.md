# OCEANLINES ocean-geography expansion plan

Status: proposed for native-role review
Research basis: `signals/discover/websearch/ocean-geography-ontology-websearch-2026-08-29.md`

## Purpose

Broaden the conceptual atlas from twelve heat-led examples into a selectable
geography of the ocean. The atlas should name large volumes and structures that
are cold, fresh, salty, oxygen-poor, deep, moving, bounded, or shaped by the
seafloor without suggesting that the ocean can be tiled into exclusive blobs.

HEATPLATES, the projection laboratory, all observed modes, and the existing
twelve records remain intact.

## Core model

Every feature belongs to one primary lens and may carry several orthogonal
facets. Features can overlap horizontally and vertically.

Primary lenses:

1. **WATERS** — three-dimensional water masses and persistent reservoirs.
2. **FLOWS** — gyres, currents, overturning branches, eddies, and rings.
3. **EDGES** — fronts, convergence/divergence zones, layer boundaries, and gates.
4. **FLOOR** — basins, shelves, ridges, trenches, plateaus, and canyons.
5. **LIFE** — oxygen, nutrient, productivity, and ecological provinces.
6. **EVENTS** — transient anomalies such as heatwaves, cold tongues, and plumes.

Facets:

- depth: surface / upper / intermediate / deep / bottom / full-column / seabed
- property: warm / cold / fresh / salty / low-oxygen / nutrient-rich / dynamic / relief
- clock: persistent / seasonal / interannual / episodic / geologic
- evidence: conceptual / observational / synthesis / modeled

These facets use controlled enumerations. Every record also carries `basis`, a
short statement of the properties, source region, formation/transformation, or
maintaining process by which the named feature is recognized.

The product must say that these are overlapping views, not mutually exclusive
countries. “Coldmass” may appear in explanatory prose, but `water mass` is the
scientific record type.

## First curated catalog

Expand from 12 to 36 records. Preserve the existing 12 and add 24 representative
features; this is an intentionally curated first pass, not an exhaustive global
gazetteer.

### WATERS — add eight

- Antarctic Bottom Water
- North Atlantic Deep Water
- Antarctic Intermediate Water
- Subantarctic Mode Water
- North Pacific Intermediate Water
- Labrador Sea Water
- Mediterranean Outflow Water
- Red Sea Water

### FLOWS — add five

- North Pacific Subtropical Gyre
- South Pacific Subtropical Gyre
- North Atlantic Subtropical Gyre
- South Atlantic Subtropical Gyre
- Indian Ocean Subtropical Gyre

### EDGES — add three

- Antarctic Polar Front
- Subantarctic Front
- Equatorial Pacific divergence and upwelling

### FLOOR — add four

- Mid-Atlantic Ridge
- East Pacific Rise
- Mariana Trench
- Kerguelen Plateau

### LIFE — add four

- Eastern Tropical North Pacific oxygen-minimum zone
- Eastern Tropical South Pacific oxygen-minimum zone
- Arabian Sea oxygen-minimum zone
- Sargasso Sea oligotrophic province

The existing Northeast Pacific Blob and El Niño tongue seed EVENTS. Existing
currents, gates, reservoirs, and buried waters are reclassified without losing
their legacy family tags.

## Interface

1. Replace the four crowded lens buttons with seven buttons: ALL FEATURES plus the
   six primary lenses. Preserve HEATMASS, OCEANREALMS, and OCEANBELTS as legacy
   study links beneath the filters rather than treating them as the full ocean.
2. Add accessible select filters for depth, property, and clock. Filters combine
   with the active primary lens and update the count, marker set, directory, URL,
   and assistive status text.
3. Keep ocean-basin names visible as quiet base geography. State beside the map
   that feature markers are representative index points, not asserted polygon
   centroids or boundaries.
4. Default to WATERS rather than showing all 36 markers simultaneously. ALL
   FEATURES remains available with deliberate collision offsets and a complete
   text-directory route, but it is not the initial cluttered view.
5. Group the textual directory by primary lens and expose only matching records.
   Every record remains keyboard selectable.
6. Expand the information panel with `LENS` and `PROPERTY` while retaining role,
   depth, clock, evidence, source, and inferential boundary.
7. Rewrite the grammar section as “Six overlapping geographies of the ocean.”
   Keep the older seven-shape heat grammar available from the HEATMASS guide.
8. Add a visible shape-and-color marker legend and an `aria-live` result summary.
   Unmatched markers are hidden and removed from keyboard navigation.

## Scientific and visual firewall

- No new filled region polygons in this stage. A marker locates the feature's
  representative setting; it does not diagnose an edge or footprint.
- Each record declares depth, property basis, persistence, evidence class,
  source, and what the marker cannot establish.
- A water mass is not a current; a front is not a wall; a gyre is not homogeneous;
  an oxygen-minimum zone is not a temperature class; a seabed feature is not a
  water property.
- Observed SST and Argo modes do not inherit conceptual labels as measurements.
- Future polygons require a reproducible variable, threshold or classification
  rule, period, depth, source receipt, and uncertainty statement.

## Data and implementation

- Extend each zone record with `lens`, `depthClass`, `properties`, `basis`, and
  `legacyFamilies` while retaining existing export fields.
- Give every new record a feature-specific authoritative source URL and source
  identifier; register sources rather than relying on a generic overview page.
- Keep source data in the existing deterministic JavaScript catalog for this
  stage; update the CSV exporter and checked-in catalog together.
- Isolate the combined-filter matcher and query-state parser as pure functions;
  test representative combinations in addition to catalog invariants.
- Use category-specific marker shape/border in addition to color.
- Update the map alternative text and directory summary from the active filters.
- Preserve query parameters for the selected lens and facets.

## Acceptance gates

- Exactly 36 unique numbered records, 24 new and 12 preserved.
- All six lenses contain at least two records and every new record has a source
  ID, authoritative URL, identifying basis, and explicit inferential boundary.
- Filtering works by lens, depth, property, and clock; reset restores WATERS.
- Controlled depth, property, clock, and evidence values pass schema checks and
  the checked-in CSV is an exact ordered projection of the application catalog.
- No more than the selected subset is keyboard-focusable or present in the
  visible directory.
- Category meaning is recoverable without color.
- Existing observed modes, depth ladder, projection laboratory, HEATPLATES,
  research exports, and relative links still pass.
- Desktop and narrow Edge inspection show no unusable marker pile-up, clipped
  controls, or hidden caveats.
- Native `.roles` review approves the implementation before the milestone is
  recorded in `PREVIEW-STATUS.md`.

## Deliberately deferred

- Observational or diagnosed polygons for water masses, fronts, or provinces.
- A claim of exhaustive global coverage.
- Common-scale comparison of schematic feature area.
- Automatic classification from World Ocean Atlas or Argo fields.
- Planetary transfer of the expanded Earth ontology.

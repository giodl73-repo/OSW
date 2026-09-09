---
skill: roles-check
topic: longhurst-2007-gebco-depths
date: 2026-09-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook, orbit]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — Longhurst 2007 geometry × GEBCO depths

**Artifact type:** external scientific-data acquisition, edition crosswalk,
derived global raster mask, bathymetric summary, and interactive cartography

**Source commit:** `8f4602e7ab9ddb3e6c5f864b6e47b50965b6ad84`

**Reviewed artifact SHA-256:**

- acquisition/build script: `116B71CCAD795A0E850CA0DE11DC375B7D90B4EA494CD146DAF1243537E7C354`
- source receipt: `C553D6FCF1F7D73413D02F594D759F4F8BBBF5F016724DE17AC30E12A700FDC9`
- derived depth/mask payload: `8DD566483E27F68BD9B2C8D53B5750BD27B7F65F7747FBE2C248326315C11EB3`
- browser data: `2E22B32B6ECA8F603979E2926E88DBF9B5D67DDED4DD4D71192E982DA1048E21`
- browser logic: `5459F36E80CBF36E94A3562B83D1B24D3A0FE6B94D11E0FC8AB590D71C42D7D2`
- browser HTML: `C7BD2DE71BC7F5D66DA994A659658C7DBD911520BC48C695689784AB71E7C221`
- third-party notices: `484AE3379048B50D5FD918D2861E9452DC1C5B7EF8314F85CB9C3C0F19BF35E3`

All eight native roles review this stage because it replaces illustrative
seed windows with provider geometry, intersects two external scientific
products, exposes an edition mismatch, and publishes a global map whose
precision and meaning need strong limits.

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Static ecological provinces are neither currents nor material water masses, and their borders are not physical walls. | P2 | Map interpretation | Call them source-aligned static mean-surface ecological footprints and keep motion and water-mass layers separate. **Resolved.** |
| 2 | The deepest seafloor band sampled inside a province is not the depth occupied by its ecology throughout the polygon. | P2 | Depth profile | Describe bands as province-wide seabed reach, never full-depth habitat or water-column occupancy. **Resolved.** |
| 3 | The 2007 edition is a useful reference coordinate system, not a diagnosis of present ocean state. | P3 | Research model | Treat dynamic fronts, heat, transport, and overturning as independently sourced overlays. **Accepted.** |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | OSW's inherited 56 identities do not exactly match the 54 geometries in Longhurst Version 4. | P2 | Edition crosswalk | Record five aliases and leave NPSE and OCAL without separate Version 4 geometry rather than fabricating borders. **Resolved.** |
| 2 | The derived map must remain auditable even though provider payloads are not mirrored. | P2 | Source custody | Record exact URLs, response bytes and hashes, headers, product versions, access time, licenses, crosswalk, and transformations. **Resolved.** |
| 3 | GEBCO source type and datum limitations survive the spatial intersection; three invalid provider polygons also required repair. | P3 | Quality record | Retain TID statistics and repair reasons, and record the zero measured planar-area change from `make_valid`. **Accepted.** |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A 0.25-degree cell-center classification with spherical area weighting is not an exact vector overlay or polygon integral. | P2 | Cartographic precision | Repeatedly label all cell and area results as sampled estimates. **Resolved.** |
| 2 | A global province map needs a projection and visual hierarchy suited to the ocean-first atlas. | P2 | Rendering | Use the named Oceanic Mollweide view, recess land and gaps, retain hairline province borders, and emphasize only the selected footprint. **Resolved.** |
| 3 | Rectilinear or simplified-looking source borders belong to the static provider product, not to new OSW generalization. | P3 | Boundary provenance | Preserve the source-aligned mask and avoid implying contemporary front precision. **Accepted.** |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “True footprint” would overstate both boundary truth and raster precision. | P2 | Public wording | Use “source-aligned 2007 footprint” and “0.25° sampled estimate.” **Resolved.** |
| 2 | Silently dropping the two older-only identities would make the 56-entry interface appear complete when it is not. | P2 | Selection state | Keep NPSE and OCAL selectable and show a conspicuous no-separate-V4-footprint state with no invented highlight. **Resolved.** |
| 3 | The 99.6% wet-center inclusion rate is a seam diagnostic, not proof that one taxonomy closes or explains the ocean. | P3 | Summary claims | Report the numerator, denominator, outside count, and boundary limits without calling it complete ocean coverage. **Accepted.** |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A canvas-only global footprint and profile would hide the result from nonvisual users. | P2 | Equivalent content | Mirror status, wet samples, area, depth extent, and TID composition in live text and accessible canvas labels. **Resolved.** |
| 2 | Selection, bathymetric bands, source state, and missing-edition state cannot rely on color alone. | P2 | Interaction and legend | Provide redundant text, a legend, a gold selected boundary, profile labels, and an explicit older-edition status. **Resolved.** |
| 3 | Changing the province must remain keyboard operable without disrupting reading position. | P3 | Controls | Reuse the native selector, update output in place, and avoid focus stealing. **Accepted.** |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Routine site use and tests must not depend on downloading multi-megabyte WFS and OPeNDAP responses. | P2 | Pipeline | Keep acquisition explicit and networked while committing deterministic derived outputs for offline use. **Resolved.** |
| 2 | Geometry aliases, raster run lengths, overlaps, area weights, and browser serialization create silent-failure risks. | P2 | Validation | Pin optional numerical dependencies and assert schema, crosswalk, cardinalities, repair set, aggregates, RLE totals, and exact browser-payload equality. **Resolved.** |
| 3 | Omitting provider bytes means a rebuild still depends on provider availability and mutable service behavior. | P3 | Reproducibility | Preserve response hashes and committed derivatives; compare future downloads before accepting regeneration. **Accepted.** |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Marine Regions attribution and the GEBCO public-domain notice must travel with the derived layer. | P2 | Licensing | Add a third-party notices file and link it from the README and viewer notes. **Resolved.** |
| 2 | A new authoritative geometry layer changes the project's documented evidence boundary and roadmap. | P2 | Project record | Align the source register, history, roadmap, method README, guide, and viewer copy in this commit. **Resolved.** |
| 3 | The permanent public identity model—54 current geometries, dual editions, or a migrated directory—has not yet been chosen. | P3 | Roadmap | Preserve the crosswalk and make that choice a named next-stage decision rather than hiding it in implementation. **Accepted.** |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Earth ecological provinces and bathymetric polygons have no direct gas-giant analogue. | P2 | Comparative interpretation | Do not transfer these geometries to Jupiter or Saturn; transfer only the evidence and provenance discipline. **Resolved.** |
| 2 | A seafloor-reached depth band is not analogous to a gas-giant pressure surface or cloud deck. | P2 | Depth analogy | Keep the comparison absent from this viewer and explain it only in a qualified comparative guide. **Resolved.** |
| 3 | The reusable contribution is the layered contract—reference partition, dynamic fields, provenance, and uncertainty—not the Earth-specific borders. | P3 | Comparative method | Carry that abstract structure into later cross-planet work. **Accepted.** |

## Totals and verdict

- P1: 0
- P2: 16, all resolved in the reviewed artifacts
- P3: 8, accepted as documented constraints or forward work
- Verdict: **APPROVED-WITH-CONDITIONS**

The stage is suitable for a private-preview commit. Before a public release,
OSW must decide whether the selector formally migrates to the 54-feature 2007
edition or supports two explicit editions. Source-aligned statistics must not
be attributed to NPSE or OCAL, the 54-feature layer must not be described as
the inherited 56-province edition, and static footprint evidence must remain
separate from dynamic or volumetric ocean claims.

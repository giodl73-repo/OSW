---
skill: validate-design
topic: atlas-07-showcase-readiness
date: 2026-08-28
reviewer_count: 10
p1_count: 0
p2_count: 16
p3_count: 24
domain_roles_active: [Physical Oceanographer, Scientific Cartographer, Accessibility Specialist, Climate Data Steward]
---

# Atlas 07 showcase-readiness design review

Scope: the complete Atlas 07 HTML, CSS, JavaScript, fixed display fields, and
headless Chromium renders at 1440×1000 and 390×844. This review asks whether
the atlas is ready to serve as a first impression for a new scientific reader,
not whether the underlying release checks passed.

## BLOCK 0 — Content signal catalogue

| Signal phrase | Domain category |
|---|---|
| “Temperature is not heat content” and transport across a declared section | physical oceanography |
| “Equirectangular display” and aligned radial azimuthal-equidistant sampling | scientific cartography |
| “Non-color map summary,” canvas descriptions, keyboard controls, and reduced motion | accessibility |
| “NOAA OISST v2.1,” fixed date, baseline, estimated error, and checksums | climate-data stewardship |
| Interactive atlas with responsive desktop and mobile layouts | web interaction |

## BLOCK 1 — Expert roster

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
| “Temperature is not heat content” and transport across a declared section | Physical Oceanographer | The atlas makes scientific distinctions whose accuracy determines whether the visual metaphor misleads. |
| “Equirectangular display” and aligned radial azimuthal-equidistant sampling | Scientific Cartographer | Projection, orientation, geographic reference, and scale design require specialist review. |
| “Non-color map summary,” canvas descriptions, keyboard controls, and reduced motion | Accessibility Specialist | Several central graphics are canvas or dense SVG and need equivalent nonvisual and low-vision access. |
| “NOAA OISST v2.1,” fixed date, baseline, estimated error, and checksums | Climate Data Steward | Product identity, transformations, uncertainty, and provenance control the meaning of observed modes. |
| Interactive atlas with responsive desktop and mobile layouts | No expert needed | The stock Implementation, Testing, and Architect disciplines cover this signal. |

BLOCK 1 domain count = 4

## BLOCK 1.5 — Roster commitment table

| Reviewer | Role | Source |
|---|---|---|
| Physical Oceanographer | Domain expert | Domain |
| Scientific Cartographer | Domain expert | Domain |
| Accessibility Specialist | Domain expert | Domain |
| Climate Data Steward | Domain expert | Domain |
| Architect | Stock discipline | Stock |
| Code-Quality | Stock discipline | Stock |
| Documentation | Stock discipline | Stock |
| Testing | Stock discipline | Stock |
| Process | Stock discipline | Stock |
| Implementation | Stock discipline | Stock |

Domain row count = 4. All domain reviewer names exactly match BLOCK 1.

## BLOCK 2 — Per-reviewer findings

### Physical Oceanographer

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | The public promise is ocean heat geography, but the only quantitative map is one day of surface temperature or anomaly; there is no heat-content or transport map yet. | P2 | hero and observed modes | Label Atlas 07 as a surface demonstrator in the first viewport and make the next quantitative layer full-depth heat content or section transport. |
| 2 | Atlas 07 cannot yet illuminate the new abyssal source-versus-transport question because it contains neither abyssal observations nor three-dimensional circulation. | P2 | observed workspace | Do not use this atlas as evidence for the abyssal mechanism; add a separately receipted deep-ocean layer later. |
| 3 | The conceptual zones repeatedly state depth, clock, evidence, and inferential boundaries. | P3 | zone panel | Retain these fields as mandatory metadata for every new zone. |
| 4 | The measurement firewall correctly separates surface temperature, volume heat content, section transport, and anomaly. | P3 | measurement firewall | Keep this compact panel adjacent to any broader heat claim. |

### Scientific Cartographer

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | The observed world map has grid lines but no latitude, longitude, basin, or coastline labels, so a new reader cannot locate a pattern precisely. | P2 | observed map | Add restrained coordinate labels and a few basin or geographic anchors without cluttering the field. |
| 2 | Continuous color keys label only their endpoints; readers cannot estimate intermediate values or identify the neutral anomaly value reliably. | P2 | temperature key | Add ticks, units, and a marked zero to the anomaly legend. |
| 3 | The conceptual SVG's embedded labels become unreadably small at a 390-pixel viewport. | P2 | conceptual map on mobile | Provide a tap-to-expand map or a mobile simplified map with external labels. |
| 4 | Projection, antimeridian, polar-cap extent, mirrored southern orientation, missingness color, and display stride are declared. | P3 | map note and polar method | Preserve this unusually strong projection disclosure. |

### Accessibility Specialist

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | The conceptual SVG has only a broad image description; its tiny internal labels are not available as a complete structured text equivalent. | P2 | conceptual map | Add an adjacent compact zone list or long description tied to the image. |
| 2 | Map modes, lenses, probes, ring inputs, and details controls are native keyboard-operable elements with visible focus treatments. | P3 | interactive controls | Preserve native semantics and test tab order on every release. |
| 3 | Observed canvases expose dynamic summaries, semantic tables, and ARIA descriptions rather than relying on color alone. | P3 | observed summaries | Keep summaries synchronized with mode and coordinate state. |
| 4 | Desktop and mobile renders show no horizontal overflow, and reduced-motion preferences disable the only transition. | P3 | responsive CSS | Retain the 390-pixel viewport as a visual regression target. |

### Climate Data Steward

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | The fixed NOAA OISST product, date, baseline, estimated-error meaning, URLs, and committed data records are declared. | P3 | observed metadata and D1 | Keep the provider receipt visible from every observed mode. |
| 2 | “Observational analysis” correctly avoids presenting OISST as raw observation-only truth. | P3 | evidence field | Use the fuller phrase in the mode label as well when space permits. |
| 3 | Absolute, anomaly, and estimated-error fields are separate controls with product-specific boundaries. | P3 | map modes and source register | Never combine the uncertainty layer into a generic confidence score. |
| 4 | Latitude summaries disclose that values are unweighted and exclude missing cells. | P3 | summary captions | Add area weighting only as a separately tested statistic. |

### Architect

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | The same shell serves a concise conceptual tour and a dense analytical workbench, creating a sharp jump in complexity when an observed mode is selected. | P2 | atlas shell | Split the experience into “Explore the idea” and “Inspect the data,” or add a clear progressive transition. |
| 2 | Every observed diagnostic is expanded by default, producing a 4,914-pixel desktop page and a 6,931-pixel mobile page. | P2 | map-data summary | Keep the map, probe, and one headline comparison open; move polar and full-ladder diagnostics into disclosures. |
| 3 | In observed desktop mode the right metadata panel stretches beside the full workbench, leaving a conspicuous empty column for most of the page. | P2 | zone panel | Make the metadata card sticky and intrinsically sized, or move it above the diagnostic stack. |
| 4 | The zone model and observed-field model share consistent role, depth, clock, evidence, boundary, and source slots. | P3 | side panel architecture | Preserve this common information contract. |

### Code-Quality

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | `app.js` combines domain data, rendering, state, URL routing, and event binding in one 633-line global script. | P3 | app.js | Separate data/model, rendering, and controller modules before adding another quantitative family. |
| 2 | DOM selectors and field identifiers are hardwired throughout rendering functions, increasing coupling between markup and code. | P3 | app.js render functions | Centralize element references or pass view objects into renderers. |
| 3 | The latitude-threshold summary assumes both hemispheres always produce a match and would fail on a different mask that does not. | P3 | `renderLatitudeLadder` | Handle a missing threshold explicitly and test it. |
| 4 | Polar colors are round-tripped through CSS strings and a number-matching regular expression. | P3 | `renderPolarMirror` | Return RGB tuples from scale functions and format CSS only at the drawing boundary. |

### Documentation

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | “0 false precision” overstates the claim while the interface displays coordinates and statistics to multiple decimal places. | P2 | hero readout | Replace it with a defensible phrase such as “declared limits” or “explicit uncertainty.” |
| 2 | SST, OISST, climatology, analysis error, and display stride arrive quickly without a short newcomer glossary. | P2 | observed workspace | Add a three-sentence “How to read this map” introduction or expandable glossary. |
| 3 | The headline and land-geography metaphor are memorable and explain the project's central idea quickly. | P3 | hero | Keep this as the public opening. |
| 4 | Method boundaries appear beside the relevant controls rather than only in repository documentation. | P3 | map note, summaries, and zone boundary | Preserve local explanations as features are reorganized. |

### Testing

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | Hosted validation and 42 offline tests protect calculations, static contracts, projection behavior, and accessibility hooks. | P3 | validation suite | Continue requiring both offline and pinned-fixture jobs. |
| 2 | CI does not capture desktop and mobile screenshots, so major whitespace, density, overlap, and hierarchy regressions can pass. | P2 | visual validation | Add deterministic screenshots for conceptual and anomaly modes at 1440 and 390 pixels. |
| 3 | Bookmarkable mode, coordinate, and ring state makes important views reproducible. | P3 | URL state | Add an automated round-trip test for every supported query parameter. |
| 4 | Canvas text alternatives are contract-tested, but no automated accessibility-engine scan is recorded. | P3 | accessibility validation | Add a browser-level accessibility scan as a supplemental check. |

### Process

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | Atlas milestones, commits, evidence classes, data dates, and role verdicts are unusually well recorded. | P3 | README milestones | Continue immutable milestone rows. |
| 2 | Release approval records scientific and functional review but not a named visual-showcase signoff using rendered desktop and mobile evidence. | P2 | release process | Add a visual-readiness gate with saved viewport evidence before the next showcase release. |
| 3 | The source register places a boundary beside every admitted claim. | P3 | source register | Keep new claims out until their boundary is written. |
| 4 | The abyssal research design is correctly separate from the current Atlas 07 evidence class. | P3 | README status | Preserve that separation until new data are implemented. |

### Implementation

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | Conceptual markers 01 and 12 are close enough to collide, making one zone appear missing in the default desktop render. | P2 | conceptual marker layer | Reposition or cluster the markers and add a visual-overlap test. |
| 2 | The observed mobile page is 6,931 pixels tall before opening the complete scan, which hides the narrative conclusion inside an instrument panel. | P2 | mobile observed mode | Collapse advanced diagnostics and add a short result summary immediately below the map. |
| 3 | The observed desktop side panel occupies a full-height grid column even though its content ends near the first map. | P2 | desktop observed mode | Change the observed layout so metadata does not stretch with the analysis column. |
| 4 | Responsive rules produce no horizontal overflow at 390 pixels and reorganize controls into usable native layouts. | P3 | mobile CSS | Preserve the current width behavior while reducing vertical density. |

## BLOCK 3 — Synthesis

```text
Overall verdict: NEEDS-WORK

P1 blockers (must resolve before implementation):
  (None -- proceed to implementation)

P2 conditions (must resolve before sign-off):
  - Physical Oceanographer 1–2 -- the quantitative atlas is surface-only and cannot yet answer the abyssal question
  - Scientific Cartographer 1–3 -- observed geography and scale need stronger reference, and the mobile conceptual map is illegible
  - Accessibility Specialist 1 -- the conceptual graphic needs a complete structured text equivalent
  - Architect 1–3 -- tour and workbench are conflated, all diagnostics are expanded, and the observed sidebar stretches empty
  - Documentation 1–2 -- “0 false precision” and unexplained technical shorthand weaken newcomer trust
  - Testing 2 -- CI lacks rendered visual-regression evidence
  - Process 2 -- release review lacks an explicit visual-showcase gate
  - Implementation 1–3 -- markers collide and observed layouts are excessively long or empty

Cross-reviewer consensus:
  Atlas 07 has a strong visual identity, careful scientific boundaries, robust
  provenance, and sound responsive fundamentals. Multiple reviewers agree that
  the observed mode now contains more analytical capability than its visual
  hierarchy can carry, while the conceptual map needs better small-screen and
  nonvisual legibility.

Strongest signal:
  Reframe the observed experience around one immediate map conclusion, with
  advanced polar and continuity diagnostics progressively disclosed.
```

## AMEND

1. Change the observed atlas shell and map-data summary so the map, a short
   conclusion, and the coordinate probe form the primary view; collapse polar
   mirrors and the full continuity analysis. This addresses the desktop empty
   column and 6,931-pixel mobile workbench.
2. Add labeled geographic anchors and intermediate legend ticks, including a
   marked anomaly zero, directly around the observed map. This makes patterns
   locatable and values estimable before deeper inspection.
3. Separate markers 01 and 12 and provide a mobile-expandable conceptual map
   plus structured zone list. This restores all twelve zones visually and
   makes the conceptual geography available beyond tiny embedded SVG text.

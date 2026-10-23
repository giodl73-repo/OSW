# NGA2024 current-name and dimension evidence

Continues draft PR83 while the independent South Indian supplementary source
acquisition runs. This batch adds primary-source naming evidence and inventory
leads; it changes no existing catalogue identity, width, length or geometry.

## Original and review scope

Official NGA low-resolution American Practical Navigator, Volume II,2024:
11,212,812 bytes,544 PDF pages, SHA256
`d3c5979f526b545831f9544ae3d91f7c2ebdf692338239585c121f4e95b32575`.
The acquisition record identifies the exact official URL, actual response and
title-page rights. Original PDF, page renders and full extracted text remain
private. Public outputs are our attributed structured facts and own diagram.

Title and selected entries on PDF indices0,409,459,469,476,477,510 were visually
read against page renders. Glossary printed pages396,446,456,463,464,497 supply
the recorded facts. A75-heading automatic candidate scan was performed; those
are not75 verified distinct physical currents, and the full glossary has not
been visually reviewed. Neighboring-entry contamination was observed and
excluded, including algae length and binary-code timing.

## Findings

- The edition explicitly aliases Norwegian Current to Norway Current and keeps
  Norway Coastal Current separate. The coastal entry's20-mile and possible
  near30-mile width statements cannot be transferred to the Norway entry.
- The source's Norway flow branches into North Cape and Spitzbergen Atlantic
  currents. Its Spitzbergen Atlantic/Spitzbergen naming convention includes
  northward/westward flow joining East Greenland Current. No modern West
  Spitsbergen identity or measured dimensions are inherited.
- Four source names were not found in the four checked released/effective/
  pending catalogue files: Mentor (alias Peru Oceanic), Cape Horn, Labrador
  Current Extension and North Africa Coast. They are inventory leads, not
  admitted distinct physical identities. Relationships to existing names need
  assessment, including Peru/Humboldt, Falkland/ACC, Labrador/shelf-continuity
  hypotheses and Algerian Current.
- Five scoped numeric candidates retain raw units and qualifiers. Cape Horn's
 150-mile band near70W and about85 miles at65W describe different locations,
 not a seasonal range. Mentor's roughly900-mile westward span at its widest
 section is not an along-current length. Unqualified mile conversion for these
 entries remains unresolved; kilometre fields stay null. Publication year is
 not treated as observation year.

These lessons are recorded as prospective requirements in
`plans/current-prose-extraction-boundary-rule-v1.md`. No old frozen measurement
operator or protocol is back-edited.

## Visualization and verification

`python analysis/build_nga_2024_nordic_names_figure.py` builds an original SVG
and checksum manifest from the structured review. It checks the source edition,
connection/alias conventions, raw coastal units and closed physical-admission
flags. The diagram is conceptual, with explicit publication/no-observation-date
and scale labels; it has no geographic footprint or implied transport budget.

Original pages were rendered and inspected. The initial PDF-engine SVG preview
ignored CSS classes; explicit presentation attributes and arrowheads corrected
portable rendering. Actual Chrome embedded-SVG rendering was inspected after
label/edge spacing was corrected. Direct standalone-SVG full-page screenshot
timed out in the harness; the bounded HTML image rendering succeeded. The
result is `figures/nga-2024-nordic-current-names.svg`.

No new almanac page is created, and no original source imagery is redistributed.
The source review/diagram can be registered in the next lossless index build.
Identity/measurement admission and review of the remaining source entries are
separate pending steps. The full core-data objective remains active.

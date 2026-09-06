---
skill: discover-websearch
topic: ocean-state-projection-candidates
date: 2026-08-29
claims_checked: 4
confirmed: 4
---

# Ocean-state projection candidates

## Phase 1 — claims to ground

| # | Claim | Source | Why it matters |
|---|---|---|---|
| 1 | Equal Earth is a sound area-honest global reference for the 56 states. | OSW prior | Province footprint comparisons must not silently distort area. |
| 2 | Interrupted Mollweide Oceanic deserves a direct OSW prototype. | Candidate | It may enlarge ocean pieces while putting discontinuities over land. |
| 3 | Spilhaus remains the strongest one-ocean continuity view but is not the sole state-map answer. | OSW prior | Continuity and state recognition are different map tasks. |
| 4 | Oblique Cylindrical Equal Area is a plausible new experimental strip view. | Candidate | A rotated great-circle axis may expose a long ocean corridor with honest area. |

## Phase 2 — web evidence

### Claim 1 — Equal Earth

- Query: `site:proj.org Equal Earth projection equal area world map`
  - Source: https://proj.org/en/stable/operations/projections/eqearth.html
  - Direct quote: “The Equal Earth projection is intended for making world maps.”
  - Relevance: PROJ documents global scope and retained relative area.
- Query: `Equal Earth map projection 2018 Savric Patterson Jenny paper equal area`
  - Source: https://doi.org/10.1080/13658816.2018.1504949
  - Direct quote: “a new equal-area pseudocylindrical projection for world maps.”
  - Relevance: The authors' paper confirms purpose and area property.
- Verdict: CONFIRMED.

### Claim 2 — Interrupted Mollweide Oceanic

- Query: `Interrupted Mollweide Oceanic View PROJ documentation equal area oceans`
  - Source: https://proj.org/en/stable/operations/projections/imoll_o.html
  - Direct quote: “an equal-area projection intended for making maps of the Earth's oceans.”
  - Relevance: This is exactly OSW's subject and preserves area.
- Query: `USGS map projections working manual interrupted Mollweide oceanic view`
  - Source: https://www.usgs.gov/media/files/map-projections-a-working-manual
  - Direct quote: “Map projections - A working manual.pdf”
  - Relevance: USGS provides the canonical projection reference; PROJ supplies the oceanic implementation details.
- Verdict: CONFIRMED.

### Claim 3 — Spilhaus

- Query: `Spilhaus projection ocean map research paper 2023`
  - Source: https://doi.org/10.1038/s41597-023-02309-6
  - Direct quote: “emphasizes the seamless connection of water masses surrounded by continents.”
  - Relevance: Peer-reviewed evidence supports the one-ocean reading.
- Query: `Spilhaus projection Woods Hole 1942 ocean continuity`
  - Source: https://www.whoi.edu/oceanus/feature/spilhaus-projection/
  - Direct quote: “the world ocean is a continuous body of water”
  - Relevance: WHOI connects the design to Spilhaus's original oceanographic purpose.
- Verdict: CONFIRMED.

### Claim 4 — Oblique Cylindrical Equal Area

- Query: `site:proj.org ocea oblique cylindrical equal area documentation rotation pole`
  - Source: https://proj.org/en/stable/operations/projections/ocea.html
  - Direct quote: “For the Oblique Cylindrical Equal Area projection a pole of rotation is needed.”
  - Relevance: PROJ supports a configurable global, equal-area oblique axis.
- Query: `USGS oblique cylindrical equal area chosen central line great circle`
  - Source: https://pubs.usgs.gov/pp/1395/report.pdf
  - Direct quote: “scale is true along chosen central line, an oblique great circle”
  - Relevance: A selected ocean great circle can become the low-distortion organizing line.
- Verdict: CONFIRMED as a prototype candidate, not yet as a preferred OSW projection.

## Phase 3 — findings

1. Equal Earth is global.
2. Equal Earth is equal-area.
3. Equal Earth permits a chosen central meridian.
4. Its familiar world silhouette makes it the clearest geographic reference.
5. Interrupted Mollweide Oceanic is explicitly designed for ocean maps.
6. It is equal-area.
7. It uses six Mollweide regions.
8. Its documented recommended center is 160°W.
9. It gains continuity at the cost of greater equatorial distortion.
10. Spilhaus makes the world ocean visually continuous.
11. Spilhaus has demonstrated use with ocean-science datasets.
12. Its unfamiliar distortion makes it a complementary view, not the sole directory map.
13. Oblique Cylindrical Equal Area is global and equal-area.
14. Its rotational pole is configurable.
15. Its low-distortion central line can follow an oblique great circle.
16. OSW should test the chosen axis empirically because no source validates a specific OSW axis.

| Claim | Evidence summary | Verdict | Primary source |
|---|---|---|---|
| Equal Earth reference | Global equal-area world projection | CONFIRMED | https://doi.org/10.1080/13658816.2018.1504949 |
| Interrupted Mollweide Oceanic | Ocean-emphasis equal-area lobed projection | CONFIRMED | https://proj.org/en/stable/operations/projections/imoll_o.html |
| Spilhaus continuity | Makes water-mass connection visually continuous | CONFIRMED | https://doi.org/10.1038/s41597-023-02309-6 |
| Oblique CEA experiment | Configurable global equal-area oblique axis | CONFIRMED FOR PROTOTYPE | https://proj.org/en/stable/operations/projections/ocea.html |

Summary: four of four claims grounded. No claims contradicted.

## Phase 4 — ungrounded claims

No fully ungrounded claims. The best rotational axis for an OSW Oblique
Cylindrical Equal Area map remains unconfirmed and must be selected through a
visual bakeoff rather than asserted from literature.

## Phase 5 — amend

1. Prototype several Oblique CEA axes through the Pacific, Atlantic, and ACC rather than choosing one rhetorically.
2. Compare all candidates with identical 56-state geometry, labels, land treatment, and line hierarchy.
3. Score state-label room, ocean cuts, basin continuity, area integrity, and polar legibility separately.

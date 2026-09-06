---
skill: discover-websearch
topic: sea ice polynyas and ocean cavities
date: 2026-09-05
claims_checked: 5
confirmed: 5
---

# Web grounding — sea ice, polynyas, and ocean cavities

## Claims to ground

| # | Claim | Source of claim | Why it matters |
|---|---|---|---|
| 1 | Sea-ice concentration, area, extent, thickness, volume, and edge are non-interchangeable measurements or objects. | OSW classification need | A surface map can otherwise overclaim ice amount and geometry. |
| 2 | Leads and polynyas are both openings in ice cover but differ in geometry, persistence, and formation. | OSW classification need | They should not share one detection rule. |
| 3 | Sea ice, fast ice, pack ice, ice shelves, grounding lines, and cavities name physically different things. | OSW classification need | Their origins, motion, boundaries, and sea-level implications differ. |
| 4 | Freezing, brine rejection, melting, and freshening transform adjacent seawater but do not prescribe one universal circulation response. | Mechanism claim | OSW must not turn a local process into deterministic overturning. |
| 5 | Ice-shelf basal melt depends on ocean access, circulation, mixing, boundary layers, and geometry; surface sea-ice state alone is insufficient. | Heat-delivery claim | This controls what OSW may infer from its present ice fields. |

## Evidence by claim

### Claim 1 — cover metrics are not interchangeable

- Query: `site:nsidc.org sea ice concentration extent thickness definition ice edge`
  - Source: <https://nsidc.org/learn/parts-cryosphere/sea-ice/quick-facts-about-sea-ice>
  - Direct quote: “Extent is always a larger number than area.”
  - Relevance: area weights concentration while extent counts thresholded cells.
- Query: `site:noaa.gov sea ice concentration extent thickness definition`
  - Source: <https://arctic.noaa.gov/report-card/report-card-2024/sea-ice-2024/>
  - Direct quote: “ice of at least 15% concentration”
  - Relevance: the common extent boundary is an explicit threshold.

**Verdict: CONFIRMED.**

### Claim 2 — leads and polynyas need separate tests

- Query: `site:nsidc.org polynya lead sea ice difference definition`
  - Source: <https://nsidc.org/learn/parts-cryosphere/sea-ice/science-sea-ice>
  - Direct quote: “Leads are narrow, linear features”
  - Relevance: geometry and short refreezing time distinguish leads.
- Query: `WMO sea ice nomenclature lead polynya definition`
  - Source: <https://nsidc.org/sites/default/files/documents/technical-reference/wmo_nomenclature_draft_version1-0.pdf>
  - Direct quote: “A stable ice-free water space”
  - Relevance: the governed nomenclature makes persistence part of polynya identity.

**Verdict: CONFIRMED.**

### Claim 3 — ice phases and cavity boundaries differ

- Query: `site:nsidc.org ice shelf floating ice grounded ice sea ice difference cavity ocean`
  - Source: <https://nsidc.org/learn/parts-cryosphere/sea-ice/quick-facts-about-sea-ice>
  - Direct quote: “Sea ice is frozen ocean water.”
  - Relevance: origin distinguishes it from land-origin glacier ice.
- Query: `site:nsidc.org ice shelf floating tongue grounded line`
  - Source: <https://nsidc.org/learn/parts-cryosphere/ice-shelves/quick-facts-about-ice-shelves>
  - Direct quote: “floating tongues of ice”
  - Relevance: an ice shelf is floating glacial structure, not sea-ice cover.

**Verdict: CONFIRMED.**

### Claim 4 — phase change alters water but response depends on context

- Query: `site:nsidc.org sea ice brine rejection salt ocean circulation`
  - Source: <https://nsidc.org/learn/parts-cryosphere/sea-ice/science-sea-ice>
  - Direct quote: “Salinity of near-surface water then rises.”
  - Relevance: freezing excludes much salt into the ocean.
- Query: `site:noaa.gov sea ice formation brine rejection density convection`
  - Source: <https://repository.library.noaa.gov/view/noaa/9516/noaa_9516_DS1.pdf>
  - Direct quote: “unlikely to overcome the local stratification”
  - Relevance: brine rejection does not guarantee deep convection everywhere.

**Verdict: CONFIRMED.**

### Claim 5 — basal heat delivery is a cavity budget, not a surface proxy

- Query: `ice shelf cavity ocean circulation basal melt heat transport review Antarctica`
  - Source: <https://www.annualreviews.org/content/journals/10.1146/annurev-marine-040323-074354>
  - Direct quote: “Ocean heat must cross many physical and dynamical barriers”
  - Relevance: the final ice–ocean boundary layer is only one part of delivery.
- Query: `ocean heat transport ice shelf cavity observations basal melt`
  - Source: <https://pmc.ncbi.nlm.nih.gov/articles/PMC5161426/>
  - Direct quote: “heat transport into and out of the cavity”
  - Relevance: Totten observations frame melting with a cavity heat budget.

**Verdict: CONFIRMED.**

## Findings table

| # | Claim | Evidence summary | Verdict | Source |
|---|---|---|---|---|
| 1 | Concentration is fractional cover | Satellite cells contain a fractional sea-ice-area estimate. | CONFIRMED | <https://nsidc.org/sipn/snapshot-arctic> |
| 2 | Extent is thresholded | NSIDC commonly counts cells at or above 15% concentration. | CONFIRMED | <https://nsidc.org/learn/parts-cryosphere/sea-ice/quick-facts-about-sea-ice> |
| 3 | Area differs from extent | Area weights fractional cover while extent counts full qualifying cells. | CONFIRMED | <https://nsidc.org/learn/ask-scientist/what-difference-between-sea-ice-area-and-extent> |
| 4 | Edge location has resolution uncertainty | Passive-microwave ice edge may differ by 25–50 km from higher-resolution systems. | CONFIRMED | <https://nsidc.org/sea-ice-today/about-data> |
| 5 | Thickness is separate | Extent observations are generally more complete than thickness observations. | CONFIRMED | <https://nsidc.org/learn/parts-cryosphere/sea-ice/quick-facts-about-sea-ice> |
| 6 | Leads are linear fractures | WMO nomenclature defines elongated cracks with explicit geometry. | CONFIRMED | <https://nsidc.org/sites/default/files/documents/technical-reference/wmo_nomenclature_draft_version1-0.pdf> |
| 7 | Polynyas are persistent openings | Winds or ocean heat sustain open water where ice is expected. | CONFIRMED | <https://nsidc.org/learn/cryosphere-glossary/polynya> |
| 8 | Lead and polynya forcing differs | Leads arise from ice motion; polynyas may involve winds or ocean heat. | CONFIRMED | <https://nsidc.org/learn/parts-cryosphere/sea-ice/science-sea-ice> |
| 9 | Sea ice is ocean-origin ice | It forms, grows, and melts in the ocean. | CONFIRMED | <https://nsidc.org/learn/parts-cryosphere/sea-ice/quick-facts-about-sea-ice> |
| 10 | Ice shelves float but originate from land ice | Grounded glaciers feed floating shelves. | CONFIRMED | <https://nsidc.org/learn/parts-cryosphere/ice-shelves/quick-facts-about-ice-shelves> |
| 11 | Grounding line is a boundary | It separates grounded ice from an adjoining floating shelf or tongue. | CONFIRMED | <https://www.sciencedirect.com/science/article/abs/pii/S0012825219300832> |
| 12 | Brine rejection raises density | Salt expelled during ice growth increases near-surface salinity and density. | CONFIRMED | <https://nsidc.org/learn/parts-cryosphere/sea-ice/science-sea-ice> |
| 13 | Deep response is conditional | Background stratification can prevent brine-driven deep convection. | CONFIRMED | <https://repository.library.noaa.gov/view/noaa/9516/noaa_9516_DS1.pdf> |
| 14 | Cavities contain structured circulation | Ross observations resolve boundary layers, mixing, and interleaving below the shelf. | CONFIRMED | <https://pmc.ncbi.nlm.nih.gov/articles/PMC7382223/> |
| 15 | Geometry controls heat access | Ridge height and roof clearance regulate warm-water inflow and melt. | CONFIRMED | <https://www.bas.ac.uk/data/our-data/publication/geometric-and-oceanographic-controls-on-melting-beneath-pine-island-glacier/> |
| 16 | Basal melt is a boundary-layer problem | Heat delivery and turbulent exchange both matter at the ice base. | CONFIRMED | <https://www.annualreviews.org/content/journals/10.1146/annurev-marine-040323-074354> |
| 17 | Cavity transport can be measured | Totten observations use inflow/outflow heat transport to constrain melt support. | CONFIRMED | <https://pmc.ncbi.nlm.nih.gov/articles/PMC5161426/> |

Summary: 5 of 5 claims confirmed; none contradicted or unconfirmed.

## Ungrounded claims

No ungrounded claims. This record does not establish global detections or exact
external vocabulary identifiers.

## Classification amendments

1. Keep cover fraction, area, extent, thickness, and volume as declared
   measurements; do not turn each statistic into a material object.
2. Add floe, fast ice, pack ice, lead, ice shelf, and grounding line because
   each changes geometry, mobility, or origin.
3. Add brine rejection and basal melting as processes, not cover objects.
4. Keep the cavity as a liquid-ocean volume whose roof is an ice shelf and whose
   entrances, internal circulation, mixing, and boundary exchange require
   separate evidence.

## Search improvements

1. Future implementation searches should use product names and exact variable
   identifiers rather than generic cryosphere terms.
2. Add operational ice-chart and in-situ thickness sources before a map layer.
3. Seek regional cavity studies for each proposed Antarctic case; no single
   warm/cold-cavity rule should be universalized.


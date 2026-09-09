---
skill: discover-websearch
topic: ocean-object-classification
date: 2026-09-05
claims_checked: 5
confirmed: 5
---

# Web grounding — ocean-object classification

## Claims to ground

| # | Claim | Source of claim | Why it matters |
|---|---|---|---|
| 1 | One flat hierarchy cannot faithfully classify ocean places, fields, structures, processes, and events. | OSW guide synthesis | A false tree would force incompatible concepts into sibling boxes. |
| 2 | A useful object record needs orthogonal facets such as geometry, relation, variable, method, scale, and time. | OSW object-card proposal | These become the machine-readable schema. |
| 3 | Seafloor and named-water geography are separate object families from moving fluid structures. | Guide coverage audit | OSW currently under-teaches the fixed boundary conditions. |
| 4 | Waves, tides, sea ice, vertical motions, and plumes are major missing families. | Guide coverage audit | “Ocean objects” cannot mean only heat and horizontal circulation. |
| 5 | OSW should map its public vocabulary to existing standards rather than claim a new scientific canon. | Repository positioning | Interoperability and honest novelty depend on this boundary. |

## Web evidence

### Claim 1 — a flat hierarchy is insufficient

- Query: `CF standard names ocean variables vocabulary facets`
  - Source: [CF Standard Name FAQ](https://cfconventions.org/faq.html)
  - Direct quote: “Common characteristics, or facets, include ... medium or realm ... transformation ... substance ... state ... quantity being measured.”
  - Relevance: a mature scientific vocabulary composes several facets instead of assigning every concept one taxonomic parent.
- Query: `INSPIRE ocean geographic feature sea region ocean feature`
  - Source: [INSPIRE Sea Regions specification](https://inspire-mif.github.io/technical-guidelines/data/sr/dataspecification_sr.html)
  - Direct quote: “An Ocean Feature such as 'temperature' or 'tidal currents' ... can define a Sea Region.”
  - Relevance: a measured phenomenon and a derived geographic region are different but related records.
- Query: `GOOS essential ocean variables physical biogeochemical biological`
  - Source: [GOOS Essential Ocean Variables](https://goosocean.org/what-we-do/framework/essential-ocean-variables/)
  - Direct quote: “The columns indicate the GOOS Expert Panel that has lead responsibility for each EOV.”
  - Relevance: operational ocean observing organizes variables by domain and use, not by a universal object tree.
- Verdict: **CONFIRMED**

### Claim 2 — classification should be faceted

- Query: `Marine Regions gazetteer ontology contains adjacent geometry`
  - Source: [Marine Regions Gazetteer Ontology](https://marineregions.org/ontology/documentation.html)
  - Direct quote: “Object Properties ... Contains ... Has geometry ... Is adjacent to ... Is part of.”
  - Relevance: ocean places require explicit spatial and hierarchical relations.
- Query: `satellite ocean phenomenon ontology coverage spatial resolution lineage`
  - Source: [SeMaRe ocean-phenomena ontology](https://www.mdpi.com/2078-2489/12/8/321)
  - Direct quote: “Phenomena ... had the following properties: Category ... Coverage.”
  - Relevance: detected phenomena need class, geometry, provenance, resolution, and time-bearing image context.
- Query: `CF standard name unique canonical units description`
  - Source: [CF Standard Name FAQ](https://cfconventions.org/faq.html)
  - Direct quote: “Several attributes are required for every standard name: the canonical units ... and the description.”
  - Relevance: identity alone is insufficient without semantic and measurement attributes.
- Verdict: **CONFIRMED**

### Claim 3 — fixed geography differs from fluid structure

- Query: `GEBCO undersea feature gazetteer generic feature type geographic position`
  - Source: [GEBCO Undersea Feature Names](https://www.gebco.net/data-products/undersea-feature-names)
  - Direct quote: “names, generic feature type and geographic position of features on the seafloor.”
  - Relevance: the seafloor already has an authoritative feature-oriented gazetteer.
- Query: `IHO S-101 seabed area point curve surface`
  - Source: [IHO S-101 DCEG](https://iho.int/uploads/user/Services%20and%20Standards/S-100WG/S-101PT12/S-101PT12_2024_05.1AB_EN_S-101_Annex_%20A_DCEG_Edition_2.0.0.20240211_Clean_V1.pdf)
  - Direct quote: “SEABED AREA. A region of the seabed including the material ... and its physical characteristics.”
  - Relevance: navigational feature catalogues treat seabed objects as geometry plus attributes.
- Query: `USGS seafloor terrain hierarchical decision tree classification`
  - Source: [Dartnell and Gardner 2009](https://pubs.usgs.gov/publication/70035266)
  - Direct quote: “analyzed in a hierarchical, decision-tree classification to delineate six seafloor provinces.”
  - Relevance: fixed terrain can support a real hierarchy even when fluid objects cannot share it.
- Verdict: **CONFIRMED**

### Claim 4 — major families remain missing

- Query: `GOOS EOV sea state sea ice surface currents`
  - Source: [GOOS Essential Ocean Variables](https://goosocean.org/what-we-do/framework/essential-ocean-variables/)
  - Direct quote: “Sea state ... Sea ice ... Surface currents ... Subsurface currents.”
  - Relevance: the observing framework treats these as distinct essential phenomena.
- Query: `NOAA waves transmit energy not water tides long waves`
  - Source: [NOAA: Why does the ocean have waves?](https://oceanservice.noaa.gov/facts/wavesinocean.html)
  - Direct quote: “Waves transmit energy, not water, across the ocean.”
  - Relevance: waves cannot be classified merely as currents or water masses.
- Query: `NOAA upwelling deep cold water rises hydrothermal plume signature`
  - Sources: [NOAA upwelling](https://oceanservice.noaa.gov/facts/upwelling.html), [NOAA hydrothermal plumes](https://www.pmel.noaa.gov/eoi/PlumeStudies/plumes-whatis.html)
  - Direct quotes: “deep, cold water rises toward the surface”; “distinctly different physical and chemical signature.”
  - Relevance: vertical-motion processes and source-tagged material plumes require different identity tests.
- Verdict: **CONFIRMED**

### Claim 5 — map to standards, do not replace them

- Query: `NERC Vocabulary Server marine controlled vocabularies interoperability reuse`
  - Source: [NERC Vocabulary Server](https://vocab.nerc.ac.uk/)
  - Direct quote: “Standardised controlled vocabularies ... enabling greater interoperability and reuse.”
  - Relevance: OSW terms should carry external mappings where suitable.
- Query: `SeaVoX water body gazetteer named regions hierarchy`
  - Source: [SeaVoX vocabulary governance](https://www.bodc.ac.uk/resources/vocabularies/seavox/)
  - Direct quote: “over 220 named regions, for example, oceans and seas.”
  - Relevance: OSW should reuse named-water identifiers instead of rebuilding a gazetteer.
- Query: `digital twins ocean semantic interoperability standards`
  - Source: [IHO: Digital Twins of the Ocean](https://ihr.iho.int/wp-content/uploads/2023/04/IHR_29-1.pdf)
  - Direct quote: “semantic interoperability is critical for ensuring that data from different sources can be integrated.”
  - Relevance: a future atlas needs crosswalks, stable identifiers, and provenance.
- Verdict: **CONFIRMED**

## Findings table

| # | Finding | Verdict | Source |
|---|---|---|---|
| 1 | Scientific variable names already compose multiple semantic facets. | CONFIRMED | [CF](https://cfconventions.org/faq.html) |
| 2 | A phenomenon can define a region without becoming identical to that region. | CONFIRMED | [INSPIRE](https://inspire-mif.github.io/technical-guidelines/data/sr/dataspecification_sr.html) |
| 3 | Observing systems group variables by physical, biogeochemical, and ecosystem domains. | CONFIRMED | [GOOS](https://goosocean.org/what-we-do/framework/essential-ocean-variables/) |
| 4 | Marine-place ontologies encode containment, adjacency, geometry, and hierarchy separately. | CONFIRMED | [Marine Regions](https://marineregions.org/ontology/documentation.html) |
| 5 | Detected phenomena need coverage, resolution, and lineage metadata. | CONFIRMED | [SeMaRe](https://www.mdpi.com/2078-2489/12/8/321) |
| 6 | Standard variables pair identity with description and canonical units. | CONFIRMED | [CF](https://cfconventions.org/faq.html) |
| 7 | GEBCO separates undersea names, feature types, and positions. | CONFIRMED | [GEBCO](https://www.gebco.net/data-products/undersea-feature-names) |
| 8 | Hydrographic catalogues permit point, curve, and surface feature geometry. | CONFIRMED | [IHO S-101](https://iho.int/uploads/user/Services%20and%20Standards/S-100WG/S-101PT12/S-101PT12_2024_05.1AB_EN_S-101_Annex_%20A_DCEG_Edition_2.0.0.20240211_Clean_V1.pdf) |
| 9 | Seafloor provinces can be derived through explicit terrain decision rules. | CONFIRMED | [USGS](https://pubs.usgs.gov/publication/70035266) |
| 10 | GOOS treats sea state, sea ice, and currents as distinct observing targets. | CONFIRMED | [GOOS](https://goosocean.org/what-we-do/framework/essential-ocean-variables/) |
| 11 | Waves primarily transmit energy and are not equivalent to bulk advection. | CONFIRMED | [NOAA](https://oceanservice.noaa.gov/facts/wavesinocean.html) |
| 12 | Upwelling and plumes require vertical-motion and source/signature tests. | CONFIRMED | [NOAA](https://oceanservice.noaa.gov/facts/upwelling.html) |
| 13 | Marine vocabularies provide stable, machine-readable identifiers. | CONFIRMED | [NVS](https://vocab.nerc.ac.uk/) |
| 14 | A governed water-body gazetteer already covers hundreds of named regions. | CONFIRMED | [SeaVoX](https://www.bodc.ac.uk/resources/vocabularies/seavox/) |
| 15 | Digital-ocean interoperability depends on shared semantics. | CONFIRMED | [IHO](https://ihr.iho.int/wp-content/uploads/2023/04/IHR_29-1.pdf) |

Summary: **5 of 5 claims confirmed; 0 contradicted; 0 unconfirmed.**

## Ungrounded claims

No ungrounded claims. The evidence does **not** establish that OSW's proposed
faceted arrangement is unique or first; no priority claim should be made.

## Amendments

1. Use an orthogonal type × identity-test matrix rather than one “kingdom to
   species” hierarchy.
2. Add fixed substrate, oscillation, phase/interface, vertical-motion, and plume
   coverage before calling the guide collection broad.
3. Give every OSW term a future `external_match` field for CF, NVS, Marine
   Regions, GEBCO/IHO, or another governed vocabulary; use `none` honestly when
   OSW is introducing only a local teaching label.

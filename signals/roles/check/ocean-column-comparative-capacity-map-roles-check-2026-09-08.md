---
skill: roles-check
topic: ocean-column-comparative-capacity-map
date: 2026-09-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook, orbit]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — Ocean Column comparative-capacity map

**Artifact type:** interactive scientific cartography, quantitative ranking,
selected-feature passport, and public documentation

**Source commit:** `d409264`

**Reviewed artifact SHA-256:**

- browser logic: `F2FF3A93F94A12BA2DFB5FDD188D5E58F9DAFF51914E84D855BF7B2FA557665F`
- browser HTML: `82A60366B2BD560162776DD172F85AB7282E55C3333C308100F1E32A6283AEC6`
- viewer tests: `52CF411D8E1DD6394201F38038E80AA9060E758EEB7A10E795124B3F30D7CE78`
- scientific tests: `084E9F304DF233CE205F0F0B250FAD800C28A0AE9E92499100DBBEA94AFAED75`
- workbench method: `6CB0352A14617CF661CA7D1764BEC677DE3CDB92382459D6522D3AF5C05EBBEB`
- address guide: `85E1227E1DF1CAC6AA6D8F679C42623AD44021185AE4B8FAF65D6EAE68ECD3A9`

## Role selection

All eight OSW roles apply. The artifact maps a scientific derivation, makes
relative comparisons visually prominent, adds four interactive modes, and
must remain legible and reproducible without turning geometric capacity into a
mechanism or planetary analogy.

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Wet area, water volume, and mean depth measure geometry, not heat content, transport, residence, productivity, or climatic influence. | P2 | Map interpretation | Call the fields comparative capacity and place the non-equivalence in viewer and guide copy. **Resolved.** |
| 2 | A province can rank highly by area but differently by volume because bathymetry changes its mean depth. | P2 | Comparative grammar | Keep area, volume, and depth as independently selectable fields rather than one composite score. **Resolved.** |
| 3 | Static ecological boundaries remain indexing geometry despite the new quantitative fills. | P3 | Scientific boundary | Keep currents, heat, and dynamic water structures as separate future overlays. **Accepted.** |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Every ranking must derive only from the same 54 source-aligned, receipted province summaries. | P2 | Data lineage | Compute ranks at runtime from the committed footprint payload; do not introduce duplicated rank constants. **Resolved.** |
| 2 | Rounded source metrics could create arbitrary tie order. | P2 | Rank method | Assert all three displayed metrics are present, positive, and unique at the committed precision. **Resolved.** |
| 3 | Global shares inherit the cell-center, coastline, seam, and GEBCO limitations of D53. | P3 | Passport | Keep “sampled” in metric names and retain the adjacent evidence boundary. **Accepted.** |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A continuous ramp would imply more precision than the 0.25° source screen warrants. | P2 | Quantitative palette | Use five explicit rank classes of 11/11/11/11/10 provinces. **Resolved.** |
| 2 | “High” means largest for area/volume but deepest for mean depth. | P2 | Legend semantics | Put “largest first” or “deepest first” in the live map-field title. **Resolved.** |
| 3 | Selected state and quantitative class must remain simultaneously readable. | P3 | Selection mark | Preserve the class fill and use a gold boundary for selection; retain cyan selection in the non-quantitative family mode. **Resolved.** |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Readers may equate a top rank with importance. | P2 | Public wording | Say explicitly that rank is geometric capacity, not ecological importance or heat influence. **Resolved.** |
| 2 | Three percentages without denominators would be ambiguous. | P2 | Passport | Label ranks “of 54” and identify area share, volume share, and deepest rank separately. **Resolved.** |
| 3 | The main discovery is the divergence among “large,” “voluminous,” and “deep,” not a winner list. | P3 | Narrative | Frame the map as comparison among different geometric questions. **Resolved.** |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Four map fields cannot depend on palette recognition. | P2 | Equivalent access | Expose native buttons, pressed state, a live field label, textual rank legend, canvas description, and exact passport. **Resolved.** |
| 2 | The selected province needs a non-color identity in quantitative modes. | P2 | Selection | Label the gold edge in the legend and report the selected code/name in the text summary. **Resolved.** |
| 3 | Added controls and three passport cards must reflow on a narrow screen. | P3 | Responsive layout | Wrap controls, stack passport cards below 700 px, and inspect a 390 px Edge rendering. **Resolved.** |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A missing or malformed comparative metric could silently collapse provinces into the last color class. | P2 | Validation | Assert complete positive metrics, 54 unique values, and expected leaders for each field. **Resolved.** |
| 2 | Every new map mode needs browser-code syntax and interface-contract coverage. | P2 | Tests | Check all mode controls, legend/passport containers, rank functions, and URL-state tokens; run `node --check`. **Resolved.** |
| 3 | Rank computation is deterministic because it uses committed rounded fields with no ties. | P3 | Reproducibility | Keep those uniqueness assertions if source regeneration changes values. **Accepted.** |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The repository must say what the new fields admit and what rank does not mean. | P2 | Project record | Align README, roadmap, D53, method, guide, and history. **Resolved.** |
| 2 | Visual approval needs both desktop and narrow evidence before commit. | P2 | Review gate | Inspect Edge at 1440 px and 390 px with the volume field active. **Resolved.** |
| 3 | This is a private-preview increment, not public release authorization. | P3 | Publication state | Commit locally only and retain the existing release boundary. **Accepted.** |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Earth seafloor-derived capacity ranks have no direct meaning for a gas giant lacking the same lower boundary. | P2 | Planetary scope | Keep the mapped rankings Earth-only. **Resolved.** |
| 2 | A deep Earth province and a deep atmospheric jet are not comparable objects or coordinates. | P2 | Analogy boundary | Require pressure/mass coordinates and dynamic evidence before any later comparison. **Accepted.** |
| 3 | Ranked-class cartography may transfer as a display method only after the compared gas-giant property is independently defined. | P3 | Method transfer | Transfer visual grammar, not present values, boundaries, or physical interpretation. **Accepted.** |

## Synthesis

Roles reviewed: 8

P1 blockers: 0 | P2 issues: 16 | P3 notes: 8

**Verdict: APPROVED-WITH-CONDITIONS**

**Top finding:** Rank must remain a transparent comparison of one declared
geometric measure and must never become an importance score.

**Cross-role consensus:** CURRENT, CHART, BEACON, and HARBOR agree that the
three quantitative questions need distinct mode labels, coarse classes, exact
selected-state text, and a persistent evidence boundary.

## Amendments

1. Use separate area, volume, and mean-depth fields with no composite score.
   **Applied in the map controls and runtime rank model.**
2. Make rank semantics and selection recoverable without color.
   **Applied in live titles, legends, passport cards, and canvas text.**
3. Prevent missing values, ties, and changed leaders from passing silently.
   **Applied in scientific-data and interface-contract tests.**

The comparative-capacity map may be committed to the private-preview branch
after the full offline suite. The open 54/56 edition decision and all dynamic
importance or mechanism claims remain outside this stage.

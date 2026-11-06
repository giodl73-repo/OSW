---
skill: roles-check
topic: kuroshio-filtered-width
date: 2026-10-18
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Kuroshio filtered width readings

Internal review against baseline `c749116b20acddc9d22dc9732275648222621f94`.
Artifact: source extraction, typed data, Rust validation and shared atlas UI.
The seven selected repository lenses cover oceanography, provenance,
visualization, explanation, accessibility, engineering and publication. ORBIT
does not apply. This is not independent oceanographic peer review.

| Role | Finding | Severity | Evidence and recommendation |
|---|---|---|---|
| CURRENT | Filtered regional means cannot establish whole-current boundaries. | P3 | No inventory width, geographic edge or animation admission. Preserve this limit. |
| CURRENT | Month labels could imply independent raw observations. | P2, resolved | Calendar fields remain null; explicit plot labels, filter and source-year axes distinguish graphical readings. |
| CURRENT | Grid interpolation and geostrophic scope constrain interpretation. | P2, resolved | Report, figure and scene retain original1/3° grid,0.1° interpolation and ageostrophic exclusion. |
| SOUNDER | Filter kernel and alignment are unspecified. | P3 | Preserve unknowns; do not reproduce a guessed filter or infer exact dates. |
| SOUNDER | Native vector stroke gap must not become invented source data. | P2, resolved | Operator records the break, adds no segment, and all192targets lie in intact segments; synthetic gap tests pass. |
| SOUNDER | Graphic precision is not measurement uncertainty. | P3 | ±5km and ±0.05plot-years explicitly describe reading allowances. Keep source uncertainty unknown. |
| CHART | Connecting sampled readings could obscure source gaps. | P3 | Unconnected marks, whiskers and numeric matrix retain extraction scope; no invented time interpolation. |
| CHART | Value extrema could look like an annual envelope. | P3 | Figure says sampled filtered curve positions; no annual physical range is supplied. |
| CHART | Full data must remain visible beyond a selected year. | P3 | Complete192point figure and all-row query accompany the16-year table selector. |
| BEACON | More rows do not mean more observations. | P3 | Header and method text say192plot readings; retain that wording beside counts. |
| BEACON | Filtered series could replace existing seasonal evidence. | P3 | Original3prose means and64spatial samples remain unchanged and separate. |
| BEACON | Readers need a short route to evidence. | P3 | Per-reading inspector, three source documents, DOI and full-size SVG links are tested. |
| HARBOR | Hover alone cannot expose reading detail. | P2, resolved | Semantic year selector, keyboard SVG inspection and named per-row inspection controls pass actual-browser checks. |
| HARBOR | Dense table must work at320px. | P3 | Labeled focusable horizontal scroll region and ArrowRight test pass without document overflow. |
| HARBOR | Color cannot convey the only numeric meaning. | P3 | Annotated cells, complete numeric tables, figure description and static rendering provide alternatives. |
| KEEL | Rehashed or coherently altered data must fail. | P3 | Eight native/actual-WASM corruptions include source/operator/figure changes, missing rows, false dates and inventory promotion. |
| KEEL | Existing data must not change incidentally. | P3 | All271old rows and239other owners match baseline; dates, geometry and inventory counts remain unchanged. |
| KEEL | Predecessor full pass does not cover this batch. | P2, open | Preserve1741tests/1159subtests c749pass. Require a complete clean successor before main release. |
| LOGBOOK | Gap work must remain in the continuing draft. | P3 | Same branch and PR83; no separate PR or main merge. |
| LOGBOOK | Source graphics are not licensed for assumed redistribution. | P3 | Retained original stays ignored; only derived readings and original OSW figures are published. |
| LOGBOOK | Working hashes alone do not certify Git bytes. | P2, open | Verify committed102engine/180research/353index pins before pushing and record the successor gate separately. |

Roles reviewed:7. P1:0. P2:7 (five resolved, two open). P3:14.
**APPROVED-WITH-CONDITIONS for derived research publication.** Main release
requires the complete latest gate; no additional physical-width admission is
approved. CURRENT and BEACON agree on filtered versus raw observations;
SOUNDER and CHART agree on retaining source gaps and graphical allowances.

Applied amendments: explicit native stroke-break retention; original-grid and
ageostrophic metadata beside the figure; accessible individual inspection
labels. Focused10tests/3subtests,66Rust tests, actual browser parity/accessibility
and preservation gates pass. Final source figure has been visually inspected.

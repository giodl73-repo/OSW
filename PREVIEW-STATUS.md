# Atlas 08–10 review-branch status

Atlas 08–10 are now visible on the pushed `atlas-08-private-preview` review
branch. They have not replaced the released Atlas 07 on `main` or GitHub Pages
and are not represented as a new version in `CITATION.cff`. The branch name and
older review records preserve the original private-preview stage; they do not
describe its current GitHub visibility.

Atlas 09 is the current native-role-approved working draft on top of that
approved review preview. It adds one fixed Scripps RG Argo pressure-layer
anomaly. Owner visual approval and any public promotion remain open.

Atlas 10 is the current native-role-approved working draft. It extends that
exact monthly source into a four-level 10/300/700/1000 dbar anomaly ladder.
Owner visual approval and public promotion remain open.

## Reviewed components

| Component | Reviewed source commit | Native verdict | Review |
|---|---|---|---|
| Ocean-first conceptual map and interactive integration | `762a7de` | APPROVED for review preview | [fluid-geography review](signals/roles/check/ocean-first-fluid-geography-roles-check-2026-08-28.md) |
| Researcher-facing claims and data receipt | `c57e5a6` | APPROVED for review preview | [evidence-note review](signals/roles/check/researcher-evidence-note-roles-check-2026-08-28.md) |
| Claim-level fifteen-source literature spine | `a93999f` | APPROVED for review preview | [literature-spine review](signals/roles/check/claim-level-literature-spine-roles-check-2026-08-28.md) |
| Machine-readable zone and claims exports | `7d673df` | APPROVED for review preview | [research-export review](signals/roles/check/machine-readable-research-exports-roles-check-2026-08-28.md) |
| Atlas 09 RG Argo 700 dbar anomaly | `ef6662e` | APPROVED by native roles; owner visual review open | [Atlas 09 depth review](signals/roles/check/atlas-09-argo-700dbar-roles-check-2026-08-28.md) |
| Atlas 10 RG Argo depth ladder | `2756f1e` | APPROVED by native roles; owner visual review open | [Atlas 10 depth-ladder review](signals/roles/check/atlas-10-argo-depth-ladder-roles-check-2026-08-28.md) |
| PELAGOS projection laboratory | `92345ec`, `dbe8165` | APPROVED as a review-branch experiment; default-atlas adoption open | [PELAGOS native-role review](signals/roles/check/pelagos-projection-laboratory-roles-check-2026-08-29.md) |
| Equal Earth and HEATPLATES shape atlas | `e91e67a` | APPROVED as additive review-branch experiments | [HEATPLATES native-role review](signals/roles/check/heatplates-shape-atlas-roles-check-2026-08-29.md) |
| Six-lens ocean geography and 36-feature catalog | `aa91cb8` | APPROVED as an additive review-preview expansion | [ocean-geography native-role review](signals/roles/check/ocean-geography-expansion-roles-check-2026-08-29.md) |
| Classic 56-province cartogram, coastline fingerprints, and monochrome continents-as-lakes study | `9df16e7`, `495ec4b`, `2327cec` | APPROVED as additive review-branch experiments; owner visual review open | [initial review](signals/roles/check/province-atlas-cartogram-roles-check-2026-08-29.md) · [coastline review](signals/roles/check/province-atlas-coastline-fingerprints-roles-check-2026-08-29.md) · [lakes review](signals/roles/check/province-atlas-continents-as-lakes-roles-check-2026-08-29.md) |
| Coast-owned 56-state ground, cross-mode integration, and province zoom | `ef5f37a`, `a72074d` | APPROVED for review preview; owner interaction review open | [interactive-ground review](signals/roles/check/interactive-province-atlas-ground-roles-check-2026-08-29.md) |

The review commits that record those verdicts follow their source commits in
Git history. Each approval remains scoped to a review preview and does not
replace external scientific peer review or authorize release promotion.

## Evidence state

- **Unchanged observational layer:** final NOAA/NCEI OISST v2.1 surface
  temperature, anomaly, and estimated-analysis-error fields for 2026-08-01.
- **New reviewed depth layer:** July 2026 Scripps RG Argo potential-
  temperature anomaly at 700 dbar, sampled to a 2-degree display grid. It is
  an objectively mapped anomaly, not absolute temperature or heat content, and
  its 64.5°S limit excludes the Antarctic shelf and ice cavities.
- **New reviewed depth-ladder extension:** same-source anomalies at 10, 300,
  and 1000 dbar, pressure controls, bookmark state, and four-level probe output.
- **New presentation layer:** pinned Natural Earth coastline geometry,
  redesigned conceptual overlays, land-reference and water-first treatments,
  seven basin labels, six selectable ocean-geography lenses, a 36-feature
  catalog with depth/property/clock facets, clearer evidence modes, researcher
  routes, a four-candidate ocean-first
  projection laboratory, and a six-panel HEATPLATES shape directory. PELAGOS
  remains an experimental equal-area aspect, not the default atlas projection;
  HEATPLATES uses panel-specific zoom and cannot compare footprint area. The
  Province Atlas adds an original, non-metric cartogram, 56-row classic
  Longhurst reference directory, and horizontally compressed public-domain
  Natural Earth coastline fingerprints; it is not geographic province-boundary
  data. Experiment 03B removes biome color and masks the compressed continents
  directly out of one neutral province field; its internal pieces remain
  schematic.
- **New common atlas ground:** coast-owned approximate province pieces now
  underlay the six conceptual lenses and all four observed evidence modes.
  Province selection is keyboard accessible, URL-addressable, zoomable, and
  persistent across view changes; this does not create observed province
  boundaries or province-aggregated data.
- **New research handoff:** bounded claims, exact source-response receipts,
  primary-literature mapping, BibTeX, optional review prompts, and CSV exports.
- **Still not present:** depth-integrated heat content, section heat transport,
  bathymetric gate diagnostics, sea-ice coupling, or validated zone boundaries.

## Validation state

Run the default offline checks from the repository root:

```powershell
python -m unittest analysis.test_atlas
node --check atlas/app.js
node --check analysis/export_research_tables.js
node analysis/export_research_tables.js
```

The current export contract contains twelve ordered zones and four bounded
claims. Source refreshes remain explicit network operations and are not part of
the default offline gate.

## Decisions deliberately still open

1. Owner visual approval of the complete review preview.
2. Whether Atlas 08 should replace Atlas 07 on the public site.
3. Whether a promoted release should retain `0.8.x` or receive a new version.
4. Whether Atlas 09's first pressure layer should be promoted after owner
   visual review.
5. Which quantitative layer should follow: absolute vertical structure,
   bathymetry/sea ice, or dynamically consistent heat transport.
6. Whether Atlas 10's pressure ladder should replace the single-level Atlas 09
   preview after owner visual review.
7. Whether PELAGOS should remain a projection study, receive quantitative
   distortion diagnostics, or become an interactive atlas option.
8. Whether HEATPLATES should remain a conceptual shape directory or gain a
   common-scale companion after observed feature boundaries are defined.
9. Whether the Province Atlas should receive owner visual approval, a styled
   HTML directory, and a separately versioned 54-province switch.
10. Whether the interactive coast-owned province ground should replace the old
    conceptual-map ground in a promoted release after owner interaction review.

Until those decisions are made, repository links may expose Atlas 10 on this
review branch while public URLs and citation metadata continue to describe
Atlas 07.

---
skill: roles-check
topic: atlas-09-argo-700dbar
date: 2026-08-28
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook, orbit]
p1_count: 0
verdict: APPROVED
---

# Atlas 09 RG Argo 700 dbar role review

Source commit: `ef6662e` (`Add first depth-resolved Argo layer`)

## Artifact identification

- Type: observational-data pipeline, generated browser artifact, interactive
  cartographic layer, documentation, and CI contract.
- Domain: physical oceanography, Argo data stewardship, cartography,
  accessibility, reproducibility, and repository release state.
- Scope: the July 2026 Scripps RG Argo potential-temperature anomaly at
  700 dbar and the generic-grid changes required to display it.

## Role selection

All eight OCEANLINES roles are selected because this is an atlas increment.
CURRENT owns the physical claim; SOUNDER the RG product receipt; CHART the
pressure-layer rendering; BEACON the public explanation; HARBOR the non-color
and keyboard paths; KEEL the generator and gates; LOGBOOK the private/public
state; and ORBIT checks that the Earth-side depth layer does not silently alter
the gas-giant analogy.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The atlas consistently calls the field a potential-temperature anomaly at 700 dbar and does not relabel it as absolute temperature, heat content, or transport. | P3 | `atlas/app.js`, generated boundary | Preserve this firewall for every later pressure level. |
| 2 | The method states that 700 dbar is a pressure surface rather than a fixed geometric depth. | P3 | Atlas fact panel | Retain pressure coordinates until an explicit pressure-to-depth transformation is introduced. |
| 3 | The 64.5°S limit and the exclusion of Antarctic shelf/cavity delivery are placed beside the main interpretation. | P3 | map insight, artifact boundary | Do not use this product alone to validate Circumpolar Deep Water access to ice shelves. |

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Provider, product version, variable ID, month, pressure, grid, stride, retrieval time, source URL, method DOI, Argo DOI, and compressed-source SHA-256 are recorded. | P3 | `analysis/fetch_argo_snapshot.py` | Keep these fields required in later schema versions. |
| 2 | Missing values are preserved and the generated artifact records the unclamped range and 7,997 valid display cells. | P3 | artifact summary | Add a separate coverage/error product if one becomes available; do not infer it from missingness. |
| 3 | Source-data acknowledgement requirements and absence of a packaged per-cell uncertainty field are explicit. | P3 | artifact metadata, researcher receipt | Keep repository MIT licensing distinct from upstream data terms. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Generic coordinate projection correctly places the RG grid beginning at 20.5°E without the former half-world index assumption. | P3 | `renderObservedField`, `renderRingStrip` | Retain coordinate-based placement for all non-OISST grids. |
| 2 | A zero-centered diverging palette and visible symmetric ±5°C clamp match an anomaly field; the textual range retains the −5.07°C source minimum. | P3 | legend, map note, fact panel | Consider a clipped-cell count if future layers have substantial tails beyond the clamp. |
| 3 | Slate out-of-domain polar bands are visually distinct from beige land-or-missing cells within the RG domain. | P3 | world map, method text | Add a compact categorical key if more mask classes are introduced. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “First look below the surface” gives a memorable but bounded entry point. | P3 | map insight | Keep the adjacent non-claims when adding more depths. |
| 2 | The main text separates depth-specific departure from absolute warmth, storage, circulation, and Antarctic delivery. | P3 | map insight and footer | Preserve this sentence-level separation in promotional copy. |
| 3 | Source and method are reachable from the map, source register, atlas method, and researcher receipt. | P3 | navigation and documentation | Keep the short route from insight to exact bytes. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The new mode is a semantic button with pressed state and remains keyboard operable. | P3 | map mode group | Add automated focus-order coverage when a browser test harness is adopted. |
| 2 | A mode-specific canvas label and five-row textual statistical table provide a non-color alternative. | P3 | canvas ARIA and latitude summaries | Continue to state baseline, pressure, month, and domain in the text equivalent. |
| 3 | Probe output uses signed values plus “warmer/cooler” language and independently samples each product grid. | P3 | coordinate probe | Add an explicit “outside source domain” probe result if future grids have larger uncovered regions. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The generator rejects absent pressure levels, validates dimensions, preserves masks, and quantizes deterministically. | P3 | `fetch_argo_snapshot.py`, fixture tests | Add coordinate-monotonicity checks before accepting products with different conventions. |
| 2 | The exact committed source hash, 73 × 180 shape, pressure, month, and valid-cell floor are locked by offline tests. | P3 | `test_argo_snapshot.py` | Lock a small set of geographic probe values if the product is promoted. |
| 3 | CI installs pinned NetCDF4 and now runs both OISST and Argo local fixtures; the full 59-test offline suite and JavaScript syntax check pass. | P3 | workflow and local validation | Add headless runtime interaction tests as a later hardening step. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | README and preview status distinguish public Atlas 07, approved private Atlas 08, and the Atlas 09 working draft. | P3 | `README.md`, `PREVIEW-STATUS.md` | Update the Atlas 09 row from working draft only after owner approval. |
| 2 | The researcher receipt, source register, method page, and 16-entry BibTeX now agree about the Argo addition. | P3 | repository documentation | Keep evidence surfaces synchronized through tests. |
| 3 | No local machine path, downloaded source file, or private correspondence appears in the committed atlas. | P3 | source commit | Continue to commit only the compact transformed artifact and receipt. |

## ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The Atlas 09 change makes no new Jupiter or Saturn claim. | P3 | scope | Treat this as an Earth-side measurement improvement, not analogy evidence. |
| 2 | The new depth view reinforces that visible or surface temperature is not a full-depth heat map. | P3 | measurement firewall | Carry the same observation-method distinction into any future gas-giant comparison. |
| 3 | No pressure-level equivalence is asserted between 700 dbar ocean water and gas-giant atmospheric pressure levels. | P3 | atlas and OCEANBELTS boundary | Require mechanism and nondimensional justification before any such comparison. |

## Synthesis

Roles reviewed: 8  
P1 blockers: 0 | P2 issues: 0 | P3 notes: 24

Verdict: **APPROVED**

Top finding: the field is reproducible and visually legible while remaining
explicitly bounded as one objectively mapped pressure-level anomaly outside
the Antarctic shelf domain.

Cross-role consensus: CURRENT, SOUNDER, CHART, BEACON, and HARBOR agree that
pressure, reference state, spatial domain, and non-claims must remain beside
the visual rather than only in backend metadata.

## Amend

The highest-severity items are non-blocking P3 hardening opportunities:

1. Add headless runtime tests for mode switching, probing, and text-summary
   updates when the repository adopts a browser test dependency.
2. Add explicit clipped-cell and outside-domain probe language if future
   pressure layers widen the anomaly tails or narrow spatial coverage.
3. Extend vertical structure with multiple pressure levels and salinity only
   under the same exact-product, uncertainty, and non-transport contract.

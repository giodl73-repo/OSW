---
skill: roles-check
topic: osw-atlases
date: 2026-08-21
reviewed_atlas_commit: 3769594
role_set_commit: 262f3e7
role_set: .roles/ROLE.md
roles_used: 8
p1_count: 0
p2_count: 0
verdict: APPROVED
---

# OCEANLINES Atlas 00–03 role review

This review applies all eight OCEANLINES functional roles to Atlas 03 at commit
`3769594`. Atlas 03 incorporates and supersedes the public surfaces of Atlas 00
(`10cf92b`), Atlas 01 (`cd7f1b9`), and Atlas 02 (`31765f3`). Roles are internal
quality-control lenses, not simulated people or external scientific peer review.

## Artifact identification

| Atlas | Evidence class | Validation at milestone |
|---|---|---|
| 00 | interactive conceptual geography | 10 historical tests |
| 01 | fixed NOAA OISST absolute SST | 15 historical tests |
| 02 | fixed absolute SST and referenced anomaly | 19 historical tests |
| 03 | conceptual, absolute SST, anomaly, and estimated analysis error | 31 current tests; Python compile; JavaScript syntax; headless-browser render |

The committed Atlas 03 data date is 1 August 2026. All observed layers use
NOAA OISST v2.1 final data and a declared retrieval timestamp of
`2026-08-21T14:00:00Z`; the atlas is neither live analysis nor a forecast.

## Role selection

All eight roles apply: the artifact makes ocean-physics claims, packages climate
data, renders maps, teaches public science, provides an interactive interface,
claims reproducibility, is preparing for public maintenance, and establishes an
Earth/gas-giant comparison vocabulary.

## CURRENT — physical oceanography

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Temperature, heat content, anomaly, transport, and estimated product error remain distinct throughout the atlas. | P3 | measurement firewall; mode boundaries | Preserve as a release invariant. |
| 2 | The conceptual map now labels its regions schematic, permeable, moving, and non-fixed directly beneath the image. | P3 | conceptual map note and SVG description | Preserve the caveat wherever the figure is reused. |
| 3 | The Drake closure discussion remains a model-dependent circulation counterfactual rather than a deterministic ice-loss claim. | P3 | `OCEANREALMS.md` gateway analysis | Require the same coupled-budget framing for future gateway scenarios. |

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | SST, anomaly, and estimated-error artifacts now share the exact `oceanlines.oisst.snapshot.v2` key set and 90×180 grid contract. | P3 | three committed artifacts and schema audit | Version the schema explicitly if any key changes. |
| 2 | Each field records variable ID, source, date, retrieval time, NCSS query, source format, checksum, units, coordinates, stride, summary, and boundary. | P3 | generated payloads | Preserve source-response SHA-256 rather than hashing only transformed output. |
| 3 | The time-matched error layer is implemented and bounded as product-specific surface analysis uncertainty, not forecast or full-budget error. | P3 | `err` artifact, UI, source register | Keep uncertainty interpretation adjacent to the field. |

## CHART — ocean cartography

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Conceptual, absolute, anomaly, and uncertainty modes have distinct titles, palettes, scales, status stamps, and evidentiary language. | P3 | four map modes | Keep mode state visible and URL-addressable. |
| 2 | The observed display now declares equirectangular projection, 0° central meridian, antimeridian seam, and two-degree display stride. | P3 | map note, textual summary, atlas README | Declare any future projection change as a data-interface change. |
| 3 | The anomaly legend uses signed cooler/warmer labels and symmetric ±5°C clipping; the error palette is sequential and explicitly lower-to-higher. | P3 | legends and palette functions | Preserve semantic scale labels independently of color. |

## BEACON — public-science editing

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | The map grammar remains memorable while the primary interactive surface immediately rejects fixed-wall interpretation. | P3 | hero, conceptual note, zone boundaries | Keep metaphor and limitation in the same shareable surface. |
| 2 | Every observed mode explains what it shows and what it cannot establish. | P3 | side-panel summary and boundary | Preserve paired claim/limit writing. |
| 3 | All four standalone SVG descriptions now contain their relevant permeability, budget, measurement, or analogy caveat. | P3 | SVG `<desc>` elements | Treat figure descriptions as scientific content during review. |

## HARBOR — accessibility

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Native buttons, visible focus, semantic landmarks, `aria-pressed`, labeled groups, reduced motion, and live detail updates remain intact. | P3 | HTML/CSS interaction contract | Preserve keyboard-native controls. |
| 2 | The canvas accessible name now changes with SST, anomaly, or error mode and points to projection and text-summary descriptions. | P3 | `setMapMode` and `aria-describedby` | Test the accessible name whenever a mode is added. |
| 3 | A non-color table reports mean, range, and valid cells across five named latitude bands; anomaly values include signed warmer/cooler language. | P3 | dynamic summary table | Keep the non-area-weighted limitation in the caption. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | A read-only GitHub workflow runs all offline tests, Python compilation, and JavaScript syntax without contacting NOAA. | P3 | `.github/workflows/validate.yml` | Confirm the first hosted run after remote creation. |
| 2 | A separate pinned-dependency job generates and parses a local NetCDF3 fixture covering dimensions, coordinate order, quantization, and masks. | P3 | optional fixture test and `netCDF4==1.7.4` | Keep remote acquisition outside both merge jobs. |
| 3 | All 31 tests pass locally; three-layer schema/provenance checks and headless conceptual/error renders also pass. | P3 | validation record for `3769594` | Use these same commands as the publication gate. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | The README milestone ledger joins each atlas to its commit, evidence class, fixed data date, and current review verdict. | P3 | root milestone table | Add tag and hosted URL columns only when they exist. |
| 2 | The checklist distinguishes locally validated CI from the still-pending hosted run, remote creation, and push. | P3 | publication checklist | Do not mark external-state items complete locally. |
| 3 | Secret/private-boundary and generated-provenance scans are clean; licensing, citation, source register, and remote status agree. | P3 | local scans and public files | Repeat the scan on the exact commit before push. |

## ORBIT — planetary comparison

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Visible color, brightness temperature, kinetic temperature, composition, heat content, and transport remain explicitly non-interchangeable. | P3 | `OCEANBELTS.md` measurement ladder | Preserve this firewall for planetary layers. |
| 2 | Transfer is framed through jets, potential-vorticity gradients, eddies, stratification, and thermal-wind constraints rather than visual stripes alone. | P3 | comparison table and figure description | Add regime numbers before making quantitative similarity claims. |
| 3 | OCEANBELTS is visibly labeled a reading lens, preventing the current Earth-only map from implying an implemented planetary observed layer. | P3 | lens control | Rename it only when a sourced planetary layer exists. |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 0  |  P3 confirmed controls: 24

Verdict: APPROVED

Top finding: Atlas 03 now couples a unified, checksummed three-layer NOAA data
contract with explicit product uncertainty and a non-color spatial summary.

Cross-role consensus: The original scientific strength—the measurement
firewall—is now encoded consistently in data schema, visual grammar,
accessibility, tests, CI, figures, and public status language.
```

## Amend

No P1 or P2 amendment remains for commit `3769594`. The next three safeguards
are external or future-scope gates rather than defects in the reviewed artifact:

1. Confirm the first hosted CI run after the public remote exists.
2. Seek domain peer review before promoting gateway counterfactuals from an
   observation-class synthesis to a new causal scientific claim.
3. Keep OCEANBELTS a reading lens until a sourced, retrieval-aware planetary
   layer passes CURRENT, SOUNDER, CHART, and ORBIT together.

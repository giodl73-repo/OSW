---
skill: roles-check
topic: province-atlas-cartogram
date: 2026-08-29
roles_used: 7
p1_count: 0
verdict: APPROVED
---

# Province Atlas cartogram native-role review

Source commit: `9df16e7` (`Add 56-province ocean cartogram`)

## Artifact identification

- Type: conceptual cartographic design, deterministic SVG, CSV reference
  directory, projection-laboratory integration, and documentation
- Domain signals: physical oceanography, ecological classification, edition
  provenance, cartogram semantics, accessibility, reproducibility, licensing,
  and private-preview repository status
- Scope: additive Experiment 03; not an observed field, geographic boundary
  product, atlas-default projection, or release promotion

## Role selection

| Role | Why selected |
|---|---|
| CURRENT | The visual could make moving ecological provinces look like fixed material territories. |
| SOUNDER | The 56/54 edition distinction and source/licensing boundary must be inspectable. |
| CHART | The artifact deliberately abandons metric geography and must disclose exactly what survives. |
| BEACON | The country/state analogy is memorable enough to outrun its scientific limits. |
| HARBOR | Codes, biome colors, hover names, responsive layout, and a textual equivalent all affect access. |
| KEEL | SVG and directory are generated artifacts requiring an offline contract. |
| LOGBOOK | The experiment must remain aligned with branch, license, source, and publication status. |

ORBIT was not selected because this artifact makes no planetary comparison.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The page and SVG call the provinces static mean ecological references and state that natural boundaries move seasonally and interannually. | P3 | map footer and method firewall | Keep this warning attached to every export. |
| 2 | The cartogram does not encode temperature, heat content, transport, or a dynamical barrier, so its shapes cannot be mistaken for a diagnosed heat budget without contradicting the visible legend. | P3 | experiment scope | Require a new observed-layer contract before adding heatmass crossings. |
| 3 | Arctic and Southern provinces are visually separated as cap/base reference groups without claiming the strips are solid walls or rings. | P3 | SVG layout | Preserve the reference-language distinction when overlays are added. |

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Source Register P5 identifies Reygondeau et al. 2013 and Marine Regions while bounding their use to vocabulary and classification context. | P3 | provenance | Add a separate source entry if a future view imports actual boundary coordinates. |
| 2 | The classic 56 vocabulary, separate OCAL/CCAL treatment, and later 54-province revision are declared rather than silently merged. | P3 | edition note and CSV | Treat each future edition as a versioned catalog, not an overwrite. |
| 3 | SVG metadata explicitly says the geometry is original and does not reproduce the CC-BY-NC-SA Marine Regions boundary dataset. | P3 | license boundary | Preserve this firewall unless repository licensing is deliberately reconsidered. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “REFERENCE CARTOGRAM · NOT A PROJECTION” is printed inside the graphic, while the page lists area, distance, direction, exact adjacency, and exact coast contact as sacrificed properties. | P3 | method legend | Never remove the in-figure qualification for a cleaner crop. |
| 2 | Pacific, Indian, and Atlantic regions dominate the canvas; land is reduced to narrow, subdued seams as requested without disappearing completely. | P3 | visual hierarchy | Retain land as context rather than a competing filled geography. |
| 3 | Four biome colors group provinces while black internal borders and four-letter codes preserve individual identity independent of hue. | P3 | visual encoding | Test any future palette against the same code-and-boundary redundancy. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “The ocean, drawn like a country” communicates the inversion immediately, and “state-like” is used instead of falsely calling the provinces political states. | P3 | headline and README | Keep “like” and “state-like” in public summaries. |
| 2 | The three-note sequence separates the memorable code system, scientific biome system, and edition issue. | P3 | explanatory notes | Preserve this progressive disclosure if the section moves. |
| 3 | Direct links lead from the visual to the 56-row directory, primary paper, source description, and method limitations. | P3 | reading path | Add province profile pages only when they can retain the same source boundary. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The embedded figure has descriptive alternative text and the standalone SVG has title/description metadata plus focusable province groups. | P3 | figure semantics | Keep group titles synchronized with the generated CSV. |
| 2 | Full province identity is not color- or pointer-dependent because the linked CSV includes code, name, basin, biome, edition, and geometry status for all 56 rows. | P3 | textual equivalent | Consider a styled HTML directory if the CSV becomes a primary public route. |
| 3 | Province notes collapse to one column and the directory link reflows at narrow widths without removing the limitation language. | P3 | responsive CSS | Include 400% zoom and keyboard checks in later browser automation. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | One standard-library Python command deterministically emits both the SVG and CSV from a single province registry. | P3 | generator | Keep the SVG and directory coupled in one build. |
| 2 | The offline suite asserts 56 rendered province groups, 56 unique CSV codes, edition labels, representative codes, method language, and the licensing firewall. | P3 | `analysis/test_atlas.py` | Add a checked generated-file digest only if manual artifact drift becomes recurrent. |
| 3 | The complete 38-test suite and `git diff --check` pass without network access. | P3 | validation gate | Retain these commands as the default contributor gate. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | README routes expose the experiment, directory, reproduction command, and non-metric status without claiming public deployment. | P3 | repository entry points | Keep hosted URLs tied to Atlas 07 until an explicit promotion decision. |
| 2 | No external boundary asset, personal data, private researcher reference, or machine-specific path entered the artifact. | P3 | public boundary | Preserve the original-geometry approach for the MIT repository. |
| 3 | The experiment is additive to PELAGOS, Equal Earth, and HEATPLATES rather than silently replacing a reviewed map family. | P3 | history and projection lab | Record owner visual approval separately from native-role approval. |

## Synthesis

```text
Roles reviewed: 7
P1 blockers: 0  |  P2 issues: 0  |  P3 notes: 21

Verdict: APPROVED
Top finding: The map succeeds because it openly changes from geographic
projection to reference cartogram and prints that loss of metric meaning inside
the artifact itself.
Cross-role consensus: CURRENT, CHART, BEACON, and HARBOR agree that the country
analogy is useful only while dynamic-boundary, edition, and non-metric limits
remain visible and available without color or hover.
```

Approval is scoped to an additive private projection-laboratory experiment. It
does not approve the cartogram as the default observational atlas map, validate
the illustrated shapes as geographic Longhurst boundaries, or replace external
scientific review.

## Amend

1. If observed or geographic province polygons are added, create a new
   source/license/transformation contract rather than modifying this cartogram.
2. Add a 54/56 edition switch only after both catalogs and their differences are
   versioned and explained beside the control.
3. Before public promotion, obtain owner visual approval and consider a styled
   HTML province directory for readers who do not use CSV directly.


---
skill: roles-check
topic: public-map-first-visitor
date: 2026-11-08
roles_used: 7
p1_count: 3
verdict: NEEDS-WORK
---

# First-visitor map and card review

This is a repository role review of code, copy, and retained cloud browser evidence, not external peer review or a study with a new visitor. The reviewed browser source is `499f60f070aa811788efa74b139d15f20290a313`, run `42525991259`. The [retained usability receipt](../../../research/public-map-usability-review-v1.json) records the exact checks, artifact custody, inspected screenshots, and subsequent small text changes.

Artifact type: browser UI and preview preparation. Signals: scientific scope, source provenance, geographic representation, public explanation, accessibility, reproducibility, and release accuracy. CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, and LOGBOOK apply for those reasons respectively. ORBIT is excluded because this change contains no planetary comparison. This is not the final full-atlas release review.

## CURRENT

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| C1 | Confirmed strength: points and approximate routes are not presented as measured current boundaries. | P3 | `public-map.js`, `mapMeaning`; map legend | Preserve these distinctions in the public projection. |
| C2 | Confirmed strength: width and route references retain separate groups and exact records. | P3 | `evidenceRows` call sites | Do not merge different operators into one dimension or infer volume. |
| C3 | The research inventory has newer depth work than this frozen display snapshot. | P2 | `PUBLIC-PREVIEW.md`, Research status | Reconcile the chosen public snapshot before advertising depth coverage in cards or queries. Do not inherit depths across current families. |

## SOUNDER

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| S1 | One contextual source ID in the frozen display lacks a source row; the citation supplement has not yet been joined into a public edition. | P1 | `public-display-source-inventory-v1.json`, `public-preview-source-supplement-v1.json` | Join the retained supplement in the public projection and enforce a closed provenance graph. This is bibliographic context, not a new independent measurement. |
| S2 | Confirmed strength: selected records are checked against pinned byte hashes; exact qualifications remain inspectable. | P3 | `verified`, `evidenceRows`; passing browser receipt | Preserve this custody when changing the data namespace. |
| S3 | Record counts can be mistaken for physical eddy counts or live data. | P2 | Prior inventory status string | Text amendment applied: say named-eddy source records and frozen research snapshot; render an existing identity scope note. Preserve unresolved identity associations. |

## CHART

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| T1 | The projection was not named beside the fast map. | P2 | `public-map.html`; existing Rust `map.rs` and `cartography.rs` | Text amendment applied: label the equirectangular grid and warn against reading physical dimensions from apparent map width or area. No projection calculation changed. |
| T2 | Confirmed strength: names are available by hover, focus, and a named selector; unlocated identities remain findable. | P3 | `render`; browser selector checks | Keep a complete textual inventory in the selected public edition. |
| T3 | Confirmed strength: map meaning is now explained in plain language separately from technical roles. | P3 | Inspected desktop and narrow-card screenshots | Retain the role explanation when a current has only a locator. Do not imply every named current has a traced route. |

## BEACON

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| B1 | Confirmed strength: a short first-visit guide connects choosing a name, reading a card, and following evidence. | P3 | Guide open/close browser check | Keep one easy example and define current and eddy before requiring technical knowledge. |
| B2 | Confirmed strength: source links sit beside references, while large exact records are disclosed on demand. | P3 | Inline citation checks and `evidenceRows` | Keep essential scope visible; do not move necessary qualifications exclusively into JSON. |
| B3 | Understandability has not been measured with a new reader. | P3 | No observed visitor session in evidence | After a reviewable preview exists, ask a reader what a point, route, and number mean; record hesitation without coaching. Do not describe automated checks as comprehension testing. |

## HARBOR

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| H1 | Confirmed strength: the selector, visible focus, headings, and world return provide alternatives to pointer-only map exploration. | P3 | Focus, keyboard Home, selector, and return checks | Keep equivalent name-based access after source screening. |
| H2 | Confirmed strength: empty search now announces the result and offers a clear action that returns focus to search. | P3 | Search recovery browser check | Retain this recovery rather than leaving an empty map unexplained. |
| H3 | Narrow-layout and reduced-motion browser checks do not establish screen-reader speech behavior or usability at every text zoom. | P3 | Browser scope and inspected 390px screenshot | Report the tested scope honestly. Include those additional checks in final bundle review where feasible. |

## KEEL

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| K1 | The browser run serves the working tree, not an enforced, selected public bundle with its full link graph checked. | P1 | `review_public_map_browser_v1.py`; source-use contract | Build the selected package first, then validate its actual pages, downloads, source links, NASA navigation, and query results. |
| K2 | Confirmed strength: cloud checks use one idle CPU and carry the cumulative UI budget; no scientific measurements were recalculated. | P3 | Workflow and retained result, 55.364067036 cumulative seconds | Continue sequential bounded verification; do not reset the same diagnostic budget. |
| K3 | This run verifies the fast map tasks, not the full advanced research UI or the repository scientific suite. | P3 | Receipt status `PASS_FAST_MAP_TASKS_ONLY` | Keep narrow status labels. Do not report skipped validation as comprehensive success. |

## LOGBOOK

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| L1 | Pending provider records remain in the internal candidate. A faster, clearer page does not clear their use. | P1 | Source-use decision registry, four pending provider source IDs | Enforce field-specific decisions in the public data projection; do not publish the working repository tree. |
| L2 | Confirmed strength: publication status remains research preview candidate; main and live Pages have not been promoted. | P3 | Publication receipt and page copy | Keep the status aligned with the actual deployable package and target. |
| L3 | The new usability proof needs a durable pointer in the readiness document. | P3 | New `public-map-usability-review-v1.json` | Add the receipt, source commit, limited scope, and remaining public-package work to readiness documentation. |

## Synthesis

Roles reviewed: 7. P1 blockers: 3. P2 issues: 3. P3 notes: 15.

Verdict: **NEEDS-WORK for public publication**. The usability changes are useful and have passing bounded browser evidence; this verdict does not require stopping preview preparation.

Top finding: prepare and validate the selected public package rather than treating the internal fast map as a public release. SOUNDER, KEEL, and LOGBOOK converge on that boundary. CURRENT, CHART, and BEACON agree that explanation must preserve the distinction between source-scoped references and complete physical dimensions.

Three amendments:

1. Applied in the map UI: first-visit guide, inline source links, expandable reference groups, search recovery, copy-view action, explicit identity scope where stored, frozen-snapshot terminology, and projection label. Browser proof covers the interaction changes; the last three small text amendments have syntax review only.
2. Required in the public data projection: preserve every current identity and eligible reference, reconcile the citation supplement and latest selected snapshot, keep eddy source cases separate from unresolved named-registry joins, and withhold pending provider uses.
3. Required before publication: verify the actual selected bundle and align counts, downloads, navigation, query data, release metadata, and public target. A future first-reader session supplies comprehension evidence; this review does not invent it or contact a reader.

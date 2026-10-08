---
skill: roles-check
topic: mindanao-mean-offshore-extent
date: 2026-10-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Mindanao mean offshore extent: internal role review

All seven installed roles selected for scientific scope, provenance, map meaning,
public explanation, accessibility, reproducibility and publication stewardship.
This is an internal review, not independent scientific peer review.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---------|----------|---------|----------------|
| 1 | Keep one-sided extent distinct from paired width | P2 | Source audit / protocol / UI / validation | Resolved: new metric, null midpoint and no full-width eligibility. |
| 2 | Reference depths are not a surface measurement layer | P2 | Source audit / protocol / UI / validation | Resolved: separate reference-depth context; fixed layer null. |
| 3 | Historical measurements and offshore eddy core differ in support | P3 | Source audit / protocol / UI / validation | Do not pool these as seasonal limits. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---------|----------|---------|----------------|
| 1 | Campaign endpoints conflict within original source | P2 | Source audit / protocol / UI / validation | Resolved: both retained; exact mean profile dates unknown. |
| 2 | Prose extraction must be bound to sampling context | P2 | Source audit / protocol / UI / validation | Resolved: full row and context bound to source audit checksum. |
| 3 | Original PDF redistribution is restricted | P3 | Source audit / protocol / UI / validation | PDF remains ignored; checksum and source URL retained. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---------|----------|---------|----------------|
| 1 | Route geography cannot receive a width buffer | P2 | Source audit / protocol / UI / validation | Resolved: source extent chart only; section/edge geometry null. |
| 2 | Compact endpoint labels overlap at 320 px | P2 | Source audit / protocol / UI / validation | Resolved: outward anchors, extra axis padding and overlap assertion. |
| 3 | Mean line endpoints indicate sampling support | P3 | Source audit / protocol / UI / validation | Preserve in metadata; do not reinterpret as current boundaries. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---------|----------|---------|----------------|
| 1 | Typical regional width label would misstate this record | P2 | Source audit / protocol / UI / validation | Resolved: explicit mean surface offshore extent in atlas/table/explorer. |
| 2 | Ranged prose is not a confidence margin | P3 | Source audit / protocol / UI / validation | Caption says no midpoint, confidence interval or annual range. |
| 3 | Abstract and transport limits are not independent measurements | P3 | Source audit / protocol / UI / validation | Excluded alternatives documented in source audit. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---------|----------|---------|----------------|
| 1 | Range must remain readable without color | P3 | Source audit / protocol / UI / validation | Text endpoints, caption and SVG aria-label provide equivalent meaning. |
| 2 | Narrow reflow must include source access | P3 | Source audit / protocol / UI / validation | 320 px check covers no overflow and source link. |
| 3 | Unresolved observations must not enable play | P3 | Source audit / protocol / UI / validation | Disabled playback and unknown annual range asserted. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---------|----------|---------|----------------|
| 1 | Protocol addition invalidates section diagnostic receipts | P2 | Source audit / protocol / UI / validation | Resolved: regenerated diagnostics; scientific values unchanged. |
| 2 | Reject scientifically misleading record mutations | P2 | Source audit / protocol / UI / validation | Resolved: 17 mutation cases preserve metric and context. |
| 3 | CI still requires final exact-head verification | P2 | Source audit / protocol / UI / validation | Open publication condition: dependent draft; do not claim main. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---------|----------|---------|----------------|
| 1 | Scope audit must accompany generated artifacts | P3 | Source audit / protocol / UI / validation | New audit and source-index registration versioned. |
| 2 | Local passing checks do not establish main coverage | P3 | Source audit / protocol / UI / validation | Publication status recorded separately. |
| 3 | A source extraction is not scientific peer review | P3 | Source audit / protocol / UI / validation | Internal role review and pending canonical admission stated. |

## Synthesis

Roles reviewed: 7. P1: 0. P2: 10 (9 addressed; CI publication condition open). P3: 11.
Verdict: APPROVED-WITH-CONDITIONS for a dependent draft.
Top finding: retain offshore extent as a separate one-sided metric.
CURRENT, CHART and BEACON agree that a crisp full-width envelope is unsupported.

## Amendments

1. Bind the complete source description and sampling context; reject promotion.
2. Label the chart and atlas as offshore extent; correct compact labels.
3. Preserve scientific values while refreshing protocol receipts; record CI separately.

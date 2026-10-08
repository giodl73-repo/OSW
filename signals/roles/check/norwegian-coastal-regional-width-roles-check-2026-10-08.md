---
skill: roles-check
topic: norwegian-coastal-regional-width
date: 2026-10-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Norwegian Coastal Current regional width review

Internal review of data, validator, Rust safeguards, chart and source inventory;
not independent peer review or canonical admission. Selected all seven project
roles for physical scope, provenance, cartography, explanation, accessibility,
reproducibility and publication status respectively.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Coastal and offshore branches must remain distinct. | P2 | Row identity/scope | Addressed: coastal owner and Halten scope bound to audit. |
| 2 | Hydrographic depth is not width's measurement layer. | P2 | Layer/context | Addressed: null fixed layer; explicit exclusion and mutation tests. |
| 3 | Original boundary definition remains unresolved. | P3 | Remaining gates | Retain source-summary status; review original figure before admission. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Source access is an indexed excerpt, not inspected full text. | P2 | Source access/UI | Addressed: explicit access note in audit, row and chart definition. |
| 2 | Prose range cannot become a midpoint or confidence interval. | P2 | Values/validator | Addressed: null value and scoped range; Python/Rust reject promotion. |
| 3 | No original-source byte receipt exists. | P3 | Provenance | Do not fabricate a hash; acquire and inspect original in follow-up. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Range must not become an occupied map buffer. | P2 | Atlas/seasonal chart | Addressed: no edges/geometry inferred; full-width bar hidden. |
| 2 | Nearby shelf/water-mass dimensions invite conflation. | P2 | Audit exclusions | Addressed: four excluded quantities with reasons. |
| 3 | A region locator would improve navigation after source inspection. | P3 | Geometry | Keep location as prose until independently supported geometry exists. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Annual variation is not supported by this range. | P2 | Caption/time | Addressed: explicit nonannual caption, null dates and disabled play. |
| 2 | Full-source limitation needs to be beside the result. | P2 | Chart definition | Addressed: visible source-quality note and browser assertion. |
| 3 | Overall coverage counts are heterogeneous scoped evidence. | P3 | Batch plan | Qualify counts; do not call 40 owners complete widths. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | SVG labels were too small at 320 px. | P2 | Regional chart | Addressed: enlarged labels and effective-size assertion. |
| 2 | Color cannot be the only range explanation. | P2 | Chart | Addressed: endpoint text, caption and dynamic SVG accessible description. |
| 3 | Narrow-screen layout needs direct inspection. | P3 | Browser evidence | Inspect saved mobile screenshot and retain no-overflow assertion. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Coherent manifest rewriting can bypass checksum-only guards. | P2 | Rust | Addressed: semantic guard and four coherent-rewrite rejection cases. |
| 2 | Original fixtures still depend on remote acquisition in CI. | P2 | Publication | Open condition: protected-main CI must pass; no checks weakened. |
| 3 | Prior browser passes do not establish this final bundle. | P3 | Validation | Rebuild and run affected browser checks on final bytes. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Local validation must not be called mainline publication. | P2 | Status | Addressed: publication remains pending; separate local receipts. |
| 2 | No restricted original should be redistributed. | P2 | Source files | Addressed: only extraction/audit stored; original not acquired. |
| 3 | New measurement rules must remain consistent. | P3 | Protocol | Existing v1.2 regional range rule applies; no protocol rewrite needed. |

## Synthesis

Roles reviewed: 7. P1: 0. P2: 14 (13 addressed, CI condition open).
P3: 7 follow-up notes. APPROVED-WITH-CONDITIONS for editorial review.
Top finding: the indexed introduction supports regional prose evidence only.
CURRENT, SOUNDER and CHART agree that boundary/depth/seasonal admission awaits
original observations. KEEL and LOGBOOK require honest final-byte validation
and passing publication gates before any mainline completion claim.

Amendments applied:

1. Bind the complete row, branch and exclusions to the source audit.
2. Display source-access limits beside the chart and enlarge mobile labels.
3. Add Python mutation tests and Rust coherent-rewrite rejection checks.

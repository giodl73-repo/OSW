---
skill: roles-check
topic: agulhas-return-adcp-width
date: 2026-10-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Agulhas Return ADCP widths: internal role review

Seven installed roles selected for scientific support, provenance, map meaning,
public explanation, accessibility, reproducibility and repository stewardship.
This is internal review, not independent scientific peer review.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---------|----------|---------|----------------|
| 1 | Width is a median across bin-wise half-maximum spans | P2 | Source audit / protocol / chart / validation | Resolved: distinct metric; no fixed-layer full-width interpretation. |
| 2 | Projection component is already included in total error | P2 | Source audit / protocol / chart / validation | Resolved: separate component; no double addition or confidence level. |
| 3 | Four crossings do not establish an annual range | P3 | Source audit / protocol / chart / validation | No annual extrema or seasonal playback; exact crossing dates unresolved. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---------|----------|---------|----------------|
| 1 | Original table differs from preliminary poster summary | P2 | Source audit / protocol / chart / validation | Resolved: use rendered original Table 1; preserve original checksum. |
| 2 | Reported aggregate uncertainty remains ambiguous | P3 | Source audit / protocol / chart / validation | Exclude 62 ±9 aggregate; retain four table measurements independently. |
| 3 | Source PDF redistribution is restricted | P3 | Source audit / protocol / chart / validation | Ignored local copy; source URL and checksum retained. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---------|----------|---------|----------------|
| 1 | A local threshold scalar cannot buffer the full route | P2 | Source audit / protocol / chart / validation | Resolved: independent comparison plot; no mapped edges or footprint. |
| 2 | 1997 observation context must be visible | P2 | Source audit / protocol / chart / validation | Resolved: year in value/caption; exact dates unresolved. |
| 3 | Whiskers could be mistaken for seasonal extrema | P3 | Source audit / protocol / chart / validation | Explicit source-total-error caption and no full-width bar. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---------|----------|---------|----------------|
| 1 | Summary and normalized 70 km are not extra observations | P2 | Source audit / protocol / chart / validation | Resolved: source audit exclusions and exactly four inventory records. |
| 2 | ADCP acronym needs explanation | P2 | Source audit / protocol / chart / validation | Resolved: chart caption defines acoustic Doppler current profiler. |
| 3 | Method and error model need nearby access | P3 | Source audit / protocol / chart / validation | Source link, layer/boundary text and complete query record available. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---------|----------|---------|----------------|
| 1 | Narrow chart text and selection must remain readable | P2 | Source audit / protocol / chart / validation | Resolved: 320 px reflow, text size, four phase selections and visual inspection. |
| 2 | Color alone cannot supply width/error information | P3 | Source audit / protocol / chart / validation | Each point has numeric text and comprehensive aria-label/caption. |
| 3 | Unsupported playback should not appear active | P3 | Source audit / protocol / chart / validation | Disabled play and absent edge locator asserted. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---------|----------|---------|----------------|
| 1 | Shared validation did not reject stale protocol receipt | P2 | Source audit / protocol / chart / validation | Resolved: moved protocol check into validate(); two regression cases. |
| 2 | Coherent receipt rewrites must not promote source support | P2 | Source audit / protocol / chart / validation | Resolved: Rust semantic guard; three native coherent-rewrite rejections. |
| 3 | Final-head full CI still pending | P2 | Source audit / protocol / chart / validation | Open publication condition; dependent draft, no main claim. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---------|----------|---------|----------------|
| 1 | Preserve earlier measurements during this update | P3 | Source audit / protocol / chart / validation | All 74 older rows and six frames equal; diagnostic changes only protocol hashes. |
| 2 | Earlier test counts did not cover new protocol gate | P3 | Source audit / protocol / chart / validation | Batch receipt records correction and exact verification scope. |
| 3 | Internal review is not scientific admission | P3 | Source audit / protocol / chart / validation | Canonical and independent scientific review remain pending. |

## Synthesis

Roles: 7. P1: 0. P2: 11 (10 addressed; final CI publication condition open). P3: 10.
Verdict: APPROVED-WITH-CONDITIONS for a dependent draft.
Top finding: preserve per-bin threshold medians and source errors as distinct quantities.
CURRENT, CHART and BEACON agree that seasonal or route-envelope inference is unsupported.

## Amendments

1. Bind four original table rows and their error components; omit ambiguous aggregate.
2. Add accessible dated local comparison without edges, buffer or seasonal play.
3. Enforce protocol receipt checks across callers and source support within Rust.

---
skill: roles-check
topic: marine-heatwave-gfs-surface-energy-screen
date: 2026-09-06
roles_used: 7
p1_count: 0
verdict: APPROVED
---

# Roles check — OSW-D12 GFS surface-energy screen

**Artifact type:** forecast-model source extraction, cross-system physical
diagnostic, static scientific map, evidence receipt, and documentation update  
**Source commit:** `556edacd5c5b9ca0b1829e804ae05384635a730b` plus the reviewed working-tree changes  
**Reviewed artifacts:** `atlas/data/gfs-mhw-surface-flux-north-atlantic-20260807-20260812.json`,
`research/osw-d12-gfs-surface-flux-screen-2026.json`, and
`figures/osw-d12-gfs-surface-flux-screen-2026.svg`

## Role selection

| Role | Why selected |
|---|---|
| CURRENT | D12 converts surface energy to a mixed-layer temperature scale across two model systems. |
| SOUNDER | Historical GFS messages are byte-range extracted, decoded, transformed, and checksum receipted. |
| CHART | Flux sign, diagnostic layer depth, and inferred temperature scale share one geographic plate. |
| BEACON | “Material contribution” must not become budget closure or atmospheric causation. |
| HARBOR | Signed fields and clipped ranges need redundant encodings beyond hue. |
| KEEL | A long optional network acquisition and native decoder need deterministic offline gates. |
| LOGBOOK | A new source class, receipt, registry row, history entry, guide, and commands must agree. |

ORBIT was not selected because D12 makes no planetary comparison.

## Review findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Bulk surface flux is not deposited uniformly through a diagnostic mixed layer, especially for penetrating shortwave. | P2 | Method/boundary | Call the result a temperature-change scale and retain shortwave penetration among unresolved terms. **Resolved.** |
| 2 | Endpoint-mean MLD does not reconstruct entrainment or layer heat content during rapid shoaling. | P2 | Depth variants | Keep start-depth and endpoint-mean results separate and deny native budget closure. **Resolved.** |
| 3 | Sub-2-m diagnostic layers make the cellwise mean nonlinear and potentially dominant. | P2 | Headline result | Add 2/5/10 m floors, box-mean slab scaling, cell fractions, median, and percentiles. **Resolved.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The `sfluxgrbf` fields are on a 3072×1536 regular Gaussian grid, not the common 0.25-degree regular GFS grid. | P2 | Source/figure/register | Name the product “native Gaussian-grid surface flux” and preserve `Ni`, `Nj`, and `gridType`. **Resolved.** |
| 2 | A checksum of extracted arrays cannot identify the upstream GRIB messages. | P2 | Provenance | Preserve all 120 index lines, inclusive ranges, message hashes, ETags, sizes, dates, and statistical metadata. **Resolved.** |
| 3 | GFS is operational forecast output, not reanalysis; RTOFS is operational assimilative output. | P2 | Evidence origin | Add and use separate governed origins for OER016 and OER015. **Resolved.** |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The first temperature-scale palette clipped negative cells as if they were zero. | P2 | Panel C | Use a zero-centered diverging scale and label blue cooling/orange warming. **Resolved.** |
| 2 | The first ±150 W/m² flux scale saturated a substantial warm tail. | P2 | Panel A | Expand the displayed positive limit to +220 W/m² while retaining zero as the semantic center. **Resolved.** |
| 3 | The three panels combine native Gaussian input and RTOFS sampling in a simple lon/lat rendering. | P3 | Footer/deck | Name the Plate Carrée display and the bilinear sampling explicitly. **Resolved.** |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Surface forcing explains the remainder” would overstate a cross-model subtraction. | P2 | Finding/guide | Say “supports an energy scale” and call every post-flux difference diagnostic bookkeeping. **Resolved.** |
| 2 | One warming number conceals the factor-of-three depth-method spread. | P2 | Callout | Lead with +0.12 to +0.34°C/day and explain that layer choice drives the range. **Resolved.** |
| 3 | Readers may repeat +113 W/m² as an observation. | P2 | Deck/footer | Repeat that it is GFS forecast-derived forcing and not reanalysis or independent validation. **Resolved.** |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Flux and inferred warming sign cannot depend on color. | P2 | Panels A/C | Add zero contours, signed units, numeric callout, and a time plot around a visible zero line. **Resolved.** |
| 2 | The three maps require an ordered textual reading path. | P2 | Panel headings | Retain A/B/C labels and full physical quantity names. **Resolved.** |
| 3 | Small SVG caveats are insufficient as the only alternative. | P3 | Companion artifacts | Pair live SVG text with detailed guide prose and machine-readable fields. **Resolved.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | ecCodes lacks a native Python 3.14 wheel in the tested environment. | P2 | Optional requirements | Pin ecCodes 2.48 and document Python 3.12 as the tested acquisition runtime; keep default analysis offline. **Resolved.** |
| 2 | A transient failure late in 120 message transfers should not fail immediately. | P2 | Fetcher | Retry bounded reads three times while retaining explicit manual refresh. **Resolved.** |
| 3 | Remote refresh cannot be a deterministic default test. | P2 | Tests | Pin the compact-row SHA-256; assert 5×34×42 support, 20 objects, 120 messages, ETags, GRIB metadata, derived values, SVG text, and local index/subset helpers. **Resolved.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | D12 adds a distinct evidence origin and source-register obligation. | P2 | OER016/D49 | Add `operational_forecast_model`, D49, and regenerate sixteen receipts. **Resolved.** |
| 2 | History and guides must preserve the factor-of-three depth sensitivity and cross-system limit. | P2 | Documentation | Record the values and boundary consistently in README, history, analysis notes, guide, and receipt. **Resolved.** |
| 3 | No commit, push, or publication was authorized in this continuation. | P3 | Repository state | Validate locally and retain the existing dirty working tree without release claims. **Accepted.** |

## Synthesis

```text
Roles reviewed: 7
P1 blockers: 0  |  P2 issues: 18  |  P3 notes: 3

Verdict: APPROVED

Top finding: positive bridge-day surface heat gain is supported as a forecast-
derived energy scale, but shallow-layer treatment changes the inferred warming
by nearly a factor of three and the GFS/RTOFS pairing cannot close a native budget.

Cross-role consensus: CURRENT, SOUNDER, and BEACON require “cross-system
plausibility screen” rather than forcing attribution. CHART and HARBOR require
signed contours, numbers, position, and text in addition to color. KEEL and
LOGBOOK require explicit optional refresh, exact message receipts, deterministic
offline validation, and no release claim.
```

## Amendments completed

1. Corrected the source-grid label, split operational forecast from operational
   assimilative provenance, and retained message-level acquisition receipts.
2. Added layer-depth sensitivity, narrowed public language to an energy scale,
   and preserved the unclosed vertical/assimilation terms.
3. Reworked signed palettes and zero contours, added acquisition retries and
   parser/subset tests, and aligned the receipt, register, history, guides, and SVG.

No external peer review is implied by this repository role check.

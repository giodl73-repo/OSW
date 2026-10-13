---
skill: roles-check
topic: acc-udintsev-breadths
date: 2026-10-09
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# ACC Udintsev quantities — internal role review

Artifact: original-source extraction, protocol, source bindings, inventory and
atlas/inspector cards. Seven repository lenses applied internally; no independent
scientific review. ORBIT excluded because the change uses no analogy.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | The abstract's 170 km headline compresses away wider boundaries. | P2 | Metric | Detailed p4517 separates 170 km SAF-SACCF and 500 km NB-SB quantities. |
| 2 | Mean contour separation is not instantaneous full-depth width. | P2 | Support | Surface MDT support, climatological operator and unresolved depth/edges explicit. |
| 3 | Cruise/particle months cannot establish width seasonality. | P2 | Calendar | Dates retained as separate context; no occupations, monthly calendar or playback. |

## SOUNDER — data stewardship

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Reference period differs from assimilated and validation observations. | P2 | Time | 1993-2012 MDT reference distinguished from 1993-2016 assimilation and 2001-2017 Argo. |
| 2 | Different metrics require different contours and identities. | P2 | Definition | Separate IDs, metric codes, labels and contour pairs; PF remains intermediate. |
| 3 | Grid spacing and hydrographic agreement do not quantify width error. | P2 | Uncertainty | Uncertainty null; both substitutions explicitly excluded. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Figure 5 is meridional distance relative to PF. | P2 | Geometry | Reviewed figure; no invented flow-normal operator or paired coordinates. |
| 2 | A 170-500 km line would imply a range. | P2 | Chart | Separate approximate point graphics with metric names and contours. |
| 3 | Local climatological values cannot buffer the global route. | P2 | Map | No mapped physical edges, route buffer or state intersection admission. |

## BEACON — science editing

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Generic width titles obscure quantity identity. | P2 | Inspector | Major-front separation and Boundary-defined breadth titles. |
| 2 | A precise-looking number can lose the source approximation. | P2 | Caption | Approximately/approximation symbol retained; uncertainty unknown. |
| 3 | Coverage could imply measured-current completeness. | P2 | Status | 114 scoped descriptions / 62 owners / 30 unassessed; full physical widths remain unresolved. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | The generic synthesis alternate text misstates this source method. | P2 | SVG | Scoped descriptions name contours, location, operator, period and unknown edges. |
| 2 | Two long captions must remain readable on mobile. | P2 | Layout | Both 320 px screenshots inspected; font-size/reflow browser checks passed. |
| 3 | Readers need an exact source path from each card. | P2 | Navigation | Separate /measurements/0 and /measurements/1 pointers, native/source parity passed. |

## KEEL — reproducibility

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Receipt-consistent edits can still invent a pooled range or dates. | P2 | Guards | Seven coherent native/WASM mutations rejected. |
| 2 | Removing context might transfer an approximate width to another owner. | P2 | Identity | Immutable ID binding rejects both Antarctic Slope and registered Algerian transfer. |
| 3 | Mutable external paper servers can prevent remote validation. | P2 | CI | Fresh ACC acquisition verified; older-source remote failures reported separately without weakening pins. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | CC BY-NC-ND does not authorize an unrestricted redistributed asset. | P2 | Original | Complete original stays local and ignored; attributed factual annotations ship. |
| 2 | Dependency refresh must preserve unrelated records and routes. | P2 | Regeneration | All 112 preceding descriptions and other decisions/dashboard entries unchanged; ledger/routes/naming unchanged. |
| 3 | Local validation or draft publication does not establish mainline admission. | P2 | Publication | Stack, scientific review, local gates and remote CI status kept distinct. |

## Synthesis and amendments

Roles reviewed: 7. P1 blockers: 0. P2 issues: 21 addressed or tied to remaining
validation. Editorial publication verdict: APPROVED-WITH-CONDITIONS after full
suite and atlas navigation. No independent scientific admission claimed.

Top finding: metric identity must travel with the approximate value. CURRENT,
SOUNDER, CHART and BEACON agree.

1. Keep two contour-defined quantities and prohibit pooled range/owner transfer.
2. Expose the meridional operator and climatological reference beside each value.
3. Verify the original, dependency pins, mobile/source/native/WASM parity and
   full-suite navigation before publication.

## Additional rendering finding

Remote PR67 push run 37908835254 exposed clipping of an Atlantic EUC SVG heading
under the Linux browser fonts. CHART and HARBOR reviewed the correction: move title
and units to wrapping HTML headings, retain units in SVG alternate text and keep
the existing SVG containment assertion. The existing browser test passed locally;
remote Linux validation remains pending. Section data and date conflicts unchanged.

## Validation outcome

Editorial publication conditions met locally: **1175 Python tests / 918 subtests**,
41 Rust tests, native/WASM builds, fresh original acquisition and dependency checks
passed. Both ACC cards passed mobile/source/query parity and seven coherent
native/WASM mutations after the final identity and encoding corrections. Atlas
navigation passed all 122 phase links and six seasonal round trips. All 48
JavaScript modules and 14 page assignments passed. Atlantic section-properties
browser passed after the heading correction, with its containment assertion intact.

Python inventory dispatch now recognizes the ACC record ID even when context is
deleted and owner reassigned; dedicated inventory-level transfer tests passed.
Scientific admission, exact edges and remote/mainline validation remain separate.

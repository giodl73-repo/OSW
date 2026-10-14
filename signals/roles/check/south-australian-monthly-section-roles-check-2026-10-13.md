---
skill: roles-check
topic: south-australian-monthly-section
date: 2026-10-13
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
p3_count: 21
verdict: APPROVED-WITH-CONDITIONS
---

# South Australian monthly component-section review

Seven installed lenses applied internally; ORBIT does not apply. No delegation
or independent scientific approval claimed. Editorial publication requires
the final offline, browser and checked-source gates; current-width admission
remains unresolved.

## CURRENT

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | Local eastward peak might be another flow or eddy | P3 | association | Named-current association unverified; fixed-component diagnostic label retained. |
| 2 | Independent model could impersonate CARS-Aus8/MOM01 | P3 | layer/source | HYCOM 2012 modeled 100 m explicitly separated from Duran's datasets and epochs. |
| 3 | Monthly peak changes could imply tracked current evolution | P3 | time | No geographic animation, climatology, annual extrema or whole-current width admission. |

## SOUNDER

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | Longitude index could select 48 W rather than 132 E | P3 | coordinates | Actual coordinate maps verified; index 3900 and depth index 19 frozen; wrong requests rejected. |
| 2 | Fill flag or packing could create fictitious ocean values | P3 | units/masks | Original Int16 values retained; -30000 preserved as missing, scale .001 m/s checked. |
| 3 | Calendar and partial support could bias monthly means | P3 | support | Complete 366-date leap year verified; complete u/v pairs require ceil(.8 × month days), without gap interpolation. |

## CHART

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | Two section endpoints could imply occupied-current area | P3 | map | Fixed section line only, no buffer, polygon, containment or NASA identification. |
| 2 | Smooth interpolated crossings could hide native resolution | P3 | resolution | June/December <4-cell flags retained; finite thresholds and grid brackets distinct from uncertainty. |
| 3 | Search window could look like measured current boundaries | P3 | profile sheet | Grey context window separated from orange crossings; full directional profiles and textual descriptions supplied. |

## BEACON

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | Hardcoded 2013 chart/title could misstate source year | P3 | UI | Rust chart year and JS profile link use actual source year; new 2012 and prior 2013 displays tested. |
| 2 | 30–130 km could be reported as annual current range | P3 | interpretation | Spread of twelve local monthly-mean profiles, no confidence or annual physical interval. |
| 3 | Reduced unassessed count could imply completed measurements | P3 | dashboard | Source-width count remains 136/72; South Australian current width and 89 published-length gaps remain unresolved. |

## HARBOR

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | Monthly selection might require pointer input | P3 | interaction | Existing keyboard selection and inspect controls exercised for new owner. |
| 2 | Color-only search and threshold meaning would exclude readers | P3 | figure | Panel titles, labeled profiles, SVG title/description and exact query JSON provide equivalent evidence. |
| 3 | Dense source data could break mobile layout | P3 | reflow | 320 px query/chart/source interactions checked; scientific profile sheet is a separate zoomable SVG. |

## KEEL

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | Rebinding a altered diagnostic and samples could pass shallow joins | P3 | integrity | Sixth frozen Rust report pin plus explicit owner and source bindings; HYCOM rebound rejected in WASM. |
| 2 | New grid could inherit OSCAR's 1/3-degree resolution rule | P3 | operator | HYCOM overrides native-spacing diagnostics to .08 degrees; independent WGS84/cell-span tests. |
| 3 | New generation could silently change earlier diagnostic data | P3 | regression | Separate source/generators; only new owner fingerprint changes; previous report/source bytes and seasonal frames preserved. |

## LOGBOOK

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | One PR per gap would fragment authorized work | P3 | delivery | Continue existing branch and draft PR83; no separate PR or merge. |
| 2 | Published-paper image exploratory output could escape without rights | P3 | public boundary | Only freely available HYCOM provider subset/metadata tracked; paper bytes/private exploration remain ignored. |
| 3 | Local green could be confused with remote CI or scientific approval | P3 | release | Final local test receipt separate from remote status; earlier source acquisition checksum failure not waived. |

## Synthesis and amendments

Seven roles; zero unresolved P1/P2 findings, 21 advisory findings.
APPROVED-WITH-CONDITIONS for editorial diagnostic publication only.
Shared CURRENT/SOUNDER/CHART condition: preserve model, layer, time, local
operator and unresolved association beside every estimate.

Implemented amendments: use actual year in chart/profile navigation; use
HYCOM's verified grid spacing instead of inherited OSCAR spacing; freeze new
source identity while preserving missing cells and unresolved current width.
Publication gates and Git state are recorded in the batch receipt after completion.

---
skill: roles-check
topic: ngcc-seasonal-vein-width
date: 2026-10-13
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
p3_count: 21
verdict: APPROVED-WITH-CONDITIONS
---

# NGCC seasonal vein descriptor review

Seven installed lenses applied internally to primary evidence, source
transcription, validation, query/atlas/seasonal views and publication receipts.
ORBIT is irrelevant. No delegation or independent scientific approval claimed.
Publication conditions: final complete offline suite and 203-source check pass.

## CURRENT

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | Current anomaly, cold water and velocity envelope differ | P3 | metric | Two explicit metrics; thermal span never replaces instantaneous current width. |
| 2 | Figure 3 variability threshold could be transferred to seasonal maps | P3 | operator | No threshold transfer; exact seasonal width boundary criterion remains unresolved. |
| 3 | Summer core displacement could imply a width range | P3 | season | 50 km shift, source cruise-label conflict and absence of compatible summer widths retained; no annual extrema. |

## SOUNDER

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | Regional descriptors could be treated as independent samples | P3 | claims | Three related current descriptors share one claim; western maxima are a subset of the range. |
| 2 | Native spacing could be confused with effective resolution | P3 | processing | 6.1 km sampling and 80/340 km filtering kept separate; no precision inferred from spacing. |
| 3 | Dates and source edition must be reproducible | P3 | provenance | Exact 23-page original, acquisition receipt, PDF hash and climatology context pinned; precise width dates remain null. |

## CHART

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | Static widths could become mapped occupied boundaries | P3 | atlas | Four point/interval charts accompany the existing editorial route; no new geographic edges or buffers. |
| 2 | Width ranges might imply confidence or temporal spread | P3 | interval | Caption preserves regional range meaning and null midpoint/uncertainty. |
| 3 | Existing direction playback could be lost or widened | P3 | seasons | Four static width phases excluded; two previous local direction phases retained and tested. |

## BEACON

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | Four records could be advertised as four measured currents | P3 | counts | Four scoped descriptors / one owner / two claim groups; no independent-replicate or whole-current claim. |
| 2 | Core offshore distance shares thermal span's numbers | P3 | explanation | 100–150 km location distinguished from thermal width in source context and frozen metadata. |
| 3 | Seasonal view needs an explicit metric in its heading | P3 | UI | Titles identify region and current-anomaly or thermal metric; captions retain seasonal and processing limits. |

## HARBOR

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | Meaning cannot rely solely on point/interval encoding | P3 | charts | Accessible SVG descriptions, numerical text, caption and source-query link accompany each graphic. |
| 2 | Static and playable phases need clear controls | P3 | interaction | Native phase selection and disabled playback for all four width records tested under reduced motion. |
| 3 | Long scientific scope notes can break reflow | P3 | mobile | Atlas and four inspector states checked at 320 px; source labels remain readable. |

## KEEL

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | Erasing a record could evade per-row guards | P3 | inventory | Native/WASM additionally require all four imported NGCC source descriptors and compiled source pin. |
| 2 | Coherent metadata edits could change scientific interpretation | P3 | validation | Frozen original rows reject midpoint, metric, owner, depth, date, uncertainty and context promotions. |
| 3 | Broader regressions need final stable artifacts | P3 | gates | Serialized engine build precedes browser/full suite; source pins and prior rows checked before publication. |

## LOGBOOK

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | A PR per descriptor violates user direction | P3 | workflow | All four descriptors accumulate in existing draft PR #83. |
| 2 | Unlicensed graphics could cross the public boundary | P3 | rights | Full PDF and original figures ignored; only factual annotations and independent charts tracked. |
| 3 | Local verification must not imply remote CI success | P3 | status | Prior-head Melet acquisition mismatch recorded; final local gates and new-head CI tracked separately. |

## Synthesis

Seven roles, no open P1/P2, 21 addressed P3 findings.
APPROVED-WITH-CONDITIONS for editorial delivery after final gates. CURRENT,
SOUNDER and BEACON agree on distinct metrics and overlapping source claims.

Amendments: preserve prose descriptors with source/metric grouping; retain
static widths alongside previous direction playback; require complete frozen
inventory and exact original provenance. Physical full-current width and
annual ranges remain separate unresolved scientific gates.

## Final publication gate

**1,336 tests and 957 subtests passed in 1239.89 seconds (20m39s).**
All 46 Rust tests and serialized locked native/WASM builds passed. Focused
source/inventory gate: 42 tests / 563 subtests. Final browser passed four
descriptors, two metrics and shared claims, native/WASM parity, atlas/source
access, 320 px reflow, four static width phases, two retained direction phases,
and three native/WASM rejection cases. Source-store browser passed all 203
exact documents, 12 seasonal snapshots, independent NOAA oracle, native/WASM
parity and checked-input failures. All 61 engine and 203 source pins verified;
all 31 local originals verified. Previous 132 rows, observation dates and
seasonal route frames retained; inventory CRLF and whitespace gate preserved.

Visual QA found the thermal interval's high label clipped in the shared SVG
renderer. Final supplemental browser checks verify horizontal label bounds;
the renderer fits close labels with small leader lines when needed. Numeric
values, markers and source interval meanings are unchanged. Point/current-
range/thermal-range captures were inspected after the fix. No original source
figure or PDF published. Internal editorial publication conditions satisfied;
physical full-current widths, mapped edges and annual ranges remain unresolved.

Final code review removed dependence on source-list position: the NGCC inventory guard locates its frozen source by stable owner identity. Rebuilt engine passed all 46 Rust tests; final native/WASM descriptor and 203-source browser checks passed again. Measurement and source bytes are unchanged.

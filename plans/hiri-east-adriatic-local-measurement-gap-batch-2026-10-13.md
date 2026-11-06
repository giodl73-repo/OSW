# Hiri and East Adriatic local measurement gap batch

2026-10-13. Continues the consolidated current gap branch and existing draft PR #83. Previous turn was progress: commit 237cce3 added three source-bound regional routes. This batch adds primary author measurement descriptors for two previously unassessed width owners.

## Numerical additions and their limits

| Current and source occupation | Descriptor | Value | What remains unknown |
| --- | --- | ---: | --- |
| Hiri under Hughes historical convention, July 1987 TEW287 A87 near Rossel | Author e-folding cross-section scale | about 50 km | Full edge-to-edge width, exact day, fixed width layer and numerical error |
| Hiri under the same convention, July 1990 Fr0690 eastern B90 | Author e-folding cross-section scale | 75 km | Full width, exact day, same-site comparability and annual range |
| East Adriatic inflow, C1 cruise 24-28 May 2017, Primosten southwest section | Author shore-to-inflow extent | about 10 km | Exact width occupation day, perpendicular correction and paired boundaries at each sampled depth |

Hiri source naming is local and historical. Hughes introduction p13 / PDF29 explicitly calls chapter 3 Hiri; chapter 3 uses a broader Coral Sea NGCU convention under presumed Vitiaz connectivity (p45 / PDF61). Only southern-Papua study reaches are indexed here under that Hiri convention. No modern north-coast NGCU alias, complete Hiri circulation identity, or transfer of its dimensions is admitted. The 0-1500 dbar transport integration and 1990 core depth 350 m do not define a fixed width layer.

An e-folding scale describes decay across a section; it is not full current width, a Gaussian sigma, a half-width or a statistical margin. The two July cases differ in year and reach. The 50/75 values are not endpoints of an annual range. Source typical 70 km, 120 km coast confinement and 160 km core offset remain different contextual descriptors. No numerical multiplier converts these values into full widths.

East Adriatic ADCP sampled 10-70 m with 4 m bins. Surface-drawn vectors represent 10 m. The prose 10 km limit belongs to cruise C1; the plotted section is 28 May 2017, but no exact occupation day is assigned to the width prose. The source's 20 km upwelling/pycnocline extent and C2's 10 km pycnocline rise are different objects. June 2018 C2 provides no second numeric current width. Conference evidence is labelled as an authored abstract, with no raw ADCP/CTD field reconstructed.

## Exact originals

- Hughes (1993) thesis: university-hosted complete original, 10,817,128 bytes / 306 pages, SHA256 `587b39c55e7bdc9f2256e0c1d1634c504d4f7562bd5e0a9681e27300907a955d`. Source title/authorship/access statement and relevant introduction, methods, text and figures reviewed. Visually inspected width/naming context pages 29,61,62,85,86,89,91. Author access conditions are retained in acquisition metadata; no PDF or figure redistribution.
- Pasaric et al. (2019): publisher-hosted CIESM volume 42 original, 101,647,086 bytes / 290 pages, SHA256 `dacc8e17c91b6cf5404a9e512f98e9f29047929ade0fb57862790f6315bc2ae5`. Reviewed the complete authored abstract on printed/PDF38, including Figure 1. Whole volume has not been reviewed. Original preserved outside Git; factual annotations and source link with page 38 anchor only. No smaller synthetic extract substitutes for the original pin.

Original acquisition hydrator includes both sources with exact SHA checks. The CIESM source alone has an explicit 110 MB limit to accommodate its complete 101 MB volume; format, integrity and other source limits are unchanged.

## Integration and invariants

Width inventory now 131 scoped records across 70 of 100 current owners; 21 unassessed. Published ranked lengths remain 11; reference routes remain 67 across 64 of 89 owners lacking published lengths. Previous 128 scoped measurements are byte-equivalent as JSON objects; 98 other current decisions are unchanged. Canonical scientific release rows are unchanged.

Source audits freeze complete measurement rows. Python checks identify known records from owner or immutable ID, independently of editable context. Rust/WASM compiles both reviewed audits into the existing original-regional guard. The tests coherently rewrite both source receipts and shared collections before attempting scope promotions, so failures demonstrate compiled scope protection beyond transport hashes.

Dashboard owner fingerprints change only for East Adriatic and Hiri. Existing seasonal route frames change only width_inventory_sha256, with geometry/calendars unchanged. Native/WASM query bundle retains 42 collections, now 131 scoped width records. Four new annotation/acquisition documents join the lossless index, now 172 exact sources. Source originals remain excluded from Git and the public index.

Atlas cards show each point with its metric and naming/date limits. Static inspectors show the source-specific title and metric; bar and annual playback remain disabled. Source query deep links resolve into the frozen audit rows. Existing route maps remain editorial geography, with no occupied width polygon, physical state containment or NASA identity inferred.

## Reproduction and gates

Run `python analysis/build_hiri_east_adriatic_local_widths.py`, then `python analysis/check_hiri_east_adriatic_local_widths.py` and the inventory checker. Review/refresh the seasonal frame's width dependency receipt, then rebuild dashboard, lossless index, query bundle and serialized Rust engine. Do not rebuild native/WASM while tests use them. Any annotation revision requires re-review, refreshed frozen audit SHA and regenerated downstream receipts.

Focused verification before final copy cleanup: 69 tests / 538 subtests passed (117.67s), including 12 coherent native rejections. Serialized final engine build: 45 Rust tests passed. Initial browser run passed all three descriptors, static inspectors, source/native parity, 320px reflow and three WASM rejections. Source naming/metric caveats and two mobile cards visually inspected; spacing in captions corrected and final browser run repeated. Final full-suite and browser receipts follow after completion.

The first complete run reported 1 stale test assumption: the section-transport regression expected zero Hiri width records. All other 1,318 tests and 925 subtests passed. That assertion now checks independently sourced width inventory coverage and verifies the transport record is absent from width records; the corrected targeted test passed in 12.03s. A fresh complete run follows; no production artifacts changed for this test correction.

## Final stable verification

- Fresh complete offline suite: **1,319 tests / 925 subtests passed in 924.16s (15m24s)**. The outdated transport/width coverage assumption is corrected without changing production records. The earlier run's failure is retained above.
- Final serialized native/WASM engine: **45 Rust tests passed**, locked builds passed. WASM 2,568,796 bytes; query bundle 47,631,613 bytes. All 60 engine pins matched final source files.
- Final browser: three source-specific point descriptors, static phase titles and metrics, disabled annual play/bar, source/native parity, 320px reflow and three compiled WASM scope rejections passed. Both mobile cards visually inspected.
- Lossless index browser: 172 exact sources / 12 seasonal snapshots, independent NOAA oracle, native/WASM parity and checked-input failure cases passed. Index 77,253,424 original bytes / 5,540,143 compressed bytes; current source hashes verified.
- All 128 prior measurements and 98 other current decisions unchanged. Only East Adriatic and Hiri owner fingerprints change. Current ledger, length evidence, reference route catalog and scientific release unchanged. Seasonal frame changes only width receipt.
- Seven role lenses reviewed 21 findings; 0 P1/P2. Editorial delivery conditions satisfied. Physical full widths, annual ranges, source-specific naming equivalence and canonical scientific admission remain unresolved.

Publication continues on the existing draft PR #83. No new PR per measurement; this is an accumulated current gap batch.

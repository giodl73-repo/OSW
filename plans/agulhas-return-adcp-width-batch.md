# Agulhas Return Current: four ADCP crossing widths

2026-10-08. Editorial source extraction, not canonical admission.

## Evidence and measurement rules

Original Boebel et al. (2003) Table 1, printed p.41 / PDF p.7, gives:

| Crossing | Width (km) | Total error (km) | Included projection component (km) |
|---|---:|---:|---:|
| Leg a | 48 | ±14 | 1 |
| Leg b, first crossing | 73 | ±18 | 6 |
| Leg b, second crossing | 78 | ±18 | 1 |
| Leg c | 48 | ±18 | 17 |

Section 3.1, pp.40–42, defines each as a median across ADCP depth bins of
half-maximum isotach distances projected normal to each bin's maximum velocity.
The deepest described bin is 325–375 m (center 350 m). This does not establish
width at a fixed surface depth or a uniform 0–1000 m layer. The latter belongs
to a separate transport estimate. ADCP is acoustic Doppler current profiler.

Preserve 1997 cruise 97/04 context, without guessing crossing dates from the
1997-08-23 SSH image or cruise end offset. Crossings b2/c were about one day
apart; neither is a seasonal observation. Locations remain prose context.
No threshold boundary coordinates, occupied footprints or route buffer admitted.

Total errors remain separate from width ranges. Source positional and projection
components already contribute to those totals; do not add projection again.
No confidence level stated. A source ± allowance is not a seasonal envelope.
The summary ~70 km and profile normalization to 70 km are not fifth measurements.
The paper's 62 ±9 km aggregate is excluded: its statistic interpretation is
unresolved relative to the four table widths. Original PDF and rendered Table 1
were inspected, rather than using the preliminary poster's different values.
Original 22-page PDF: 3,243,676 bytes; SHA256
 a7b2701cee8584dea6ce137fabd8aea2a72ce7ca16440b29fa06e704321e8ce9.
Restricted PDF remains an ignored local research copy; source URL/checksum stored.

## Integration

Four complete records and context bind to the source audit. Protocol v1.23
introduces layer-median threshold widths and distinct source errors. Python
validates exact source rows; Rust guards the scalar/error/threshold, dates,
layer and eligibility fields even after coherent receipt rewriting.
Atlas cards and the seasonal explorer show source errors. Four-point comparison
uses explicit error whiskers, axis/units, source, date context and caption.
No full-width bar, edge locator, annual range, ranking or seasonal play enabled.
Queries retain complete source metadata and native/WASM equality.

Coverage: 78 scoped width-related records across 39 current owners, 54 unassessed.
These are heterogeneous scoped metrics, not 39 whole-current widths.
Source index: 81 documents; 39 query collections; 240 dashboard objects.
All 74 previous measurement rows and six seasonal frame objects unchanged.
Three Gulf Stream/Loop section diagnostics changed only general_protocol_sha256.
The width inventory's protocol receipt and upstream seasonal width receipt
were rebound; no scientific samples changed.

## Receipt correction

The standalone width check caught a stale protocol_sha256. That receipt was
already stale in the preceding snapshot after protocol v1.22; shared validate()
did not check it. The receipt now matches v1.23 and shared validation checks
it for every builder/test caller. A regression rejects stale hash/file values.
Full tests on a preceding head had therefore not proved this particular gate.
The initial build completed before this correction; all bundles and native/WASM
outputs were rebuilt afterward. Only final outputs are shipped.

## Validation and publication

Final native/WASM build: 38 Rust tests passed. General query browser parity
passed with 42 scoped-capability objects (including derived candidates).
Expanded range browser passed four crossing selections, four source records,
complete native/WASM row equality, 320 px reflow and three coherent source/row
rewrites rejected by Rust. The initial mobile screenshot was visually inspected;
final date/acronym text edits passed the final browser rerun. Its final
full-page 320 px screenshot was visually inspected.
39 JavaScript syntax checks and 14 page assignments pass (assignments are not
test results). Full suite: 823 tests and 729 subtests passed in 235.85 seconds.
Final date/acronym/text-size assertions were added after that run; the browser
rerun passed these final presentation changes, including the text-size check.

The preceding publication coverage run passed its final 27 registered browser
checks across two resumes, including every state/date source inventory. It
precedes this scientific batch and does not establish final-head full coverage.
PR30 exact head 0ff10d0 was open with active CI and human-enabled auto-merge.
This new batch will be a dependent draft; main and scientific admission pending.

Reproduce:

```powershell
python analysis/build_current_section_width_series.py
python analysis/build_loop_current_section_spans.py
python analysis/check_current_width_inventory.py
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
python -m pytest analysis -q
python analysis/test_black_sea_regional_width_browser.py
python analysis/test_rust_query_browser.py
```

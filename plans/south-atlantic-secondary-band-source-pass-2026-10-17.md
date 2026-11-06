# South Atlantic October1983 southern component breadth

Continues from fully validated South Pacific data checkpoint62f2a2b and
receipts3df64bf on the same branch /draftPR83. No merge or new PR.

## What is admitted

The unchanged14-page Stramma and Peterson (1990) original reports a200 km
southern SAC band at the Knorr1 E section in October1983. It carries only
part of the SAC flow; the primary surface front carries additional flow.
This is a source-reported local component breadth. Total SAC width and the
diameter of its secondary core remain unknown.

The reference is sigma4=45.87 kg/m3 at3470–3560 m. The upper1000 m is
transport/field context, not a uniform width slab. The primary-front station
bracket, secondary-core latitude and200 km core displacement are not paired
width edges. Source-rounded8 Sv /17 Sv transport context and Table2's8.3 Sv,
8.8 Sv and-1.4 Sv remain separate contextual quantities, not width errors.

Exact days, width-evaluation depth, numerical cutoff, geographic boundaries,
uncertainty, whole-current breadth and seasonal/annual extrema remain unknown.
No zero-to200 interval, route buffer or seasonal interpolation is admitted.
The historical component is kept separate from modern30 W surface diagnostics.

Original pages851,853,854 and855 were visually inspected. OCR was a locating
aid only. The ignored original retains SHA256
f8a926976c10b79227eabbfb28e1d30ae0fe97a87deab2875dfe0abe22af2716.
Git contains factual annotations, acquisition receipt, protocol and independent
statement graphic; no copyrighted source pages or original PDF.

## Integration and evidence

-148 scoped width records /78 owners, including71 with numeric descriptions
 and7 with qualified constraints only. These are not whole-current dimensions.
-274 indexed JSON documents;45 collections;35 diagnostics;25 series.
-All147 prior width rows and34 diagnostics compare equal.41 other collections
 compare exactly. Seasonal-route rows and four other cards change only their
 parent inventory hash. Only the South Atlantic scientific card changes.
-271 width samples,75 routes, all canonical collections and all prior series
 remain unchanged.
-26 source tests pass in0.74s; combined source/Southern-inventory check27 tests
 passes in1.31s.47 Rust tests pass in1.79s.
-Actual atlas/seasons/query/source/inspector/mobile parity passes, with retained
 local diagnostics and nine coherent native/WASM rejections. No PDF requests or
 seasonal playback. Mobile card and independent graphic visually inspected.
-WASM3,335,468 bytes; query bundle71,823,564 bytes. Engine has71 dependency hashes.
-The new browser check is first in the standard shipped-WASM runner.

These are current-batch checks. The preceding147-record baseline separately
passes1512 tests /1061 subtests in2210.98s, all45 collections and all100 cards.
Do not attribute that earlier full run to this added record. The complete new
offline gate must be recorded after the clean data commit.

## Remaining work

Full updated-data publication validation and final role verdict remain pending.
Remote CI currently passes changed South Pacific/Radenac/Qiu acquisitions but
stops at the unchanged VanAken2003 Reading source with connection refused.
An official KNMI copy was found, but its bytes and producer differ; it has not
been admitted as a byte-identical mirror and no pin was relaxed.

Local logs: `.pytest_cache/south-atlantic-component-preparation/`.
Rebuild with dashboard, index bundle, query bundle, then Rust/WASM engine;
never rebuild while validation uses the executable. Run the dedicated source
tests and `analysis/test_south_atlantic_secondary_band_browser.py`, then the
full offline suite from a clean committed checkout before final approval.

# Kuroshio normal-span integration — 2026-10-21

Continues `codex/current-measurement-gaps` and draft PR #83. No new PR or
main merge. The overall current measurement gap-filling goal remains incomplete.

## Delivered

- Bind the frozen scientific report to `current_axis_normal_samples`: 16,470
  attempts, 14,034 resolved and 2,436 unresolved. The primary 14 km tangent
  half-window resolves 4,680 of 5,490 attempts. Unknown uncertainty, threshold
  attainment and boundary fallback remain null. No physical width admission.
- Preserve source IDs, semantic case IDs, rejected cases and exact source JSON.
  Validate every projected row, edition, dependency, diagnostic and current owner
  in Rust before queries. Old snapshots without the new edition remain readable.
- Extend the existing query, atlas, current card and seasons component with
  metric and 7/14/28 km tangent controls. Share and return links preserve all four
  selectors. Global and local maps use Rust-projected geodesic normal segments;
  unresolved sections produce no segment. Switching currents clears overlays.
- Present selected-day status, annual and selected-month available-sample ranges,
  counts and same-day method sensitivity. Ranges are not confidence intervals,
  climatology or physical annual bounds. Velocity normal and ocean connectivity
  remain unverified. Gold lines represent model geometry, never occupied ribbons.
- Add the exact report, figure receipt and typed contract to source queries:
  418 index documents. The dashboard lights one current for normal-span evidence;
  only Kuroshio's measurement/time fingerprints change among current owners.

## Checks and limits

The integration has 50 collections and 59,824 rows. All previous rows and other
dashboard owners were compared to `99892a4`: unchanged except Kuroshio owner
capabilities/links and the additional diagnostic. All 6,588 old regional model
attempts, physical inventories, state joins and canonical release files remain
unchanged. There are still 101 accepted current names, 28 proposals, 12 qualified
ranked lengths and 157 scoped width records across 83 owners. The new model
spans do not reduce the 89 unranked identities or 18 owners without scoped width.

Focused Python: 28 tests and 18 subtests pass. Rust: all 103 tests pass.
All 65 top-level almanac JavaScript files pass syntax checks. Native validation
reads the previous full snapshot, verifies all 107 atlas source documents
against file bytes and preserves missingness in all 540 displayed normal cases.
The actual normal browser gate verifies native/WASM parity, exact source access,
selector synchronization, share/return links, keyboard, 320 px reflow, reduced
motion and the one-owner dashboard metric. The existing regional browser gate
also passes, including its dated maps, source queries, seasons and playback.
Desktop/mobile screenshots were
inspected; gold contrast and table width were corrected before the final gate.

The immutable scientific report still hashes to
`9e0c4cbbd62426c68aa29c45149106fbdbf52ed2ca159b852c912f5572a13346`.
Its producer and figure remain unchanged from the 23-report byte-exact Linux
reproduction recorded at `93a854b`; that is source evidence, not a claim that
the new integration has passed every CI job. The latest complete local Python
suite remains the older `774e466` baseline. A fresh whole-suite run is not
claimed; free disk space is below its 4 GiB guard. Release gates remain open.

The logical packet is 139,720,931 bytes in nine checked parts. Seven superseded
generated parts were retired; original scientific files remain. The final WASM
is 48,287,854 bytes. A shared static source string removed two duplicated 22 MB
copies from an intermediate build. Source upload limits remain 512 MiB; loading
still materializes the full snapshot, so this is not a lazy-loading solution.
All 345 staged engine dependencies were checked against their manifest hashes.

## Reproduce

```powershell
python -m pytest analysis/test_kuroshio_axis_normal_query.py analysis/test_kuroshio_axis_normal.py analysis/test_kuroshio_wang_query.py -q
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
$env:OSW_TEST_BROWSER='C:/Program Files/Google/Chrome/Application/chrome.exe'
python analysis/test_kuroshio_axis_normal_browser.py
python analysis/test_kuroshio_wang_query_browser.py
```

Use the existing checkout server on port 8788. Build commands are sequential:
the source index must follow the dashboard, and the engine must follow the
packet. Browser checks are registered in the common UI runner.

## Next

Continue current length, width, date/depth and uncertainty gaps on this same PR.
Other 1993–2023 years and the other 27 source levels remain unextracted; these
three-depth 2024 results establish no whole-current or long-term inventory.

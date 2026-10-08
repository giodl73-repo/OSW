# Gulf-of-Alaska coastal current: typical width

Date: 2026-10-08. Working editorial source summary, not canonical admission.

## Evidence and result

Jarosz et al. (2017), doi:10.1002/2016JC012102, Introduction, describes a
typical approximately **35 km** width for the Gulf-of-Alaska coastal current.
This is literature context in an observational paper. Its winter experiment
does not supply the observation dates, depth or paired boundaries of this
particular width statement. Publisher full-text HTML Introduction and abstract
were inspected; no source figure, original width observations or PDF acquired.

The new record uses the existing regional scalar summary class. Range, section,
measurement depth, occupation dates and calendar months remain null. Annual
extrema, playback, whole-current representation and width ranking remain false.
The Gulf shelf current is distinct from the offshore Alaska Current, Alaskan
Stream and the Arctic/Bering namesake. The reported 35 km is not an offshore
distance, a transport integration window or a seasonal maximum.

Coverage: **73 records for 37 current owners; 56 owners remain unassessed**.
Exact comparison against the preceding commit confirms all 72 prior width
records and all six seasonal frame objects unchanged.
All 72 earlier measurement records remain unchanged. Route coverage stays
63 candidates for 60 unranked owners. There are still 240 dashboard objects
and 39 query collections.

## Query and visual integration

The existing seasonal explorer displays a regional summary, with no full-width
bar, edge locator, seasonal playback or annual range. The record is queryable in
Rust/WASM and linked to its source. Its audit and the existing Labrador and
East Australian scalar audits are registered for lossless source queries:
the index now has **79 documents**.

Scalar audit receipts are now included in both the query bundle inputs and
dashboard source fingerprints. This strengthens provenance for all three scalar
owners. The width validator also binds the boundary wording to the source audit.
The six seasonal route frames only refresh the width-inventory checksum; their
scientific content is unchanged.

## Validation and corrections

The first bundle build rejected the old seasonal-width inventory checksum.
After confirming all six frame records unchanged, the basis was refreshed.
The first Labrador browser check asserted before WASM initialization finished;
it now waits for the rendered summary heading and exercises the new Gulf record
at 320 px plus complete native/WASM query-row equality.

Full local suite: **818 tests and 628 subtests passed**, 212.14 seconds.
The final runner default-path insertion and two new runner regression tests
follow that full run; both tests and two subtests pass on the final runner.
The expanded regional-summary browser check passed, including the 320 px
Gulf record and complete native/WASM row equality. General query and dashboard
browser checks passed, including all 240 objects, integrity rejection cases,
updates and mobile behavior. The final Gulf width screenshot was recaptured
with the summary visible and visually inspected.

The native/WASM build passed,
including 38 Rust tests; JavaScript syntax and all 14 page assignments pass.
Assignments do not prove that all 52 registered browser checks ran locally.

Reproduction:

```powershell
python analysis/check_current_width_inventory.py
python analysis/check_current_seasonal_route_frames.py
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
python -m pytest analysis -q
python analysis/test_labrador_regional_width_browser.py
python analysis/test_rust_query_browser.py
python analysis/test_motion_dashboard_browser.py
```

Review: `signals/roles/check/alaska-coastal-gulf-width-roles-check-2026-10-08.md`.

## Browser publication correction

The previous consolidated CI failure exposed a required browser override in
individual scripts. Twenty-nine later scripts still use that variable directly.
The shared runner now resolves Playwright's installed Chromium executable when
the override is absent and passes it consistently to every child. Explicit
user-selected browser paths remain honored. Default Chromium is not installed
on this local machine, so CI must confirm the default launch. Local checks use
the installed Chrome override.

## Remaining work

Review original width definitions and obtain paired repeat sections before
regional seasonal extrema or whole-current dimensions. Many other widths,
route axes, eddy footprints and physical state joins remain unresolved.
Protected-main publication is still subject to required exact-head CI.

The first attempt to insert the shared browser default did not match the
runner file newline convention. Inspection caught the missing diff; final
insertion is verified by the two environment-propagation regression tests.

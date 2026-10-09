# Tsushima coastal-branch modal width batch

## Evidence

Masaji Matsuyama (1990), *The Structure of the Nearshore Branch of the Tsushima Current on the Shelf off the San’in Coast in Summer*, Journal of the Oceanographical Society of Japan 46(4):156–166, DOI [10.1007/BF02125576](https://doi.org/10.1007/BF02125576).

Complete publisher original: 11 pages, 1,772,559 bytes; SHA256 `513c7b63658ab04c8e5157d414743d249ba919176d4682dbe8df4b72ab9ced55`. Fresh request with the acquisition helper's actual User-Agent matches the pin. Copyright retained; original ignored. Source equation, method, station dates and contradictory longitude caption visually reviewed.

One editorial record: reported **22 km** offshore decay estimate for the nearshore shelf branch during the 1980 campaign. The adopted edge is `exp(-3)` of coastal modal amplitude. The printed coefficient `1.3e-4 m^-1` calculates **23.076923 km**; the summary gives **about 20 km**. Preserve all three meanings and the unresolved arithmetic discrepancy. No interval or additional independent measurement inferred.

Additional original-method finding: p161 Eq8 prints a plus-sign offshore equation but claims an exponential decay solution. For real positive gamma, substituting that expression gives a nonzero residual. Record this as an editorial consistency check, leave the sign unresolved, and label the diagram as an illustration of the published exponential expression. No silently corrected equation or validated source derivation is claimed.

Campaign July26–August25; A/B cover this period, C/D/E end August14. Five-station mean uses July26–August14; H hydrographic profile August8 feeds the mode eigenvalue problem. A single homogeneous width interval remains unassigned. Separate 1964–1985 climatology has a 134°E caption /132°E Discussion conflict and is excluded from width support. No recurring calendar, fixed layer slab, mapped edge or numeric uncertainty assigned.

## Implementation

- Dedicated `campaign_modal_decay_width` phase and `modal_decay_context`; accumulated rules in campaign-modal-decay-width-protocol-v1.md.
- Strict reviewed source/audit/protocol/acquisition pins; Python and unconditional compiled Rust owner guard retain every operator and conflict.
- One model decay diagram and separately labeled values on atlas map card and width inspector; lossless source-query navigation.
- Tsushima dashboard entry updates its source, measurement and time-context fingerprints; no monthly width samples are created.
- Local coverage **97 width records /53 owners /39 unassessed**. Earlier width records and seasonal map frames unchanged. The 89 current length gaps and named-eddy footprint gaps remain.

## Reproduction

```powershell
python analysis/acquire_local_paper_fixtures.py
python analysis/check_tsushima_modal_width.py
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
python -m pytest -q
python analysis/check_almanac_javascript.py
python analysis/check_almanac_page_coverage.py
$env:OSW_TEST_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
python analysis/test_tsushima_modal_width_browser.py
```

Reuse a server at 8788 serving this checkout for individual browser checks. CI runs the registered check through `run_rust_query_browser_checks.py --start-server` with installed Chromium.

## Review and publication

Seven selected role lenses; 18 P2 issues addressed, 3 P3 notes retained, no P1. Internal approval with conditions does not grant scientific admission. Work targets a draft atop PR59, not a merged mainline claim.

Parent PR59 remote offline job 113686827056 (run37889455216) failed acquiring the preexisting Qiu/Chen NEC source after three connection timeouts, before tests. Both parent NetCDF jobs passed. Local source availability and local test results do not establish that remote gate passes.

Validation:

- Full offline baseline: **900 Python tests /918 subtests passed** before the additional Eq8-sign context amendment.
- Final amendment: **71 focused Python tests /551 subtests passed**, including the new equation conflict and all inventory/dashboard checks. One local NumPy binary-size warning was reported; no test failed.
- Final build: **41 Rust tests passed**, native and WASM built with the amended audit compiled in. WASM 1,939,112 bytes; query bundle 46,111,172 bytes. Every engine input hash verified.
- Final registered browsers: Tsushima (map/inspector/mobile/source and native/WASM parity, coherent native and direct WASM rejection), seasonal snapshot, and motion dashboard. Generic query browser passed before the Eq8 context amendment; no claim that the entire registered browser list was rerun here.
- All **48 JS modules** and **14 page validation assignments** pass. Assignments are separate from executed checks.
- Prior width records and seasonal geometry frames unchanged; only Tsushima dashboard owner entry changes. Lossless source corpus: 116 documents /76,320,553 original bytes /5,436,605 compressed bytes.
- Mobile method panel visually reviewed; source original remains excluded from Git.

Draft publication identifiers are recorded in the handoff after push; remote checks are a separate pending gate.

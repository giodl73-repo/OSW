# Western Adriatic radar width batch

2026-10-09. Stacked on Baffin draft PR64. Chavanne et al. (2007), JGR 112
C03S21, doi:10.1029/2006JC003523, supplies two local mean width values:

| Location | Width | Support |
| --- | --- | --- |
| Off Ravenna | 40 km | Mean alongshore flow, cross-shore section AA' |
| Off Pesaro | 50 km | Mean alongshore flow, cross-shore section BB' |

Section 5 paragraph 30 spans PDF6-7. Figures 13-14 on PDF14 show the mean
vector field and cross-shore profiles. Figure 15 on PDF15 averages velocity
from the coast to no mean flow, with seasonal velocity fluctuations. Neither
figure supplies a seasonal width time series. The 40/50 difference is between
locations and cannot become a 40-50 km annual or confidence interval.

Deployment spans October 2002 to October 2004, but site coverage differs;
Figure 2 shows no early Ravenna observations. Exact valid times, mean weights
and local sample counts are unresolved. The approximately 1 m effective radar
depth is not a fixed layer. Vector grid, search radius and range resolution
are separate processing quantities, not width uncertainty. The compared tidal
model lacks the observed mesoscale current; these are observed radar means.

The tidal discrepancy strip, velocity confidence ellipses, peak velocities and
offshore peak positions are distinct from width. Figure 14 and Figure 15 define
opposite signs for southeastward velocity; those source conventions remain
separate. No merged curve, repaired sign or inferred width sample is supplied.

## Original and integration

Selected PDF pages 1,2,3,6,7,14,15 visually inspected. No full-paper review,
raw field reconstruction, profile digitization or coordinate extraction.
Original is 2,524,809 bytes /18 pages, SHA256
`ebb25a7d586df892886aa028bc4304f93f41ec0aa1d84629d7c54d46627fe3e5`.
Copyright AGU 2007; no redistribution license established. Original stays
ignored, with acquisition receipt and attributed factual extraction tracked.

Inventory becomes **105 scoped records /57 owners /35 unassessed**. The 103
prior records remain unchanged. Atlas and inspector show separate mean-width
diagrams and exact source array pointers. Source index has 126 documents;
all 39 query collections and 240 dashboard objects remain. Seasonal playback,
canonical width/length ranking, current edge geometry and state joins are not
admitted by this evidence.

Python binds original, acquisition, protocol, audit and full rows. Compiled
Rust uses its shared identity registry and array lookup, now covering eleven
original-regional owners. Adversarial checks include recomputed source receipts
with scope edits, invented fixed layers and context deletion/owner transfer.

## Verification

Rebuild dashboard, source index, query bundle and native/WASM engines. Run
the complete default Python suite, locked offline Rust suite, registered
Western Adriatic browser check and prior Baffin regression. Verify source
and engine pins, prior record/route compatibility and mobile screenshot.
Results are appended after execution.

### Verified CI build-order fix

PR64 offline run 37902887498/job113729329476 successfully acquired sources,
then failed 11 Python tests with FileNotFoundError for the native CLI. The
workflow built Rust only after pytest. Move the existing pinned 1.95.0 Rust
test/build steps before both Python gates. No test, integrity check, dependency
pin or source acquisition rule is weakened. Local validation already builds
native/WASM before running the full suite. Fresh remote outcome remains pending.

Overall core gaps remain: 89 currents lack admitted published ranked lengths,
35 width owners remain unassessed, and most named-eddy and seasonal geometries
remain unresolved. Local validation and draft publication do not establish
mainline or remote gate completion.

### Completed verification

- Full default Python suite: **1,004 passed /918 subtests**, 343.49 seconds.
- Locked offline Rust suite: **41 passed**; native/WASM engines rebuilt.
- Western Adriatic registered browser: both mobile diagrams and phase/source
  links, native/WASM source/query parity, unsupported playback/edges absent,
  coherent loader scope rejection and combined context/owner rejection pass.
- Existing Baffin registered browser regression passes after the new source.
- Western Adriatic mobile screenshot visually inspected; readable labels,
  distinct source captions and no clipping/document overflow.
- Fresh original download matches its 2,524,809-byte SHA256 pin.
- Scope audit SHA256:
  `61d4d2dfdccb2c51c70d0487ab393a7359bb5b75b8ac5d0d89e7c8adf12ee9fa`.
- Prior 103 width rows, other decisions, canonical ledger and route catalog
  preserved. Seasonal frames change only their width-inventory dependency pin.
  Only Western Adriatic dashboard entry changes. Engine manifest pins pass.
- Both PR64 offline jobs were inspected: each failed the same 11 tests because
  the native CLI did not yet exist. Both NetCDF jobs passed. The workflow order
  fix is included here; fresh remote CI remains pending.
- Pinned Rust 1.95.0 built a native CLI offline in a fresh isolated target
  directory. The 11-owner alias regressions plus Baffin and Western Adriatic
  native scope guards all passed against that fresh executable: **13 tests**,
  55.75 seconds. This verifies the build-before-test precondition locally;
  it is not a claim that the pending Linux workflow has passed.

Reproduction (after acquiring local originals):

```powershell
$env:CARGO_INCREMENTAL='0'
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
python -m pytest -q
python analysis/test_western_adriatic_mean_widths_browser.py
python analysis/test_baffin_regional_widths_browser.py
```

Browser commands use the verified checkout server at 127.0.0.1:8788 and the
configured Playwright Chromium executable. CI uses its pinned native toolchain
and installed Chromium, building the native CLI before the Python gates.

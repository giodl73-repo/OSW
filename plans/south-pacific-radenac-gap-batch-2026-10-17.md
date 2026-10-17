# South Pacific constraint and Radenac source edition

Data commit: `62f2a2bfbe94913ffb9d9eab9b1a1ac8129eed06`.
Same branch `codex/current-measurement-gaps`, same draft PR83. No merge.

## Scientific addition

Stramma, Peterson and Tomczak (1995), *The South Pacific Current*, original
p82, Table1(d), Table2(d), Figure3: an enhanced eastward relative-geostrophic
band reported less than200 km wide near nominal170 W in March1990.
The reference is sigma2=36.75 kg/m3, at1800–1840 m. The upper1000 m field
plot is contextual; the exact width evaluation depth and edge cutoff remain
unknown. Exact days, lower bound and numerical error are unavailable.

The paper's100 km transport sensitivity assumption, greater-than500 km
separation from northern ACC flow, front station bracket and peak velocities
are not width measurements or boundaries. The new record supplies no point
estimate, zero-to200 interval, geographic footprint, ranking or annual range.
March1990 is month precision, not an invented full-month occupation interval.

The original15-page image-scan PDF is checksum pinned and ignored. Original
pages were visually reviewed; OCR located passages only. Git contains the
acquisition receipt, factual scope audit, protocol and independent SVG.
The existing atlas and seasons card render the constraint and source query;
the older local component climatologies remain independently accessible.

## Repository-generated Radenac cover

Remote CI on2efe752 failed while acquiring the Radenac2016 original because
HAL regenerated its cover. The retained reviewed original response remains
unchanged at SHA2566da50667b80790752fa0189ff9cf0cdfd88c521509b0f393365de306286bacbe.
The independently acquired response SHA256 is
edfbc33ecbbba856cf3249b5014c41282353eef7b6a58ff5c41da779719bb328.
Its22 article pages,394 article objects, page order, raw streams and resources
match the reviewed edition. Article graph SHA256:
fe9a7071fe427195d563a0bc2a84752875ddd88b94252ca6b9aaa46e1b72ca34.

The frozen contract permits14 observed wrapper objects, bounded metadata
changes and the same cover text; its allowlist is disjoint from the article
objects. All other object identities and content remain protected. Fresh
responses are stored separately as `repository-current.pdf`. Corruption of a
retained original cannot fall back. Existing four NGCC measurements and their
audit remain unchanged. Builders bind the verified edition contract rather
than mislabeling fresh response bytes as the historical original checksum.

## Integrated coverage and gates

-147 scoped width records /77 current owners;100 named current cards.
-272 indexed JSON documents;45 collections;34 diagnostics;25 series.
-271 width samples and75 reference routes remain unchanged.
-All146 prior width rows and33 prior diagnostics compare equal.
-41 other collections compare exactly; six seasonal route rows change only
  their parent inventory hash. Four other cards change only that same hash
  inside seasonal map features; their geography and science remain unchanged.
-60 focused source/acquisition tests and20 subtests pass in6.81 seconds.
-39 inventory/climatology tests and538 subtests pass in406.77 seconds.
-Fresh-only source tests:20 tests /13 subtests pass using an actual separately
  acquired HAL response, without the historical original file.
-47 Rust tests pass in1.85 seconds.70 engine dependency hashes verify.
-WASM3,325,364 bytes; query bundle71,792,333 bytes. Staged bytes match disk
  exactly for all31 data/code files. No original PDF staged.
-Actual South Pacific atlas/seasons/query/source/inspector/mobile parity passes;
  all nine coherent native/WASM alterations reject. No PDF requests or seasonal
  playback. Mobile card and independent figure visually inspected.
-Actual NGCC browser regression passes all four unchanged descriptors, both
  distinct metrics, static phase handling, mobile and three native/WASM rejections.
-JavaScript syntax passes for55 almanac files;14 pages have validation assignments.

At this checkpoint the complete offline suite is running from clean62f2a2b;
Retained southern climatologies, all-collection and all-card browser
regressions are also in progress. These gates are not claimed as passing yet.
Logs are local under `.pytest_cache/south-pacific-constraint-preparation/` and
`.pytest_cache/radenac-cover-review/`. Update this receipt when terminal.

Reproduction:

```powershell
python analysis/acquire_local_paper_fixtures.py
python analysis/check_current_width_inventory.py
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
python -m pytest analysis -q
python analysis/run_rust_query_browser_checks.py --start-server
```

Never rebuild the native executable while validation uses it. Existing
loopback-server users should omit `--start-server`. No claim of complete
current measurement coverage follows from the scoped-record count.

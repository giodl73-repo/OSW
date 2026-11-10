# Caribbean current measurement gap batch

Current-only gap filling, based on main `19148702de6433253dbf412a0a28c0cb4f8e409e`.

## Result

Added one author-reported Caribbean mainstream span: approximately **410 km**
at **67 W in October 1974**. Associated geostrophic surface speed is **0.66 m/s**,
retained as source context. The described section fixes its southern limit at
Los Roques, 12 N; paired velocity edges and perpendicular-axis correction remain
unreproduced. The 1600 dbar reference is not a width depth slab.

The separate historical width range ends in unqualified miles. Its numerical
endpoints and unresolved units remain inspectable; no normalized range or annual
margin is admitted. Typical 60-nautical-mile station spacing is not an error bar.
The author speed range is historical context, not annual velocity extrema.

Source: Duncan, Schladow and Williams (1982), *Surface Currents Near the Greater
and Lesser Antilles*, IHR 59(2), 67-78:
https://journals.lib.unb.ca/index.php/ihr/article/view/23548
Original PDF: 1,523,058 bytes, 12 pages; SHA256
`df7041ed36e8e2d4019f4a0a8e59bdbd76ab1e516c2d9e6f423bf1a69f666377`.
Pages 1,7,9,10,11 rendered and visually inspected. Original header confirms July
1982; the archive's 2015 upload date is separate. Underlying Duncan et al. 1976
raw section study remains unreviewed. Original PDF and review images stay ignored.

## Data and presentation

- Width inventory: **128 records / 68 owners / 23 unassessed**, previously
  127 / 67 / 24. This closes a scoped evidence gap, not whole-current width.
- All 127 earlier width records and 99 unrelated current decisions unchanged.
- Only `current:caribbean` changes dashboard fingerprint.
- Existing atlas/card and static inspector show date, width, speed and limits.
- New source query exposes the unresolved-unit context at its exact pointer.
- Compiled Rust guard freezes identity and source scope; coherent receipt
  rewrites cannot invent ranges, depth bounds, observation dates or uncertainty.
- Separate source index: 159 JSON documents. Forty-two query collections,
  100 current and 140 eddy selectors, 64 route candidates and 11 ranked
  published current lengths remain. Canonical physical claims are unchanged.

## Reproduce

```powershell
python analysis/acquire_local_paper_fixtures.py
python analysis/build_caribbean_dated_width.py
```

Review and refresh only `width_inventory_sha256` in the seasonal route document
after inventory regeneration; its route values and seasonal conventions remain.
Then run dashboard, index and query bundle builders followed by the serialized
Rust engine build. Run the focused tests, Caribbean browser and offline suite.

## Validation

- Focused Python: 51 tests and 538 subtests pass, including eight native
  coherent source mutations and all existing width-inventory checks.
- Serialized native/WASM build: 45 Rust tests pass.
- Caribbean browser passes static phase, date/speed, source/native parity,
  320-pixel layout and two direct compiled WASM scope rejections.
- Mobile chart screenshot visually inspected; date and limits readable.
- All 54 JavaScript modules and 14 page assignments pass.
- Full offline suite: 1,293 tests and 925 subtests pass in 976.22 seconds.
- Existing atlas browser: 85 exact source documents, 18 loader rejections,
  native/WASM parity, 100 current/140 eddy selectors and 64 cards pass.
- Internal role review: current/source/cartography/accessibility/reproducibility
  lenses; separate independent scientific admission remains pending.

## Remaining work

23 currents remain unassessed for width. Most full annual dimension ranges and
89 published whole-current lengths remain unresolved. Coastal Portugal-current
widths encountered during research belong to a different feature from the
offshore Portugal Current and were not transferred to that owner.

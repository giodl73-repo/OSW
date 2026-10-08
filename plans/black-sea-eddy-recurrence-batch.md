# Black Sea named-eddy recurrence batch

Branch `codex/black-sea-eddy-recurrence`, based on the Black Sea width branch.
Editorial source extraction; protected publication and independent scientific
admission remain pending. This advances the full data-gap goal.

## Evidence and distinctions

Korotaev et al. (2011), doi:10.5194/os-7-629-2011, section 3.1, printed page
633, contains quantitative recurrence descriptions for nine already named
Black Sea regions. The original CC BY 3.0 PDF and rendered page were inspected.
Existing PDF bytes, acquisition receipt and attribution are reused unchanged.

| Region | Approximate presence days/year | Approximate per-event lifetime |
|---|---:|---|
| Bosphorus | 260 | 85 days, mean |
| Batumi | 210 | Not quantified; narrative early March–end October |
| Sukhumi | 120 | 1 month, typical |
| Caucasus | 160 | Not quantified |
| Kerch | 240 | 80 days, mean |
| Crimea | 115 | 1 month, mean |
| Sevastopol | 150 | 50 days, mean |
| Constantsa | 190 | 50 days, typical |
| Kaliakra | 190 | 50 days, typical |

Occurrence and event lifetime are not interchangeable. Months stay months;
seasons stay narrative, without exact calendar assignments. The synthesis does
not state its averaging interval or detection criterion. Nearby Figure 2 dates
are not applied to these statistics. These records cannot establish individual
tracks, occupied footprints, NASA generation matches or physical state joins.
Danube remains a named region without numerical recurrence from this passage.

## Integration

- Reproducible manual extraction and versioned recurrence protocol.
- New `eddy_recurrence` collection: nine records, exact existing owner IDs.
- Rust validates receipt hashes, original source binding, owner labels/IDs,
  lifetime units, null dates/geometry and false admission flags.
- Object cards display presence meters with numeric/text equivalents, separate
  lifetime statistics, original citation and a sorted comparison query.
- Native/WASM object views return exact scoped recurrence records.
- Source index exposes the extraction and validates it before packaging.
- Exactly nine dashboard source/time fingerprints change. All latest observed
  dates remain identical to the parent; no fresh observations are invented.
- Canonical release collections, current widths/lengths, identity census and
  prior geometry records are unchanged. The bundle has 39 collections and the
  source index 76 documents; all 240 dashboard objects remain.

## Verification

- Full local suite: 812 tests and 619 subtests passed, 237.28 seconds.
- Following the final source-index consistency guard, the affected recurrence
  and dashboard suite passed 24 tests and 21 subtests. One existing NumPy binary
  size warning was emitted; no test failed. The full result above precedes that
  guard and the last Rust source-binding checks.
- 38 Rust unit tests pass; native and shipped WASM builds pass after the final
  source-binding guards. All manifest build hashes match current files.
- All nine recurrence cards pass full native/WASM object-view parity, source
  units, meter semantics, source links, sorting/query parity, mobile reflow,
  and the absence of an unsupported Danube summary.
- Three coherently rehashed source-receipt mutations are rejected for invented
  seasonal playback, geometry and observation dates. Python mutations reject
  swapped statistics, unit changes, wrong owner and scope promotion.
- Original source page and mobile card screenshot inspected.
- 39 JavaScript modules and 14 page assignments pass; these assignments do not
  prove all 52 registered browser checks ran in this batch.
- A rebuild attempted during a native browser check hit a Windows executable
  lock. An earlier dashboard initialization check also timed out during receipt
  refresh. Both sessions ended; the final build was serialized and build hashes
  checked before rerunning the affected browser checks. This records the failed
  attempts without treating them as successful validation.
- Source-index regeneration preserves compressed corpus bytes but updates the
  catalog's validator checksum. An attempted assertion that both files would
  remain unchanged failed on that expected catalog change; both source receipts
  were checked and the compiled catalog rebuilt afterwards.
- The serialized dashboard rerun passed all 240 objects, exact native/WASM
  parity, four receipt/projection rejections, updates, outage retention and mobile.

Reproduction:

```powershell
python analysis/build_black_sea_eddy_recurrence.py
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
python -m pytest analysis -q
python analysis/test_black_sea_eddy_recurrence_browser.py
python analysis/test_motion_dashboard_browser.py
python analysis/check_almanac_javascript.py
python analysis/check_almanac_page_coverage.py
```

Run builds before native/browser checks; Windows holds executing binaries open.
Browser checks require the checkout server on port 8788 and `OSW_TEST_BROWSER`.
The seven-role review is stored in
`signals/roles/check/black-sea-eddy-recurrence-roles-check-2026-10-07.md`.

## Still required for the full goal

89 missing published lengths, 57 unassessed width owners, compatible seasonal
dimension series, most named eddy footprints and physical state membership remain.
The publication stack also remains pending. Regional recurrence totals fill
almanac attributes, not the missing dated geometry.

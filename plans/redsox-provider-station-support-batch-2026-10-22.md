# REDSOX station metadata: complete source audit and query delivery

Continues branch `codex/current-measurement-gaps`, draft PR83. No separate PR
or main merge. Method/protocol/source preflight frozen at26e87ec before the
first full-archive classification. Exploratory: selected records and primary
methods had already been inspected. No blinded or external review claimed.

## Source evidence and original custody

Peters et al.2005, printed570, section2, visually confirms a combined CTD/LADCP
package. NCEI README_FIRST2016, PDF2, visually documents UTC header conventions
and packet-loss synchronization limitations during REDSOX-2/REDSEA. It does
not establish winter sample synchronization. Original author quality notes
retain rejected downcasts10/63; their wording alone does not resolve every
distributed processing tag. Cruise-report Figure7(a)/caption, printed21,
was visually checked for the two channel lobes and station order.

Five original methods/cruise documents were reacquired from the official NCEI
URLs and match all previously published lengths/SHA exactly. Two cruise PDFs
were restored to their declared, ignored local paths. No old receipt or raw
profile was rewritten. Original PDFs, methods text and page renders remain
private; no redistribution permission inferred. The isolated1f4e017 test snapshot
was not modified. Existing Peters original was independently hash-checked.

## Complete result, with limited meaning

All445 velocity profiles and461 CTD records retained. The original444 filename
joins remain exact. Of the velocity records,431 have agreeing provider station
fields under the new rule,13 need metadata review and1 has no distributed CTD
companion. All17 CTD-only records remain, without an invented velocity partner.

The rule compares campaign, filename station, CTD header station, exact decoded
position values, timestamp availability and reported UTC date. It never chooses
a nearest neighbor, substitutes reviewed fields for raw headers, or rejects a
record merely because the two timestamp roles have a negative difference.
The signed difference is neither cast duration nor a correction to apply.

Every physical-cast and sample-synchronization verification flag stays false.
Header agreement does not clear source reference/processing exclusions or prove
plume membership. Transit/far-field profiles remain in this experiment archive;
they are not445 newly identified Red Sea current observations. No current
width, length, annual range, footprint, ranking or new source observation set.

Actual report2,903,598 bytes, SHA256
`db06ac15973b4a05d4c3e1c40102ca00a2b27f305b332c81d52eca85dea20045`.
All18 frozen dependencies match and both old metadata inventories reconstruct
exactly from their retained original ASCII archives. Eight focused tests pass,
including complete445/461 coverage, unchanged original metadata/joins,
timestamp-difference sign, missingness and the distinction from physical proof.

## Missing companion investigation

RSX1 cast74 is absent from the checked ASCII and MATLAB CTD directories in
both public archive versions1.1 and1.2. Each directory lists237 profiles and
contains the positive control cast73. Version names are linked by the public
accession index; successful control HEAD responses distinguish the missing
candidate from an unavailable directory. The missing-file checks return404.
No numerical alternative was acquired or imputed. This is a point-in-time
published-directory check, not proof that an unpublished/raw record cannot
exist elsewhere. Exact listing hashes/URLs and scope are preserved separately.

## Source-query scalar equality repair

The metadata exposes an actual source-filter bug: stored `-919.0` did not match
requested integer`-919`, while the main collection query already compared
scalar numeric values correctly. A new Rust regression failed on that exact
case before the fix. Source `eq`/`ne` now reuse the existing precise scalar
comparison, preserving missing/null behavior, strings/booleans and the53-bit,
signed64 and unsigned64 precision boundaries. No source value is normalized or
rounded, no epsilon introduced, and no complex-object/array semantics changed.

All134 Rust tests pass, including the new regression; complete native atlas
ingestion passes. Fresh WASM47,986,721 bytes, SHA256
`0e1068856b3a889ce1e1468c3af58d578801ea3e8655a44d46c6e9bd28fa1b76`.
All587 engine hashes match. Packet185,727,284 logical bytes in12 parts.

## Atlas and visual delivery

`/figures/redsox-station-support-2001/` provides a compact station matrix,
campaign/status/record controls, equivalent metadata/check tables, original
full records,17 unmatched CTD rows and exact per-record source-query links.
Symbols and text duplicate the palette. Field agreement is not a velocity
quality grade. Source timestamp roles are explained in plain language;
full checksums remain in the complete record, with prefixes in the compact
table. Invalid selections, empty filters, keyboard, history and permalinks
are covered. The view passes all445 actual profile selections,461 complete
CTD metadata records and12 filter states at320px. The initial phone inspection
identified an opaque time-role enum and oversized checksum cells; both were
replaced by readable presentation before final verification.

The Red Sea current card links directly to the view, all445 comparisons and
the13 metadata-review records. Main source catalog501 documents,
369,429,269 original bytes /59,166,415 gzip bytes. One new complete diagnostic
`diagnostic:redsox-provider-station-support`, yielding52 collections,
106,815 rows and63 diagnostics. The missing-cast availability review is
indexed and linked by the diagnostic; source/method/custody documents remain
queryable with their exact bytes.

Actual Chrome/native/WASM comparison passes the complete diagnostic, all445
velocity/461 CTD metadata,13 reviews,1 missing companion,17 CTD-only records,
all4 archive-directory checks and3 real source integer/float equality and
inequality cases. At320px, keyboard navigation works from current card through
the selected station view to its exact complete source record. No page errors
or automatic original downloads. Both browser checks are in the default runner
and focused CI; scientific replay adds the36th report without removing any
previous target. The eight new focused tests are also in CI. Fresh remote
execution remains pending publication.

## Preservation and remaining gates

All106,814 previous rows remain exact except the Red Sea object's source
fingerprints, additive evidence links and diagnostic ownership. Its other
fields, capabilities, dates, geometry and linked-source count5 stay exact.
All495 prior source descriptors and actual source-file bytes, plus144 protected
scientific/source files, remain exact. Widths170, reference routes78,
hydrography46,944 and registered sources175 unchanged. No physical width-owner
gap is declared closed by metadata agreement.

Previous ae6c73f CI scientific job120248778883 and full-source UI job
120248778790 are terminal SUCCESS. They prove the preceding snapshot, not this
new source/API snapshot. The isolated full Python suite at1f4e017 is terminal:2250 tests and1248 subtests passed;16 tests failed. Failures include exhausted temporary storage, stale inventory expectations and source-binding checks. Its snapshot/logs remain retained; fixes and a fresh full gate remain outstanding.
No overall-green or release claim. No new full suite started below its unchanged
4GiB start preflight. Source/derived1GiB and engine512MiB guards also remain.

## Reproduce

```powershell
python analysis/redsox_provider_station_support.py check
python -m pytest analysis/test_redsox_provider_station_support.py analysis/test_redsox_provider_station_report.py -q
python analysis/build_redsox_station_support_view.py
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
$env:OSW_TEST_BROWSER='C:/Program Files/Google/Chrome/Application/chrome.exe'
python analysis/run_rust_query_browser_checks.py --only-check test_redsox_station_support_browser.py test_redsox_station_support_query_browser.py
```

The check/build/view operations use retained local originals; no automatic
acquisition. Existing frozen producers/protocols/preflights/reports remain
unchanged. Future physical measurements need their own layer, current-feature,
sampling, boundary and timing support; field agreement alone does not supply it.

# Atlantic station metadata gap closure

Parent snapshot: 2d9829a6555649f52ee94d3d29b569d550c80225 (#33).
Branch: codex/pelagia-station-date-reconciliation.

## Completed source work

The newer integrated Pelagia bottle product explicitly credits corrected dates
to Robert Key. All 46 original summary station/cast identities match its
metadata. Positions agree exactly after the recorded decimal conversion. The
month/day values agree; three UTC times differ by one minute, with both versions
and signed differences retained. The 42 casts within the paper section window
restore sampling maps for its North Atlantic, Irminger and East Greenland span
records. Original summary events and their 2005 dates are preserved unchanged;
only derived points receive separate sampling_date/sampling_time_utc fields.

The Charles Darwin CD171 summary was also recovered from the original CCHDO
integrated Dataset. It supplies 143 original events and 137 casts within the
paper's sampling window for the Gulf Stream record. Preserve its Atl32N archive
label and the paper's A03/nominal 36 N label separately. The paper model selected
112 stations; the cruise-wide context is not a reconstruction of that subset.

Current audit: 18 original cruise summaries, 4,772 original events and sampling
maps for all 30 published span records across nine currents. No source-metadata
map gaps remain within this batch. The checked source catalog has 73 documents.
Original sources, timestamp corrections and selected station coordinates are
inspectable through the checked Rust source query. Maps use Rust cartography.

## Evidence boundaries

No current boundary station pairs are admitted. All 30 context records still
have unresolved boundary mapping and false footprint, state-intersection and
annual-series eligibility. Geodetic datum and position uncertainty are null.
The 89 missing published lengths, 58 unassessed widths and most named-eddy
footprints remain core gaps. Frozen release records and reported width values
are unchanged. This batch completes cruise sampling metadata, not all core data.

## Reproduction

```powershell
python analysis/build_pelagia_date_reconciliation.py
python analysis/build_atlantic_station_context.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python -m pytest analysis -q
python analysis/test_atlantic_station_context_browser.py
python analysis/check_almanac_javascript.py
python analysis/check_almanac_page_coverage.py
```

Sources are local and checksum-pinned; no network read is needed for extraction
or validation. CSV/TXT archive bytes are protected by scoped .gitattributes.

## Validation

- Full offline suite passed 809 tests and 598 subtests after Pelagia reconciliation.
- After adding CD171, all 13 affected source/parser/matching tests passed again.
- All 38 Rust unit tests passed on the final source catalog; native and shipped
  WASM rebuilt successfully after clearing disposable incremental cache to
  recover from a terminal disk-full compilation error.
- All 39 JavaScript files and 14 page validation assignments passed.
- Final station browser passed all 30 exact source joins/maps, corrected
  timestamps and the complete 46-row correction-query link, source/native
  parity, mobile keyboard scrolling, current-switch cleanup and integrity
  rejection.
- All 17 previously archived cruises retain exactly unchanged original events;
  all 19 source files match their original byte/hash receipts.
- Seven-role internal review: zero P1, three resolved P2 issues, protected-main
  publication remains an open P2 condition. Independent scientific admission
  is not implied.

## Publication

Protected main publication remains pending. The parent #33 push CI failed while
acquiring an external paper fixture (connect timeout), while its separate PR
check remained live at the last inspection. No full exact-head CI or current
mainline coverage claim is made here. Next: recover model station pairings and
review actual edge geometry; admit dimensional evidence separately under the
measurement rules, and clear protected publication gates.

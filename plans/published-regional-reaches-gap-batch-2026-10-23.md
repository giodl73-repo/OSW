# Published regional reaches gap batch

Continue on `codex/current-measurement-gaps` and draft PR83. No main merge.
Batch compatible source facts before the next native/WASM and browser cycle.
One heavy local job at a time, BelowNormal on one logical CPU; numerical and
Cargo workers remain one. Full regression remains a separate final batch gate.

## Algerian Current: original-reviewed dated regional constraint

Arnone, Wiesenburg and Saunders (1990), DOI10.1029/JC095iC02p01587,
reports a near-coastal reach **over 300 km between Oran and Algiers** during
combined ship/satellite work 1–22 May 1986. The ship-only cruise ends 21 May.
The nearby 30 km value is coast proximity, not current width.

The retained DTIC original is 853,466 bytes, provider MD5/SHA1 verified and
local SHA256 pinned. It has 11 PDF pages including its cover; printed journal
pages 1596–1597 are missing. The abstract on printed 1587 and supporting results
on printed 1590 were visually inspected. No full-paper review is asserted.
The original permits public release and states the paper is not subject to
US copyright; attribution and its incomplete state are retained.

Prospective method/source/test/protocol/preflight were frozen in commit
`c2adb97` before report execution. No distance calculation or digitization
was performed. First report/figure execution passed; exact read-only replay
also passed. Twenty-five synthetic checks and two independent original/product
checks passed. The SVG was rendered with PyMuPDF and visually inspected,
without starting Chromium. No layout collisions were observed at native size.

Products:

- `research/algerian-arnone-1990-reported-reach-v1.json`
- `figures/algerian-arnone-1990-reported-reach-v1.svg`
- Source custody in `research/source-data/arnone-algerian-1990/`.

Retain the strict `gt` comparator, absent upper endpoint and absent numerical
uncertainty. Whole-current centreline length, physical length lower bound,
width, annual/seasonal range, geometry and ranking eligibility stay null/false.
This fills a dated regional-reach evidence gap; it does not close the
whole-current measurement gap or change the canonical current count.

## Working query/card admission

The working atlas now includes a distinct `current_regional_reaches` record,
its source-reported constraint claim and two provenance records. The frozen
report and diagram are unchanged. Three Algerian card links expose the diagram,
exact query row and incomplete original-source custody. The existing query
inspector displays the strict threshold, dated regional support, unknown upper
endpoint and uncertainty, and a responsive copy of the frozen diagram.

Source counts now use the actual `linked_source_count` field and registered
references. The query projection also retains an existing OSW NASA-crosswalk
media-ledger reference that it previously dropped for this current. The card
has five references, including the new primary paper and internal method.
The restored ledger is OSW authored; it is not a NASA upstream dataset or an
additional independent ocean observation. All registered reference IDs resolve.

Before/after preservation proves 108,440 prior rows exact, with only the
Algerian card changed, and four new records: 108,445 rows in 55 collections.
All 548 prior source documents remain byte-exact; five new documents bring the
lossless index to 553. The 170 width records, 78 routes, 13 qualified length ranks
and all previous measurement/length-assessment rows are unchanged.

The next source hunt checked Mindanao, Antilles, Alaska, Baffin, Guinea and
Ligurian candidates. No additional along-current length was admitted:
Antilles 520 nautical miles refers to an offshore survey section; Mindanao 80 km
is an objective-mapping scale; Baffin 1000 km describes the bay; Guinea 7600 km
is regional coastline. Keep these exclusions when extending source coverage.
Other measurement, seasonal, eddy inventory and state-intersection gaps remain.

## Verification and remaining gates

`analysis/published_regional_reaches_query.py` now builds an exact delivery
contract over the frozen source report and diagram. It binds a distinct
`current_regional_reaches` record, its source-reported constraint claim, and
two provenance records. The owner join carries the reach ID and actual source
references. All source, report, method and figure bytes are pinned. Three
card links target the diagram, exact query row and original-source custody.

Thirteen focused adapter checks verify strict comparator/unknown bounds,
atomic rejection of partial or duplicate joins, source-count consistency,
the existing length/width/ranking rows remaining exact and query links resolving
to the admitted records. Forty focused checks cover the source, report and
adapter. All 150 Rust tests passed, including the new source-bound admission
guard. After a query-only provenance correction, Cargo confirmed the compiled
native code was unchanged and the complete native atlas passed. WASM compiled
to 49,316,863 bytes; all 722 engine input pins match the delivered files.

The registered browser check proves four exact records through native CLI
and WASM, the mobile atlas disclosure/query link, keyboard opening of the
inspector, the visible strict threshold, and responsive diagram at 320 px.
Desktop table/inspector and phone card/inspector screenshots were inspected.
No original PDF, NetCDF or ZIP was automatically downloaded. The check uses
serial desktop and mobile browser instances to release their large workspaces.

Initial attempts and corrections are retained in the local delivery receipts:
a baseline manifest-key error before generation, metadata counted as sources,
the dropped existing media-ledger reference caught by complete-atlas validation,
manifest-wrapper import/disk-space failures after successful compilation,
a missing bundled browser, the undefined collection caption/hidden table value
found visually, and a combined-browser mobile reload timeout. No scientific
producer, protocol, source facts, report or figure was revised after execution.

Only query presentation changed after compilation. Compiler dependency files
prove these UI files are not embedded inputs; 720 other engine pins remain exact,
the two presentation pins were refreshed, and the compiled WASM is unchanged.
The undefined caption now has a collection label and a generic fallback.

Linux CI for the prior source/adapter commit cfff6f1 independently reproduced
all 40 registered scientific reports exactly, including the frozen Algerian
report and SVG, and passed 40 regional focused checks. It does not prove the
subsequent runtime delivery. The complete local Python regression remains
deferred under the user's serial batch policy. That commit's offline CI job
failed while acquiring the Rotschi (1972) original with HTTP403; no guard was
disabled and no full-suite pass is claimed.

Reproduce the scoped checks sequentially:

1. `python -m pytest -q analysis/test_published_current_regional_reaches_v1.py analysis/test_published_current_regional_reaches_admission.py analysis/test_published_regional_reaches_query.py`
2. `python analysis/published_current_regional_reaches_v1.py check`
3. `python analysis/published_regional_reaches_query.py check`
4. `python analysis/build_rust_query_engine.py` after generating dashboard, query packet and source index in order.
5. `python analysis/test_published_regional_reaches_browser.py` with a preview server and an installed Playwright browser, or `OSW_TEST_BROWSER` pointing to an existing browser.

All heavy local stages ran separately, BelowNormal on one logical CPU, with
one Cargo/numerical worker. Checked inactive generated packets and compiler
intermediates were retired for disk space; all scientific originals and
products, the active packet, standalone native CLI and final WASM were retained.
The seven installed role lenses reviewed 21 findings; final gate resolutions
are in `signals/roles/check/published-regional-reaches-roles-check-2026-10-23.md`.

Whole-current lengths, physical widths, annual/seasonal envelopes, remaining
identity/geometry gaps, eddy inventory and state intersections remain broader
goal work. No main merge, full-regression pass or external scientific approval is claimed.

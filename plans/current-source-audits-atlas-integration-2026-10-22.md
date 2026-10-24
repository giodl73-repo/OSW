# Current source audits: main atlas integration

Continues draft PR83 on `codex/current-measurement-gaps`. Data baseline is
53cfc3caf9e09b616b26294ca2b1465d074de305. No new PR or main merge.
This integrates the completed Indian SECC source-boundary audit and selected
original-page Red Sea channel-width review into the existing atlas.

## Delivered source and query structure

Five additional lossless documents: boundary report, frozen preflight, view
manifest, Red Sea primary-source review and acquisition receipt. Main source
catalog now495 documents,366,508,562 original bytes /58,985,204 gzip bytes.
The new adapter verifies the exact complete boundary report, all source/view
bindings and Red Sea identity/admission flags before any dashboard or query
build. Original source publications remain private.

Two typed diagnostics retain the complete respective source documents:

- `diagnostic:indian-secc-2013-source-boundaries`
- `diagnostic:red-sea-ozgokmen-2003-width-scope`

The two current objects list their diagnostic IDs. Their evidence links expose
the complete144 attempts and156 terminal records, source review findings and
all acquisition fields. The SECC card links directly to the monthly visual
inventory. That view supplies selected-month query links with exact offsets;
months without retained terminals hide that unavailable link and still expose
all12 failed/successful attempts. No zero-limit or fabricated empty profile.

The atlas remains52 collections, now106,814 rows and62 diagnostics. No new
physical current width, axis, length, annual range, footprint or state join.

## Preservation and completed local engine checks

Complete baseline comparison passes:106,812 old rows unchanged except source
fingerprints, additive evidence links and diagnostic ownership on the Indian
SECC and Red Sea objects. Every other field on those objects remains exact,
including capabilities, map features, dates and linked-source counts3/5.
Only their source-section fingerprints change; old evidence links remain.
Exactly2 diagnostics are added. All138 protected scientific/source files and
all490 previous source descriptors plus actual source-file bytes remain exact.
All170 scoped widths,78 reference routes,46,944 hydrography rows and175
registered source rows remain unchanged. This does not close the physical
width-owner gaps.

All133 Rust tests and complete native atlas ingestion pass. All560 engine
dependency hashes match. WASM47,984,930 bytes, SHA256
`90c8731d7bd57be45b0efd00172bb9dc4786d991b118be8a2106b1f98f35f231`.
The query packet is183,845,230 logical bytes in11 transport parts. Four
focused source-boundary tests pass, including complete actual-data preservation.
Actual browser verification of this integrated snapshot is terminal PASS.
Both complete typed diagnostics, all144 attempts,156 terminal records,
12 monthly summaries,4 Red Sea findings and every acquisition-receipt field
match native/WASM results exactly. All12 selected-month query links are
checked, including absent-terminal states. At320px, keyboard navigation works
from each current card into its evidence; the SECC path continues through the
selected May view to all24 corresponding terminal records. No page errors or
automatic original downloads. The Red Sea phone query screenshot was visually
inspected. The standalone view also passes all12 months and keyboard/history
again against the regenerated assets. Both checks are registered in the default
runner and focused CI, with all previous checks retained.

## Independent prior-stage receipts

At1f4e017, run39897134063/job120230060425 is terminal SUCCESS for all4
South Indian full-source/property browser checks:72 profile selections,
360 charts,23,472 source cells,12 raw/12 derived full months,2 pressure
sections,36 property cases/144 masks/4,258 pair relationships, keyboard
current-card navigation and320px reflow. No automatic originals or errors.
This closes the older independent main property/source UI condition.

At53cfc3c, run39900218249/job120239839548 is terminal SUCCESS:
69 preceding conformance tests,4 source-boundary tests, complete boundary
report byte exact and complete property report byte exact on Linux. These
scientific inputs/operators/reports are unchanged by the present integration.
The new integrated source/card/query snapshot still requires its own CI gate.

The broad offline suite at isolated1f4e017 remains live and has emitted
failures. Preserve its snapshot and process until terminal diagnostics are
available; do not restart it or claim whole-suite success. CI offline paper
fixture acquisition failures remain separate from focused reproduction gates.

## Reproduce

```powershell
python analysis/indian_secc_source_boundary_audit.py check
python analysis/build_indian_secc_source_boundary_view.py
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
python -m pytest analysis/test_indian_secc_source_boundary_audit.py analysis/test_indian_secc_source_boundary_report.py -q
$env:OSW_TEST_BROWSER='C:/Program Files/Google/Chrome/Application/chrome.exe'
python analysis/run_rust_query_browser_checks.py --only-check test_indian_secc_source_boundary_browser.py test_current_gap_source_query_browser.py
```

No automatic downloads. Frozen scientific producers/protocols/preflights are
unchanged. Source, display and typed-query evidence keep their separate scopes.

## Local storage and transport custody

After all new native/browser consumers finished,11 superseded generated packet
parts were checked against baseline lengths/SHA and exact packet-directory
containment, then retired. They remain in Git history; no provider original
was removed. All11 replacement parts remain exact after lossless NTFS
compression. All1,574 explicitly selected text copies in inactive earlier
snapshots also retain identical before/after hashes after NTFS compression;
the live1f4e017 test snapshot and other served workspaces were excluded.

Available disk remains below the4GiB start reserve for another complete-suite
run. That preflight is unchanged; no new full run was started. The existing
isolated full run remains live and must reach terminal diagnostics. Its initial
4GiB preflight passed; current free space is not a new successful preflight.

Before publication, all892 unique staged blobs match the560 engine dependency
and495 source-document pins exactly. No line-ending or staging conversion
changes the scientific/compiled inputs. This receipt is additional to the
complete row/source preservation and native/WASM browser checks above.

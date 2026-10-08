# Atlantic cruise width gap batch

## Result and scope

30 local transport-selected hydrographic section spans for nine previously
unassessed canonical currents: Falkland (Malvinas), Brazil, Benguela, Canary,
Gulf Stream, North Atlantic, Irminger, East Greenland and upper West Greenland.
The width inventory moves from 39 records / 26 owners to 69 records / 35 owners.
58 currents remain unassessed, two have derived candidates awaiting review,
and five have reviewed sources without a comparable numeric width.

This batch preserves the original publisher Tables 1 and 2 under CC BY 4.0.
All original first-sheet cells are retained separately from the admitted
extractions. Explicit cruise joins preserve dates crossing a year boundary,
source station labels, nominal section labels, longitude bounds, density layer
indices and reported depth extent. Two 2018 24 S rows are held out because
Table 1 instead labels the candidate cruise 19 S. Other exclusions retain
their source addresses. No recirculation is merged into a parent width.

All 30 records are available through the shared `widths` Rust/WASM collection,
the source document query workspace, atlas width cards and the evidence page.
The evidence page adds independent scalar bars and a source table per current.
There is no new map geometry, interpolation, seasonal playback, annual range,
whole-current ranking or canonical admission.

## Rules and regeneration

The versioned supplement is `atlantic-cruise-section-width-protocol-v1.md`.
Earlier width rules and numerical records are preserved. Regenerate with:

```powershell
python analysis/build_atlantic_cruise_widths.py --update-inventory
python analysis/check_current_width_inventory.py
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python -m pytest analysis -q
python analysis/run_rust_query_browser_checks.py
python analysis/check_almanac_javascript.py
python analysis/check_almanac_page_coverage.py
```

Original acquisition is explicit and already archived; default extraction and
tests do not contact the publisher. The standard-library XLSX parser was
independently checked against bundled read-only openpyxl for every populated
and empty first-sheet cell in both tables. No spreadsheet dependency is added.
The registered cruise browser check exercises all 30 records and nine owners,
dates, depth contexts, share links, narrow-screen keyboard scrolling and exact
native/WASM query parity. The browser runner now declares 49 checks; declaration
does not establish a passing publication run.

Local verification: 38 Rust unit tests and both native/WASM builds passed.
The complete Python suite passed 796 tests and 598 subtests; after final
provenance and byte-count checks, 72 affected tests and 409 subtests passed.
The cruise browser check passed all 30 records and nine owners, and the existing
seasonal-source browser check passed exact source parity and rejection paths.
The dashboard browser check passed coverage lights, update isolation, receipt
rejections, all 240 records, atlas links, keyboard selection and mobile layout.
All 38 JavaScript modules passed syntax checks; all 14 pages retain validation
assignments. Every one of the earlier 39 width records was checked for exact
preservation. Mobile output was visually inspected. These are local results,
not claims that all 49 browser checks or mainline publication have passed.

## Next core gaps

- Recover actual boundary station coordinates before atlas section locators or
  OSW state intersections for this batch. Retain station indexing ambiguities.
- Resolve the 2018 A095 latitude mismatch using cruise source metadata before
  admitting the two held-out spans.
- Review Antilles and deep-current tables under their separate metric and
  identity rules. Transport uncertainty remains distinct from width uncertainty.
- Continue the 58 unassessed widths with source-specific layer and time support.
- Published ranked lengths remain 11 of 100. The 89 missing source lengths retain
  their editorial route candidates and unresolved endpoints separately.
- Named eddy footprints remain a separate gap: repeated named regions and
  operational detections cannot substitute for individually dated footprints.

## Publication

Based on the pending branching-selector PR #31. Do not merge this batch into its
dependency branch. After preceding work lands, preserve the candidate tree,
retarget/rebase to main and pass the required publication contexts. Earlier
mainline receipts describe their original commits and remain unchanged.
The role receipt is an internal seven-lens review, not independent peer review.

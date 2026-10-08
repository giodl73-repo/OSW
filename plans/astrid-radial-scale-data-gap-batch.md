# Astrid radial definitions and publication follow-through

2026-10-08. Base 90e3f249aa1da12b362a9d1b1aa201e286cd3dde (draft PR45).

## Gap resolved

The geography ledger previously exposed an unqualified 120 km radius.
Original Table 3 and section 7.2 define it as the radius of maximum tangential
velocity in a two-layer, circularly symmetric diagnostic model. A separate
140 km radius is the authors' integration limit at thermocline relaxation.
The source uses the 10 C isotherm as the layer interface and notes that this
model mainly captures the baroclinic component despite observed deep flow.

Store two definitions, not a 120–140 km interval. Neither supplies a dated
closed geographic boundary. Numerical uncertainty, exact occupations and
geometry remain unknown; no diameter, area, seasonal series or physical
OSW containment is admitted. Current width and length inventories are unchanged.

Original: van Aken et al. (2003), Deep-Sea Research II 50, 167–195,
doi:10.1016/S0967-0645(02)00383-1. Full institutional-hosted original text read;
printed pages 190–191 rendered and Table 3 visually inspected. Original PDF:
1,136,090 bytes, SHA256
`00f15a476e1584ae8666d3ab5198d4139b4b63da5d2c78ca7ddd179ee3836776`.
All rights reserved; original ignored, acquisition metadata retained.
The explicit fixture-acquisition command hydrates this sixth pinned original.

## Data and visualization

Add a source audit with both records and precise locators; bind the geography
entry's copied records to the audit. Python validates source bytes, acquisition,
metrics and inference exclusions. Rust binds complete atlas audit bytes to its
compiled document. Exact source-index receipts protect the inventory view.

Charts appear in the eddy inventory and on Astrid's atlas card, with distinct
point rows, labels, accessible descriptions and a source-query link. Updated
measurement/source fingerprints let the dashboard signal the evidence change.
The chart's numerical scale is schematic; map geometry remains a locator.

Source index: 90 documents. Atlas snapshot: 79 source documents. Still 87 current
width records, 43 scoped owners, 50 unassessed, 11 published length owners and
one stored named-eddy footprint candidate. Most footprints remain unresolved.

## Verification record

40 Rust tests passed. Focused Python source-scope and coherent atlas rewrite
checks passed. Atlas browser checks passed for 79 sources, 18 rejected loader
cases, 100 current / 140 eddy selectors and 63 cards. JavaScript syntax passed
for 42 files; all 14 page assignments verified. Full Python and expanded eddy
browser checks passed: 833 Python tests / 913 subtests; all 136 indexed
eddy identities, six native/WASM inventory views, both new chart paths,
320 px text containment/reflow and source-query record parity. The final
portable CLI-path change was separately rerun through both focused tests.

The first Rust build found that a minimal current-only atlas fixture did not
include Astrid. Source requirements now apply when Astrid is present, while
the production atlas cannot omit its audit. The first browser check caught
small text in a detached inventory row; explicit table-cell sizing fixed it.
A subsequent wait used an uninitialized bare global; it now waits through
the window property during query-page loading. Neither failed attempt is a pass.
A standalone pytest invocation hit sandbox temp permissions; workspace TEMP/TMP
resolved it. The full suite uses that workspace temp location. An almanac
verifier initially lacked its public cartographic cache; its authorized source
acquisition rerun passed the complete inventory check.

## Publication

PR30 merged into main at 2026-10-08 11:07:39 UTC after both offline and both
NetCDF jobs passed. PR43, PR44 and PR45 contain newer work and remain draft.
Consolidate these verified additions with this batch against updated main;
passing local checks do not establish new mainline publication.

Remaining source work: recover dated boundary coordinates and a boundary
convention before any footprint; compatible repeat observations before seasons;
independent scientific admission. The full core-data goal remains active.

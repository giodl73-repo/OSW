# Azores Countercurrent coordinate interpretation

Continues the same branch and PR83. This adds reviewed source-quantity meaning,
an independent coordinate diagram and dashboard/source-query navigation.
It does not add a current-width measurement or close the physical width gap.

Carracedo et al. (2012), printed pp278–279 / PDF pp16–17, cites a mean width
range of 100–250 km from Alves et al. (2002). Selected pages of the exact 2012
original were read and visually inspected: 2,341,819 bytes, SHA256
`2e196e4cb410201afae9b433cdcc1e85ab52a86b36d73b0ef1f8670abb0507a6`.
Original and page pixels remain excluded from Git; acquisition receipt is public.

The publisher-indexed primary POSAF discussion and Figure 9 caption describe
the mean westward subsurface maximum at **section distances about 100–250 km**,
with pressure context 500–1200 dbar. The caption labels the temporal mean
February–June 1999; the prose calls it a four-month winter-to-late-spring record.
No exact occupation endpoints inferred. Direct original access returned 403;
the full original and figure pixels remain unreviewed.

The inspected meanings differ. The arithmetic coordinate difference is about
150 km; it is not a verified physical width, paired velocity-boundary span,
flow-normal width, statistical interval or annual range. The origin and mooring
georeferencing remain unreviewed. The primary passage alone does not prove
that no separate width statement exists elsewhere in the complete article.
The secondary range therefore remains unadmitted pending full original,
figure-axis and method review. No midpoint of the secondary range is selected.

The diagram uses an independently drawn linear display axis, not a digitized
source curve or geographic transect. Source values and distinctions are also
available as exact JSON in the source-query UI. Dashboard evidence links take
readers directly to the figure and audit. All source-query booleans prohibiting
width admission are explicit. Named-current widths and source counts are not
inflated by this clarification: 138 scoped width records and 211 width samples
remain unchanged; the source corpus grows from 218 to 220 documents.

Only the countercurrent dashboard entry changes. Existing observation dates,
scientific arrays, widths, routes, samples, diagnostics and seasonal geometry
are preserved. Independent scientific admission and the broader core-data
objective remain open.

Reproduce: `python analysis/build_azcc_coordinate_meaning_figure.py`; rebuild
dashboard, separate index corpus, query bundle and serialized native/WASM.
Focused gate: three tests / five subtests passed. All 46 Rust tests passed.
The 220-source index browser passed exact sources, twelve seasonal snapshots,
independent NOAA oracle, native/WASM parity and checked-input failures. Source
query passed typed coordinate values, false width admission and 320 px reflow.
An initial ad hoc check expected ten fields; the actual nine-field source object
was correct and the check was corrected. Figure visually inspected. All 220
source hashes/byte counts and engine dependency pins verified.

The full offline suite passed: **1,369 tests / 1,014 subtests**,
1251.01 seconds (20m51s). The preceding publication head's remote job stopped during external
paper acquisition; this is not a source-width validation failure or green CI.

Final delivery: 46 Rust tests and serialized native/WASM builds passed;
220-source index and source-query/mobile browser checks passed. All source
and engine pins verified; only countercurrent dashboard evidence changes.
Prior observations and scientific dimensions remain unchanged. Internal
review permits this source clarification; scientific admission and the
broader data-gap objective remain open. Remote failure at the preceding
head was a Radenac HAL download timeout; new-head CI will be tracked separately.

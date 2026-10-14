# South Australian monthly section gap batch

Continue `codex/current-measurement-gaps` and draft PR83. No separate PR;
publication is a scoped model diagnostic, not canonical width admission.

## Source and measurement

GOFS 3.0 HYCOM+NCODA global 1/12 degree reanalysis, 2012 daily 00Z modeled
100 m velocities at 132 E, over 38–32 S. Official catalog identifies the
product, experiment, date extent and freely available rights:
https://tds.hycom.org/thredds/catalogs/GLBu0.08/reanalysis.html?dataset=GLBu0.08-reanalysis

Original ASCII response: 1,021,030 bytes, SHA256
`524cc83b5c873848634e83dc9e03e35e885779757f0466bbcb978792b490ebc6`.
Original DAS/DDS, request indices, coordinate maps, Int16 source values,
scaling, missing flags, acquisition time and hashes retained. Longitude
index 3900 is verified as 132 E; index 1650 would select 48 W. Depth index
19 is 100 m. All 366 days of leap year 2012 are present, without invented
dates. 27,816 source vector positions remain reconstructible.

Rules declared before velocity acquisition in the dedicated input/protocol.
Require complete u/v pairs on at least 80% of calendar days for each monthly
cell mean. Find the positive eastward peak within 35.5–33.5 S, minimum
0.02 m/s. Resolve the first connected 40/50/60% crossings; missing cells,
land masks and domain edges cannot close or double a one-sided span.
Compute WGS84 separation and round to 10 km. Distinguish grid brackets,
threshold sensitivity and unknown measurement uncertainty.

All twelve nominal sections resolve: monthly rounded values are
40, 50, 40, 130, 60, 30, 50, 40, 40, 40, 70, 30 km. June and December
are narrower than four nominal 0.08-degree spacings; all threshold scenarios
resolve. No search-edge peaks. The 30–130 km spread describes these local
monthly means; no annual physical range, climatology, whole-current width,
flow-normal section, occupied polygon or tracked seasonal geometry follows.
Named-current association remains unverified.

Duran et al. (2020), doi:10.1016/j.pocean.2019.102254, informs eastern-GAB
investigation geography. HYCOM is an independent model/epoch, not their
CARS-Aus8 or MOM01 reproduction. Their transport control boxes are not
width measurements. Exploratory categorical figure profiles did not yield
reliable paired crossings, so no figure-derived source width was admitted;
the declared velocity operator was not weakened to obtain a result.

## Inventory and presentation

Source widths unchanged: 136 records across 72 owners. Unassessed width
owners 14 → 13; section-diagnostic owners with width unresolved 6 → 7.
Published ranked lengths remain 11, with 89 gaps. Route count remains 73
across 67 of those 89 owners; 22 route-owner gaps remain.

Only South Australian dashboard evidence fingerprints change; all latest
observation dates remain unchanged. Seasonal route frames remain identical,
with only their width-inventory checksum refreshed. The five earlier OSCAR
diagnostics, source bytes and numerical profiles are unchanged.

Query bundle: 199 scoped samples, 24 diagnostics, 16 series, 42 collections.
Index corpus: 208 exact JSON documents. Native/WASM monthly charts, section
endpoint maps, source inspection, keyboard month selection and profile-sheet
links expose the readings. Chart titles and profile URLs now use actual
source year, preserving 2013 labels for earlier sections. The twelve-panel
scientific SVG includes modeled depth/source, full profiles, search window,
threshold crossings and resolution flags.

## Verification

Focused source/operator/inventory gate: 47 tests, 551 subtests passed.
Serialized Rust engine build: 46 Rust tests passed, native and WASM built.
Full offline gate: **1,342 tests and 963 subtests passed in 1264.98 seconds
(21m04s)**. Browser passed six contexts / 72 monthly component samples,
including 39 nominal resolution flags, native/WASM parity, keyboard inspection,
pagination-independent charts/maps, actual-year profile links, 320 px reflow,
five native and four WASM rejection cases. Legacy sample check passed all
127 original samples and five missing readings. Source-store browser passed
208 exact documents, 12 seasonal snapshots, independent NOAA oracle,
native/WASM parity and checked-input failures. All 61 engine pins and all
208 source-document hashes/byte counts verified; staged bytes match workspace.
The profile sheet was visually reviewed, including the complete declared domain
and hatching for cells without complete-pair support. Original provider ASCII
retains its blank final line; provider bytes were not whitespace-normalized.

Prior PR83 remote CI at `5eb505e` failed before tests while acquiring the
Melet Solomon paper: downloaded checksum differs from its original acquisition.
This source pin was not changed or waived; local regression results do not
establish remote CI success.
Internal seven-role review covers editorial publication; external scientific
width admission and remaining core measurement gaps are unresolved.

Reproduce: verify acquisition without `--acquire`; build HYCOM spans and
figure; validate width inventory; build dashboard, index and query bundle;
serialize engine build before running pytest/browser checks. Retained provider
bytes support offline reconstruction. Published source pins are unchanged.

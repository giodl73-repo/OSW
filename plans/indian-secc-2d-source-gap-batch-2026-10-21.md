# Indian Ocean SECC: surrounding velocity source gap

Continues `codex/current-measurement-gaps` / draft PR83. Previous turn
published aa9b5fc with two source-defined Norwegian slope mean-core spans.
This batch targets an individual uncovered-width entry and its missing
surrounding source data. No new PR and no main merge.

## Investigation and selection

Original Stramma1992 South Indian Ocean Current pages were rendered and
inspected during selection. Its conclusion explicitly says station spacing
was insufficient to investigate width. The coarse sections and fronts cannot
supply a defensible current width. No new numerical admission is made from
those pages, and no restricted original is redistributed.

The Indian Ocean SECC already had two native80⅓E/80⅔E columns and an exploratory
EOF audit. Those sections lack the surrounding geometry needed to distinguish
eastward bands, eddies and equatorial flows. Before requesting the new cube,
the protocol fixed50–90E/2N–10S,2013, both components and all native grid cells.
The earlier datasets and audits were known; this is exploratory selection.

## Original source

NOAA OceanWatch ERDDAP dataset yearly_336c_0b32_9cd3, OSCAR2017.0,
nominal15m upper-ocean mapped vectors. Original metadata permits free use
and redistribution, retaining accuracy/use disclaimers. Exact CSV and metadata
responses, requested/resolved URLs, HTTP200, UTC acquisition times, byte
lengths and SHA256 are retained in a deterministic source ZIP.

New source:72 actual2013 timestamps ×37 latitudes ×121 longitudes =
322,344 vector positions. All pairs finite; zero both/one-component missing.
The source clock remains nonuniform five/six-day; no73rd record or missing
depth layer invented. Both historical slices reproduce all4464 overlapping
vectors in0–10S exactly: finite float64 bits, signed zero, masks, coordinates
and clocks. Previously acquired10–12S tails remain retained outside this cube.

## Derived fields and maps

Twelve monthly paired-vector means retain all4477 cells per month, paired
counts, contributing source indices and actual clocks. January has7 source
times, February5 and other months6. At least five complete pairs are required;
missing one component excludes the pair without filling either source value.
All744 overlapping monthly slice cells reproduce historical means/counts/masks
at their finite float64 bits. Independent summation uses a forward roundoff
bound; that bound is not a physical velocity or width error.

The independent twelve-panel SVG/PNG uses equirectangular longitude/latitude,
a fixed−0.4 to+0.4m/s eastward-component scale, explicit clipping counts,
fixed0.2m/s vector key,4-column/2-row display thinning and two comparison
meridians. All unthinned values remain queryable. A twelve-row summary provides
source coverage, clocks and spatial component extrema. Component extrema are
not width ranges or annual physical variability. Fine islands/land masks are
not resolved by this coarse product even where every source vector is finite.

The SECC dashboard owner records a source-context update and four evidence
links: map, complete monthly fields, scalar monthly summary and original ZIP.
The common
Rust/WASM lossless source store exposes both data forms. Card disclosure and
query navigation retain keyboard access and320px layout. No original ZIP is
downloaded automatically. The source update does not add current observations
to the catalogue's observation-date evidence or claim physical geometry.

## Scope and continuing gaps

Current association, total-flow axis, paired boundaries, flow-normal width,
whole-current length, uncertainty, physical annual ranges, state passage and
NASA identification remain unresolved. The frequency-classification window
from Huang2023 is not used as flow boundaries, and no EOF-paper reproduction
is claimed. This closes surrounding-source custody and visualization for the
declared investigation; it does not close the final current-width admission.

Accepted catalogue101 names/28 proposals,12 ranked lengths/89 unranked,
158 scoped widths/83 owners and18 uncovered-width owners remain. Expected
lossless source documents426, main collections50/59,828rows and diagnostics55.
Only the SECC owner/source fingerprint should change; prior data rows, dates,
source originals and23 scientific reports/producers must remain exact. The
new source report is included as the24th scientific reconstruction target.

## Reproduce

```powershell
# Acquisition is explicit; never overwrite an existing source directory.
python analysis/acquire_indian_secc_oscar_2d.py
python analysis/build_indian_secc_oscar_2d_source.py
python analysis/build_indian_secc_oscar_2d_source_figure.py
python -m pytest analysis/test_indian_secc_oscar_2d_source.py -q
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
$env:OSW_TEST_BROWSER='C:/Program Files/Google/Chrome/Application/chrome.exe'
python analysis/test_indian_secc_oscar_2d_browser.py
```

Ten source/mean tests and109 Rust tests passed. Source figure and320px card
were visually inspected; the initial bottom caption overlap was corrected.
Final dashboard, source index, packet, native atlas and WASM builds passed.
Both actual Chrome gates passed: new12 monthly fields/12 summary records are
exact in native/WASM queries; existing12 West Australian fields and paired
support remain exact. Keyboard navigation,320px reflow and zero automatic
original-archive requests passed; the direct ZIP link is verified.

All23 previous reports and their23 producers remain byte exact against aa9b5fc.
All prior scientific typed rows are unchanged; only the SECC object fingerprint
and evidence links change. The final archive link changes only those links and
their dashboard provenance receipts in the packet. All386 staged engine input
hashes match, including the original numerical ZIP. All426 indexed source-file
hashes match. The packet is139,747,499 bytes in9 parts; WASM is49,475,839 bytes.
The source corpus retains301,302,385 original bytes, compressed to46,212,707.
Superseded generated transport parts were retired only after exact hash/length
and workspace containment verification; source originals remain retained.
66 top-level JavaScript syntax checks passed; no JavaScript implementation
changed. The new report is registered as scientific target24; the entire24
report reconstruction suite is not claimed as locally rerun.

At aa9b5fc/run39710076013, scientific-reproduction and NetCDF passed;
offline stopped before tests on retained IRD Rotschi1972 HTTP403. This source
intake does not repair that external acquisition. Full local suite remains
unrun below its4GiB disk guard; no overall green CI or completed program claim.

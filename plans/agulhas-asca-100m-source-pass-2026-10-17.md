# Agulhas ASCA100 m: exact source subset and first quality review

Continues the same current-gap branch and PR83. Source acquisition, quality
review and Rust/query/atlas integration are complete. Dedicated actual
native/WASM/source/inspector/mobile checks pass. All45 collection checks pass; current-card sweep and full
publication gate remain pending. Dimensional operators, new width records and
scientific current boundaries remain unadmitted.

## Source identity and rights

Beal Lab / University of Miami, Agulhas System Climate Array (ASCA), source
product version2.0, Zenodo record versionv1, DOI10.5281/zenodo.20515068:
https://zenodo.org/records/20515068

The linked file ASCA0618_gridded_TS_UV_V2.nc has provider size2,023,275,108
bytes and published MD5 071e845768f46f2c3485523219350063. The complete file was
not acquired or verified. Retain that distinction: exact selected source bytes
are protected by their response and reconstructed-array SHA256s. The provider
record declares CC BY4.0; retained header also permits redistribution/use.
Credit Beal, project leader; McMonigal and Gunn, data curators; Novelli, data
manager; and McMonigal et al.(2020), doi:10.1175/JPO-D-20-0018.1, and Gunn et
al.(2020), doi:10.1175/JPO-D-20-0093.1, for observations and mapping methods.

The lab's current data page links to this exact record:
https://beal-agulhas.earth.miami.edu/data-and-products/index.html
It reports a2021 correction to ASCA ADCP rotation. Its separate September2026
salt-transport correction is not a new velocity-field version. Original papers,
corrigenda, instrument spacing and mapping uncertainty need review before any
width analysis. Source header says product version2 but history first version;
retain both facts without treating it as an uncorrected raw instrument archive.

## Frozen selection and preservation

Selection was declared before deriving any widths: all931 source times, all601
along-array cells, source100 m depth (index5 of226), all four variables temp,
sal, v and U. Native dimensions are time/depth/distance, float32 big endian.

The source NetCDF3 header and complete coordinate arrays occupy bytes0-11011.
Using offsets in that pinned header,59 HTTP multi-range responses retain exactly
3,724 field/time slices,9,389,366 response bytes and2,238,124 scalar values,
including NaNs. No source PDF or complete2GB NetCDF packaged. The59 original
response bodies, coordinate/header prefix, provider record and acquisition
receipt are retained under research/source-data/asca-2016-2018-100m/.

Original scalar bytes, order and missing masks are unchanged. Array SHA256s:

| Source variable | SHA256 of source float bytes, source time/distance order |
| --- | --- |
| temp |1fb84eaa119f6d3bdfbf1ae6772bdf08aacb3ee45998e729771822ddf8fe77ad |
| sal |48a7f9477566cc8597531433357548d9e301579ef27354b6cbc855232e57829d |
| v |ddbffe123e1acdfc5d3b87bd8f428a8f14ae824108870b8be2b3dda66771e22e |
| U |04200dcec2cd40cbd00b2bb3dff56719f2e367e8eac2d2502f17d887a012abde |

Independent response checks on acquisition:42 temperature profiles agree
byte-for-byte with the earlier partial full-file response. The first v/U profile
agrees with a separate two-range request. These are transport cross-checks, not
independent scientific measurements. All source ranges and aggregate float-byte
hashes are rechecked offline by analysis/check_asca_100m_source.py.

## Quality findings and rules

- Source period19April2016 to3June2018:27 calendar bins with partial first/last
  months, not27 full monthly observations or a long-term climatology.
-931 timestamps stored as float32 epoch seconds. Actual increments71,936 and
 72,064 seconds, deviating by at most64 seconds from a nominal20-hour clock.
  Calendar-bin membership is identical under that sensitivity check. Preserve
  supplied timestamps; no clock restoration or silent rounding applied.
- Output spacing500 m is interpolation, not independent instrument resolution.
- Finite cells: temp519,378; sal520,429; v519,799; U308,161. No infinite values.
  Retain variable-specific masks. Paired v/U positions308,161; unavailable pairs
 251,370. Across-array v remains available over offshore regions lacking U.
- v is negative southwest; U is positive southeast along the array. Do not
  interpret either alone as total speed, fill U with zero or rotate incomplete
  pairs into an invented complete geographic vector field.
- A missing cell does not establish land, an edge or physical current absence.
- Header geographic bounding box provides regional context; it supplies no
  paired current edges or diagnosed current footprint at any time.
- No half-speed, fixed-speed, zero-flow boundary, core selection, obliquity
  correction, seasonal extremum or current-width error has been adopted.

## Required information and visualization

Independent source-field plot: figures/agulhas-asca-100m-source-fields.png.
It displays all931 profiles for the four fields; gray is unavailable source data.
Axes use along-array distance and supplied UTC time; the two velocity color scales
are centered on zero. This is a fixed-depth source overview, not an occupied map.

Reproduce and verify without a provider connection:

```powershell
python analysis/check_asca_100m_source.py --figure figures/agulhas-asca-100m-source-fields.png
```

Three negative checks pass: same-length header and raw-response corruption,
and changed selection depth, are rejected. Restored source validates. Prototype
figure reviewed; revised subtitle spacing removes an overlap. No existing
query bundle, canonical measurement, route, width sample or dashboard changed by
this source pass. Scientific and query integration remains the next step.

## Prepared chronological data packets

`analysis/build_asca_100m_sections.py` now exports the exact finite source
float32 values into `research/agulhas-asca-100m-observed-profiles.json` and
27 descriptive calendar sections into
`research/agulhas-asca-100m-monthly-sections.json`. The generated
`research/agulhas-asca-100m-query-contract.json` binds both files, source
acquisition, builder and aggregation protocol by checksum. This contract is
prepared; it is not registered in the current Rust engine or index catalog.

All finite source values round-trip through JSON exactly and every NaN position
remains null. Independent Python statistics checks agree for all64,908
field/cell/month counts, means, sample standard deviations and nulls. Paired
vector means use common original-time masks, independently of scalar means.

The coverage rule explicitly allows the source's64-second float32 clock bound
when testing one nominal20-hour endpoint interval. Without that allowance,
four full nominal schedules would be mislabeled incomplete by64 seconds. No
timestamps or monthly memberships change.25 bins have full nominal calendar-time
support; April2016 and June2018 are partial, with15 and3 source records.

## Next implementation contract

1. Register a typed `current_sections` collection for27 monthly section records;
   keep the931 original timestamped profiles queryable in the lossless source
   store. Avoid adding profile rows to scalar mooring velocities, model frames,
   width measurements or width-sample families with incompatible definitions.
2. Bind the collection and exact source JSON to the compiled query contract.
   Reject coherent owner, date, mask, mean, sample-count, paired-support, source,
   calendar-completeness and dimensional-admission alterations in native/WASM.
3. Add actual query-chart selection and chronological frame controls, plus direct
   current-card and inspector links. Use the existing query UI, with exact source
   filters on record.year and record.month. Preserve years and partial-bin labels;
   no annual wraparound, invented intermediate frames or typical seasonal cycle.
4. Present field-specific means/counts and descriptive spread. Paired-vector
   support is separate; missing offshore U must stay visible. Array distance is
   not geographic current extent. The current's existing map remains context.
5. Add dashboard evidence/time-series links and source fingerprints for Agulhas.
   The source profiles add data coverage; scoped-width counts remain146 across76
   owners. Preserve all earlier widths, samples, routes and canonical arrays.
6. Verify actual query/atlas/inspector/mobile and source-query parity through the
   native/WASM store, plus the new collection in complete mainline coverage.
   Review with the repository roles before publication. Do not rebuild the native
   executable while the current full-suite process uses it.

## Original methods and correction review, 17 October

Read Gunn et al. (2020), DOI10.1175/JPO-D-20-0093.1, original
pages3546-3548 and3558, from the institutional copy at
https://eprints.soton.ac.uk/483992/1/phoc_jpo_d_20_0093.1.pdf.
This review establishes processing context, not new numerical width admission:

- The array includes seven tall moorings and four CPIES instruments. Typical
  instrument spacing is about30 km horizontally; the500 m output grid is
  interpolation. Offshore CPIES pairs provide geostrophic velocity, distinct
  from direct ADCP/current-meter measurements closer to the coast.
- The paper describes40-hour low-pass filtering,20-hour subsampling and
  regression extensions of incomplete instrumental records. These are processed
  observational fields, not931 independent instantaneous surveys.
- The article describes20 dbar vertical output spacing; the retained NetCDF
  coordinate is explicitly depth in metres. Keep the actual file coordinate and
  this documentary distinction; do not silently relabel100 m as100 dbar.
- ADCP surface coverage can be limited by mooring blow-down. Offshore
  upper-ocean scalar reconstruction includes satellite-based information.
  Missing100 m velocity components remain missing, despite available scalars.
- The original219 km mean zero-isotach coast-to-jet transport limit is not the
  half-peak100 m section metric. Do not copy it into this fixed-depth series,
  use it as a whole-current width, or adopt it before the corrections are checked.
- Published velocity-error profiles distinguish sampling, instrument and
  reconstructed-record contributions. A depth-averaged error is not a100 m
  pointwise uncertainty or a lateral-edge error bar. No such error is assigned.

Corrections identified: Gunn et al. (2022), DOI10.1175/JPO-D-21-0172.1,
and McMonigal et al. (2022), DOI10.1175/JPO-D-21-0175.1. The latter's
institutional abstract at https://hdl.handle.net/10948/2044870 confirms an
ADCP rotation coding error at moorings C/D, affecting published mean transports,
and replacement of the original supplemental animation. Full corrected tables
and figures remain unreviewed; publisher access returned403 and the repository
provides metadata without a downloadable paper. The Beal Lab's corrected
velocity product is the source retained here; no independent rotation repair
is applied. Original transport values or old figure boundaries cannot establish
new dimensional records until the corrected source is examined.

New focused source/aggregation gate:10 tests pass in27.69 seconds, including
all monthly field and paired-support statistics, exact finite float32 bits,
null masks, timestamps, partial bins and four corrupted-source rejection cases.
These tests are separate from the already-running Loop publication suite;
that earlier invocation does not cover this new test file.

## Prepared Rust scene and renderer

The unregistered `rust/osw-query/src/current_sections.rs` validates the monthly
source against the small compiled query contract, exact source bytes, dependency
pins and current-owner links. It projects chronological frames with axes fixed
to the full27-frame series, separate scalar and paired-component statistics,
source filters and attribution. It does not embed the37 MB original-profile
JSON into the engine. Eleven coherent negative cases reject altered means,
availability, paired counts, year, owner, geographic edges, annual range,
deleted frames, joins, counts and contract pins.

The new `almanac/current-section-charts.js` renders these scenes with four
field charts, missing-cell breaks, descriptive sample-spread shading, exact
cell support, source/inspector links and chronological manual/play controls.
Playback stops at the end; reduced motion disables autoplay. At320 px the
chart itself scrolls horizontally; page controls fit the screen. The first
browser check caught an intrinsic select-width overflow, now corrected.
Desktop/mobile screenshots have been visually reviewed.

Validation used a separate small offline Rust harness under
`.pytest_cache/asca-rust-prototype`, without changing the running mainline
executable. It compiles the actual new module and generates the renderer scene
from the frozen source. `analysis/test_asca_section_renderer_browser.py`
passes all27 frames, field availability, source filters, inspector callbacks,
mobile layout, discrete playback and reduced motion. The10 source tests pass
again in21.56 seconds after fixing a corrupted separator in generated labels.

The preceding preparation checkpoint used an isolated harness. The integration
below followed after the Loop full-suite invocation passed; that checkpoint had
146 scoped widths /76 owners and44 collections.

## Integrated current-sections collection

Integrated against Loop checkpoint8225959 and acquisition-CLI correction2efe752
on the same branch and PR83. Source packets regenerate from retained bytes;
builders reject stale or altered packets. The small compiled contract now has
status `frozen_source_section_query_contract`.

- 45 query collections, including27 `current_sections`;269 indexed JSON sources,
  including all931 original profiles.25 series, retaining all24 earlier rows.
- 146 widths /76 owners,271 width samples,75 reference routes and33 diagnostics
  remain unchanged. All42 other legacy collections compare equal to8225959.
  Only Agulhas dashboard content changes; new empty section joins are added to
  other query objects without changing their scientific content.
- Agulhas time evidence and source fingerprints include the new sections and
  source contract. Its scoped-width capability remains1. Time samples become27.
- Existing atlas card links to the real monthly charts. Both card inspector and
  raw-profile source query are reachable through the existing query page.
- 10 source tests pass in11.23 seconds;47 Rust tests pass. WASM3,258,640 bytes;
  query bundle71,764,032 bytes. The raw37 MB source-profile JSON remains in the
  independent source corpus and is not embedded in the WASM binary.
- Actual browser/native/WASM parity passes for27 frames, source filters,
  inspector, atlas navigation,320 px layout and reduced motion. All11 coherent
  source/projection/admission alterations reject in both native and WASM engines.
- The dedicated integration test is registered first in the normal shipped-WASM
  runner. All45 collection checks pass;100-current-card sweep is running; final default
  offline publication validation and review remain pending.

The first browser attempt found the prior suite's temporary server had stopped.
A verified loopback server was started before rerunning; the complete actual
integration test then passed. The mobile chart-scroll hint now precedes charts.

Reproduce integration after source packets are prepared:

```powershell
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
python -m pytest -q analysis/test_asca_100m_sections.py
python analysis/test_asca_sections_browser.py
python analysis/test_rust_collection_coverage_browser.py
python analysis/test_atlas_inline_width_browser.py
```

Never rebuild the native executable while a validation process uses it. Original
method corrections, geographic source-line reconstruction, physical edges,
width uncertainty and annual extrema remain separate open scientific work.

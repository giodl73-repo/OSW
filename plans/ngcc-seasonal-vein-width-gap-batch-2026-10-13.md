# New Guinea Coastal seasonal vein width batch

Continues draft PR #83 on `codex/current-measurement-gaps`. Previous turn was
progress: South Indian section data was verified, committed and pushed as
2b9b329. This batch fills a missing source-width assessment for NGCC.

## Primary evidence

Radenac et al. (2016), DOI 10.1002/2015JC011438, section 5.1 / printed p2242 /
retained PDF13, directly reports three related surface current-anomaly vein
descriptors: 120 km east of Vitiaz Strait at track 099, 100–200 km west of the
strait, and near 200 km at the two widest western tracks 023 and 201. Keep
the last as one descriptor covering two sites; it is a subset of the western
range, not an independent measured mean or two extra replicates.

The paper separately describes a 100–150 km cold-water vein following the
current core west of the strait. This fourth record is a thermal-water-mass
metric. The identically numbered 100–150 km offshore core location is a
different quantity, as are NGCUC width, strait breadth, Gaussian preprocessing
scales, summer core displacement and lateral Ekman/upwelling scale.

Section 5 declares 2001–2010 reconstructed monthly seasonal climatology with
150–500 day filtering; Figure 10 illustrates August/February. The source
width prose belongs to the trade-wind/austral-winter discussion. It does not
supply twelve monthly width samples, exact width dates, numerical errors,
uniform depth bounds or paired geographic edges. Figure 3's half-maximum
standard-deviation envelope is a separate full-period variability operator;
prepared raster readings were not admitted as these seasonal descriptors.
The conflicting section 2.2 cruise-season labels remain explicitly unresolved.

Complete unchanged HAL deposit: 7,675,633 bytes, 23 pages (cover plus 22 journal
pages), SHA256 `6da50667b80790752fa0189ff9cf0cdfd88c521509b0f393365de306286bacbe`.
PDF pages 1,2,6,7,11,12,13,14 were visually inspected. Copyright/all-rights-
reserved is retained; original PDF and figures remain ignored. Only factual
annotations and independent point/interval charts are published.

## Integration and invariants

Add four scoped descriptors with two distinct metrics and two source-claim
groups. The three current-anomaly descriptions overlap geographically and
are not independent replicates. The western ranges retain null midpoints;
all four retain null numerical uncertainty, exact dates and fixed-depth
geometry, with ranking/full-current/annual-extrema admission false.

Source-width inventory becomes 136 records across 72 owners; 15 owners remain
unassessed. All 132 earlier records are unchanged. Only the NGCC dashboard
fingerprint changes; every observation date is preserved. Canonical data,
11 ranked lengths, 89 length gaps, 73 reference routes and 175 query samples
remain unchanged. The seasonal route file refreshes only its width-inventory
checksum. Source corpus becomes 203 exact JSON documents. The original joins
the strict local-paper hydrator, now 31 locally verified originals.

Native/WASM source guards freeze each row's metric, scope and source group,
and require the complete four-record inventory for the imported NGCC owner.
The atlas shows all four charts; query/source inspection reaches their exact
blueprints. Seasonal inspector titles distinguish current-anomaly and thermal
records. Those four width phases are static; the two previously supported
local direction phases retain playback. No width footprint, route buffer,
state containment, NASA identity or annual current geometry is inferred.

## Verification and publication

46 Rust tests and serialized locked native/WASM builds passed. Focused source
and inventory tests: 42 passed / 563 subtests. Browser passed four descriptors,
two metrics/source groups, native/WASM parity, atlas/source inspection, mobile,
four static seasonal selections, two retained direction phases, and three
native/WASM rejections (midpoint, metric substitution, missing descriptor).
Final complete offline and 203-document source-store results are appended.

Reproduce with local original verification; width validation; dashboard,
index-corpus and query-bundle builders; serialized engine build; then default
offline pytest and the new browser/index-store checks against localhost:8788.
Source acquisition is explicit and excluded from default offline tests.
Seven-role internal review is editorial; scientific full-current and annual
width admission remain unresolved. Prior-head CI 38493743460 stopped before
tests at a Melet original checksum mismatch. No alternate paper or pin used.

## Final publication gate

**1,336 tests and 957 subtests passed in 1239.89 seconds (20m39s).**
All 46 Rust tests and serialized locked native/WASM builds passed. Focused
source/inventory gate: 42 tests / 563 subtests. Final browser passed four
descriptors, two metrics and shared claims, native/WASM parity, atlas/source
access, 320 px reflow, four static width phases, two retained direction phases,
and three native/WASM rejection cases. Source-store browser passed all 203
exact documents, 12 seasonal snapshots, independent NOAA oracle, native/WASM
parity and checked-input failures. All 61 engine and 203 source pins verified;
all 31 local originals verified. Previous 132 rows, observation dates and
seasonal route frames retained; inventory CRLF and whitespace gate preserved.

Visual QA found the thermal interval's high label clipped in the shared SVG
renderer. Final supplemental browser checks verify horizontal label bounds;
the renderer fits close labels with small leader lines when needed. Numeric
values, markers and source interval meanings are unchanged. Point/current-
range/thermal-range captures were inspected after the fix. No original source
figure or PDF published. Internal editorial publication conditions satisfied;
physical full-current widths, mapped edges and annual ranges remain unresolved.

Final code review removed dependence on source-list position: the NGCC inventory guard locates its frozen source by stable owner identity. Rebuilt engine passed all 46 Rust tests; final native/WASM descriptor and 203-source browser checks passed again. Measurement and source bytes are unchanged.

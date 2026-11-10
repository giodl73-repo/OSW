# Caribbean RU29 dated source coverage — 23 October 2026

Continuing branch `codex/current-measurement-gaps`, existing draft PR 83.
No main merge and no new PR. The wider current length, physical width,
seasonality, identity, geometry and eddy inventory objective remains open.

## Added evidence

Gradone et al. (2026), DOI 10.5194/os-22-735-2026; source dataset
10.5281/zenodo.18332586, Joseph Gradone / Rutgers, CC BY 4.0.
Eleven selected original NetCDF products are retained unchanged: the processed
mission velocity product, two complete interpolated occupations and both
rotations' tracked, untracked, short and correspondence eddy products.
The full 1.07 GB archive was not downloaded or checksum-verified. Selected
member payload ranges, ZIP sizes/CRC32 and local SHA256 were checked.

The complete recursive readback retains **306 variables and 3,609,111 values**,
original packed values, exact integer clocks, attributes, dimensions, masks,
contour padding, file-local IDs and all four nested virtual-state groups.
It is a source inventory, not 3.6 million independent observations.

The current layer includes 486 processed mission profile slots plus two
100-depth by 97-latitude interpolated occupations with both horizontal
velocity components. Four comparable panels use one fixed ±0.5 m/s scale;
there are zero finite values beyond that display scale in those panels.
All full values remain in the mirror. Grey means missing.

Source-page entry: `/almanac/caribbean-source.html`. It provides the four
panels, source-file/field search, group-aware inventory, and a lazy numerical
cell reader for both complete interpolated occupations. The 1.07 MB page
payload copies source records unchanged. The 44 MB complete mirror and
originals are not downloaded during ordinary page browsing.

## Frozen calculation history

1. Commit `7a867da`: v1 producer, protocol, 13 synthetic checks, preflight,
   originals, custody and initial metadata review frozen before array readback.
2. Actual v1 readback rejected nested groups in the first correspondence file.
   Source arrays had been read; no public mirror/report/figure was emitted.
   The original method and failure are retained unchanged.
3. Recursive metadata inspection identified LastVirtualObs and
   LastPreviousVirtualObs in each correspondence file. Future source schema
   reviews must inspect nested structure before the first method freeze.
4. Commit `fd05d20`: v2 recursive reader and two additional synthetic checks
   frozen before actual recursive readback. It imports the original v1 display,
   raw summary and encoding operators unchanged.
5. Actual v2 readback passed. Exact replay of all three products passed.
   An independent original-NetCDF comparison passed for every source array,
   group, mask and attribute. A separate check binds both complete occupation
   payload records to the retained full mirror.

Products:

- `research/caribbean-ru29-source-fields-v2.json`
- `research/caribbean-ru29-source-inventory-v2.json`
- `figures/caribbean-ru29-velocity-sections-v2.svg`
- `research/caribbean-ru29-source-page-v1.json` (delivery copy)

## Interpretation and unresolved source issues

The provider's multiweek occupations are not instantaneous maps. Exact
declared windows are 27 April 20:05–18 May 12:00 and 18 May 12:00–6 June 00:00
2024 UTC. The fixed 69°W interpolation grid is not the actual trajectory.
The paper states navigation missed full current width and the approximately
1000 m depth limit missed deeper flow. No new whole-current length, physical
width, seasonal envelope, rank, official eddy name or state intersection is
admitted by this batch. The prior Duncan (1982) dated regional width evidence
is preserved. No existing assessment or query collection was overwritten.

Current variables generally lack unit attributes; figure units are attributed
to paper section 2.1.1 and the Final author notebook. Eddy contour latitude
metadata says degrees_east/axis X; the original text is retained. The paper's
Gaussian filter/1 cm contour description differs from commented Final
notebook Bessel/0.002 code. This remains unresolved. Archived output retention
does not establish reproduction of the eddy detection pipeline. File-local
tracking IDs are not official names; terminal virtual state is not observation.
No transport calculation or verification against the paper's headline transport
values has been performed here. Source RMS O(0.05) m/s is not per-cell CI.

## Local verification and operating limits

- 15 prospective synthetic checks passed before v2 actual readback.
- Complete actual original comparison and unchanged occupation delivery check.
- Exact v2 report/mirror/figure replay.
- Native Caribbean length query completed before browser launch.
- One browser page: eleven files, 55 fields in the selected correspondence
  product, nested-field filtering, empty search, 320px reflow, keyboard controls,
  and numerical cell readout for both components and occupations.
- Desktop and phone screenshots visually reviewed; no page errors.
- All 671 existing runtime engine input pins remain exact; no existing
  canonical source or current measurement record was changed in this batch.
- All local work at BelowNormal on one logical CPU. Data processing, native
  checks and browser checks ran separately. No build or full-suite overlap.
- Standalone source page has its own coverage class; it is not labelled a
  WASM measurement admission. Focused checks and source replay assigned in CI.

## Canonical query and atlas admission follow-up

The complete readback is now available through the existing Rust source-query
store. Thirteen pinned JSON sources are registered; source catalogue count is
548. The main query bundle adds one scoped diagnostic and two source records,
without embedding the 44 MB readback in that main bundle. The Caribbean card
links directly to the visual page, diagnostic, original field inventories,
both occupations' velocity cells and retained virtual tracking state.

`analysis/caribbean_ru29_query.py` verifies the frozen scientific products and
the complete occupation payload before building the delivery contract.
`rust/osw-query/src/caribbean_source_fields.rs` binds exact records, dependencies,
catalogue descriptors, owner references, card scope and links. It rejects
promotion of these source records into dimensions or reconstructed observations.
The source mirror retains every field; source-query records use file-scoped
JSON pointers, not official eddy names or verified geographic memberships.

### Local gates

- Nine admission tests pass, including complete navigation pointers and atomic
  rejection of duplicate records or missing owners.
- All 147 Rust tests pass, including four new source-admission tests.
- Native full atlas validation passed before WASM compilation.
- WASM: 49,279,603 bytes. Separate compressed source corpus: 71,040,814 bytes.
- Preservation: 108,437 of 108,438 prior rows exact. The sole changed prior
  row is the Caribbean card; only source references, source accounting,
  fingerprints, evidence links and the scoped source context changed.
- Exactly three records added; 108,441 total rows in the same 54 collections.
- All 535 prior source descriptors and source bytes remain exact. All 13
  ranked lengths, 170 widths and 78 reference routes remain exact.
- Native source query matched all eleven original-readback members and all
  3,609,111 retained values against the frozen mirror before Chromium opened.
- WASM matched all three complete current variable groups and all four terminal
  virtual-state groups. Both tracked-observation flag first pages were checked;
  complete flag arrays are covered by the native full-mirror comparison.
- Browser query workspace closed before atlas workspace creation. Keyboard
  disclosure and card-to-visual navigation pass at 320px. Actual source-query
  and phone screenshots visually reviewed. No original PDF/ZIP/NetCDF fetched.

### Corrections retained during delivery

The initial adapter omitted the two new owner source references; admission
tests caught this and the adapter now adds them atomically. Preservation then
caught source-group list aliasing: supporting metadata was being counted as
source records. The Caribbean source group is now separated from its source
record list. The typed query card also restores its existing NASA-crosswalk
media-ledger reference, `source:4f7441b953be4651`, which was previously omitted.
The final five registered source references match the displayed count. No new
scientific dataset is claimed for that restored ledger reference.

The first browser run completed source comparisons but failed to find a link
inside the collapsed evidence section. The corrected test opens that existing
section with the keyboard; the complete second run passes. Initial failure
state, source screenshot and test snapshot are retained privately.

After the full native/WASM build, the source-count and reference corrections
required runtime-data regeneration. All 696 compiled/static engine inputs
were verified unchanged; the corrected bundle passed native atlas validation.
Only the runtime packet references in the engine manifest were refreshed.
WASM bytes, source catalogue and scientific source products remained exact;
the compiler and 147-test suite were not repeated for this metadata correction.

All heavy local stages ran separately, BelowNormal on one CPU. A browser GPU
helper reset its limits; the owned-descendant monitor reapplied them. Private
receipts: `.pytest_cache/caribbean-ru29-delivery/`, including corrected-build,
final-runtime-v2, preservation-result.json and browser/result.json.

### Remote and remaining work

The preceding pushed source-layer head `9ebc91e840cff02ad2dbcfa971b8109806247678`
has terminal Linux conformance success, job 120584011886. Its log verifies all
17 focused source checks and exact hashes for mirror, inventory, figure and
page payload. This is prior-head evidence, not fresh CI for the canonical
admission. Fresh-head CI must be observed after publication. The older offline
acquisition failure and the separate full regression gate remain open.

No whole-current length, physical width, seasonal envelope, official eddy name,
geometry or state membership is added. The wider current measurement and
required visualization objective remains active; this source admission does
not complete the core gap campaign.

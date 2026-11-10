# Consolidated current measurement gap batch

2026-10-13. Continues branch `codex/current-measurement-gaps` and draft PR #83; subsequent current gap work accumulates here. No PR per current or measurement.

## Scope and rules

The Caribbean dated 410 km section-width evidence remains in this batch's parent commit. This addition supplies three previously missing regional reference routes using the existing M01-M13 protocol, unchanged WGS84 generator, original-source receipts, and 81 retained scenarios per route. It adds no published whole-current lengths, physical widths or annual dimension ranges.

| Current | Declared regional reach | Approximate route length | Editorial scenario envelope |
| --- | --- | ---: | ---: |
| New Guinea Coastal Current | Northwestward surface reference, selected 146 E to 142 E gates | 500 km | 400-600 km |
| Mauritanian Current | Summer surface reference south of Cap Blanc, selected 17 N to 20 N gates | 300 km | 200-400 km |
| Tasman Front | Historical Australia-northern-New-Zealand connection, selected 154 E to 172 E offshore gates near 34 S | 1,700 km | 1,600-1,800 km |

These numbers measure OSW's declared polylines. Gates and bends are editorial, not observed origin/termination, current core, coast length or measured meanders. Scenario bounds describe drawing/gate choices; they are not seasonal ranges or confidence intervals. All three are studied reaches excluded from both published length ranking and the comparable reference-route ordering.

## Source support

Retained Tomczak/Godfrey university-hosted compilation: 36,625,246 bytes, 401 pages, SHA256 `35e36f9b834c9c31c2cee64abc36d0c687d71e3d388c2cf1c40bc026e613738b`. Original and acquisition receipt unchanged. This batch reviewed PDF pages 121,135,136,137,138,139,259,260; selected relevant pages rendered and visually inspected. The existing acquisition review describes the earlier review; new per-current scope audits record this extension.

- NGCC: Figure8.6 (printed111 / PDF121), discussion printed125-126 / PDF135-136. Chapter8 version1.1 March2005. April-November surface reference reverses during December-March; northwestward flow below200m belongs to excluded deeper context. No fixed layer or seasonal geometry extracted.
- Mauritania: printed249-250 / PDF259-260, chapter14 version1.2 September2002. Summer surface poleward geography south of CapBlanc; winter subsurface continuation toward CapeBojador excluded. This passage does not specify month windows; no calendar manufactured.
- Tasman: printed127-129 / PDF137-139, chapter8 version1.1 March2005. Historical connection, meanders and statistical front position. Separate1979 hydrography and1982-1985 SST observations do not date OSW's line. Oke etal2019, doi:10.1016/j.jmarsys.2019.103217, author institutional abstract read; full article not acquired. Its contrary interpretation of discontinuous streams/eddy fields is retained in the audit, source card and time convention. The canonical name is an atlas index, not proof of a continuously identifiable jet.

No original PDF, source figure, digitized curve or restricted field is redistributed. Independently selected geography and attributed factual annotations are packaged. Coarse land clearance does not establish shelf, reefs, bathymetry or velocity correspondence.

## Integration

67 reference routes now cover64 of89 currents lacking published ranked lengths;25 lack a route. The100-current ledger,11 published length owners,128 scoped width records across68 currents and seasonal-route frames are unchanged. Only `current:new-guinea-coastal-current`, `current:mauritanian`, and `current:tasman-front` dashboard fingerprints change in this addition.

Family and endpoint audit basis hashes were reviewed/refreshed. Indian SEC and Pacific NEC monthly extraction documents change only `scope_audit_sha256`, with numerical series unchanged. No new family identity admitted.

The lossless index includes all three inputs, reports and audits (168 source documents). Query bundle retains42 collections, now67 reference routes; canonical scientific claims unchanged. Atlas selection, full map card, source contexts, NASA crop context and display-state joins use the existing UI. NASA links and atlas state crossings remain geographic display context, not current identification or physical containment.

## Reproduction and verification

For each of the three `*-reference-path-input.json` files, run `python analysis/build_current_reference_path_candidate.py --input research/<input>`; rebuild the route catalog, refresh reviewed family/endpoint dependency receipts, rebuild the two monthly bifurcation extractions, rebuild catalog/dashboard, index corpus, query bundle and serialized native/WASM engine. Do not rebuild executables while tests use them.

Full gate: `python -m pytest -q`; browser gate: `python analysis/test_reference_route_atlas_browser.py` with Chrome via `OSW_TEST_BROWSER`. Source originals must pass their acquisition SHA pins. New estimates use existing geodesic, protocol, topology, receipt and cross-layer rejection tests. Browser regression now derives total route count from the catalog and explicitly exercises all three new map-card links and 320px reflow.

### Final stable results

- Complete offline suite: **1,293 Python tests and 925 subtests passed**, 1002.72 seconds (16m42s). The earlier pre-label-fix attempt was interrupted and is not counted.
- Serialized native/WASM engine: **45 Rust tests passed**; locked builds passed. WASM 2,547,884 bytes; query bundle 47,594,351 bytes. All 60 engine dependency hashes checked against final files.
- Atlas browser passed: 100 selectable currents, 67 route cards, all three added map-card links and source caveats, global zoom/pan/reset, 140 eddy records, keyboard interaction and 320px reflow. Three mobile cards visually inspected; SVG source-label clipping corrected before final browser run.
- Index browser passed: 168 exact source documents, 12 seasonal snapshots, independent NOAA oracle, native/WASM parity and checked-input rejection cases. All 168 current source-file byte hashes verified against the catalog.
- Lossless index: 77,231,806 original bytes / 5,534,275 compressed bytes. All 64 earlier route catalog records and comparable reference-route ordering unchanged.
- Frozen original/input/audit receipts verified. Only the three new route owners change dashboard fingerprints. Prior widths, ranked length evidence, current ledger and seasonal-route frames byte-identical; both prior monthly extractions differ only in their dependency receipt.
- Seven installed role lenses: 21 P3 findings resolved or retained as physical-admission limits; 0 P1/P2. Internal review permits editorial delivery and does not supply independent scientific approval.

Publication remains the same draft PR; no scientific admission or mainline claim.

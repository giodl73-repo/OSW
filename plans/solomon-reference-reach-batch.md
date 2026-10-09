# Solomon Islands reference reach

2026-10-09 UTC. Editorial atlas coverage; no canonical measurement admission.

## Evidence and scope

Melet et al. (2010), DOI 10.1175/2009JPO4264.1, proposes an equatorward SICU east of the Solomon Islands. The coauthor abstract is available; indexed primary text gives a 1986–2004 model mean in the sigma 24.0–26.5 thermocline layer. The original full article and its Figure 4 remain inaccessible. OSW has not digitized that figure or reconstructed its velocity field.

Ganachaud et al. (2017), DOI 10.1525/elementa.221, is retained unchanged under its printed CC BY 4.0 license. NOAA's institutional checksum matches the 4,409,638-byte, 27-page PDF: `981f64dfa09125766a185228391a4e8099f98285cedaaaedecccc9533fa03b9e`. Figures 1, 2 and 7, relevant methods, page 17 SICU discussion and the page 27 license were inspected. This is a selected-page source review, not reproduction of every analysis in the article.

The later paper interprets northward SICU flow near northeast Bougainville. It distinguishes adjacent stations 42 and 43 and finds no ADCP flow between them. Similar tracer profiles at stations 13 and 43 do not establish a continuous route. Figure 7a/b uses an altimetric anomaly and drifter climatology composite; 7c/d uses shipboard ADCP in two depth layers. The surface northwestward flow described on page 12 cannot define the complete undercurrent axis.

## Measurement rules

The shared protocol M01–M13 applies unchanged. OSW supplies six geographic offshore vertices and two alternative shapes, with uniform longitude shifts and independent endpoint latitude shifts: 81 retained scenarios. Initial central-chain placements touched the coarse land mask near Malaita; vertices were moved east and the entire grid regenerated. Coarse clearance does not establish reef clearance, bathymetric support or current core position.

The declared reach is between 162.0 E, 9.6 S and 155.8 E, 4.6 S. Its WGS84 polyline sum rounds to approximately 900 km, with an 800–1,000 km rounded editorial scenario envelope. These bounds concern chosen paths and endpoints, not measured seasonal changes or statistical confidence. The reach is excluded from published whole-current ranking and provisional comparable-route ordering. NICU continuation, Solomon Strait crossing and upstream SEC are excluded. Width, annual ranges and continuous measured-axis dates remain null; seasonal playback remains unsupported.

Retained-original receipts now bind route owner, reviewed audit, acquisition receipt and original bytes. Catalog, dashboard and query builds reject changed bytes, cross-owner receipts and inconsistent original metadata. No new dimensions are transferred from neighboring currents.

## Delivery and verification

Atlas: 64 routes /61 of the 89 currents without published ranked length; 28 still without routes. The canonical inventory remains 100 currents, 11 published ranked length owners and 97 scoped width records. Only the SICU dashboard owner changes, so update highlighting remains specific.

Rebuild: candidate → route catalog → route/state join → dashboard → lossless index → query bundle → native/WASM engine. Family naming audit basis is refreshed against the new route catalog without changing any family proposals or admissions.

The family refresh also requires an endpoint-audit receipt refresh and regeneration of the Indian SEC /Pacific NEC monthly extraction receipts. Their numerical series, source PDFs, methods and scientific scopes are unchanged. The source corpus preserves the updated dependency chain.

Browser checks cover SICU selection, route map, source contexts, card deep link, native/WASM query parity, retained null dimensions and mobile reflow. Wider regressions also cover all 100 width cards and the monthly section display. Verification results are recorded below after the final run.

Publication remains a draft branch stacked on PR60. PR60's inspected offline CI job failed during an existing Qiu/Chen paper download, before tests; its NetCDF checks passed. This batch does not claim mainline delivery or a passing remote gate.

### Verified results

- Final stable `python -m pytest -q`: **902 tests /918 subtests passed**, 243.86 seconds. Earlier runs identified the family and endpoint dependency receipts; the complete final run passes after both chains were refreshed.
- Final native/WASM engine build: **41 Rust tests passed**; locked offline native and WASM builds passed. WASM 1,939,784 bytes; query bundle 46,219,972 bytes.
- Browser regressions passed: reference atlas (including SICU, 320-pixel screenshot), three route-map deep links, all 89 route decisions with SICU native/WASM parity, 83 exact atlas source documents and 18 loader rejection cases, monthly section display, all 100 width cards /97 scoped records, dashboard coverage lights, index page and final 118-source index-store parity.
- Final lossless corpus: **118 documents /76,331,745 original bytes /5,439,516 compressed bytes**.
- Query, engine and index dependency hashes verified. Existing canonical current, length, width and seasonal-geometry files byte-identical to parent. Indian SEC and Pacific NEC extraction documents differ only in `scope_audit_sha256`. Only SICU dashboard owner changes.
- Seven-role review: 19 P2 findings addressed, two P3 conditions retained; no P1. External scientific admission remains a separate gate.

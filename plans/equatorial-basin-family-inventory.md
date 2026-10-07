# Equatorial basin-family inventory revision — 2026-10-07

Status: local editorial candidate; canonical identity admission and measurements remain pending.

## What this adds

The 100-name ledger has North Equatorial and South Equatorial family records without basin-qualified member records. NOAA's glossary enumerates Atlantic and Pacific northern flows and Atlantic, Pacific and Indian southern flows under shared terms. OSW proposes five qualified labels and identifiers. These are five inventory proposals, not five newly discovered currents or five admitted measured objects.

The proposed-member audit records source terms separately from OSW labels, source URLs and entry locators, retrieval date, pinned local inputs, parent-family identifiers and missing physical scopes. The expansion worklist grows from 23 to 28 proposals. The atlas displays the proposals as existing inventory cards, while its admitted-current directory remains at 100. The dashboard reports the pending inventory count separately from object coverage.

## Source-convention case held for review

NOAA also uses North Equatorial terminology seasonally in the Indian Ocean. Its approximate calendar is retained only as reported naming usage. Schott, Xie and McCreary (2009), section 2.2.2, describes seasonally opposed summer and winter monsoon flows. The correspondence to OSW's existing Monsoon Current identity remains unresolved. No sixth proposal, alias equivalence, annual geometry or physical seasonal range is admitted.

Sources:
- [NOAA Tides & Currents glossary](https://www.tidesandcurrents.noaa.gov/glossary.html), North Equatorial, South Equatorial and Monsoon entries.
- [Schott, Xie and McCreary (2009)](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2007RG000245), sections 2.2.1.1 and 2.2.2; figures 3–4 captions. No figure axes digitized.

## Query and integrity path

Both `research/equatorial-basin-family-inventory-audit.json` and `research/ocean-current-inventory-expansion-candidates.json` are declared in `almanac/index-sources.json`, bringing the lossless checked corpus from 63 to 65 sources. They can be queried by document address and JSON pointer through the Rust index store. Existing atlas receipts supply the expanded proposal inventory through WASM. The main snapshot remains 38 collections and 240 objects.

Example index query:

```json
{"document":"research/equatorial-basin-family-inventory-audit.json","pointer":"/proposed_members","limit":10}
```

Protocol validation rejects stale audit inputs, unresolved parent/source references, mismatched worklist membership, duplicate identities, measured dimensions on naming proposals, rank admission and annual-geometry claims from the naming calendar. Negative tests exercise these boundaries. Source naming itself does not establish a current axis, layer or measured extent.

## Reproduce

```powershell
python analysis/check_current_measurement_protocol.py
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python -m pytest analysis -q
python analysis/test_reference_route_atlas_browser.py
python analysis/test_atlas_monthly_section_browser.py
python analysis/test_rust_index_store_browser.py
python analysis/test_rust_index_page_browser.py
python analysis/test_motion_dashboard_browser.py
```

Browser checks reuse a checkout server on port 8788. On Windows, set `OSW_TEST_BROWSER` to the installed Chrome executable. The full required remote gate remains the 47-check browser runner plus both protected CI contexts.

## Admission sequence

1. Review qualified identities, aliases and scope against primary regional studies.
2. Declare layer, temporal support, branches and upstream/downstream endpoint gates.
3. Recover source-supported geometry and explicit scenario choices under M01–M13.
4. Review width and seasonal geometry independently; keep unsupported values missing.
5. Integrate admitted identities through taxonomy, source ledgers, release, query objects, map geometry and state joins in one reviewed revision.

No family length is formed by summing basin members or branches. Existing ranked lengths, width records and measured geometry remain the basis for scientific claims.

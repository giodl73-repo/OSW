# Antilles published cruise-span extension

Continue branch `codex/current-measurement-gaps` and draft PR #83. This extends the established Atlantic cruise-section extraction rules to publisher Table 2 rows 51-53; it does not alter the original v1/v2 receipts or earlier measurements.

## Scope decision and source conflicts

The initial Atlantic batch explicitly held these rows out because section 3.1.7 names Cape Hatteras while Tables 1/2 identify A05 and the Antilles Current. Use the publisher's unambiguous table identity, supported by three independently archived A05 cruise summaries. Preserve the incompatible prose location as an unresolved source wording conflict; do not silently correct the article, geocode Cape Hatteras or claim author confirmation. The table's nominal 24.5 N label is not the latitude of its western boundary stations. Their tracks may deviate substantially.

Transcribe the original XLSX distances: 125 km (row 51), 38 km (row 52), 39 km (row 53). The prose rounds the last two to approximately 38 km; retain this discrepancy and prefer the exact table cell. Values and source context were viewed before this declaration. No blinded analysis or preregistration is claimed.

## Required evidence and operator

1. Verify the unchanged original publisher workbook byte counts and SHA256; retain all source cells, row numbers, station-range labels, longitude limits, density-layer indices and reported depth extent.
2. Join rows 51/52/53 to Table 1 rows 6/12/18 and cruises 29HE19920714/74DI20040404/29AH20110128, respectively. Retain the whole-section windows 1992-07-20 to1992-08-14, 2004-04-07 to2004-05-09 and 2011-01-28 to2011-03-11. Decade groups are not temporal means.
3. Verify the existing CCHDO acquisition receipt and three raw summaries. Parse all events using the unchanged, pinned station-context parser. Retain all in-window hydrographic cast positions as unconnected sampling context. Report actual latitude support and archive cruise aliases; never assign publisher model indices to archive station numbers by row order or rounded longitude.
4. Preserve the publisher's transport-diagnosed section-span definition from section 2.3: horizontal station limits selected by the accumulated transport slope, with density-layer flow direction setting vertical limits. Do not substitute a velocity half-peak operator, a transport-array span or a surface-current envelope.
5. Original published distances are scalars; do not recompute from nominal 24.5 N or the two longitudes. No endpoint coordinate pairs, mapped edges, polygons, state intersection, physical axis or current-wide width follow from these rows.
6. Keep width error and ranges null; transport uncertainty is not width uncertainty. The three cruises do not establish annual extrema, seasonal cycles, a trend or a continuous time series. Whole-current representativeness, full-width inference, ranking and seasonal playback remain false.
7. Retain the licensed publisher article and receipt; visually check Table 2 and section 3.1.7 against the original source. This is source extraction with explicitly quarantined geographic wording, not correction of the publication or independent scientific admission.

## Delivery and verification

Use a separate Antilles extraction receipt so all 32 prior Atlantic spans and all 150 prior width rows remain unchanged by value. Add three scoped transport-selected spans for Antilles through the existing inventory, Rust/WASM query, card and independent cruise-bar presentation. Expose exact source records and the location/rounding conflicts beside them. No new page or PR. Verify source reconstruction, scope/mutation rejection, preservation, numeric/bar parity, source navigation and keyboard/mobile behavior before claiming delivery. The current NECC gate remains pinned to its own earlier commit.

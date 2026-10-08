# Atlantic cruise-section span extraction v1

Effective 2026-10-07. Supplements the required identity, source, layer, time,
boundary and comparability rules in the current width measurement protocol.

## Definition

`inverse_hydrographic_section_span` stores the distance reported in Caínzos
et al. (2023), Table 2 column D. The horizontal limits are station pairs
selected by consistent slope of accumulated eastward horizontal mass transport.
The vertical limits retain the integrated flow direction (Section 2.3).
This is a transport-diagnosed cruise-section span. It is not a fixed velocity
threshold, instantaneous envelope, length along the current or array coverage.

## Reproducibility and support

Archive the original publisher Tables 1 and 2 under their CC BY 4.0 license,
with URLs, byte counts, SHA-256 hashes and retrieval date. Retain all first-sheet
cells and source row numbers. Reject changed workbooks and unexpected formulas.
Transcribe the reported distance without recalculating it from longitude.
Keep station labels, longitude limits, layer indices and reported depth extent.
Reported transport errors do not provide width error bars. Unknown width
uncertainty remains null. No extra precision is created.

Explicitly join each nominal section and inverse-model decade group to the
cruise in Table 1. Preserve its sampling window as a whole-section window.
It is not the exact occupation date of the selected boundary stations.
The decade group is not a decade mean or a seasonal climatology. Cross-year
windows retain both years. Table 1 latitude labels remain alongside Table 2
nominal labels, including subpolar differences and station-index ambiguities.

Density layers have spatially varying depth. The reported depth extent is
context, not a uniform fixed-depth measurement layer. A nominal latitude and
two longitudes do not supply endpoint coordinates: boundary track deviations
are explicitly described in Section 2.1. Leave section geometry null until
actual station positions are recovered. Do not produce a map edge locator,
route buffer, occupied footprint, area or state intersection from these cells.

## Identity and exclusions

Map Falkland (Malvinas) explicitly to `falkland`; preserve upper West Greenland
as the reported branch of `west-greenland`, distinct from its deep flow.
Keep East Greenland distinct from East Greenland Coastal. Gulf Stream remains
distinct from the Gulf Stream System and its recirculation. Do not merge
recirculation rows into a parent-current width. This first batch excludes
already-assessed currents, equatorial-family rows, fronts and new identities.
Keep every exclusion addressable by source row and reason.

Table 2's 2010–2019 24 S rows cannot be safely joined to Table 1's 2018 A095
row labelled 19 S. Hold the Brazil and Benguela rows out pending resolution.
Antilles rows remain outside this batch; their prose location conflict and
previous separate source review are not resolved by assuming an alias.

## Presentation and admission

Show independent spans grouped by current and nominal section, with cruise,
sampling window, depth context and source-row links. Bar lengths may encode
the stored scalar on a labelled kilometre axis, but are not geographic widths.
Do not connect snapshots into interpolated time series, play them as seasons,
aggregate them into annual minima/maxima, rank whole currents or imply equal
layer/section support. Exact source records stay available in Rust/WASM queries.
All whole-current, ranking, annual-extrema, confidence and geographic playback
flags remain false. Independent scientific admission remains a release gate.

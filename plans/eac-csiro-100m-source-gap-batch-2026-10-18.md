# East Australian Current daily source gap batch

Baseline `58afccb4b5a622f63ff0e901c90aa06dd5a95f92`. Continue branch
`codex/current-measurement-gaps` and draft PR83; no separate PR or main merge.

## Source and declared selection

CSIRO DOI [10.25919/sfw7-hc46](https://doi.org/10.25919/sfw7-hc46),
collection69711, metadata version23/data version19, file67390004, CC BY4.0.
The descriptor is Sloyan, Cowley and Chapman (2024), Scientific Data11,10,
[doi:10.1038/s41597-023-02857-x](https://doi.org/10.1038/s41597-023-02857-x).
The source-selection protocol was frozen before decoding the selected fields;
source metadata and methods had already been examined. No blinded claim.

The complete381,438,579byte ZIP and its8,108,045,936byte NetCDF member were
checksummed locally, including ZIP CRC verification. Acquisition first stopped
at the scratch-space guard; resumed extraction compared every existing prefix
byte before appending. Exact hashes and stable provider URLs are in
`research/source-data/eac-csiro-v23-100m/acquisition.json`. Large originals and
temporary signed provider URLs are not redistributed. The retained NPZ has
eight exact100m fields at3770dates and124positions, plus all source coordinate
arrays. Every selected bit was compared with a second original-file read.

## What was filled

The atlas now retains3,739,840 field values: geographic eastward/northward
velocity, temperature, salinity and each supplied uncertainty field. The source
clock runs2012-04-01T12:00Z through2022-07-27T12:00Z in daily steps, across124
calendar months. The final month contains27records. Calendar completeness is
distinct from availability:3141dates have data and629dates remain all missing
(2013-08-27 through2015-05-17). No missing date is filled or dropped.

This is processed, five-day-filtered, SOM-filled and spatially mapped source
output, not3770independent daily observations. All available dates have113
paired velocity positions. Two positions lie on the100m bottom and prescribe
zero velocity and zero velocity uncertainty on all3141available dates. These
6282paired boundary cells do not prove calm water or absence of error.
Provider uncertainty is not assigned an undocumented confidence convention.

The fixed WGS84 source array is173.373km long, with approximately1–2km mapped
spacing and much wider original mooring spacing. This is sampling geometry,
not current length or lateral edges. No source rotation or geographic width
polygon is inferred. Physical width, annual extrema and new observation dates
remain unadmitted.

The source header says remove good flags1/2/5 whereas the descriptor says
retain them; it names nearest-neighbour mapping whereas the descriptor and
collection metadata name natural-neighbour mapping. Both discrepancies remain
explicit. A pinned precursor repository's cleaning predicate excludes3/4,
but that does not authenticate the final SOM/spatial processing build.

## Query and visualization

All3770daily profiles are losslessly queryable through the checked source
index. NaNs become JSON nulls; original bits remain in the NPZ. The23.67MB
profile corpus is not duplicated into the main query packet or WASM binary.
One diagnostic and one series extend the existing45collections. Dashboard
time support counts3141data-bearing frames, retaining629unavailable calendar
records separately. All463old width samples,45diagnostics,27series,155width
rows,81width owners,11lengths,76routes and all observation dates are preserved.

Atlas card, seasons and diagnostic views share month/day controls, four source
field charts with supplied uncertainty, a Rust-projected OSW reference map of
124fixed sampling positions, keyboard position selection and exact-record
links. Missing values break curves; prescribed bottom values have explicit
text context. Optional playback traverses recorded days within a month and
stops at its end. Reduced motion disables playback. Whole-period SVG/PNG
overviews expose source availability and all eight fields.

## Verification and next work

Focused source checks:13Python tests pass;72Rust tests and native atlas smoke
pass. Preservation checks bind111engine inputs,180research inputs,361indexed
documents and8additional source-contract inputs to working bytes. The durable
actual-browser check is registered in the shipped-WASM runner and covers
three views, every source row via pagination, native/Rust projection parity,
missing dates, source bottom context, keyboard/reflow/playback and independent
packet/source-index corruption rejection. Exact execution status belongs in
the PR and local receipts; this plan does not label an active gate passed.

The next scientific step is a separately declared section-width operator,
including vector direction, source grid geometry, uncertainty and boundary
truncation. Source acquisition and animation alone do not close that gap.

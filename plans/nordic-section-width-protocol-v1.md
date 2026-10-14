# Nordic source-defined section widths, version 1

## Identity and admission

Store the source feature name on every row. Norwegian Current has unresolved
naming overlap with Norwegian Coastal Current in the OSW catalog. Fer et al.
(2020) study the Norwegian Atlantic Slope Current. Its new section result belongs
only to proposed identity `norwegian-atlantic-slope`, with no canonical
`current_id`. Do not attach branch dimensions to `norwegian` or
`norwegian-coastal`. Retain the four existing proposed Norwegian branch-width
records unchanged and store the new section result separately.

Kolås and Fer (2018) study the West Spitsbergen Current and its Svalbard branch.
The six measurements already exist under canonical `west-spitsbergen`.
Reuse those records and their existing audit; do not duplicate them under
historical `spitsbergen-atlantic`, whose name equivalence remains unresolved.
Section C precedes the inferred Yermak/Svalbard partition. Do not call all three
threshold-defined sections pure Svalbard-branch widths.

All rows remain editorial source extractions, excluded from whole-current width
ranking, annual extrema, seasonal playback and physical map bands. Exact edge
coordinates and width measurement uncertainties are not extracted.

## Fer et al. 2020

Keep the author-reported 25–30 km range with no chosen midpoint. It is the
20%-of-maximum lateral span of depth-integrated relative geostrophic current
at Gimsøy, referenced to surface pressure. Four occupations are listed:
2016-07-30, 2016-11-19, 2017-03-08 and 2017-06-07. The source does not assign
individual width values to them in the reviewed paragraph. This range is
neither four numerical widths nor an annual minimum/maximum.

The paragraph does not unambiguously specify width integration bounds. Leave
fixed depth bounds unknown. Nearby 50–650 m transport integration and 50–1500 m
comparison, 500–750 m bottom isobaths, 200–600 m mooring mean velocities,
14-month deployment, and 2000–2017 climatology are different supports.
The effective 12.5+7.6=20.1 km transport integration width and its assumed
4 km error are not the diagnosed section-width range or its uncertainty.

## Kolås and Fer 2018

Read Table 2 as section A/tube1, A/tube2, B/tube1, B/tube2, C/tube1,
C/tube2. Six entries represent three sections under two alternative methods,
not six independent occupations. The cruise window is 2015-08-12 through
2015-08-21; exact per-section calendar dates are not extracted. A, B, C take
about 20, 11, 20 hours; section A start to C finish spans five days. The assumed
synopticity is a source assumption, not proven stationarity or annual behavior.

Tube 1 bounds are the first drops of layer-integrated transport density below
AW layer thickness times 0.04 m/s. Preserve threshold cases in order:

| Section | 0.02 m/s | 0.04 m/s primary | 0.08 m/s |
| --- | ---: | ---: | ---: |
| A | 29 km | 24 km | 17 km |
| B | 24 km | 21 km | 11 km |
| C | 37 km | 35 km | 32 km |

The sorted endpoint ranges are operator sensitivity, not measurement errors,
confidence intervals or seasonal extrema. At C the offshore boundary is
substituted from SADCP (x=-11 km for the primary calculation) because roughly
20 km outer LADCP station spacing does not resolve the lateral structure.

Tube 2 conserves approximately 1.3 Sv to within 10%, giving widths 24, 61,
10 km at A, B, C. The 10% tolerance applies to volume flux, not width error.
These are alternate transport-conserving stream-tube spans. Never pool the two
methods into one current-width range or select whichever gives a preferred width.

Vertical support follows the Atlantic Water layer or seabed. Table 1 classifies
AW using practical salinity >34.88 (absolute salinity >35.05 g/kg) and
conservative temperature >=2 C; its observed 45–475 m range is not fixed
stream-tube integration limits. Absolute geostrophic velocity uses a 100 dbar
reference plus detided LADCP reference velocity; 100 dbar is not a fixed 100 m
layer. AOTIM-5 removes barotropic tide. Interpolation to 1 km by 2 m and
10 km by 10 m smoothing do not create native measurement resolution.

## Reproduction and presentation

Retain both exact original PDFs with CC BY 4.0 attribution, acquisition byte
counts and SHA-256. Frozen audits pin records and method metadata. Python and
Rust must reject altered definitions, identities, dates, units, source hashes,
missing rows and promoted annual/full-current values. Charts distinguish the
primary points, threshold sensitivity and alternate transport widths on a
common kilometer scale; filtered queries retain source-method context while
marking matching records. Every row links to its source audit and original.

# Angola Nansen native source sections, version 1

This is an exploratory source-array inventory, declared after inspecting the
provider index, all NetCDF headers and selected thesis methods pages. Velocity
sample values and derived widths have not been inspected. It is not blinded or
an external registration. Freeze this protocol, operator, synthetic tests and
input hashes before reading the actual arrays.

Use the complete unmodified PANGAEA.868683 EAF_Nansen archive. Inventory every
member; parse all eleven named vmADCP sections, retaining the separate CTD file
as an unanalysed source member. Do not substitute the separate Meteor sections
at approximately11S or moorings for these nominal12S Nansen sections.

Require PROFILE and DEPTH dimensions, TIME/LAT/LON vectors on PROFILE, DEPTH on
DEPTH, and U_CUR/V_CUR on PROFILE,DEPTH. Require source units exactly as inspected:
days since1990-01-01 00:00:00, deg north, deg east, m, m/s. Keep the120 and240
native depth grids and profile ordering. Reject changed schemas/units, infinities,
finite declared fill sentinels and masked finite data. Preserve NaNs as explicit
JSON nulls and signed finite binary64 values without rounding. Do not silently
drop profiles or reconcile unequal U/V masks. Retain both component masks and
their disagreement count. Reject unsupported NetCDF variables or attributes
rather than guessing their meaning.

Retain raw numeric TIME. Do not attach UTC or decode a calendar that the provider
does not explicitly specify. Display source time in days from its stated epoch.
Retain every source position; min/max values describe sampling coverage only.
Report finite/missing counts and finite source ranges per variable, dimensions,
member checksums, exact field-file checksums and the entire input-hash receipt.
The native U/V names are retained; no alongshore rotation is applied. No quality
flag field is present in these files; finite does not mean independently QC
approved. No velocity averaging, filtering, interpolation, bathymetric relocation,
model filling, contouring, edge calculation or seasonal inference is permitted.

One gzip JSON field file per section contains all six native arrays and their
metadata. JSON encoding is deterministic, rejects NaN/Infinity, and uses null
only for source NaNs. Gzip uses an empty filename and mtime0. A report inventories
all members and records every section, summary and generated-file hash. Keep a
1GiB free-space start guard. Build refuses an existing report or field directory;
failed products are retained. Check mode rebuilds in memory and compares every
byte; it does not rewrite outputs. Corrections require a new version.

Present a section selector, native U/V heatmap and complete selected-cell values,
profile coordinates, source time and depth. Native profile index is the horizontal
axis, not offshore distance. Missing cells must remain visibly missing, without
smoothing. Retain source depth values including any unusual levels. Show finite
coverage and missing quality metadata alongside the graphic. These are observed
source samples, not current edges, a measured current width, annual extrema, a
geographic route, an OSW state join or a canonical Angola identity admission.
Link exact field files, provider DOI, original archive and methods review.

Keep the11 ship sections distinct from the author's model-assisted transport
reconstruction. The15–90km and30–200m integration box cannot become a75km current
width. Width extraction and identity admission require separate prospective
methods and review after this source inventory is complete.

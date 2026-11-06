# South Indian supplementary native 100m/200m source

Declared before requesting the additional layers. This is a separate source
selection; the completed 15m/1000m source and its scientific reports stay frozen.

## Source and sampling

Use the exact retained HYCOM GOFS3.1 GLBv0.08 expt53.X `/data/2013`
metadata/coordinate originals. Select native depths **100m and200m**, native
indices19 and22, every native latitude from48S to30S and the same three native
meridians around80E. Retain all four packed Int16 variables `water_u`, `water_v`,
`water_temp` and `salinity`, their coordinate maps, receipts and failures.

Keep exactly the earlier363 available daily00Z timestamps. Missing2013 dates
Aug14/Dec25 remain missing. Split each earlier logical time run into consecutive
groups of at most **three** dates before any new request; do not change the
cohort in response to results. Two workers,180-second socket timeout,20,000,000
bytes per response. Resumption reuses only validated matching raw/receipt pairs.
An observation timeout does not authorize a second acquisition process.

Require at least1GiB free before acquisition/compilation. Do not remove source
originals or weaken existing512MiB engine/4GiB full-suite guards.

## Raw monthly products

Use the existing strict four-field coordinate/packing validator. The common
daily mask is the intersection of all four non-fill variables at each native
cell and depth. Count calendar days, require ceil(0.8*days_in_month), sum packed
values in Int64, decode the exact Float32 scale/offset into Float64 and preserve
nulls. No interpolation, latitude smoothing, monthly reweighting or vertical
averaging. Verify the complete expected time vector for each month before means.
Write portable ZIP_STORED/NPY1.0 arrays and unrounded nullable JSON. These raw
products contain **in-situ temperature**, not potential temperature.

## Temperature reference conversion fixed before acquisition

Use GSW-Python **3.6.23** in a separate derived diagnostic, not by rewriting raw
source temperature. At each daily common-valid cell:

1. Compute sea pressure `p_from_z(-depth_m, latitude, 0, 0)` in dbar. Zero dynamic
   height and zero surface geopotential are explicit approximations, not observed
   pressure or sea-surface height. Do not equate metres and decibars.
2. Treat model `salinity` in psu as Practical Salinity; reject negative valid
   values before GSW can clamp them. Calculate `SA_from_SP(SP,p,lon,lat)` in g/kg.
3. Calculate `pt0_from_t(SA,t,p)` at reference sea pressure0dbar. HYCOM metadata
   says in-situ temperature, but does not independently establish ITS-90. Record
   the **ITS-90 input assumption**; no historical temperature-scale equivalence
   is established by this conversion.
4. Convert daily pairs before monthly averaging using the same daily common
   mask and calendar eligibility. A conversion of monthly mean SP/temperature
   is not the mean daily conversion. Preserve any derived nonfinite outcome as
   a failure; do not silently shrink the raw cohort or fill values.

GSW source conventions: [pressure](https://www.teos-10.org/pubs/gsw/html/gsw_p_from_z.html),
[Absolute Salinity](https://www.teos-10.org/pubs/gsw/html/gsw_SA_from_SP.html),
[potential temperature](https://www.teos-10.org/pubs/gsw/html/gsw_pt0_from_t.html).
Pin operator and installed GSW version before new data. Actual original-based
reconstruction and cross-platform exactness remain gates before canonical
derived publication. Never round outputs or relax byte comparison to pass a gate;
use a declared versioned correction if arithmetic proves nonportable.

## Scientific limits and later assessment

Sparrow etal1996 Table1 motivates the missing depths:100m STF temperature/salinity
brackets and200m ARF potential-temperature criteria. A property bracket is not a
velocity boundary, verified front identity or current width. The source's older
historical/model climatologies are not reproduced by a2013 HYCOM comparison.
This two-level supplement still cannot diagnose descent of the vertical salinity
minimum used for SAF identification. It adds no along-current axis support.

No named-current/front association, physical width/length/axis, annual extrema,
seasonal footprint, NASA/state intersection or seasonal playback is admitted by
acquisition or temperature conversion. Any classification/edge calculation needs
its own declared method before calculation, preserving unsuccessful candidates.

## Custody

The public preflight pins the new producer, protocol and conversion operator,
source selection and unchanged earlier source/report dependencies before the
first new field response. Check those pins on acquisition and compilation.
Keep genuine provider responses separately; no synthesized provider files.
Only NAVO-permitted source data may be packaged. Retained copyrighted papers
remain private. Continue the existing branch/draft PR83.

GSW conformance checks use the pinned release's complete MATLAB check cast and
its supplied accuracy bound for Absolute Salinity. The older3.05 web example
differs by about1.5e-5g/kg in the installed3.6.23 release; it is not an exact
reference for this release's salinity atlas. The pt0/pressure web examples pass.
These method-accuracy checks do not replace strict source/product replay gates.

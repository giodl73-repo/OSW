# South Indian missing front-level source batch

Continues the same branch and draft PR83 from655f6ba. Previous goal turn made
verified progress: completed and published the15m/1000m source/profile/query
integration, all23,472 exact native/WASM source cells,72 cases and12 full months.
The present batch targets a concrete remaining vertical-support gap.

The existing Sparrow1996 full-paper review identifies100m/200m property criteria
that the old source cannot test. The separate preflight now freezes those exact
native depths, the earlier363 daily00Z timestamps,326 latitudes and three nearby
80E meridians. All four fields remain paired.135 requests each contain at most
three dates, with two workers,180-second socket timeout and20MB response cap.

The new producer is an explicit derivative of the frozen old producer, with
independent protocol and schemas. It preserves the old parser, metadata checker
and common-mean arithmetic exactly, verified by regression. Complete monthly
time vectors are checked before means. The declaration pins old source products,
original-response archive, both diagnostics and their dependencies. Existing
files and source selections are not revised.

The temperature operator is declared before requesting new values. It uses
GSW3.6.23, negative native depth for pressure, explicit zero dynamic-height and
surface-geopotential approximations, Practical-to-Absolute Salinity conversion
and potential temperature referenced to0dbar. The model temperature's ITS-90
scale is an explicit unverified assumption. Daily conversion precedes averaging;
it does not replace in-situ source temperature. Negative valid salinity is
rejected before GSW could clamp it. Raw common masks and calendar eligibility
survive the derived calculation.

Fourteen focused tests pass, including complete unchanged daily support,
wrong-depth/time/grid/packing rejection, declaration-before-values enforcement,
source-method parity, official pt0/pressure examples, the pinned release's full
Absolute-Salinity check cast, nonlinear daily-before-monthly conversion, velocity
missingness, eligibility and negative-salinity/version rejection. The older
GSW3.05 online salinity example differs by about1.5e-5g/kg from3.6.23; this is
recorded explicitly and the pinned release's independent check data are used.
Method-accuracy tolerances do not replace strict original/product replay gates.

## Commands and remaining gates

```text
python analysis/acquire_south_indian_front_levels.py plan
python analysis/south_indian_front_level_preflight.py declare
python -m pytest -q analysis/test_south_indian_front_levels.py
python analysis/acquire_south_indian_front_levels.py acquire --first-request-only
python analysis/acquire_south_indian_front_levels.py acquire
python analysis/acquire_south_indian_front_levels.py compile
```

Never replace an existing declaration. Reuse only checked matching raw/receipt
pairs. Collect the active process to a terminal state before a retry; an
observation timeout does not establish process termination. Failed URLs and
partial pairs require preservation and inspection. A new partition would need a
separate declaration preserving the complete cohort, not an invented response.

Actual acquisition, complete source assembly, original-based offline replay,
canonical temperature-conversion portability, source publication and native/WASM
presentation remain unverified at this declaration milestone. No runtime build
or browser check is claimed for new source data. The working atlas at655f6ba is
unchanged. Native100/200m fields still cannot establish the SAF vertical salinity
minimum, a verified named-current association, current width/length/axis, annual
extrema or a seasonal footprint. Those gaps remain open.


## First actual source and live acquisition

Declaration/code commitb2a83c7 was pushed to the existing PR before requesting
new field data. The first genuine supplementary response passed the full packed
four-field/map validator:262,312 bytes for the first frozen three dates, native
100m/200m levels and original section grid. It is retained with the original URL,
headers, acquisition time and content checksum. The initial one-request process
is terminalPASS; the separate complete acquisition reuses that validated pair.
The remaining frozen135-request batch is now running with two workers. No
partial source is published or presented as a full-year result.

A source packager now prepares the genuine raw/receipt archive and independently
reconstructs all three raw products before publication. It refuses to overwrite
an existing public source and checks the public destination boundary. Two added
regressions reject a genuine earlier15m/1000m response as the wrong selection
before creating a publication, and reject an out-of-tree destination. The focused
suite is now **16 passed**. Actual full-source replay, derived portability and
new-layer query/visual integration remain pending; passing guard tests does not
establish those results.


## Early cross-platform thermodynamic conformance

While the actual source acquisition remains active, a separate numerical probe
uses synthetic packed fields on the retained coordinate grid. It contains five
synthetic days, all326 latitudes/two depths/three meridians, explicit four-field
missingness, calendar-like eligibility and six exact output arrays. These are
not actual model-field values, observations or admitted current measurements.

`python analysis/check_south_indian_front_temperature_portability.py` checks
all finite numeric bits and the whole portable stored NPZ against a Windows
reference. Only missing NaN payloads use an explicit canonical NumPy sentinel;
no finite value is rounded or approximately accepted. Pressure, Absolute
Salinity, potential temperature, common masks/counts and monthly potential
means must reproduce exactly. The local gate passes. The independent Linux CI
job installs pinned NumPy/GSW/h5py and runs this check without a paper download.
Actual-source conversion/replay still requires its own complete-source gate.

The probe is a separate synthetic conformance artifact and does not modify any
frozen acquisition input, conversion method or previous scientific report.
Linux evidence is pending. A portability failure requires a recorded versioned
correction; it must not be hidden by relaxing the exact gate.

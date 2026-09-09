# M3 native-face section transport

`prepare_oras5_drake_request.py` writes an exact, checksum-receipted dry-run
CDS request by default. Downloading is opt-in and requires the external
`cdsapi` client, configured credentials, licence acceptance, and enough space
for global all-level files.

```powershell
python prepare_oras5_drake_request.py
# Only after configuring CDS access:
python prepare_oras5_drake_request.py --download path/to/oras5-2018.zip
```

`inspect_oras5_section_readiness.py` inventories one or more extracted NetCDF
files. It fails closed unless potential temperature, native U/V velocity,
native U/V coordinates, horizontal face widths, vertical thicknesses, wet
masks, and time are all explicit. Rotated east/north fields may be useful for
diagnostics but are not accepted as native face fluxes, and nominal grid
resolution is never converted silently into face area.

`fetch_oras5_mesh_inventory.py` performs a small metadata-only OPeNDAP request
against the public ICDC ORCA025 `mesh_mask.nc`; it does not download the
reported 650,753,384-byte file. The current 38-variable receipt confirms U/V
horizontal metrics, masks, and coordinates but reports the absence of explicit
`e3u`/`e3v` layer-thickness arrays.
The receipt also records, without yet accepting, the CDFTOOLS 3.0 candidate
that reconstructs face thickness as the minimum of adjacent partial-step
T-cell thicknesses. Acceptance requires an ORAS5-configuration reference and
edge/volume-conservation tests.

`reconstruct_nemo_face_thickness.py` makes that candidate falsifiable on a
synthetic partial-step grid. It reconstructs bottom T cells from `mbathy`,
`e3t_ps`, and `e3t_0`, then emits only interior U/V faces using adjacent
minima. Output shapes shrink by one column for U and one row for V, so there is
no copied terminal edge.

```powershell
python reconstruct_nemo_face_thickness.py `
  --input fixtures/nemo-partial-step-synthetic.json `
  --output ../research/osw-m3-nemo-face-thickness-verification.json
python -m unittest test_reconstruct_nemo_face_thickness.py
```

This is still synthetic method verification, not acceptance of reconstructed
ORAS5 face geometry.

The live path is now implemented by `fetch_oras5_drake_mesh_subset.py`,
`audit_nemo_face_thickness_reconstruction.py`,
`fetch_oras5_drake_state_subset.py`, `derive_oras5_drake_gate.py`, and
`extract_oras5_drake_section.py`. They retrieve a compact native mesh, test the
reconstruction against native masks and depth bounds, retrieve one native
monthly T/U/V state, select a land-bounded U-face gate, and build the explicit
partial-cell section contract.

```powershell
python fetch_oras5_drake_mesh_subset.py
python audit_nemo_face_thickness_reconstruction.py `
  --input ../atlas/data/oras5-drake-mesh.nc `
  --output ../research/osw-m3-oras5-face-thickness-audit.json
python fetch_oras5_drake_state_subset.py --month 201802
python derive_oras5_drake_gate.py
python extract_oras5_drake_section.py
python calculate_section_transport.py `
  --input ../research/osw-m3-oras5-drake-section-input-201802.json `
  --output ../research/osw-m3-oras5-drake-transport-201802.json
```

The February 2018 gate reports 124.29 Sv net eastward. Heat transport must be
quoted with its reference temperature: 2.32 PW at −1.9°C, 1.35 PW at 0°C, and
−1.20 PW at 5°C. It remains one monthly assimilative-reanalysis member and one
open section, not climatology, mass closure, convergence, or Antarctic heat
delivery.

`synthesize_oras5_drake_seasons.py` combines the same gate calculation for
February, May, August, and November without calling four samples an annual
mean. `build_oras5_drake_seasonal_view.py` turns the result into a gate passport
that keeps eastward flow, westward counterflow, net volume, transport-weighted
temperature, and all three heat-reference cases visible.

```powershell
python synthesize_oras5_drake_seasons.py
python build_oras5_drake_seasonal_view.py
python analyze_oras5_drake_gate_sensitivity.py
python build_oras5_drake_method_sensitivity_view.py
python synthesize_oras5_drake_vertical.py
python build_oras5_drake_vertical_view.py
python synthesize_oras5_drake_temperature_classes.py
python build_oras5_drake_temperature_class_view.py
python synthesize_oras5_drake_section_field.py
python build_oras5_drake_section_field_view.py
python build_oras5_drake_transport_field_view.py
```

The method-sensitivity run keeps two questions separate. It shifts the native
land-bounded gate across five columns from 69.125°W to 65.125°W, then holds the
primary gate fixed while comparing arithmetic-mean, west-point, east-point,
and upwind T-to-U collocation. The first changes the four-sample mean volume by
only 0.111 Sv across gates. The second leaves volume invariant but shifts the
0°C-reference mean heat result by up to 0.050 PW. These are bounded method
tests, not observational error bars or a reconstruction of model-native tracer
advection.

The vertical synthesis preserves layerwise positive and negative branches,
then assigns each nominal model-level midpoint to one of five declared depth
strata. The strata conserve the section totals to floating-point roundoff. They
show full-depth volume transport but a shallower 0°C-reference heat signature;
they are not water-mass or overturning classifications.

The temperature-class synthesis repartitions the same wet face cells at 0, 1,
2, 3, and 5°C. It preserves eastward and westward branches and closes both net
volume and 0°C-reference heat back to the section result. The classes are
descriptive thermal populations, never water-mass identities.

The section-field synthesis averages the same four native gate inputs cell by
cell and retains their latitude, nominal layer depths, partial bottom cells,
temperature, and normal velocity. Its SVG uses a declared nonlinear depth scale
and samples motion symbols for legibility. Dots and crosses mean eastward out
of and westward into the north–south slice; they are not along-section arrows.

The same section-field receipt also carries four-sample mean signed volume and
0°C-reference heat contribution for every wet native cell. The matched
transport-field SVG uses an asinh color scale to preserve weak and strong lanes.
Cell sums reproduce the section totals exactly; individual brightness remains
resolution-dependent.

`analyze_oras5_drake_control_box.py` opens M4 by joining two U boundaries and
two V boundaries around one grid-aligned box. It reports every outward volume
and reference-relative heat term, the boundary sum, and the exact
reference-change identity. `build_oras5_drake_control_box_view.py` renders the
four-boundary split and the remaining monthly heat divergence.

```powershell
python analyze_oras5_drake_control_box.py
python build_oras5_drake_control_box_view.py
python analyze_oras5_drake_control_box_sensitivity.py
python build_oras5_drake_control_box_sensitivity_view.py
```

The volume boundary sum is near zero, but the calculation still lacks matched
storage tendency, surface forcing, diffusion/mixing, and model-native tracer
advection. Its heat residual is advective boundary divergence—not accumulation.
The nested sensitivity run changes eastward and northward extent separately;
all boxes remain volume-balanced while their heat residuals move substantially.

`fetch_oras5_drake_t_metrics.py` retrieves native `e1t` and `e2t` into a
separate checksummed companion, leaving the accepted face-geometry file and its
hash unchanged. `analyze_oras5_drake_storage_probe.py` combines those areas with
partial T-cell thickness and four monthly temperature states. The resulting
three endpoint tendencies are reference-invariant but sparse; they are compared
with endpoint-average advection only as a diagnostic.

```powershell
python fetch_oras5_drake_t_metrics.py
python analyze_oras5_drake_storage_probe.py
python build_oras5_drake_storage_probe_view.py
```

The unclosed remainder is not assigned to a process. Proper closure requires
time-integrated native tracer tendencies, surface/ice fluxes, diffusion, mixing,
and every boundary term over identical intervals.

`fetch_oras5_drake_budget_state.py` retrieves only the compact native T/U/V
windows required by the primary control box. Twelve 2018 files total roughly
9.7 MB. `analyze_oras5_drake_monthly_budget.py` builds eleven adjacent-month
storage/advection comparisons and verifies four exact anchors against the prior
full-subset calculations.

```powershell
1..12 | ForEach-Object {
  python fetch_oras5_drake_budget_state.py --month ("2018{0:D2}" -f $_)
}
python analyze_oras5_drake_monthly_budget.py
python build_oras5_drake_monthly_budget_view.py
```

`fetch_oras5_drake_surface_heat.py` retrieves all twelve native ORCA025
`sohefldo` monthly means over that same 86×16 T-cell footprint.
`analyze_oras5_drake_surface_budget.py` area-integrates the positive-downward
flux and subtracts it from the storage-plus-outward-advection remainder.

```powershell
python fetch_oras5_drake_surface_heat.py
python analyze_oras5_drake_surface_budget.py
python build_oras5_drake_surface_budget_view.py
```

The 334-day mean surface input is +0.0195 PW: 31% of the pre-surface gap. The
remaining +0.0427 PW is not assigned to a process. ORAS5 `sohefldo` is a
model/reanalysis forcing term with surface-restoring context, not direct
observation or a model-native tracer-budget diagnostic.

```powershell
python inspect_oras5_section_readiness.py path/to/*.nc `
  --output ../research/osw-m3-oras5-readiness-2018.json
python fetch_oras5_mesh_inventory.py `
  --output ../research/osw-m3-oras5-mesh-inventory.json
```

Only a passing and then manually validated intake may be converted to the
flattened `[levels, segments]` contract consumed by
`calculate_section_transport.py`. That kernel reports positive, negative, and
net volume; transport-weighted branch temperature; reference-relative heat;
the exact reference-change identity; and layer contributions. One open section
always leaves mass closure unevaluated.

```powershell
python calculate_section_transport.py `
  --input fixtures/section-transport-balanced-synthetic.json `
  --output ../research/osw-m3-section-kernel-verification.json
python -m unittest test_prepare_oras5_drake_request.py `
  test_oras5_section_readiness.py test_section_transport.py
```

The committed section result is explicitly synthetic. It verifies the
calculation pathway and does not estimate Drake Passage heat transport.

# Heat-scale ledger

`heat_zone_ledger.py` converts either a water-volume temperature excess or a
sustained heat-transport rate into integrated energy and an ideal latent-melt
equivalent.

The result is an upper-bound unit conversion. It is not a heat-delivery model,
ice-sheet response model, or sea-level forecast.

```powershell
python heat_zone_ledger.py --volume-km3 1 --temperature-excess-c 1
python heat_zone_ledger.py --power-tw 1 --duration-days 365.25
python -m unittest test_heat_zone_ledger.py
```

Defaults are documented in `--help`; calculations use the Python standard
library only.

## OISST snapshot pipeline

`fetch_oisst_snapshot.py` retrieves a fixed NOAA/NCEI subset, validates its
rectangular grid, quantizes SST, anomaly, or estimated analysis error to integer
hundredths of a degree Celsius, and writes a compact browser artifact with query
and checksum provenance. The ERDDAP/CSV backend uses the standard library. The
NCSS/NetCDF backend used by the committed artifacts requires
`requirements-observations.txt`.

```powershell
python -m pip install -r ../requirements-observations.txt
python fetch_oisst_snapshot.py --backend ncss --date 2026-08-01 --stride 8 `
  --retrieved-at 2026-08-21T14:00:00Z `
  --output ../atlas/data/oisst-2026-08-01.js

python fetch_oisst_snapshot.py --backend ncss --variable anom `
  --date 2026-08-01 --stride 8 `
  --retrieved-at 2026-08-21T14:00:00Z `
  --output ../atlas/data/oisst-anomaly-2026-08-01.js

python fetch_oisst_snapshot.py --backend ncss --variable err `
  --date 2026-08-01 --stride 8 `
  --retrieved-at 2026-08-21T14:00:00Z `
  --output ../atlas/data/oisst-error-2026-08-01.js
```

## RG Argo pressure-layer pipeline

`fetch_argo_snapshot.py` packages one exact pressure level from a fixed monthly
Scripps RG Argo extension. Atlas 10 commits July 2026 potential-temperature
anomalies at 10, 300, 700, and 1000 dbar, each sampled from the native 1-degree
grid at a 2-degree display stride. Every artifact preserves the same compressed
source checksum, product version, baseline, grid extent, and missing values.

```powershell
foreach ($pressure in 10, 300, 700, 1000) {
  python fetch_argo_snapshot.py `
    --month 2026-07 `
    --pressure-dbar $pressure `
    --stride 2 `
    --retrieved-at 2026-08-28T19:02:31Z `
    --output "../atlas/data/argo-temperature-anomaly-${pressure}dbar-2026-07.js"
}

python -m unittest test_argo_snapshot.py
```

These are objectively mapped anomalies at four pressure surfaces. They are not
raw-float coverage, absolute temperature, water-column heat content, or transport.
The product grid ends at 64.5°S, so it cannot diagnose Antarctic shelf or
ice-cavity heat delivery.

## OSCAR surface-motion pipelines

`fetch_oscar_snapshot.py` is the production M1 ingestion contract for NASA
PO.DAAC OSCAR Final v2.0. It discovers the exact daily granule through CMR,
packages jointly masked `u` and `v` components as signed integer millimetres
per second, and records the collection, DOI, granule URL, retrieval time, and
source checksum. Protected payload access requires a temporary
`EARTHDATA_TOKEN` or a local NetCDF retrieved with NASA's official PO.DAAC
subscriber; credentials are never written to the artifact.

```powershell
$env:EARTHDATA_TOKEN = "<temporary token>"
python fetch_oscar_snapshot.py --date 2025-01-01 --stride 8 `
  --output ../atlas/data/oscar-currents-2025-01-01.js
Remove-Item Env:EARTHDATA_TOKEN
```

`fetch_oscar_historical_pilot.py` uses NOAA's public mirror of the older
third-degree, 5-day OSCAR archive to make the visual grammar test reproducible
without authentication. The committed pilot is a single 2018-11-16 field and
is prominently distinguished from OSCAR v2.0.

```powershell
python fetch_oscar_historical_pilot.py --date 2018-11-16 --stride 16 `
  --output ../atlas/data/oscar-historical-2018-11-16.js

python build_oscar_motion_view.py `
  --data ../atlas/data/oscar-historical-2018-11-16.js `
  --land-geojson path/to/ne_110m_land.geojson `
  --output ../figures/osw-motion-surface-historical-pilot.svg

python fetch_oscar_persistence_pilot.py `
  --start 2018-01-01 --stop 2018-11-21 `
  --time-stride 6 --space-stride 16 `
  --output ../atlas/data/oscar-persistence-2018.js

python build_oscar_persistence_view.py `
  --data ../atlas/data/oscar-persistence-2018.js `
  --land-geojson path/to/ne_110m_land.geojson `
  --output ../figures/osw-motion-persistence-2018.svg

python fetch_oscar_seasonal_pilot.py `
  --start 2017-12-01 --stop 2018-11-21 --space-stride 20 `
  --output ../atlas/data/oscar-seasons-2018.js

python fetch_oscar_timeseries_pilot.py `
  --start 2017-12-01 --stop 2018-11-21 --space-stride 20 `
  --output ../atlas/data/oscar-timeseries-2018.js

python fetch_oscar_timeseries_pilot.py `
  --start 2017-12-01 --stop 2018-11-21 --space-stride 2 `
  --north -45 --south -70 --west 280 --east 320 `
  --output ../atlas/data/oscar-timeseries-drake-2018.js

python fetch_oscar_timeseries_pilot.py `
  --start 2017-12-01 --stop 2018-11-21 --space-stride 1 `
  --north -45 --south -70 --west 280 --east 320 `
  --output ../atlas/data/oscar-timeseries-drake-native-2018.js

python build_oscar_seasonal_view.py `
  --data ../atlas/data/oscar-seasons-2018.js `
  --land-geojson path/to/ne_110m_land.geojson `
  --output ../figures/osw-motion-seasons-2018.svg

python derive_oscar_seasonal_agreement.py `
  --input ../atlas/data/oscar-seasons-2018.js `
  --output ../atlas/data/oscar-seasonal-agreement-2018.js

python build_oscar_seasonal_agreement_view.py `
  --data ../atlas/data/oscar-seasonal-agreement-2018.js `
  --land-geojson path/to/ne_110m_land.geojson `
  --output ../figures/osw-motion-seasonal-agreement-2018.svg

python audit_regions_against_motion.py `
  --input ../atlas/data/oscar-seasons-2018.js `
  --json-output ../research/osw-motion-region-audit-2018.json `
  --boundary-csv-output ../research/osw-motion-boundary-audit-2018.csv `
  --region-csv-output ../research/osw-motion-region-audit-2018.csv

python build_motion_region_audit_view.py `
  --seasonal-data ../atlas/data/oscar-seasons-2018.js `
  --audit ../research/osw-motion-region-audit-2018.json `
  --land-geojson path/to/ne_110m_land.geojson `
  --output ../figures/osw-motion-region-audit-2018.svg

python build_motion_border_orientation_view.py `
  --seasonal-data ../atlas/data/oscar-seasons-2018.js `
  --audit ../research/osw-motion-region-audit-2018.json `
  --land-geojson path/to/ne_110m_land.geojson `
  --output ../figures/osw-motion-border-orientation-2018.svg

python analyze_motion_partition_sensitivity.py `
  --input ../atlas/data/oscar-seasons-2018.js `
  --output ../research/osw-motion-partition-sensitivity-2018.json `
  --csv-output ../research/osw-motion-partition-sensitivity-2018.csv

python build_motion_partition_sensitivity_view.py `
  --data ../research/osw-motion-partition-sensitivity-2018.json `
  --land-geojson path/to/ne_110m_land.geojson `
  --output ../figures/osw-motion-partition-sensitivity-2018.svg

python analyze_motion_partition_robustness.py `
  --input ../atlas/data/oscar-seasons-2018.js `
  --output ../research/osw-motion-partition-robustness-2018.json `
  --csv-output ../research/osw-motion-partition-robustness-2018.csv

python build_motion_partition_robustness_view.py `
  --data ../research/osw-motion-partition-robustness-2018.json `
  --land-geojson path/to/ne_110m_land.geojson `
  --output ../figures/osw-motion-partition-robustness-2018.svg

python derive_motion_region_passports.py `
  --input ../research/osw-motion-region-audit-2018.json `
  --output ../research/osw-motion-region-passports-2018.json `
  --csv-output ../research/osw-motion-region-passports-2018.csv

python build_motion_region_passports_view.py `
  --data ../research/osw-motion-region-passports-2018.json `
  --output ../figures/osw-motion-region-passports-2018.svg

python audit_region_membership_motion.py `
  --input ../atlas/data/oscar-seasons-2018.js `
  --output ../research/osw-motion-region-membership-2018.json `
  --region-csv-output ../research/osw-motion-region-membership-2018.csv `
  --state-csv-output ../research/osw-motion-state-passports-2018.csv

python build_region_membership_motion_view.py `
  --membership ../research/osw-motion-region-membership-2018.json `
  --passports ../research/osw-motion-region-passports-2018.json `
  --output ../figures/osw-motion-region-membership-2018.svg

python build_region_membership_seams_view.py `
  --seasonal-data ../atlas/data/oscar-seasons-2018.js `
  --membership ../research/osw-motion-region-membership-2018.json `
  --land-geojson path/to/ne_110m_land.geojson `
  --output ../figures/osw-motion-region-membership-seams-2018.svg

python build_region_membership_seasons_view.py `
  --seasonal-data ../atlas/data/oscar-seasons-2018.js `
  --membership ../research/osw-motion-region-membership-2018.json `
  --land-geojson path/to/ne_110m_land.geojson `
  --output ../figures/osw-motion-region-membership-seasons-2018.svg

python simulate_oscar_pathways.py `
  --input ../atlas/data/oscar-timeseries-drake-native-2018.js `
  --output ../research/osw-m2-drake-pathways-2018.json

python simulate_oscar_pathways.py --timestep-hours 3 `
  --output ../research/osw-m2-drake-pathways-2018-step3.json
python simulate_oscar_pathways.py --timestep-hours 12 `
  --output ../research/osw-m2-drake-pathways-2018-step12.json
python analyze_pathway_timestep_sensitivity.py

python simulate_oscar_pathways.py `
  --input ../atlas/data/oscar-timeseries-drake-2018.js `
  --output ../research/osw-m2-drake-pathways-coarse-2018.json
python analyze_pathway_grid_sensitivity.py

python analyze_pathway_release_sensitivity.py
python analyze_pathway_release_time_sensitivity.py
python synthesize_pathway_release_sensitivities.py

python build_drake_pathways_view.py `
  --data ../research/osw-m2-drake-pathways-2018.json `
  --land-geojson path/to/ne_110m_land.geojson `
  --output ../figures/osw-motion-drake-pathways-2018.svg

python build_drake_release_sensitivity_view.py `
  --primary ../research/osw-m2-drake-pathways-2018.json `
  --sensitivity ../research/osw-m2-drake-release-sensitivity-2018.json `
  --land-geojson path/to/ne_110m_land.geojson `
  --output ../figures/osw-motion-drake-release-sensitivity-2018.svg

python build_drake_release_sensitivity_view.py `
  --primary ../research/osw-m2-drake-pathways-2018.json `
  --sensitivity ../research/osw-m2-drake-release-time-sensitivity-2018.json `
  --land-geojson path/to/ne_110m_land.geojson `
  --output ../figures/osw-motion-drake-release-time-sensitivity-2018.svg

python build_drake_corridor_passport_view.py `
  --primary ../research/osw-m2-drake-pathways-2018.json `
  --paired ../research/osw-m2-drake-release-sensitivity-pair-2018.json `
  --land-geojson path/to/ne_110m_land.geojson `
  --output ../figures/osw-motion-drake-corridor-passport-2018.svg
```

The resulting plate turns zoning off. Direction and speed are primary; land
is quiet context. It is a historical surface-velocity pilot, not a parcel
simulation, full-depth current field, or heat-transport calculation.

The persistence pilot uses eleven roughly monthly samples. Its declared ratio
is `magnitude(mean velocity) / mean speed`: zero indicates directional
cancellation and one indicates alignment. It is useful for separating a
single-day pattern from sampled persistence, but it is not a climatology,
Lagrangian coherent structure, or region boundary.

The four-panel seasonal pilot uses all 71 five-day fields returned between
December 2017 and November 2018, grouped into meteorological seasons. It can
show reversals hidden by an annual mean, but one historical year cannot define
a seasonal climatology.

The derived holds/turns plate computes cross-season unit-direction agreement
and the largest pairwise seasonal turning angle. Thresholded aligned/turning
candidate counts are declared interpretive bins; the continuous diagnostics
remain primary and do not define regions.

The boundary audit then restores only the frozen 22-region overlay. Its
cut-through score multiplies mean flow along the flat nearest-seed border
normal by rescaled directional similarity across neighboring cells; a separate
table measures internal directional similarity. Solid lines have at least eight
neighbor pairs, dashed lines have three to seven, and sparse borders remain
quiet. These are support classes, not statistical confidence: neighboring
samples are spatially dependent. The result is not a boundary-normal
calculation on validated oceanographic geometry, a merge instruction, or a
zoning revision. The JSON and boundary CSV also carry DJF, MAM, JJA, and SON
scores plus their descriptive floor, ceiling, and range; the figure renders
the four values as a compact seasonal fingerprint.

The orientation plate uses the same samples and geometry but compares the
tangential and normal components directly. Its signed margin is
`cut-through score − along-border score`; this exposes flow-following borders
without mislabeling them as impermeable barriers.

The partition-sensitivity study discards OSW zoning entirely and joins
four-neighbor cells by mean seasonal directional similarity across ten
thresholds. It reports all connected components, several minimum-size counts,
largest-component dominance, and retained coverage. Component colors are local
to each panel and do not imply identity across thresholds.

The robustness study compares four-neighbor and eight-neighbor graphs plus four
leave-one-season-out cases. It intentionally keeps the component-size rule and
threshold sweep fixed. The leave-one-out cases share most of their source data
and are sensitivity checks, not independent replicates.

The passport derivation aggregates incident boundary support into each frozen
region while preserving the independent interior and seasonal diagnostics. It
does not calculate a composite rank. Regions without a screened incident
border retain null border fields rather than false zeros.

The membership audit aggregates each province's supported coarse cells into
four seasonal mean vectors. It compares every supported member pair within a
region and reports the mean, minimum, and worst pair. These are unweighted
display-grid summaries; pairs need not be geographically adjacent.

The same membership artifact also records sampled four-neighbor state
adjacencies. The seam view matches those pairs to exact owned edges in the
nearest-seed construction and masks colored diagnostic lines beneath the pinned
Natural Earth land geometry. One or two neighbor pairs remain dashed.

The seasonal seam plate uses the same sampled contacts and owned edges but
colors them from separate DJF, MAM, JJA, and SON similarity fields. Its
same-class count is descriptive; the four seasons share one historical year
and are not independent persistence estimates.

The time-series package preserves all 71 source fields on the same fixed
25-by-54 grid for the M2 pathway laboratory. Every frame has an ISO timestamp,
joint finite-component mask, quantized zonal and meridional velocities, and
valid-cell count. The artifact records both the downloaded-byte checksum and a
canonical checksum of the packaged frames. It deliberately contains no
interpolation, parcel releases, trajectories, temperature, or heat transport.
The Drake/Scotia packages keep the same dates over 45–70°S, 80–40°W at both
roughly two-thirds and one-third of a degree. The native one-third-degree field
is the primary method domain; the coarsened field is retained as a spatial
sensitivity case.

The first M2 run declares that policy rather than hiding it. Four seasonal
release dates each seed ten equal-count wet-interior points on a schematic Drake section;
a deterministic RK4 solver integrates for 30 days with a six-hour step, linear
time interpolation, strict four-wet-corner bilinear space interpolation, no
diffusion, and termination at an invalid stencil or domain edge. Thirty-five
of 40 tracks complete. Track density and completion are not volume, residence,
coherence, temperature advection, or heat transport.

The 3-, 6-, and 12-hour integrations retain the same 35 completions and five
losses. Across the 35 commonly completed tracks, the largest endpoint
separation from the 3-hour reference is 1.40 km. Near-mask loss timing spans at
most six hours across steps, but termination time is still not interpreted as
beaching time or coastal residence.

Spatial sampling is the stronger sensitivity. Native one-third-degree and
coarsened two-thirds-degree runs both report 35/40 completions, but two track
identities switch status. Among 34 commonly completed tracks, endpoint
separation has a 79.01 km median and 310.68 km maximum. The matching aggregate
count therefore does not validate the coarsened path shapes.

Release-position sensitivity then replaces every central point with a
deterministic 3×3 neighborhood offset by ±15 km along and across the section.
Of 360 trials, 321 complete. Thirty-three neighborhoods complete all nine,
five are mixed, and two lose all nine. The median of the central-complete
neighborhood median endpoint shifts is 58.46 km; the largest individual shift
is 507.63 km. The result supports a broad corridor while rejecting any one
track as uniquely representative. The equal-count grid is not probabilistic.

The matched clock experiment starts each central release at five deterministic
times spanning −5 to +5 days. Of 200 tracks, 176 complete; 34 windows complete
all five, two are mixed, and four lose all five. The typical central-complete
window median endpoint shift is 41.60 km and the maximum is 548.23 km. The two
sensitivity studies jointly support a broad corridor, not one exact path.

The paired passport refuses a composite confidence score. Every seasonal row
has eight of ten seeds full under both the position and clock tests. Across all
40 central releases, 32 are full/full, two are lost/lost, and six are mixed or
one-sided. This locates the robust interior and fragile margins without
turning completion support into probability, exchange, or heat delivery.

`analyze_arctic_entrances_motion.py` opens the next M2 area with two matched
native-resolution OSCAR substrates. It screens normal surface velocity across
Fram Strait and the Barents Sea Opening, splitting Fram into western export,
central transition, and eastern inflow lanes. `build_arctic_entrances_motion_view.py`
renders the pair in local Lambert equal-area panels.

```powershell
python fetch_oscar_timeseries_pilot.py --space-stride 1 --north 80 --south 72 --west 340 --east 379.6666667 --output ../atlas/data/oscar-timeseries-fram-native-2018.js
python fetch_oscar_timeseries_pilot.py --space-stride 1 --north 80 --south 68 --west 20 --east 60 --output ../atlas/data/oscar-timeseries-barents-native-2018.js
python analyze_arctic_entrances_motion.py
python build_arctic_entrances_motion_view.py
```

The result is intentionally not a transport calculation. It lacks section
area, depth, temperature, salinity, and Atlantic Water classification.

`prepare_oras5_arctic_entrances_request.py` freezes the next M3 contract before
retrieval. It declares both native domains, four seasonal months, T/U/V plus
salinity, candidate geographic sections, required branch decompositions, and
the geometry/collocation audits that must pass before transport.

```powershell
python prepare_oras5_arctic_entrances_request.py
python fetch_oras5_drake_mesh_subset.py --context arctic-entrances --west -25 --east 50 --south 66 --north 84 --output ../atlas/data/oras5-arctic-entrances-mesh.nc --receipt ../research/osw-m3-oras5-arctic-entrances-mesh.json
python derive_oras5_arctic_gate_readiness.py
python build_oras5_arctic_gate_readiness_view.py
```

The native-mesh audit finds an asymmetric geometry result before any state
download. Fram Strait aligns with a 60-face, surface-land-bounded native V row.
At the Barents Sea Opening, the U column whose mean longitude lies closest to
20°E bends from 15.40°E to 25.88°E over the declared latitude interval and
remains wet past both endpoints. It is rejected as a gate. The T mask adds a
second constraint: the approximate Bear Island target is wet at ORCA025, with
the nearest dry T cell more than 200 km away. OSW therefore forks the contract:
a virtual-endpoint mixed U/V Fugløya–Bear proxy for observational comparison,
or a distinct land-bounded Norway–Svalbard gate for model budgets. They cannot
share a name or interpretation. This is geometry readiness—not velocity,
volume, heat, or Arctic delivery.

`derive_oras5_barents_section_bakeoff.py` then constructs both honest answers
on the native C-grid graph. Each path consists solely of wet U/V faces and is
audited for a connected F-corner chain, unique faces, degree-two internal
corners, and zero corner duplication.

```powershell
python derive_oras5_barents_section_bakeoff.py
python build_oras5_barents_section_bakeoff_view.py
```

The Fugløya–Bear observational proxy uses 43 faces (23 U + 20 V) and two
virtual wet endpoints. The Norway–Svalbard model closure uses 73 faces
(36 U + 37 V), reaches modeled coast at both ends, and terminates about 243 km
from the approximate Bear target. Both are topologically valid; they do not
measure the same domain. Face signs are stored consistently toward the Barents
side for future transport, but no state field is used here.

`analyze_oras5_barents_section_sensitivity.py` crosses nine declared endpoint
intents with 10, 20, and 40 km line-departure penalties for both section
meanings. `build_oras5_barents_section_sensitivity_view.py` renders the 54-case
matrix.

```powershell
python analyze_oras5_barents_section_sensitivity.py
python build_oras5_barents_section_sensitivity_view.py
```

All nine endpoint cases are invariant across the three cost scales. Endpoint
placement produces nine proxy paths (39–49 faces) and six closure paths
(73–74 faces), however; maximum face-set replacement from baseline is 100% and
81% respectively. Future transport must carry endpoint sensitivity. The 20 km
penalty is retained solely as a reproducible construction default.

The full-depth geometry stage first reruns the adjacent-minimum reconstruction
against the complete Arctic mesh, then selects only the three accepted surface
paths and audits their masks, widths, partial steps, wet areas, and reference-
level depth-bin closure.

```powershell
python audit_nemo_face_thickness_reconstruction.py --input ../atlas/data/oras5-arctic-entrances-mesh.nc --output ../research/osw-m3-oras5-arctic-face-thickness-audit.json
python audit_oras5_arctic_section_geometry.py
python build_oras5_arctic_section_geometry_view.py
```

The mesh-wide reconstruction has zero U/V mask mismatches and a maximum column-
depth residual of 7.1×10⁻¹⁵ m. Fram has 814 km² of wet section area and reaches
2,577 m; its below-700-m fraction is 60%. The 161 km² Fugløya–Bear proxy and
224 km² Norway–Svalbard closure reach 444 m and 432 m, with no area below
700 m in these reference-level bins. This is an internal geometry-consistency
pass, not independent validation of the precise ORAS5 production thickness.

The first state-field pilot retrieves February 2018 potential temperature,
practical salinity, native U velocity, and native V velocity across the same
75 × 200 × 240 mesh window. It extracts all three section definitions without
regular-grid interpolation, applies every stored native-face normal sign, and
collocates T/S from the two adjacent T cells.

```powershell
python fetch_oras5_arctic_state_subset.py --month 201802
python extract_oras5_arctic_sections.py
python calculate_section_transport.py --input ../research/osw-m3-oras5-arctic-fram-section-input-201802.json --output ../research/osw-m3-oras5-arctic-fram-transport-201802.json --reference-temperature -1.9 --reference-temperature 0 --reference-temperature 2
python analyze_oras5_arctic_transport_pilot.py
python build_oras5_arctic_transport_pilot_view.py
```

Fram contains +6.21 Sv northward and −6.66 Sv southward branches, with a
−0.45 Sv net. The Barents proxy and closure yield +3.23 and +3.64 Sv net; the
0.41 Sv gap belongs to their different endpoints and domains. Their 0°C-
reference advective heat signals are +52, +73, and +81 TW respectively.
Negative-side, positive-side, mean, and upwind tracer collocation leave volume
unchanged and move heat by no more than 1.71%. Joint T/S Atlantic Water classes
follow a published comparison convention, not a universal water-mass border.
This one month is not seasonality, climatology, convergence, or Arctic heat
delivery.

May, August, and November use the identical state, extraction, and transport
contracts. `synthesize_oras5_arctic_seasons.py` verifies all 12 transport-input
hashes and builds the four-snapshot comparison.

```powershell
python synthesize_oras5_arctic_seasons.py
python build_oras5_arctic_seasons_view.py
```

Fram remains net southward in all four samples (−0.45 to −2.05 Sv) while its
0°C-reference heat remains positive (+24 to +64 TW). The Barents proxy remains
eastward at +2.77 to +3.80 Sv and the closure at +3.10 to +4.03 Sv. The closure
exceeds the proxy in every sampled month by 0.23–0.49 Sv. These sign-persistence
checks establish a four-snapshot pattern, not a time-weighted annual mean or
interannual result.

`prepare_nordic_seas_budget.py` turns those open gateways into an M4
control-volume contract. The first endpoint audit rejects the existing Arctic
mesh for this job because its rotated southern edge does not reach the Faroes
and Scotland. A new 75 × 256 × 296 native mesh spans every candidate opening.
The first Denmark intent also moves from open water to represented Greenland
coast.

```powershell
python prepare_nordic_seas_budget.py
python derive_oras5_nordic_southern_sections.py
python derive_oras5_nordic_control_volume.py
python audit_oras5_nordic_section_geometry.py
python build_oras5_nordic_section_geometry_view.py
python fetch_oras5_drake_t_metrics.py --context nordic-seas --mesh-receipt ../research/osw-m4-oras5-nordic-seas-mesh.json --output ../atlas/data/oras5-nordic-t-metrics.nc --receipt ../research/osw-m4-oras5-nordic-t-metrics.json
python fetch_oras5_nordic_surface_heat.py
python analyze_oras5_nordic_surface_heat.py
python build_oras5_nordic_surface_heat_view.py
1..12 | ForEach-Object { $month = '2018{0:D2}' -f $_; python fetch_oras5_nordic_budget_state.py --month $month }
python analyze_oras5_nordic_partial_budget.py
python build_oras5_nordic_partial_budget_view.py
python fetch_oras5_nordic_column_heat.py --retrieved-at 2026-09-05T00:00:00Z
python analyze_oras5_nordic_storage_crosscheck.py
python build_oras5_nordic_storage_crosscheck_view.py
python audit_oras5_native_budget_availability.py --retrieved-at 2026-09-05T00:00:00Z
python fetch_oras5_nordic_seasonal_context.py --retrieved-at 2026-09-05T00:00:00Z
python analyze_oras5_nordic_remainder_context.py
python build_oras5_nordic_remainder_context_view.py
python analyze_oras5_nordic_collocation_sensitivity.py
python build_oras5_nordic_collocation_sensitivity_view.py
python analyze_oras5_nordic_heat_exchange_anatomy.py
python build_oras5_nordic_heat_exchange_anatomy_view.py
python build_oras5_nordic_heat_exchange_depth_view.py
python analyze_oras5_nordic_face_heat_map.py
python build_oras5_nordic_face_heat_map_view.py
python build_oras5_nordic_face_intensity_bakeoff_view.py
python build_oras5_nordic_face_driver_view.py
python build_oras5_nordic_face_persistence_view.py
python analyze_oras5_nordic_face_jet_runs.py
python build_oras5_nordic_face_jet_runs_view.py
python analyze_oras5_nordic_jet_run_sensitivity.py
python build_oras5_nordic_jet_run_sensitivity_view.py
python analyze_oras5_nordic_heat_relay.py
python build_oras5_nordic_heat_relay_view.py
python build_nordic_seas_budget_contract_view.py
```

The fixed three-part southern intent does not close: the ORCA025 Faroe
representation cannot support two independent land-attached cuts at those
endpoints. A continuous Iceland–Scotland Ridge cut works, then exposes another
missing opening through the North Sea. Adding a declared northern North Sea
section produces the accepted five-section surface room: 284 unique boundary
faces enclose 12,550 wet T cells; every face separates inside from outside and
the component reaches no mesh edge. The full-depth audit then gives every face
a native width, reconstructed partial-step thickness, wet mask, and area. All
five sections pass zero-mismatch, positive-area, and exact depth-bin closure
checks. Fram supplies 814 of the 1,816 km² total boundary area and reaches
2,577 m. The ledger is five pass / three open. This remains internal geometry;
state-field retrieval and advective/storage arithmetic have not advanced.

The surface stage aligns native `e1t`/`e2t` metrics and all twelve 2018 monthly
`sohefldo` fields to the exact 12,550-cell mask. The 2.713-million-km² room has
a time-weighted net downward flux of −39.4 W/m²: −106.8 TW or −3.37 ZJ across
the year, meaning net ocean heat loss under the source sign convention. Four
months warm the ocean and eight cool it. This is one ORAS5 member and year and
one budget term—not a climatology or a closed heat budget.

The compact state contract bounds T/S around every storage cell and both
tracer neighbors of every section face, then bounds U and V around only the
required native faces. Twelve files total roughly 110 MB. Their offline partial
budget keeps volume closure first: monthly imbalance spans −0.064 to +0.074 Sv.
At 0°C reference the time-weighted advective convergence is +96.8 TW, surface
input −106.8 TW, and the diagnostic mean unresolved remainder +37.7 TW.
Finite-difference storage uses monthly-mean midpoints. The remainder retains all
missing native tracer-budget terms and is not a causal label.

The storage cross-check integrates archived native `sohtcbtm` total-column heat
content over the identical area and applies the same monthly-midpoint finite
difference. It agrees with reconstructed 75-level temperature storage at
*r* = 0.99998 with 1.45 TW RMSE. Using that independent storage moves the mean
remainder only from +37.7 to +37.9 TW. The accompanying live-catalog audit
records all 23 ICDC ORCA025 variable families and confirms that the public
monthly archive has no model-native tendency, tracer-advection, mixing,
diffusion, ice-heat-exchange, or assimilation-increment families. This is an
availability boundary, not evidence that the production model never computed
those terms.

The seasonal-context stage retrieves native `ileadfra` (whose source metadata
labels it Ice concentration), `iicethic`, and `somxl010` over the same mesh. It
reports area-weighted ice concentration, 15% ice extent, a
concentration-times-thickness ice-volume proxy, and mixed-layer depth alongside
the monthly remainder. Zero-lag correlations are +0.05 for ice concentration,
−0.01 for ice volume, and +0.33 for mixed-layer depth. These twelve values are
an exploratory timing comparison; no lag search, significance claim, causal
attribution, or replacement for missing native tendencies is made.

The collocation sensitivity holds geometry, velocity, storage, and surface
forcing fixed while assigning adjacent-mean, upstream-donor, inside-cell, or
outside-cell temperature to every wet boundary face. Inside/outside results
shift annual convergence only ±2.25 TW. Upwind donor sampling shifts it +43.0
TW and changes the mean remainder from +37.7 to −5.3 TW, mostly through
Iceland–Scotland (+33.9 TW) and Denmark Strait (+10.6 TW). This is a sensitivity
endpoint, not reconstruction of NEMO's nonlinear time-stepped FCT/TVD operator:
all four rules multiply separate monthly-mean velocity and temperature fields.

The heat-exchange anatomy retains the upwind donor choice but splits every gate
into positive inward and outward branch magnitudes. Annual branch heat is
formed by day-weighting monthly fluxes; effective branch temperature is the
ratio of weighted heat to weighted volume. Denmark exports net volume while
converging +36.9 TW, Iceland–Scotland converges +222.9 TW through enormous
opposing streams, and Fram imports net volume while diverging −34.5 TW. These
are donor-rule diagnostics, not native FCT/TVD fluxes.

The same receipt preserves six midpoint-assigned reference-depth bins matching
the full-depth geometry audit. The depth view sums net inward-minus-outward
heat by gate and layer. It finds +148.8 TW above 700 m and −9.0 TW below,
including broadly distributed 0–700 m Iceland–Scotland input, upper-300 m
Norway–Svalbard loss, and upper-700 m Fram loss. Midpoint bins approximate
partial-bottom placement and do not define water masses.

The native-face map day-weights each monthly upwind-donor contribution before
summing vertically on all 284 faces. Section sums reproduce the paired-branch
receipt to numerical precision. There are 115 positive and 169 negative faces;
their 1,067 TW gross absolute exchange cancels by 87% to +140 TW net. The top
20 faces carry 52% of gross activity. Symbol area maps total TW per face—not
cross-sectional flux density—so face width and wet depth remain part of the
visual magnitude.

The intensity bakeoff divides annual face TW by fixed reconstructed wet
cross-sectional area and reports MW/m² through the vertical gate. Twelve of the
top 20 total-transport faces remain top-20 by intensity. The +66.4 TW face near
13.0°W, 64.0°N also has the maximum +7.66 MW/m² inward intensity. This unit is
not an air–sea surface flux and should not be compared numerically with
`sohefldo` W/m².

The driver view uses the exact identity `H = ρCp × A × Ugross × Θnet`, where
`Ugross` is inward-plus-outward volume exchange divided by wet face area and
`Θnet` is net face heat divided by `ρCp` and gross volume exchange. The 284-face
P90/P10 spreads are 12.8× in area, 8.1× in gross speed, and 22.7× in
`|Θnet|`. The leading face combines 8.66 km², 0.249 m/s, and +7.49°C. `Θnet`
contains directional and thermal cancellation and is not a water-mass
temperature.

The persistence view retains the twelve unweighted monthly face contributions
before their day-weighted annual reduction. It reranks all 284 faces each month.
The annual leader is positive and absolute rank #1 in 12/12 months; all annual
top-20 faces keep one sign, and monthly top-20 overlap spans 14–19 with a mean
of 16.7. Only 88 faces overall keep one sign for all twelve months. These tests
describe within-2018 monthly persistence, not interannual climatology.

`analyze_oras5_nordic_face_jet_runs.py` partitions each ordered section into
maximal adjacent sequences sharing annual heat sign. Its 95 runs recover all
284 faces and both gross and net heat exactly. The strongest import is a
four-face, 33 km, +106.5 TW Iceland-side core; the strongest export is a
33-face, 326 km, −72.0 TW Norway–Svalbard band. The top ten runs carry 50% of
gross exchange and retain sign in 12/12 monthly means. Fifty-one single-face
runs expose the sensitivity of unthresholded sign segmentation.

`analyze_oras5_nordic_jet_run_sensitivity.py` classifies faces by centered
local sums over 1, 3, 5, and 7 ordered faces, then sums original unsmoothed TW
inside each component. Run counts fall 95, 53, 36, and 29; singleton counts fall
51, 13, 6, and 4. The annual-leader component remains the strongest import at
1 and 3 faces, but a separate 32-face, +144.3 TW Scotland-side band leads at
5 and 7. Face order is not uniform distance, endpoint windows are truncated,
and no smoothing scale is selected as uniquely correct.

The same analyzer now calibrates those index windows against cumulative
face-center radii of 0, 20, 30, and 50 km. Paired 3/20, 5/30, and 7/50
face/km classifications agree on 277, 278, and 266 of 284 faces (97.5%, 97.9%,
and 93.7%). Physical-radius run counts are 95, 47, 37, and 29. Distance follows
face centers rather than exact face edges, so it reduces but does not eliminate
scale semantics.

`analyze_oras5_nordic_heat_relay.py` groups Denmark, Iceland–Scotland, and the
northern North Sea as southern input, then Fram and Norway–Svalbard as northern
export. Same-month correlation is 0.81 and is the strongest of twelve circular
alignments. Surface forcing and storage correlate at 0.98. Recomputing the
remainder with the same upwind convention gives annual means of +260.4 TW
southern input, −120.4 TW northern export, −107.6 TW surface, +26.5 TW storage,
and −5.8 TW unresolved. Circular shifts are timing contrasts, not a null model;
twelve seasonal months do not establish transit or causality.

`analyze_arctic_entrances_sensitivity.py` tests six Fram latitudes, five
eastern-lane starts, three western-lane ends, and eleven Barents longitudes.
`build_arctic_entrances_sensitivity_view.py` renders the 59-case sign and
magnitude challenge.

```powershell
python analyze_arctic_entrances_sensitivity.py
python build_arctic_entrances_sensitivity_view.py
```

`simulate_arctic_entrance_pathways.py` applies the same strict wet-stencil RK4
contract used by the Drake pilot to three entrance corridors and four seasonal
release times. Fram integrations stop at 20 days because the OSCAR substrate
ends at 80°N; Barents integrations run for 30 days. The output preserves every
completed and terminated track. `build_arctic_entrance_pathways_view.py`
renders the three panels without converting equal release counts into
transport or probability.

```powershell
python simulate_arctic_entrance_pathways.py
python build_arctic_entrance_pathways_view.py
```

`analyze_indonesian_gate_readiness.py` begins the next gateway by auditing five
candidate Indonesian Throughflow screens against a matching 71-field native
OSCAR subset. It records every screen point, finite-frame support, seasonal and
annual surface sign, and a declared readiness verdict. The accompanying plate
uses Natural Earth 1:10m land because the island cuts are part of the test.

```powershell
python fetch_oscar_timeseries_pilot.py --space-stride 1 --north 10 --south -15 --west 105 --east 140 --output ../atlas/data/oscar-timeseries-indonesian-native-2018.js
python analyze_indonesian_gate_readiness.py
python build_indonesian_gate_readiness_view.py
```

`fetch_hycom_indonesian_gates.py` performs a compact public OPeNDAP pull from
HYCOM GLBa0.08 experiment 91.2. It stores one daily T/S/U/V section sample at
all 33 standard z levels for each candidate instead of downloading a large
regional volume. `analyze_indonesian_grid_bakeoff.py` compares grid support
with the OSCAR audit while refusing a cross-product skill interpretation.

```powershell
python fetch_hycom_indonesian_gates.py
python analyze_indonesian_grid_bakeoff.py
python build_indonesian_grid_bakeoff_view.py
```

### Agulhas M2 junction

`stitch_oscar_agulhas_timeseries.py` joins the matched west and east source
windows across the OSCAR archive's 20°E storage seam. Longitudes 365–379.667°E
are normalized to 5–19.667°E and placed before the untouched 20–55°E columns;
no velocity values are interpolated. `analyze_agulhas_motion.py` then measures
speed, direction fractions, and vector coherence in four declared diagnostic
windows and integrates seven seed points at four seasonal release dates.

```powershell
python stitch_oscar_agulhas_timeseries.py
python analyze_agulhas_motion.py
python build_agulhas_motion_view.py
python analyze_agulhas_source_pathways.py
python build_agulhas_source_pathways_view.py
```

The output receipt is `../research/osw-m2-agulhas-motion-2018.json`; the plate
is `../figures/osw-motion-agulhas-junction-2018.svg`. Every track uses forward
RK4 with six-hour steps, daily output, strict jointly wet bilinear stencils, no
diffusion, and no transport weighting. These are nominal-15-m kinematic
pathways, not water-mass, volume, heat, or probability estimates.

The source-tagged extension writes
`../research/osw-m2-agulhas-source-pathways-2018.json` and
`../figures/osw-motion-agulhas-source-pathways-2018.svg`. It expands four
upstream centers into 3×3 ±0.1° neighborhoods at three dates, integrates each
path for 150 days, and preserves unresolved, terminated, and both-threshold
outcomes. A 3×3 sensitivity matrix crosses west gates at 12/15/18°E with east
gates at 33/35/37°E. The resulting counts test the fate definition; they are
not leakage percentages.

`prepare_agulhas_m3_experiment.py` converts the published experiment design
into a machine-readable intake and acceptance contract. The authors' GEOMAR
archive now resolves the reference GoodHope geometry: 53 West-section and two
Northwest-section coordinate records form the composite leakage exit. A new
run must still map that reference line onto its own native grid.

```powershell
python prepare_agulhas_m3_experiment.py
python build_agulhas_m3_contract_view.py
python fetch_geomar_agulhas_derived.py
python analyze_geomar_agulhas_transport.py
python build_geomar_agulhas_transport_view.py
```

The outputs are `../research/osw-m3-agulhas-experiment-contract.json` and
`../figures/osw-m3-agulhas-experiment-contract.svg`. The fetcher adds a compact,
checksum-pinned 304 KB CC BY 4.0 subset of the authors' derived INALT20/Parcels
output. The attributed recalculation in
`../research/osw-m3-geomar-agulhas-published-replication.json` and
`../figures/osw-m3-geomar-agulhas-published-replication.svg` recovers a mean
West+Northwest leakage of 9.894 Sv across 57 release years (1958–2014), a
2.082 Sv descriptive population spread, a +0.464 Sv per decade OLS trend, and
a 40.02 Sv mean East exit. These are summaries of published model output—not
a new OSW simulation, an observational estimate, heat transport, or an
uncertainty interval. The archive does not contain the raw 3-D velocity needed
to execute a new trajectory experiment.

## Projection bakeoff

`build_projection_bakeoff.py` projects one schematic fluid overlay and the
checksum-pinned Natural Earth coastline geometry into four global candidates:
Spilhaus, Oceanic Interrupted Goode Homolosine, South-Pacific-centered Equal
Earth, and experimental PELAGOS. It also builds HEATPLATES, a six-panel local
Lambert equal-area shape directory.
PELAGOS uses established spherical Lambert azimuthal equal-area mathematics
centered at 20°S, 165°W, placing its antipodal singular boundary at 20°N,
15°E in the Sahara. It is a proposed aspect and cut policy, not a new equation.

```powershell
python -m pip install -r ../requirements-projections.txt
python build_projection_bakeoff.py `
  --land-geojson path/to/ne_110m_land.geojson `
  --output-dir ../figures
```

The four global outputs use identical schematic heatmass polygons with inset
shelf contours, anomalies, currents, buried Arctic inflow, gates, and ACC.
HEATPLATES uses panel-specific zoom so each object remains legible; footprint
area must not be compared across its panels. All polygon boundaries are
illustrative rather than observed thresholds. The figures compare projection
and shape-atlas behavior; they are not observational heat fields or transport
calculations.

`build_state_data_views.py` takes the seven observational fields already
packaged for Atlas 10 and projects their source cells directly into the winning
Oceanic Mollweide state view. It adds the same provisional realm/region/state
hierarchy as a reference overlay and matched north/south LAEA mirrors. It does
not aggregate values by state.

```powershell
python build_state_data_views.py `
  --land-geojson path/to/ne_110m_land.geojson `
  --data-dir ../atlas/data `
  --output-dir ../figures
```

## Detected-object receipts

`fetch_noaa_crw_mhw_point.py` downloads 32 exact NOAA Coral Reef Watch daily
NetCDF files, records each raw-file SHA-256, and extracts the category at the
independently selected 42.125°N, 49.875°W pixel. Then
`detect_noaa_crw_marine_heatwave.py` applies the registry's five-day duration
and two-day gap rule:

```powershell
python fetch_noaa_crw_mhw_point.py
python detect_noaa_crw_marine_heatwave.py
python build_ocean_object_evidence_receipts.py
```

The result is a point-event receipt, not a spatial footprint. The companion
`fetch_oisst_mhw_point.py` and `detect_oisst_marine_heatwave.py` preserve an
independent raw-SST implementation path; its remote acquisition is resumable
and refuses to emit a complete source artifact until all baseline years arrive.

`derive_noaa_crw_mhw_footprint.py` advances one step further on 2026-08-01. It
re-downloads the exact raw file pinned by the point receipt, verifies its hash,
and extracts the native-grid four-neighbor component containing the OSW-D1
anchor. `build_detected_mhw_footprint_view.py` renders its exact row-run shape:

```powershell
python derive_noaa_crw_mhw_footprint.py
python build_detected_mhw_footprint_view.py
```

This is a daily footprint. Tracking one identity through shape overlap,
splits, merges, and gaps is deliberately a separate next-stage method.

`track_noaa_crw_mhw_footprint.py` performs that next stage without silently
animating unrelated blobs. It verifies all 32 upstream files, follows the
greatest exact-pixel-overlap branch forward and backward from the qualified
anchor, reports every overlap fraction and branch ambiguity, and reproduces
the OSW-D2 seed byte-for-structure. `build_tracked_mhw_lineage_view.py` renders
six identical-frame snapshots plus the area history:

```powershell
python track_noaa_crw_mhw_footprint.py
python build_tracked_mhw_lineage_view.py
python build_ocean_object_evidence_receipts.py
```

The exact-overlap lineage ends on August 10; bridging the point event's
August 11 gap is not automatic and remains a sensitivity question.

`analyze_mhw_gap_identity.py` performs that sensitivity rather than choosing by
intuition. It independently seeds the seven-day post-gap lineage, measures its
exact overlap with the August 10 remnant, and compares uninterrupted daily
inheritance with a one-day temporal-gap policy. `build_mhw_gap_identity_view.py`
renders the two valid results side by side:

```powershell
python analyze_mhw_gap_identity.py
python build_mhw_gap_identity_view.py
python build_ocean_object_evidence_receipts.py
```

The result reconnects under the one-day policy with 122 exact grid locations and zero
spatial dilation; it remains split under uninterrupted daily inheritance.

`analyze_mhw_tracking_sensitivity.py` holds the greatest-intersection branch
rule fixed while crossing four- versus eight-neighbor adjacency with five
minimum-overlap policies. `build_mhw_tracking_sensitivity_view.py` renders the
ten outcomes as a policy matrix and dated stability timeline:

```powershell
python analyze_mhw_tracking_sensitivity.py
python build_mhw_tracking_sensitivity_view.py
python build_ocean_object_evidence_receipts.py
```

Adjacency is invariant in this case. Overlap thresholds expose a 21-day
permissive lineage, an 18-day moderate-threshold plateau, and a one-day result
under IoU 0.50. These are threshold-state identity outcomes, not water-parcel
tracking or a physical mechanism diagnosis.

`analyze_mhw_branch_policy_sensitivity.py` then holds four-neighbor adjacency
and any-exact-cell overlap fixed while changing the score that chooses one
branch at a split or merge. `build_mhw_branch_policy_view.py` exposes both the
lineage lifetimes and the two divergent component choices:

```powershell
python analyze_mhw_branch_policy_sensitivity.py
python build_mhw_branch_policy_view.py
python build_ocean_object_evidence_receipts.py
```

Three policies reproduce the same 21 components cell for cell. Maximizing only
candidate-inherited fraction selects 12- and one-cell splinters because each is
fully contained in the preceding shape, then stops after 14 days. The receipt
therefore preserves branch selection as part of the identity contract.

`build_mhw_lineage_family.py` avoids selecting one heir. It expands forward and
backward from the same anchor, retaining every distinct adjacent-day component
reachable by exact native-cell overlap. `build_mhw_lineage_family_view.py`
renders the resulting directed acyclic graph:

```powershell
python build_mhw_lineage_family.py
python build_mhw_lineage_family_view.py
python build_ocean_object_evidence_receipts.py
```

The family contains 28 nodes and 29 edges. Its 21-node D3 trunk has seven side
components, five split nodes, and one merge node. No minimum size is imposed;
tiny branches remain evidence rather than being silently pruned.

`analyze_mhw_lineage_family_pruning.py` applies six minimum daily component
areas to D7, removes incident edges, and recomputes the anchor-connected induced
graph. `build_mhw_family_pruning_view.py` renders the topology ladder:

```powershell
python analyze_mhw_lineage_family_pruning.py
python build_mhw_family_pruning_view.py
python build_ocean_object_evidence_receipts.py
```

The 21 primary nodes survive every tested threshold without an override. Side
components fall from seven to four, four, two, one, and zero; the sole merge
disappears at 500 km². Thresholds are illustrative, not calibrated defaults.

`build_mhw_typed_gap_graph.py` combines the D7 family with D4's seven-day
post-gap primary lineage while preserving two edge meanings. Solid edges join
consecutive active days; one typed edge spans the inactive August 11 field and
requires exact endpoint overlap. `build_mhw_typed_gap_graph_view.py` renders
both policy outcomes:

```powershell
python build_mhw_typed_gap_graph.py
python build_mhw_typed_gap_graph_view.py
python build_ocean_object_evidence_receipts.py
```

The strict graph remains 28 nodes and 29 edges through August 10. The
conditional graph has 35 nodes and 36 edges through August 18. The post-gap
addition is one primary lineage, not a complete branch-family expansion.

`fetch_oisst_mhw_bridge.py` extracts six separate-product OISST fields over a fixed
North Atlantic box, and `analyze_oisst_mhw_bridge.py` pairs the nearest OISST
cell and fixed-box mean with the CRW anchor categories.
`build_oisst_mhw_bridge_view.py` renders the six-field cross-check:

```powershell
python fetch_oisst_mhw_bridge.py --retrieved-at 2026-09-06T00:00:00Z
python analyze_oisst_mhw_bridge.py
python build_oisst_mhw_bridge_view.py
python build_ocean_object_evidence_receipts.py
```

The August 12 CRW category return occurs while the nearest OISST cell cools
0.13°C. The fixed OISST box mean warms 0.160°C and its maximum warms 0.18°C,
so the result motivates a spatial/product distinction rather than a local
reheating claim. Surface forcing, currents, mixing, and causation remain open.

`fetch_rtofs_mhw_bridge.py` uses HTTP range reads against NOAA's public RTOFS
S3 archive to extract six collocated surface-temperature, surface-current, and
mixed-layer-thickness snapshots. `analyze_rtofs_mhw_advection.py` estimates
local tangent-plane gradients and an endpoint-mean horizontal-advection term;
`build_rtofs_mhw_advection_view.py` renders the bridge interval and five-day
tendency sequence:

```powershell
python fetch_rtofs_mhw_bridge.py --retrieved-at 2026-09-06T00:00:00Z
python analyze_rtofs_mhw_advection.py
python build_rtofs_mhw_advection_view.py
python build_ocean_object_evidence_receipts.py
```

From August 11 to 12 the RTOFS fixed box warms 0.5396°C/day. Horizontal
advection contributes +0.0708°C/day, leaving +0.4688°C/day unresolved; at the
anchor it opposes the modeled warming. The remainder is not assigned to the
atmosphere because surface flux, vertical/mixing, assimilation, and native
model tendency terms have not yet been added.

`fetch_gfs_mhw_surface_flux.py` uses NOAA's public GFS `.idx` sidecars and HTTP
byte ranges to retain only six surface-energy messages from each of four
six-hour-average forecast files per day. `analyze_gfs_mhw_surface_flux.py`
reconstructs net downward flux, bilinearly samples it on the RTOFS grid, and
converts the energy to a mixed-layer temperature-change scale. The conversion
retains native, 2/5/10 m floor, and box-mean slab depth variants;
`build_gfs_mhw_surface_flux_view.py` renders their bridge-day geography and
five-interval evolution:

```powershell
# ecCodes 2.48 has been acquisition-tested under Python 3.12 on Windows.
py -3.12 fetch_gfs_mhw_surface_flux.py --retrieved-at 2026-09-06T00:00:00Z
python analyze_gfs_mhw_surface_flux.py
python build_gfs_mhw_surface_flux_view.py
python build_ocean_object_evidence_receipts.py
```

The GFS box changes from net surface heat loss on August 7–9 to heat gain on
August 10–11. During the August 11–12 bridge interval it gains +112.61 W/m².
Depending on the declared RTOFS mixed-layer depth treatment, that is a
+0.1219 to +0.3381°C/day temperature-change scale, compared with D11's
+0.4688°C/day pre-flux remainder. This is a cross-system magnitude test—not an
atmospheric reanalysis, a native GFS/RTOFS budget closure, or attribution.

`fetch_rtofs_mhw_upper_ocean.py` extracts potential temperature at all fifteen
RTOFS standard depths from 0 through 50 m. The analyzer integrates changes over
fixed 10, 20, 30, and 50 m columns, avoiding division by the rapidly changing
diagnostic mixed-layer thickness. The view contrasts surface change, fixed-column
change, their difference, vertical profiles, and cumulative storage:

```powershell
python fetch_rtofs_mhw_upper_ocean.py --retrieved-at 2026-09-06T00:00:00Z
python analyze_rtofs_mhw_upper_ocean_storage.py
python build_rtofs_mhw_upper_ocean_storage_view.py
python build_ocean_object_evidence_receipts.py
```

From August 11 to 12 the RTOFS box surface warms +0.5396°C while the fixed
0–50 m mean warms +0.0997°C. The upper ocean therefore gains heat, but the
surface intensifies 5.4 times faster. Constant-`ρCp` storage is +236.03 W/m²
through 50 m, compared with +112.61 W/m² forecast-derived GFS surface gain.
The difference is not a closed residual: horizontal and vertical transport,
mixing, analysis increments, native-layer geometry, and cross-model mismatch
remain unresolved.

The upper-ocean source cube also carries eastward and northward velocity at
the same fifteen depths. `analyze_rtofs_mhw_upper_ocean_advection.py` estimates
`−u·∇T` independently at every depth, averages interval endpoints, and
integrates the tendency through fixed columns. The four-neighbor sensitivity
checks the primary eight-neighbor gradient; the view compares storage,
horizontal motion, GFS surface flux, and the explicitly partial residual:

```powershell
python analyze_rtofs_mhw_upper_ocean_advection.py
python build_rtofs_mhw_upper_ocean_advection_view.py
python build_ocean_object_evidence_receipts.py
```

During August 11–12, depth-integrated horizontal advection is +171.21 W/m²,
72.5% of RTOFS's +236.03 W/m² fixed-column storage scale. Adding +112.61 W/m²
GFS surface gain gives 120.2%, leaving −47.79 W/m². This close magnitude is
not a native closure: the flux crosses model systems and the offline advection
is neither conservative convergence nor native tracer tendency. The result's
durable lesson is vertical: a surface diagnostic equal to 13.1% of surface
warming coexists with a distinct 0–50 m diagnostic equal to 72.5% of fixed-column
storage. These are different supports and denominators, not one fraction traced
downward.

## Source-aligned province-wide bathymetry

`acquire_longhurst_2007_gebco_depths.py` performs one explicit network stage
across the Marine Regions Longhurst Version 4 WFS and global 0.25° GEBCO_2026
elevation/TID grids. It applies point-in-polygon membership at GEBCO centers,
records three source-ring validity repairs, weights wet cells by spherical
area, and emits the 56↔54 edition crosswalk, 54 province summaries, and a
run-length footprint mask used by the Ocean Column workbench.

```powershell
python -m pip install -r ../requirements-geography.txt
python acquire_longhurst_2007_gebco_depths.py
python -m pytest test_longhurst_2007_gebco_depths.py test_ocean_column_viewer.py -q
```

The source responses are not vendored. Their exact URLs, byte counts, response
metadata, and SHA-256 hashes are committed in the source receipt. The resulting
681,631 wet intersections estimate province seafloor-depth distributions at
the declared sampling. The same build integrates spherical cell area ×
bathymetry-truncated band thickness, yielding per-province water volume,
area-weighted mean depth, and a five-band volume ledger. Its
1.338-billion-km³ total is 0.0258% below an independent USGS global context
estimate, a scale check that did not calibrate the calculation. These outputs
are not exact polygon/native-grid volumes, ecological occupancy at depth,
dynamic provinces, current boundaries, heat, or transport.

`derive_province_hypsometric_fingerprints.py` is the offline next stage. It
binds to the depth payload by SHA-256 and derives one complete, mutually
exclusive floor character from the dominant seafloor-area band, plus
independent substantial-band breadth (≥5%), hadal presence, and area-to-volume
rank shift. It writes both the research JSON and browser payload without any
network access:

```powershell
python derive_province_hypsometric_fingerprints.py
python -m pytest test_province_hypsometric_fingerprints.py -q
```

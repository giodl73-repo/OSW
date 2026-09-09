# Ocean Column Address workbench

This browser-only workbench implements the interaction grammar defined in
[Guide 15](../guides/15-OCEAN-COLUMN-ADDRESS.md). It is reference geography and
conceptual teaching material—not an observed three-dimensional ocean product.

## What is real in this stage

- The 56 province names, codes, basins, and biomes come from the committed
  [classic reference directory](../research/longhurst-province-reference.csv).
- The five bands, exact endpoints, vertical direction, mask rule, and overlay
  boundary come from the machine-readable
  [edition-1 contract](../research/ocean-column-address-v1.json).
- The builder records SHA-256 hashes for both inputs in `data.js`.
- One GEBCO_2026 15-arc-second grid cell is sampled at each approximate display
  seed through CEDA OPeNDAP. The committed receipt preserves all 56 exact query
  URLs, ASCII responses, and response checksums. Fifty-three are wet; NEWZ,
  NWCS, and REDS are retained as non-wet seed results.
- The matching GEBCO Type Identifier cells show 28 direct-measurement sources,
  24 indirect or interpolated sources, one mixed/unknown pre-generated grid,
  and the three land cells. The viewer reports the exact TID code and definition
  rather than using “measured” as a blanket quality claim.

## What is illustrative

The 90 m shelf, 4,800 m basin, and 8,000 m trench remain teaching columns. The
additional selected-seed column is a measured GEBCO grid value, but it is not a
province mean, range, profile, area, or occupancy fraction. The mixed-layer,
thermocline, water-mass, and bottom-boundary ranges are hypothetical overlays
chosen only to demonstrate overlap.

“Readable bands” gives each of the five bands equal display height and is
explicitly non-linear. “Linear depth” maps 0–8,000 m proportionally and exposes
how thin the upper bands become at full-ocean scale.

## Seed neighborhoods

Each approximate seed also has an 8° × 8° geographic window sampled every
0.25°: 33 × 33 or 1,089 elevation cells plus matching TID cells. Across all 56
windows that is 60,984 paired samples. Twenty-nine windows are entirely wet at
this sampling; 27 contain both land and water; none is entirely dry. The source
classes are 22,430 direct-measurement, 32,855 indirect/interpolated, 1,139
mixed/unknown, and 4,560 land samples.

The neighborhood map can show either the depth band reached by the seafloor or
the GEBCO source class. It is a regular longitude/latitude display, not an
equal-area map: pixel counts and proportions are sample counts, never area
fractions. The window does not follow or estimate province boundaries.

## Source-aligned province footprints

The next panel replaces the seed window with the revised Longhurst 2007
geometry distributed by Marine Regions as Version 4. A global GEBCO_2026
elevation/TID screen assigns 0.25° pixel centers to those polygons and weights
every wet center by its spherical cell area. The result contains 681,631 wet
province intersections, no overlaps, and 54 province-wide depth/source
summaries. The map uses Oceanic Mollweide so the geographic view is equal-area;
the quantitative summaries retain independent spherical weights.

The same cells now support a first three-dimensional reference ledger. For
each wet center, OSW multiplies spherical cell area by the thickness of each
pelagic band present above the local GEBCO seabed. Summing those prisms yields
approximately 1.338 billion km³ across the source-aligned footprint: 5.14%
epipelagic, 19.50% mesopelagic, 62.84% bathypelagic, 12.41% abyssopelagic, and
0.11% hadalpelagic. The browser can switch the depth bar between water-volume
share and the earlier seafloor-reaching area share.

This is a sampled volume approximation, not voxelized native-resolution
ocean volume. It omits partial coastal cells, uses center membership and
prismatic cell geometry, and inherits GEBCO and Version 4 seams. Its total is
0.0258% below the independent USGS context estimate of 1.338 billion km³; that
agreement is a scale check, not calibration or validation of province values.

This resolves geometry for the source's 54-province edition, not retroactively
for every name in OSW's older 56-identity directory. Five codes crosswalk by
alias (`CHIL/HUMB`, `INDE/IND E`, `INDW/IND W`, `NASE/NAST E`, and
`NASW/NAST W`). `NPSE` and `OCAL` have no separate Version 4 footprint because
the later edition merged or reorganized the relevant North Pacific geography.
The viewer leaves those two selections unhighlighted rather than inventing a
border.

The provider geometry contains three invalid rings (`ALSK`, `NECS`, `SUND`);
the acquisition records the GEOS validity repair. It also preserves 5,519
polygon centers that GEBCO classifies as non-wet and 2,772 globally wet GEBCO
centers outside the polygon cover. Those are source/grid seam diagnostics, not
cells silently reassigned to make the map close.

## Rebuild and verify

```powershell
python analysis/build_ocean_column_viewer.py
python analysis/build_gebco_province_seed_neighborhoods.py
node --check column/app.js
python -m pytest analysis/test_ocean_column_viewer.py analysis/test_longhurst_2007_gebco_depths.py -q
```

Refresh the source only as an explicit network operation:

```powershell
python -m pip install -r requirements-geography.txt
python analysis/acquire_gebco_province_seed_depths.py
python analysis/acquire_gebco_province_seed_neighborhoods.py
python analysis/acquire_longhurst_2007_gebco_depths.py
python analysis/build_gebco_province_seed_depths.py
python analysis/build_gebco_province_seed_neighborhoods.py
python analysis/build_ocean_column_viewer.py
```

The default test suite remains offline. Generated browser payloads are committed
so the page does not need a provider or build step at runtime. The full provider
geometry and GEBCO responses are checksum-receipted but omitted under the
declared source-payload posture.

## Next evidence gate

The geometry, bathymetry, and sampled depth-band volume gates are now
implemented for the source-aligned 54. The next horizontal gate is an edition
decision: preserve an explicit 56/54 selector, migrate
the quantitative address to Version 4, or locate an independently reproducible
and redistributable older geometry. No approach may silently project the two
unmatched identities onto Version 4.

GEBCO is implemented source D5 in the [source register](../SOURCE-REGISTER.md).
The grid is public domain with requested attribution. GEBCO states that its
terrain is assembled from heterogeneous sources, assumes mean sea level while
noting possible shallow-water datum exceptions, and is not for navigation.

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

## Rebuild and verify

```powershell
python analysis/build_ocean_column_viewer.py
node --check column/app.js
python -m pytest analysis/test_ocean_column_viewer.py -q
```

Refresh the source only as an explicit network operation:

```powershell
python analysis/acquire_gebco_province_seed_depths.py
python analysis/build_gebco_province_seed_depths.py
python analysis/build_ocean_column_viewer.py
```

The default test suite remains offline. `data.js` is committed so the page does
not need a provider or build step at runtime.

## Next evidence gate

Province-wide occupancy needs all of the following before it can replace the
single-cell screen and teaching columns:

1. exact, licensed horizontal province geometry rather than OSW's approximate
   nearest-seed display geometry;
2. a controlled GEBCO_2026 spatial subset covering that exact geometry;
3. coordinate bounds, vertical datum, wet mask, and partial-cell policy;
4. a deterministic intersection with source checksums and uncertainty notes;
5. `.roles` review of the resulting cartography and data claim.

GEBCO is implemented source D5 in the [source register](../SOURCE-REGISTER.md).
The grid is public domain with requested attribution. GEBCO states that its
terrain is assembled from heterogeneous sources, assumes mean sea level while
noting possible shallow-water datum exceptions, and is not for navigation.

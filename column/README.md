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

## What is illustrative

The 90 m shelf, 4,800 m basin, and 8,000 m trench are teaching columns. They are
not sampled at the selected province, and selecting a province × band pair does
not establish that the address class contains wet volume. The mixed-layer,
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

The default test suite remains offline. `data.js` is committed so the page does
not need a provider or build step at runtime.

## Next evidence gate

Province-specific occupancy needs all of the following before it can replace
the teaching columns:

1. exact, licensed horizontal province geometry rather than OSW's approximate
   nearest-seed display geometry;
2. a pinned version and subset of a bathymetry grid such as GEBCO;
3. coordinate bounds, vertical datum, wet mask, and partial-cell policy;
4. a deterministic intersection with source checksums and uncertainty notes;
5. `.roles` review of the resulting cartography and data claim.

GEBCO is currently only candidate source D5 in the
[source register](../SOURCE-REGISTER.md). No GEBCO bytes are present in this
stage.

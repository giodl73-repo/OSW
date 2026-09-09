# What an Ocean State Contains

A province is an address. A property passport asks what a particular dataset
contains at that address without pretending that the province is a sealed box.

OSW's first contents screen uses the native ORAS5 ocean grid in the Drake
sector. It joins each wet temperature-cell center to one revised Longhurst
Version 4 province, then keeps depth and month explicit. The result is a
reproducible model-screened distribution, not a new water-mass map.

## Read the complete address

```text
GEOMETRY EDITION × PROVINCE × DEPTH SUPPORT × VALID TIME × PROPERTY × METHOD
longhurst-v4-54   ANTA       0–200 m         2018-08      temperature osw-hydrography-pilot-v1
```

Changing any term changes the question. In particular, a February surface
distribution cannot silently stand in for an annual, full-depth, or
climatological inventory.

## What Stage 3 admits

The current pilot has six supported province footprints in the downloaded
Drake subset: `ANTA`, `APLR`, `FKLD`, `HUMB`, `SANT`, and `SSTC`. Four monthly
means—February, May, August, and November 2018—sample four supported depth
bands from 0 to 6,000 m. This produces 96 province × depth × month passports.

Each passport reports the sample count, coverage, minimum, maximum, mean,
standard deviation, and five distribution quantiles. Coverage and estimated
uncertainty remain different fields: all current passports have complete
support among the expected native samples, but uncertainty is **not
estimated** from one ensemble member and four months.

[Open the Contents workbench](../exchange/) or [download the complete
receipt](../research/ocean-state-hydrography-pilot-2018.json).

## Why distributions come before averages

Two neighboring states can have similar means but very different mixtures of
temperatures. Quantiles retain more of that structure:

```text
p10 ───── p25 ═════ median ═════ p75 ───── p90
tails        middle half of native samples        tails
```

The samples are intentionally identified as unweighted native T-cell-level
values. They are not volume-weighted because a complete admitted T-cell
horizontal-metric convention has not yet entered this contents product.

## Reading the two maps

The temperature map colors only native cells inside the actual downloaded
Drake extent. Gray province area outside that window means **out of domain**,
not missing temperature or an inferred continuation. The companion support
map shows whether the selected passport has complete, partial, or absent
native support. The six-state text table carries the same result without
requiring color or spatial perception.

## What an adjacent contrast means

For every supported shared edge, OSW compares the two independently summarized
province distributions at the same depth and month. A difference in medians is
a descriptive contrast. It does not establish a front, barrier, exchange,
transport, mechanism, or independent significance. Native ocean cells are
spatially autocorrelated, and the pilot makes 128 related comparisons.

Stage 4 must independently test motion normal to a selected source edge before
the project can say anything about crossing water or heat.

## Variables that remain unavailable

- **Salinity:** absent from the already-custodied Drake state subsets.
- **Density:** cannot be derived without salinity and a declared equation of
  state.
- **Oxygen:** absent from the subsets.
- **Heat content:** withheld until horizontal metrics, complete volume support,
  density, heat capacity, and a reference convention are admitted together.

Temperature is therefore never relabeled as heat content. Distribution spread
is never relabeled as uncertainty. A model screen is never relabeled as an
observation.

## Reproduce and audit

The machine receipt binds the mutable Marine Regions response, normalized
geometry, ORAS5 mesh and four temperature files, license and citation notes,
grid extent, assignment counts, passports, contrasts, unsupported variables,
and limitations. Regeneration is an explicit network operation:

```powershell
python analysis/acquire_ocean_state_hydrography_pilot.py
```

Default verification is offline and compares the browser derivative with the
committed receipt. Future methods must create a new version and revision
lineage instead of rewriting the meaning of old state accounts.

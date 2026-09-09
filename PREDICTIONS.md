# OSW Predictions

These tests convert the atlas vocabulary into claims that can fail. They do
not assume that Antarctic water masses and gas-giant belts share one material
mechanism.

## HZ1 — A surface band does not preserve one identity with depth

**Claim.** A tracer-defined band crossing a major stratification,
condensation, or circulation transition will not retain one fixed relationship
among temperature, composition, density, and velocity at every depth.

**Ocean measure.** Compare sea-surface temperature, mixed-layer properties,
Winter Water, Circumpolar Deep Water, density surfaces, and velocity along a
frozen Southern Ocean section.

**Jupiter measure.** Compare co-registered visible, infrared, and microwave
contrasts with full contribution functions, keeping temperature and ammonia
retrieval branches separate through the 5–10 bar jovicline.

**Falsifier.** After matching resolution and observation kernels, the surface
boundary predicts all admitted deeper boundaries and contrast signs within
uncertainty.

## HZ2 — Cross-front exchange is spatially concentrated

**Claim.** Exchange across a persistent current or front clusters where the
mean barrier meanders, destabilizes, meets another coherent feature, or
interacts with topography.

**Ocean measure.** Compare cross-front velocity–temperature covariance with
eddy kinetic energy, front curvature, ridges, fracture zones, and downstream
topographic position.

**Gas-giant measure.** Test whether cross-jet tracer exchange clusters near
persistent waves, vortices, jet curvature, or outbreak regions. Treat this as
a proxy unless the enthalpy flux is closed.

**Falsifier.** Exchange is spatially uniform, performs no better than
coverage-matched null locations, or disappears when navigation and kernel
uncertainty are propagated.

## HZ3 — Freshening can hide heat below without creating it

**Claim.** Where salinity controls upper-ocean density, meltwater can strengthen
surface stratification, reduce upward heat exchange, and increase subsurface
heat convergence even as the surface cools. The sign can reverse regionally if
lateral freshwater transport blocks warm-water supply.

**Measure.** Resolve freshwater source depth, salinity and density profiles,
mixed-layer depth, vertical heat flux, shelf-break supply, dense-water
formation, and subsurface storage in one conservation-complete experiment.

**Falsifier.** Freshening causes no resolved stratification or flux change,
subsurface warming is absent, or an independently measured advective change
fully explains the result.

## HZ4 — A Jovian circulation reversal requires independent channels

**Claim.** If stacked circulation cells or precipitation physics cause the
jovicline contrast reversal, independently sensitive temperature and
composition channels should show a vertically ordered transition consistent
with the retrieved thermal-wind shear.

**Measure.** Freeze pressure contribution functions, geometry, temperature and
ammonia branches, condensation/stability predictions, cloud-top winds, and the
moist thermal-wind calculation before fitting the transition.

**Falsifier.** Transition pressure is unstable across independent
observations, retrieval branches imply incompatible shear, the reversal follows
opacity assumptions instead of a physical layer, or a null circulation fits
equally well.

## Result vocabulary

| Result | Meaning |
|---|---|
| `supported_within_regime` | relation survives uncertainty and nulls in the stated regime |
| `partial_or_regional` | support is limited to resolved sectors, pressures, or seasons |
| `non_transfer` | diagnostic works in one system but the cross-system transfer fails |
| `unresolved_by_observation` | available kernels, cadence, or budget terms cannot distinguish alternatives |

`Unresolved` is not evidence for or against a mechanism. `Non-transfer` is a
scientific result rather than a failed project.

# OCEANBELTS — Heat Zones on Gas Giants

**Status:** controlled Earth–Jupiter–Saturn translation · observation-class
synthesis

**Question:** When can a visible belt or zone on a gas giant be called a heat
zone?

## Answer

Not from color alone. A gas-giant band becomes a thermal observation only when
an instrument's pressure-sensitive signal is inverted or otherwise related to
kinetic temperature with composition, opacity, viewing geometry, and retrieval
uncertainty carried along. Even then, temperature at one pressure is not
vertically integrated heat content, and neither quantity is a measured heat
transport. Jupiter provides the decisive warning: Juno microwave observations
show belt/zone brightness contrasts reversing at roughly 5–10 bar. The same
named latitude band changes character with depth.

![A stripe changes identity with depth](figures/ocean-belts.svg)

## A cloud top is not a surface

Earth's ocean has a material free surface and a seafloor. Jupiter and Saturn do
not have an equivalent solid or liquid boundary at the visible clouds. Their
vertical coordinate is most usefully described by pressure:

```text
low pressure / high altitude
  -> hazes and upper clouds
  -> visible cloud tracers
  -> weather layer and condensable species
  -> deeper, warmer, denser atmosphere
  -> fluid interior
high pressure / greater depth
```

The apparent edge of the planet is an optical-depth surface whose altitude
depends on wavelength, composition, clouds, and viewing angle. Two instruments
can map the same latitude and longitude while sensing different overlapping
pressure ranges.

## Five observables that must remain separate

| Observable | What it actually says | What it does not establish |
|---|---|---|
| visible color / albedo | reflected sunlight shaped by clouds, haze, particles, and illumination | kinetic temperature or heat content |
| infrared brightness spectrum | thermal emission weighted across pressure and molecular opacity | a direct thermometer at one exact level without retrieval assumptions |
| microwave brightness temperature | emitted microwave intensity shaped by physical temperature and absorbers such as ammonia and water | kinetic temperature alone |
| cloud-tracked wind | motion of a tracer feature at an inferred cloud level | deep material velocity or heat flux |
| gravity harmonic | integrated mass anomaly constrained through an interior/dynamics model | a local temperature, composition, or velocity profile |

Brightness temperature is the temperature a blackbody would need to reproduce
the observed radiance at that wavelength. It need not equal the kinetic
temperature of one physical parcel when opacity varies across a broad
contribution function.

## Jupiter's belts change character with pressure

Jupiter's familiar dark belts and bright zones correlate strongly with zonal
jets, cloud properties, and upper-tropospheric circulation. Juno's Microwave
Radiometer extended the comparison beneath the visible clouds.

The central result is a reversal:

```text
upper troposphere, below about 5 bar
  belts: microwave bright
  zones: microwave dark

transition around roughly 5–10 bar: “jovicline”

deeper troposphere, above about 10 bar
  belts: microwave dark
  zones: microwave bright
```

Microwave-bright can mean physically warmer, depleted in microwave absorbers
such as ammonia, or a combination. Microwave-dark can mean cooler, enriched in
absorbers, or a combination. The reversal therefore demonstrates a change in
belt/zone structure with depth, but it does not by itself uniquely separate
temperature from composition
([Fletcher et al., 2021](https://doi.org/10.1029/2021JE006858)).

This is the gas-giant equivalent of the Antarctic warning that a cold surface
can overlie warmer deep water. The mechanisms and materials differ, but the
observational lesson transfers exactly:

> a two-dimensional band name cannot substitute for a vertical state.

## Thermal wind: the useful bridge

Horizontal temperature and composition gradients affect density. Away from
the equator, in a rotating, approximately balanced atmosphere, those gradients
relate to the vertical shear of the zonal wind through an atmospheric
thermal-wind relation. In pressure coordinates, a dry ideal-gas schematic is

```text
partial(u_g) / partial(ln p)
  = (R / f) partial(T) / partial(y)
```

with sign and component conventions stated for the chosen coordinates. Moist
condensation and molecular-weight gradients require a more complete form.
Thus a belt/zone temperature contrast can constrain how a jet changes with
pressure, but only within the balance and retrieval assumptions.

For the Juno microwave contrast, temperature-only and ammonia-only
interpretations imply different shear magnitudes. Fletcher et al. found that
the ammonia-only contribution generated much weaker shear in their moist
thermal-wind analysis. The observation therefore constrains candidate vertical
circulations without turning brightness directly into temperature.

## Saturn: bands, seasons, and pressure-sensitive winds

Saturn's visible atmosphere is also organized by zonal jets, belts, storms,
and polar structures. Cassini supplied complementary operators:

- ISS images tracked clouds at wavelength-dependent levels;
- VIMS sampled reflected and thermal structure, including 5-micron windows;
- CIRS retrieved temperature and composition over pressure ranges;
- radio tracking constrained gravity harmonics used to infer deep wind extent.

Cassini observations at different wavelengths found wind differences between
cloud levels separated by hundreds of millibars, while CIRS temperatures
provided thermal-wind constraints on vertical shear
([García-Melendo et al., 2011](https://doi.org/10.1016/j.icarus.2011.07.005)).
Saturn also has pronounced seasonal forcing, so a band observed at two epochs
need not represent the same thermal state even if its jet remains recognizable.

Gravity analyses suggest Saturn's jets extend thousands of kilometers below
the clouds, but this is an inversion of integrated gravity measurements—not a
photographed deep wind or temperature section
([Galanti et al., 2025](https://doi.org/10.1038/s41467-025-57790-x)).

## Translating the ocean heat-zone ledger

| Ocean heat-zone category | Gas-giant translation | Evidence ceiling |
|---|---|---|
| temperature zone | retrieved kinetic temperature over a pressure kernel | retrieval, not direct in-situ profile except a probe path |
| heat-content zone | enthalpy integrated through a defined pressure/mass column | rarely closed observationally; composition and depth matter |
| heat-transport zone | correlated enthalpy and velocity across a boundary | normally inferred from models and partial observations |
| transformation zone | condensation, evaporation, precipitation, convection, and compositional change | cloud appearance alone does not close latent-heat or mass budgets |
| heat source/sink | absorbed sunlight, emitted radiation, latent heating, and internal flux | top-of-atmosphere balance does not locate every interior pathway |
| transport barrier | jet and potential-vorticity gradient inhibiting meridional exchange | tracer edge is not automatically a material boundary |

The gas giants have an additional heat source absent from the ocean analogy:
substantial intrinsic heat escaping from their interiors. Earth's ocean is
heated primarily through the surface by the Sun and atmosphere, with geothermal
input comparatively small. Jupiter and Saturn combine absorbed sunlight,
internal cooling/contraction, radiation, convection, composition, and cloud
microphysics.

## What would count as a measured gas-giant heat zone?

A strong claim requires a ladder:

1. **Tracer band:** repeatable visible or spectral contrast.
2. **Pressure kernel:** documented vertical sensitivity for each channel.
3. **Temperature/composition separation:** retrieval with covariance and
   alternative opacity assumptions.
4. **Wind field:** co-located tracer velocities at a known or bounded pressure.
5. **Vertical shear:** thermal-wind consistency across pressure levels.
6. **Flux estimate:** correlated velocity and thermodynamic anomalies through a
   declared boundary.
7. **Budget:** radiation, latent heating, storage, transport, and internal flux
   reconciled within uncertainty.

Most iconic images stop at Level 1. Juno MWR and Cassini CIRS/VIMS move parts of
the problem into Levels 2–5. A global, vertically resolved heat-transport
budget comparable to Earth's best-observed ocean sections remains much harder.

## Controlled correspondences

| Shared physics | Earth ocean expression | Gas-giant expression |
|---|---|---|
| rotation redirects pressure-gradient acceleration | geostrophic currents along fronts | zonal winds along atmospheric gradients |
| thermal-wind balance | density gradients imply vertical current shear | temperature/composition gradients imply vertical wind shear |
| stratification | temperature–salinity density layers | entropy, temperature, and composition gradients |
| jet barrier | reduced exchange across ACC or boundary-current fronts | reduced meridional tracer exchange across zonal jets |
| instability and eddies | cross-front heat and tracer transport | storms, waves, and vortices exchange momentum and tracers |

## Analogy stop conditions

Stop or rewrite the comparison when:

- visible color is labeled temperature without a thermal retrieval;
- brightness temperature is treated as kinetic temperature without opacity;
- a pressure-weighted kernel is plotted as an exact geometric depth;
- cloud-tracked speed is extended downward without gravity, microwave, or
  dynamical constraints;
- a belt name is assumed to have one sign of temperature or composition at all
  pressures;
- top-of-atmosphere radiation is presented as a measured internal heat pathway;
- ocean salinity, seafloor topography, or ice-shelf mechanics is assigned a
  fictitious one-to-one gas-giant counterpart.

## Working conclusion

> A gas-giant belt becomes a heat zone only after wavelength, pressure,
> temperature, composition, velocity, and time are disentangled. The visible
> stripe is the beginning of the measurement—not the result.

The next scientific step is the [OSW prediction
set](PREDICTIONS.md),
which turns the jovicline and cross-jet leakage ideas into tests that can return
support, a regional result, non-transfer, or observationally unresolved.

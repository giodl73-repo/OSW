# OCEANREALMS — Heat Zones Are Budgets, Not Belts

**Status:** conceptual research note · observation-class synthesis

**Question:** What does it mean to call part of an ocean a “heat zone,” and how
does heat cross the fronts separating one zone from another?

## Answer in one paragraph

A heat zone is not a sealed volume of uniformly warm water. It is a region in
which heating, cooling, storage, transport, mixing, and phase change have a
distinctive balance over a stated depth and time interval. Temperature tells
how warm a sample is; heat content combines temperature with the mass of water;
heat transport measures energy crossing a boundary per unit time. Ocean fronts
often mark abrupt changes among these regimes and support fast along-front
jets, but they leak through eddies, overturning, mixing, and topographically
guided intrusions. Around Antarctica, the surface can be near freezing while a
large reservoir of warmer Circumpolar Deep Water approaches the continental
shelf from below. A surface temperature map therefore cannot by itself reveal
the heat available to melt an ice shelf.

![Heat zones are budgets, not belts](figures/heat-gates.svg)

## Five meanings that must not be collapsed

| Zone type | Defining question | Example | Required observation |
|---|---|---|---|
| temperature zone | What is the local temperature? | cold Antarctic surface water | temperature with depth and time |
| heat-content zone | How much thermal energy is stored in a volume? | a thick layer of Circumpolar Deep Water | temperature, salinity, pressure, volume, and seawater thermodynamics |
| heat-transport zone | How much heat crosses a boundary per unit time? | poleward eddy heat flux across an ACC front | velocity and temperature covariance across a section |
| heat-transformation zone | Where does water gain/lose buoyancy or change water-mass identity? | sea-ice formation and dense shelf-water production | air-sea-ice fluxes plus hydrography |
| heat-sink/source zone | Where does energy enter or leave the chosen ocean volume? | basal melting beneath an ice shelf | cavity circulation, temperature/salinity, and melt or flux constraints |

The word **zone** is incomplete unless the variable, vertical range, boundary,
and averaging period are supplied.

## The minimum heat ledger

For a pedagogical approximation with nearly constant density `rho` and heat
capacity `c_p`, the heat-content anomaly of a volume is

```text
H' = integral_V rho c_p (Theta - Theta_ref) dV
```

where `Theta` is a temperature variable suitable for heat accounting and
`Theta_ref` is a declared reference. Operational oceanography uses seawater
thermodynamics rather than assuming fresh water with exactly constant
properties; the approximation above is a scale model, not the full
[TEOS-10](https://www.teos-10.org/) calculation.

Advective heat transport through a section is schematically

```text
Q_adv = integral_A rho c_p (Theta - Theta_ref) (u dot n) dA
```

where `u dot n` is velocity normal to the section. A meaningful transport
calculation must state the section, reference convention, mass balance, depth,
and averaging interval. A warm current is not automatically a net heat source:
its contribution depends on what returns across the rest of the boundary.

The budget for a selected ocean volume can then be read as

```text
change in stored heat
  = net surface heat input
  + convergence of ocean heat transport
  + exchange with sea ice and land ice
  + unresolved/mixing terms
```

This ledger prevents four common substitutions:

- temperature is not heat content;
- heat content is not heat transport;
- a front is not an impermeable wall;
- sea-surface temperature is not the full-depth heat budget.

## Scale intuition without turning it into a forecast

Using a constant seawater density of `1027 kg m^-3`, heat capacity of
`3990 J kg^-1 K^-1`, ice latent heat of `334,000 J kg^-1`, and ice density of
`917 kg m^-3`:

| Idealized input | Integrated energy | Latent-melt energy equivalent |
|---|---:|---:|
| 1 km³ seawater cooled by 1 °C | 4.10 PJ | 0.0123 Gt or 0.0134 km³ of ice |
| 1 TW sustained for 1 day | 86.4 PJ | 0.259 Gt or 0.282 km³ of ice |
| 1 TW sustained for 365.25 days | 31,558 PJ | 94.5 Gt or 103 km³ of ice |

These are **unit conversions and upper-bound scales**, not melt predictions.
They assume the declared fraction of energy reaches ice and is spent entirely
on latent heat. Real pathways lose or redistribute heat, warm ice and water,
change circulation and stratification, and interact with geometry and stress.
The comparison nevertheless explains why a seemingly modest temperature
excess can matter when either the water volume or sustained flux is large.

The deterministic calculator and tests are in
[`analysis/heat_zone_ledger.py`](analysis/heat_zone_ledger.py) and
[`analysis/test_heat_zone_ledger.py`](analysis/test_heat_zone_ledger.py). For
example:

```powershell
python analysis/heat_zone_ledger.py --volume-km3 1 --temperature-excess-c 1
python analysis/heat_zone_ledger.py --power-tw 1 --duration-days 365.25
```

## Why the fronts persist

![How a front maintains itself and leaks](figures/front-feedback.svg)

A front is a maintained dynamical balance rather than a painted temperature
line. The causal chain begins with temperature and salinity contrasts, which
create horizontal density and pressure gradients. On a rotating planet, the
large-scale response is not simply flow from warm toward cold or high pressure
toward low pressure. Coriolis acceleration turns much of the flow along the
front in approximate geostrophic balance:

```text
f k × u_g = -(1 / rho_0) grad_h(p)
```

The horizontal density gradient also implies vertical shear through thermal-
wind balance. With `z` positive upward, the schematic vector form is:

```text
partial(u_g) / partial(z)
  = -(g / (f rho_0)) k × grad_h(rho)
```

The component signs change with coordinate convention and the sign of `f`
changes between hemispheres; the transferable point is that **a horizontal
density contrast supports a jet whose velocity changes with depth**.
Temperature alone is insufficient because salinity also changes seawater
density.

The resulting jet and sharp potential-vorticity gradient can inhibit exchange
across the front. That reduced exchange helps preserve the density contrast
supporting the jet: a positive maintenance loop. But the tilted density
surfaces also store available potential energy. Baroclinic instability releases
part of that energy into meanders and eddies, which transport heat and tracers
across the mean current and tend to flatten the density surfaces.

```text
wind + buoyancy forcing
  -> steepen density surfaces and maintain the front
  -> strengthen shear and available potential energy
  -> generate baroclinic eddies
  -> cross-front transport tends to flatten the surfaces
  -> time-varying balance between mean jet and eddies
```

In Southern Ocean theory this opposition appears in **eddy compensation**:
wind-driven overturning and eddy-induced overturning can partly oppose one
another. The compensation is not exact, and the three-dimensional exchange is
concentrated around topographic hot spots rather than distributed uniformly
around a latitude circle
([Marshall and Speer, 2012](https://doi.org/10.1038/ngeo1391);
[Bennetts et al., 2024](https://doi.org/10.1029/2022RG000781)).

This resolves an apparent contradiction. The ACC can be both a powerful
transport barrier and a major site of cross-front heat exchange. “Barrier”
describes reduced exchange relative to surrounding flow; “eddy heat flux”
describes the structured leakage that remains.

## The Southern Ocean in horizontal rings

The following is a conceptual transect, not a fixed set of latitude lines.
ACC fronts meander, split into branches, and are steered by bathymetry.

```text
equatorward

warmer subtropical regimes
  | Subtropical Front
Subantarctic zone
  | Subantarctic Front
Polar Frontal Zone and eastward ACC jets
  | Polar Front
Antarctic / subpolar surface regime
  | southern ACC fronts and subpolar gyres
Antarctic Slope Front and Slope Current
continental shelf, ice-shelf cavities, and coast

poleward
```

The Subantarctic Front and Polar Front can be traced around Antarctica, but
the ACC is a system of several deep-reaching fronts and branches rather than
one line ([Orsi et al., 1995](https://doi.org/10.1016/0967-0637(95)00021-W);
[Sokolov and Rintoul, 2009](https://doi.org/10.1029/2008JC005108)). Temperature,
salinity, density, sea-surface height, velocity, and a water-mass boundary can
all yield related but non-identical front positions.

These fronts favor rapid flow **along** the boundary and inhibit exchange
**across** it. The inhibition is dynamical, not material. Mesoscale eddies,
meanders, wind-driven overturning, and interactions with ridges transport heat
and water across the mean frontal system. Any diagram showing a solid cold ring
must therefore be read as shorthand for a leaky, moving barrier.

## The more surprising vertical stack

Near Antarctica, “cold surface over warmer deep water” is often more useful
than a warm-to-cold horizontal map:

```text
atmosphere
seasonal sea ice / open water
cold surface mixed layer
cold Winter Water remnant
warmer, saltier Circumpolar Deep Water
continental shelf troughs and ice-shelf cavities
dense shelf water and Antarctic Bottom Water pathways
seafloor
```

Here **warm** is relative. Water only a few degrees above its local freezing
point can deliver substantial heat when a large volume reaches an ice-shelf
base. Circumpolar Deep Water rises along sloping density surfaces toward the
Antarctic margin. The Antarctic Slope Front and Current can form another
barrier at the shelf break. Where that barrier is weak, or where troughs,
canyons, winds, and eddies provide routes across it, modified deep water can
flood the shelf and enter ice-shelf cavities
([Thompson et al., 2018](https://doi.org/10.1029/2018RG000624)).

The journey to Antarctic land ice therefore contains at least two distinct
gates:

```text
subtropical / global-ocean heat
  -> cross the ACC frontal system
  -> enter subpolar gyres and the Circumpolar Deep Water reservoir
  -> cross the Antarctic Slope Front and shelf break
  -> follow shelf troughs
  -> cross the ice-shelf front
  -> circulate through a sub-ice cavity
  -> transfer heat to ice at the boundary
```

Passing one gate does not guarantee passage through the next. This is why
regional bathymetry can matter as much as the circumpolar-average current.

## Where the heat actually goes

Heat delivered across the Antarctic shelf break does not remain available
indefinitely. It can be lost upward to the atmosphere, used in sea-ice change,
returned offshore, mixed into another water mass, or consumed as latent heat
while melting land ice. A recent coupled ocean–sea-ice–iceberg modeling study
estimated that land-ice melt was the largest modeled heat sink on the
Antarctic continental shelf—about 60% of heat supplied across the shelf break
in that experiment ([Moorman et al., 2026](https://doi.org/10.1126/sciadv.aec7443)).
That fraction is model- and configuration-dependent; it is not a universal
constant for every sector or climate state.

## What Drake closure would change

Closing Drake Passage would not merely slide every heat-zone boundary toward
Antarctica. It would change the circulation that creates the zones:

| Link | Likely response in a full-depth closure experiment | What remains unresolved |
|---|---|---|
| circumpolar path | continuous ACC no longer possible | strength and shape of replacement gyres |
| ACC fronts | collapse, relocate, or become basin-bound fronts | regional cross-front exchange |
| overturning | global and Southern Ocean cells reorganize | model-dependent adjustment and equilibrium |
| sea ice | substantial retreat in coupled simulations | exact regional and seasonal pattern |
| grounded ice | warmer forcing raises loss risk | magnitude, snowfall compensation, thresholds, and millennial response |

The experiment changes the container and therefore the allowed circulation
modes. It is not equivalent to turning off a refrigerator or opening a pipe of
tropical water.

## The gas-giant translation

Jupiter's and Saturn's visible belts and zones should not be read as alternating
hot and cold reservoirs. A visible band may express cloud composition, opacity,
vertical motion, wind shear, or tracer chemistry at a particular pressure
level. A jet can be a transport barrier even when the sharpest color boundary,
temperature gradient, and material boundary do not coincide.

The controlled correspondence is:

| Ocean diagnostic | Gas-giant counterpart | Shared question |
|---|---|---|
| temperature section with depth | temperature retrieval with pressure | where is the thermal gradient? |
| salinity/temperature water-mass tracer | molecular/cloud tracer | what identifies the sampled fluid? |
| velocity across a front | cloud-tracked winds across a jet | how strong is the shear? |
| eddy heat flux | correlated temperature/tracer and velocity fluctuations | what crosses the mean jet? |
| bathymetric gateway | no direct cloud-level equivalent | which boundary condition permits or forbids a closed path? |

The last row is deliberately asymmetric. Gas giants help reveal what a fluid
can do without continents; Earth reveals what walls, gateways, and seafloor
topography add.

## Measurement ladder

A claimed heat zone becomes progressively stronger evidence as these levels
are satisfied:

1. **Map:** a repeatable temperature or tracer contrast is observed.
2. **Section:** its vertical structure and water masses are measured.
3. **Velocity:** the along-zone jet and cross-zone motion are constrained.
4. **Covariance:** transient eddy or turbulent heat flux is estimated.
5. **Budget:** storage change, boundary transports, and surface/ice fluxes close
   within uncertainty.
6. **Mechanism:** a model or natural experiment predicts how the budget changes
   when wind, geometry, stratification, or forcing changes.

A colored surface map reaches Level 1. It does not by itself show a heat
reservoir, barrier strength, or ice-melt pathway.

## Stop conditions

Reject or rewrite a “heat zone” claim when any of the following occurs:

- no depth or time interval is declared;
- temperature is used as a proxy for integrated heat without a volume;
- a mean front is treated as a material wall;
- surface cold is used to infer the absence of subsurface heat;
- a modeled sea-ice response is reported as a simulated grounded-ice response;
- a gas-giant color band is called a thermal zone without a pressure-sensitive
  temperature retrieval.

## Working conclusion

> Heat zones are dynamically maintained budget regimes. Their boundaries guide
> flow more strongly than they stop it, and their most consequential heat may
> be hidden vertically rather than visible at the surface.

The [OSW prediction
set](PREDICTIONS.md)
now registers vertical-identity, leakage-hot-spot, freshwater-hidden-heat, and
jovicline-mechanism tests with valid negative and unresolved outcomes.

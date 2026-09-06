# Seafloor, Coasts, and Topographic Steering

*The seafloor is comparatively fixed. The circulation it constrains is not.*

## Object cards

| Object | Defined by | Typical geometry | What it can constrain |
|---|---|---|---|
| Shelf | shallow submerged continental margin | broad surface | coastal exchange, tides, mixing, habitats |
| Slope | descent from shelf toward deep ocean | inclined surface | boundary currents, fronts, cross-slope exchange |
| Rise | sedimented transition below many slopes | broad incline | deep pathways and deposition |
| Ridge | elongated seafloor high | line-like crest and flanks | deep connection, steering, wave generation |
| Sill | shallowest controlling part of a passage | crest across a channel | maximum connected depth and overflow structure |
| Trench | long, narrow deep depression | trough | abyssal pathways and plate-boundary setting |
| Seamount | isolated or grouped seafloor high | 3-D peak | local wakes, mixing, deflection, habitats |
| Canyon/trough | incised cross-slope depression | channel | focused cross-shelf pathways |

GEBCO and the IHO maintain governed terminology and a digital gazetteer for
named undersea features
([GEBCO Undersea Feature Names](https://www.gebco.net/data-products/undersea-feature-names)).
OSW should reuse those names and types rather than invent replacements.

## Relief is nested

```text
coast       shelf        slope          rise       abyssal plain       ridge
  │     ____________
  │____/            \                                      /\
                    \                                    /  \
                     \__________                ________/    \_______
                                \______________/
           canyon cuts across slope                 sill crosses passage
```

A global physiographic class, a named feature, and a gridded depth value are
three different records. The class “continental slope” describes a landform
family; a named canyon identifies one member; a bathymetric raster supplies
estimated elevation at cells. None alone tells us the velocity or heat flux.

## Three meanings commonly hidden inside “gate”

```text
NATURAL LANDFORM        DYNAMIC CHOKE POINT       MEASUREMENT SECTION

ridge + passage    →    flow constrained by  →   analyst chooses faces
fixed terrain           depth and width            and sign convention

What exists?            What does it do?            What crosses it?
```

- A **passage** or **sill** is physical geometry.
- A **choke point** is an interpretation that geometry materially constrains a
  process under specified conditions.
- A **gate** is a declared surface used to measure flux.

They may coincide, but not automatically. A poorly placed gate can cut across
land, miss a branch, or measure a different domain from the named passage.

## How topography steers without dictating

Rotation, stratification, pressure gradients, friction, and time dependence
all matter. Topography enters by changing water-column thickness, blocking some
depth classes, guiding boundary currents, generating waves and turbulence, and
concentrating exchange near ridges, sills, and canyons.

```text
deep current approaches ridge
             ───────►      /\
                          /  \
          blocked below sill  ├── deflected along contours
          connected above     ├── accelerated through passage
                              └── mixed / wave-radiating wake
```

The result is conditional. The same ridge can steer one density layer, permit
another to cross, and produce intermittent eddy exchange. Bathymetry is a
boundary condition, not a complete circulation solution.

## Four examples

- **Greenland–Scotland Ridge:** sills and passages organize exchanges between
  the Nordic Seas and North Atlantic; dense overflows and upper Atlantic inflow
  occupy different vertical structures.
- **Drake Passage and Scotia Arc:** the opening permits circumpolar connection,
  while ridges and fracture zones steer fronts and concentrate interactions.
- **Indonesian seas:** multiple narrow, shallow passages and sills create a
  branched, vertically structured throughflow that coarse surface maps cannot
  represent adequately.
- **Antarctic margin:** shelf-break fronts inhibit exchange, while troughs,
  canyons, winds, and eddies can help modified deep water reach continental
  shelves and ice-shelf cavities
  ([Thompson et al. 2018](https://doi.org/10.1029/2018RG000624)).

## The decisive tests

1. Identify the bathymetric product, version, vertical datum, grid, and uncertainty.
2. Separate terrain class, named feature, dynamic role, and measurement section.
3. Test whether represented wet cells are actually connected at the relevant depth.
4. Resolve sill depth, passage width, partial cells, masks, and section orientation.
5. Compare flow along and across depth contours through time and depth.
6. Challenge the gate path and endpoints instead of treating one line as canonical.
7. Measure transport before claiming that terrain blocks or delivers heat.

## OSW examples

The Nordic control volume was not closed by drawing five familiar place names.
It required a flood-filled wet-cell interior and 284 unique native faces, each
separating inside from outside. Fram Strait contributes 814 of the resulting
1,816 km² full-depth boundary area and is the only section with most area below
700 m.

[Open the Nordic geometry audit](../figures/osw-m4-oras5-nordic-section-geometry.svg)
and [inspect its receipt](../research/osw-m4-oras5-nordic-section-geometry-audit.json).

The Indonesian audit failed at coarse resolution for Lombok and Ombai before
any transport was calculated. A finer HYCOM sample improved wet vertical
support, but collocated standard-grid profiles still did not become native-face
transport geometry.

[Compare the Indonesian grids](../figures/osw-m3-indonesian-grid-bakeoff-2018.svg)
and [inspect the bakeoff receipt](../research/osw-m3-indonesian-grid-bakeoff-2018.json).

## Planetary boundary

Solid coasts, sills, and shallow bathymetry have no direct counterpart in a gas
giant's visible weather layer. Earth therefore teaches how fixed boundaries can
interrupt longitude, create gateways, and steer particular depths; gas giants
help expose the jet-forming behavior of a rotating fluid without that shallow
ocean-floor geometry. This is a boundary-condition contrast, not evidence that
the remaining dynamics are otherwise identical.

[Compare the two systems](07-OCEANS-AND-GAS-GIANTS.md).

## Common mistakes

- Treating the coastline as the only solid boundary that matters.
- Assuming the deepest charted point is the controlling sill depth.
- Inferring current direction solely from the orientation of a trench or ridge.
- Calling every narrow passage a closed or controlling heat gate.
- Using a global bathymetric grid beyond its effective local resolution.
- Equating geometric connectivity with actual water-mass or heat transport.
- Forgetting that ice-shelf cavities add moving and poorly observed boundaries.

## Next

[Waves, Tides, and Oscillations](../CLASSIFICATION.md#next-research-layers) will
separate energy propagation and periodic motion from bulk water transport.

[Field Guide index](README.md) · [Gates, Transports, and Relays](04-GATES-TRANSPORTS-AND-RELAYS.md) · [Classification](../CLASSIFICATION.md)

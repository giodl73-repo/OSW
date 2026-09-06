# Water Masses and Layers

*A water mass is not merely water in one place. It is water recognized by a
combination of properties and history.*

## Object card

| Attribute | Water mass |
|---|---|
| Defined by | ranges or structure in temperature, salinity, density, oxygen, tracers, and sometimes origin |
| Geometry | a three-dimensional, deforming volume; often disconnected in geographic space |
| Boundary | a surface in property space, mapped back into geographic depth and location |
| Lifetime | months to centuries depending on formation and mixing |
| Carries | heat, salt, carbon, oxygen, nutrients, and history |
| Does not require | all of its water to move in the same direction |

## Geographic space and property space

```text
GEOGRAPHIC SECTION                         PROPERTY SPACE

surface  warm Atlantic layer              salinity
────────████████████──────                 high ┤   Atlantic Water
        █████████████  front                    │      ● ● ●
        ───────────────                        │   ● ●
        cold intermediate water                │
        ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒                        │ ● Polar Water
deep    dense overflow water               low └────────────── temperature
        ████████████████                         cold       warm
```

On a map, one water mass can appear in several patches. In temperature–salinity
space those patches may form one recognizable family. That is why a water-mass
atlas cannot be only a flat political-style map.

## Layers are different

A layer is usually defined vertically:

- the mixed layer is stirred enough to have relatively uniform properties;
- the thermocline has a strong vertical temperature gradient;
- the halocline has a strong salinity gradient;
- the pycnocline has a strong density gradient;
- an isopycnal layer lies between selected density surfaces.

A water mass may occupy several layers, and a layer may contain several water
masses. “Deep water” is therefore not automatically one water mass.

## Examples

- **Atlantic Water:** comparatively warm and saline water entering the Nordic
  Seas and Arctic through multiple branches.
- **Polar Surface Water:** colder, fresher upper water shaped by ice, freshwater,
  and surface forcing.
- **Denmark Strait Overflow Water:** dense outflow crossing the Greenland–Scotland
  Ridge and contributing to North Atlantic deep waters.
- **Mode water:** a thick low-potential-vorticity water mass produced by repeated
  winter mixing and subduction.

## The decisive tests

1. Declare the variables and thresholds used to identify the mass.
2. Show the object in temperature–salinity or density coordinates.
3. Map its three-dimensional geographic occupancy.
4. Test sensitivity to thresholds and season.
5. Distinguish volume present from volume transported.

The modern water-mass-transformation framework describes conversion as volume
flux between property classes. See [Chen et al. 2025](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2025JC022445)
and the Arctic temperature/salinity budget formulation in
[Lambert et al. 2019](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2017JC013704).

## Common mistakes

| Mistake | Correction |
|---|---|
| A warm color patch is a water mass. | It is a candidate until salinity, density, depth, and continuity are tested. |
| A water mass is a current. | Properties define the mass; velocity defines the current. |
| Every molecule belongs to exactly one permanent mass. | Mixing and threshold choices create transition zones and changing membership. |
| A deep gateway carries deep heat. | Geometry permits transport; measured velocity and temperature determine where heat crosses. |

## OSW example

Our Nordic depth matrix shows +148.8 TW of boundary convergence above 700 m but
−9.0 TW below, even though Fram Strait extends beyond 2,500 m. The result is a
transport statement by depth, not yet a formal water-mass classification.

[Open the depth matrix](../figures/osw-m4-oras5-nordic-heat-exchange-depth-2018.svg).

## Next

[Fronts, Jets, and Bands](02-FRONTS-JETS-AND-BANDS.md) explains what happens where
property fields meet velocity structure.

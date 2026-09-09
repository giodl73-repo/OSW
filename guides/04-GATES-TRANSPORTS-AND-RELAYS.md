# Gates, Transports, and Relays

*A gate is a measuring surface. A current may cross it, turn beside it, or cross
twice in opposite directions.*

## Object cards

| Object | Definition |
|---|---|
| Gate | declared vertical section across which flux is integrated |
| Face | smallest native model-grid element of that gate |
| Branch | contiguous or property-defined subset of transport |
| Control volume | closed room whose storage and boundary exchanges can be balanced |
| Relay | region receiving, transforming, storing, and exporting a transported property |

## From arrow to measurement

```text
                    VERTICAL GATE
surface  ─────────────────────────────────────
 warm inflow  →→→  │ +u × T × face area │
 return flow  ←←←  │ -u × T × face area │
 deep water   ←──  │ -u × T × face area │
bottom   ─────────────────────────────────────

Volume transport = Σ(normal velocity × wet face area)
Heat transport   = ρCp Σ(normal velocity × wet face area × temperature anomaly)
```

Velocity alone is not transport. Temperature alone is not heat transport. A
valid section needs normal velocity, wet width, vertical thickness, mask,
orientation, and an explicit heat reference.

The second expression is a **reference-dependent advective heat transport**.
Changing the reference temperature changes an individual open-gate value by
`ρCp × volume transport × reference-temperature change`. It does not change a
closed control-volume convergence when the volume budget closes consistently.
Therefore OSW must report the reference temperature and volume closure beside
every heat-transport comparison. Native model tracer fluxes can also contain
covariance, diffusion, and parameterized terms that monthly mean `u × T` omits.

## Why opposite flows matter

A gate total is often the small difference between much larger inward and
outward branches:

```text
gross inward heat     +363 TW
gross outward heat    -223 TW
                      -------
net convergence       +140 TW
```

This is not wasted detail. Warm inflow and cold outflow can produce heat import
even when the net volume points outward; the reverse is also possible.

## The control-volume relay

```text
                        atmosphere
                           ▲ heat loss
                           │
Atlantic input ─────► [ NORDIC ROOM ] ─────► Arctic export
                           │
                           ├── storage change
                           ├── mixing/transformation
                           └── unresolved/native model terms
```

For a fixed volume, a schematic heat account is:

```text
storage tendency = boundary convergence + surface input + internal/unresolved terms
```

## OSW example

Our 2018 upwind sensitivity resolves +260.4 TW through three southern gates,
−120.4 TW through Fram and Norway–Svalbard, −107.6 TW at the surface, +26.5 TW
storage tendency, and −5.8 TW unresolved.

[Open the relay](../figures/osw-m4-oras5-nordic-heat-relay-2018.svg) and
[inspect the receipt](../research/osw-m4-oras5-nordic-heat-relay-2018.json).

The same-month correlation between southern input and northern export is 0.81,
but twelve seasonal values cannot supply parcel travel time. A relay is a budget
architecture, not a claim that the same molecule crossed the room that month.

## The decisive tests

1. Does every gate face separate inside from outside?
2. Are signs oriented consistently?
3. Is volume closure evaluated before heat interpretation?
4. Are inward and outward branches retained?
5. Does the storage method match the time support of the fluxes?
6. Are omitted mixing, ice, diffusion, and assimilation terms named?

## Common mistakes

- Drawing a line that does not reach represented land and calling the room closed.
- Comparing heat transports with different reference temperatures without checking volume closure.
- Treating monthly mean `velocity × temperature` as the model's native nonlinear tracer flux.
- Interpreting a small remainder as proof that every physical process is resolved.
- Reading correlation as transit time.

## Next

[Transformation and Overturning](05-TRANSFORMATION-AND-OVERTURNING.md) explains
how water changes class while it passes through the relay.

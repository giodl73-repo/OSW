# Eddies, Filaments, and Barriers

*Some ocean objects are defined less by what they look like now than by what
their water does over time.*

## Object cards

| Object | Practical definition | Principal risk |
|---|---|---|
| Eddy | rotating mesoscale feature detected from height, velocity, vorticity, or trajectories | different detectors find different boundaries |
| Coherent set | region whose contents mix relatively little with surroundings over a chosen interval | coherence depends on interval and data |
| Transport barrier | moving curve/surface across which exchange is small | a snapshot front may not be material |
| Filament | elongated tracer or property structure produced by stretching | visual shape can outlive material coherence |
| Recirculation | flow that turns back toward its source or loops within a region | not necessarily a closed eddy |

## Eulerian versus Lagrangian seeing

```text
SNAPSHOT (Eulerian)                 TRAJECTORIES (Lagrangian)

velocity now:                       water over time:
↗ ↑ ↖                               ┌──────── barrier ────────┐
→ ○ ←       looks rotational        │  ↻ trapped trajectories │
↘ ↓ ↙                               └─────────────────────────┘

Question: what is happening here?   Question: what stays together?
```

Sea-surface-height contours and vorticity give useful instantaneous eddy
detectors. Lagrangian coherent structures and transfer operators instead ask
how trajectories separate, converge, or remain together. They can reveal a
“hidden dynamical skeleton” that is not obvious in a velocity snapshot.

[Beron-Vera et al. 2008](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2008GL033957)
showed that Lagrangian structures delineate domains with different advective
properties. [Froyland et al. 2007](https://doi.org/10.1103/PHYSREVLETT.98.224503)
used transfer operators to detect coherent surface-ocean regions.

## Scale and lifetime are part of the name

An “eddy” without a detection method and time interval is incomplete metadata.
An object can be coherent for ten days but leaky over six months. A surface
eddy may not retain water at depth. A visually circular feature may rotate
without translating its contents very far.

```text
formation ───── coherent interval ───── leakage/merger ───── decay
   t0                 t1–t2                    t3               t4

The object's boundary is a spacetime claim, not permanent geography.
```

## Examples

- Gulf Stream warm- and cold-core rings;
- Agulhas rings shed into the South Atlantic;
- Fram Strait Atlantic Water recirculation;
- Southern Ocean eddies interacting with circumpolar fronts;
- tracer filaments stretched around eddy edges.

Mesoscale eddies are prominent upper-ocean structures and can contribute to
heat-flux convergence and marine heatwave evolution
([Vogt et al. 2023](https://www.nature.com/articles/s41467-023-38811-z)).

## The decisive tests

1. Declare Eulerian or Lagrangian definition.
2. Declare spatial resolution and time interval.
3. Track boundary survival, leakage, splitting, and merger.
4. Compare at least two defensible detectors.
5. Validate with drifters, floats, tracers, or independent observations where possible.

## Common mistakes

- Inferring material transport from a circular sea-surface-height contour alone.
- Assuming a front is an impermeable barrier.
- Calling a simulated particle path a measured current.
- Treating the same eddy ID as meaningful after splitting or merger.
- Assuming surface coherence extends through the water column.

## OSW connection

Our present Nordic “jet runs” are Eulerian connected components on a boundary.
They are not coherent sets. Proving that their water stays together would require
time-resolved 3-D trajectories or a transfer-operator experiment. This is an
important future distinction, not a wording detail.

## Next

[Gates, Transports, and Relays](04-GATES-TRANSPORTS-AND-RELAYS.md) changes the
question from recognizing a structure to measuring what crosses a boundary.

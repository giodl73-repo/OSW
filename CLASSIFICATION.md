# Classifying Ocean Objects

**Status:** OSW working classification v0.1 · research-grounded teaching schema,
not a replacement for scientific controlled vocabularies

The ocean does not divide into one natural stack of kingdoms, nations, and
states. A water mass, front, current, marine heatwave, seafloor ridge, and
measurement gate are different *kinds of claims*. They can overlap at the same
place without contradiction.

OSW therefore classifies every term on two primary axes.

## Axis A — what kind of thing is it?

| Type | Meaning | Example |
|---|---|---|
| Material body | water recognized by composition, properties, or source | Atlantic Water, river plume |
| Layer/interface | vertically or materially organized surface or stratum | mixed layer, thermocline |
| Gradient boundary | edge diagnosed from rapid spatial change | front, plume edge |
| Contact boundary | physical transition between touching material regimes | grounding line |
| Flow structure | organized pattern in velocity | current, jet, gyre, eddy |
| Connectivity structure | relation revealed by trajectories over time | coherent set, transport barrier |
| Flux/budget construct | geometry declared to measure exchange or storage | gate, control volume, relay |
| Process | change, conversion, or transfer rather than a bounded object | mixing, subduction, overturning |
| Event/classified state | time-dependent condition meeting a rule | marine heatwave, bloom, seascape class |
| Reference geography | indexing region defined by convention or classification | basin, Longhurst province |
| Substrate feature | comparatively fixed solid boundary geometry | shelf, ridge, canyon |
| Wave/oscillation | propagating or periodic disturbance | swell, tide, internal wave |
| Phase/cover object | non-liquid phase or cavity that alters ocean boundaries | sea ice, polynya, ice-shelf cavity |

## Axis B — what makes us recognize it?

```text
property signature ───── water mass, plume
vertical structure ───── mixed layer, thermocline
horizontal gradient ──── front, ice edge
velocity pattern ─────── current, jet, gyre, eddy
trajectory relation ──── coherent set, barrier, pathway
section integral ─────── gate, branch, flux
closed budget ────────── control volume, relay
conversion rate ──────── transformation, formation
anomaly/event rule ───── heatwave, cold spell, bloom
classifier/convention ── seascape, province, basin
terrain geometry ─────── shelf, ridge, canyon
frequency/phase ──────── wave, tide, oscillation
phase fraction ───────── sea-ice cover, polynya
```

This second axis is the object's **identity test**. Two objects that look alike
can be different if they pass different tests. One object can also receive
secondary tests without changing its primary type.

## Why the matrix beats one tree

```text
                         SAME OCEAN LOCATION
                                  │
             ┌────────────────────┼────────────────────┐
             ▼                    ▼                    ▼
       material claim       motion claim          event claim
       Atlantic Water       current core          heatwave pixel
             │                    │                    │
       property test        velocity test        anomaly test
```

A tree would make those three labels compete for one parent. The matrix lets
them overlap while preserving what evidence each label requires.

## The v0.1 registry

The machine-readable [object registry](research/ocean-object-classification.csv)
contains **110 core terms across 13 types**. Its companion
[relationship registry](research/ocean-object-relations.csv) records 107 explicit
connections among those terms. One hundred ten is an editorial coverage count, not a
claim that nature contains exactly 110 ocean objects. New terms can be added
only when their primary type, identity test, geometry, time behavior, coverage,
mobility, evidence status, and external anchor are declared.

## Classification is also a graph

Types tell us what an object *is*. Relations tell us how ocean objects work
together.

```text
water mass ──carried by──► current ──measured across──► gate
    ▲                         │                           │
    │                         └──often follows──► front  ├──bounds──► control volume
 transformed by                                   ▲     │
    │                                             │     └──supports──► relay
  mixing ◄────────── eddy ───────reshapes────────┘

ridge / shelf / canyon ─────────steers or channels────────► flow
```

Every relationship carries a qualification and status. `established` means the
relation is a standard scientific use; `qualified` means it is common but not
necessary or universal; `osw_construct` marks a local analytical connection.
The graph therefore never turns “often coincides with” into “is identical to.”

The registry deliberately includes three things that are often left out:

1. **Fixed constraints:** shelves, slopes, ridges, trenches, and canyons shape
   the moving ocean but do not move with it.
2. **Non-advective motion:** waves and tides can move energy or phase without
   transporting the same body of water across a basin.
3. **Measurement constructs:** a gate or control volume is drawn by an analyst;
   it is not a naturally bounded water mass.

## Coverage is a separate promise

An object type does not automatically tile the ocean.

| Coverage value | Meaning |
|---|---|
| `exhaustive` | every valid cell receives one membership under this declared rule |
| `partial` | objects occupy some of the domain; ordinary water remains outside |
| `event_only` | membership exists only while an event rule is met |
| `sparse` | discrete named or detected features occur within a wider background |
| `construct_only` | geometry exists because an analysis declares it |

Only an exhaustive layer can behave like a complete state map. Longhurst
provinces can do that under their ecological reference rule. Eddies, fronts,
heatwaves, gates, and plumes cannot—and should not be padded until they do.

## Interoperability boundary

OSW's role is to connect concepts for readers and maps. It should reuse or map
to governed identifiers wherever possible:

- [CF Standard Names](https://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html) for measured variables and units;
- [NERC Vocabulary Server](https://vocab.nerc.ac.uk/) for marine terms and instruments;
- [Marine Regions](https://marineregions.org/ontology/documentation.html) and
  SeaVoX for named water bodies and spatial relations;
- [GEBCO](https://www.gebco.net/data-products/undersea-feature-names) and IHO
  terminology for named undersea features;
- [GOOS Essential Ocean Variables](https://goosocean.org/what-we-do/framework/essential-ocean-variables/)
  for observation requirements.

An `OSW local` anchor means a teaching or analytical construct, not a newly
discovered natural class.

## Next research layers

The classification has exposed six guide chapters cleanly:

1. ~~seafloor, coasts, and topographic steering~~ — now [Guide 08](guides/08-SEAFLOOR-COASTS-AND-TOPOGRAPHIC-STEERING.md);
2. ~~waves, tides, and oscillations~~ — now [Guide 09](guides/09-WAVES-TIDES-AND-OSCILLATIONS.md);
3. ~~plumes, upwelling, and vertical exchange~~ — now [Guide 10](guides/10-PLUMES-UPWELLING-AND-VERTICAL-EXCHANGE.md);
4. ~~sea ice, polynyas, and ocean cavities~~ — now [Guide 11](guides/11-SEA-ICE-POLYNYAS-AND-OCEAN-CAVITIES.md);
5. ~~biological and chemical objects carried and transformed by the physical ocean~~ — now [Guide 12](guides/12-LIFE-OXYGEN-NUTRIENTS-AND-CARBON.md);
6. a compact visual matrix and decision path across the complete registry.

Those chapters should refine the existing registry rather than create a second
list of terms.

## Evidence

See the [classification web-grounding record](signals/discover/websearch/ocean-object-classification-websearch-2026-09-05.md)
and the [Field Guide to Ocean Objects](guides/README.md).

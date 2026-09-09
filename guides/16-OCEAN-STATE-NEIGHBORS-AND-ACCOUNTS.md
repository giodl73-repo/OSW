# Ocean-State Neighbors and Accounts

An ocean state does not need a wall around it to have useful neighbors.

OSW uses source-backed provinces as stable geographic reference units. Water,
heat, salt, organisms, and anomalies may cross their edges. That permeability
is not a defect: it is what lets us ask how the states interact and how their
condition changes over time.

## Three different statements

```text
SHARED EDGE          MOTION SCREEN          MEASURED EXCHANGE
two polygons touch   velocity crosses or    volume or tracer flux is
along a line         follows that edge      integrated through a section
```

The first statement is geometric. The second describes a velocity field. The
third requires compatible three-dimensional velocity, grid metrics, layer
thickness, masks, time support, and—when heat is involved—temperature and a
reference convention. None can silently stand in for the next.

## What the first graph found

The revised Longhurst 2007 Version 4 source contains 54 separately backed
province geometries. Exact post-repair boundary intersection produces:

- **54 nodes**;
- **128 shared linear edges**;
- **10 point-only contacts**, retained but rejected as graph edges;
- degrees from **1 to 11**, with a mean of **4.74 neighbors**; and
- **127 of 128** source edges visible as neighboring assigned cells at the
  0.25° display resolution.

The exception is the short `CNRY--MEDI` source edge: its roughly 17 km encoded
shared boundary is real in the source geometry but disappears from the sampled
cell-neighbor diagnostic. The graph therefore comes from polygon topology, not
from colored pixels.

[Open the workbench](../column/) and choose **Neighbors**, or inspect the
[machine-readable graph](../research/longhurst-2007-province-adjacency.json),
[rejected contacts](../research/longhurst-2007-province-adjacency-rejected.json),
and [source receipt](../research/longhurst-2007-province-adjacency-source-receipt.json).

## Reading a border passport

Each accepted edge records its two states, spherical shared-edge length,
source intersection type, and whether the 0.25° display grid contains adjacent
cells. Its physical class remains `undetermined_reference_edge`.

That deliberately does **not** tell us whether the edge is:

- a front or current;
- a barrier or retention boundary;
- a strait, sill, or transport gateway;
- a place of large or small exchange; or
- coherent from surface to seabed.

Those are later measurements.

## From five bins to a state silhouette

The first continuous-hypsometry prototype freezes six method archetypes before
examining their new curves: `SUND`, `NADR`, `SPSG`, `ANTA`, `NPPF`, and `NECS`.
Every curve gives the sampled seafloor depth at each area-weighted percentile.

Two examples show why this matters:

- `NECS` has a 66 m median sampled seabed and 90.2% of its sampled wet area is
  shallower than 200 m.
- `NPPF` is so deep that even its 10th-percentile sampled seabed is 4,261 m;
  its median is 5,349 m.

The 0.5° center screen changes mean depth by less than 30 m in each of the six
prototypes, but coastal shelf fraction and local quantiles can still shift.
This is one declared resolution comparison, not a complete uncertainty model.

[Inspect the prototype](../research/longhurst-2007-province-continuous-hypsometry-prototype.json)
and its [source receipt](../research/longhurst-2007-province-continuous-hypsometry-source-receipt.json).

## The accounting analogy

Economic geography distinguishes what exists inside a reference area from what
crosses its boundary and how the balance changes. OSW can borrow that grammar
without turning ocean provinces into countries:

| Account | Ocean example | Do not confuse it with |
|---|---|---|
| Inventory | heat, freshwater, oxygen, or volume inside a declared province × depth address | transport |
| Flow | inward, outward, gross, and net section transport | a map of temperature |
| Change | inventory tendency over a matched interval | a causal explanation |
| Balance | compatible inventory, boundary, surface, and other terms | automatic closure |
| Relationship | leading source/destination neighbors and lag | proof of causal delivery |
| Shock | marine heatwave, freshwater pulse, ice event, or circulation disruption | permanent state identity |
| Revision | recalculation under a newer edition or method | silent replacement of history |

Every account needs valid time, acquisition time, geometry and method versions,
source identity, units, spatial and vertical support, coverage, uncertainty or
sensitivity, and revision lineage. Missing values remain missing.

## What happens next

After the adjacency and depth foundation is reviewed, the first exchange pilot
will be selected by a rule frozen before transport results are inspected. The
rule favors source custody, audited native-grid geometry, compatible vertical
and seasonal support, and strong controls—not dramatic or attractive outcomes.

Read the [pilot-selection rule](../plans/ocean-state-exchange-pilot-selection.md).
Passing that rule authorizes a method test, not a conclusion that the selected
border is physically real.

## Common mistakes

- Treating point contact, proximity, or neighboring raster cells as a shared
  source edge.
- Treating a shared source edge as a wall, gateway, or measured interaction.
- Comparing inventories across dates after silently changing geometry, grid,
  mask, depth, or method.
- Calling temperature an inventory of heat or calling crossing velocity heat
  transport.
- Filling an unsupported state or date to make the accounting table complete.
- Choosing the first exchange pilot because its preliminary result looks
  dramatic or supports a preferred zoning.

## Keep the language honest

- Say **neighboring reference states** after a shared-edge test.
- Say **crossing velocity** only after declaring depth and time support.
- Say **volume transport** only after integrating compatible normal velocity
  and face area.
- Say **heat transport** only after adding a declared thermal convention.
- Say **balance** only when the terms share a control volume and time basis.
- Keep **unknown** when the evidence cannot make the next distinction.

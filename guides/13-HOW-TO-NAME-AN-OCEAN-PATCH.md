# How to Name an Ocean Patch

*Begin with what was measured. Earn the noun afterward.*

**Evidence class:** this is a decision aid generated from OSW's editorial
classification. It is not a detected world map, natural hierarchy, or scientific
standard.

[Open the visual matrix](../figures/osw-ocean-object-matrix.svg) ·
[inspect its machine summary](../research/ocean-object-matrix-summary.json) ·
[read the design contract](../plans/ocean-object-visual-matrix.md)

## The five-step ladder

```text
1 MEASURE       property · velocity · phase · terrain
      ↓
2 ORGANIZE      body · layer · boundary · flow
      ↓
3 CLASSIFY      event · state · reference geography
      ↓
4 INTEGRATE     pool · storage · control volume
      ↓
5 CROSS         boundary flux · transport
```

The ladder is not a mandatory sequence for every study. It prevents a common
shortcut: treating a measured value as though it already proves a bounded
object, an event, an inventory, or transport.

## Start with the measurand

```text
What produced the mark, line, region, or colour?
├── property/composition ─► body, layer, boundary, or event?
├── velocity/trajectory ──► flow or connectivity structure?
├── repeating phase ──────► wave or oscillation?
├── terrain/contact ──────► substrate or contact boundary?
├── fractional cover ─────► phase/cover object?
└── integral over geometry
    ├── amount inside volume ─► pool/storage
    └── crossing per time ────► flux/transport
```

Then declare geometry, time support, coverage promise, mobility, evidence
status, uncertainty, and counterexample.

## The 13 primary types

| Type | Decisive question | Examples |
|---|---|---|
| Material body | Which water or material is this? | water mass, plume, phytoplankton community |
| Layer/interface | How is it organized vertically? | mixed layer, thermocline, oxygen minimum zone |
| Gradient boundary | Where does a property change rapidly? | front, plume edge, ice edge |
| Contact boundary | Where do touching material regimes change? | grounding line |
| Flow structure | Which organized velocity pattern exists? | current, jet, eddy, upwelling |
| Connectivity structure | What remains connected over time? | coherent set, barrier, pathway |
| Flux/budget construct | What is integrated within or across geometry? | gate, control volume, DIC pool, CO₂ flux |
| Process | What changes, converts, or transfers? | mixing, transformation, production, basal melt |
| Event/classified state | Which rule is met now? | heatwave, hypoxia, bloom, surge |
| Reference geography | Which indexing convention applies? | basin, province, realm |
| Substrate feature | Which solid terrain constrains flow? | shelf, ridge, sill, canyon |
| Wave/oscillation | Which phase or frequency propagates or repeats? | tide, swell, Rossby wave, seiche |
| Phase/cover object | What covers, opens within, or roofs the ocean? | sea ice, lead, polynya, ice shelf |

The type is primary, not exclusive. A current may carry a material body; a
front may bound it; an event may overlay both; and a gate may measure what
crosses them.

## The identity-test matrix

The lower field of the SVG places a dot where at least one registry object uses
an identity test as its primary test. Sparse rows are informative: terrain
geometry identifies substrate and contact/cover objects, spectral phase
identifies waves, trajectory coherence identifies connectivity, and section or
inventory integrals identify budget constructs.

Dots do **not** encode abundance, area, certainty, importance, or every possible
secondary test. Counts describe this version of the registry only.

## Worked examples

### An orange patch in SST

It begins as a temperature field. A marine heatwave requires a baseline,
percentile/threshold, duration, and spatial rule. A warm water mass requires a
three-dimensional property signature. Heat content requires depth integration.
Heat transport additionally requires velocity and boundary geometry.

### A green surface patch

Ocean colour can estimate chlorophyll. A phytoplankton community needs abundance
and composition evidence; production is a rate; a bloom needs a time-dependent
accumulation rule; harmfulness needs toxin, mortality, nuisance, or impact
evidence.

### A white polar region

Sea-ice concentration is fractional cover. Extent applies a threshold; thickness
and volume need other measurements. A lead or polynya needs opening geometry and
time behavior. An ice shelf is land-origin floating ice roofing a liquid cavity.

### An arrow through a strait

An arrow may schematize a current, but measured transport requires section
orientation, velocity normal to the section, wet area, units, time support, and
provenance. Reference-relative heat transport also needs temperature and a
declared reference.

## Crossing to another world

The grammar can organize comparison with an atmosphere or gas giant, but an
Earth-ocean name does not transfer merely because two images have similar
bands, spots, or colours. First compare the observable, forcing,
stratification, rotation, depth, compressibility, boundaries, and sampling
method. Then state which mechanism is analogous and which resemblance remains
only visual. [Guide 07](07-OCEANS-AND-GAS-GIANTS.md) develops that test.

## Common mistakes

- Naming an object from colour or shape alone.
- Treating a primary type as the only relation an object can have.
- Reading registry counts as natural frequency or importance.
- Assuming a missing dot means a combination is physically impossible.
- Calling partial objects an exhaustive partition of the ocean.
- Mixing observed representation, scientific status, and object type.
- Skipping geometry, time, scale, threshold, uncertainty, or counterexample.

## Use the full system

The [Field Guide index](README.md) provides the domain chapters. The
[classification](../CLASSIFICATION.md) defines the facets. The
[object registry](../research/ocean-object-classification.csv) and
[relation graph](../research/ocean-object-relations.csv) are the machine-readable
sources behind this overview.

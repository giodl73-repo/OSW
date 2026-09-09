# Ocean-State Exchange Research Program

Status: Stages 0-6 complete; Stage 7 implemented and at its native role gate;
final repository audit pending

Date: 2026-09-08

Source baseline: `80a18986a1913558a52021571a0e560a86276b8e`

## Active bounded goal

Test whether source-backed ocean provinces provide useful reference units for
describing ocean structure and exchange by building a reproducible
province-adjacency graph, continuous depth fingerprints, hydrographic
inventories, and velocity-weighted boundary diagnostics, while treating
merge, split, move, demote, and retain as equally valid outcomes.

The owner first activated the bounded slice, then explicitly set completion of
this full plan as the active goal on 2026-09-08. Stages 3-7 may therefore
advance only in order through their declared evidence and native-role gates.
This does not authorize publication, promotion, an unreviewed zoning change,
or claims wider than the admitted sources.

## Why this is the next question

OSW can now describe two parts of an ocean address with source-aligned evidence:

- **where:** 54 revised Longhurst 2007 Version 4 province footprints;
- **how much geometric capacity:** spherical wet area and bathymetry-truncated
  volume across five declared pelagic depth bands.

That foundation does not establish that a province is a material container,
transport barrier, water mass, dynamical regime, or full-depth ecological
object. The missing verb is exchange: what enters, leaves, crosses, remains,
sinks, rises, accumulates, or dissipates within the reference geography.

The program therefore moves from static geometry to increasingly demanding
tests of physical usefulness. It does not begin by drawing a more satisfying
11-, 22-, 54-, or 56-part partition.

## Research hypothesis

**Primary hypothesis:** some source-backed province boundaries or coherent
groups of boundaries organize repeatable differences in hydrographic content,
pathway retention, and cross-boundary transport strongly enough to serve as
useful ocean-state reference geography at declared depths and times.

**Falsification conditions:** the hypothesis fails globally, or for a named
boundary, when one or more of the following persists after sensitivity tests:

- transport crosses the candidate boundary as readily as it travels along it;
- seasonal or interannual boundary displacement is comparable to the feature's
  width and destroys repeatable adjacency or content contrasts;
- hydrographic distributions on the two sides are not meaningfully distinct;
- pathway residence and destination statistics are no better than matched
  displaced or rotated control boundaries;
- results reverse under defensible grid, mask, depth, time, or tracer-collocation
  choices; or
- the controlling gate, bathymetric feature, or front lies elsewhere.

A failed boundary is a result. The allowed dispositions are **retain**,
**merge**, **split**, **move**, **demote to display reference**, or **unknown**.

## Terms and evidence boundary

- **Province** means a declared source-edition polygon used as a horizontal
  reference address. It is not presumed to be a physical container.
- **Adjacency** means a reproducibly detected shared geometric edge under a
  declared geometry edition and tolerance. It does not imply exchange.
- **Gateway** means a declared physical section through which volume or tracer
  transport is evaluated. A gateway is not automatically a province border.
- **Hydrographic content** means the distribution of identified water
  properties inside a declared horizontal, vertical, and temporal support.
- **Boundary exchange** means signed and gross transport normal to a declared
  edge. Surface velocity crossing is only a screen; volume and heat transport
  require three-dimensional velocity, thickness, tracer, and reference-state
  treatment.
- **Heat content** is not temperature, and neither is heat transport.
- **Ocean state** remains OSW's public geographic metaphor unless and until a
  specific physical identity test is passed.

Every quantitative result must state its geometry edition, projection only when
relevant to display, grid, mask, time support, depth support, variable and units,
reference state, transformation, missing-data treatment, uncertainty or
sensitivity, and evidence class.

The revised Longhurst provinces were defined primarily as surface
biogeographic references. Reusing their horizontal footprints below the surface
creates an OSW comparison column; it does not extend their ecological identity
to the abyss or establish vertically coherent borders.

## Research questions

1. Which source-backed provinces share boundaries, and what physical or
   cartographic kind of edge separates each pair?
2. What continuous seafloor-depth and water-column-capacity fingerprint
   distinguishes each province beyond the current five-band summary?
3. Do adjacent provinces contain distinguishable temperature, salinity,
   density, or oxygen distributions at matched depths and seasons?
4. How much surface motion, volume, and reference-relative heat crosses each
   testable boundary in either direction?
5. Which borders persist, migrate, leak, reverse, or disappear across depth,
   season, year, model product, and observational support?
6. Do tracked heat anomalies follow, cross, divide within, or ignore this
   reference geography?
7. Which borders should be retained, merged, split, moved, or demoted after the
   diagnostics and negative controls are considered together?
8. Can a stable set of province × depth accounts reveal comparable changes in
   ocean inventories, exchanges, relationships, and shocks through time even
   where the boundaries remain permeable?

## Longitudinal ocean-state accounts

The provinces do not have to be sealed physical containers to become useful
accounting units. A stable reference geography can support repeated,
version-controlled measurements of how different parts of the ocean change and
interact through time. The limited economic analogy is useful here:

| Account concept | Ocean-state measure | Required caution |
|---|---|---|
| Inventory | volume, heat content, freshwater content, oxygen, or another declared property inside a province × depth support | An inventory depends on the grid, mask, vertical support, time, and reference convention. |
| Cross-border flow | inward, outward, gross, and net volume or tracer transport across a declared edge | A shared geometric edge is not automatically a valid transport section. |
| Change | tendency of an inventory over a matched interval | Endpoint change, mean tendency, and subdaily variability are different measures. |
| Balance | inventory change compared with compatible boundary and surface terms | An unresolved residual is not automatically mixing, vertical exchange, or error. |
| Relationship | leading source and destination neighbors, exchange asymmetry, retention, and lag | Correlation or sequence does not establish causal delivery. |
| Shock | marine heatwave, freshwater pulse, deoxygenation episode, ice event, or circulation disruption | Event identity and attribution require their own controls and evidence. |
| Revision | recalculation under a newer source, geometry edition, or method | Historical values must remain versioned rather than silently overwritten. |

This creates an **ocean-state observatory**: comparable passports and time
series that show each state's condition, its strongest relationships, and how
both change. “State” still denotes a geographic reference unit in this view,
not sovereignty, impermeability, or a claim that all water inside shares one
physical state.

The first accounts should remain sparse and physically interpretable. Add a
metric only when its stock-or-flow meaning, units, spatial and vertical support,
time basis, uncertainty, and update cadence are explicit. A state dashboard
must show missing and revised values, not reward completeness by filling gaps
with incompatible products.

Each account record must carry `valid_time`, `acquired_at`, geometry edition,
method version, source identity, support fraction, uncertainty or sensitivity,
and revision lineage. Comparisons across dates are permitted only when these
contracts are compatible or when a documented bridge calculation makes the
difference explicit.

## Program stages

### Stage 0 — Freeze the address and comparison contracts

Resolve or explicitly parameterize the 54/56 edition mismatch before attaching
province-wide quantities. Version 4 provides 54 independent source geometries;
`NPSE` and `OCAL` must not receive invented Version 4 borders. Declare spherical
area conventions, longitude-seam handling, coastal and ice masks, boundary
tolerance, minimum support, depth bands, time aggregations, and uncertainty
language.

**Outputs**

- versioned geometry-edition manifest;
- quantitative-address policy for the 54/56 mismatch;
- analysis-grid and mask contract;
- frozen pilot-selection rule and matched-control construction;
- schema and test fixtures for later stages.

**Exit gate:** every downstream record can identify one geometry edition and
one complete support contract without silently translating 56 names into 54
footprints.

### Stage 1 — Build the global adjacency and gateway graph

Derive the topology of the 54 source-backed footprints on the sphere. Record
shared-edge length, point-only contacts, seam behavior, coastline contact,
ice/missing-data contact, and the relationship between province edges and known
physical gateways. Validate representative edges manually and with synthetic
seam, island, sliver, and tolerance fixtures.

The graph must distinguish:

- geometric neighbors;
- physically testable shared sections;
- declared gateways that do not coincide with province edges; and
- edges that cannot support a transport estimate with the admitted data.

**Outputs**

- machine-readable node, edge, and geometry-edition tables;
- an ocean-state neighbor atlas with a complete textual equivalent;
- border passports stating edge type, length method, support, and caveats;
- topology validation receipt and rejected-edge log.

**Exit gate:** adjacency is deterministic across a clean offline run, all edges
trace to the source geometry, and no map styling is presented as a measured
barrier.

### Stage 2 — Replace five bins with continuous depth fingerprints

Calculate area-weighted seafloor-depth distributions for every source-backed
province: quantiles, cumulative area and volume curves, shelf fraction, relief
breadth, maximum sampled depth, and sensitivity to sampling resolution and
coastal treatment. Preserve the five declared bands as an accessible address
index rather than the sole description of vertical shape.

**Outputs**

- one normalized hypsometric curve and uncertainty/sensitivity record per
  province;
- comparable state silhouettes and a nonvisual ranked table;
- diagnostics for classifications that change under plausible thresholds;
- resolution and bathymetry-source comparison for representative province
  archetypes.

**Exit gate:** displayed distinctions survive declared resolution tests or are
labeled unstable; no bathymetric silhouette is called a water mass or dynamic
object.

### Stage 3 — Inventory hydrographic contents

Admit temperature, salinity, density, and oxygen in that order only when source
identity, licensing, vertical coordinates, uncertainty, quality flags, and
coverage can be preserved. Summarize distributions—not only means—by province,
depth support, season, and climatological or event interval. Add heat content
only with a declared density, heat capacity, reference convention, and complete
volume support.

**Outputs**

- property passports for each supported province × depth address;
- coverage and estimated-uncertainty maps beside every property view;
- adjacent-state contrast statistics with multiple-comparison and spatial-
  autocorrelation limitations stated;
- observed, climatological, and model-screened layers kept separately
  selectable and separately receipted.
- versioned province × depth time series suitable for longitudinal state
  comparison without silently changing geometry or method between dates.

**Exit gate:** every property can be regenerated from an admitted source or
bounded local derivative; missing observations remain missing; temperature,
heat content, anomaly, and transport are never substituted for one another.

### Stage 4 — Measure boundary motion and exchange

Begin with a surface normal-versus-along-boundary velocity screen, then advance
only supported edges to three-dimensional volume transport and
reference-relative advective heat transport. Report inward, outward, gross, and
net components, vertical anatomy, seasonal reversal, temporal variability, and
uncertainty or product sensitivity. Do not call open-edge transport convergence;
convergence requires a closed control volume and compatible remaining terms.

Select the first pilot by the frozen rule rather than by the most dramatic
result. Candidate scoring should include existing source custody, native-grid
section support, identifiable adjacent provinces, depth coverage, a matched
control, and a known gate or topographic test. The Southern Ocean/Drake sector
is a strong method-validation candidate because OSW already has section work,
but the gate and province-edge geometries must remain distinct.

**Outputs**

- border exchange scorecards by depth and season;
- maps whose border width/direction encode measured exchange while quiet state
  interiors preserve orientation;
- source/destination neighbor summaries and uncertainty-aware ranks;
- matched displaced/rotated controls and product-sensitivity results;
- explicit lists of unsupported and inconclusive borders.

**Exit gate:** at least one pilot boundary and its controls pass native-grid,
sign, units, thickness, tracer-collocation, missing-value, and closure-scope
tests. A surface crossing map alone does not satisfy this gate.

### Stage 5 — Test dynamic boundary stability

Compare the static reference edges with independently diagnosed fronts and
property gradients by season and year. Measure displacement, overlap,
persistence, cross-edge contrast, surface-to-depth agreement, and reversal.
Treat a moving front as a moving feature; do not turn its climatological mean
into a wall.

**Outputs**

- seasonal boundary envelopes and persistence summaries;
- static-edge versus diagnosed-feature mismatch maps;
- depth-consistency matrices;
- boundary dispositions supported by explicit thresholds and controls.

**Exit gate:** thresholds are frozen before disposition, failure cases remain
visible, and no merge/split/move recommendation rests on a single field or
season.

### Stage 6 — Follow heat events through the graph

Connect the existing event-lineage work to the tested adjacency graph. For each
admitted event, distinguish geometric overlap, observed property propagation,
model pathway, volume exchange, and heat transport. Report origin uncertainty,
border crossings, splitting and merging, dwell time, depth penetration,
termination, and unsupported intervals.

**Outputs**

- event routes expressed as time-varying province × depth addresses;
- source, transit, destination, and unresolved-state passports;
- event and weak/non-event control comparisons;
- an accessible sequence view plus downloadable lineage records.
- state-account timelines that place each event shock beside the affected
  inventories, exchanges, uncertainties, and later revisions.

**Exit gate:** an event route does not infer transported heat from overlap,
streamlines, or parcel counts alone, and claims survive at least one declared
identity sensitivity.

### Stage 7 — Synthesize the zoning decision

Combine geometry, hypsometry, hydrographic content, exchange, retention,
boundary stability, vertical agreement, gate dependence, negative controls,
and uncertainty without forcing one scalar score to conceal conflicts.

**Outputs**

- per-border evidence matrix;
- retain/merge/split/move/demote/unknown recommendations;
- candidate revised geography shown beside—not substituted for—the source
  edition;
- a public explanation of what the tests establish and cannot establish.

**Exit gate:** every disposition traces to evidence and falsification criteria;
unknown remains an acceptable result; owner approval and external scientific
review are separate from repository role approval.

## Cross-stage visual grammar

The signature view is a border-first Oceanic Mollweide map. Province interiors
stay visually quiet. A selected property determines an appropriate, labeled
border encoding:

- adjacency: edge type and confirmed support;
- motion screen: normal versus along-edge velocity;
- volume exchange: signed direction plus gross and net transport;
- heat transport: a diverging, zero-centered scale with units and reference
  temperature;
- stability: persistence and displacement rather than a falsely crisp line;
- evidence: observed, derived, model-screened, unsupported, and inconclusive
  remain distinguishable without color alone.

Land, sea ice, sub-ice or cavity support, missing data, and out-of-domain areas
remain visually and textually distinct. Every map identifies its projection,
date or interval, depth, variable, units, scale, source class, and uncertainty
or sensitivity near the view.

Selection opens a border passport, its two neighboring state passports, depth
and time controls, uncertainty/sensitivity, plain-language finding and limit,
and a direct evidence receipt. The same claim must be recoverable from a
keyboard-operable table and data-oriented text alternative.

A longitudinal view complements the map rather than crowding it. For one
selected province × depth address, it aligns property inventories, boundary
flows, event intervals, support changes, and revisions on a common time axis.
Stock, flow, anomaly, and balance terms must use distinct visual grammar and
must never share a scale merely because they refer to the same state.
An equivalent table lists every displayed timestamp, value, unit, support,
evidence class, uncertainty or sensitivity, and revision status in reading
order; keyboard selection updates both views without moving focus.

## Research controls

- Freeze pilot and comparison rules before inspecting headline outcomes.
- Include displaced, rotated, seasonal, weak-event, or non-event controls as
  appropriate to the claim.
- Correct for grid staggering, partial cells, coastline/ice masks, longitude
  seams, spatial autocorrelation, and unequal observational support.
- Compare at least two defensible resolutions for representative boundary and
  province archetypes before generalizing global ranks.
- Keep source, transformed, derived, and display artifacts separate and
  checksummed.
- Keep default verification offline; make remote acquisition explicit,
  versioned, and replaceable by compact local fixtures.
- Admit fields independently. Failure to obtain one variable must not be
  disguised by substituting a different physical quantity.
- Publish negative and inconclusive results with the same identity and support
  metadata as positive results.

## Priority and dependencies

```text
Stage 0 address contract
        |
        +--> Stage 1 adjacency graph --> Stage 4 boundary exchange --+
        |                                  |                          |
        +--> Stage 2 depth fingerprints ---+--> Stage 5 stability ----+--> Stage 7 zoning decision
        |                                  |                          |
        +--> Stage 3 contents -------------+--> Stage 6 event routes -+
```

Stages 1 and 2 can begin after Stage 0 and do not require live velocity fields.
Stage 3 requires separate data admission. Stage 4 requires velocity and, for
heat transport, compatible tracer and grid metrics. Stages 5 and 6 require the
earlier identity and evidence contracts. Stage 7 cannot begin merely because a
preferred number of regions looks cartographically attractive.

## First bounded research slice

The first goal-sized slice should stop after **Stage 1 plus the Stage 2 method
prototype**:

1. freeze the source-edition, seam, tolerance, grid, and mask contracts;
2. derive and validate the complete 54-province adjacency graph;
3. classify graph edges without claiming barriers or measured exchange;
4. produce the neighbor atlas, textual equivalent, border passports, and
   topology receipt;
5. prototype continuous hypsometry on a frozen set of shelf-led,
   deep-floor-led, abyssal-floor-led, polar, seam-crossing, and small/coastal
   province archetypes; and
6. write the Stage 4 pilot-selection rule without selecting on results.

This slice creates immediate scientific and visual value while keeping new
remote hydrographic and velocity acquisition outside its completion claim.

## Completion evidence for the first slice

- deterministic schema-validated adjacency artifacts and checksums;
- synthetic and real-edge tests for seam, point contact, sliver, tolerance,
  coastline, and missing geometry behavior;
- manual audit of a frozen representative edge set;
- hypsometry sensitivity results for the frozen archetype set;
- map, table, text alternative, and border-passport browser checks at desktop
  and narrow viewports;
- source-register entry, method note, guide, history milestone, and limitations;
- normal offline suite, generated-SVG parsing, browser syntax checks, and native
  `.roles` review;
- no public promotion, zoning disposition, or transport claim implied by
  completion.

Run the current default verification baseline from the repository root:

```powershell
python -m pytest analysis -q
python -m unittest discover -s analysis -p "test_*.py"
python -m compileall -q analysis
node --check atlas/app.js
git diff --check
```

Add focused schema, topology, projection, text-equivalence, and browser tests
with the slice; remote acquisition remains an explicit non-default operation.

## Decision after the first slice

Choose the first exchange pilot only after examining topology, source custody,
grid compatibility, and control feasibility. The decision record must explain
why the chosen edge can test the method and name at least one attractive edge
that was rejected. Then admit hydrographic and velocity sources through their
own evidence and licensing gates before beginning Stages 3 or 4.

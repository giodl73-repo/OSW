# Ocean-State Exchange Pilot Selection Rule

Status: frozen rule executed; `SANT--SSTC` selected before transport outcomes

Date: 2026-09-08

Applies after: completion and review of the first bounded Ocean-State Exchange
Research Program slice

## Purpose

Choose the first boundary-exchange method pilot without inspecting or rewarding
a dramatic velocity, volume-transport, heat-transport, retention, or zoning
result. The pilot tests the method; it is not chosen to make the ocean-state
system look successful.

## Candidate universe

Begin with all accepted shared-source edges in
`research/longhurst-2007-province-adjacency.json`. Point-only contacts,
tolerance-only near misses, sampled-grid-only neighbors, the older-only `NPSE`
and `OCAL` identities, and physical gateways that do not coincide with a source
province edge are not candidate province borders.

## Eligibility gates

A candidate must pass every gate before comparison:

1. **Identity:** one stable edge ID, two source-backed Version 4 provinces, and
   non-zero exact shared-edge length.
2. **Geometry:** an auditable section can be represented on the candidate
   velocity product's native staggered grid without silently moving the source
   edge to a more convenient gate.
3. **Fields:** compatible velocity, layer thickness, mask, horizontal metrics,
   time support, and—only for heat transport—temperature and reference-state
   conventions are identifiable.
4. **Custody:** source, version, license, query, acquisition time, checksums,
   transformations, and redistribution posture can be recorded.
5. **Controls:** at least one displaced or rotated section can be constructed
   under the same grid, support, and calculation contract.
6. **Numerics:** signs, units, face orientation, partial cells, missing values,
   tracer collocation, and longitude seams have testable local fixtures.
7. **Scope:** the computation and compact evidence derivative fit the agreed
   first-pilot resource and repository limits.

Failure of a gate yields `ineligible` with a reason; it does not lower an
opaque score or invite substitution by a different physical quantity.

## Ordering eligible candidates

Order candidates lexicographically by the following pre-result criteria:

1. source payload already under valid OSW custody;
2. independently audited native-grid face geometry already available;
3. complete vertical and seasonal support under one compatible product;
4. strongest matched-control design;
5. source edge visible in the committed 0.25° support diagnostic;
6. coverage of a method archetype not already tested; and
7. stable edge ID as the final deterministic tie-breaker.

Do not use apparent exchange strength, preferred direction, familiar current
name, visual beauty, agreement with a desired realm, media interest, or a
surprising preliminary result to order candidates.

## Required decision record

The selection record must include:

- the complete candidate universe and graph checksum;
- pass/fail/unknown for every eligibility gate;
- ordering values for every eligible candidate;
- the selected edge and its two province identities;
- the selected control geometry and why it is comparable;
- at least one attractive rejected candidate and the exact rejection reason;
- all source and method dependencies still missing; and
- the statement that pilot selection does not validate the border or authorize
  a global transport atlas.

## Known candidate context, not a selection

The Southern Ocean/Drake sector has existing OSW native-section work and is a
strong method-validation context. Drake Passage is a physical gateway, however,
and must not be substituted for a Version 4 province edge. It enters the
candidate comparison only if a source edge independently passes every gate.

## Recorded decision

The rule found six eligible source edges in the custodied ORAS5 Drake subset.
`SANT--SSTC` ranked first because 16 of 18 supported native boundary faces
(88.89%) could be paired one-for-one with a same-orientation face displaced one
T cell into `SANT`, while preserving the exact vertical wet mask and complete
four-month fields. This was the strongest matched-control fraction; no velocity,
temperature contrast, transport sign, transport magnitude, or desired zoning
result entered the ordering.

`ANTA--SANT` was an attractive eligible alternative with more faces, but its
matched-control fraction was lower (124 of 204, or 60.78%). The selected
segment is a bounded method sample near the northern edge of the regional
subset. It is not Drake Passage, not the whole global `SANT--SSTC` source edge,
and not evidence that the border is a material barrier.

[Inspect the complete 128-candidate decision record](../research/ocean-state-exchange-pilot-selection-v1.json).

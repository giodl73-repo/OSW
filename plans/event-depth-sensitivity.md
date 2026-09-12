# Event depth and time sensitivity

Status: research intake; retrieval and source admission required

Date: 2026-09-12

## Question

Does the bounded North Atlantic 2026 event screen retain its storage/advection
scale relationship when the fixed column is extended from 0–50 m to 0–100 m
and 0–200 m, and when endpoint and matched daily tendencies are compared?

## Non-negotiable source boundary

The committed D13/D14 RTOFS payload contains standard-depth temperatures only
through 50 m. It cannot support an inferred 100 m or 200 m result. A valid
extension requires an immutable retrieval containing temperature and horizontal
velocity at admitted standard depths through 200 m for the already-declared
box and interval, plus its exact provider/product/version/request receipt and
checksums.

## Design

1. Freeze the existing box, 2026-08-07 to 2026-08-12 bridge interval, density,
   heat capacity, coordinate convention, and endpoint screen before reading
   deeper outcomes.
2. Acquire an RTOFS/compatible operational assimilative product at 0–200 m;
   retain raw response bytes, query, grid, units, fill values, depth coordinate,
   and acquisition time. Do not silently substitute HYCOM, a reanalysis, or a
   climatology.
3. Recompute D13-style fixed-column temperature tendency at 50, 100, and
   200 m with exact depth samples, then D14-style horizontal-advection screens
   using the same declared gradient sensitivities at each depth.
4. Compare endpoint-mean and daily-mean treatments only where the source
   cadence supports both. Label differing time supports rather than averaging
   them into a single answer.
5. Publish a missing-term ledger for vertical velocity, mixing, shortwave
   penetration, layer-depth tendency, and assimilation increments. A residual
   remains unresolved unless a compatible native term is admitted.

## Exit evidence

- immutable source/request receipt and source-register entry;
- reproducible 50/100/200 m D13/D14 derivatives with no copied values;
- depth/time comparison figure and JSON receipt with signs, units, support,
  uncertainty/sensitivity, and exclusions;
- tests covering missing depths, cadence mismatch, units, and unchanged 50 m
  reproduction;
- native-role review and browser-facing evidence boundary;
- no causal attribution, budget closure, or public-release claim.

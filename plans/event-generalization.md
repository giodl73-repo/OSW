# Event generalization and control-window contract

Status: pre-registration; case selection not yet executed

Date: 2026-09-12

## Purpose

Test whether the current North Atlantic event-screen result is peculiar to its
chosen bridge interval, without converting a convenience sample into a general
mechanism claim.

## Frozen selection rule

1. Use the same NOAA CRW product, threshold category, 0.25° province-address
   grid, and daily footprint/lineage policy as D1–D9.
2. Define an event case as a primary lineage with at least 21 exact-daily
   nodes and a maximum daily area of at least 25,000 km².
3. Select the first qualifying lineage after the present D3 primary interval
   in chronological source order, excluding any lineage sharing a footprint
   pixel with it. Do not choose by apparent surface forcing or advection.
4. Select one control window in the same fixed North Atlantic box and calendar
   season, using the first consecutive six-day interval with no category-one
   footprint pixel in the box and complete source availability.
5. Apply identical RTOFS/GFS retrieval, declared depth support, and analysis
   scripts to both cases. If immutable source versions differ, compare only
   within each acquisition family and label that limitation.

## Required outputs

- machine-readable selection receipt listing all candidates, exclusions, and
  the deterministic winner;
- one event and one control receipt; both retain unsupported/missing terms;
- paired figures comparing storage, horizontal-advection screen, and crossed
  GFS surface scale without summing them into closure;
- a second region/season only after the first event/control pair completes;
- explicit result options: similar, different, indeterminate, or unavailable.

## Prohibitions

- no post-hoc case selection by effect size;
- no claim of causal explanation or generality from one replication;
- no joining products/years without source-edition disclosure;
- no public promotion until retrievals, receipts, tests, and review complete.

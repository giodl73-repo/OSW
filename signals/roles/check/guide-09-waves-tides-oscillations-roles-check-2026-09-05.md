---
skill: roles-check
topic: guide-09-waves-tides-oscillations
date: 2026-09-05
roles_used: 8
p1_count: 0
verdict: APPROVED
---

# Native-role review — Guide 09: Waves, Tides, and Oscillations

## Artifact identification

- **Type:** research-grounded public guide and classification increment
- **Artifacts:** Guide 09, guide index, classification and relationship
  registries, source register, discovery signal, history, and tests
- **Source commit:** `556edacd5c5b9ca0b1829e804ae05384635a730b`
- **Snapshot:** named uncommitted working-tree files on 2026-09-05
- **Validation:** `python -m pytest analysis -q` — 389 passed, 10 subtests passed

All eight native roles apply because the guide links physical mechanisms,
measurements, diagrams, public hazard terminology, classification contracts,
repository state, and planetary wave comparison.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The guide replaces the absolute “energy, not water” slogan with a leading-order distinction plus Stokes-drift, breaking, and nonlinear exceptions. | P3 | Pattern versus parcel motion | Preserve the qualified formulation. |
| 2 | Tide elevation, tidal velocity, residual current, and transport remain separate quantities. | P3 | Tide versus tidal current | Require the measured component and phase in future layers. |
| 3 | Internal-wave generation, propagation, breaking, and irreversible mixing are explicitly separate claims. | P3 | Surface and internal tide | Do not infer mixing from wave presence alone. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The first coastal-height decomposition did not state beside the equation that components require a shared datum, location, time support, and statistic. | P2 | Coastal heights | **Fixed:** place the compatibility rule immediately below the conceptual sum. |
| 2 | The initial Stokes-transport statement lacked its direct operational source beside the claim. | P2 | Pattern versus parcel motion | **Fixed:** link the NOAA WaveWatch III manual in place. |
| 3 | NOAA, GFDL, WHOI, UCAR, and hazard-service evidence is preserved in a claim-level discovery artifact and source register. | P3 | Evidence | Retain direct institutional/primary routes. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Schematics distinguish surface, interior, horizontal velocity, vertical elevation, phase motion, and parcel motion. | P3 | Diagrams | Use distinct glyphs if these become mapped animation layers. |
| 2 | The guide warns that a surface-height signature can understate thermocline displacement. | P3 | Rotating wave grammars | Pair surface maps with depth structure where the claim requires it. |
| 3 | No projection-dependent map is added in this increment. | P3 | Scope | Re-run CHART on the first global wave rendering. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The opening sentence clearly distinguishes a traveling pattern from a traveling body of water. | P3 | Opening | Retain as the public hook with the nearby exceptions. |
| 2 | Similar coastal water-level signals are separated by forcing rather than appearance. | P3 | Coastal heights | Preserve tsunami/tide terminology because it affects safety literacy. |
| 3 | Common mistakes directly counter the most repeatable misconceptions. | P3 | Common mistakes | Keep caveats adjacent when extracting guide graphics. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | All ASCII diagrams have prose/table equivalents and use no colour-only meaning. | P3 | Whole guide | Keep prose canonical. |
| 2 | Harmonic and hazard concepts are named in words rather than only symbolic notation. | P3 | Tide and hazards | Add data tables when real time series are introduced. |
| 3 | Link labels identify the scientific or operational destination. | P3 | Sources and navigation | Preserve descriptive links. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The standard guide contract now includes Guide 09 and verifies all local links offline. | P3 | `analysis/test_guides.py` | Keep the page enumerated. |
| 2 | Registry validation protects the expansion to 80 terms and 56 relationships. | P3 | Classification tests | Require deliberate count/test changes for future concepts. |
| 3 | The complete offline suite passes after integration. | P3 | Full suite | Retain as merge gate. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | README, guide index, classification, history, source register, signal, and tests agree on the new guide and count. | P3 | Repository routes | Version them together when requested. |
| 2 | History records that 80 is evolutionary editorial coverage rather than a natural constant. | P3 | History | Preserve that caveat. |
| 3 | This remains an uncommitted working guide, not a released Atlas mode. | P3 | Review scope | Add a containing commit only after one exists. |

## ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The planetary paragraph requires restoring force, vertical mode, compressibility, forcing, and observed level to match. | P3 | Planetary connection | Keep mechanism before visual resemblance. |
| 2 | It does not identify similar-looking undulations as the same mode. | P3 | Planetary connection | Require a falsifiable mode-specific comparison. |
| 3 | Earth tidal and topographic specifics are not exported to gas giants. | P3 | Whole guide | Continue using the Guide 07 protocol for cross-world mappings. |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues found: 2 (2 resolved)  |  P3 notes: 22
Residual P1: 0  |  Residual P2: 0

Verdict: APPROVED
Top finding: pattern propagation, parcel oscillation, residual drift, and net
transport are related but non-interchangeable claims.
Cross-role consensus: frequency, phase, depth, forcing, datum, and measured
variable must accompany every wave or water-level object.
```

This approves Guide 09 for the working guide collection. It is not external
scientific peer review, a hazard forecast, or an Atlas release.

## Amendments completed

1. Added direct WaveWatch support for the residual Stokes-transport caveat.
2. Added the same-datum, same-location, same-time-support, compatible-statistic
   rule beside the conceptual coastal water-level decomposition.
3. Added seven distinct registry terms and eleven qualified relations instead
   of treating similar water-level and wave phenomena as synonyms.

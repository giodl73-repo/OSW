# Guided Event Anatomy

Status: implemented, validated, and native-role approved; owner review remains

Date: 2026-09-09

Source baseline: `912d138c0822127c2f4ed13c79c3718f03c5766b`

## Product question

What do five increasingly physical evidence screens reveal about one tracked
North Atlantic marine heatwave, and where does each screen stop?

## Visible result

Create `/event/` as a five-scene, map-first reading journey. It is a guided
composition of committed D-series evidence, not a new analysis product and not
another atlas mode.

| Scene | Visitor question | Primary evidence | Evidence class |
|---|---|---|---|
| Event | What was tracked? | D1 point detection, D3 lineage, D9 typed gap | derived observation product |
| Surface | Did a second surface product see the sensitive interval? | D10 OISST/CoralTemp bridge cross-check | derived cross-product comparison |
| Sky–ocean boundary | What surface-energy direction and scale did GFS show? | D12 GFS surface-flux screen | operational forecast/model screen |
| Column | Did the upper 50 m store heat? | D13 RTOFS fixed-depth storage screen | operational assimilative-model screen |
| Motion | How did the horizontal-advection screen compare with the storage scale? | D14 RTOFS horizontal-advection screen | offline model-derived screen |

The page reads numerical findings and limitations from committed JSON. It may
use the matching committed SVG as the stable scene visual, but must not copy a
scientific value into untracked HTML or JavaScript prose.

## Route contract

- Canonical URLs are `/event/?scene=event`, `surface`, `boundary`, `column`, and
  `motion`; an invalid or absent scene resolves to `event` and replaces the URL.
- Previous/next, five labeled scene tabs, left/right arrow keys while focus is
  in the tablist, and a reset control provide equivalent navigation.
- Browser history restores a scene without reloading evidence.
- The README exposes three primary entrances—Explore the ocean, Follow heat,
  and Inspect evidence—with Follow heat linking to this journey in one action.
- The final scene links forward to the Exchange Observatory event route without
  suggesting that the North Atlantic event validates ocean-state borders.

## Scene anatomy

Every scene keeps the same reading order:

1. scene number, question, evidence-class badge, and support interval;
2. one stable visual with a concise alternative;
3. a plain-language finding derived from the receipt;
4. a small facts row for variable/units, depth, time, and spatial support;
5. “What this does not establish,” sourced from the receipt boundary;
6. direct links to the JSON receipt, SVG, evidence-receipt guide, and source
   register.

A persistent progress rail shows all five scene names and evidence classes.
Observed/derived/model-screened status is encoded by words and marks as well as
color. Stock, flow, anomaly, tendency, and partial residual never share an
unlabeled scale.

The committed SVGs have different native aspect ratios and internal layouts.
The page gives them a common visual stage with `object-fit: contain` and never
crops, stretches, redraws, or implies that their panel scales are comparable.

## Frozen scene-field manifest

The first implementation may render only these headline selectors:

| Scene | Selector | Display meaning |
|---|---|---|
| Event | D3 `tracked_window.day_count` | primary-lineage duration |
| Event | D3 `summary.maximum_daily_area_km2` | maximum thresholded daily footprint |
| Event | D9 `identity_evaluation.finding` | policy-conditioned gap extension |
| Surface | D10 `bridge_day_comparison.oisst_anchor_change_c` | nearest OISST cell change |
| Surface | D10 `bridge_day_comparison.oisst_fixed_box_mean_change_c` | fixed-box OISST mean change |
| Sky–ocean boundary | D12 `bridge_evaluation.gfs_box_net_downward_surface_flux_w_m2` | positive-downward surface flux scale |
| Column | D13 `bridge_evaluation.box_zero_to_50_m_storage_tendency_w_m2` | fixed-column storage tendency |
| Column | D13 `bridge_evaluation.gfs_surface_flux_fraction_of_rtofs_storage_scale` | crossed-system scale ratio |
| Motion | D14 `bridge_evaluation.rtofs_offline_0_50_m_horizontal_advection_w_m2` | offline advection scale |
| Motion | D14 `bridge_evaluation.horizontal_advection_fraction_of_storage` | advection/storage scale ratio |
| Motion | D14 `bridge_evaluation.cross_system_partial_residual_w_m2` | explicitly unresolved partial residual |

Selectors, schema IDs, units, sign conventions, labels, source paths, receipt
links, and figure links live together in `scenes.js`. Tests compare every
selector with its committed JSON and reject additions not declared here.

## Evidence and language boundaries

- “Event” means a threshold-defined surface lineage whose identity depends on
  explicit overlap, branch, and gap policies; it is not a material water body.
- D10 is a separate-product surface cross-check, not independent validation.
- D12 is a crossed-system surface-flux screen, not atmospheric causation or
  uniform deposition into the upper ocean.
- D13 is fixed 0–50 m storage from standard-depth-interpolated temperature, not
  native-layer heat content or a closed budget.
- D14 is offline Eulerian horizontal advection, not native tracer flux,
  conservative convergence, or causal attribution.
- The partial residual stays unresolved. It is never relabeled as mixing,
  vertical exchange, assimilation, or error.

## Loading and failure behavior

- Load only the seven declared JSON records and the active scene SVG; do not
  load NetCDF or unrelated atlas payloads.
- Validate each payload’s expected schema before rendering.
- A loading status and any failure are announced through a polite live region
  without moving focus.
- If one scene fails, retain navigation and show its expected receipt link,
  schema, and a bounded error; never fall back to invented values.
- The journey remains readable as a linear document when JavaScript is absent:
  scene questions, evidence classes, boundaries, and direct receipt links are
  present in HTML, while interactive values are explicitly marked unavailable.

## Responsive and accessibility contract

- At 390 CSS pixels, the map, finding, and limitation remain in the same scene
  without horizontal page overflow.
- The scene selector uses tab semantics; focus is visible and is not moved on
  pointer selection, history restoration, data load, or error.
- Active scene, evidence class, loading, and error state do not rely on color.
- SVGs use the committed accessible title/description; the page adds a
  scene-specific data-oriented textual summary rather than repeating the title.
- Reduced-motion preference disables animated transitions; the baseline needs
  no essential animation.
- Without JavaScript, all five scene summaries and receipt links remain in
  document order. With JavaScript, tab semantics apply only after inactive
  panels can be hidden and restored safely.

## Implementation shape

```text
event/index.html       semantic route shell and no-script reading path
event/styles.css       map-first scene, progress rail, responsive rules
event/app.js           URL/history/navigation, schema gates, rendering
event/scenes.js        declarative scene/source/field contract
analysis/test_event_journey.py
```

`scenes.js` declares paths, schemas, field selectors, labels, units, evidence
class, and receipt/figure links. `app.js` owns behavior but contains no copied
headline numbers. Pure selector, schema, URL, and formatting functions remain
exportable for Node-based offline tests. A selector missing from a payload is a
visible error and a test failure.

## Acceptance gate

- All five scenes render from committed records and reproduce the receipt
  values used in their findings.
- Direct URLs, history, reset, tabs, arrow navigation, and next/back work.
- The route is reachable from the README in one action.
- Every scene presents finding, support, evidence class, and limitation in text.
- Invalid schema, missing field, missing file, and invalid scene fixtures fail
  safely.
- Static HTML retains a complete five-scene reading route without JavaScript.
- Desktop and 390-pixel browser inspection passes with keyboard and reduced
  motion checks.
- Focused tests, the complete offline suite, Python compilation, JavaScript
  syntax checks, generated-SVG parsing, `git diff --check`, and native `.roles`
  closeout pass.

## Non-goals

- no new scientific derivation, event selection, or source acquisition;
- no causal attribution or budget closure;
- no global generalization from this event;
- no replacement of Atlas 07 or release-status change;
- no VTRACE or role-process vocabulary in the visitor interface; and
- no automatic public promotion merely because the branch merges.

Before closeout, reconcile the roadmap's baseline test count, completed
exchange-program wording, and branch applicability statement with repository
reality; this housekeeping must not alter public release status.

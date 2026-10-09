---
skill: roles-check
topic: solomon-coastal-confinement
date: 2026-10-09
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Coastal confinement — internal role review

Artifact: source extraction, protocol, inventory, Rust identity binding and atlas
cards. Seven repository role lenses applied internally; these are not independent
scientific reviewers. ORBIT excluded because no analogy is used.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Coast confinement cannot establish full width. | P2 | Width fields | Both scalar/range null; source relation in typed constraint. |
| 2 | Core depths and thermocline density layer are different supports. | P2 | Layer | Sigma bounds / core contexts separate; no fixed slab. |
| 3 | Transport calendar and variability could become width evolution. | P2 | Time | No month/date/error admission or playback. |

## SOUNDER — data stewardship

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | HAL deposit date differs from publication and simulation. | P2 | Receipt | All three operators explicit; original checksum/bytes pinned. |
| 2 | NICU citation could imply original cruise review. | P2 | Source class | Underlying paper unreviewed; actual HTTP403 recorded. |
| 3 | Original model paper is not reproduced field data. | P2 | Extraction | Selected pages / no digitization declared; grid and model periods contextual. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Coast-distance scale could create a false buffer. | P2 | Geography | Map-buffer eligibility false; no footprint or state join derived. |
| 2 | Existing routes are editorial, not model axes. | P2 | Routes | Existing geometry unchanged; new source audit does not diagnose axes. |
| 3 | A point/span chart would suggest paired width edges. | P2 | Cards | Textual constraint graphic; no scalar point, span or bar. |

## BEACON — science editing

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Generic size label hides confinement operator. | P2 | UI | Atlas and inspector say Coastal confinement. |
| 2 | Model result / cited observation need visible distinction. | P2 | Captions | Distinct captions and source notes retain class. |
| 3 | 60 owners could imply 60 measured full widths. | P2 | Coverage | Scoped descriptions count; measured widths and full objective still incomplete. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Old NGCU-specific alternate text would misdescribe new records. | P2 | SVG | Scoped accessible description overrides only confinement grammar. |
| 2 | Source links must address the correct row. | P2 | Query | Array audit pointer used; native/source parity tested. |
| 3 | Longer labels must remain readable on mobile. | P2 | Cards | 320 px reflow, rendered-font checks and screenshots required. |

## KEEL — reproducibility

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | One audit for two owners breaks owner inference. | P2 | Rust | Known ID matches immutable source owner before source selection. |
| 2 | Context deletion / cross-owner substitution can hide evidence transfers. | P2 | Integrity | Owner guards and coherent mutations for both owners, including registered/unregistered transfers. |
| 3 | Generated source pins and preceding multi-audit owner case could drift. | P2 | Pipeline | Dependency comparisons and prior Jutland browser regression required. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | HAL Authorization is not a source redistribution license. | P2 | Original | AMS copyright recorded; source PDF ignored. |
| 2 | Historic source audits must not imply newly traced geometry. | P2 | Scope record | Historic artifacts retained, new review separately identified. |
| 3 | Local passing gates / mainline / independent science are different states. | P2 | Publication | Draft stack, remote results and remaining scientific gates reported separately. |

## Synthesis

Roles reviewed: 7. P1 blockers: 0. P2 issues: 21 addressed or tied to executable
validation. APPROVED-WITH-CONDITIONS for editorial publication after validation.
Top finding: preserve one-sided coast confinement rather than assigning a width.
CURRENT, CHART, SOUNDER and BEACON agree on that restriction.

Three amendments:

1. Use typed confinement descriptions with null widths and explicit support.
2. Bind the two source owners independently and test coherent identity transfers.
3. Give the shared renderer scoped alternate text and array-aware source links;
   verify mobile cards and existing constraints.

Original cruise methods, paired boundaries and independent scientific admission
remain outstanding after editorial validation.

## Executed checks

1,107 Python tests and 918 subtests passed in 444.01 seconds. All 41 Rust tests
and native/WASM builds passed. New confinement browser, prior Jutland browser
and original regional-width browser passed; the latter retains NGCU and West
Australian constraint regression coverage. Both 320 px screenshots visually
inspected. Original reacquisition, dependency/source pins, 48 module syntax
checks, 14 page assignments, Python compilation and whitespace checks passed.

Full seasonal navigation passed 100 current links, 64 route-card links, 119
phase deep links and six round trips, including share/update/reset and mobile
reflow. Editorial validation conditions satisfied; scientific admission and
mainline publication remain outstanding.

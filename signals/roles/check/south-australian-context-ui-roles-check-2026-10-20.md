---
skill: roles-check
topic: south-australian-context-ui
date: 2026-10-20
source_commit: ce3cb2c99395f66a3bfeb5837d6580462645ffc1
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Internal checked-atlas integration review

Seven repository lenses; no external peer-review claim. Scope: compact scene,
Rust validation/query/snapshots, source index, dashboard joins and shared
card/seasons/query renderer. ORBIT is excluded: no planetary comparison.
Approval is for the continuing draft PR, not physical-width admission or a
mainline/full-program completion claim.

## CURRENT — physical claims

| # | Finding | Severity | Disposition |
|---|---|---|---|
| 1 | Highlighted model cells can look like a current footprint. | P2 | Grid-context wording, missing-support legend, explicit unresolved identity/width, null geographic edges. Implemented. |
| 2 | Twelve monthly means do not describe continuous motion or annual extrema. | P2 | Playback steps recorded 2012 means, without interpolation; annual-range admission remains false. Implemented. |
| 3 | Local direction cannot correct the old fixed-section span. | P2 | Old spans/endpoints remain exact, original profiles linked; no rotation/cosine width adjustment. Implemented. |

## SOUNDER — exact evidence

| # | Finding | Severity | Disposition |
|---|---|---|---|
| 1 | A compact scene must retain every threshold outcome and support denominator. | P2 | All 36 memberships, twelve seeds, day counts, pair requirements and 247 sampled vector positions/month preserved; actual-source tests pass. |
| 2 | Rescaling or coherently resealing an altered scene must fail. | P2 | Compiled exact summary/helper and 23 input pins, exact diagnostic projection and owner join; Rust/native/WASM rejection cases cover changes. |
| 3 | Full source records must remain recoverable alongside visual summaries. | P2 | Six supporting documents join the checked index; all twelve full monthly records match native and actual WASM source queries. Implemented. |

## CHART — geographic/visual meaning

| # | Finding | Severity | Disposition |
|---|---|---|---|
| 1 | Display projection and directional glyphs need explicit conventions. | P2 | Supplied lon/lat, local aspect 35°S, longitude correction and direction-only fixed-stride arrows; no shoreline inferred. Implemented. |
| 2 | Phone tick labels were too small. | P2 | Dedicated responsive tick/axis sizes, positive southern-latitude ticks labelled °S, extra footer space. Final phone maps visually inspected. |
| 3 | Extra digits could imply precision beyond the existing reporting rule. | P2 | Approximate displayed old spans use 10 km rounding; raw precise source values remain queryable. Implemented. |

## BEACON — explanations/navigation

| # | Finding | Severity | Disposition |
|---|---|---|---|
| 1 | Added data support must not imply new width records. | P2 | 155 widths and 463 old samples unchanged; new diagnostic remains separate, all admission flags false. Implemented. |
| 2 | Original monthly profiles could be obscured by a new default scene. | P2 | Explicit old-diagnostic link plus existing seasons evidence; old records and mixed-query legacy scenes compare unchanged. Implemented. |
| 3 | Inspection/share links must retain the selected source scope. | P2 | Exact monthly pointer and month/threshold share parameters; actual browser checks all months and restores December/60%. Implemented. |

## HARBOR — accessible interaction

| # | Finding | Severity | Disposition |
|---|---|---|---|
| 1 | Wrapped select labels included option text in the accessible name. | P2 | Initial browser failure retained; explicit accessible labels fix exact keyboard/control targeting. Implemented and rechecked. |
| 2 | Automatic playback must respect user motion/visibility intent. | P2 | Reduced-motion disable, manual selection retained, stop on collapse/hide/removal/control changes. Browser covers reduced motion, playback and collapse-stop. |
| 3 | Map color alone cannot convey evidence or limits. | P2 | Updated named SVG/description, live textual readings, numerical definition list, exact membership/support links, 320 px reflow. Implemented. |

## KEEL — verification

| # | Finding | Severity | Disposition |
|---|---|---|---|
| 1 | Native tests alone do not verify shipped WASM/UI. | P2 | Registered actual browser matrix: three views ×36 cases, source-row parity, packet/index corruption, keyboard, share and motion tests. |
| 2 | A new module could drop old mixed-query scenes or unrelated data. | P2 | All other collections, 47 old diagnostics, 239 other objects/dashboard rows and dates preserved; all five legacy mixed scene arrays compare exactly to predecessor. |
| 3 | The live predecessor full run cannot certify later UI edits. | P2 | Exact ce3cb2c scope recorded; no restart or latest-full-pass claim. A clean UI successor full gate remains a release condition. |

## LOGBOOK — truthful delivery

| # | Finding | Severity | Disposition |
|---|---|---|---|
| 1 | Per-gap PRs contradict the requested workflow. | P3 | Continue the same branch/draft PR83; no merge. |
| 2 | Remote CI failures cannot be described as passing tests. | P3 | ce3 attempts failed before tests: GEOMAR source403/Hawaii timeout. Source pins retained; local gates reported separately. |
| 3 | This integration does not complete the full measurement inventory. | P3 | Batch identifies remaining named-flow/physical-dimension work and keeps the full objective active. |

## Synthesis

21 findings: 0 P1, 18 P2, 3 P3. CURRENT, CHART and BEACON agree that the
selected component is model-grid context rather than a physical footprint.
Draft delivery is approved with remaining scientific-admission and successor
full-regression conditions. There is no external scientific endorsement.

Three principal amendments: explicit control labels; readable phone axes and
reported-span precision; recorded-only playback with motion/collapse stopping.
No existing source values or canonical dimensions changed to satisfy tests.

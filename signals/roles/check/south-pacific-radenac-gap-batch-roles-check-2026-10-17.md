---
skill: roles-check
topic: south-pacific-radenac-gap-batch
date: 2026-10-17
source_commit: 62f2a2bfbe94913ffb9d9eab9b1a1ac8129eed06
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Seven-role source, data and presentation review

Review target: the South Pacific March1990 constraint, Radenac article-edition
verification, generated query/index products and integrated card. Roles selected
for physical scope, provenance, cartography, explanation, accessibility,
reproducibility and repository accuracy. ORBIT is not relevant to this batch.
This is a review through the installed lenses, not independent human approval.

| Role / # | Finding | Severity / state | Evidence / recommendation |
|---|---|---|---|
| CURRENT1 | A less-than description cannot supply a representative current width. | P2 resolved | Frozen record keeps point, lower bound, error and ordinary range null; source mutation tests and native/WASM guards pass. |
| CURRENT2 | Figure3 uses sigma2=36.75 and section-specific1800–1840 m reference. | P2 resolved | Audit and graphic preserve reference; changing it rejects. Upper1000 m remains plot context. |
| CURRENT3 | Front bracket, peak velocity,100 km assumption and ACC separation cannot become edges. | P2 resolved | Each interpretation is explicitly excluded and source tests reject promotion. |
| SOUNDER1 | HAL full response changed while scientific edition stayed identical. | P2 resolved | Frozen graph protects all22 article pages and394 objects, raw streams, resources and order. |
| SOUNDER2 | Fresh bytes must retain their own response identity. | P2 resolved | Separate file; historical receipt untouched; no PDF rewriting and no fallback from damaged original. Actual fresh-only tests pass. |
| SOUNDER3 | Cover permission must be narrow and not include article resources. | P2 resolved |14 observed wrapper IDs are disjoint from protected graph; exact object inventory, cover text and remaining objects verified. |
| CHART1 | A width buffer would imply geographic edges absent from the source. | P2 resolved | Independent qualifier graphic and text only; no new footprint or buffered route. |
| CHART2 | An apparent annual cycle would overstate one historical section. | P2 resolved | New month-dated phase preserves1990-03; playback disabled, annual extrema null. Actual seasons card checked. |
| CHART3 | Existing100 W climatology differs from historical170 W section. | P2 resolved | Separate diagnostics retained; actual atlas link survives. Full retained-climatology browser regression pending. |
| BEACON1 | Publication year must not replace observation month. | P2 resolved | Card prominently says March1990 and distinguishes publication1995. |
| BEACON2 | The headline must retain the inequality. | P2 resolved | SVG and textual card show less than200 km; no numeric point admitted. |
| BEACON3 | Source and method should be reachable directly. | P3 verified | Actual source query at /measurement equals native result; inspector works without fetching PDF. |
| HARBOR1 | SVG meaning must be available without color. | P2 resolved | Explicit aria label, inequality text, caption and method note; inspected mobile rendering. |
| HARBOR2 | Narrow screens must preserve qualification and source access. | P3 verified |320 px page reflow passes; full caption and ordinary source link visible. |
| HARBOR3 | Reduced motion must not trigger seasonal animation. | P3 verified | Reduced-motion viewport checked; play control remains disabled. Broader current-card keyboard regression pending. |
| KEEL1 | Complete default offline gate must run from a clean commit. | P2 pending | Full pytest invocation started from clean62f2a2b. Record terminal result before merge approval. |
| KEEL2 | Generated provenance and prior data must remain coherent. | P2 resolved |70 engine hashes verified; staged bytes equal disk; prior146 widths /33 diagnostics unchanged. Seasonal parent hash refresh isolated. |
| KEEL3 | Changed-source UI and broad regression gates must complete. | P2 pending | New integrated UI and nine coherent rejection cases pass. NGCC browser regression passes;39 inventory/climatology tests and538 subtests pass. Retained-climatology browser, all45 collections and all100 cards are running; record outcomes before merge approval. |
| LOGBOOK1 | Scope count must not be advertised as complete measurement coverage. | P2 resolved | Receipt calls147 records scoped; source boundaries, uncertainties and seasonal coverage remain open. |
| LOGBOOK2 | Copyrighted original scans must stay outside Git. | P2 resolved | Only receipts, factual annotations, independent graphic and verifier contract staged; original PDF ignored. |
| LOGBOOK3 | Continue one reviewable batch without PR proliferation. | P3 verified | Existing branch /draft PR83 retained; no merge or new PR. Source commit explicit. |

Roles reviewed:7. Outstanding P1 blockers:0. Outstanding P2 gates:2.
Verdict: **APPROVED-WITH-CONDITIONS**. No merge approval yet.

Top finding: the source supplies a qualified local historical band description,
not an exact or seasonally comparable whole-current dimension. CURRENT, SOUNDER
and CHART agree that reference, support and inequality must travel with it.

## Three amendments

1. Completed: freeze month precision, reference state and excluded numeric
   interpretations in Python and compiled Rust admission, including deletion,
   owner reassignment and coherent forged-source rejection.
2. Completed: bind generated HAL responses to a frozen scientific edition while
   preserving original response identity and protected article resources.
3. Pending: append terminal full-suite and broad browser results here and in the
   batch receipt; update the same PR. Keep verdict conditional until then.

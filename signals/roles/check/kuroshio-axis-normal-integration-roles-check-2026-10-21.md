---
skill: roles-check
topic: kuroshio-axis-normal-integration
date: 2026-10-21
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Kuroshio normal-span integration review

Internal review of code, typed contract, generated packet, shared UI and
validation evidence. Lenses are the installed `.roles` files, applied by the
same reviewer; this is not independent external scientific approval.

| Role / selection reason | Finding | Severity | Resolution |
|---|---|---|---|
| CURRENT / physical scope | C01: Geometric axis normal cannot establish velocity normal or ocean connectivity. | P2 | Resolved: false verification flags and adjacent UI scope. |
| CURRENT | C02: Monthly ranges and tangent spread could imply physical uncertainty. | P2 | Resolved: available-day counts/ranges and method-sensitivity wording; physical uncertainty stays null. |
| CURRENT | C03: Regional model samples could inflate whole-current widths or ranks. | P2 | Resolved: separate collection, false admission/rank flags; old inventories and state joins preserved. |
| SOUNDER / provenance | S01: Each row needs its exact source case and provider license. | P2 | Resolved: semantic ID, edition-scoped pointer, exact source query and unchanged licensed source record. |
| SOUNDER | S02: Failed cases and unknown threshold/fallback cannot become zero. | P2 | Resolved: all 16,470 cases retained; native equality rejects modified nulls or missing rows. |
| SOUNDER | S03: UI transformations need a separate pinned contract. | P2 | Resolved: dedicated adapter/protocol/contract, frozen scientific producer unchanged. |
| CHART / cartography | M01: Normal lines must use source intersections and geodesic projection. | P2 | Resolved: Rust densifies geodesic segments; rejected sections have empty paths, not ribbons. |
| CHART | M02: Initial brown normal lines had poor map contrast. | P2 | Resolved: gold lines on both maps, inspected in rendered desktop/mobile screenshots. |
| CHART | M03: Paired cards could leave stale date/depth/metric/window geometry. | P2 | Resolved: all four selectors synchronize; browser verifies overlay updates and clearing. |
| BEACON / explanation | B01: Normal mode initially retained the regional coverage headline. | P2 | Resolved: dynamic heading and primary normal coverage count. |
| BEACON | B02: Same-day sensitivity needs its three-window denominator and missing state. | P2 | Resolved: 0–3 window completeness and qualified method spread in table. |
| BEACON | B03: A short path from map to source/method must survive the integration. | P2 | Resolved: inspect row, exact report, normal figure and provider citation links. |
| HARBOR / equivalent access | H01: More columns squeezed words into unreadable fragments. | P2 | Resolved: wider table within labelled keyboard-focusable horizontal scroll region. |
| HARBOR | H02: Selection meaning cannot depend on gold or pointer use. | P2 | Resolved: named metric/window controls, live status, dated SVG title and equivalent case table. |
| HARBOR | H03: Navigation, phone layout and reduced motion need actual browser checks. | P2 | Resolved: Enter navigation, keyboard selects, 320 px page reflow and disabled playback pass. |
| KEEL / reproducibility | K01: Partial or rebound editions must fail before querying. | P2 | Resolved: full Rust equality, dependency/source/owner bindings and mutation tests. |
| KEEL | K02: Browser/native geometry and backward snapshots need executable proof. | P2 | Resolved: exact native/WASM result, old full snapshot, 107 exact source documents, 103 Rust tests. |
| KEEL | K03: A fresh complete clean offline suite is still a release requirement. | P2 | Open release gate: focused gates pass; free space is below full-suite guard. No main merge or full-suite claim. |
| LOGBOOK / repository state | L01: A PR per gap would make the program unmanageable. | P2 | Resolved: same branch/draft PR #83; no new PR or main merge. |
| LOGBOOK | L02: Build growth and stale generated parts could hide source loss. | P2 | Resolved: shared static source reduces WASM to 48 MB; seven superseded parts retired; originals retained. |
| LOGBOOK | L03: Published status must distinguish filled model coverage from remaining inventories. | P2 | Resolved: versioned batch report and current PR snapshot retain 89 unranked names and 18 owners without scoped width; goal incomplete. |

Seven roles, 21 findings: zero P1, 21 P2 (20 resolved, one open release gate),
zero P3. **APPROVED-WITH-CONDITIONS for this continuing draft increment.**
Main merge/release remain gated on fresh full validation. CURRENT, SOUNDER,
CHART and BEACON agree that geometric model coverage must not be presented as
physical inventory completion.

Highest-priority amendments applied: keep a separate typed model collection;
fix map contrast/table width and dynamic coverage; preserve all selectors and
verify the actual shared UI. Source reproduction remains the earlier exact
23-report Linux evidence; fresh integration CI is reported separately.

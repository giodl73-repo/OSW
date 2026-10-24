---
skill: roles-check
topic: indian-secc-hycom-source-foundation
date: 2026-10-22
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Internal role review: source foundation, not a measurement admission

Artifact: source acquisition/package code, frozen candidate-test protocol,
diagnostic/map generators and pending browser gate. These are internal review
lenses applied by the implementing agent, not seven external approvals.
Selected the seven installed data/science/cartography/accessibility/repository
roles. ORBIT is unrelated to this source preparation.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation/status |
|---|---|---|---|---|
| 1 | Daily-00Z model means differ from full three-hour means and observations. | P2 | Source protocol | Fixed: estimator and interpretation explicit. |
| 2 | A finer grid alone cannot isolate product/depth/forcing differences. | P2 | Diagnostic protocol | Fixed: no resolution-only attribution. |
| 3 | Local paired edges and axis checks do not establish current identity. | P2 | Stronger candidate gate | Fixed: identity, width, annual-range and state admissions remain false. |

## SOUNDER — data stewardship

| # | Finding | Severity | Section | Recommendation/status |
|---|---|---|---|---|
| 1 | Missing three-hour times make a blind index stride unsafe. | P2 | Selection | Fixed: exact calendar lookup; 363 dates and two absent 00Z dates. |
| 2 | Component-specific fills could create vectors from different times. | P2 | Monthly operator | Fixed and tested: common paired mask, calendar-based eligibility. |
| 3 | Packing scale has a declared Float32 type, not exact decimal 0.001. | P2 | Decoding | Fixed and tested: binary32-to-binary64 scale and Int64 sums. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation/status |
|---|---|---|---|---|
| 1 | A source mask could be mistaken for land or a current outline. | P2 | Prepared view | Fixed in generator: gray means missing/inadequate support; no coastline inference. |
| 2 | A threshold span could imply an admitted width. | P2 | Prepared view | Fixed in generator: dotted diagnostics and dashed candidates; admissions false. |
| 3 | Rendered map fidelity remains unverified. | P2 | View gate | Open: render/inspect real results before publishing a view or claiming a cartographic pass. |

## BEACON — science editing

| # | Finding | Severity | Section | Recommendation/status |
|---|---|---|---|---|
| 1 | A smaller native grid could be described prematurely as a measured current. | P2 | Page notice | Fixed in generator: no named-current width or whole-current axis admitted. |
| 2 | Acquisition progress could be confused with gap closure. | P2 | Batch record | Fixed: catalog counts unchanged; no completed source/candidate claim. |
| 3 | One year of sample means cannot support annual physical extrema. | P2 | Protocol and report | Fixed: explicit null/false annual/seasonal admissions. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation/status |
|---|---|---|---|---|
| 1 | Color alone cannot convey diagnostic success or model direction. | P2 | Prepared view | Implemented: arrows, line styles, textual outcomes and all-month table. |
| 2 | The month control needs keyboard access and updated context. | P2 | Prepared view | Implemented: labeled native select, live summary and image alternative. |
| 3 | Keyboard, narrow reflow and actual image alternatives remain untested. | P2 | Browser gate | Open: prepared gate must pass on real generated assets before UI completion. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation/status |
|---|---|---|---|---|
| 1 | A mutable live provider must not become a default unit-test dependency. | P2 | Acquisition CLI | Fixed: explicit network action; 14 focused offline tests pass. |
| 2 | Retained ZIPs need exact member bounds and byte checks. | P2 | Package/reproduce | Implemented/tested for traversal, member-set and checksum rejection. |
| 3 | Full source reconstruction and diagnostic reproduction are pending. | P2 | Source gate | Open: no reproducibility claim until retained originals rebuild exact output bytes. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation/status |
|---|---|---|---|---|
| 1 | Gap batches must stay in the continuing branch/draft PR. | P2 | Workflow | Fixed: branch/PR #83 retained; no merge/new PR. |
| 2 | Historical source and method bytes must remain auditable. | P2 | Custody | Original source, original pre-amendment protocol and failed selection retained privately for packaging. |
| 3 | Existing broad gate failures cannot be relabeled by focused tests. | P2 | Batch status | Fixed: prior Rotschi HTTP403 and unrun new view/source gates stated explicitly. |

## Synthesis and amendments

Seven roles, 21 findings. Zero unresolved P1 blockers for this **source-code
foundation**; three P2 execution gates remain open (render/inspect, browser,
source reconstruction). Other findings are resolved in code or explicit scope.
Verdict: approved with those conditions; **not approval to admit a width or
publish unexecuted scientific results**.

Highest-priority amendments implemented: exact clock selection across missing
timestamps; common paired monthly masks with typed packing; independent
axis/edge/resolution/identity gates. Finish retained-source reconstruction,
real diagnostic calculation and browser/visual checks before claiming the
source and its query/UI integration complete. No permission pause is required.

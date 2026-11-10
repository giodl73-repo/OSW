---
skill: roles-check
topic: portugal-orca-section-span
date: 2026-10-17
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Portugal ORCA section-span preparation review

Scope: five new preparation files against base5212c8e. No inventory, generated
UI, Rust or WASM changes. Seven installed role lenses applied directly; this
does not claim seven independent human or agent reviewers. ORBIT does not apply
to the source measurement and reproduction work.

## Findings

| Role | Finding | Severity | Evidence and disposition |
|---|---|---|---|
| CURRENT | Coordinate separation is not a flow-normal or whole-current width. | P2 | Dedicated metric, protocol and graphic explicitly retain that distinction; registration must preserve it. |
| CURRENT | Cruise envelope cannot become the exact section observation period. | P2 | Observed period/month samples remain null; cruise context has explicit false occupation flag. |
| CURRENT | Density layers and transport uncertainty cannot define a metre slab or width error. | P2 | Fixed depths and uncertainty null; promotion tests reject both. |
| SOUNDER | Raw original and original-page visual review are missing. | P2 | Explicit false provenance flags and recovery gate; no fabricated PDF pin. Candidate preparation only. |
| SOUNDER | WGS84 is a transformation convention rather than a source datum claim. | P2 | Separate assumption flag and null source datum; mutation test rejects promotion. |
| SOUNDER | Frozen source input must be distinguishable from publisher bytes. | P2 | Exact event plus entire local source-file SHA verified; no publisher byte-equivalence claim. |
| CHART | Section endpoints must not turn into an axis, route buffer or footprint. | P2 | Section geometry and diagram are labelled; physical widths remain null. Enforce when integrated. |
| CHART | Parallel distance and shortest geodesic have different meanings. | P3 | Protocol chooses inverse geodesic explicitly; alternative is not an error bar. |
| CHART | Standalone graphic is legible, but actual small-card layout is untested. | P2 |640x420 Chrome render visually reviewed; mobile card validation remains a registration gate. |
| BEACON | A precise internal calculation can imply excessive source precision. | P2 | Display rounded to116 km with approximation sign; unrounded value retained only as calculation evidence. |
| BEACON | Whole-width and date limitations belong beside the number. | P2 | Both visible in graphic and protocol; preserve in actual card. |
| BEACON | Candidate preparation must not be advertised as filled product coverage. | P2 | Status explicitly unregistered; counts remain148 records/78 owners. |
| HARBOR | Graphic meaning needs text beyond color. | P2 | SVG title, description, endpoints and scope supplied; no palette-only encoding. |
| HARBOR | Narrow view and zoom cannot be inferred from desktop rendering. | P2 | No mobile or integrated accessibility pass claimed; required before registration. |
| HARBOR | Static historic evidence cannot justify animated seasonal states. | P2 | Playback flag false and no monthly samples; mutation test rejects invented playback. |
| KEEL | The native executable is in use by the earlier full suite. | P2 | No rebuild or generated-data mutation in preparation. |
| KEEL | Calculation and unsupported-inference guards need executable evidence. | P2 |20 source tests pass; inverse direction independently checked. This is not compiled parity. |
| KEEL | Native/WASM and coherent input mutation gates are still outstanding. | P2 | Explicit registration work; no claim of runtime admission yet. |
| LOGBOOK | Earlier full-run results do not validate this later candidate. | P2 | Separate checkpoint, focused results and active-run status in receipt. |
| LOGBOOK | A provider timeout is not checksum success or scientific invalidity. | P2 | Latest remote Qiu timeout recorded; prior Reading failure retained as history. No pins relaxed. |
| LOGBOOK | Publication must stay in the existing rolling PR. | P2 | Same branch/PR83; no new PR or merge. |

## Synthesis

Roles reviewed:7. Open P1 blockers:0. All preparation-stage P2 findings addressed
by scope, provenance and status amendments. Product registration remains
conditional on its runtime and UI gates; the candidate is not admitted evidence
coverage yet. P3 note: keep the calculation convention visible.

Verdict: **APPROVED-WITH-CONDITIONS for preparation only**.
Top finding: published coordinates support reproducible section separation,
not a whole-current or seasonal width.
Cross-role consensus: CURRENT/CHART/BEACON require the same local-section scope;
SOUNDER/KEEL/LOGBOOK require precise provenance and validation boundaries.

## Amendments applied

1. Separated local section separation, flow-normal width and whole-current
   width, with source datum and physical uncertainty unresolved.
2. Recorded missing original PDF/page review and exact cruise-versus-section
   time support in machine-readable context and human-readable presentation.
3. Kept coverage counts and generated products unchanged until scientific
   admission, native/WASM parity and actual UI checks are completed.

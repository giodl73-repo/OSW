---
skill: roles-check
topic: portugal-orca-section-span-integration
date: 2026-10-17
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Portugal section-span integration review

Artifact: registration, compiled admission and existing UI flows following
preparation commit2df6f24. Seven installed lenses applied directly, without
claiming independent human/agent review. ORBIT is outside this artifact's scope.

| Role | Finding | Severity | Disposition |
|---|---|---|---|
| CURRENT | Coordinate separation cannot establish flow-normal or whole-current width. | P2 | Dedicated phase/context, null physical widths and false ranking/extrema flags retained in both runtimes. |
| CURRENT | Cruise dates do not establish exact section sampling days. | P2 | Cruise context separate; observed period and monthly samples null; temporal promotion rejected. |
| CURRENT | Density layers and transport error must not become fixed depths or width error. | P2 | No fixed metre bounds or uncertainty invented; source and coherent runtime tests reject both. |
| SOUNDER | Original PDF acquisition and page review are missing. | P2 | This limitation is visible in every shared chart and frozen audit; no PDF checksum claimed. |
| SOUNDER | Assumed ellipsoid must not be misrepresented as the source datum. | P2 | WGS84 calculation convention explicit, source datum null; datum promotion test rejects. |
| SOUNDER | Editable audit and source receipt could be coherently forged. | P2 | Compiled frozen descriptor, mandatory owner/source bindings and exact diagnostic guards reject the tested forgery. |
| CHART | Local section geometry could be confused with a current axis or footprint. | P2 | Diagram and scene name section limits; no route buffer or physical width envelope generated. |
| CHART | Prior surface diagnostic must remain separate. | P2 | Existing40 N link retained on Portugal atlas card; no profile/time-domain combination. |
| CHART | Parent hash refresh must not disguise changes to other mapped currents. | P2 | Six seasonal rows and four other cards differ only in inventory/parent-file SHA values; scientific geometry is equal. |
| BEACON | Excess internal precision could imply precise physical width. | P2 | Approximate116 km display; unrounded inverse geodesic kept in calculation context. |
| BEACON | Scope limitations must remain beside the value. | P2 | Local-section title, unknown physical width/range and date limitation are visible in atlas, seasons and query. |
| BEACON | New source evidence is not full measurement coverage. | P2 |149 scoped records/79 names is distinguished from whole-current or annual-extrema coverage. |
| HARBOR | Plot meaning must survive loss of color or pointer interaction. | P2 | SVG role/description, endpoint labels and prose provide equivalent evidence; keyboard record inspection checked. |
| HARBOR | Narrow viewport can hide long provenance text. | P2 | Actual320px render inspected; reflow assertion passes and source links remain visible. |
| HARBOR | Static historical evidence cannot imply seasonal animation. | P2 | No monthly frames or playback; disabled control checked under reduced motion. |
| KEEL | Complete-inventory deletion must not bypass per-row validation. | P2 | Python and native/WASM require the Portugal record when owner/source exists; coherent deletion rejects. |
| KEEL | Build dependencies must include new frozen input and admission code. | P2 | Audit and Rust module included in engine manifest; final bytes must match staged bytes. |
| KEEL | A partial full-suite run cannot count as validation success. | P2 | Prior148-record run explicitly stopped at51%; combined149-record gate required and tracked separately. |
| LOGBOOK | Old preparation review cannot imply product registration was already tested then. | P2 | Preparation receipt retained as history; this integration has a separate receipt and review. |
| LOGBOOK | Provider acquisition failures must remain visible. | P2 | Latest observed remote Qiu timeout recorded; preceding Reading failure retained; no pins relaxed. |
| LOGBOOK | User requested one rolling publication boundary. | P2 | Same branch and draft PR83; no new PR and no merge. |

## Verification and verdict

-57 source/inventory/seasonal tests and546 subtests passed in377.28s. Final
  display-language update:20 source tests passed in0.54s; input coordinates and
  geodesic value unchanged.
-Final build:47 Rust tests passed in1.81s. Shared WASM and CLI compiled from
  the same source.275 indexed JSON sources and45 query collections.
-Actual UI: atlas, seasons, filtered query chart, source inspector,320px and
  reduced-motion checks passed in the initial integration; nine coherent
  native/WASM alterations rejected. The final-byte mixed-query check is a
  separate publication gate, recorded below once terminal.
-All100 current cards and149 distinct records pass definition/source links,
  keyboard disclosure, conflict display, inspector return, reset, mobile and
  stored-evidence checks without direct source requests.
-All148 prior width rows,35 prior diagnostics and41 other query collections
  compare equal. Only Portugal has new scientific card evidence; other changed
  cards/seasonal rows carry parent hash refreshes only.

Roles reviewed:7. Open P1 blockers:0. Preparation/integration P2 findings are
addressed in the implementation. Full batch validation and complete remote
acquisition remain open publication conditions, not inferred successes.

Verdict: **APPROVED-WITH-CONDITIONS**. Top finding: this is reproducible local
section separation, not a physical whole-current width or seasonal range.
CURRENT/CHART/BEACON agree on scope; SOUNDER/KEEL/LOGBOOK agree on exact evidence
and gate accounting.

## Amendments applied

1. Preserved source-coordinate, calculation, temporal, layer and physical-width
   distinctions in a dedicated typed record and shared accessible chart.
2. Added mandatory compiled source/record/diagnostic checks and explicit missing
   original provenance, with coherent invalid-input exercises.
3. Kept prior scientific data equal and retained the rolling PR boundary;
   stopped the partial gate explicitly and require the combined full run.

## Final-byte publication checks

Final browser run is terminal **PASS**: filtered and combined-width query
native/WASM parity, atlas, seasons, source inspection, record inspection,
320px, reduced motion and nine coherent native/WASM rejections. No original
PDF requested or seasonal playback enabled. Final mobile graphic visually
inspected. All100-card run is separately terminal PASS.73 engine dependency
hashes match disk. The complete suite collects1573 tests; its combined run
remains the outstanding local gate, with remote acquisition separately open.

## Corrected admission-order follow-up

The d5afdba full run exposed a P2 ordering regression: the new mandatory
Portugal guard rejected an aliased Baffin descriptor before its original-source
identity check. It was intentionally stopped after23%, with the focused
failure reproduced and retained. This does not invalidate the prior invalid-
input rejection result; it identifies incorrect diagnostic precedence.

Moving the complete Portugal check immediately after seasonal per-row source
validation preserves both guards.13 affected identity-transfer tests pass in
99.98s; the rebuilt native/WASM Portugal UI and all nine coherent rejection
cases pass again.73 final engine hashes match. Full-suite and remote-source
conditions remain open. No source pin or rejection assertion was weakened.
